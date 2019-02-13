import itertools
import operator
import re

from typing import Callable, Dict, FrozenSet, List, Set, Tuple
from typing import Iterable, Iterator
from typing import Optional, Sequence, Union

from pint import UnitRegistry

from dataclasses import dataclass

ureg = UnitRegistry()
Q_ = ureg.Quantity

OPPOSITE_COMPARISONS = {
    ">=": "<",
    "==": "!=",
    "<>": "=",
    "<=": ">",
    "=": "!=",
    ">": "<=",
    "<": ">=",
}


class Factor:
    """A factor is something used to determine the applicability of a legal
    procedure. Factors can be both inputs and outputs of legal procedures.
    In a chain of legal procedures, the outputs of one may become inputs for
    another. Common types of factors include Facts, Evidence, Allegations,
    Motions, and Arguments."""

    def __init__(self, generic: bool = True):
        self.generic = generic

    @classmethod
    def from_dict(cls, factor: dict) -> "Factor":
        """
        Turns a dict recently created from a chunk of JSON into a Factor object.
        """

        # TODO: make subclass search recursive, or make a different factory function
        class_options = cls.__subclasses__()
        for c in class_options:
            cname = factor.get("type", "")
            if cname.capitalize() == c.__name__:
                return c.from_dict(factor)
        raise ValueError(
            f'"type" value in input must be one of {class_options}, not {cname}'
        )

    def __eq__(self, other: "Factor") -> bool:
        if self.__class__ != other.__class__:
            return False
        if self.generic == other.generic == True:
            return True
        return self.__dict__ == other.__dict__

    def __gt__(self, other: "Factor") -> bool:
        if self == other:
            return False
        if isinstance(self, other.__class__):
            if other.generic:
                return True
        return False

    def __hash__(self):
        return hash(
            (
                self.__class__.__name__,
                *[v for v in self.__dict__.values() if not isinstance(v, set)],
            )
        )


