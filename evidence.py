import operator

from typing import Callable, Dict, List, Set, Tuple
from typing import Iterable, Iterator, Mapping
from typing import Optional, Sequence, Union

from entities import Entity
from spoke import Factor, Fact
from spoke import evolve_match_list


class Evidence(Factor):
    def __init__(
        self,
        form: Optional[str] = None,
        to_effect: Optional[Fact] = None,
        statement: Optional[Fact] = None,
        stated_by: Optional[Entity] = None,
        derived_from: Optional[Entity] = None,
        absent: bool = False,
        generic: bool = False,
    ):

        self.form = form
        self.to_effect = to_effect
        self.statement = statement
        self.stated_by = stated_by
        self.derived_from = derived_from
        self.absent = absent
        self.generic = generic

    def __hash__(self):
        return hash(
            (
                self.__class__.__name__,
                *[v for v in self.__dict__.values() if not isinstance(v, set)],
            )
        )

    def __str__(self):
        if self.form:
            s = self.form
        else:
            s = self.__class__.__name__
        if self.derived_from:
            s += f", derived from <{self.derived_from}>"
        if self.stated_by:
            s += f", with a statement by <{self.stated_by}>, "
        if self.statement:
            s += f', asserting the fact: "{str(self.statement)}"'
        if self.to_effect:
            s += f', supporting the factual conclusion: "{str(self.to_effect)}"'
        return s.capitalize() + "."

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if (self.stated_by is None) != (other.stated_by is None):
            return False

        if self.absent != other.absent:
            return False

        matches = [None for slot in range(max(self.entity_context) + 1)]

        if other.stated_by is not None:
            matches[self.stated_by] = other.stated_by

        if (self.derived_from is None) != (other.derived_from is None):
            return False

        if other.derived_from is not None:
            matches[self.derived_from] = other.derived_from

        if (self.stated_by == self.derived_from) != (
            other.stated_by == other.derived_from
        ):
            return False

        matchlist = {tuple(matches)}

        matchlist = evolve_match_list(
            self.to_effect, other.to_effect, operator.eq, matchlist
        )

        return bool(
            evolve_match_list(self.statement, other.statement, operator.eq, matchlist)
        )

    def __gt__(self, other):
        return self >= other and self != other

    def implies_if_present(self, other):
        """Determines whether self would imply other assuming
        both of them have self.absent == False."""

        if self.form != other.form and other.form is not None:
            return False

        matches = [None for slot in range(max(self.entity_context) + 1)]

        if other.stated_by is not None and self.stated_by is None:
            return False

        if other.stated_by is not None:
            matches[self.stated_by] = other.stated_by

        if other.derived_from is not None and self.derived_from is None:
            return False

        if other.derived_from is not None:
            matches[self.derived_from] = other.derived_from

        if self.absent != other.absent:
            return False

        if not self.to_effect >= other.to_effect:
            return False

        matchset = {tuple(matches)}

        if other.to_effect is not None:
            matchset = {
                m
                for m in find_matches(
                    frozenset([self.to_effect]),
                    {other.to_effect},
                    tuple(matches),
                    operator.ge,
                )
            }
            if not matchset:
                return False

        if self.statement != other.statement and not self.statement > other.statement:
            return False

        if other.statement is None:
            return True

        return any(
            {
                m
                for m in find_matches(
                    frozenset([self.statement]),
                    {other.statement},
                    tuple(match),
                    operator.ge,
                )
            }
            for match in matchset
        )

    def __ge__(self, other):
        if not isinstance(other, Factor):
            raise TypeError(
                f"'Implies' not supported between instances of "
                + f"'{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )
        if not isinstance(other, self.__class__):
            return False

        if self.absent and other.absent:
            return other.implies_if_present(self)

        if self.absent == other.absent == False:
            return self.implies_if_present(other)

        return False

    def make_absent(self) -> "Evidence":
        return Evidence(
            form=self.form,
            to_effect=self.to_effect,
            statement=self.statement,
            stated_by=self.stated_by,
            derived_from=self.derived_from,
            absent=not self.absent,
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

    def __len__(self):

        entities = self.get_entity_orders().pop()
        return len(set(entities))

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
