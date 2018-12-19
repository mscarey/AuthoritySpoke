import datetime
import itertools
import json
import operator

from typing import Dict, FrozenSet, Iterable, List, Mapping
from typing import Optional, Sequence, Set, Tuple, Union
from dataclasses import dataclass
from collections import namedtuple

from pint import UnitRegistry

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

    def __eq__(self, other) -> bool:
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

    def __gt__(self, other) -> bool:
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

        # TODO: check that there's a reasonable answer for which supporting input should be
        # considered more specific: "x was greater than 20" or "x was exactly 25"
        # (remembering that more information in a supporting input is not deemed to undercut).

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

    def __ge__(self, other):
        if self == other:
            return True
        return self > other

    def contradicts(self, other):
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

    def quantity_comparison(self):
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

    def negated(self):
        return Predicate(
            content=self.content,
            truth=not self.truth,
            reciprocal=self.reciprocal,
            comparison=self.comparison,
            quantity=self.quantity,
        )

    # TODO: allow the same entity to be mentioned more than once


@dataclass(frozen=True)
class Factor:
    """A factor is something used to determine the applicability of a legal
    procedure. Factors can be both inputs and outputs of legal procedures.
    In a chain of legal procedures, the outputs of one may become inputs for
    another. Common types of factors include Facts, Evidence, Allegations,
    Motions, and Arguments."""


