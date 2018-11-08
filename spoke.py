from typing import Dict, Optional, Sequence, Tuple, Union

class Entity:
    """A person, place, thing, or event that needs to be mentioned in
    multiple predicates/factors in a holding."""

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

class Human(Entity):
    """A "natural person" mentioned as an entity in a factor.
    See Slaughter-House Cases, 83 U.S. 36, 99,
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
                '"reciprocal" flag is only allowed with exactly 2 entities.')

    def __hash__(self):
        return hash((self.content, self.reciprocal))

    def __len__(self):
        return self.content.count("{}")

    def __repr__(self):
        return f'Predicate({self.content}, {self.reciprocal})'

    def __str__(self):
        return self.content

    def __eq__(self, other):
        if not isinstance(other, Predicate):
            return False
        return self.content == other.content and self.reciprocal == other.reciprocal

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

    def __hash__(self):
        return hash((self.predicate, self.truth_of_predicate))

    def __str__(self):
        return f'Fact: {self.predicate}'

    def __repr__(self):
        return f'Fact("{self.predicate}", {self.truth_of_predicate})'

    def __gt__(self, other):
        return NotImplemented

    def __eq__(self, other):
        if not isinstance(other, Fact):
            return False
        return (self.predicate == other.predicate) & (self.truth_of_predicate == other.truth_of_predicate)

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

    def __init__(self, outputs: Dict[Factor, Tuple[int]],
                 inputs: Optional[Dict[Factor, Tuple[int]]] = None,
                 even_if: Optional[Dict[Factor, Tuple[int]]] = None,
                 mandatory: bool = False,
                 universal: bool = False,
                 rule_valid: Union[bool, None] = True):

        self.outputs = outputs
        self.inputs = inputs or {}
        self.even_if = even_if or {}

        """TODO: Maybe what's currently called a Holding object should be
        called a Procedure object, except that I should factor out the next
        three flags and put them on a new object type called a
        Holding which is a relation between an Opinion and a Procedure."""

        self.mandatory = mandatory
        self.universal = universal
        self.rule_valid = rule_valid

    def __hash__(self):
        return hash((tuple(self.outputs), tuple(self.inputs), tuple(self.even_if),
                self.mandatory, self.universal, self.rule_valid))



    def match_entity_roles(self, other):
        """Make a temporary dict for information from other.
        For each entity slot in each factor in self, check the matching
        entity slot in other. If it contains something that's not already
        in the temp dict, add it and the corresponding symbol from self
        as a key and value. If it contains something that the temp dict
        doesn't match to self's value for that slot, return False. If
        none of the slots return False, return True."""

        entity_roles = {}
        for x in zip((self.outputs, self.inputs, self.even_if),
                     (other.outputs, other.inputs, other.even_if)):
            self_factor_list = sorted(x[0], key=str)
            other_factor_list = sorted(x[1], key=str)
            if len(self_factor_list) != len(other_factor_list):
                return False
            factor_pairs = zip(self_factor_list, other_factor_list)
            for pair in factor_pairs:
                if str(pair[0]) != str(pair[1]):
                    return False
                for i in range(len(x[0][pair[0]])):
                    self_entity_label = x[0][pair[0]][i]
                    other_entity_label = x[1][pair[1]][i]
                    if self_entity_label not in entity_roles:
                        entity_roles[self_entity_label] = other_entity_label
                    if entity_roles[self_entity_label] != other_entity_label:
                        return False
        return True

    def __eq__(self, other):
        """Determines if the two holdings have all the same factors
        with the same entities in the same roles, not whether they're
        actually the same Python object."""

        if not isinstance(other, Holding):
            return False

        if (self.mandatory != other.mandatory) or \
            (self.universal != other.universal) or \
            (self.rule_valid != other.rule_valid):
            return False

        if not self.match_entity_roles(other):
            return False

        return other.match_entity_roles(self)

    def __repr__(self):
        return (f'{self.__class__.__name__}('
        f'{self.outputs}, {self.inputs}, {self.even_if}, '
        f'{self.mandatory}, {self.universal}, {self.rule_valid})')
