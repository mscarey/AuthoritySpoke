"""
Functions to load JSON or XML files for conversion into authorityspoke objects.

Will usually hand off data to the io.readers module to create authorityspoke objects.
"""
import json
import pathlib

from typing import Any, Dict, List, Iterator, Optional, Tuple, Union

from authorityspoke.enactments import Code
from authorityspoke.holdings import Holding
from authorityspoke.jurisdictions import Regime
from authorityspoke.opinions import Opinion
from authorityspoke.selectors import TextQuoteSelector

from authorityspoke.io import anchors, filepaths, readers
from authorityspoke.io.text_expansion import expand_shorthand
from authorityspoke.io.schemas import RawHolding, RawDecision


def load_code(
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


def load_and_read_holdings(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
    regime: Optional[Regime] = None,
) -> Tuple[
    List[Holding], List[List[TextQuoteSelector]], Dict[str, List[TextQuoteSelector]]
]:
    """
    Read holdings with text anchors from a file.
    """
    raw_holdings = load_holdings(
        filename=filename, directory=directory, filepath=filepath
    )
    holding_anchors = anchors.get_holding_anchors(raw_holdings)
    named_anchors = anchors.get_named_anchors(raw_holdings)
    holdings = readers.read_holdings(raw_holdings, regime=regime)
    return holdings, holding_anchors, named_anchors


def load_holdings(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
) -> List[RawHolding]:
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

    :returns:
        a list of :class:`Rule`\s from a JSON file in the
        ``example_data/holdings`` subdirectory, from a JSON
        file.
    """
    validated_filepath = filepaths.make_filepath(
        filename, directory, filepath, default_folder="holdings"
    )
    with open(validated_filepath, "r") as f:
        holdings = json.load(f)
    holdings = expand_shorthand(holdings)
    return holdings


def load_decision(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
) -> RawDecision:
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

    return decision_dict
