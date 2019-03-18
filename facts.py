import operator
from typing import Callable, Dict, List, Set, Tuple
from typing import Iterable, Iterator, Mapping
from typing import Optional, Sequence, Union

from spoke import Factor, Predicate, OPPOSITE_COMPARISONS
from file_import import log_mentioned_context
from entities import Entity

from dataclasses import dataclass

STANDARDS_OF_PROOF = {
    "scintilla of evidence": 1,
    "preponderance of evidence": 2,
    "clear and convincing": 3,
    "beyond reasonable doubt": 4,
}


@dataclass(frozen=True)
class Fact(Factor):
    """An assertion accepted as factual by a court, often through factfinding by
    a judge or jury."""

    # TODO: rename entity_context

    predicate: Optional[Predicate] = None
    entity_context: Tuple[Factor, ...] = ()
    name: Optional[str] = None
    standard_of_proof: Optional[str] = None
    absent: bool = False
    generic: bool = False
    case_factors: Tuple[Factor, ...] = ()

    def __post_init__(self):

        if self.standard_of_proof and self.standard_of_proof not in STANDARDS_OF_PROOF:
            raise ValueError(
                f"standard of proof must be one of {STANDARDS_OF_PROOF.keys()} or None."
            )
        entity_context = self.entity_context
        case_factors = self.case_factors
        object.__delattr__(self, "case_factors")

        if not entity_context:
            entity_context = range(len(self.predicate))
        case_factors = self.__class__.wrap_with_tuple(case_factors)
        entity_context = self.__class__.wrap_with_tuple(entity_context)

        if len(entity_context) != len(self.predicate):
            raise ValueError(
                "The number of items in 'entity_context' must be "
                + f"{len(self.predicate)}, to match predicate.context_slots"
            )

        if any(not isinstance(s, Factor) for s in entity_context):
            if any(not isinstance(s, int) for s in entity_context):
                raise TypeError(
                    "entity_context parameter must contain all integers "
                    + "or all Factor objects."
                )
            if len(case_factors) >= max(entity_context):
                entity_context = tuple(case_factors[i] for i in entity_context)
            else:
                raise ValueError(
                    "Items in the entity_context parameter should "
                    + "be Factor or a subclass of Factor, or should be integer "
                    + "indices of Factor objects in the case_factors parameter."
                )
        object.__setattr__(self, "entity_context", entity_context)

    def __str__(self):
        if self.name:
            string = self.name
        else:
            predicate = str(self.predicate.content_with_entities(self.entity_context))
            standard = (
                f" by the standard {self.standard_of_proof},"
                if self.standard_of_proof
                else ""
            )
            string = (
                f"{'the absence of ' if self.absent else ''}the fact"
                + f"{standard} {predicate}"
            )
        if self.generic:
            return f"<{string}>"
        return string

    @property
    def context_factors(self) -> Tuple[Factor, ...]:
        """
        This function and interchangeable_factors should be the only parts
        of the context-matching process that need to be unique for each
        subclass of Factor. It specifies what attributes of self and other
        to look in to find Factor objects to match.

        For Fact, it returns the entity_context, which can't contain None.
        Other classes should need the annotation Tuple[Optional[Factor], ...]
        instead.
        """

        return self.entity_context

    @property
    def interchangeable_factors(self) -> List[Dict[Factor, Factor]]:
        """
        Yields the ways the context factors referenced by the Fact object
        can be reordered without changing the truth value of the Fact.
        Currently the predicate must be phrased either in a way that doesn't
        make any context factors interchangeable, or if the "reciprocal" flag
        is set, in a way that allows only the first two context factors to switch
        places.

        Each dict returned has factors to replace as keys, and factors to
        replace them with as values. If there's more than one way to
        rearrange the context factors, more than one dict should be returned.
        """
        if self.predicate and self.predicate.reciprocal:
            return [
                {
                    self.entity_context[1]: self.entity_context[0],
                    self.entity_context[0]: self.entity_context[1],
                }
            ]
        return []

    def __eq__(self, other: Factor) -> bool:
        if not isinstance(other, Factor):
            raise TypeError(
                f"{self.__class__} objects may only be compared for "
                + "equality with other Factor objects or None."
            )
        if self.__class__ != other.__class__:
            return False
        if self.generic == other.generic == True:
            return True
        if (
            self.predicate != other.predicate
            or self.standard_of_proof != other.standard_of_proof
            or self.absent != other.absent
            or self.generic != other.generic
        ):
            return False

        context_registers = iter(self.context_register(other, operator.eq))
        return any(register is not None for register in context_registers)

    def make_generic(self) -> "Fact":
        """
        This returns a new object changing generic to True. But it does
        preserve the predicate attribute.
        For a Fact with no features specified, use: Fact(generic=True)
        """

        return Fact(
            predicate=self.predicate,
            entity_context=self.entity_context,
            standard_of_proof=self.standard_of_proof,
            absent=self.absent,
            generic=True,
        )

    def generic_factors(self) -> Dict[Factor, None]:
        """Returns an iterable of self's generic Factors,
        which must be matched to other generic Factors to
        perform equality tests between Factors."""

        if self.generic:
            return {self: None}
        return {
                generic: None
                for factor in self.entity_context
                for generic in factor.generic_factors()
        }

    def predicate_in_context(self, entities: Sequence[Factor]) -> str:
        """Prints the representation of the Predicate with Entities
        added into the slots, with added text from the Fact object
        indicating the class name and whether the Predicate is
        "Absent" or not."""

        return (
            f"{'Absent ' if self.absent else ''}{self.__class__.__name__}: "
            + f"{self.predicate.content_with_entities(entities)}"
        )

    def __len__(self):
        return len(self.entity_context)

    def __gt__(self, other: Optional[Factor]) -> bool:
        """Indicates whether self implies other, taking into account the implication
        test for predicates and whether self and other are labeled 'absent'"""

        if self == other:
            return False
        return self >= other

    def __ge__(self, other: Optional[Factor]) -> bool:
        if other is None:
            return True
        if not isinstance(other, Factor):
            raise TypeError(
                f"{self.__class__} objects may only be compared for "
                + "implication with other Factor objects or None."
            )

        if not isinstance(self, other.__class__):
            return False

        if other.generic:
            return True

        if self.generic:
            return False

        if bool(self.standard_of_proof) != bool(other.standard_of_proof):
            return False

        if (
            self.standard_of_proof
            and STANDARDS_OF_PROOF[self.standard_of_proof]
            < STANDARDS_OF_PROOF[other.standard_of_proof]
        ):
            return False

        if not (self.predicate >= other.predicate and self.absent == other.absent):
            return False

        context_registers = iter(self.context_register(other, operator.ge))
        return any(register is not None for register in context_registers)

    def contradicts(self, other: Optional[Factor]) -> bool:
        """Returns True if self and other can't both be true at the same time.
        Otherwise returns False."""

        if other is None:
            return False
        if not isinstance(other, Factor):
            raise TypeError(
                f"{self.__class__} objects may only be compared for "
                + "contradiction with other Factor objects or None."
            )

        if not isinstance(other, self.__class__):
            return False

        self_implies_other = iter(self.context_register(other, operator.ge))
        if any(register is not None for register in self_implies_other):
            if self.predicate.contradicts(other.predicate) and not (
                self.absent | other.absent
            ):
                return True
            if self.predicate >= other.predicate and other.absent and not self.absent:
                return True

        other_implies_self = iter(self.context_register(other, operator.le))
        if any(register is not None for register in other_implies_self):
            if self.predicate.contradicts(other.predicate) and not (
                self.absent | other.absent
            ):
                return True
            if other.predicate >= self.predicate and self.absent and not other.absent:
                return True
        return False

    def copy_with_foreign_context(self, context_assignment):
        # TODO: move to Factor class, handle inheritance
        new_context = tuple(
            [context_assignment.get(entity) for entity in self.entity_context]
        )
        return Fact(
            predicate=self.predicate,
            entity_context=new_context,
            standard_of_proof=self.standard_of_proof,
            absent=self.absent,
            generic=self.generic,
        )

    @classmethod
    @log_mentioned_context
    def from_dict(
        cls, fact_dict: Optional[Dict[str, Union[str, bool]]], mentioned: List[Factor]
    ) -> Tuple[Optional["Fact"], List[Factor]]:
        """Constructs and returns a Fact object from a dict imported from
        a JSON file in the format used in the "input" folder."""

        if fact_dict.get("type") and fact_dict["type"].lower() != "fact":
            raise ValueError(
                f'"type" value in input must be "fact", not {fact_dict["type"]}'
            )
        context_with_indices: Dict[Factor, int] = {}
        comparison = None
        quantity = None
        if fact_dict.get("content"):
            for factor in mentioned:
                if factor.name and factor.name in fact_dict["content"]:
                    context_with_indices[factor] = fact_dict["content"].find(factor.name)
                    fact_dict["content"] = fact_dict["content"].replace(factor.name, "{}")
            context_factors = sorted(
                context_with_indices,
                key=lambda k: context_with_indices[k],
            )
            for item in OPPOSITE_COMPARISONS:
                if item in fact_dict["content"]:
                    comparison = item
                    fact_dict["content"], quantity = fact_dict["content"].split(item)
                    quantity = Predicate.str_to_quantity(quantity)
                    fact_dict["content"] += "{}"

        # TODO: get default attributes from the classes instead of
        # rewriting them here.
        predicate = Predicate(
            content=fact_dict.get("content"),
            truth=fact_dict.get("truth", True),
            reciprocal=fact_dict.get("reciprocal", False),
            comparison=comparison,
            quantity=quantity
        )

        factor = cls(
            predicate,
            context_factors,
            name=fact_dict.get("name", None),
            standard_of_proof=fact_dict.get("standard_of_proof", None),
            absent=fact_dict.get("absent", False),
            generic=fact_dict.get("generic", False),
        )
        if factor.name:
            mentioned.append(factor)
        return factor, mentioned

    def new_context(
        self,
        changes: Dict[Factor, Factor],
    ) -> Factor:
        """
        Creates a new Fact object, replacing the old entity_context
        attribute with a new one.
        """
        if self in changes:
            return changes[self]
        new_entity_context = []
        for factor in self.entity_context:
            if factor in changes:
                new_entity_context.append(changes[factor])
            else:
                new_entity_context.append(factor)
        return Fact(
            self.predicate,
            tuple(new_entity_context),
            self.name,
            self.standard_of_proof,
            self.absent,
            self.generic,
        )
