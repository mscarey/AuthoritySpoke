""":class:`.Factor` subclass for things that exist in the outside world."""

from __future__ import annotations
from dataclasses import astuple, dataclass, field
from typing import Iterator, List, Optional

from anchorpoint import TextQuoteSelector

from authorityspoke.comparisons import ContextRegister, new_context_helper
from authorityspoke.factors import Factor


@dataclass()
class Entity(Factor):
    r"""
    Things that exist in the outside world, like people, places, or events.

    Not concepts that derive their meaning from litigation,
    such as a legal Fact, an Allegation, a Pleading, etc.

    Best used to specify things to be mentioned in
    multiple :class:`.Factor`\s in a :class:`.Rule`, often in the
    :class:`.Predicate` of a :class:`.Fact` object.

    An :class:`Entity` is often, but not always, ``generic`` with
    respect to the meaning of the :class:`.Rule` in which it is
    mentioned, which means that the :class:`.Rule` is understood
    to apply generally even if some other :class:`Entity` was
    substituted.

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
    generic: bool = True
    plural: bool = False
    anchors: List[TextQuoteSelector] = field(default_factory=list)

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

    def __ge__(self, other: Optional[Factor]):
        if other is None:
            return True
        if not isinstance(other, Entity):
            return False
        if self.generic is False and self.name == other.name:
            return True
        return other.generic

    def __str__(self):
        if self.generic:
            return f"<{self.name}>"
        return self.name

    def _context_register(self, other: Factor, comparison) -> Iterator[ContextRegister]:
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
    def new_context(self, changes: ContextRegister) -> Entity:
        """
        Create new :class:`Factor`, replacing keys of ``changes`` with values.

        Assumes no changes are possible because the :func:`new_context_helper`
        decorator would have replaced ``self`` if any replacement was available.
        """
        return self
