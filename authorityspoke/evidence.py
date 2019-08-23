from dataclasses import dataclass

from typing import ClassVar, Iterator, Optional

from authorityspoke.entities import Entity
from authorityspoke.factors import ContextRegister, Factor
from authorityspoke.facts import Fact


@dataclass(frozen=True)
class Exhibit(Factor):
    """
    A source of information for use in litigation.

    .. note
        "Derived_from" and "offered_by" parameters were removed
        because the former is probably better represented as a :class:`Fact`,
        and the latter as a :class:`Motion`.

    TODO: Allowed inputs for ``form`` will need to be limited.
    """

    form: Optional[str] = None
    statement: Optional[Fact] = None
    stated_by: Optional[Entity] = None
    name: Optional[str] = None
    absent: bool = False
    generic: bool = False
    context_factor_names: ClassVar = ("statement", "stated_by")

    def _means_if_concrete(self, other: Factor) -> Iterator[ContextRegister]:
        if isinstance(other, self.__class__) and self.form == other.form:
            yield from super()._means_if_concrete(other)

    def _implies_if_concrete(self, other: Factor) -> Iterator[ContextRegister]:
        if isinstance(other, self.__class__) and (
            self.form == other.form or other.form is None
        ):
            yield from super()._implies_if_concrete(other)

    def __str__(self):
        string = (
            f'{("by " + str(self.stated_by) + ", ") if self.stated_by else ""}'
            + f'{("asserting " + str(self.statement)) if self.statement else ""}'
        )
        string = super().__str__().format(string)
        return string.replace("exhibit", self.form or "exhibit").strip()


@dataclass(frozen=True)
class Evidence(Factor):
    """An :class:`Exhibit` admitted by a court to aid a factual determination."""

    exhibit: Optional[Exhibit] = None
    to_effect: Optional[Fact] = None
    name: Optional[str] = None
    absent: bool = False
    generic: bool = False
    context_factor_names: ClassVar = ("exhibit", "to_effect")

    def __str__(self):
        string = (
            f'{("of " + str(self.exhibit)) + ", " if self.exhibit else ""}'
            + f'{("which supports " + str(self.to_effect)) if self.to_effect else ""}'
        )
        return super().__str__().format(string).strip()
