from authorityspoke.io import loaders, readers, schemas
from authorityspoke.io import name_index, text_expansion


class TestCollectMentioned:
    def test_mentioned_from_entity(self):
        obj = {"type": "Entity", "name": "Ann"}
        obj, mentioned = name_index.collect_mentioned(obj)
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
        obj = text_expansion.expand_shorthand(self.relevant_dict)
        assert obj["context_factors"][0]["context_factors"][0]["name"] == "Short Name"

    def test_expand_shorthand_turns_context_factor_str_into_list(self):
        short_shot_long = text_expansion.expand_shorthand(
            self.relevant_dict["context_factors"][0]
        )
        assert isinstance(short_shot_long["context_factors"], list)

    def test_assign_name(self):
        """
        The collect_mentioned function should assign name to this Fact
        because it doesn't already have one.
        """
        short_shot_long = text_expansion.expand_shorthand(
            self.relevant_dict["context_factors"][0]
        )
        with_name, mentioned = name_index.collect_mentioned(short_shot_long)
        assert with_name["name"] == "Short Name shot Longer Name"

    def test_mentioned_from_fact_and_entities(self):
        obj = text_expansion.expand_shorthand(self.relevant_dict)
        obj, mentioned = name_index.collect_mentioned(obj)
        assert mentioned["relevant fact"]["type"] == "Fact"
        shooting = mentioned["relevant fact"]["context_factors"][0]
        assert shooting["context_factors"][0]["name"] == "Short Name"

    def test_mentioned_ordered_by_length(self):
        record, mentioned = name_index.index_names(self.relevant_dict)
        shortest = mentioned.popitem()
        assert shortest[0] == "Short Name"

    def test_name_inferred_from_content(self, make_regime):
        """
        Test that a name field is generated for Factors without them.

        The Factors must be inserted in "mentioned" with the generated name.
        """

        oracle_records = loaders.load_holdings("holding_oracle.json")
        oracle_holdings = readers.read_holdings(oracle_records, regime=make_regime)
        factor = oracle_holdings[2].inputs[0]
        assert factor.content == "{} was an original work"

    def test_enactment_name_index(self, make_regime):
        """
        Test error message:
        'Name "securing for authors" not found in the index of mentioned Factors'
        """
        feist_records = loaders.load_holdings("holding_feist.json")
        record, mentioned = name_index.index_names(feist_records)
        assert "securing for authors" in mentioned

    def test_context_factor_not_collapsed(self, make_regime):
        """
        There is a context factor listed for this Fact, but it hasn't been collapsed
        in the content phrase.
        """
        holding = {
            "inputs": {
                "type": "fact",
                "content": "Rural's telephone listings were names, towns, and telephone numbers of telephone subscribers",
                "context_factors": {
                    "type": "entity",
                    "name": "Rural's telephone listings",
                    "plural": True,
                },
            },
            "outputs": {
                "type": "fact",
                "content": "Rural's telephone listings were an original work",
                "truth": False,
            },
        }
        holding = text_expansion.expand_shorthand(holding)
        built = readers.read_holding(record=holding, regime=make_regime)
        assert built.inputs[0].short_string.startswith(
            "the fact that <Rural's telephone listings> were names"
        )

    def test_enactment_name_in_holding(self, make_regime):
        """
        Test error message:
        'Name "securing for authors" not found in the index of mentioned Factors'
        """
        feist_records = loaders.load_holdings("holding_feist.json")
        feist_holdings = readers.read_holdings(feist_records, regime=make_regime)
        assert "securing for authors" in str(feist_holdings)


class TestRetrieveMentioned:
    def test_add_found_context_to_content(self):
        fact = {
            "type": "fact",
            "predicate": {"content": "{} threw a pie at Larry but it hit {}"},
            "context_factors": [
                {"type": "Entity", "name": "Moe"},
                {"type": "Entity", "name": "Curly"},
            ],
        }
        obj = {"type": "Entity", "name": "Larry"}
        (
            fact["predicate"]["content"],
            fact["context_factors"],
        ) = text_expansion.add_found_context(
            fact["predicate"]["content"], fact["context_factors"], obj
        )
        assert fact["predicate"]["content"] == "{} threw a pie at {} but it hit {}"
        assert fact["context_factors"][1]["name"] == "Larry"

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

    def test_get_references_without_changing_mentioned(self):
        """
        This isn't catching the bug where the mentioned dict is mutated.
        """
        schema = schemas.HoldingSchema()
        schema.context["mentioned"] = name_index.Mentioned(
            {
                "Bradley": {"type": "entity"},
                "fact that Bradley committed a crime": {
                    "type": "fact",
                    "content": "Bradley committed a crime",
                },
            }
        )
        assert (
            schema.context["mentioned"]["fact that Bradley committed a crime"][
                "content"
            ]
            == "Bradley committed a crime"
        )
        new = {
            "inputs": "fact that Bradley committed a crime",
            "outputs": {"type": "fact", "content": "Bradley committed a tort"},
        }
        holding = schema.load(new)
        assert holding.inputs[0].context_factors[0].name == "Bradley"
        # Making the same assertion again to show it's still true
        assert (
            schema.context["mentioned"]["fact that Bradley committed a crime"][
                "content"
            ]
            == "Bradley committed a crime"
        )

    overlapping_names_mentioned = {
        "Godzilla": {"type": "Entity"},
        "Mothra": {"type": "Entity"},
        "Mecha Godzilla": {"type": "Entity"},
    }

    def test_retrieve_references_with_substring(self):
        """
        The Mentioned object must be sorted longest to shortest.

        Also, the name used as the key for the Mentioned dict will
        have to be included in each Entity dict in the `context`
        list created by `get_references_from_mentioned`.
        """

        mentioned = name_index.Mentioned(self.overlapping_names_mentioned)
        content = "Mecha Godzilla threw Mothra at Godzilla"
        schema = schemas.FactSchema()
        mentioned = mentioned.sorted_by_length()
        schema.context["mentioned"] = mentioned
        new_content, context = schema.get_references_from_mentioned(content)
        assert new_content == "{} threw {} at {}"
        assert context[2] == {"name": "Godzilla", "type": "Entity"}

    def test_mentioned_object_string(self):
        mentioned = name_index.Mentioned(self.overlapping_names_mentioned)
        assert "Mentioned({'Godzilla'" in str(mentioned)
        assert "Mentioned({'Godzilla'" in repr(mentioned)

    def test_unmarked_factor_when_one_was_marked(self):
        fact = {
            "type": "fact",
            "content": "{} lived at Elsinore",
            "context_factors": [{"type": "Entity", "name": "Hamlet"}],
        }
        schema = schemas.FactSchema()
        schema.context["mentioned"] = name_index.Mentioned(
            {"Elsinore": {"type": "Entity"}}
        )
        loaded = schema.load(fact)
        assert loaded.predicate.content == "{} lived at {}"
