from typing import Dict, Union

class Entity:
    def __init__(self, name: str):
        self.name = name

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


class Factor:
    pass

class Fact:

    def __init__(self, predicate: Predicate, truth_of_predicate: bool = True):

        self.predicate = predicate
        self.truth_of_predicate = truth_of_predicate

    def __str__(self):
        return f'Fact: {self.predicate_with_truth()}'

    def predicate_with_truth(self):
        truth = "It is false that " if not self.truth_of_predicate else ""
        return f'{truth}{self.predicate}'

    def predicate_with_entities(self, entities: list) -> str:
        """Creates a sentence by substituting the names of entities
        from a particular case."""

        if len(entities) != len(self.predicate):
            raise ValueError(
                f'Exactly {len(self.predicate)} entities needed to complete ' +
                f'"{self.predicate}", but {len(entities)} were given.')
        return self.predicate_with_truth().format(*entities)

class Holding:

    def __init__(self, inputs: Dict[Factor, str], outputs: Dict[Factor, str],
                 rule_valid: Union[bool, None] = True):

        self.rule_valid = rule_valid
