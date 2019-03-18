from dataclasses import dataclass
import operator

from typing import Callable, Dict, List, Set, Tuple
from typing import Iterable, Iterator, Mapping
from typing import Optional, Sequence, Union

from enactments import Enactment
from entities import Entity
from facts import Fact
from file_import import log_mentioned_context
from spoke import Factor


@dataclass(frozen=True)
class Exhibit(Factor):
    """A source of information for use in litigation.

    "derived_from" and and "offered_by" parameters were removed
    because the former is probably better represented as a Fact,
    and the latter as a Motion.

    Allowed inputs for "form" will need to be limited.
    """

    form: Optional[str] = None
    statement: Optional[Fact] = None
    stated_by: Optional[Entity] = None
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

        return (self.statement, self.stated_by)

    @classmethod
    @log_mentioned_context
    def from_dict(
        cls, factor_dict: Dict, mentioned: List[Union[Factor, Enactment]]
    ) -> "Exhibit":
        if factor_dict.get("type").lower() != "exhibit":
            raise ValueError(
                f'"type" value in input must be "exhibit", not {factor_dict.get("type")}'
            )
        statement, mentioned = Fact.from_dict(factor_dict.get("statement"), mentioned)
        stated_by, mentioned = Entity.from_dict(factor_dict.get("stated_by"), mentioned)
        return (
            cls(
                form=factor_dict.get("form"),
                statement=statement,
                stated_by=stated_by,
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
            self.form != other.form
            or self.statement != other.statement
            or self.stated_by != other.stated_by
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

    def generic_factors(self) -> Iterable[Factor]:
        """Returns an iterable of self's generic Factors,
        which must be matched to other generic Factors to
        perform equality tests between Factors."""

        if self.generic:
            yield self
        else:
            collected_factors = [
                generic
                for factor in (self.statement, self.stated_by)
                for generic in factor.generic_factors()
            ]
            for output in set(collected_factors):
                yield output

    def contradicts(self, other: Factor):
        return self >= other.make_absent()

    def implies_if_present(self, other: "Exhibit"):

        if not isinstance(self, other.__class__):
            return False

        if other.generic:
            return True

        if self.generic:
            return False

        if not (self.form == other.form or other.form is None):
            return False

        if other.statement:
            if not (self.statement and self.statement >= other.statement):
                return False

        if other.stated_by:
            if not (self.stated_by and self.stated_by >= other.stated_by):
                return False

        context_registers = iter(self.context_register(other, operator.ge))
        return any(register is not None for register in context_registers)

    def __gt__(self, other: Optional[Factor]) -> bool:
        if other is None:
            return True
        if self == other:
            return False
        return self >= other

    def __str__(self):
        string = (
            f'{"absent " if self.absent else ""}{self.form if self.form else "exhibit"}'
            + f'{(" by " + str(self.stated_by)) if self.stated_by else ""}'
            + f'{(", asserting " + str(self.statement)) if self.statement else ""}'
        )
        if self.generic:
            string = f"<{string}>"
        return string


@dataclass(frozen=True)
class Evidence(Factor):
    """An Exhibit that has been admitted by the court to aid a
    factual determination."""

    exhibit: Optional[Exhibit] = None
    to_effect: Optional[Fact] = None
    name: Optional[str] = None
    absent: bool = False
    generic: bool = False

    def __str__(self):
        if self.exhibit:
            string = str(self.exhibit)
        else:
            string = self.__class__.__name__
        if self.to_effect:
            string += f", which supports {str(self.to_effect)}"
        if self.generic:
            return f"<{string}>"
        return string

    def __eq__(self, other: Factor) -> bool:
        if not isinstance(other, self.__class__):
            return False

        if self.absent != other.absent:
            return False

        if self.generic == other.generic == True:
            return True

        if not (
            self.exhibit == other.exhibit
            and self.to_effect == other.to_effect
            and self.generic == other.generic
        ):
            return False

        context_registers = iter(self.context_register(other, operator.eq))
        return any(register is not None for register in context_registers)

    def __gt__(self, other: Factor) -> bool:
        return self >= other and self != other

    @property
    def context_factors(self) -> Tuple[Optional[Exhibit], Optional[Fact]]:
        """
        This function and interchangeable_factors should be the only parts
        of the context-matching process that need to be unique for each
        subclass of Factor. It specifies what attributes of self and other
        to look in to find Factor objects to match.

        For Fact, it returns the entity_context, which can't contain None.
        Other classes should need the annotation Tuple[Optional[Factor], ...]
        instead.
        """

        return (self.exhibit, self.to_effect)

    def generic_factors(self) -> Iterable[Factor]:
        """Returns an iterable of self's generic Factors,
        which must be matched to other generic Factors to
        perform equality tests between Factors."""

        if self.generic:
            yield self
        else:
            collected_factors = []
            for factor in (self.to_effect, self.exhibit):
                if factor:
                    for generic in factor.generic_factors():
                        collected_factors.append(generic)
            for output in collected_factors:
                yield output

    def implies_if_present(self, other: Factor):
        """Determines whether self would imply other assuming
        both of them have self.absent == False."""

        if not isinstance(self, other.__class__):
            return False

        if other.exhibit:
            if not self.exhibit or not self.exhibit >= other.exhibit:
                return False

        if other.to_effect:
            if not self.to_effect or not self.to_effect >= other.to_effect:
                return False

        context_registers = iter(self.context_register(other, operator.ge))
        return any(register is not None for register in context_registers)

    def __ge__(self, other: Factor) -> bool:
        if not isinstance(other, Factor):
            raise TypeError(
                f"'Implies' not supported between instances of "
                + f"'{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )

        if self.absent and other.absent:
            return bool(other.implies_if_present(self))

        if self.absent == other.absent == False:
            return bool(self.implies_if_present(other))

        return False

    def make_absent(self) -> "Evidence":
        return Evidence(
            exhibit=self.exhibit,
            to_effect=self.to_effect,
            absent=not self.absent,
            generic=self.generic,
        )

    def contradicts(self, other: Optional[Factor]) -> bool:

        if other is None:
            return False

        if not isinstance(other, Factor):
            raise TypeError(
                f"'Contradicts' not supported between instances of "
                + f"'{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )

        if not isinstance(other, self.__class__):
            return False

        if self >= other.make_absent():
            return True

        return other > self.make_absent()

    @classmethod
    @log_mentioned_context
    def from_dict(
        cls, factor_dict: Dict, mentioned: List[Factor]
    ) -> Tuple["Evidence", List[Factor]]:
        if factor_dict["type"].lower() != "evidence":
            raise ValueError(
                f'"type" value in input must be "evidence", not {factor_dict["type"]}'
            )
        if factor_dict.get("exhibit"):
            exhibit = Exhibit.from_dict(factor_dict.get("exhibit"), mentioned)
        else:
            exhibit = None
        if factor_dict.get("to_effect"):
            to_effect = Fact.from_dict(factor_dict.get("to_effect"), mentioned)
        else:
            to_effect = None

        return Evidence(
            exhibit=exhibit,
            to_effect=to_effect,
            name=factor_dict.get("name"),
            absent=factor_dict.get("absent"),
            generic=factor_dict.get("generic"),
        ), mentioned
