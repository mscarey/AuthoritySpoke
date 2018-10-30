class Factor:

    def __init__(self, content: str, level: str = "Fact"):
        self.content = content
        self.level = level

    def __str__(self):
        return f'{self.level}: {self.content}'

    def __len__(self):
        return self.content.count("{}")

    def content_with_entities(self, entities: list):
        """Creates a sentence by substituting the names of entities
        from a particular case."""

        if len(entities) != len(self):
            raise ValueError(
                f'Exactly {len(self)} entities needed to complete ' +
                f'"{self.content}", but {len(entities)} were given.')
        return self.content.format(*entities)
