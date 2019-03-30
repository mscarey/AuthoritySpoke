import functools
from typing import Callable, Dict, List, Tuple
from typing import Optional, Union


def log_mentioned_context(func: Callable):
    """
    Decorator for make_dict() methods of Factor subclasses.

    If factor_record is a string instead of a dict, looks up the
    corresponding factor in "mentioned" and returns that instead of
    constructing a new Factor. Also, if a newly-constructed Factor
    has a name attribute, logs the factor in "mentioned" for later use.
    """

    @functools.wraps(func)
    def wrapper(
        cls,
        factor_record: Union[str, Optional[Dict[str, Union[str, bool]]]],
        mentioned: List[Union["Factor", "Enactment"]],
    ) -> Tuple[Optional["Factor"], List["Factor"]]:

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
        factor, mentioned = func(cls, factor_record, mentioned)
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
