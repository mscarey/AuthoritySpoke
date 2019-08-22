from dataclasses import dataclass

from typing import ClassVar, Optional

from authorityspoke.entities import Entity
from authorityspoke.factors import Factor
from authorityspoke.facts import Fact


@dataclass(frozen=True)
class Pleading(Factor):
    r"""A document filed by a party to make :class:`Allegation`\s."""

    filer: Optional[Entity] = None
    name: Optional[str] = None
    absent: bool = False
    generic: bool = False
    context_factor_names: ClassVar = ("filer",)

    def __str__(self):
        string = f'{("filed by " + str(self.filer) if self.filer else "")}'
        return super().__str__().format(string)


@dataclass(frozen=True)
class Allegation(Factor):
    """
    A formal assertion of a :class:`Fact`.

    May be included by a party in a :class:`Pleading`
    to establish a cause of action.
    """

    to_effect: Optional[Fact] = None
    pleading: Optional[Pleading] = None
    name: Optional[str] = None
    absent: bool = False
    generic: bool = False
    context_factor_names: ClassVar = ("to_effect", "pleading")

    def __str__(self):
        string = (
            f'{("in " + str(self.pleading) + ",") if self.pleading else ""}'
            + f'{("claiming " + str(self.to_effect) + ",") if self.to_effect else ""}'
        )
        string = string.strip(",")
        return super().__str__().format(string)
