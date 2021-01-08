import os

from dotenv import load_dotenv

from legislice.download import Client

from authorityspoke.io import loaders, readers, schemas
from authorityspoke.io import name_index, text_expansion

load_dotenv()

TOKEN = os.getenv("LEGISLICE_API_TOKEN")


class TestCollectMentioned:
    client = Client(api_token=TOKEN)

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

    def test_index_names(self, raw_factor):
        obj, mentioned = name_index.index_names(raw_factor["relevant"])
        factor = mentioned[obj]["context_factors"][0]
        assert mentioned[factor]["context_factors"][0] == "Short Name"

    def test_index_names_turns_context_factor_str_into_list(self, raw_factor):
        short_shot_long, mentioned = name_index.index_names(
            raw_factor["relevant"]["context_factors"][0]
        )
        assert isinstance(mentioned[short_shot_long]["context_factors"], list)

    def test_index_before_apostrophe(self):
        """
        Not catching the error where 'Bradley exhibited an expectation of privacy in
        Bradley's marijuana patch' becomes '{} exhibited an expectation of privacy in {{}'
        """
        raw_holding = {
            "outputs": [
                {
                    "type": "Fact",
                    "content": "the {possessive noun}'s factor was linked correctly",
                },
                {
                    "type": "Fact",
                    "content": "the possessive noun's factor was still linked correctly",
                },
            ],
        }
        holding, mentioned = name_index.index_names(raw_holding)
        factor_name_1 = holding["outputs"][0]
        assert mentioned[factor_name_1]["context_factors"][0] == "possessive noun"
        factor_name_2 = holding["outputs"][1]
        assert mentioned[factor_name_2]["context_factors"][0] == "possessive noun"

    def test_update_context_from_bracketed_name(self):
        content = "{} sent a message to {Bob's friend}"
        context_factors = [{"type": "Entity", "name": "Bob"}]
        new_content, context_factors = text_expansion.get_references_from_string(
            content, context_factors
        )
        assert new_content == "{} sent a message to ${bob_s_friend}"
        assert len(context_factors) == 2

    def test_assign_name(self, raw_factor):
        """
        The collect_mentioned function should assign a name to this Fact
        because it doesn't already have one.
        """
        short_shot_long = text_expansion.expand_shorthand(
            raw_factor["relevant"]["context_factors"][0]
        )
        collapsed, mentioned = name_index.collect_mentioned(short_shot_long)
        assert collapsed == "Short Name shot Longer Name"
        assert mentioned[collapsed]["context_factors"][0] == "Short Name"

    def test_mentioned_from_fact_and_entities(self, raw_factor):
        obj = text_expansion.expand_shorthand(raw_factor["relevant"])
        obj, mentioned = name_index.collect_mentioned(obj)
        assert mentioned["relevant fact"]["type"] == "Fact"
        shooting = mentioned["relevant fact"]["context_factors"][0]
        assert mentioned[shooting]["context_factors"][0] == "Short Name"

    def test_mentioned_ordered_by_length(self, raw_factor):
        obj = text_expansion.expand_shorthand(raw_factor["relevant"])
        obj, mentioned = name_index.index_names(obj)
        shortest = mentioned.popitem()
        assert shortest[0] == "Short Name"

    def test_name_inferred_from_content(self, fake_usc_client):
        """
        Test that a name field is generated for Factors without them.

        The Factors must be inserted in "mentioned" with the generated name.
        """

        oracle_records = loaders.load_holdings("holding_oracle.json")
        oracle_holdings = readers.read_holdings(oracle_records, client=fake_usc_client)
        factor = oracle_holdings[2].inputs[0]
        assert factor.content == "${the_java_api} was an original work"

    def test_enactment_name_index(self):
        """
        Test error message:
        'Name "securing the right to writings" not found in the index of mentioned Factors'
        """
        feist_records = loaders.load_holdings("holding_feist.json")
        record, mentioned = name_index.index_names(feist_records)
        assert "securing the right to writings" in mentioned

    def test_context_factor_not_collapsed(self, fake_usc_client):
        """
        There is a context factor listed for this Holding, but it hasn't been collapsed
        in the content phrase.
        """
        holding = {
            "inputs": {
                "type": "fact",
                "content": (
                    "Rural's telephone listings were names, towns, and telephone "
                    "numbers of telephone subscribers"
                ),
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
        built = readers.read_holding(record=holding, client=fake_usc_client)
        assert built.inputs[0].short_string.startswith(
            "the fact that <Rural's telephone listings> were names"
        )

    def test_enactment_name_in_holding(self, fake_usc_client):
        """
        Test error message:
        'Name "securing for authors" not found in the index of mentioned Factors'
        """
        feist_records = loaders.load_holdings("holding_feist.json")
        feist_holding = readers.read_holding(feist_records[0], client=fake_usc_client)
        assert "securing for limited Times" in feist_holding.short_string

    def test_update_name_index_with_longer_factor(self):
        raw_fact = {
            "predicate": {"content": "{Bradley} lived at Bradley's house"},
            "type": "fact",
        }
        old_mentioned = name_index.Mentioned({"Bradley's house": {"type": "Entity"}})
        obj, new_mentioned = name_index.update_name_index_from_fact_content(
            obj=raw_fact, mentioned=old_mentioned
        )
        found_content = obj["predicate"]["content"].lower()
        assert found_content == "${bradley} lived at ${bradley_s_house}"
        # Check that context_factors match the order of the sentence
        assert obj["context_factors"][0]["name"] == "Bradley"
        assert obj["context_factors"][1]["name"] == "Bradley's house"

    def test_link_longest_context_factors_first(self):
        """
        If read_holdings interprets the second "Bradley" string as
        a reference to Bradley rather than "Bradley's house", it's wrong.
        """
        to_read = {
            "outputs": [
                {"type": "fact", "content": "{Bradley's house} was a house"},
                {"type": "fact", "content": "{Bradley} lived at Bradley's house"},
            ]
        }
        record, mentioned = name_index.index_names(to_read)
        lived_at = record["outputs"][1]
        assert mentioned[lived_at]["context_factors"][1] == "Bradley's house"


class TestRetrieveMentioned:
    def test_add_found_context_to_content(self):
        fact = {
            "type": "fact",
            "predicate": {"content": "$moe threw a pie at Larry but it hit $curly"},
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
        assert (
            fact["predicate"]["content"]
            == "$moe threw a pie at ${larry} but it hit $curly"
        )
        assert fact["context_factors"][1]["name"] == "Larry"

    def test_add_found_context_included_in_placeholder_name(self):
        content = (
            "$the_Amazon has slower Amazon deliveries because of ${the_Amazon}'s size"
        )
        context_factors = [{"type": "Entity", "name": "the Amazon"}]
        new_content, new_context_factors = text_expansion.add_found_context(
            content=content,
            context_factors=context_factors,
            factor={"type": "Entity", "name": "Amazon"},
        )
        expected = "$the_Amazon has slower ${amazon} deliveries because of ${the_Amazon}'s size"
        assert new_content == expected
        assert len(new_context_factors) == 2
        assert new_context_factors[1]["name"] == "Amazon"

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
        assert new_content == "${mecha_godzilla} threw ${mothra} at ${godzilla}"
        assert context[2] == {"name": "Godzilla", "type": "Entity"}

    def test_mentioned_object_string(self):
        mentioned = name_index.Mentioned(self.overlapping_names_mentioned)
        assert "Mentioned({'Godzilla'" in str(mentioned)
        assert "Mentioned({'Godzilla'" in repr(mentioned)

    def test_unmarked_factor_when_one_was_marked(self):
        fact = {
            "type": "fact",
            "content": "$Hamlet lived at Elsinore",
            "context_factors": [{"type": "Entity", "name": "Hamlet"}],
        }
        schema = schemas.FactSchema()
        schema.context["mentioned"] = name_index.Mentioned(
            {"Elsinore": {"type": "Entity"}}
        )
        loaded = schema.load(fact)
        assert loaded.predicate.content == "$Hamlet lived at ${elsinore}"
