from __future__ import annotations

import functools
import pathlib

from typing import Callable, Dict, Iterable, List
from typing import Optional, Sequence, Tuple, Union


def log_mentioned_context(func: Callable):
    """
    Decorator for :meth:`.Factor.from_dict()` and :meth:`.Enactment.from_dict()`.

    If factor_record is a :class:`str` instead of a :class:`dict`, looks up the
    corresponding factor in "mentioned" and returns that instead of
    constructing a new :class:`Factor`. Also, if the newly-constructed
    :class:`Factor` has a ``name`` attribute, logs the :class:`Factor`
    in ``mentioned`` for later use.
    """

    @functools.wraps(func)
    def wrapper(
        cls,
        factor_record: Union[str, Optional[Dict[str, Union[str, bool]]]],
        mentioned: Optional[List[Union["Factor", "Enactment"]]] = None,
        regime: Optional["Regime"] = None,
    ) -> Tuple[Optional["Factor"], List["Factor"]]:

        if mentioned is None:
            if isinstance(factor_record, str):
                raise TypeError(
                    "No 'mentioned' list exists to search for a Factor "
                    + f"or Enactment by the name '{factor_record}'."
                )
            if factor_record.get("path") or factor_record.get("filename"):
                return func(cls, factor_record, regime)
            else:
                return func(cls, factor_record, mentioned=[], regime=regime)

        if factor_record is None:
            return None, mentioned

        if isinstance(factor_record, str):
            for context_factor in mentioned:
                if (
                    hasattr(context_factor, "name")
                    and context_factor.name == factor_record
                ):
                    return context_factor, mentioned
            raise ValueError(
                f'The object "{factor_record}" should be a dict '
                + "representing a Factor or a string "
                + "representing the name of a Factor included in context_list."
            )
        if factor_record.get("path") or factor_record.get("filename"):
            factor = func(cls, factor_record, regime)
        else:
            factor, mentioned = func(cls, factor_record, mentioned, regime)
        if not factor.name and (not hasattr(factor, "generic") or not factor.generic):
            for context_factor in mentioned:
                if context_factor == factor:
                    return context_factor, mentioned
        mentioned.append(factor)
        mentioned = sorted(
            mentioned, key=lambda f: len(f.name) if f.name else 0, reverse=True
        )
        return factor, mentioned

    return wrapper


def get_directory_path(stem: str) -> pathlib.Path:
    """
    This function finds a data directory for importing files, if
    the current working directory is that directory, is its
    parent directory, or is a sibling
    directory. Otherwise it won't find the right directory.

    This function doesn't obviously belong in the context module.

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
