"""
Converting simple structured data from XML or JSON into authorityspoke objects.

These functions will usually be called by functions from the io.loaders module
after they import some data from a file.
"""

import datetime
from functools import partial

from typing import Dict, List, Iterable, Iterator, Optional, Tuple, Union

from authorityspoke.enactments import Code, Enactment
from authorityspoke.factors import Factor
from authorityspoke.holdings import Holding
from authorityspoke.jurisdictions import Regime
from authorityspoke.opinions import Opinion
from authorityspoke.procedures import Procedure
from authorityspoke.rules import Rule
from authorityspoke.selectors import TextQuoteSelector


def read_holding(
    outputs: Optional[Union[str, Dict, List[Union[str, Dict]]]],
    inputs: Optional[Union[str, Dict, List[Union[str, Dict]]]] = None,
    despite: Optional[Union[str, Dict, List[Union[str, Dict]]]] = None,
    exclusive: bool = False,
    rule_valid: bool = True,
    decided: bool = True,
    mandatory: bool = False,
    universal: bool = False,
    generic: bool = False,
    enactments: Optional[Union[Dict, Iterable[Dict]]] = None,
    enactments_despite: Optional[Union[Dict, Iterable[Dict]]] = None,
    text: Optional[Union[str, Dict, Iterable[Union[str, Dict]]]] = None,
    mentioned: Optional[List[Factor]] = None,
    regime: Optional[Regime] = None,
) -> Iterator[Tuple[Holding, List[Factor], Dict[Factor, List[TextQuoteSelector]]]]:
    r"""
    Create new :class:`Holding` object from simple datatypes from JSON input.

    Will yield multiple items if ``exclusive: True`` is present in ``record``.

    :param inputs:
        data for constructing :class:`.Factor` inputs for a :class:`.Rule`

    :param despite:
        data for constructing despite :class:`.Factor`\s for a :class:`.Rule`

    :param outputs:
        data for constructing :class:`.Factor` outputs for a :class:`.Rule`

    :param enactments:
        the :class:`.Enactment`\s cited as authority for
        invoking the ``procedure``.

    :param enactments_despite:
        the :class:`.Enactment`\s specifically cited as failing
        to preclude application of the ``procedure``.

    :param mandatory:
        whether the ``procedure`` is mandatory for the
        court to apply whenever the :class:`.Rule` is properly invoked.
        ``False`` means that the ``procedure`` is "discretionary".

    :param universal:
        ``True`` if the ``procedure`` is applicable whenever
        its inputs are present. ``False`` means that the ``procedure`` is
        applicable in "some" situation where the inputs are present.

    :param generic:
        whether the :class:`Rule` is being mentioned in a generic
        context. e.g., if the :class:`Rule` is being mentioned in
        an :class:`.Argument` object merely as an example of the
        kind of :class:`Rule` that might be mentioned in such an
        :class:`.Argument`.

    :param name:
        an identifier used to retrieve the :class:`Rule` when
        needed for the composition of another :class:`.Factor`
        object.

    :param rule_valid:
        Whether the :class:`.Rule` is asserted to be valid (or
        useable by a court in litigation).

    :param decided:
        Whether it should be deemed decided whether the :class:`.Rule`
        is valid. If not, the :class:`.Holding` have the effect
        of overruling prior :class:`.Holding`\s finding the :class:`.Rule`
        to be either valid or invalid.

    :param text:
        Text selectors for the whole :class:`Holding`, not for any
        individual :class:`.Factor`. Often selects text used to
        indicate whether the :class:`.Rule` is ``mandatory``, ``universal``,
        ``valid``, or ``decided``, or shows the ``exclusive`` way to reach
        the outputs.

    :param mentioned:
        Known :class:`.Factor`\s that may be reused in constructing
        the new :class:`Holding`.

    :param regime:
        Collection of :class:`.Jurisdiction`\s and corresponding
        :class:`.Code`\s for discovering :class:`.Enactment`\s to
        reference in the new :class:`Holding`.

    :returns:
        New :class:`.Holding`, and an updated dictionary with mentioned
        :class:`.Factor`\s as keys and their :class:`.TextQuoteSelector`\s
        as values.
    """

    # If lists were omitted around single elements in the JSON,
    # add them back

    factor_text_links: Dict[Factor, List[TextQuoteSelector]] = {}
    list_mentioned: List[Factor] = mentioned or []

    selectors = read_selectors(text)

    basic_rule, list_mentioned, factor_text_links = read_rule(
        outputs=outputs,
        inputs=inputs,
        despite=despite,
        mandatory=mandatory,
        universal=universal,
        generic=generic,
        enactments=enactments,
        enactments_despite=enactments_despite,
        mentioned=list_mentioned,
        regime=regime,
        factor_text_links=factor_text_links,
    )
    yield (
        Holding(
            rule=basic_rule, rule_valid=rule_valid, decided=decided, selectors=selectors
        ),
        list_mentioned,
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
            yield (Holding(rule=modified_rule, selectors=selectors), list_mentioned, {})


def read_holdings(
    holdings: Dict[str, Iterable],  # TODO: remove "mentioned", leaving a list
    regime: Optional[Regime] = None,
    mentioned: Optional[List[Factor]] = None,
    factor_text_links=None,
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
    list_mentioned: List[Factor] = mentioned or []

    factor_dicts = holdings.get("mentioned_factors")

    # populates mentioned with context factors that don't
    # need links to Opinion text
    if factor_dicts:
        for factor_dict in factor_dicts:
            _, list_mentioned, factor_text_links = Factor.from_dict(
                factor_record=factor_dict,
                mentioned=list_mentioned,
                regime=regime,
                factor_text_links=factor_text_links,
            )

    finished_holdings: List[Holding] = []
    text_links = {}
    for holding_record in holdings["holdings"]:
        for finished_holding, new_mentioned, factor_text_links in read_holding(
            mentioned=list_mentioned, regime=regime, **holding_record
        ):
            list_mentioned = new_mentioned
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


def read_rule(
    outputs: Optional[Union[str, Dict, List[Union[str, Dict]]]],
    inputs: Optional[Union[str, Dict, List[Union[str, Dict]]]] = None,
    despite: Optional[Union[str, Dict, List[Union[str, Dict]]]] = None,
    mandatory: bool = False,
    universal: bool = False,
    generic: bool = False,
    enactments: Optional[Union[Dict, Iterable[Dict]]] = None,
    enactments_despite: Optional[Union[Dict, Iterable[Dict]]] = None,
    mentioned: List[Factor] = None,
    regime: Optional[Regime] = None,
    factor_text_links: Optional[Dict[Factor, List[TextQuoteSelector]]] = None,
) -> Iterator[Tuple[Rule, List[Factor]]]:
    r"""
    Make :class:`Rule` from a :class:`dict` of strings and a list of mentioned :class:`.Factor`\s.

    :param inputs:
        data for constructing :class:`.Factor` inputs for a :class:`.Rule`

    :param despite:
        data for constructing despite :class:`.Factor`\s for a :class:`.Rule`

    :param outputs:
        data for constructing :class:`.Factor` outputs for a :class:`.Rule`

    :param enactments:
        the :class:`.Enactment`\s cited as authority for
        invoking the ``procedure``.

    :param enactments_despite:
        the :class:`.Enactment`\s specifically cited as failing
        to preclude application of the ``procedure``.

    :param mandatory:
        whether the ``procedure`` is mandatory for the
        court to apply whenever the :class:`.Rule` is properly invoked.
        ``False`` means that the ``procedure`` is "discretionary".

    :param universal:
        ``True`` if the ``procedure`` is applicable whenever
        its inputs are present. ``False`` means that the ``procedure`` is
        applicable in "some" situation where the inputs are present.

    :param generic:
        whether the :class:`Rule` is being mentioned in a generic
        context. e.g., if the :class:`Rule` is being mentioned in
        an :class:`.Argument` object merely as an example of the
        kind of :class:`Rule` that might be mentioned in such an
        :class:`.Argument`.

    :param mentioned:
        a series of context factors, including any generic
        :class:`.Factor`\s that need to be mentioned in
        :class:`.Predicate`\s. These will have been constructed
        from the ``mentioned_entities`` section of the input
        JSON.

    :param regime:

    :returns:
        iterator yielding :class:`Rule`\s with the items
        from ``mentioned_entities`` as ``context_factors``
    """

    def list_from_records(
        record_list: Union[Dict[str, str], List[Dict[str, str]]],
        mentioned: List[Factor],
        class_to_create,
        regime: Optional[Regime] = None,
        factor_text_links: Dict = None,
    ) -> Union[List[Factor], List[Enactment]]:
        factors_or_enactments: Union[List[Factor], List[Enactment]] = []
        if record_list is None:
            record_list = []
        if not isinstance(record_list, list):
            record_list = [record_list]
        for record in record_list:
            created, mentioned, factor_text_links = class_to_create.from_dict(
                record, mentioned, regime=regime, factor_text_links=factor_text_links
            )
            factors_or_enactments.append(created)
        return tuple(factors_or_enactments), mentioned, factor_text_links

    factor_dicts = [outputs, inputs, despite]
    factor_groups = []
    for i, category in enumerate(factor_dicts):
        category, mentioned, factor_text_links = list_from_records(
            record_list=category,
            mentioned=mentioned,
            class_to_create=Factor,
            regime=regime,
            factor_text_links=factor_text_links,
        )
        factor_groups.append(category)

    enactment_dicts = [enactments, enactments_despite]
    enactment_groups = []
    for i, category in enumerate(enactment_dicts):
        category, mentioned, factor_text_links = list_from_records(
            record_list=category,
            mentioned=mentioned,
            class_to_create=Enactment,
            regime=regime,
            factor_text_links=factor_text_links,
        )
        enactment_groups.append(category)

    procedure = Procedure(
        outputs=factor_groups[0], inputs=factor_groups[1], despite=factor_groups[2]
    )

    return (
        Rule(
            procedure=procedure,
            enactments=enactment_groups[0],
            enactments_despite=enactment_groups[1],
            mandatory=mandatory,
            universal=universal,
        ),
        mentioned,
        factor_text_links,
    )


def read_selector(text: Union[dict, str]) -> TextQuoteSelector:
    """
    Create new instance from JSON user input.

    If the input is a :class:`str`, tries to break up the string
    into :attr:`~TextQuoteSelector.prefix`, :attr:`~TextQuoteSelector.exact`,
    and :attr:`~TextQuoteSelector.suffix`, by splitting on the pipe characters.

    :param text:
        a string or dict representing a text passage

    :returns: a new :class:`TextQuoteSelector`
    """
    if isinstance(text, dict):
        return TextQuoteSelector(**text)
    if text.count("|") == 0:
        return TextQuoteSelector(exact=text)
    elif text.count("|") == 2:
        prefix, exact, suffix = text.split("|")
        return TextQuoteSelector(exact=exact, prefix=prefix, suffix=suffix)
    raise ValueError(
        "'text' must be either a dict, a string containing no | pipe "
        + "separator, or a string containing two pipe separators to divide "
        + "the string into 'prefix', 'exact', and 'suffix'."
    )


def read_selectors(
    records: Optional[Union[str, Dict, Iterable[Union[str, Dict]]]]
) -> List[TextQuoteSelector]:
    r"""
    Create list of :class:`.TextQuoteSelector`\s from JSON user input.

    If the input is a :class:`str`, tries to break up the string
    into :attr:`~TextQuoteSelector.prefix`, :attr:`~TextQuoteSelector.exact`,
    and :attr:`~TextQuoteSelector.suffix`, by splitting on the pipe characters.

    :param record:
        a string or dict representing a text passage, or list of
        strings and dicts.

    :returns: a list of :class:`TextQuoteSelector`\s
    """
    if records is None:
        return []
    if isinstance(records, (str, dict)):
        return [read_selector(records)]
    return [read_selector(record) for record in records]
