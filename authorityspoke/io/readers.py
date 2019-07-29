"""
Converting simple structured data from XML or JSON into authorityspoke objects.

These functions will usually be called by functions from the io.loaders module
after they import some data from a file.
"""

import datetime
from functools import partial
import json
import pathlib

from typing import Dict, List, Iterable, Iterator, Optional, Tuple, Union

from authorityspoke.enactments import Code
from authorityspoke.factors import Factor
from authorityspoke.holdings import Holding
from authorityspoke.io import filepaths
from authorityspoke.jurisdictions import Regime
from authorityspoke.opinions import Opinion
from authorityspoke.rules import Rule
from authorityspoke.selectors import TextQuoteSelector


def read_holding(
    record: Dict, mentioned: List[Factor], regime: Optional[Regime] = None
) -> Iterator[Tuple[Holding, List[Factor], Dict[Factor, List[TextQuoteSelector]]]]:
    """
    Create new :class:`Holding` object from user input.

    Will yield multiple items if ``exclusive: True`` is present in ``record``.

    :param record:
        A representation of a :class:`Holding` in the format
        used for input JSON

    :param mentioned:
        known :class:`.Factor`\s that may be reused in constructing
        the new :class:`Holding`

    :param regime:
        a collection of :class:`.Jurisdiction`\s and corresponding
        :class:`.Code`\s for discovering :class:`.Enactment`\s to
        reference in the new :class:`Holding`.

    :returns:
        new :class:`Holding`.
    """

    # If lists were omitted around single elements in the JSON,
    # add them back

    for category in ("inputs", "despite", "outputs"):
        if isinstance(record.get(category), (str, dict)):
            record[category] = [record[category]]

    factor_text_links: Dict[Factor, List[TextQuoteSelector]] = {}
    factor_groups: Dict[str, List] = {"inputs": [], "outputs": [], "despite": []}

    for factor_type in factor_groups:
        for factor_dict in record.get(factor_type) or []:
            created, mentioned = Factor.from_dict(factor_dict, mentioned, regime=regime)
            if isinstance(factor_dict, dict):
                selector_group = factor_dict.pop("text", None)
                if selector_group:
                    if not isinstance(selector_group, list):
                        selector_group = list(selector_group)
                    selector_group = [
                        TextQuoteSelector.from_record(selector)
                        for selector in selector_group
                    ]
                    factor_text_links[created] = selector_group
            factor_groups[factor_type].append(created)

    exclusive = record.pop("exclusive", None)
    rule_valid = record.pop("rule_valid", True)
    decided = record.pop("decided", True)
    selector = TextQuoteSelector.from_record(record.pop("text", None))

    basic_rule, mentioned = Rule.from_dict(
        record=record, mentioned=mentioned, regime=regime, factor_groups=factor_groups
    )
    yield (
        Holding(
            rule=basic_rule, rule_valid=rule_valid, decided=decided, selectors=selector
        ),
        mentioned,
        factor_text_links,
    )

    if exclusive:
        if not rule_valid:
            raise NotImplementedError(
                "The ability to state that it is not 'valid' to assert "
                + "that a Rule is the 'exclusive' way to reach an output is "
                + "not implemented, so 'rule_valid' cannot be False while "
                + "'exclusive' is True. Try expressing this in another way "
                + "without the 'exclusive' keyword."
            )
        if not decided:
            raise NotImplementedError(
                "The ability to state that it is not 'decided' whether "
                + "a Rule is the 'exclusive' way to reach an output is "
                + "not implemented. Try expressing this in another way "
                + "without the 'exclusive' keyword."
            )
        for modified_rule in basic_rule.get_contrapositives():
            yield (Holding(rule=modified_rule, selectors=selector), mentioned, {})


def read_holdings(
    holdings: Dict[str, Iterable],  # TODO: remove "mentioned", leaving a list
    regime: Optional[Regime] = None,
    mentioned: List[Factor] = None,
    include_text_links: bool = False,
) -> Union[List[Holding], Tuple[List[Holding], Dict[Factor, List[TextQuoteSelector]]]]:
    r"""
    Load a list of :class:`Holdings`\s from JSON, with optional text links.

    :param holdings:
        the record from JSON in the format that lists ``mentioned_factors``
        followed by a list of holdings

    :parame regime:

    :param mentioned:
        A list of :class:`.Factor`\s that the method needs to
        expect to find in the :class:`.Opinion`\'s holdings,
        but that won't be provided within the JSON, if any.

    :param include_text_links:

    :returns:
        a list of :class:`Rule`\s from a JSON file in the
        ``example_data/holdings`` subdirectory, from a JSON
        file.
    """
    if not mentioned:
        mentioned = []

    factor_dicts = holdings.get("mentioned_factors")

    # populates mentioned with context factors that don't
    # need links to Opinion text
    if factor_dicts:
        for factor_dict in factor_dicts:
            _, mentioned = Factor.from_dict(
                factor_dict, mentioned=mentioned, regime=regime
            )

    finished_holdings: List[Holding] = []
    text_links = {}
    for holding_record in holdings["holdings"]:
        for finished_holding, new_mentioned, factor_text_links in read_holding(
            holding_record, mentioned=mentioned, regime=regime
        ):
            mentioned = new_mentioned
            finished_holdings.append(finished_holding)
            text_links.update(factor_text_links)
    if include_text_links:
        return finished_holdings, text_links
    return finished_holdings


