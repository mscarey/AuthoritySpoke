import datetime
import json

from typing import Dict, Optional, Sequence, Tuple, Union
from dataclasses import dataclass


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
    """A "natural person" mentioned as an entity in a factor.
    See Slaughter-House Cases, 83 U.S. 36, 99,
    https://www.courtlistener.com/opinion/88661/slaughter-house-cases/"""

    pass


@dataclass(frozen=True)
class Predicate:
    """A statement about real events or about legal conclusions.
    Predicates may be "alleged" by a pleading, "supported" by evidence, or
    "found" to be factual by a jury verdict or a judge's finding of fact.

    If reciprocal==True, then the order of the first two entities will
    be considered interchangeable."""

    content: str
    truth: bool = True
    reciprocal: bool = False

    def __post_init__(self):
        if len(self) < 2 and self.reciprocal:
            raise ValueError(
                f'"reciprocal" flag not allowed because {self.content} '
                f"has {len(self)} entities, fewer than 2."
            )

    def __len__(self):
        return self.content.count("{}")

    def __str__(self):
        truth_prefix = "It is false that " if not self.truth else ""
        return f'{truth_prefix}{self.content}'

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
        return (f"{'Absent ' if self.absent else ''}{self.__class__.__name__}: " +
               f"{self.predicate.content_with_entities(entities)}")

    def contradicts(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.predicate.contradicts(other.predicate) and not (self.absent | other.absent):
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

    def match_entity_roles(self, self_factors, other_factors):
        """Make a temporary dict for information from other.
        For each entity slot in each factor in self, check the matching
        entity slot in other. If it contains something that's not already
        in the temp dict, add it and the corresponding symbol from self
        as a key and value. If it contains something that the temp dict
        doesn't match to self's value for that slot, return False. If
        none of the slots return False, return True."""

        entity_roles = {}

        self_factor_list = sorted(self_factors, key=str)
        other_factor_list = sorted(other_factors, key=str)

        # TODO: to create a __gt__ test, test whether each factor in one holding
        # implies a factor in the other...and also has the entity markers
        # in the right order

        if len(self_factor_list) != len(other_factor_list):
            return False
        factor_pairs = zip(self_factor_list, other_factor_list)
        for pair in factor_pairs:

            # tests whether the corresponding factors have the
            # same string representation

            if str(pair[0]) != str(pair[1]):
                return False

            # tests whether the corresponding factors have the
            # same number of entities (unnecessary?)

            if len(self_factors[pair[0]]) != len(other_factors[pair[1]]):
                return False
            for i in range(len(self_factors[pair[0]])):
                self_entity_label = self_factors[pair[0]][i]
                other_entity_label = other_factors[pair[1]][i]
                if self_entity_label not in entity_roles:
                    entity_roles[self_entity_label] = other_entity_label
                if entity_roles[self_entity_label] != other_entity_label:
                    return False
        return True

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
            if not self.match_entity_roles(x[0], x[1]):
                return False

        return True


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
