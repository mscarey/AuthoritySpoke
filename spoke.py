import datetime
import itertools
import json
import operator
import pathlib
import re

from typing import Callable, Dict, FrozenSet, List, Set, Tuple
from typing import Iterable, Iterator
from typing import Optional, Sequence, Union
from dataclasses import dataclass

from pint import UnitRegistry
from bs4 import BeautifulSoup
from enactments import Code, Enactment

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

    def __init__(self, name: Optional[str] = None, generic: bool = True):
        self.name = name or f"a {self.__class__.__name__.lower()}"
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
        for entry in other.__dict__:
            if other.__dict__[entry] is not None:
                if type(other.__dict__.get(entry)) in (str, bool):
                    if self.__dict__.get(entry) != other.__dict__.get(entry):
                        return False
                else:
                    if not self.__dict__.get(entry) >= other.__dict__.get(entry):
                        return False
        return True

    def __hash__(self):
        return hash(
            (
                self.__class__.__name__,
                *[v for v in self.__dict__.values() if not isinstance(v, set)],
            )
        )


class Entity(Factor):
    """A person, place, thing, or event that needs to be mentioned in
    multiple predicates/factors in a holding."""

    def __init__(
        self, name: Optional[str] = None, generic: bool = True, plural: bool = False
    ):
        Factor.__init__(self, name, generic)
        self.plural = plural

    def __str__(self):
        return self.name


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
    ) -> Tuple["Predicate", Tuple[Entity, ...]]:

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

        entities = (Entity(e) for e in entities)

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
        self, entities: Union[Entity, Sequence[Union[int, Entity]]]
    ) -> str:
        """Creates a sentence by substituting the names of entities
        from a particular case into the predicate_with_truth."""

        if isinstance(entities, Entity):
            entities = (entities,)
        if all(isinstance(item, int) for item in entities):
            entities = [f"<{item}>" for item in entities]
        if len(entities) != len(self):
            raise ValueError(
                f"Exactly {len(self)} entities needed to complete "
                + f'"{self.content}", but {len(entities)} were given.'
            )
        return str(self).format(*(str(e) for e in entities))

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