def read_opinion(
    citations: List[Dict[str, str]],
    decision_date: str,
    court: Dict[str, Union[str, int]],
    casebody: Optional[Dict] = None,
    name: str = "",
    name_abbreviation: str = "",
    first_page: str = "",
    last_page: str = "",
    lead_only: bool = True,
    as_generator: bool = False,
    **kwargs
) -> Union[Opinion, Iterator[Opinion], List[Opinion]]:
    r"""
    Create and return one or more :class:`.Opinion` objects.

    This function uses the model of a judicial decision from
    the `Caselaw Access Project API <https://api.case.law/v1/cases/>`_.
    One of these records may contain multiple :class:`.Opinion`\s.

    Typically one record will contain all the :class:`.Opinion`\s
    from one appeal, but not necessarily from the whole lawsuit. One
    lawsuit may contain multiple appeals or other petitions, and
    if more then one of those generates published :class:`.Opinion`\s,
    the CAP API will divide those :class:`.Opinion`\s into a separate
    record for each appeal.

    The lead opinion is commonly, but not always, the only
    :class:`.Opinion` that creates binding legal authority.
    Usually every :class:`.Rule` posited by the lead :class:`.Opinion` is
    binding, but some may not be, often because parts of the
    :class:`.Opinion` fail to command a majority of the panel
    of judges.

    :param citations:
        Page references that would be used to locate the decision in
        printed volumes. May be the closest things to accepted
        identifiers for a decision.

    :param casebody:
        A large section of the CAP API response containing all the
        text that was printed in the reporter volume. Only available
        if the ``full_case`` flag was used in the API request.

    :param decision_date:
        The day the :class:`.Opinion`\s were issued, in ISO format.

    :param court:
        A dict containing the :class:`.Court` slug, hopefully a unique
        identifier of the court. Also contains the "id", which can be
        resorted to when the slug turns out not to be unique.

    :param name:
        Full name of the lawsuit. Sometimes the same lawsuit may change
        its name as time passes between multiple appeals.

    :param name_abbreviation:
        A shorter name for the lawsuit. Courts may or may not have
        deterministic rules for creating the abbreviation given
        the full name. This may be only one of many possible abbreviations.

    :param first_page:
        The first printed page where any of the :class:`.Opinion`\s for this
        decision can be found. Does not come with an identifier of the reporter,
        but in most cases there is only one official reporter, which is the most
        likely choice.

    :param last_page:
        The last printed page where any of the :class:`.Opinion`\s for this
        decision can be found.

    :param lead_only:
        If ``True``, returns a single :class:`.Opinion` object
        from the first opinion found in the
        ``casebody/data/opinions`` section of the dict, which should
        usually be the lead opinion. If ``False``, returns an iterator that yields
        :class:`.Opinion` objects from every opinion in the case.
    """

    def make_opinion(
        name: str,
        name_abbreviation: str,
        citations: Iterable[str],
        first_page: Optional[int],
        last_page: Optional[int],
        decision_date: datetime.date,
        court: str,
        opinion_dict: Dict[str, str],
    ) -> Opinion:

        author = opinion_dict.get("author")
        if author:
            author = author.strip(",:")

        return Opinion(
            name=name,
            name_abbreviation=name_abbreviation,
            citations=citations,
            first_page=first_page,
            last_page=last_page,
            decision_date=decision_date,
            court=court,
            position=opinion_dict.get("type"),
            author=author,
            text=opinion_dict.get("text"),
        )

    if not casebody:
        casebody = {}

    opinions = casebody.get("data", {}).get(
        "opinions", [{"type": "majority", "author": None}]
    )

    make_opinion_given_case = partial(
        make_opinion,
        name=name,
        name_abbreviation=name_abbreviation,
        first_page=int(first_page) if first_page else None,
        last_page=int(last_page) if last_page else None,
        decision_date=datetime.date.fromisoformat(decision_date),
        court=court["slug"],
        citations=tuple(c["cite"] for c in citations),
    )
    if lead_only:
        if as_generator:
            return iter([make_opinion_given_case(opinion_dict=opinions[0])])
        else:
            return make_opinion_given_case(opinion_dict=opinions[0])
    elif as_generator:
        return iter(
            make_opinion_given_case(opinion_dict=opinion_dict)
            for opinion_dict in opinions
        )
    return [
        make_opinion_given_case(opinion_dict=opinion_dict) for opinion_dict in opinions
    ]
