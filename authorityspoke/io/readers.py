import json
import pathlib

from typing import Dict, List, Optional, Tuple, Union

from authorityspoke.enactments import Code
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


def make_filepath(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
    default_folder: str = "holdings",
):
    """
    Create :class:`.pathlib.Path` for a file containing XML or JSON to load as objects.

    :param filename:
        just the name of the file, without the directory.

    :param directory:
        just the directory, without the path

    :param filepath:
        a full path that just needs to be checked for validity and returned

    :param default_folder:
        a folder name to use in constructing a missing directory path

    :returns:
        the path to the desired file
    """
    if filepath:
        if not isinstance(filepath, pathlib.Path):
            raise TypeError('"filepath" must by type pathlib.Path')
        return filepath
    if not filename:
        raise ValueError(
            '"filepath" or "filename" must be given to find a file to open.'
        )
    if not directory:
        directory = get_directory_path(default_folder)
    return directory / filename


def read_json(
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
    validated_filepath = make_filepath(
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
    """
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
    validated_filepath = make_filepath(
        filename, directory, filepath, default_folder="codes"
    )
    return Code(filepath=validated_filepath)
