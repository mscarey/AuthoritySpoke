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

    :returns:
        a new :class:`.Factor` object in the new context.
    """

    @functools.wraps(func)
    def wrapper(
        factor: Factor, changes: Optional[Union[Sequence[Factor], Dict[Factor, Factor]]]
    ) -> Factor:

        if changes is None:
            return func(factor, changes)
        if not isinstance(changes, Iterable):
            changes = (changes,)
        if not isinstance(changes, dict):
            generic_factors = factor.generic_factors
            if len(generic_factors) != len(changes):
                raise ValueError(
                    'If the parameter "changes" is not a list of '
                    + "replacements for every element of factor.generic_factors, "
                    + 'then "changes" must be a dict where each key is a Factor '
                    + "to be replaced and each value is the corresponding "
                    + "replacement Factor."
                )
            changes = dict(zip(generic_factors, changes))
        for context_factor in changes:
            if factor.name == context_factor or (
                factor.means(context_factor) and factor.name == context_factor.name
            ):
                return changes[context_factor]

        return func(factor, changes)

    return wrapper
