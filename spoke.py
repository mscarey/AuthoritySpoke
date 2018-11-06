from typing import Dict, Optional, Sequence, Union

class Entity:
    """A person, place, thing, or event that needs to be mentioned in
    multiple predicates/factors in a holding."""

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

class Human(Entity):
    """A "natural person". See Slaughter-House Cases, 83 U.S. 36, 99,
    https://www.courtlistener.com/opinion/88661/slaughter-house-cases/"""
    pass

class Predicate:
    """A statement about real events or about legal conclusions.
    Predicates may be "alleged" by a pleading, "supported" by evidence, or
    "found" to be factual by a jury verdict or a judge's finding of fact"""

    def __init__(self, content: str, reciprocal: bool = False):
        self.content = content
        self.reciprocal = reciprocal

        if len(self) != 2 and self.reciprocal:
            raise ValueError(
                f'"Reciprocal" flag is only allowed with exactly 2 entities.')

    def __len__(self):
        return self.content.count("{}")

    def __str__(self):
        return self.content

    def content_with_truth(self, truth_of_predicate=True) -> str:
        truth_prefix = "It is false that " if not truth_of_predicate else ""
        return truth_prefix + self.content

    def content_with_entities(self, entities: Union[Entity, Sequence[Entity]],
                              truth_of_predicate=True) -> str:
        """Creates a sentence by substituting the names of entities
        from a particular case into the predicate_with_truth."""
        if isinstance(entities, Entity):
            entities = (entities,)
        if len(entities) != len(self):
            raise ValueError(
                f'Exactly {len(self)} entities needed to complete ' +
                f'"{self.content}", but {len(entities)} were given.')

        return self.content_with_truth(truth_of_predicate).format(
            *(str(e) for e in entities))

class Factor:
    """A factor is something used to determine the applicability of a legal
    procedure. Factors can be both inputs and outputs of legal procedures.
    In a chain of legal procedures, the outputs of one may become inputs for
    another. Common types of factors include Facts, Evidence, Allegations,
    Motions, and Arguments."""
    pass

class Fact(Factor):
    """An assertion accepted as factual by a court, often through factfinding by
    a judge or jury."""

    def __init__(self, predicate: Predicate, truth_of_predicate: bool = True):

        self.predicate = predicate
        self.truth_of_predicate = truth_of_predicate

    def __str__(self):
        return f'Fact: {self.predicate}'

    def str_in_context(self, entities: Sequence[Entity]) -> str:
        content = self.predicate.content_with_entities(
            entities, self.truth_of_predicate
            )
        return f'Fact: {content}'


class Holding:
    """A statement of law about how courts should resolve litigation. Holdings
    can be described as legal procedures in terms of inputs and outputs. When
    holdings appear in judicial opinions they are often hypothetical and
    don't necessarily imply that the court accepts the factual assertions or
    other factors that make up their inputs or outputs."""

    def __init__(self, outputs: Dict[Factor, Sequence[int]],
                 inputs: Optional[Dict[Factor, Sequence[int]]] = None,
                 even_if: Optional[Dict[Factor, Sequence[int]]] = None,
                 mandatory: bool = False,
                 universal: bool = False,
                 rule_valid: Union[bool, None] = True):

        self.outputs = outputs
        self.inputs = inputs
        self.even_if = even_if
        self.mandatory = mandatory
        self.universal = universal
        self.rule_valid = rule_valid

    def __eq__(self, other):
        return False