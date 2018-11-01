from typing import Dict, Union

class Factor:

    def __init__(self, predicate: str, truth_of_predicate: bool = True,
        level: str = "Fact", reciprocal: bool = False):

        self.predicate = predicate
        self.truth_of_predicate = truth_of_predicate
        self.level = level
        self.reciprocal = reciprocal

        if len(self) != 2 and self.reciprocal:
            raise ValueError(
                f'"Reciprocal" flag is only allowed with exactly 2 entities.')

    def __str__(self):
        return f'{self.level}: {self.predicate_with_truth()}'

    def __len__(self):
        return self.predicate.count("{}")

    def predicate_with_truth(self):
        truth = "It is false that " if not self.truth_of_predicate else ""
        return f'{truth}{self.predicate}'

    def predicate_with_entities(self, entities: list) -> str:
        """Creates a sentence by substituting the names of entities
        from a particular case."""

        if len(entities) != len(self):
            raise ValueError(
                f'Exactly {len(self)} entities needed to complete ' +
                f'"{self.predicate}", but {len(entities)} were given.')
        return self.predicate_with_truth().format(*entities)

class Holding:

    def __init__(self, inputs: Dict[Factor, str], outputs: Dict[Factor, str],
                 rule_valid: Union[bool, None] = True):

        self.rule_valid = rule_valid
        pass
