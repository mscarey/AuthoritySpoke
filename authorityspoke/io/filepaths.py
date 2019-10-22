"""Functions to help locate data to import on disk."""

import pathlib

from typing import Optional


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
        return pathlib.Path(filepath)
    if not directory:
        directory = get_directory_path(default_folder)
    to_append = filename or ""
    return directory / to_append


def get_directory_path(stem: str) -> pathlib.Path:
    """
    Find a data directory for importing files.

    Only in this module temporarily to prevent a circular import.

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
