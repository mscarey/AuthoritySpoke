"""
Functions to load JSON or XML files for conversion into authorityspoke objects.

Will usually hand off data to the io.readers module to create authorityspoke objects.
"""

import json
import pathlib

from typing import List, Optional

import yaml


from authorityspoke.decisions import DecisionReading, RawDecision
from authorityspoke.holdings import RawHolding

from authorityspoke.io import filepaths, readers


def load_holdings(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
) -> List[RawHolding]:
    r"""
    Load list of records from YAML or JSON to create :class:`.Holding`\s with text selectors.

    :param filename:
        the name of the JSON file to look in for :class:`Holding`
        data in the format that lists ``mentioned_factors``
        followed by a list of holdings.

    :param directory:
        the path of the directory containing the JSON file.

    :param filepath:
        Complete path to the XML file representing the :class:`.Code`,
        including filename.

    :returns:
        a list of :class:`Holding`\s from a JSON file in the
        ``example_data/holdings`` subdirectory, from a JSON
        file.
    """
    validated_filepath = filepaths.make_filepath(
        filename, directory, filepath, default_folder="holdings"
    )

    with open(validated_filepath, "r") as f:
        if validated_filepath.suffix == ".yaml":
            holdings = yaml.safe_load(f)
        else:
            holdings = json.load(f)

    return holdings


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


def load_decision_as_reading(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
) -> DecisionReading:
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

    loaded = load_decision(filename=filename, directory=directory, filepath=filepath)
    return readers.read_decision(loaded)
