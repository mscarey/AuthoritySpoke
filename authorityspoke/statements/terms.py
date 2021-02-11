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

    def means(self, other):
        """
        Test whether ``other`` has the same meaning as ``self``.

        ``Generic`` :class:`Entity` objects are considered equivalent
        in meaning as long as they're the same class. If not ``generic``,
        they're considered equivalent if all their attributes are the same.
        """

        if self.__class__ != other.__class__:
            return False
        if self.generic and other.generic:
            return True
        return astuple(self) == astuple(other)

    def __str__(self):
        if self.generic:
            return f"<{self.name}>"
        return self.name

    def _context_register(
        self, other: Comparable, comparison: Callable
    ) -> Iterator[ContextRegister]:
        """
        Find how ``self``\'s context of can be mapped onto ``other``\'s.

        :yields:
            the only possible way the context of one ``Entity`` can be
            mapped onto the context of another.
        """
        if comparison(self, other):
            generic_register = ContextRegister()
            generic_register.insert_pair(self, other)
            generic_register.insert_pair(other, self)
            yield generic_register

    @new_context_helper
    def new_context(self, changes: ContextRegister) -> Term:
        """
        Create new :class:`Factor`, replacing keys of ``changes`` with values.

        Assumes no changes are possible because the :func:`new_context_helper`
        decorator would have replaced ``self`` if any replacement was available.
        """
        return self