@dataclass()
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

    def __post_init__(self):
        if len(self) < 2 and self.reciprocal:
            raise ValueError(
                f'"reciprocal" flag not allowed because {self.content} '
                f"has {len(self)} entities, fewer than 2."
            )
        # Assumes that the obverse of a statement about a quantity is
        # necessarily logically equivalent
        if self.comparison == "==":
            object.__setattr__(self, "comparison", "=")
        if self.comparison == "!=":
            object.__setattr__(self, "comparison", "<>")
        if self.comparison and self.truth is False:
            object.__setattr__(self, "truth", True)
            object.__setattr__(
                self, "comparison", OPPOSITE_COMPARISONS[self.comparison]
            )
        if self.comparison and self.comparison not in OPPOSITE_COMPARISONS.keys():
            raise ValueError(
                f'"comparison" string parameter must be one of {OPPOSITE_COMPARISONS.keys()}.'
            )
        # TODO: prevent len() from breaking when there's an entity
        # reference between the brackets in the text.

        slots = self.content.count("{}")
        if self.quantity:
            slots -= 1
        object.__setattr__(self, "entity_context", tuple(range(slots)))
        object.__setattr__(
            self, "entity_orders", self.get_entity_orders(self.entity_context)
        )
        return slots

    @staticmethod
    def from_string(
        content: str, truth: Optional[bool] = True, reciprocal: bool = False
    ) -> Tuple["Predicate", Tuple[Factor, ...]]:

        """Generates a Predicate object and Entities from a string that
        has curly brackets around the Entities and the comparison/quantity.
        Assumes the comparison/quantity can only come last."""

        comparison = None
        quantity = None
        pattern = r"\{([^\{]+)\}"

        entities = re.findall(pattern, content)
        for c in OPPOSITE_COMPARISONS:
            if entities[-1].startswith(c):
                comparison = c
                quantity = entities.pop(-1)
                quantity = quantity[2:].strip()
                if quantity.isdigit():
                    quantity = int(quantity)
                elif quantity.isdecimal():
                    quantity = float(quantity)
                else:
                    quantity = Q_(quantity)

        entities = (Factor(e) for e in entities)

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

    def __len__(self):
        """
        Returns the number of entities that can fit in the pairs of brackets
        in the predicate. self.quantity doesn't count as one of these entities,
        even though the place where self.quantity goes in represented by brackets
        in the "content" string.

        Also called the linguistic valency, arity, or adicity.
        """

        slots = self.content.count("{}")
        if self.quantity:
            slots -= 1
        return slots

    def __str__(self):
        truth_prefix = "it is false that " if not self.truth else ""
        if self.quantity:
            slots = ("{}" for slot in range(len(self)))
            content = self.content.format(*slots, self.quantity_comparison())
        else:
            content = self.content
        return f"{truth_prefix}{content}"

    def __eq__(self, other: "Predicate") -> bool:
        if not isinstance(other, self.__class__):
            return False

        if (
            self.content.lower() == other.content.lower()
            and self.reciprocal == other.reciprocal
            and self.quantity == other.quantity
        ):
            if self.truth == other.truth and self.comparison == other.comparison:
                return True  # Equal if everything is same
            if (
                self.comparison
                and OPPOSITE_COMPARISONS[self.comparison] == other.comparison
                and (
                    (self.truth == True and other.truth == False)
                    or (self.truth == False and other.truth == True)
                )
            ):
                # Equal if everything is same except obverse quantity statement.
                return True
        return False

    def __gt__(self, other: "Predicate") -> bool:
        """Indicates whether self implies the other predicate,
        which is True if their statements about quantity imply it.
        Returns False if self and other are equal."""

        if not isinstance(other, self.__class__):
            return False

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

    def __ge__(self, other: "Predicate") -> bool:
        if self == other:
            return True
        return self > other

    def __hash__(self):
        return hash(
            (
                self.__class__.__name__,
                *[v for v in self.__dict__.values() if not isinstance(v, set)],
            )
        )

    def contradicts(self, other: "Predicate") -> bool:
        """This first tries to find a contradiction based on the relationship
        between the quantities in the predicates. If there are no quantities, it
        returns false only if the content is exactly the same and self.truth is
        different.
        """
        if not isinstance(other, self.__class__):
            return False

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

        if not (self.content == other.content and self.reciprocal == other.reciprocal):
            return False

        if self.quantity and other.quantity:
            if (
                "<" in self.comparison or "=" in self.comparison
            ) and "<" in other.comparison:
                if self.quantity > other.quantity:
                    return True
            if (
                ">" in self.comparison or "=" in self.comparison
            ) and ">" in other.comparison:
                if self.quantity < other.quantity:
                    return True
            if ">" in self.comparison and "=" in other.comparison:
                if self.quantity > other.quantity:
                    return True
            if "<" in self.comparison and "=" in other.comparison:
                if self.quantity < other.quantity:
                    return True
            if "=" in self.comparison and "=" not in other.comparison:
                if self.quantity == other.quantity:
                    return True
            if "=" not in self.comparison and "=" in other.comparison:
                if self.quantity != other.quantity:
                    return True
            return False
        return self.content == other.content and self.truth != other.truth

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

    def content_with_entities(
        self, entities: Union[Factor, Sequence[Union[int, Factor]]]
    ) -> str:
        """Creates a sentence by substituting the names of entities
        from a particular case into the predicate_with_truth."""

        if isinstance(entities, Factor):
            entities = (entities,)
        if len(entities) != len(self):
            raise ValueError(
                f"Exactly {len(self)} entities needed to complete "
                + f'"{self.content}", but {len(entities)} were given.'
            )
        if any(isinstance(item, int) for item in entities):
            names = [f"<{item}>" for item in entities]
        else:
            names = [
                f"<{str(item)}>" if item.generic else str(item) for item in entities
            ]
        return str(self).format(*(str(e) for e in names))

    def negated(self) -> "Predicate":
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

    def get_entity_orders(self, entity_context):
        """
        Currently the only possible rearrangement is to swap the
        order of the first two entities if self.reciprocal.

        :returns: a set of tuples indicating the ways the entities
        could be rearranged without changing the meaning of the predicate.

        """

        orders = {entity_context}

        if self.reciprocal:
            swapped = tuple([1, 0] + [n for n in range(2, len(self))])
            orders.add(swapped)

        return orders

    # TODO: allow the same entity to be mentioned more than once


