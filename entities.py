"""
Entity and its subclasses are subclasses of Factor that represent
people, places, or things. Unlike Facts, Evidence, and Allegations
(which are also subclasses of Factor), Entities don't take Predicates
as parameters, so they won't (probably?) need to incorporate
ordered tuples of other Factors.
"""

from typing import Optional

from spoke import Factor


class Entity(Factor):
    """A person, place, thing, or event that needs to be mentioned in
    multiple predicates/factors in a holding."""

    def __init__(
        self, name: Optional[str] = None, generic: bool = True, plural: bool = False
    ):
        Factor.__init__(self, name, generic)
        self.plural = plural

    def __str__(self):
        return self.name


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
