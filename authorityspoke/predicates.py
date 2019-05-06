from __future__ import annotations

import re

from typing import Any, Callable, Dict, List, Tuple
from typing import ClassVar, Iterable, Iterator, Mapping
from typing import Optional, Sequence, Set, Type, Union

from dataclasses import dataclass

from pint import UnitRegistry

ureg = UnitRegistry()
Q_ = ureg.Quantity

@dataclass(frozen=True)
class Predicate:
    """
    A statement about real events or about a legal conclusion.
    Predicates may be "alleged" by a pleading, "supported" by evidence, or
    "found" to be factual by a jury verdict or a judge's finding of fact.

    A predicate's self.content string shows where references to specific
    entities from the case can be used as subjects or objects of the predicate.

    If self.reciprocal is True, then the order of the first two entities will
    be considered interchangeable. There's no way to make any entities
    interchangeable other than the first two.

    A predicate can also end with a comparison to some quantity, as described
    by a ureg.Quantity object from the pint library. See pint.readthedocs.io.

    If a quantity is defined, a "comparison" should also be defined. That's
    a string indicating whether the thing described by the predicate is
    greater than, less than, or equal to the quantity. Even though "="
    is the default, it's the least useful, because courts almost always state
    rules that are intended to apply to quantities above or below some threshold.

    The quantity comparison can only be mentioned last. No entities may be
    mentioned after the quantity comparison is mentioned.
    """

    content: str
    truth: Optional[bool] = True
    reciprocal: bool = False
    comparison: Optional[str] = None
    quantity: Optional[Union[int, float, ureg.Quantity]] = None
    opposite_comparisons: ClassVar = {
            ">=": "<",
            "==": "!=",
            "<>": "=",
            "<=": ">",
            "=": "!=",
            ">": "<=",
            "<": ">=",
        }

    def __post_init__(self):

        normalize_comparison = {"==": "=", "!=": "<>"}
        if self.comparison in normalize_comparison:
            object.__setattr__(
                self, "comparison", normalize_comparison[self.comparison]
            )

        if self.comparison and self.comparison not in self.opposite_comparisons.keys():
            raise ValueError(
                f'"comparison" string parameter must be one of {self.opposite_comparisons.keys()}.'
            )

        if self.context_slots < 2 and self.reciprocal:
            raise ValueError(
                f'"reciprocal" flag not allowed because "{self.content}" has '
                f"{self.context_slots} spaces for context entities. At least 2 spaces needed."
            )

        if self.comparison and self.truth is False:
            object.__setattr__(self, "truth", True)
            object.__setattr__(
                self, "comparison", self.opposite_comparisons[self.comparison]
            )

    @property
    def context_slots(self) -> int:
        """
        :returns:
            the number of context :class:`Factor`\s that must be
            specified to fill in the blanks in ``self.content``.
        """

        slots = self.content.count("{}")
        if self.quantity:
            slots -= 1
        return slots

    def content_with_entities(self, entities: Union[Factor, Sequence[Factor]]) -> str:
        """Creates a sentence by substituting the names of entities
        from a particular case into the predicate_with_truth."""

        if not isinstance(entities, Iterable):
            entities = (entities,)
        if len(entities) != len(self):
            raise ValueError(
                f"Exactly {len(self)} entities needed to complete "
                + f'"{self.content}", but {len(entities)} were given.'
            )
        return str(self).format(*(str(e) for e in entities))

    def contradicts(self, other: Optional[Predicate]) -> bool:
        """This first tries to find a contradiction based on the relationship
        between the quantities in the predicates. If there are no quantities, it
        returns false only if the content is exactly the same and self.truth is
        different.
        """
        if other is None:
            return False

        if not isinstance(other, self.__class__):
            raise TypeError(
                f"{self.__class__} objects may only be compared for "
                + "contradiction with other {self.__class__} objects or None."
            )

        if (type(self.quantity) == ureg.Quantity) != (
            type(other.quantity) == ureg.Quantity
        ):
            return False

        if self.truth is None or other.truth is None:
            return False

        if (
            isinstance(self.quantity, ureg.Quantity)
            and self.quantity.dimensionality != other.quantity.dimensionality
        ):
            return False

        if not (
            self.content.lower() == other.content.lower()
            and self.reciprocal == other.reciprocal
        ):
            return False

        if self.quantity and other.quantity:
            if (
                ">" in self.comparison or "=" in self.comparison
            ) and "<" in other.comparison:
                if self.quantity > other.quantity:
                    return True
            if (
                "<" in self.comparison or "=" in self.comparison
            ) and ">" in other.comparison:
                if self.quantity < other.quantity:
                    return True
            if ">" in self.comparison and "=" in other.comparison:
                if self.quantity > other.quantity:
                    return True
            if "<" in self.comparison and "=" in other.comparison:
                if self.quantity < other.quantity:
                    return True
            if ("=" in self.comparison) != ("=" in other.comparison):
                if self.quantity == other.quantity:
                    return True
            return False
        return self.content == other.content and self.truth != other.truth

    def __eq__(self, other: Predicate) -> bool:
        if not isinstance(other, self.__class__):
            return False

        if (
            self.content.lower() == other.content.lower()
            and self.reciprocal == other.reciprocal
            and self.quantity == other.quantity
        ):
            return self.truth == other.truth and self.comparison == other.comparison

    @classmethod
    def from_string(
        cls, content: str, truth: Optional[bool] = True, reciprocal: bool = False
    ) -> Tuple[Predicate, Tuple["Factor", ...]]:

        """
        Generates a Predicate object and Entities from a string that
        has curly brackets around the Entities and the comparison/quantity.
        Assumes the comparison/quantity can only come last.
        This may never be used because it's an alternative to
        Fact.from_dict(). This function identifies Entities
        by finding brackets around them, while Fact.from_dict()
        depends on knowing the names of the Entities in advance.
        """

        comparison = None
        quantity = None
        pattern = r"\{([^\{]+)\}"

        entities = re.findall(pattern, content)
        for c in cls.opposite_comparisons:
            if entities[-1].startswith(c):
                comparison = c
                quantity = entities.pop(-1)
                quantity = quantity[2:].strip()
                quantity = cls.str_to_quantity(quantity)

        return (
            Predicate(
                content=re.sub(pattern, "{}", content),
                truth=truth,
                reciprocal=reciprocal,
                comparison=comparison,
                quantity=quantity,
            ),
            tuple(entities),
        )

    def __gt__(self, other: Optional[Predicate]) -> bool:
        """Indicates whether self implies the other predicate,
        which is True if their statements about quantity imply it.
        Returns False if self and other are equal."""

        if other is None:
            return True
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"{self.__class__} objects may only be compared for "
                + f"implication with other {self.__class__} objects or None."
            )

        # Assumes no predicate implies another based on meaning of their content text
        if not (
            self.content.lower() == other.content.lower()
            and self.reciprocal == other.reciprocal
        ):
            return False

        if other.truth is None:
            return True

        if self.truth is None:
            return False

        if not (
            self.quantity and other.quantity and self.comparison and other.comparison
        ):
            return False

        if isinstance(self.quantity, ureg.Quantity) != (
            isinstance(other.quantity, ureg.Quantity)
        ):
            return False

        if (
            isinstance(self.quantity, ureg.Quantity)
            and self.quantity.dimensionality != other.quantity.dimensionality
        ):
            return False

        if "<" in self.comparison and (
            "<" in other.comparison or "=" in other.comparison
        ):
            if self.quantity < other.quantity:
                return True
        if ">" in self.comparison and (
            ">" in other.comparison or "=" in other.comparison
        ):
            if self.quantity > other.quantity:
                return True
        if "=" in self.comparison and "<" in other.comparison:
            if self.quantity < other.quantity:
                return True
        if "=" in self.comparison and ">" in other.comparison:
            if self.quantity > other.quantity:
                return True
        if "=" in self.comparison and "=" in other.comparison:
            if self.quantity == other.quantity:
                return True
        if "=" not in self.comparison and "=" not in other.comparison:
            if self.quantity == other.quantity:
                return True
        return False

    def __ge__(self, other: Predicate) -> bool:
        if self == other:
            return True
        return self > other


    def __len__(self):
        """
        :returns:
            the number of entities that can fit in the pairs of brackets
            in the predicate. ``self.quantity`` doesn't count as one of these entities,
            even though the place where ``self.quantity`` goes in represented by brackets
            in the ``self.content`` string.

        Also called the linguistic valency, arity, or adicity.
        """

        return self.context_slots

    def quantity_comparison(self) -> str:
        """String representation of a comparison with a quantity,
        which can include units due to the pint library."""

        if not self.quantity:
            return None
        comparison = self.comparison or "="
        expand = {
            "=": "exactly equal to",
            "!=": "not equal to",
            ">": "greater than",
            "<": "less than",
            ">=": "at least",
            "<=": "no more than",
        }
        return f"{expand[comparison]} {self.quantity}"

    def negated(self) -> Predicate:
        """
        Returns a copy of the same Predicate, but with the opposite
        truth value.
        """

        return Predicate(
            content=self.content,
            truth=not self.truth,
            reciprocal=self.reciprocal,
            comparison=self.comparison,
            quantity=self.quantity,
        )

    def __str__(self):
        if self.truth is None:
            truth_prefix = "whether "
        elif self.truth is False:
            truth_prefix = "it is false that "
        else:
            truth_prefix = ""
        if self.quantity:
            slots = ("{}" for slot in range(len(self)))
            content = self.content.format(*slots, self.quantity_comparison())
        else:
            content = self.content
        return f"{truth_prefix}{content}"


    @staticmethod
    def str_to_quantity(quantity: str) -> Union[float, int, ureg.Quantity]:
        """
        :param quantity:
            when a string is being parsed for conversion to a
            :class:`Predicate`, this is the part of the string
            after the equals or inequality sign.
        :returns:
            a Python number object or a :class:`Quantity`
            object created with `pint.UnitRegistry
            <https://pint.readthedocs.io/en/0.9/tutorial.html>`_.
        """
        quantity = quantity.strip()
        if quantity.isdigit():
            return int(quantity)
        float_parts = quantity.split(".")
        if len(float_parts) == 2 and all(
            substring.isnumeric() for substring in float_parts
        ):
            return float(quantity)
        return Q_(quantity)
