r"""
Decorators for memoizing generic :class:`.Factor`\s.

Used when changing an abstract :class:`.Rule` from
one concrete context to another.
"""

from __future__ import annotations

import functools

from typing import Callable, Dict, Iterable
from typing import Optional, Sequence, Union


def new_context_helper(func: Callable):
    r"""
    Search :class:`.Factor` for generic :class:`.Factor`\s to use in new context.

    Decorator for :meth:`Factor.new_context`.

    If a :class:`list` has been passed in rather than a :class:`dict`, uses
    the input as a series of :class:`Factor`\s to replace the
    :attr:`~Factor.generic_factors` from the calling object.

    Also, if ``changes`` contains a replacement for the calling
    object, the decorator returns the replacement and never calls
    the decorated function.

    :param factor:
        a :class:`.Factor` that is having its generic :class:`.Factor`\s
        replaced to change context (for instance, to change to the context
        of a different case involving parties represented by different
        :class:`.Entity` objects).

    :param changes:
        indicates the which generic :class:`.Factor`\s within ``factor`` should
        be replaced and what they should be replaced with.

    :param context_opinion:
        a second object that with generic factors that need to be searched
        when trying to resolve what a string in the `changes` parameter
        refers to.

    :returns:
        a new :class:`.Factor` object in the new context.
    """

    @functools.wraps(func)
    def wrapper(
        factor: Factor,
        changes: Optional[Union[Sequence[Factor], Dict[Factor, Factor]]],
        context_opinion: Optional[Opinion] = None,
    ) -> Factor:

        if changes is None:
            return factor
        if not isinstance(changes, Iterable):
            changes = (changes,)
        if not isinstance(changes, dict):
            generic_factors = factor.generic_factors
            if len(generic_factors) < len(changes):
                raise ValueError(
                    f"The iterable {changes} is too long to be interpreted "
                    + f"as a list of replacements for the "
                    + f"{len(generic_factors)} items of generic_factors."
                )
            changes = dict(zip(generic_factors, changes))

        for context_factor in changes:
            name_to_seek = changes[context_factor]
            if isinstance(name_to_seek, str):
                changes[context_factor] = factor.get_factor_by_name(name_to_seek)
            if context_opinion and not changes[context_factor]:
                changes[context_factor] = context_opinion.get_factor_by_name(
                    name_to_seek
                )
            if not changes[context_factor]:
                raise ValueError(
                    f"Unable to find a Factor with the name '{name_to_seek}'"
                )

            if factor.means(context_factor) and factor.name == context_factor.name:
                return changes[context_factor]

        return func(factor, changes)

    return wrapper
