"""Functions for saving objects to file after they have been JSON serialized."""
import json
import pathlib

from typing import Dict, List, Optional, Union

from justopinion.decisions import Decision

from authorityspoke.decisions import Decision
from authorityspoke.io import filepaths


def case_to_file(
    case: Union[Decision, Decision],
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
) -> None:
    r"""
    Save one case from an API response as a JSON file.

    :param results:
        A dict representing a case, in the format
        of the Caselaw Access Project API.

    :param filename:
        Filename (not including the directory) for the
        file where the downloaded opinion should be saved.

    :param directory:
        A :py:class:`~pathlib.Path` object specifying the directory where the
        downloaded opinion should be saved. If ``None`` is given, the current
        default is ``example_data/cases``\.

    :param filepath:
        Complete path to the location where the JSON file should be saved,
        including filename.
    """
    validated_filepath = filepaths.make_filepath(
        filename, directory, filepath, default_folder="cases"
    )
    with open(validated_filepath, "w") as fp:
        fp.write(case.json(indent=4))