@dataclass()
class Fact(Factor):
    """An assertion accepted as factual by a court, often through factfinding by
    a judge or jury."""

    predicate: Optional[Predicate] = None
    entity_context: Union[int, Tuple[int, ...]] = ()
    absent: bool = False
    standard_of_proof: Optional[str] = None
    generic: bool = False

    def __post_init__(self):
        if not self.entity_context:
            object.__setattr__(
                self, "entity_context", tuple(range(len(self.predicate)))
            )
        if isinstance(self.entity_context, int):
            object.__setattr__(self, "entity_context", (self.entity_context,))
        object.__setattr__(self, "entity_orders", self.get_entity_orders())

        if len(self) != len(self.predicate):
            raise ValueError(
                "".join(
                    [
                        "entity_context must have one item for each entity slot ",
                        "in self.predicate, but the number of slots ",
                        f"for {str(self.predicate)} == {len(self.entity_context)} ",
                        f"and len(self.predicate) == {len(self.predicate)}",
                    ]
                )
            )
        if self.standard_of_proof and self.standard_of_proof not in STANDARDS_OF_PROOF:
            raise ValueError(
                f"standard of proof must be one of {STANDARDS_OF_PROOF.keys()} or None."
            )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Factor):
            return False
        return (
            self.predicate == other.predicate
            and self.absent == other.absent
            and self.standard_of_proof == other.standard_of_proof
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

    def __str__(self):
        predicate = str(self.predicate.content_with_entities(self.entity_context))
        standard = f" ({self.standard_of_proof})" if self.standard_of_proof else ""
        return "".join(
            [
                f"{'Absent ' if self.absent else ''}{self.__class__.__name__}",
                f"{standard}: {predicate}",
            ]
        )

    def make_generic(self):
        # TODO: change this to return a new form of the Fact, with any referenced
        # Factors marked as generic replaced by blank versions of themselves
        # (but still with the generic flag)
        predicate = str(self.predicate)
        standard = f" ({self.standard_of_proof})" if self.standard_of_proof else ""
        return "".join(
            [
                f"{'Absent ' if self.absent else ''}{self.__class__.__name__}",
                f"{standard}: {predicate}",
            ]
        )

    def predicate_in_context(self, entities: Sequence[Entity]) -> str:
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

        if other is None:
            return True

        if not isinstance(other, Factor):
            raise TypeError(
                f"'Implies' not supported between instances of "
                + f"'{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )

        if not isinstance(other, self.__class__):
            return False

        if bool(self.standard_of_proof) != bool(other.standard_of_proof):
            return False
        if (
            self.standard_of_proof
            and STANDARDS_OF_PROOF[self.standard_of_proof]
            < STANDARDS_OF_PROOF[other.standard_of_proof]
        ):
            return False

        if self == other:
            return False
        if self.predicate >= other.predicate and self.absent == other.absent:
            return True
        return False

    def __ge__(self, other: Optional["Fact"]) -> bool:
        if self == other:
            return True
        return self > other

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

        return set(
            tuple([x for i, x in sorted(zip(order, self.entity_context))])
            for order in self.predicate.entity_orders
        )

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

    def make_abstract(self, entity_slots: Iterable[Entity]) -> "Fact":
        """
        Creates a new Fact object, this time with numbered
        entity slots instead of actual entities. The indices of
        the Entities in entity_slots correspond to the numbers
        that will be assigned to the slots in the new object's
        self.entity_context.
        """

        if any(not isinstance(s, Entity) for s in entity_slots):
            raise TypeError(
                "entity_slots must be an interable containing only Entity objects."
            )
        if any(e not in entity_slots for e in self.entity_context):
            raise ValueError(
                f"Every entity in self.entity_context must be present in "
                + f"entity_slots, but {e} is missing."
            )
        slots = [entity_slots.index(e) for e in self.entity_context]
        return Fact(self.predicate, tuple(slots), self.absent, self.standard_of_proof)

    def make_concrete(self, entities: Iterable[Entity]) -> "Fact":
        """
        Creates a new Fact object, replacing the numbered
        entity slots with entities in the order they're mentioned
        in the Prodicate. The integer indices in self.entity_context
        will not be used in creating the new object.
        """
        if any(not isinstance(s, Entity) for s in entities):
            raise TypeError(
                "entities must be an interable containing only Entity objects."
            )
        if len(entities) != len(self.entity_context):
            raise ValueError(
                f"The number of entities should be equal to the number of slots "
                + f"in self.entity_context, which is {len(self.entity_context)}."
            )
        return Fact(
            self.predicate, tuple(entities), self.absent, self.standard_of_proof
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

        Entity slots should be collected from each parameter
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


@dataclass()
class Procedure:
    """A (potential) rule for courts to use in resolving litigation. Described in
    terms of inputs and outputs, and also potentially "even if" factors, which could
    be considered "failed undercutters" in defeasible logic.

    Input factors are not treated as potential undercutters.
    Instead, they're assumed to be additional support in favor of the output.
    If a factor is relevant both as support for the output and as a potential
    undercutter, include it in both 'inputs' and 'despite'."""

    outputs: Union[Factor, Iterable[Factor]]
    inputs: Union[Factor, Iterable[Factor]] = frozenset([])
    despite: Union[Factor, Iterable[Factor]] = frozenset([])

    def __post_init__(self):

        if isinstance(self.outputs, Factor):
            object.__setattr__(self, "outputs", frozenset((self.outputs,)))
        if isinstance(self.inputs, Factor):
            object.__setattr__(self, "inputs", frozenset((self.inputs,)))
        if isinstance(self.despite, Factor):
            object.__setattr__(self, "despite", frozenset((self.despite,)))
        object.__setattr__(self, "outputs", frozenset(self.outputs))
        object.__setattr__(self, "inputs", frozenset(self.inputs))
        object.__setattr__(self, "despite", frozenset(self.despite))

        for x in self.outputs | self.inputs | self.despite:
            if not isinstance(x, Factor):
                raise TypeError(
                    (
                        f"Input, Output, and Despite groups must contain only ",
                        f"type Factor, but {x} was type {type(x)}",
                    )
                )

    def __eq__(self, other: "Procedure") -> bool:
        """Determines if the two procedures have all the same factors
        with the same entities in the same roles, not whether they're
        actually the same Python object."""

        if not isinstance(other, Procedure):
            return False

        if len(other) != len(self):  # redundant?
            return False

            # Verifying that every factor in self is in other.
            # Also verifying that every factor in other is in self.

        return self.check_factor_equality(other) and other.check_factor_equality(self)


    def check_factor_equality(self, other: "Procedure") -> bool:
        """
        Determines whether every factor in other is in self, with matching entity slots.
        """
        matchlist = frozenset([tuple([None for i in range(len(self))])])
        matchlist = evolve_match_list(
            self.outputs, other.outputs, operator.eq, matchlist
        )
        matchlist = evolve_match_list(self.inputs, other.inputs, operator.eq, matchlist)
        return bool(
            evolve_match_list(self.despite, other.despite, operator.eq, matchlist)
        )

    def __ge__(self, other: "Procedure") -> bool:
        """
        Tests whether the assertion that self applies in some cases
        implies that the procedure "other" applies in some cases.

        When self and other are holdings that both apply in SOME cases:

        Self does not imply other if any input of other
        is not equal to or implied by some input of self.

        Self does not imply other if any output of other
        is not equal to or implied by some output of self.

        Self does not imply other if any despite of other
        is not equal to or implied by some despite or input of self.
        """

        if not isinstance(other, self.__class__):
            raise TypeError(
                f"'Implies' not supported between instances of "
                + f"'{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )

        despite_or_input = {*self.despite, *self.inputs}

        matchlist = frozenset([tuple([None for i in range(len(self))])])
        matchlist = evolve_match_list(self.inputs, other.inputs, operator.ge, matchlist)
        matchlist = evolve_match_list(
            self.outputs, other.outputs, operator.ge, matchlist
        )
        matchlist = evolve_match_list(
            despite_or_input, other.despite, operator.ge, matchlist
        )

        return bool(matchlist)

    def __gt__(self, other: "Procedure") -> bool:
        if self == other:
            return False
        return self >= other

    def __hash__(self):
        return hash(
            (
                self.__class__.__name__,
                *[v for v in self.__dict__.values() if not isinstance(v, set)],
            )
        )

    def __len__(self):
        """
        Returns the number of entities that need to be specified for the procedure.
        Works by flattening a series of "markers" fields from the Context objects.
        """

        return len(
            set(
                marker
                for markertuple in (
                    factor.entity_context
                    for factor in self.factors_all()
                    if hasattr(factor, "entity_context")
                )
                for marker in markertuple
            )
        )

    def __str__(self):
        text = "Procedure:"
        if self.inputs:
            text += "\nSupporting inputs:"
            for f in self.inputs:
                text += "\n" + str(f)
        if self.despite:
            text += "\nEven if:"
            for f in self.despite:
                text += "\n" + str(f)
        if self.outputs:
            text += "\nOutputs:"
            for f in self.outputs:
                text += "\n" + str(f)
        return text

    def contradiction_between_outputs(
        self, other: "Procedure", m: Tuple[int, ...]
    ) -> bool:
        """
        Returns a boolean indicating if any factor assignment can be found that
        makes a factor in the output of other contradict a factor in the
        output of self.
        """
        return any(
            other_factor.contradicts(self_factor)
            and (
                check_entity_consistency(other_factor, self_factor, m)
                for self_factor in self.outputs
            )
            for other_factor in other.outputs
            for self_factor in self.outputs
        )

    def factors_all(self) -> Set[Factor]:
        """Returns a set of all factors."""

        inputs = self.inputs or set()
        despite = self.despite or set()
        return {*self.outputs, *inputs, *despite}

    def factors_sorted(self) -> List[Factor]:
        """Sorts the procedure's factors into an order that will always be
        the same for the same set of factors, but that doesn't correspond to
        whether the factors are inputs, outputs, or "even if" factors."""

        return sorted(self.factors_all(), key=repr)

    def find_consistent_factors(
        self,
        for_matching: FrozenSet[Factor],
        need_matches: FrozenSet[Factor],
        matches: Tuple[Optional[int], ...],
    ) -> Iterator[Tuple[Optional[int], ...]]:
        """
        Recursively searches for a list of entity assignments that can
        cause all of 'other_factors' to not contradict any of the factors in
        self_matches. Calls a new instance of consistent_entity_combinations
        for each such list that is found. It finally returns
        matchlist when all possibilities have been searched.
        """

        if not need_matches:
            yield matches
        else:
            need_matches = set(need_matches)
            n = need_matches.pop()
            valid_combinations = n.consistent_entity_combinations(for_matching, matches)
            for c in valid_combinations:
                matches_next = list(matches)
                for i in c:
                    matches_next[i] = c[i]
                matches_next = tuple(matches_next)
                for m in self.find_consistent_factors(
                    for_matching, frozenset(need_matches), matches_next
                ):
                    yield m

    def contradicts_some_to_all(self, other: "Procedure") -> bool:
        """
        Tests whether the assertion that self applies in SOME cases
        contradicts that the procedure "other" applies in ALL cases,
        where at least one of the holdings is mandatory.

        :param other:
        """

        if not isinstance(other, self.__class__):
            return False

        self_despite_or_input = {*self.despite, *self.inputs}

        # For self to contradict other, every input of other
        # must be implied by some input or despite factor of self.
        matchlist = frozenset([tuple([None for i in range(len(self))])])
        matchlist = evolve_match_list(
            self_despite_or_input, other.inputs, operator.ge, matchlist
        )

        # For self to contradict other, some output of other
        # must be contradicted by some output of self.

        return any(self.contradiction_between_outputs(other, m) for m in matchlist)

    def implies_all_to_all(self, other: "Procedure") -> bool:
        """
        Tests whether the assertion that self applies in ALL cases
        implies that the procedure "other" applies in ALL cases.

        For self to imply other, every input of self
        must be implied by some input of other.

        Self does not imply other if any output of other
        is not equal to or implied by some output of self.

        Self does not imply other if any despite of other
        contradicts an input of self.

        :param other:
        """

        if not isinstance(other, self.__class__):
            return False

        if self == other:
            return True
        matchlist = frozenset([tuple([None for i in range(len(self))])])
        matchlist_from_other = evolve_match_list(
            other.inputs, self.inputs, operator.ge, matchlist
        )
        matchlist = self.get_foreign_match_list(matchlist_from_other)
        matchlist = evolve_match_list(
            self.outputs, other.outputs, operator.ge, matchlist
        )

        # For every factor in other, find the permutations of entity slots
        # that are consistent with matchlist and that don't cause the factor
        # to contradict any factor of self.

        return any(
            any(
                match
                for match in self.find_consistent_factors(self.inputs, other.despite, m)
            )
            for m in matchlist
        )

    def get_foreign_match_list(
        self, foreign: FrozenSet[Tuple[int, ...]]
    ) -> FrozenSet[Tuple[int, ...]]:
        """Gets a version of matchlist in which the indices represent
        other's entity slots and the values represent self's entity slots.

        Compare this to the regular matchlist objects, in which the
        indices represent self's entity slots and the values represent
        other's."""

        def get_foreign_match(
            length, foreign_match: Tuple[int, ...]
        ) -> Tuple[int, ...]:
            blank = [None] * len(self)
            for e in enumerate(foreign_match):
                if e[1] is not None:
                    blank[e[1]] = e[0]
            return tuple(blank)

        length = len(self)
        return frozenset([get_foreign_match(length, match) for match in foreign])

    def implies_all_to_some(self, other: "Procedure") -> bool:
        """
        This is a different process for checking whether one procedure implies another,
        used when the list of self's inputs is considered an exhaustive list of the
        circumstances needed to invoke the procedure (i.e. when the rule "always" applies
        when the inputs are present), but the list of other's inputs is not exhaustive.

        For self to imply other, every input of self must not be
        contradicted by any input of other.

        For self to imply other, every output of other
        must be equal to or implied by some output of self.

        Self does not imply other if any despite factors of other
        are contradicted by inputs of self.

        :param other:
        """

        if not isinstance(other, self.__class__):
            return False

        matchlist = frozenset([tuple([None for i in range(len(self))])])
        matchlist = evolve_match_list(
            self.outputs, other.outputs, operator.ge, matchlist
        )

        # Not checking whether despite factors of other are
        # contradicted by inputs of self, assuming they can't be
        # because they would be contradicted by inputs of other.

        # For every factor in other, find the permutations of entity slots
        # that are consistent with matchlist and that don't cause the factor
        # to contradict any factor of self.

        other_despite_or_input = {*other.despite, *other.inputs}

        return any(
            any(
                match
                for match in self.find_consistent_factors(
                    other_despite_or_input, self.inputs, m
                )
            )
            for m in matchlist
        )

    def contradicts(self, other):
        raise NotImplementedError(
            "Procedures do not contradict one another unless one of them ",
            "applies in 'ALL' cases. Consider using the ",
            "'contradicts_some_to_all' method.",
        )


@dataclass()
class Rule:
    """
    A statement in which a court posits a legal rule as authoritative,
    deciding some aspect of the current litigation but also potentially
    binding future courts to follow the rule. When holdings appear in
    judicial opinions they are often hypothetical and don't necessarily
    imply that the court accepts the factual assertions or other factors
    that make up the inputs or outputs of the procedure mentioned in the
    holding.
    """


@dataclass()
class ProceduralRule(Rule):

    """
    procedure (Procedure): optional because a holding can contain
    an attribution instead of a holding

    enactments (Union[Enactment, Iterable[Enactment]]): the set of
    enactments cited as authority for the holding

    enactments_despite (Union[Enactment, Iterable[Enactment]]):
    the set of enactments specifically cited as failing to undercut
    the holding

    mandatory (bool): whether the procedure is mandatory for the
    court to apply whenever the holding is properly invoked. False
    may be used for procedures deemed "discretionary".
    Not applicable to attributions.

    universal (bool): True if the procedure is applicable whenever
    its inputs are present. False means that the procedure is
    applicable in "some" situation where the facts are present.
    Not applicable to attributions.

    rule_valid (bool): True means the holding asserts the procedure
    is a valid legal rule. False means it's not a valid legal
    rule.

    decided (bool): False means that it should be deemed undecided
    whether the rule is valid, and thus can have the effect of
    overruling prior holdings finding the rule to be either
    valid or invalid. Seemingly, decided=False should render the
    "rule_valid" flag irrelevant. Note that if an opinion merely
    says the court is not deciding whether a procedure or attribution
    is valid, there is no holding, and no Rule object should be
    created. Deciding not to decide a rule's validity is not the same
    thing as deciding that a rule is undecided.
    """

    procedure: Procedure
    enactments: Union[Enactment, Iterable[Enactment]] = frozenset([])
    enactments_despite: Union[Enactment, Iterable[Enactment]] = frozenset([])
    mandatory: bool = False
    universal: bool = False
    rule_valid: bool = True
    decided: bool = True

    def __post_init__(self):
        if isinstance(self.enactments, Enactment):
            object.__setattr__(self, "enactments", frozenset((self.enactments,)))
        if isinstance(self.enactments_despite, Enactment):
            object.__setattr__(
                self, "enactments_despite", frozenset((self.enactments_despite,))
            )
        object.__setattr__(self, "enactments", frozenset(self.enactments))
        object.__setattr__(
            self, "enactments_despite", frozenset(self.enactments_despite)
        )

    def __str__(self):
        support = despite = None
        if self.enactments:
            support = "Based on this legislation:\n" + "\n".join(
                [str(e) for e in self.enactments]
            )
        if self.enactments_despite:
            despite = "Despite the following legislation:\n" + "\n".join(
                [str(e) for e in self.enactments_despite]
            )
        text = "".join(
            (
                "Rule:\n",
                f"{support or ''}",
                f"{despite or ''}",
                f"\nIt is {'' if self.decided else 'not decided whether it is '}",
                f"{str(self.rule_valid)} that in {'ALL' if self.universal else 'SOME'} cases ",
                f"where the inputs of the following procedure are present, the court ",
                f"{'MUST' if self.mandatory else 'MAY'} accept the procedure's output(s):\n",
            )
        )
        text += str(self.procedure)
        return text

    def __len__(self):
        """Returns the number of entities needed to provide context
        for the Rule, which currently is just the entities needed
        for the Rule's Procedure."""

        return len(self.procedure)

    def contradicts_if_valid(self, other) -> bool:
        """Determines whether self contradicts other,
        assuming that rule_valid and decided are
        True for both Rules."""

        if not isinstance(other, self.__class__):
            return False

        if not self.mandatory and not other.mandatory:
            return False

        if not self.universal and not other.universal:
            return False

        if other.universal and not self.universal:
            return self.procedure.contradicts_some_to_all(other.procedure)

        if self.universal and not other.universal:
            return other.procedure.contradicts_some_to_all(self.procedure)

        # This last option is for the ALL contradicts ALL case (regardless of MAY or MUST)
        # It could use more tests.

        return other.procedure.contradicts_some_to_all(
            self.procedure
        ) or self.procedure.contradicts_some_to_all(other.procedure)

    def implies_if_decided(self, other) -> bool:

        """Simplified version of the __ge__ implication function
        covering only cases where decided is True for both Rules,
        although rule_valid can be False."""

        if self.rule_valid and other.rule_valid:
            return self.implies_if_valid(other)

        if not self.rule_valid and not other.rule_valid:
            return other.implies_if_valid(self)

        # Looking for implication where self.rule_valid != other.rule_valid
        # is equivalent to looking for contradiction.

        # If decided rule A contradicts B, then B also contradicts A

        if other.rule_valid and not self.rule_valid:
            return self.contradicts_if_valid(other) or other.implies_if_valid(self)

        # if self.rule_valid and not other.rule_valid
        return other.contradicts_if_valid(self) or self.implies_if_valid(other)

    def implies_if_valid(self, other) -> bool:
        """Simplified version of the __ge__ implication function
        covering only cases where rule_valid and decided are
        True for both Rules."""

        if not isinstance(other, self.__class__):
            return False

        # If self relies for support on some enactment text that
        # other doesn't, then self doesn't imply other.

        if not all(
            any(other_e >= e for other_e in other.enactments) for e in self.enactments
        ):
            return False

        # If other specifies that it applies notwithstanding some
        # enactment not mentioned by self, then self doesn't imply other.

        if not all(
            any(e >= other_d for e in (self.enactments | self.enactments_despite))
            for other_d in other.enactments_despite
        ):
            return False

        if other.mandatory > self.mandatory:
            return False

        if other.universal > self.universal:
            return False

        if self.universal > other.universal:
            return self.procedure.implies_all_to_some(other.procedure)

        if other.universal:
            return self.procedure.implies_all_to_all(other.procedure)

        return self.procedure >= other.procedure

    def __gt__(self, other) -> bool:
        if self == other:
            return False
        return self >= other

    def __ge__(self, other) -> bool:
        """Returns a boolean indicating whether self implies other,
        where other is another Rule."""

        if not isinstance(other, self.__class__):
            raise TypeError(
                f"'Implies' not supported between instances of "
                + f"'{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )

        if self.decided and other.decided:
            return self.implies_if_decided(other)

        # A holding being undecided doesn't seem to imply that
        # any other holding is undecided, except itself and the
        # negation of itself.

        if not self.decided and not other.decided:
            return self == other or self == other.negated()

        # It doesn't seem that any holding being undecided implies
        # that any holding is decided, or vice versa.

        return False

    def __hash__(self):
        return hash(
            (
                self.__class__.__name__,
                *[v for v in self.__dict__.values() if not isinstance(v, set)],
            )
        )

    def negated(self):
        return ProceduralRule(
            procedure=self.procedure,
            enactments=self.enactments,
            enactments_despite=self.enactments_despite,
            mandatory=self.mandatory,
            universal=self.universal,
            rule_valid=not self.rule_valid,
            decided=self.decided,
        )

    def contradicts(self, other) -> bool:
        """
        A holding contradicts another holding if it implies
        that the other holding is false. Generally checked
        by testing whether self would imply other if
        other had an opposite value for rule_valid.
        """

        if not isinstance(other, self.__class__):
            raise TypeError(
                f"'Contradicts' not supported between instances of "
                + f"'{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )

        if self.decided and other.decided:
            return self >= other.negated()

        if not self.decided and not other.decided:
            return self == other or self == other.negated()

        # A decided holding doesn't "contradict" a previous
        # statement that any rule was undecided.

        if self.decided and not other.decided:
            return False

        # If holding A implies holding B, then the statement
        # that A is undecided contradicts the prior holding B.

        # if not self.decided and other.decided:
        return other.implies_if_decided(self)


def opinion_from_file(path):
    """This is a generator that gets one opinion from a
    Harvard-format case file every time it's called. Exhaust the
    generator to get the lead opinion and all non-lead opinions."""

    with open(path, "r") as f:
        opinion_dict = json.load(f)

    citations = tuple(c["cite"] for c in opinion_dict["citations"])

    for opinion in opinion_dict["casebody"]["data"]["opinions"]:
        author = None
        position = opinion["type"]
        author = opinion["author"].strip(",:")

        yield Opinion(
            opinion_dict["name"],
            opinion_dict["name_abbreviation"],
            citations,
            int(opinion_dict["first_page"]),
            int(opinion_dict["last_page"]),
            datetime.date.fromisoformat(opinion_dict["decision_date"]),
            opinion_dict["court"]["slug"],
            position,
            author,
        )


@dataclass
class Opinion:
    """A document that resolves legal issues in a case and posits legal holdings.
    Usually only a majority opinion will create holdings binding on any courts.
    """

    name: str
    name_abbreviation: str
    citations: Tuple[str]
    first_page: int
    last_page: int
    decision_date: datetime.date
    court: str
    position: str
    author: str

    def __post_init__(self):
        self.holdings = {}

    def get_entities(self):
        return [e for t in self.holdings.values() for e in t]

    def posits(
        self, holding: Rule, entities: Optional[Tuple[Entity, ...]] = None
    ) -> None:
        if entities is None:
            entities = self.get_entities()[: len(holding)]  # TODO: write test

        if len(holding) > len(entities):
            raise ValueError(
                f"The 'entities' parameter must be a tuple with "
                + f"{len(holding)} entities. This opinion doesn't have "
                + "enough known entities to create context for this holding."
            )

        if holding not in self.holdings:
            self.holdings[holding] = entities

        return None

    def holding_in_context(self, holding: Rule):
        if not isinstance(holding, Rule):
            raise TypeError("holding must be type 'Rule'.")
        if holding not in self.holdings:
            raise ValueError
            (
                f"That holding has not been posited by {self.name}. "
                + "Try using the posits() method to add the holding to self.holdings."
            )
        pass  # TODO: tests

    def dict_from_input_json(self, filename: str) -> Tuple[Dict, Dict]:
        """
        Makes entity and holding dicts from a JSON file in the format that lists
        mentioned_entities followed by a list of holdings.
        """

        path = pathlib.Path("input") / filename
        with open(path, "r") as f:
            case = json.load(f)
        return case["mentioned_factors"], case["holdings"]

    def holdings_from_json(self, filename: str) -> Dict["Rule", Tuple[Entity, ...]]:
        """Creates a set of holdings from a JSON file in the input subdirectory,
        adds those holdings to self.holdings, and returns self.holdings."""

        entity_list, holding_list = self.dict_from_input_json(filename)
        for record in holding_list:
            factor_groups = {"inputs": set(), "outputs": set(), "despite": set()}
            for factor_type in factor_groups:
                factor_list = record.get(factor_type, [])
                if not isinstance(factor_list, list):
                    factor_list = [factor_list]
                for factor_dict in factor_list:
                    factor = Factor.from_dict(factor_dict)
                    factor_groups[factor_type].add(factor)
            procedure = Procedure(
                inputs=factor_groups["inputs"],
                outputs=factor_groups["outputs"],
                despite=factor_groups["despite"],
            )

            enactment_groups = {"enactments": set(), "enactments_despite": set()}
            for enactment_type in enactment_groups:
                enactment_list = record.get(enactment_type, [])
                if isinstance(enactment_list, dict):
                    enactment_list = [enactment_list]
                for enactment_dict in enactment_list:
                    enactment_groups[enactment_type].add(
                        Enactment.from_dict(enactment_dict)
                    )

            holding = ProceduralRule(
                procedure=procedure,
                enactments=enactment_groups["enactments"],
                enactments_despite=enactment_groups["enactments_despite"],
                mandatory=record.get("mandatory", False),
                universal=record.get("universal", False),
                rule_valid=record.get("rule_valid", True),
                decided=record.get("decided", True),
            )
            # There's currently no way to get the entities from the Predicates.
            self.holdings[holding] = entities
        return self.holdings


class Attribution:
    """An assertion about the meaning of a prior Opinion. Either a user or an Opinion
    may make an Attribution to an Opinion. An Attribution may attribute either
    a Rule or a further Attribution."""

    pass
