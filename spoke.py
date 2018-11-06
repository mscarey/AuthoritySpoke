from typing import Dict, Sequence, Union

class Entity:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

class Person(Entity):
    pass

class Predicate:

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
    pass

class Fact:

    def __init__(self, predicate: Predicate, truth_of_predicate: bool = True):

        self.predicate = predicate
        self.truth_of_predicate = truth_of_predicate

    def __str__(self):
        return f'Fact: {self.predicate}'

    def str_in_context(self, entities: Sequence[Entity]):
        content = self.predicate.content_with_entities(
            entities, self.truth_of_predicate)
        return f'Fact: {content}'


class Holding:

    def __init__(self, inputs: Dict[Factor, str], outputs: Dict[Factor, str],
                 rule_valid: Union[bool, None] = True):

        self.rule_valid = rule_valid
