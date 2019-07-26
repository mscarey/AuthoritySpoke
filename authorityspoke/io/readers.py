import json
import pathlib

from typing import Dict, List, Optional, Tuple, Union

from authorityspoke.factors import Factor
from authorityspoke.holdings import Holding
from authorityspoke.jurisdictions import Regime
from authorityspoke.selectors import TextQuoteSelector


def get_directory_path(stem: str) -> pathlib.Path:
    """
    Find a data directory for importing files.

    Will only find the correct directory if it is the current working
    directory is that directory, is its child directory, or is a sibling
    directory. Requires the directory to be found within an ``example_data``
    directory.

    :param stem:
        name of the folder where the desired example data files
        can be found, e.g. "holdings" or "opinions".

    :returns:
        path to the directory with the desired example data files.
    """
    directory = pathlib.Path.cwd()
    if directory.stem == stem:
        return directory
    if directory.stem != "example_data":
        directory = directory / "example_data"
    directory = directory / stem
    if not directory.exists():
        directory = pathlib.Path.cwd().parent / "example_data" / stem
    return directory


def read_dict(
    case: Dict,
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


def read_json(
    filename: str,
    directory: Optional[pathlib.Path] = None,
    regime: Optional[Regime] = None,
    mentioned: List[Factor] = None,
    include_text_links: bool = False,
) -> Union[List[Holding], Tuple[List[Holding], Dict[Factor, List[TextQuoteSelector]]]]:
    r"""
    Load a list of :class:`Holdings`\s from JSON.

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
    if not directory:
        directory = get_directory_path("holdings")
    with open(directory / filename, "r") as f:
        case = json.load(f)
    return read_dict(
        case=case,
        regime=regime,
        mentioned=mentioned,
        include_text_links=include_text_links,
    )
