from dataclasses import dataclass
import operator

from typing import Callable, Dict, List, Set, Tuple
from typing import Iterable, Iterator, Mapping
from typing import Optional, Sequence, Union

from entities import Entity
from spoke import Factor, Fact

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
    absent: bool = False
    generic: bool = False

    def _compare_factor_attributes(self, other, mapping):
        """
        This function should be the only part of the context-matching
        process that needs to be unique for each subclass of Factor.
        It specifies what attributes of self and other to look in to find
        Factor objects to match.
        """
        self_attributes = (self.statement, self.stated_by)
        other_attributes = (other.statement, other.stated_by)

        return self._update_mapping(mapping, self_attributes, other_attributes)

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

        return self._find_matching_context(other, operator.eq)

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
            for factor in (
                self.statement,
                self.stated_by,
            ):
                if factor:
                    for generic_factor in factor.generic_factors():
                        yield generic_factor

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

        return self._find_matching_context(other, operator.ge)

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
    absent: bool = False
    generic: bool = False

    def __hash__(self):
        return hash(
            (
                self.__class__.__name__,
                *[
                    v
                    for v in self.__dict__.values()
                    if not isinstance(v, set) and not isinstance(v, list)
                ],
            )
        )

    def __str__(self):
        if self.exhibit:
            s = str(self.exhibit)
        else:
            s = self.__class__.__name__
        if self.to_effect:
            s += f", which supports {str(self.to_effect)}"
        return s

    def __eq__(self, other):
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

        return self._find_matching_context(other, operator.eq)

    def __gt__(self, other):
        return self >= other and self != other

    def generic_factors(self) -> Iterable[Factor]:
        """Returns an iterable of self's generic Factors,
        which must be matched to other generic Factors to
        perform equality tests between Factors."""

        if self.generic:
            yield self
        else:
            for factor in (
                self.to_effect,
                self.exhibit,
            ):
                if factor:
                    for generic_factor in factor.generic_factors():
                        yield generic_factor

    def _compare_factor_attributes(self, other, mapping):
        """
        This function should be the only part of the context-matching
        process that needs to be unique for each subclass of Factor.
        It specifies what attributes of self and other to look in to find
        Factor objects to match.
        """
        self_attributes = (self.exhibit, self.to_effect)
        other_attributes = (other.exhibit, other.to_effect)

        return self._update_mapping(mapping, self_attributes, other_attributes)

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

        return self._find_matching_context(other, operator.ge)

    def __ge__(self, other):
        if not isinstance(other, Factor):
            raise TypeError(
                f"'Implies' not supported between instances of "
                + f"'{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )

        if self.absent and other.absent:
            return other.implies_if_present(self)

        if self.absent == other.absent == False:
            return self.implies_if_present(other)

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

    def get_entity_orders(self):

        """
        The possible entity arrangements are based on the
        entities for the referenced Predicate statement,
        and the integer local attributes self.stated_by
        and self.derived_from.

        Factor slots should be collected from each parameter
        in the order they're listed:
            self.statement_context
            self.to_effect
            self.stated_by
            self.derived_from

        :returns: a set of tuples indicating the ways the entities
        could be rearranged without changing the meaning of the
        Evidence object.

        """
        int_attrs = list(self.int_attrs) or []

        if self.statement:
            statement_orders = self.statement.entity_orders
        else:
            statement_orders = ((),)

        if self.to_effect:
            effect_orders = self.to_effect.entity_orders
        else:
            effect_orders = ((),)

        entity_orders = set()

        for sc in statement_orders:
            for eo in effect_orders:
                entity_orders.add(tuple(list(sc) + list(eo) + int_attrs))

        return entity_orders

    def from_dict(factor: Optional[dict]) -> Optional["Evidence"]:
        if factor is None:
            return None
        if factor["type"].capitalize() != "Evidence":
            raise ValueError(
                f'"type" value in input must be "evidence", not {factor["type"]}'
            )
        return Evidence(
            form=factor.get("form"),
            to_effect=Fact.from_dict(factor.get("to_effect")),
            statement=Fact.from_dict(factor.get("statement")),
            stated_by=factor.get("stated_by"),
            derived_from=factor.get("derived_from"),
            absent=factor.get("absent"),
        )
