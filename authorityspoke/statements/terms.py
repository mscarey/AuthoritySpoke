""":class:`.Comparable` subclass for things that can be referenced in a Statement."""

from __future__ import annotations
from dataclasses import astuple, dataclass
from typing import Callable, Iterator, List, Optional

from authorityspoke.statements.comparable import (
    Comparable,
    ContextRegister,
    new_context_helper,
)


@dataclass()
class Term(Comparable):
    r"""
    Things that can be referenced in a Statement.

    The name of a Term can replace the placeholder in a StatementTemplate

    :param name:
        An identifier. An :class:`Entity` with the same ``name``
        is considered to refer to the same specific object, but
        if they have different names but are ``generic`` and are
        otherwise the same, then they're considered to have the
        same meaning and they evaluate equal to one another.

    :param generic:
        Determines whether a change in the ``name`` of the
        :class:`Entity` would change the meaning of the
        :class:`.Factor` in which the :class:`Entity` is
        embedded.

    :param plural:
        Specifies whether the :class:`Entity` object refers to
        more than one thing. In other words, whether it would
        be represented by a plural noun.
    """

    name: Optional[str] = None
    absent: bool = False
    generic: bool = True
    plural: bool = False

    def __str__(self):
        if self.generic:
            return f"<{self.name}>"
        return self.name