def check_entity_consistency(
    left: Factor, right: Factor, matches: tuple
) -> Set[Tuple[int, ...]]:
    """
    Given entity assignments for self and other, determines whether
    the factors have consistent entity assignments such that both can
    be true at the same time.

    All of self's entities must match other's, but other may have entities
    that don't match self.

    :param other:

    :param matches: a tuple the same length as len(self). The indices represent
    self's entity slots, and the value at each index represents other's
    corresponding entity slots that have already been assigned, if any.

    :returns: a set containing self's normal entity tuple, self's reciprocal
    entity tuple, both, or neither, depending on which ones match with other.
    """

    def all_matches(self_order: Tuple[int], other_order: Tuple[int]) -> bool:
        """
        Determines whether the entity slots assigned so far are
        consistent for the Factors designated self and other,
        regardless of whether it's possible to make consistent
        assignments for the remaining slots.
        """
        m = list(matches)
        for i, slot in enumerate(other_order):
            if m[slot] == self_order[i] or m[slot] is None:
                m[slot] = self_order[i]
            else:
                return False
        return True

    if not isinstance(right, left.__class__):
        raise TypeError(f"other must be type Factor")

    answers = set()

    for self_order in left.entity_orders:
        for other_order in right.entity_orders:
            if all_matches(self_order, other_order):
                answers.add(self_order)

    return answers


def find_matches(
    for_matching: FrozenSet[Factor],
    need_matches: Set[Factor],
    matches: Tuple[Optional[int], ...],
    comparison: Callable[[Factor, Factor], bool],
) -> Iterator[Tuple[Optional[int], ...]]:
    """
    Generator that recursively searches for a tuple of entity
    assignments that can cause all of 'need_matches' to satisfy
    the relation described by 'comparison' with a factor
    from for_matching.

    :param for_matching: A frozenset of all of self's factors. These
    factors aren't removed when they're matched to a factor from other,
    because it's possible that one factor in self could imply two
    different factors in other.

    :param need_matches: A set of factors from other that have
    not yet been matched to any factor from self.

    :param matches: A tuple showing which factors from
    for_matching have been matched.

    :param comparison: A function used to filter the for_matching
    factors into the "available" collection. A factor must have
    the "comparison" relation with the factor from the need_matches
    set to be included as "available".

    :returns: iterator that yields tuples of entity assignments that can
    cause all of 'need_matches' to satisfy the relation described by
    'comparison' with a factor from for_matching.
    """

    if not need_matches:
        yield matches
    else:
        need_matches = set(need_matches)
        n = need_matches.pop()
        available = {a for a in for_matching if comparison(a, n)}
        for a in available:
            matches_found = check_entity_consistency(n, a, matches)
            for source_list in matches_found:
                matches_next = list(matches)
                for i in range(len(a)):
                    if comparison == operator.le:
                        matches_next[source_list[i]] = a.entity_context[i]
                    else:
                        matches_next[a.entity_context[i]] = source_list[i]
                matches_next = tuple(matches_next)
                for m in find_matches(
                    for_matching, frozenset(need_matches), matches_next, comparison
                ):
                    yield m


def evolve_match_list(
    available: FrozenSet[Factor],
    need_matches: FrozenSet[Factor],
    comparison: Callable[[Factor, Factor], bool],
    prior_matches: FrozenSet[Tuple[Optional[int], ...]],
) -> FrozenSet[Tuple[Optional[int], ...]]:

    """
    Takes all the tuples of entity assignments in prior_matches, and
    updates them with every consistent tuple of entity assignments
    that would cause every Factor in need_matches to be related to
    a Factor in "available" by the relation described by "comparison".
    """
    if isinstance(available, Factor):
        available = frozenset([available])
    if isinstance(need_matches, Factor):
        need_matches = {need_matches}

    new_matches = set()
    for m in prior_matches:
        for y in find_matches(available, need_matches, m, comparison):
            new_matches.add(y)
    return frozenset(new_matches)


STANDARDS_OF_PROOF = {
    "scintilla of evidence": 1,
    "preponderance of evidence": 2,
    "clear and convincing": 3,
    "beyond reasonable doubt": 4,
}


