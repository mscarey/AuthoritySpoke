"""
Entity and its subclasses are subclasses of Factor that represent
people, places, or things. Unlike Facts, Evidence, and Allegations
(which are also subclasses of Factor), Entities don't take Predicates
as parameters, so they won't (probably?) need to incorporate
ordered tuples of other Factors.
"""

from typing import Dict, List, Optional

from spoke import Factor

from dataclasses import astuple, dataclass


@dataclass(frozen=True)
class Entity(Factor):
    """A person, place, thing, or event that needs to be mentioned in
    multiple predicates/factors in a holding."""

    name: Optional[str] = None
    generic: bool = True
    plural: bool = False

    @classmethod
    def new(
        cls, name: Optional[str] = None, generic: bool = True, plural: bool = False
    ):
        """Placeholder for normalizing inputs before initializing."""
        return cls(name, generic, plural)


    def __eq__(self, other: Optional[Factor]):
        if type(self) != type(other):
            return False
        if self.generic and other.generic:
            return True
        return astuple(self) == astuple(other)

    def __ge__(self, other: Optional[Factor]):
        return self == other or self > other

    def __gt__(self, other: Optional[Factor]):
        if other is None:
            return True
        if not isinstance(self, other.__class__):
            return False
        if self == other:
            return False
        if self.generic == False and self.name == other.name:
            return True
        return other.generic

    def __str__(self):
        if self.generic:
            return f"<{self.name}>"
        return self.name

    def context_register(self, other: Factor, comparison) -> Optional[Dict[Factor, Factor]]:
        """Returns a list of possible ways the context of self can be
        mapped onto the context of other. Other subclasses of Factor
        will have more complex lists."""
        if comparison(self, other) and (self.generic or other.generic):
            return {self: other, other: self}
        return None

    def make_generic(self):
        if not self.generic:
            return self.__class__(name=self.name, generic=True, plural=self.plural)
        else:
            return self


class Human(Entity):
    """
    A "natural person" mentioned as an entity in a factor. On the distinction
    between "human" and "person", see Slaughter-House Cases, 83 U.S. 36, 99.
    https://www.courtlistener.com/opinion/88661/slaughter-house-cases/
    """

    pass


class Event(Entity):
    """
    Events may be referenced as entities in a predicate's content.
    See Lepore, Ernest. Meaning and Argument: An Introduction to Logic
    Through Language. Section 17.2: The Event Approach
    """
