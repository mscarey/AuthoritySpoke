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
        Factor.__init__(self, generic)
        self.name = name
        self.plural = plural

    def __repr__(self):
        return (f"{self.__class__.__name__}({self.name}"+
        f'{", generic=False" if not self.generic else ""}'+
        f'{", plural=True" if self.plural else ""})')

    def __str__(self):
        if self.generic:
            return f'<{self.name}>'
        return self.name

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
