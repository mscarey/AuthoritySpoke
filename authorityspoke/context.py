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

        if isinstance(factor_record, str):
            if mentioned is None:
                raise TypeError(
                    "No 'mentioned' list exists to search for a Factor "
                    + f"or Enactment by the name '{factor_record}'."
                )
            for context_factor in mentioned:
                if (
                    hasattr(context_factor, "name")
                    and context_factor.name == factor_record
                ):
                    return context_factor, mentioned
            raise ValueError(
                "The 'factor_record' parameter should be a dict "
                + "representing a Factor or a string "
                + "representing the name of a Factor included in 'mentioned'."
            )

        if factor_record is None:
            return None, mentioned

        mentioned = mentioned or []

        new_factor = func(cls, factor_record, mentioned=mentioned, regime=regime)

        if not new_factor.name and (
            not hasattr(new_factor, "generic") or not new_factor.generic
        ):
            for context_factor in mentioned:
                if context_factor == new_factor:
                    return context_factor, mentioned
        if hasattr(new_factor, "recursive_factors"):
            factors_to_add = new_factor.recursive_factors
        else:
            factors_to_add = [new_factor]
        for recursive_factor in factors_to_add:
            if recursive_factor not in mentioned:
                mentioned.append(recursive_factor)
        mentioned = sorted(
            mentioned, key=lambda f: len(f.name) if f.name else 0, reverse=True
        )
        return new_factor, mentioned

    return wrapper


def get_directory_path(stem: str) -> pathlib.Path:
    """
    Find a data directory for importing files.

    Will only find the correct directory if it is the current working
    directory is that directory, is its child directory, or is a sibling
    directory. Requires the directory to be found within an ``example_data``
    directory.

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
