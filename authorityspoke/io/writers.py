"""Functions for saving objects to file after they have been JSON serialized."""
import json
import pathlib

from typing import Dict, List, Optional

from authorityspoke.io import filepaths


def case_to_file(
    case: Dict,
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
        json.dump(case, fp, ensure_ascii=False, indent=4)


def cases_to_file(
    results: List[Dict],
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
) -> None:
    """
    Save cases from an API response as JSON files.

    :param results:
        A list of dicts representing cases, in the format
        of the Caselaw Access Project API.

    :param filename:
        Filename (not including the directory) for the
        file where the downloaded opinion should be saved.

    :param directory:
        A :py:class:`~pathlib.Path` object specifying the directory where the
        downloaded opinion should be saved. If ``None`` is given, the current
        default is ``example_data/cases``.

    :param filepath:
        Complete path to the location where the JSON file should be saved,
        including filename.
    """
    for number, case in enumerate(results):
        if not filename:
            mangled_filename = f'{case["id"]}.json'
        else:
            mangled_filename = filename
            if number > 0:
                mangled_filename = mangled_filename.replace(".", f"_{number}.")
        case_to_file(
            case=case, filename=mangled_filename, directory=directory, filepath=filepath
        )
    return None