@dataclass(frozen=True)
class Fact(Factor):
    """An assertion accepted as factual by a court, often through factfinding by
    a judge or jury."""

    predicate: Predicate
    entity_context: Tuple[int, ...] = ()
    absent: bool = False

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
                    f"len(entity_context) == {len(self.entity_context)} ",
                    f"and len(self.predicate) == {len(self.predicate)}",
                )
            )

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.predicate == other.predicate and self.absent == other.absent

    def __str__(self):
        predicate = str(self.predicate).format(*self.entity_context)
        return (
            f"{'Absent ' if self.absent else ''}{self.__class__.__name__}: {predicate}"
        )

    def __len__(self):
        return len(self.entity_context)

    def __gt__(self, other) -> bool:
        """Indicates whether self implies other, taking into account the implication
        test for predicates and whether self and other are labeled 'absent'"""

        if not isinstance(other, self.__class__):
            return False
        if self == other:
            return False
        if self.predicate >= other.predicate and self.absent == other.absent:
            return True
        return False

    def __ge__(self, other):
        if self == other:
            return True
        return self > other

    def predicate_in_context(self, entities: Sequence[Entity]) -> str:
        return (
            f"{'Absent ' if self.absent else ''}{self.__class__.__name__}: "
            + f"{self.predicate.content_with_entities(entities)}"
        )

    def contradicts(self, other) -> bool:
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
        self, other, matches
    ) -> List[Tuple[int, ...]]:
        """
        Given entity assignments for self and other, determines whether
        the factors have consistent entity assignments such that both can
        be true at the same time.

        All of self's entities must match other's, but other may have entities
        that don't match self.

        if self.predicate.reciprocal, the function will also compare other
        to self with the first two entity slots of self_entities transposed.

        Parameters:

        other (Fact)

        matches (tuple): a list the same length as len(self). The indices represent
        self's entity slots, and the value at each index represents other's
        corresponding entity slots that have already been assigned, if any.

        Returns a list containing self's normal entity tuple, self's reciprocal
        entity tuple, both, or neither, depending on which ones match with other.

        """

        def all_matches(need_list) -> bool:
            return all(
                matches[other.entity_context[i]] == need_list[i]
                or matches[other.entity_context[i]] is None
                for i in range(len(other))
            )

        if not isinstance(other, self.__class__):
            raise TypeError(f"other must be type {self.__class__}")

        answer = []

        if all_matches(self.entity_context):
            answer.append(self.entity_context)

        if self.predicate.reciprocal:
            swapped = list(self.entity_context)
            swapped[0], swapped[1] = swapped[1], swapped[0]
            if all_matches(swapped):
                answer.append(tuple(swapped))

        return answer

    def consistent_entity_combinations(self, factors_from_other_procedure, matches) -> List[Dict]:
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
                i: (
                    slot
                    for slot in matches
                    if (not matches[slot] or matches[slot] == source_list[i])
                )
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
        for group in (self.outputs, self.inputs, self.despite):
            for x in group:
                if not isinstance(x, Factor):
                    raise TypeError(
                        (
                            f"{group} must contain only type Factor,",
                            f"but {x} was type {type(x)}",
                        )
                    )

        object.__setattr__(self, "outputs", frozenset(self.outputs))
        object.__setattr__(self, "inputs", frozenset(self.inputs))
        object.__setattr__(self, "despite", frozenset(self.despite))

    def __len__(self):
        """
        Returns the number of entities that need to be specified for the procedure.
        Works by flattening a series of "markers" fields from the Context objects.
        """

        return len(
            set(
                marker
                for markertuple in (
                    factor.entity_context for factor in self.all_factors()
                )
                for marker in markertuple
            )
        )

    def __str__(self):
        text = "Procedure:"
        if self.inputs:
            text += "\nInputs:"
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

    def all_factors(self) -> Set[Factor]:
        """Returns a set of all factors."""

        inputs = self.inputs or set()
        despite = self.despite or set()
        return {*self.outputs, *inputs, *despite}

    def sorted_factors(self) -> List[Factor]:
        """Sorts the procedure's factors into an order that will always be
        the same for the same set of factors, but that doesn't correspond to
        whether the factors are inputs, outputs, or "even if" factors."""

        return sorted(self.all_factors(), key=repr)


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

    def find_matches(self, self_matches, other_factors, m, matchlist, comparison):
        """
        Recursively searches for a list of entity assignments that can
        cause all of 'other_factors' to satisfy the relation described by
        'comparison' with a factor from self_matches. When one such list
        is found, the function adds that list to matchlist and continues
        searching. It finally returns matchlist when all possibilities
        have been searched.
        """
        matches = tuple(m)
        need_matches = {f for f in other_factors}
        if not need_matches:
            matchlist.append(matches)
            return matchlist
        n = need_matches.pop()
        available = {a for a in self_matches if comparison(a, n)}
        for a in available:
            matches_found = n.check_entity_consistency(a, matches)
            for source_list in matches_found:
                matches_next = list(matches)
                for i in range(len(a)):
                    matches_next[a.entity_context[i]] = source_list[i]
                matchlist = self.find_matches(
                    self_matches, need_matches, matches_next, matchlist, comparison
                )
        return matchlist

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
                matchlist = self.find_matches(x[0], x[1], m, matchlist, operator.eq)

            # Also verifying that every factor in other is in self.

            prior_list = tuple(matchlist)
            matchlist = []
            for m in prior_list:
                matchlist = self.find_matches(x[1], x[0], m, matchlist, operator.eq)

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
                matchlist = self.find_matches(x[0], x[1], m, matchlist, x[2])

            if not matchlist:
                return False

        return bool(matchlist)

    def __gt__(self, other):
        if self == other:
            return False
        return self >= other

    def implies_all_to_all(self, other):
        """
        Tests whether the assertion that self applies in ALL cases
        implies that the procedure "other" applies in ALL cases.

        For self to imply other, every input of self
        must be implied by some input of other.

        Self does not imply other if any output of other
        is not equal to or implied by some output of self.

        Self does not imply other if any despite of other
        contradicts an input of self.
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
                matchlist = self.find_matches(x[0], x[1], m, matchlist, x[2])

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

    def exhaustive_implies(self, other):
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

        # This is more consistent with __ge__ than __gt__.
        # I can't think of a use case for the __gt__ behavior of
        # returning False when the Procedures are equal.

        if self == other:
            return True

        matchlist = [tuple([None for i in range(len(self))])]

        for x in ((self.outputs, other.outputs, operator.ge),):

            prior_list = tuple(matchlist)
            matchlist = []
            for m in prior_list:
                matchlist = self.find_matches(x[0], x[1], m, matchlist, x[2])

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

    def exhaustive_contradicts(self, other):
        """
        Self contradicts other if:
        Other has all the inputs of self, but an output of self
        contradicts an output of other.
        """
        pass


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
    mandatory: bool = False
    universal: bool = False
    rule_valid: bool = True
    decided: bool = True

    def __str__(self):
        text = "".join(
            (
                f"Holding: It is {'' if self.decided else 'not decided whether it is '}",
                f"{str(self.rule_valid)} that in {'ALL' if self.universal else 'SOME'} cases ",
                f"where the inputs of the following procedure are present, the court ",
                f"{'MUST' if self.mandatory else 'MAY'} accept the procedure's output(s):\n",
            )
        )
        text += str(self.procedure)
        return text

    def implies_if_valid(self, other) -> bool:
        """Simplified version of the __ge__ implication function
        covering only cases where rule_valid and decided are
        True for both Holdings."""

        if other.mandatory > self.mandatory:
            return False

        if other.universal > self.universal:
            return False

        if self.universal > other.universal:
            return self.procedure.exhaustive_implies(other.procedure)

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

            if self.rule_valid and other.rule_valid:
                return self.implies_if_valid(other)

            if not self.rule_valid and not other.rule_valid:
                return other.implies_if_valid(self)


        # In NO cases where A, the output MUST/MAY be X
        # does imply:
        # In NOT ALL/NO cases where A, the output MUST be X
        if (
            self.decided
            and other.decided
            and not self.rule_valid
            and not other.rule_valid
            and other.universal >= self.universal
            and other.mandatory >= self.mandatory
        ):
            return self.procedure.exhaustive_implies(other.procedure)

        raise NotImplementedError("Haven't reached that case yet.")

    def negated(self):
        return ProceduralHolding(
            procedure=self.procedure,
            mandatory=self.mandatory,
            universal=self.universal,
            rule_valid=not self.rule_valid,
            decided=self.decided,
        )

    def contradicts(self, other):
        """
        Accomplished by testing whether self would imply other if
        other had an opposite value for rule_valid? What if
        rule_valid was None (undecided)?
        """
        return self >= other.negated()


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
