import datetime
import json

from typing import Dict, List, Mapping, Optional, Sequence, Set, Tuple, Union
from dataclasses import dataclass

from pint import UnitRegistry

ureg = UnitRegistry()
Q_ = ureg.Quantity

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
    between "human" and "person", see Slaughter-House Cases, 83 U.S. 36, 99,
    https://www.courtlistener.com/opinion/88661/slaughter-house-cases/"""

    pass


@dataclass(frozen=True)
class Predicate:
    """
    A statement about real events or about legal conclusions.
    Predicates may be "alleged" by a pleading, "supported" by evidence, or
    "found" to be factual by a jury verdict or a judge's finding of fact.

    If reciprocal==True, then the order of the first two entities will
    be considered interchangeable. There's no way to make any entities
    interchangeable other than the first two.

    A predicate can also end with a comparison to some quantity, as described
    by a ureg.Quantity object from the pint library. See pint.readthedocs.io.

    If a quantity is defined, a "comparison" should also be defined. That's
    a string indicating whether the thing described by the predicate is
    greater than, less than, or equal to the quantity. Even though "="
    is the default, it's the least useful, because courts almost always state
    rules that are intended to apply to quantities above or below some threshold.
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
        if self.comparison == "==":
            self.comparison = "="
        comparison_options = ("<", "<=", "=", ">=", ">")
        if self.comparison and self.comparison not in comparison_options:
            raise ValueError(
                f'"comparison" string parameter must be one of {comparison_options}.'
            )

    def __len__(self):
        """Returns the number of entities that can fit in the bracketed slots
        in the predicate. self.quantity doesn't count as one of these entities,
        even though it does go in a slot."""

        slots = self.content.count("{}")
        if self.quantity:
            slots -= 1
        return slots

    def __str__(self):
        truth_prefix = "It is false that " if not self.truth else ""
        if self.quantity:
            slots = ("{}" for slot in range(len(self)))
            content = self.content.format(*slots, self.quantity_str())
        else: content = self.content
        return f"{truth_prefix}{content}"

    def quantity_str(self):
        if not self.quantity:
            return None
        comparison = self.comparison or "="
        expand = {
            "=": "equal to",
            ">": "greater than",
            "<": "less than",
            ">=": "at least",
            "<=": "no more than",
                }
        return f'{expand[comparison]} {self.quantity}'


    def contradicts(self, other):
        """This returns false only if the content is exactly the same and self.truth is
        different. Will break if symbols for entities are allowed to appear in self.content.
        """
        if isinstance(other, self.__class__):
            return self.content == other.content and self.truth != other.truth
        return False

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
    absent: bool = False

    def __str__(self):
        return f"{'Absent ' if self.absent else ''}{self.__class__.__name__}: {self.predicate}"

    def __gt__(self, other):
        return NotImplemented

    def predicate_in_context(self, entities: Sequence[Entity]) -> str:
        return (
            f"{'Absent ' if self.absent else ''}{self.__class__.__name__}: "
            + f"{self.predicate.content_with_entities(entities)}"
        )

    def contradicts(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.predicate.contradicts(other.predicate) and not (
            self.absent | other.absent
        ):
            return True
        if (self.predicate == other.predicate) and (self.absent != other.absent):
            return True
        return False

    # TODO: I'd like a function to determine if a factor implies another,
    # but it would need entity context,
    # and I guess it would have to be from the point of view of a particular court.


@dataclass(frozen=True)
class Procedure:
    """A (potential) rule for courts to use in resolving litigation. Described in
    terms of inputs and outputs, and also potentially "even if" factors, which could
    be considered "failed undercutters" in defeasible logic."""

    outputs: Dict[Factor, Tuple[int]]
    inputs: Optional[Dict[Factor, Tuple[int]]] = None
    even_if: Optional[Dict[Factor, Tuple[int]]] = None

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

    def all_factors(self) -> Dict[Factor, Tuple[int]]:
        """Used for the entity_permutations function."""
        inputs = self.inputs or {}
        even_if = self.even_if or {}
        return {**self.outputs, **inputs, **even_if}

    def sorted_factors(self) -> List[Factor]:
        """Used for the entity_permutations function."""
        return sorted(self.all_factors(), key=repr)

    def entity_permutations(self) -> Set[List[int]]:
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
        """Determines if the two holdings have all the same factors
        with the same entities in the same roles, not whether they're
        actually the same Python object."""

        if not isinstance(other, Procedure):
            return False

        for x in (
            (self.outputs, other.outputs),
            (self.inputs or {}, other.inputs or {}),
            (self.even_if or {}, other.even_if or {}),
        ):
            if x[0].keys() != x[1].keys():
                return False

        return any(
            (self.match_entity_roles(x, y) and self.match_entity_roles(y, x))
            for x in self.entity_permutations()
            for y in other.entity_permutations()
        )

    # TODO: to create a __gt__ test, test whether each factor in one holding
    # implies a factor in the other...and also has the entity markers
    # in the right order


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
