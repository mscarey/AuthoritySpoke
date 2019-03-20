from dataclasses import dataclass
import operator

from typing import Callable, Dict, List, Set, Tuple
from typing import Iterable, Iterator, Mapping
from typing import Optional, Sequence, Union

from entities import Entity
from facts import Fact
from file_import import log_mentioned_context
from spoke import Factor


@dataclass(frozen=True)
class Allegation(Factor):
    """
    A formal assertion of a Fact, included by a party in a Pleading
    to establish a cause of action.

    # TODO: inherit generic functions from Factor
    """

    to_effect: Optional[Fact] = None
    pleading: Optional[Factor] = None # update after creating Pleading class
    name: Optional[str] = None
    absent: bool = False
    generic: bool = False

    @property
    def context_factors(self) -> Tuple[Optional[Fact], Optional[Entity]]:
        """
        This function and interchangeable_factors should be the only parts
        of the context-matching process that need to be unique for each
        subclass of Factor. It specifies what attributes of self and other
        to look in to find Factor objects to match.

        For Fact, it returns the entity_context, which can't contain None.
        Other classes should need the annotation Tuple[Optional[Factor], ...]
        instead.
        """

        return (self.to_effect, self.pleading)

    @classmethod
    @log_mentioned_context
    def from_dict(
        cls, factor_dict: Dict, mentioned: List[Union[Factor]]
    ) -> "Allegation":
        if factor_dict.get("type").lower() != "allegation":
            raise ValueError(
                f'"type" value in input must be "allegation", not {factor_dict.get("type")}'
            )
        to_effect, mentioned = Fact.from_dict(factor_dict.get("to_effect"), mentioned)
        pleading, mentioned = Factor.from_dict(factor_dict.get("pleading"), mentioned)
        return (
            cls(
                to_effect=to_effect,
                pleading=pleading,
                name=factor_dict.get("name"),
                absent=factor_dict.get("absent"),
                generic=factor_dict.get("generic"),
            ),
            mentioned,
        )

    def __eq__(self, other: Factor) -> bool:
        if self.__class__ != other.__class__:
            return False

        if self.absent != other.absent:
            return False

        if self.generic == other.generic == True:
            return True

        if (
            self.to_effect != other.to_effect
            or self.pleading != other.pleading
            or self.generic != other.generic
        ):
            return False

        context_registers = iter(self.context_register(other, operator.eq))
        return any(register is not None for register in context_registers)

    def __ge__(self, other: Optional[Factor]) -> bool:
        if other is None:
            return True

        if not isinstance(other, Factor):
            raise TypeError(
                f"'Implies' not supported between instances of "
                + f"'{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )

        if self.absent == other.absent == False:
            return self.implies_if_present(other)
        if self.absent == other.absent == True:
            return other.implies_if_present(self)
        return False

    def generic_factors(self) -> Dict[Factor, None]:
        """Returns an iterable of self's generic Factors,
        which must be matched to other generic Factors to
        perform equality tests between Factors."""

        if self.generic:
            return {self: None}
        return {
            generic: None
            for factor in [x for x in (self.to_effect, self.pleading) if x]
            for generic in factor.generic_factors()
        }

    def contradicts(self, other: Factor):
        return self >= other.make_absent()

    def implies_if_present(self, other: "Allegation"):

        if not isinstance(self, other.__class__):
            return False

        if other.generic:
            return True

        if self.generic:
            return False

        if other.to_effect:
            if not (self.to_effect and self.to_effect >= other.to_effect):
                return False

        if other.pleading:
            if not (self.pleading and self.pleading >= other.pleading):
                return False

        context_registers = iter(self.context_register(other, operator.ge))
        return any(register is not None for register in context_registers)

    def __gt__(self, other: Optional[Factor]) -> bool:
        if other is None:
            return True
        if self == other:
            return False
        return self >= other

    def new_context(self, changes: Dict[Factor, Factor]) -> "Allegation":
        """
        Creates new Factor object, replacing keys of "changes" with their values.
        """
        if self in changes:
            return changes[self]
        to_effect = self.to_effect.new_context(changes) if self.to_effect else None
        pleading = self.pleading.new_context(changes) if self.pleading else None
        return Allegation(
                to_effect=to_effect,
                pleading=pleading,
                name=self.name,
                absent=self.absent,
                generic=self.generic,
            )

    def __str__(self):
        string = (
            f'{"absent " if self.absent else ""}allegation'
            + f'{(" in " + str(self.pleading) if self.pleading else "")}'
            + f'{(", asserting " + str(self.to_effect)) if self.to_effect else ""}'
        )
        if self.generic:
            string = f"<{string}>"
        return string
