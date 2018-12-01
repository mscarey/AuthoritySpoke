import datetime
import json
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
    """A "natural person" mentioned as an entity in a factor. On the distinction
    between "human" and "person", see Slaughter-House Cases, 83 U.S. 36, 99.
    https://www.courtlistener.com/opinion/88661/slaughter-house-cases/"""

    pass


@dataclass(frozen=True)
class Predicate:
    """
    A statement about real events or about a legal conclusion.
    Predicates may be "alleged" by a pleading, "supported" by evidence, or
    "found" to be factual by a jury verdict or a judge's finding of fact.

    A predicate's self.content string shows where references to specific
    entities from the case can be used as subjects or objects of the predicate.

    Events may be referenced as entities in a predicate's content.
    See Lepore, Ernest. Meaning and Argument: An Introduction to Logic
    Through Language. Section 17.2: The Event Approach

    If self.reciprocal is True, then the order of the first two entities will
    be considered interchangeable. There's no way to make any entities
    interchangeable other than the first two.

    A predicate can also end with a comparison to some quantity, as described
    by a ureg. Quantity object from the pint library. See pint.readthedocs.io.

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
        """Indicates whether self implies the other predicate, which is True if
        they're equal or if their statements about quantity imply it."""

        if not isinstance(other, self.__class__):
            return False
        if self == other:
            return True
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

        if (type(self.quantity) == ureg.Quantity) != (
            type(other.quantity) == ureg.Quantity
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

    def __lt__(self, other) -> bool:
        return other > self

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
    entity_context: Optional[Tuple[int, ...]] = None
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
        if self.predicate > other.predicate and self.absent == other.absent:
            return True
        return False

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
        if self.predicate > other.predicate and other.absent and not self.absent:
            return True
        if other.predicate > self.predicate and self.absent and not other.absent:
            return True
        return False

    # TODO: A function to determine if a factor implies another (transitively)
    # given a list of factors that imply one another or a function for determining
    # which implication relations (represented by production rules?)
    # are binding from the point of view of a particular court.


@dataclass(frozen=True)
class Procedure:
    """A (potential) rule for courts to use in resolving litigation. Described in
    terms of inputs and outputs, and also potentially "even if" factors, which could
    be considered "failed undercutters" in defeasible logic."""

    outputs: Union[Factor, Iterable[Factor]]
    inputs: Union[Factor, Iterable[Factor]] = frozenset([])
    even_if: Union[Factor, Iterable[Factor]] = frozenset([])

    def __post_init__(self):

        if isinstance(self.outputs, Factor):
            object.__setattr__(self, "outputs", frozenset((self.outputs,)))
        if isinstance(self.inputs, Factor):
            object.__setattr__(self, "inputs", frozenset((self.inputs,)))
        if isinstance(self.even_if, Factor):
            object.__setattr__(self, "even_if", frozenset((self.even_if,)))
        for group in (self.outputs, self.inputs, self.even_if):
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
        object.__setattr__(self, "even_if", frozenset(self.even_if))

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
            text += "    Inputs:"
            for f in self.inputs:
                text += "\n" + str(f)
        if self.even_if:
            text += "    Even if:"
            for f in self.even_if:
                text += "\n" + str(f)
        if self.outputs:
            text += "    Outputs:"
            for f in self.outputs:
                text += "\n" + str(f)
        return text

    def match_entity_roles(self, self_entities, other_entities):
        """Make a temporary dict for information from other.
        For each entity slot in each factor in self, check the matching
        entity slot in other. If it contains something that's not already
        in the temp dict, add it and the corresponding symbol from self
        as a key and value. If it contains something that the temp dict
        doesn't match to self's value for that slot, return False. If
        none of the slots return False, return True."""

        entity_roles = {}

        if len(self_entities) != len(other_entities):
            return False

        entity_pairs = zip(self_entities, other_entities)
        for pair in entity_pairs:
            if pair[0] not in entity_roles:
                entity_roles[pair[0]] = pair[1]
            if entity_roles[pair[0]] != pair[1]:
                return False

        return True

    def all_factors(self) -> Set[Factor]:
        """Returns a set of all factors."""

        inputs = self.inputs or set()
        even_if = self.even_if or set()
        return {*self.outputs, *inputs, *even_if}

    def sorted_factors(self) -> List[Factor]:
        """Sorts the procedure's factors into an order that will always be
        the same for the same set of factors, but that doesn't correspond to
        whether the factors are inputs, outputs, or "even if" factors."""

        return sorted(self.all_factors(), key=repr)

    def get_entity_permutations(self) -> Optional[Set[Tuple[int]]]:
        """Returns every possible ordering of entities that could be
        substituted into an ordered list of the factors in the procedure."""

        all_factors = self.all_factors()
        sorted_factors = self.sorted_factors()

        def add_some_entities(
            all_factors: Mapping[Factor, Tuple[int]],
            entity_permutations: list,
            entity_list: list,
            sorted_factors: list,
            i: int,
        ) -> Optional[Set[Tuple[int]]]:
            """Recursive function that flattens the entity labels for
            each of the factors into a list, except that if the order of
            entities can vary, the function continues writing one variant of
            the list but calls a second instance of itself to continue
            writing the other variant list. It may split multiple times
            before it reaches the end of the sequence."""

            if i >= len(sorted_factors):
                entity_permutations.append(tuple(entity_list))
                return None
            if sorted_factors[i].predicate.reciprocal:
                new_entity_list = entity_list.copy()
                reciprocal_entities = [*all_factors[sorted_factors[i]]]
                new_entity_list.append(reciprocal_entities[1])
                new_entity_list.append(reciprocal_entities[0])
                new_entity_list.extend(reciprocal_entities[2:])
                add_some_entities(
                    all_factors,
                    entity_permutations,
                    new_entity_list,
                    sorted_factors,
                    i + 1,
                )
            entity_list.extend(all_factors[sorted_factors[i]])
            add_some_entities(
                all_factors, entity_permutations, entity_list, sorted_factors, i + 1
            )
            return set(entity_permutations)

        return add_some_entities(all_factors, [], [], sorted_factors, 0)

    def __eq__(self, other):
        """Determines if the two procedures have all the same factors
        with the same entities in the same roles, not whether they're
        actually the same Python object."""

        if not isinstance(other, Procedure):
            return False

        if len(other) != len(self):  # redundant?
            return False

        def find_matches(self_factors, other_factors, matches, matchlist):
            sf = {f for f in self_factors}
            if not sf:
                matchlist.append(matches)
                return matchlist
            s = sf.pop()
            for o in other_factors:
                if s == o:
                    if all(
                        matches[s.entity_context[i]] == o.entity_context[i]
                        or not matches[s.entity_context[i]]
                        for i in range(len(s))
                    ):
                        for i in range(len(s)):
                            matches[s.entity_context[i]] = o.entity_context[i]
                        matchlist = find_matches(sf, other_factors, matches, matchlist)
                    if s.predicate.reciprocal:  # please refactor
                        swapped = list(
                            [
                                o.entity_context[1],
                                o.entity_context[0],
                                o.entity_context[2:],
                            ]
                        )
                        if all(
                            matches[s.entity_context[i]] == swapped[i]
                            or not matches[s.entity_context[i]]
                            for i in range(len(s))
                        ):
                            for i in s.entity_context:
                                matches[i] = swapped[i]
                            matchlist = find_matches(
                                sf, other_factors, matches, matchlist
                            )
            return matchlist

        matchlist = [[None for i in range(len(self))]]

        for x in (
            (self.outputs, other.outputs),
            (self.inputs, other.inputs),
            (self.even_if, other.even_if),
        ):

            # Not equal if self has any factor other lacks
            for factor in x[0]:
                if not any(factor == other_factor for other_factor in x[1]):
                    return False

            # Not equal if other has any factor self lacks
            for other_factor in x[1]:
                if not any(factor == other_factor for factor in x[0]):
                    return False

            # converting to prior_list to start over searching for new matches
            # when moving from outputs to inputs or to even_if
            prior_list = matchlist.copy()
            matchlist = []
            for m in prior_list:
                matchlist = find_matches(x[0], x[1], m, matchlist)

        return bool(matchlist)

    def entities_of_implied_factors(
        self, other: Factor, factor_group: str = "outputs"
    ) -> Dict[Factor, Optional[Tuple[Tuple[int, ...], ...]]]:
        """
        Gets every order of entities from every factor in other that
        would cause each factor of self to be implied by other.
        Takes into account swapped entities for reciprocal factors.

        This method doesn't reveal which factor of other will imply any
        particular factor of self, if the factor of self has the correct
        entities. It shouldn't matter, if the purpose is to tell which
        entities to select to cause each factor of self to be implied by other.

        This should handle entity matching for the __gt__ function.
        """

        if factor_group == "inputs":
            self_factors = self.inputs or {}
            other_factors = other.inputs or {}
        elif factor_group == "outputs":
            self_factors = self.outputs
            other_factors = other.outputs
        elif factor_group == "even_if":
            self_factors = self.even_if or {}
            other_even_if = other.even_if or {}
            other_inputs = other.inputs or {}
            other_factors = {**other_even_if, **other_inputs}
        else:
            raise ValueError(
                f'"factor_group" must be "inputs", "outputs", or "even_if", not {factor_group}.'
            )

        normal_order = {
            f: list(other_factors[x] for x in other_factors.keys() if x > f)
            for f in self_factors.keys()
        }
        reciprocal_order = {
            f: list(
                (other_factors[x][1], other_factors[x][0], *other_factors[x][2:])
                for x in other_factors.keys()
                if x.predicate.reciprocal and x > f
            )
            for f in self_factors.keys()
        }
        return {
            f: tuple((*normal_order[f], *reciprocal_order[f]))
            for f in self_factors.keys()
        }

    def __lt__(self, other):
        """
        For other to imply self:
        All outputs of other are implied by outputs of self with matching entities
        All inputs of self are implied by inputs of other with matching entities
        All even_if factors of other are implied by even_if factors or inputs of self
        """

        # TODO: maybe generate every combination of self's factors where every factor
        # that needs to be implied is implied, and for each factor combination,
        # check every entity marker combination. Only need one match to return True.
        # If the factors have a consistent order by repr, the entity markers can just be
        # a sequence of ints.

        if not isinstance(other, Procedure):
            return False

        # matching["inputs"] shows the entities each factor in self.inputs would
        # have to take to be implied by other.inputs with other's default entities.

        # matching["outputs"] and matching["even_if"] show the entities each factor
        # in other.outputs and other.even_if would have to take to be implied by self
        # with self's default entities.

        matching = {
            "inputs": self.entities_of_implied_factors(other, "inputs"),
            "outputs": other.entities_of_implied_factors(self, "outputs"),
            "even_if": other.entities_of_implied_factors(self, "even_if"),
        }

        # If any factor doesn't match with any entity set, that part of the problem is
        # unsatisfiable and other can't imply self.

        if any(
            any(not matching[group][factor] for factor in matching[group])
            for group in matching
        ):
            return False

        return False

    def exhaustive_implies(self, other):
        """
        This is a different process for checking whether one procedure implies another,
        used when the list of self's inputs is considered an exhaustive list of the
        circumstances needed to invoke the procedure (i.e. when the rule "always" applies
        when the inputs are present).

        For other to imply self:
        All outputs of other are implied by outputs of self with matching entities
        All inputs of self are implied by inputs of other with matching entities
        No even_if factors of other are contradicted by inputs of self
        """

        pass


@dataclass
class Holding:
    """A statement in which a court posits a legal rule as authoritative,
    deciding some aspect of the current litigation but also potentially
    binding future courts to follow the rule. When holdings appear in
    judicial opinions they are often hypothetical and don't necessarily
    imply that the court accepts the factual assertions or other factors
    that make up the inputs or outputs of the procedure mentioned in the
    holding."""

    procedure: Optional[Procedure] = None
    mandatory: bool = False
    universal: bool = False
    rule_valid: Union[bool, None] = True


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
