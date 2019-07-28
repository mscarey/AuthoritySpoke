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
from authorityspoke.selectors import TextQuoteSelector


def read_dict(
    case: Dict[str, Iterable],  # TODO: change format to list
    regime: Optional[Regime] = None,
    mentioned: List[Factor] = None,
    include_text_links: bool = False,
) -> Union[List[Holding], Tuple[List[Holding], Dict[Factor, List[TextQuoteSelector]]]]:
    r"""
    Load a list of :class:`Holdings`\s from JSON, with optional text links.

    :param filename:
        the name of the JSON file to look in for :class:`Rule`
        data in the format that lists ``mentioned_factors``
        followed by a list of holdings

    :param directory:
        the path of the directory containing the JSON file

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

    factor_dicts = case.get("mentioned_factors")

    # populates mentioned with context factors that don't
    # need links to Opinion text
    if factor_dicts:
        for factor_dict in factor_dicts:
            _, mentioned = Factor.from_dict(
                factor_dict, mentioned=mentioned, regime=regime
            )

    finished_holdings: List[Holding] = []
    text_links = {}
    for holding_record in case.get("holdings"):
        for finished_holding, new_mentioned, factor_text_links in Holding.from_dict(
            holding_record, mentioned, regime=regime
        ):
            mentioned = new_mentioned
            finished_holdings.append(finished_holding)
            text_links.update(factor_text_links)
    if include_text_links:
        return finished_holdings, text_links
    return finished_holdings


def json_holdings(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
    regime: Optional[Regime] = None,
    mentioned: List[Factor] = None,
    include_text_links: bool = False,
) -> Union[List[Holding], Tuple[List[Holding], Dict[Factor, List[TextQuoteSelector]]]]:
    r"""
    Load a list of :class:`.Holding`\s from JSON.

    :param filename:
        the name of the JSON file to look in for :class:`Rule`
        data in the format that lists ``mentioned_factors``
        followed by a list of holdings.

    :param directory:
        the path of the directory containing the JSON file.

    :param filepath:
        Complete path to the XML file representing the :class:`.Code`,
        including filename.

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
    validated_filepath = filepaths.make_filepath(
        filename, directory, filepath, default_folder="holdings"
    )
    with open(validated_filepath, "r") as f:
        case = json.load(f)
    return read_dict(
        case=case,
        regime=regime,
        mentioned=mentioned,
        include_text_links=include_text_links,
    )


def read_code(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
) -> Code:
    r"""
    Create a new :class:`.Code` from an XML filepath.

    Defers parsing of the XML until later, which makes "read" in the
    function name misleading.

    :param filename:
        Name of the XML file representing the :class:`.Code`.
        Ignored if filepath is given.

    :param directory:
        Directory where the XML file can be found.
        Ignored if filepath is given.

    :param filepath:
        Complete path to the XML file representing the :class:`.Code`,
        including filename.

    :returns:
        new :class:`.Code` object that can be used to parse the XML to
        find text of :class:`.Enactment`\s.
    """
    validated_filepath = filepaths.make_filepath(
        filename, directory, filepath, default_folder="codes"
    )
    return Code(filepath=validated_filepath)


def opinion_from_case(
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


def json_opinion(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
    lead_only: bool = True,
    as_generator: bool = False,
) -> Union[Opinion, Iterator[Opinion], List[Opinion]]:
    r"""
    Create and return one or more :class:`.Opinion` objects from JSON.

    Relies on the JSON format from the `Caselaw Access Project
    API <https://api.case.law/v1/cases/>`_.

    :param filename: The name of the input JSON file.

    :param directory: The directory where the input JSON file is located.

    :param filepath:
        Complete path to the JSON file representing the :class:`.Opinion`,
        including filename.

    :param lead_only:
        If True, returns a single :class:`.Opinion` object,
        otherwise returns an iterator that yields every
        :class:`.Opinion` in the case.

    :param as_generator:
        if True, returns a generator that
        yields all opinions meeting the query.
    """

    validated_filepath = filepaths.make_filepath(
        filename, directory, filepath, default_folder="cases"
    )

    with open(validated_filepath, "r") as f:
        decision_dict = json.load(f)

    return opinion_from_case(
        lead_only=lead_only, as_generator=as_generator, **decision_dict
    )
