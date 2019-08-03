"""
Functions to load JSON or XML files for conversion into authorityspoke objects.

Will usually hand off data to the io.readers module to create authorityspoke objects.
"""
import json
import pathlib

from typing import Dict, List, Iterator, Optional, Tuple, Union

from authorityspoke.enactments import Code
from authorityspoke.factors import Factor
from authorityspoke.holdings import Holding
from authorityspoke.io import filepaths, readers
from authorityspoke.jurisdictions import Regime
from authorityspoke.opinions import Opinion
from authorityspoke.selectors import TextQuoteSelector


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


def load_holdings(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
    regime: Optional[Regime] = None,
    mentioned: List[Factor] = None,
    report_mentioned: bool = False,
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

    :param report_mentioned:

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
    answer, mentioned = readers.read_holdings(
        holdings=holdings, regime=regime, mentioned=mentioned, report_mentioned=True
    )
    return (answer, mentioned) if report_mentioned else answer


def load_opinion(
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

    return readers.read_opinion(
        lead_only=lead_only, as_generator=as_generator, **decision_dict
    )
