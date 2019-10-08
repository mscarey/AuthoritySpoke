from authorityspoke.io import name_index, readers, schemas


class TestCollectMentioned:
    def test_mentioned_from_entity(self):
        obj = {"type": "Entity", "name": "Ann"}
        mentioned = name_index.collect_mentioned(obj)
        assert mentioned["Ann"]["type"] == "Entity"

    def test_insert_in_mentioned_does_not_change_obj(self):
        mentioned = name_index.Mentioned()
        obj = {"type": "Entity", "name": "Remainer"}
        mentioned.insert_by_name(obj)
        assert obj["name"] == "Remainer"
        assert "name" not in mentioned["Remainer"].keys()

    relevant_dict = {
        "content": "{} is relevant to show {}",
        "type": "Fact",
        "name": "relevant fact",
        "context_factors": [
            {"content": "{Short Name} shot {Longer Name}", "type": "Fact"},
            {
                "content": "{} murdered {}",
                "context_factors": ["Short Name", "Longer Name"],
                "type": "Fact",
            },
        ],
    }

    def test_expand_shorthand(self):
        obj = name_index.expand_shorthand_mentioned(self.relevant_dict)
        assert obj["context_factors"][0]["context_factors"][0]["name"] == "Short Name"

    def test_mentioned_from_fact_and_entities(self):
        obj = name_index.expand_shorthand_mentioned(self.relevant_dict)
        mentioned = name_index.collect_mentioned(self.relevant_dict)
        assert mentioned["relevant fact"]["type"] == "Fact"
        shooting = mentioned["relevant fact"]["context_factors"][0]
        assert shooting["context_factors"][0]["name"] == "Short Name"

    def test_mentioned_ordered_by_length(self):
        obj, mentioned = name_index.index_names(self.relevant_dict)
        mentioned = mentioned.sorted_by_length()
        shortest = mentioned.popitem()
        assert shortest[0] == "Short Name"


class TestRetrieveMentioned:
    def test_retrieve_mentioned_during_load(self):
        """
        Test that the schema can recreate the Entity objects "Alice" and
        "Bob" from just their name strings, by having added them to
        "mentioned" when they first appeared.
        """
        relevant_dict = {
            "predicate": {"content": "{} is relevant to show {}"},
            "type": "Fact",
            "context_factors": [
                {
                    "predicate": {"content": "{} shot {}"},
                    "context_factors": [
                        {"name": "Alice", "type": "Entity"},
                        {"name": "Bob", "type": "Entity"},
                    ],
                    "type": "Fact",
                },
                {
                    "predicate": {"content": "{} murdered {}"},
                    "context_factors": ["Alice", "Bob"],
                    "type": "Fact",
                },
            ],
        }
        relevant_fact = readers.read_fact(relevant_dict)
        assert relevant_fact.context_factors[1].context_factors[1].name == "Bob"

    def test_retrieve_references_with_substring(self):
        """
        The Mentioned object must be sorted longest to shortest.

        Also, the name used as the key for the Mentioned dict will
        have to be included in each Entity dict in the `context`
        list created by `get_references_from_mentioned`.
        """

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
