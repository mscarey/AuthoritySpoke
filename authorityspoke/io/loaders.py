"""
Functions to load JSON or XML files for conversion into authorityspoke objects.

Will usually hand off data to the io.readers module to create authorityspoke objects.
"""
import json
import pathlib

from typing import Any, Dict, List, Iterator, Optional, Tuple, Union

from legislice.download import Client
from legislice.name_index import EnactmentIndex

from authorityspoke.decisions import Decision
from authorityspoke.holdings import Holding
from authorityspoke.opinions import AnchoredHoldings
from authorityspoke.rules import Rule

from authorityspoke.io import filepaths, readers
from authorityspoke.io.name_index import Mentioned
from authorityspoke.io.schemas import RawHolding, RawDecision


def load_holdings(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
) -> List[RawHolding]:
    r"""
    Load a list of records from JSON to create :class:`.Holding`\s.

    :param filename:
        the name of the JSON file to look in for :class:`Holding`
        data in the format that lists ``mentioned_factors``
        followed by a list of holdings.

    :param directory:
        the path of the directory containing the JSON file.

    :param filepath:
        Complete path to the XML file representing the :class:`.Code`,
        including filename.

    :parame regime:

    :returns:
        a list of :class:`Holding`\s from a JSON file in the
        ``example_data/holdings`` subdirectory, from a JSON
        file.
    """
    validated_filepath = filepaths.make_filepath(
        filename, directory, filepath, default_folder="holdings"
    )
    with open(validated_filepath, "r") as f:
        holdings = json.load(f)

    return holdings


def load_rules_with_index(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
    client: Optional[Client] = None,
    many: bool = True,
) -> Tuple[List[Rule], Mentioned]:
    r"""
    Read :class:`.Rule`\s from a file.

    Even though this function will generate :class:`.Rule`\s instead
    of :class:`.Holding`\s, it uses the :func:`load_holding` function.
    Some fields that can exist in a :class:`.Holding` object (rule_valid,
    decided, exclusive) are not applicable to :class:`.Rule`\s.

    :param filename: The name of the input JSON file.

    :param directory: The directory where the input JSON file is located.

    :param filepath:
        Complete path to the JSON file representing the :class:`.Opinion`,
        including filename.

    :param regime:
        The regime to reference for the :class:`Enactment`\s
        mentioned in the holding.
    """
    raw_rules = load_holdings(filename=filename, directory=directory, filepath=filepath)
    return readers.read_rules_with_index(raw_rules, client=client, many=many)


def load_and_read_holdings(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
    client: Optional[Client] = None,
) -> List[Holding]:
    """
    Read holdings from a file.

    :param filename: The name of the input JSON file.

    :param directory: The directory where the input JSON file is located.

    :param filepath:
        Complete path to the JSON file representing the :class:`.Opinion`,
        including filename.

    :param client:
        The client with an API key to download :class:`Enactment`\s
        mentioned in the holding.
    """
    raw_holdings = load_holdings(
        filename=filename, directory=directory, filepath=filepath
    )
    return readers.read_holdings(raw_holdings, client=client)


def load_holdings_with_index(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
    client: Optional[Client] = None,
    enactment_index: Optional[EnactmentIndex] = None,
) -> readers.HoldingsIndexed:
    """Read holdings with factor index from a file."""
    raw_holdings = load_holdings(
        filename=filename, directory=directory, filepath=filepath
    )
    return readers.read_holdings_with_index(
        raw_holdings, client=client, enactment_index=enactment_index
    )


def load_holdings_with_anchors(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
    client: Optional[Client] = None,
) -> AnchoredHoldings:
    """Read holdings from file, with Opinion text anchors for holdings and factors."""
    raw_holdings = load_holdings(
        filename=filename, directory=directory, filepath=filepath
    )
    return readers.read_holdings_with_anchors(raw_holdings, client=client)


def load_decision(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
) -> RawDecision:
    r"""
    Load file containing a judicial decision with one or more opinions.

    Relies on the JSON format from the `Caselaw Access Project
    API <https://api.case.law/v1/cases/>`_.

    :param filename: The name of the input JSON file.

    :param directory: The directory where the input JSON file is located.

    :param filepath:
        Complete path to the JSON file representing the :class:`.Opinion`,
        including filename.
    """

    validated_filepath = filepaths.make_filepath(
        filename, directory, filepath, default_folder="cases"
    )

    with open(validated_filepath, "r") as f:
        decision_dict = json.load(f)

    return decision_dict


def load_and_read_decision(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
) -> Decision:
    r"""Load file containing a judicial decision and make an Opinion object."""
    raw_decision = load_decision(
        filename=filename, directory=directory, filepath=filepath
    )
    return readers.read_decision(raw_decision)