class Fact(Factor):
    """An assertion accepted as factual by a court, often through factfinding by
    a judge or jury."""

    # TODO: rename entity_context

    def __init__(
        self,
        predicate: Optional[Predicate] = None,
        entity_context: Union[Factor, Iterable[Factor], int, Iterable[int]] = (),
        standard_of_proof: Optional[str] = None,
        absent: bool = False,
        generic: bool = False,
        case_factors: Iterable[Factor] = (),
    ):

        Factor.__init__(self, generic)
        self.predicate = predicate
        self.standard_of_proof = standard_of_proof
        self.absent = absent
        self.generic = generic

        def wrap_with_tuple(item) -> Tuple[Union[int, Factor], ...]:
            if isinstance(item, list):
                return tuple(item)
            if not isinstance(item, tuple):
                return (item,)
            return item

        case_factors = wrap_with_tuple(case_factors)
        self.entity_context = wrap_with_tuple(entity_context)

        if any(not isinstance(s, Factor) for s in self.entity_context):
            if any(not isinstance(s, int) for s in self.entity_context):
                raise TypeError(
                    "entity_context parameter must contain all integers "
                    + "or all Factor objects."
                )
            if len(case_factors) >= max(self.entity_context):
                self.entity_context = tuple(
                    case_factors[i] for i in self.entity_context
                )
            else:
                raise ValueError(
                    "Items in the entity_context parameter should "
                    + "be Factor or a subclass of Factor, or should be integer "
                    + "indices of Factor objects in the case_factors parameter."
                )

        if predicate and len(self.entity_context) < len(predicate):
            if len(case_factors) < len(predicate):
                raise ValueError(
                    f"Must supply exactly {len(self.predicate)} "
                    + "factor(s) to fill the slots in self.predicate, either "
                    + "as entity_context or case_factors."
                )
            self.entity_context = case_factors[: len(predicate)]

        self.entity_orders = self.get_entity_orders()

        if self.standard_of_proof and self.standard_of_proof not in STANDARDS_OF_PROOF:
            raise ValueError(
                f"standard of proof must be one of {STANDARDS_OF_PROOF.keys()} or None."
            )

    def __hash__(self):
        """
        Even though this is duplicative, it needs to be here as long as the
        class defines its own __eq__ function.
        """

        return hash(
            (
                self.__class__.__name__,
                *[v for v in self.__dict__.values() if not isinstance(v, set)],
            )
        )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({repr(self.predicate)}, {self.entity_context}, "
            + f"{self.standard_of_proof}, absent={self.absent}, generic={self.generic})"
        )

    def __str__(self):
        predicate = str(self.predicate.content_with_entities(self.entity_context))
        standard = f" ({self.standard_of_proof})" if self.standard_of_proof else ""
        return (
            f"{'Absent ' if self.absent else ''}{self.__class__.__name__}"
            + f"{standard}: {predicate}"
        )

    def __eq__(self, other: "Factor") -> bool:
        if self.__class__ != other.__class__:
            return False
        if self.generic == other.generic == True:
            return True
        return (
            self.predicate == other.predicate
            and all(
                row[0] == row[1]
                for row in zip(self.entity_context, other.entity_context)
            )
            and self.standard_of_proof == other.standard_of_proof
            and self.absent == other.absent
            and self.generic == other.generic
        )

    def make_generic(self) -> "Fact":
        """
        This changes generic to True and calls make_generic recursively
        on all the Factors in entity_context. But it does preserve the
        predicate attribute. For a Fact with no features specified, use:

        Fact(generic=True)
        """
        new_context = tuple([f.make_generic() for f in self.entity_context])
        return Fact(
            predicate=self.predicate,
            entity_context=new_context,
            standard_of_proof=None,
            absent=self.absent,
            generic=True,
        )

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

    def __ge__(self, other: Optional["Fact"]) -> bool:
        if other is None:  # TODO: remember why this is here
            return True

        if not isinstance(other, Factor):
            raise TypeError(
                f"'Implies' not supported between instances of "
                + f"'{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )

        if not isinstance(self, other.__class__):
            return False

        if self == other:
            return False

        if other.generic:
            return True

        if bool(self.standard_of_proof) != bool(other.standard_of_proof):
            return False

        if (
            self.standard_of_proof
            and STANDARDS_OF_PROOF[self.standard_of_proof]
            < STANDARDS_OF_PROOF[other.standard_of_proof]
        ):
            return False

        if self.predicate >= other.predicate and self.absent == other.absent:
            return True
        return False

    def contradicts(self, other: Optional[Factor]) -> bool:
        """Returns True if self and other can't both be true at the same time.
        Otherwise returns False."""

        if other is None:
            return False

        if not isinstance(other, Factor):
            raise TypeError(
                f"'Contradicts' not supported between instances of "
                + f"'{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )

        if not isinstance(other, self.__class__):
            return False

        if self.predicate.contradicts(other.predicate) and not (
            self.absent | other.absent
        ):
            return True
        if self.predicate >= other.predicate and other.absent and not self.absent:
            return True
        if other.predicate >= self.predicate and self.absent and not other.absent:
            return True
        return False

    def consistent_entity_combinations(
        self, factors_from_other_procedure, matches
    ) -> List[Dict]:
        """Finds all possible entity marker combinations for self that
        don't result in a contradiction with any of the factors of
        other. The time to call this function
        repeatedly during a recursive search should explode
        as the possibilities increase, so it should only be run
        when matches has been narrowed as much as possible."""

        answer = []
        for source_list in self.entity_orders:
            available_slots = {
                i: [
                    slot
                    for slot in matches
                    if slot is not None
                    and (matches[slot] is None or matches[slot] == source_list[i])
                ]
                for i in range(len(self))
            }
            keys, values = zip(*available_slots.items())
            combinations = (
                dict(zip(keys, v))
                for v in itertools.product(*values)
                if len(v) == len(set(v))
            )
            for c in combinations:
                if not any(
                    (
                        a.contradicts(self) and (a.entity_context[i] == c[i] for i in c)
                        for a in factors_from_other_procedure
                    )
                ):
                    answer.append(c)
        return answer

    def get_entity_orders(self) -> Set[Tuple[int, ...]]:

        """
        Currently the only possible arrangements are derived from
        the predicate attribute.

        Each tuple in the returned set is an ordering of
        self.entity_context, using the indices from one of
        self.predicate.entity_orders.

        :returns: a set of tuples indicating the ways the entities
        could be rearranged without changing the meaning of the Fact.

        """

        if self.predicate:
            return set(
                tuple([x for i, x in sorted(zip(order, self.entity_context))])
                for order in self.predicate.entity_orders
            )
        return set()

    @staticmethod
    def from_dict(factor: Optional[dict]) -> Optional["Fact"]:
        if factor is None:
            return None
        if factor["type"].capitalize() != "Fact":
            raise ValueError(
                f'"type" value in input must be "fact", not {factor["type"]}'
            )
        predicate, entities = Predicate.from_string(
            content=factor.get("content"),
            truth=factor.get("truth", True),
            reciprocal=factor.get("reciprocal", False),
        )
        yield Fact(
            predicate,
            entities,
            factor.get("absent", False),
            factor.get("standard_of_proof", None),
        )

        for entity in entities:
            yield entity

    def make_abstract(self, entity_slots: Iterable[Factor]) -> "Fact":
        """
        Creates a new Fact object, this time with numbered
        entity slots instead of actual entities. The indices of
        the Entities in entity_slots correspond to the numbers
        that will be assigned to the slots in the new object's
        self.entity_context.
        """

        if any(not isinstance(s, Factor) for s in entity_slots):
            raise TypeError(
                "entity_slots must be an interable containing only Factor objects."
            )
        if any(e not in entity_slots for e in self.entity_context):
            raise ValueError(
                f"Every entity in self.entity_context must be present in "
                + f"entity_slots, but {e} is missing."
            )
        slots = [entity_slots.index(e) for e in self.entity_context]
        return Fact(self.predicate, tuple(slots), self.absent, self.standard_of_proof)

    def new_context(
        self,
        entity_context: Union[Iterable[int], Iterable[Factor]],
        case_factors: Iterable[Factor] = (),
    ) -> "Fact":
        """
        Creates a new Fact object, replacing the old entity_context
        attribute with a new one.
        """

        if len(entity_context) != len(self.entity_context):
            raise ValueError(
                f"The number of entities should be equal to the number of slots "
                + f"in self.entity_context, which is {len(self.entity_context)}."
            )
        return Fact(
            self.predicate,
            entity_context,
            self.absent,
            self.standard_of_proof,
            case_factors,
        )

    # TODO: A function to determine if a factor implies another (transitively)
    # given a list of factors that imply one another or a function for determining
    # which implication relations (represented by production rules?)
    # are binding from the point of view of a particular court.


@dataclass()
class Evidence(Factor):

    form: Optional[str] = None
    to_effect: Optional[Fact] = None
    statement: Optional[Fact] = None
    stated_by: Optional[int] = None
    derived_from: Optional[int] = None
    absent: bool = False

    def __post_init__(self):
        int_attrs = []
        if self.stated_by is not None:
            int_attrs.append(self.stated_by)
        if self.derived_from is not None:
            int_attrs.append(self.derived_from)
        object.__setattr__(self, "int_attrs", tuple(int_attrs))

        # The Entities in entity_context now include the Entities used in
        # the Fact referenced in self.to_effect

        if self.statement:
            int_attrs = list(self.statement.entity_context) + int_attrs
        if self.to_effect:
            int_attrs += list(self.to_effect.entity_context)
        object.__setattr__(self, "entity_context", tuple(int_attrs))
        object.__setattr__(self, "entity_orders", self.get_entity_orders())

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
