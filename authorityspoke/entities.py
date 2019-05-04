"""
Entity and its subclasses are subclasses of Factor that represent
people, places, or things. Unlike Facts, Evidence, and Allegations
(which are also subclasses of Factor), Entities don't take Predicates
as parameters, so they won't (probably?) need to incorporate
ordered tuples of other Factors.
"""
from __future__ import annotations

from typing import Dict, Iterator, Optional

from authorityspoke.factors import Factor, new_context_helper

from dataclasses import astuple, dataclass


@dataclass(frozen=True)
class Entity(Factor):
    """
    A person, place, thing, or event that needs to be mentioned in
    multiple :class:`Factor`\s in a :class:`Rule`, often in the
    :class:`Predicate` of a :class:`Fact` object.

    An :class:`Entity` is often, but not always, ``generic`` with
    respect to the meaning of the :class:`Rule` in which it is
    mentioned, which means that the :class:`Rule` is understood
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
        :class:`Factor` in which the :class:`Entity` is
        embedded.

    :param plural:
        Specifies whether the :class:`Entity` object refers to
        more than one thing. In other words, whether it would
        be represented by a plural noun.
    """

    name: Optional[str] = None
    generic: bool = True
    plural: bool = False

    def __eq__(self, other):
        """
        ``generic`` :class:`Entity` objects are considered equal
        as long as they're the same class. If not ``generic``, they're
        considered equal if all their attributes are the same.
        """

        if self.__class__ != other.__class__:
            return False
        if self.generic and other.generic:
            return True
        return astuple(self) == astuple(other)

    def __ge__(self, other: Optional[Factor]):
        if other is None:
            return True
        if not isinstance(self, other.__class__):
            return False
        if self.generic == False and self.name == other.name:
            return True
        return other.generic

    def __str__(self):
        if self.generic:
            return f"<{self.name}>"
        return self.name

    def _context_register(
        self, other: Factor, comparison
    ) -> Iterator[Dict[Factor, Factor]]:
        """
        :yields:
            possible ways the context of ``self`` can be
            mapped onto the context of ``other``.
        """

        # If there was a way to compare an Entity to None, should it return {}?
        if comparison(self, other):
            yield {self: other, other: self}

    def contradicts(self, other: Factor) -> bool:
        if not isinstance(other, Factor):
            raise TypeError(
                f"'Contradicts' not supported between class "
                + f"{self.__class__.__name__} and class {other.__class__.__name__}."
            )
        return False

    @new_context_helper
    def new_context(self, context: Dict[Factor, Factor]) -> Entity:
        return self

class Association(Entity):
    """
    An entity representing a set of people such as members or shareholders,
    or a business such as a corporation or LLC, but not an unincorporated
    business such as a sole proprietorship.
    """

class Human(Entity):
    """
    A "natural person" mentioned as an entity in a factor. On the distinction
    between "human" and "person", see Slaughter-House Cases, 83 U.S. 36, 99.
    https://www.courtlistener.com/opinion/88661/slaughter-house-cases/
    """


class Event(Entity):
    """
    Events may be referenced as entities in a predicate's content.
    See Lepore, Ernest. Meaning and Argument: An Introduction to Logic
    Through Language. Section 17.2: The Event Approach
    """
