"""
Entity and its subclasses are subclasses of Factor that represent
people, places, or things. Unlike Facts, Evidence, and Allegations
(which are also subclasses of Factor), Entities don't take Predicates
as parameters, so they won't (probably?) need to incorporate
ordered tuples of other Factors.
"""

from typing import Dict, List, Optional

from spoke import Factor
from file_import import log_mentioned_context

from dataclasses import astuple, dataclass


@dataclass(frozen=True)
class Entity(Factor):
    """A person, place, thing, or event that needs to be mentioned in
    multiple predicates/factors in a holding."""

    name: Optional[str] = None
    generic: bool = True
    plural: bool = False

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
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

    @classmethod
    def from_dict(cls, entity_dict, mentioned):
        factor = cls(name=entity_dict.get("name"),
        generic=entity_dict.get("generic", True),
        plural=entity_dict.get("generic", False))
        return factor, mentioned

    def context_register(
        self, other: Factor, comparison
    ) -> Optional[Dict[Factor, Factor]]:
        """Returns a list of possible ways the context of self can be
        mapped onto the context of other. Other subclasses of Factor
        will have more complex lists."""

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

    def make_generic(self):
        if not self.generic:
            return self.__class__(name=self.name, generic=True, plural=self.plural)
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
