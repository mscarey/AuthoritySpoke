from authorityspoke.io import name_index, schemas


class TestMentioned:
    def test_references_from_mentioned_with_substring(self):
        mentioned = name_index.Mentioned(
            {
                "Godzilla": {"type": "Entity"},
                "Mothra": {"type": "Entity"},
                "Mecha Godzilla": {"type": "Entity"},
            }
        )
        content = "Mecha Godzilla threw Mothra at Godzilla"
        schema = schemas.FactSchema()
        schema.context["mentioned"] = mentioned
        new_content, context = schema.get_references_from_mentioned(content)
        assert new_content == "{} threw {} at {}"
        assert context[2] == {"name": "Godzilla", "type": "Entity"}
