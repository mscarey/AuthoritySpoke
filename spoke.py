import datetime
import itertools
import json
import operator
import re

from typing import Callable, Dict, FrozenSet, Iterable, List
from typing import Optional, Sequence, Set, Tuple, Union
from dataclasses import dataclass
from collections import namedtuple

from pint import UnitRegistry
from bs4 import BeautifulSoup
import roman

ureg = UnitRegistry()
Q_ = ureg.Quantity

OPPOSITE_COMPARISONS = {
    ">": "<=",
    ">=": "<",
    "=": "!=",
    "<>": "=",
    "<": ">=",
    "<=": ">",
}


@dataclass()
class Entity:
    """A person, place, thing, or event that needs to be mentioned in
    multiple predicates/factors in a holding."""

    name: str
    plural: bool = False

    def __str__(self):
        return self.name


@dataclass()
class Human(Entity):
    """
    A "natural person" mentioned as an entity in a factor. On the distinction
    between "human" and "person", see Slaughter-House Cases, 83 U.S. 36, 99.
    https://www.courtlistener.com/opinion/88661/slaughter-house-cases/
    """

    pass


@dataclass()
class Event(Entity):
    """
    Events may be referenced as entities in a predicate's content.
    See Lepore, Ernest. Meaning and Argument: An Introduction to Logic
    Through Language. Section 17.2: The Event Approach
    """


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
    truth: bool = True
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
        if self.comparison and not self.truth:
            object.__setattr__(self, "truth", True)
            object.__setattr__(
                self, "comparison", OPPOSITE_COMPARISONS[self.comparison]
            )

        if self.comparison and self.comparison not in OPPOSITE_COMPARISONS.keys():
            raise ValueError(
                f'"comparison" string parameter must be one of {OPPOSITE_COMPARISONS.keys()}.'
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
                and self.truth != other.truth
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

    def content_with_entities(self, entities: Union[Entity, Sequence[Entity]]) -> str:
        """Creates a sentence by substituting the names of entities
        from a particular case into the predicate_with_truth."""

        if isinstance(entities, Entity):
            entities = (entities,)
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

    def entity_orders(self):
        """
        Returns a set of tuples indicating the ways the entities
        could be rearranged without changing the meaning of the predicate.

        Currently the only possible rearrangement is to swap the
        order of the first two entities if self.reciprocal.
        """
        orders = {(tuple(n for n in range(len(self))))}
        return orders

    # TODO: allow the same entity to be mentioned more than once


@dataclass(frozen=True)
class Factor:
    """A factor is something used to determine the applicability of a legal
    procedure. Factors can be both inputs and outputs of legal procedures.
    In a chain of legal procedures, the outputs of one may become inputs for
    another. Common types of factors include Facts, Evidence, Allegations,
    Motions, and Arguments."""


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

    predicate: Predicate
    entity_context: Tuple[int, ...] = ()
    absent: bool = False
    standard_of_proof: Optional[str] = None

    def __post_init__(self):
        if not self.entity_context:
            object.__setattr__(
                self, "entity_context", tuple(range(len(self.predicate)))
            )
        if isinstance(self.entity_context, int):
            object.__setattr__(self, "entity_context", (self.entity_context,))
        if len(self) != len(self.predicate):
            raise ValueError(
                (
                    "entity_context must have one item for each entity slot ",
                    "in self.predicate, but ",
                    f"len(entity_context) for {str(self.predicate)} == {len(self.entity_context)} ",
                    f"and len(self.predicate) == {len(self.predicate)}",
                )
            )
        if self.standard_of_proof and self.standard_of_proof not in STANDARDS_OF_PROOF:
            raise ValueError(
                f"standard of proof must be one of {STANDARDS_OF_PROOF.keys()} or None."
            )

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (
            self.predicate == other.predicate
            and self.absent == other.absent
            and self.standard_of_proof == other.standard_of_proof
        )

    def __str__(self):
        predicate = str(self.predicate).format(*self.entity_context)
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

    def __gt__(self, other) -> bool:
        """Indicates whether self implies other, taking into account the implication
        test for predicates and whether self and other are labeled 'absent'"""

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

    def __ge__(self, other) -> bool:
        if self == other:
            return True
        return self > other

    def contradicts(self, other) -> bool:
        """Returns True if self and other can't both be true at the same time.
        Otherwise returns False."""

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

    def check_entity_consistency(
        self, other: Factor, matches: tuple
    ) -> List[Tuple[int, ...]]:
        """
        Given entity assignments for self and other, determines whether
        the factors have consistent entity assignments such that both can
        be true at the same time.

        All of self's entities must match other's, but other may have entities
        that don't match self.

        if self.predicate.reciprocal, the function will also compare other
        to self with the first two entity slots of self_entities transposed.

        :param other:

        :param matches: a list the same length as len(self). The indices represent
        self's entity slots, and the value at each index represents other's
        corresponding entity slots that have already been assigned, if any.

        :returns: a list containing self's normal entity tuple, self's reciprocal
        entity tuple, both, or neither, depending on which ones match with other.

        """

        def all_matches(needed: Tuple[int]) -> bool:
            """
            Determines whether the entity slots assigned so far are
            consistent for the Factors designated self and other,
            regardless of whether it's possible to make consistent
            assignments for the remaining slots.
            """

            return all(
                matches[other.entity_context[i]] == needed[i]
                or matches[other.entity_context[i]] is None
                for i in range(len(other))
            )

        if not isinstance(other, Factor):
            raise TypeError(f"other must be type Factor")

        answer = []

        if all_matches(self.entity_context):
            answer.append(self.entity_context)

        if self.predicate.reciprocal:
            swapped = list(self.entity_context)
            swapped[0], swapped[1] = swapped[1], swapped[0]
            if all_matches(swapped):
                answer.append(tuple(swapped))

        return answer

    def consistent_entity_combinations(
        self, factors_from_other_procedure, matches
    ) -> List[Dict]:
        """Finds all possible entity marker combinations for self that
        don't result in a contradiction with any of the factors of
        other. The time to call this function
        repeatedly during a recursive search should explode
        as the possibilities increase, so it should only be run
        when matches has been narrowed as much as possible."""

        source_lists = [self.entity_context]
        answer = []
        if self.predicate.reciprocal:
            swapped = list(self.entity_context)
            swapped[0], swapped[1] = swapped[1], swapped[0]
            source_lists.append(tuple(swapped))
        for source_list in source_lists:
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

    # TODO: A function to determine if a factor implies another (transitively)
    # given a list of factors that imply one another or a function for determining
    # which implication relations (represented by production rules?)
    # are binding from the point of view of a particular court.


@dataclass(frozen=True)
class Evidence(Factor):

    form: Optional[str] = None
    physical_object: Optional[Entity] = None
    derived_from: Optional[Entity] = None
    to_effect: Optional[Predicate] = None
    absent: bool = False


@dataclass(frozen=True)
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
                        f"{group} must contain only type Factor,",
                        f"but {x} was type {type(x)}",
                    )
                )

    def __eq__(self, other):
        """Determines if the two procedures have all the same factors
        with the same entities in the same roles, not whether they're
        actually the same Python object."""

        if not isinstance(other, Procedure):
            return False

        if len(other) != len(self):  # redundant?
            return False

        matchlist = [tuple([None for i in range(len(self))])]

        for x in (
            (self.outputs, other.outputs),
            (self.inputs, other.inputs),
            (self.despite, other.despite),
        ):

            # Verifying that every factor in self is in other.

            prior_list = tuple(matchlist)
            matchlist = []
            for m in prior_list:
                # TODO: try rewriting without matchlist as parameter
                matchlist = self.find_matches(x[0], set(x[1]), m, matchlist, operator.eq)

            # Also verifying that every factor in other is in self.

            prior_list = tuple(matchlist)
            matchlist = []
            for m in prior_list:
                matchlist = self.find_matches(x[1], set(x[0]), m, matchlist, operator.eq)

        return bool(matchlist)

    def __ge__(self, other):
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

        if not isinstance(other, Procedure):
            return False

        matchlist = [tuple([None for i in range(len(self))])]
        despite_or_input = {*self.despite, *self.inputs}

        for x in (
            (self.inputs, other.inputs, operator.ge),
            (self.outputs, other.outputs, operator.ge),
            (despite_or_input, other.despite, operator.ge),
        ):

            prior_list = tuple(matchlist)
            matchlist = []
            for m in prior_list:
                matchlist = self.find_matches(x[0], set(x[1]), m, matchlist, x[2])

            if not matchlist:
                return False

        return bool(matchlist)

    def __gt__(self, other):
        if self == other:
            return False
        return self >= other

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

    def contradiction_between_outputs(self, other, m):
        """
        Returns a boolean indicating if any factor assignment can be found that
        makes a factor in the output of other contradict a factor in the
        output of self.
        """
        return any(
            other_factor.contradicts(self_factor)
            and (
                other_factor.check_entity_consistency(self_factor, m)
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

    def find_consistent_factors(self, self_matches, other_factors, m, matchlist):
        """
        Recursively searches for a list of entity assignments that can
        cause all of 'other_factors' to not contradict any of the factors in
        self_matches. Calls a new instance of consistent_entity_combinations
        for each such list that is found. It finally returns
        matchlist when all possibilities have been searched.
        """

        matches = tuple(m)
        need_matches = {f for f in other_factors}
        if not need_matches:
            matchlist.append(matches)
            return matchlist
        n = need_matches.pop()
        valid_combinations = n.consistent_entity_combinations(self_matches, matches)
        for c in valid_combinations:
            matches_next = list(matches)
            for i in c:
                matches_next[i] = c[i]
                matchlist = self.find_consistent_factors(
                    self_matches, need_matches, matches_next, matchlist
                )
        return matchlist

    def find_matches(
        self,
        for_matching: FrozenSet[Factor],
        need_matches: Set[Factor],
        matches: Tuple[Optional[int], ...],
        matchlist: List[Tuple[Optional[int], ...]],
        comparison: Callable[[Factor, Factor], bool],
    ):
        """
        Recursively searches for a tuple of entity assignments that can
        cause all of 'need_matches' to satisfy the relation described by
        'comparison' with a factor from for_matching. When one such tuple
        is found, the function adds that tuple to matchlist and continues
        searching. It finally returns matchlist when all possibilities
        have been searched.

        :param for_matching: A frozenset of all of self's factors. These
        factors aren't removed when they're matched to a factor from other,
        because it's possible that one factor in self could imply two
        different factors in other.

        :param need_matches: A set of factors from other that have
        not yet been matched to any factor from self.

        :param matches: A tuple showing which factors from
        for_matching have been matched.

        :param matchlist: A list of "matches" objects known to be
        consistent with the factors that have been considered so far,
        including need_matches.

        :param comparison: A function used to filter the for_matching
        factors into the "available" collection. A factor must have
        the "comparison" relation with the factor from the need_matches
        set to be included as "available".

        :returns: a new version of matchlist, which may have new tuples
        of entity assignments that weren't present in the version of
        matchlist that was used as an input parameter.
        """

        if not need_matches:
            matchlist.append(matches)
            return matchlist
        n = need_matches.pop()
        available = {a for a in for_matching if comparison(a, n)}
        for a in available:
            matches_found = n.check_entity_consistency(a, matches)
            for source_list in matches_found:
                matches_next = list(matches)
                for i in range(len(a)):
                    matches_next[a.entity_context[i]] = source_list[i]
                matches_next = tuple(matches_next)
                matchlist = self.find_matches(
                    for_matching, need_matches, matches_next, matchlist, comparison
                )
        return matchlist

    def contradicts_some_to_all(self, other):
        """
        Tests whether the assertion that self applies in SOME cases
        contradicts that the procedure "other" applies in ALL cases,
        where at least one of the holdings is mandatory.

        """

        if not isinstance(other, self.__class__):
            return False

        prior_list = (tuple([None] * len(self)),)
        self_despite_or_input = {*self.despite, *self.inputs}
        matchlist = []

        # For self to contradict other, every input of other
        # must be implied by some input or despite factor of self.

        for m in prior_list:
            matchlist = self.find_matches(
                self_despite_or_input, set(other.inputs), m, matchlist, operator.ge
            )
        if not matchlist:
            return False

        prior_list = tuple(matchlist)
        matchlist = []

        # For self to contradict other, some output of other
        # must be contradicted by some output of self.

        return any(self.contradiction_between_outputs(other, m) for m in prior_list)

    def implies_all_to_all(self, other: "Procedure"):
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

        matchlist = [tuple([None for i in range(len(self))])]

        for x in (
            (other.inputs, self.inputs, operator.ge),
            (self.outputs, other.outputs, operator.ge),
        ):

            prior_list = tuple(matchlist)
            matchlist = []
            for m in prior_list:
                matchlist = self.find_matches(x[0], set(x[1]), m, matchlist, x[2])

            if not matchlist:
                return False

        # For every factor in other, find the permutations of entity slots
        # that are consistent with matchlist and that don't cause the factor
        # to contradict any factor of self.

        prior_list = tuple(matchlist)
        matchlist = []
        for m in prior_list:
            matchlist = self.find_consistent_factors(
                self.inputs, other.despite, m, matchlist
            )

        return bool(matchlist)

    def implies_all_to_some(self, other):
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
        """

        if not isinstance(other, self.__class__):
            return False

        matchlist = [tuple([None for i in range(len(self))])]

        for x in ((self.outputs, other.outputs, operator.ge),):

            prior_list = tuple(matchlist)
            matchlist = []
            for m in prior_list:
                matchlist = self.find_matches(x[0], set(x[1]), m, matchlist, x[2])

            if not matchlist:
                return False

        # Not checking whether despite factors of other are
        # contradicted by inputs of self, assuming they can't be
        # because they would be contradicted by inputs of other.

        # For every factor in other, find the permutations of entity slots
        # that are consistent with matchlist and that don't cause the factor
        # to contradict any factor of self.

        other_despite_or_input = {*other.despite, *other.inputs}

        prior_list = tuple(matchlist)
        matchlist = []
        for m in prior_list:
            matchlist = self.find_consistent_factors(
                other_despite_or_input, self.inputs, m, matchlist
            )

        return bool(matchlist)

    def contradicts(self, other):
        raise NotImplementedError(
            "Procedures do not contradict one another unless one of them ",
            "is designated 'exhaustive'. Consider using the ",
            "'exhaustive_contradicts' method.",
        )


class Code:
    """
    A constitution, code of statutes, code of regulations,
    or collection of court rules.
    """

    def __init__(self, path: str):
        self.path = path
        self.xml = self.get_xml()
        self.title = self.xml.find("dc:title").text
        if "Constitution" in self.title:
            self.level = "constitutional"
        if "United States" in self.title:
            self.sovereign = "federal"

    def __str__(self):
        return self.title

    def get_xml(self):
        with open(self.path) as fp:
            xml = BeautifulSoup(fp.read(), "lxml-xml")
        return xml

    def provision_effective_date(self, cite):
        """
        Given the "citation" of a legislative provision
        (only XML element names are used as citations so far),
        retrieves the effective date of the provision from
        the United States Legislative Markup (USLM) XML version
        of the code where the provision is located.

        So far this only covers the US Constitution.
        """

        if self.level == "constitutional" and self.sovereign == "federal":
            if "amendment" not in cite.lower():
                return datetime.date(1788, 9, 13)
            roman_numeral = cite.split("-")[1]
            amendment_number = roman.from_roman(roman_numeral)
            if amendment_number < 11:
                return datetime.date(1791, 12, 15)
            section = self.xml.find(id=cite)
            if section.name == "level":
                enactment_text = section.find("note").p.text
            else:
                enactment_text = section.parent.find("note").p.text
            month_first = re.compile(
                r"""(?:Secretary of State|Administrator of General Services|certificate of the Archivist)(?: accordingly issued a proclamation)?,? dated (\w+ \d\d?, \d{4}),"""
            )
            day_first = re.compile(
                r"(?:Congress|Secretary of State),? dated the (\d\d?th of \w+, \d{4}),"
            )
            result = month_first.search(enactment_text)
            if result:
                return datetime.datetime.strptime(result.group(1), "%B %d, %Y").date()
            result = day_first.search(enactment_text)
            return datetime.datetime.strptime(result.group(1), "%dth of %B, %Y").date()

        return NotImplementedError


class Enactment(Factor):
    def __init__(
        self,
        code: Code,
        section: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ):
        self.code = code
        self.section = section
        self.start = start
        self.end = end

        xml = self.code.get_xml()
        self.text = self.get_cited_passage(xml)

        self.effective_date = self.code.provision_effective_date(section)

    def get_cited_passage(self, xml):
        passages = xml.find(id=self.section).find_all(name="text")
        text = "".join(passage.text for passage in passages)
        if self.start:
            l = text.find(self.start)
        else:
            l = 0
        if self.end:
            r = text.find(self.end) + len(self.end)
        else:
            r = len(text)
        return text[l:r]

    def __hash__(self):
        return hash((self.text, self.code.sovereign, self.code.level))

    def __str__(self):
        return f'"{self.text}" ({self.code.title}, {self.section})'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return (
            self.text.strip(",:;. ") == other.text.strip(",:;. ")
            and self.code.sovereign == other.code.sovereign
            and self.code.level == other.code.level
        )

    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return other.text.strip(",:;. ") in self.text

    def __gt__(self, other):
        if self == other:
            return False
        return self >= other


@dataclass
class Holding:
    """
    A statement in which a court posits a legal rule as authoritative,
    deciding some aspect of the current litigation but also potentially
    binding future courts to follow the rule. When holdings appear in
    judicial opinions they are often hypothetical and don't necessarily
    imply that the court accepts the factual assertions or other factors
    that make up the inputs or outputs of the procedure mentioned in the
    holding.
    """


@dataclass
class ProceduralHolding(Holding):

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
    is valid, there is no holding, and no Holding object should be
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
                "Holding:\n",
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

    def contradicts_if_valid(self, other) -> bool:
        """Determines whether self contradicts other,
        assuming that rule_valid and decided are
        True for both Holdings."""

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
        covering only cases where decided is True for both Holdings,
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
        True for both Holdings."""

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
        where other is another Holding."""

        if not isinstance(other, self.__class__):
            return False

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

    def negated(self):
        return ProceduralHolding(
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
        return self.implies_if_decided(other)


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


class Attribution:
    """An assertion about the meaning of a prior Opinion. Either a user or an Opinion
    may make an Attribution to an Opinion. An Attribution may attribute either
    a Holding or a further Attribution."""

    pass
