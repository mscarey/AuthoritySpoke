import pathlib


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
