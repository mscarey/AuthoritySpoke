import os

from dotenv import load_dotenv

from legislice.download import Client

from authorityspoke import Fact
from authorityspoke.io import loaders, readers
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
        factor = mentioned[obj]["terms"][0]
        assert mentioned[factor]["terms"][0] == "Short Name"

    def test_index_names_turns_context_factor_str_into_list(self, raw_factor):
        short_shot_long, mentioned = name_index.index_names(
            raw_factor["relevant"]["terms"][0]
        )
        assert isinstance(mentioned[short_shot_long]["terms"], list)

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
        assert mentioned[factor_name_1]["terms"][0] == "possessive noun"
        factor_name_2 = holding["outputs"][1]
        assert mentioned[factor_name_2]["terms"][0] == "possessive noun"

    def test_update_context_from_bracketed_name(self):
        content = "{} sent a message to {Bob's friend}"
        terms = [{"type": "Entity", "name": "Bob"}]
        new_content, terms = text_expansion.get_references_from_string(content, terms)
        assert new_content == "{} sent a message to ${bob_s_friend}"
        assert len(terms) == 2

    def test_assign_name(self, raw_factor):
        """
        The collect_mentioned function should assign a name to this Fact
        because it doesn't already have one.
        """
        short_shot_long = text_expansion.expand_shorthand(
            raw_factor["relevant"]["terms"][0]
        )
        collapsed, mentioned = name_index.collect_mentioned(short_shot_long)
        assert collapsed == "Short Name shot Longer Name"
        assert mentioned[collapsed]["terms"][0] == "Short Name"

    def test_mentioned_from_fact_and_entities(self, raw_factor):
        obj = text_expansion.expand_shorthand(raw_factor["relevant"])
        obj, mentioned = name_index.collect_mentioned(obj)
        assert mentioned["relevant fact"]["type"] == "Fact"
        shooting = mentioned["relevant fact"]["terms"][0]
        assert mentioned[shooting]["terms"][0] == "Short Name"

    def test_mentioned_ordered_by_length(self, raw_factor):
        obj = text_expansion.expand_shorthand(raw_factor["relevant"])
        obj, mentioned = name_index.index_names(obj)
        shortest = mentioned.popitem()
        assert shortest[0] == "Short Name"

    def test_name_inferred_from_content(self):
        """
        Test that a name field is generated for Factors without them.

        The Factors must be inserted in "mentioned" with the generated name.
        """

        oracle_records = loaders.load_holdings("holding_oracle.yaml")
        for holding in oracle_records:
            holding.pop("enactments", None)
            holding.pop("enactments_despite", None)
        holdings, mentioned = name_index.index_names(oracle_records)
        assert holdings[2]["inputs"][0] == "the Java API was an original work"
        assert (
            mentioned["the Java API was an original work"]["predicate"]["content"]
            == "${the_java_api} was an original work"
        )

    def test_enactment_name_index(self):
        """
        Test error message:
        'Name "securing the right to writings" not found in the index of mentioned Factors'
        """
        feist_records = loaders.load_holdings("holding_feist.yaml")
        record, mentioned = name_index.collect_enactments(feist_records)
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
                "terms": {
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
        built = readers.read_holdings(record=[holding], client=fake_usc_client)
        assert (
            built[0]
            .inputs[0]
            .short_string.startswith(
                "the fact that <Rural's telephone listings> were names"
            )
        )

    def test_enactment_name_in_holding(self, fake_usc_client):
        """
        Test error message:
        'Name "securing for authors" not found in the index of mentioned Factors'
        """
        feist_records = loaders.load_holdings("holding_feist.yaml")
        feist_holdings = readers.read_holdings(
            [feist_records[0]], client=fake_usc_client
        )
        assert "securing for limited Times" in feist_holdings[0].short_string

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
        # Check that terms match the order of the sentence
        assert obj["terms"][0]["name"] == "Bradley"
        assert obj["terms"][1]["name"] == "Bradley's house"

    def test_link_longest_terms_first(self):
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
        assert mentioned[lived_at]["terms"][1] == "Bradley's house"


class TestRetrieveMentioned:
    def test_add_found_context_to_content(self):
        fact = {
            "type": "fact",
            "predicate": {"content": "$moe threw a pie at Larry but it hit $curly"},
            "terms": [
                {"type": "Entity", "name": "Moe"},
                {"type": "Entity", "name": "Curly"},
            ],
        }
        obj = {"type": "Entity", "name": "Larry"}
        (
            fact["predicate"]["content"],
            fact["terms"],
        ) = text_expansion.add_found_context(
            fact["predicate"]["content"], fact["terms"], obj
        )
        assert (
            fact["predicate"]["content"]
            == "$moe threw a pie at ${larry} but it hit $curly"
        )
        assert fact["terms"][1]["name"] == "Larry"

    def test_add_found_context_included_in_placeholder_name(self):
        content = (
            "$the_Amazon has slower Amazon deliveries because of ${the_Amazon}'s size"
        )
        terms = [{"type": "Entity", "name": "the Amazon"}]
        new_content, new_terms = text_expansion.add_found_context(
            content=content,
            terms=terms,
            factor={"type": "Entity", "name": "Amazon"},
        )
        expected = "$the_Amazon has slower ${amazon} deliveries because of ${the_Amazon}'s size"
        assert new_content == expected
        assert len(new_terms) == 2
        assert new_terms[1]["name"] == "Amazon"

    def test_retrieve_mentioned_during_load(self):
        """
        Test that the schema can recreate the Entity objects "Alice" and
        "Bob" from just their name strings, by having added them to
        "mentioned" when they first appeared.
        """
        relevant_dict = {
            "predicate": {"content": "{} is relevant to show {}"},
            "type": "Fact",
            "terms": [
                {
                    "predicate": {"content": "{} shot {}"},
                    "terms": [
                        {"name": "Alice", "type": "Entity"},
                        {"name": "Bob", "type": "Entity"},
                    ],
                    "type": "Fact",
                },
                {
                    "predicate": {"content": "{} murdered {}"},
                    "terms": ["Alice", "Bob"],
                    "type": "Fact",
                },
            ],
        }
        record = readers.expand_shorthand(relevant_dict)
        record, mentioned = readers.index_names(record)
        expanded = readers.expand_factor(record, mentioned)

        relevant_fact = Fact(**expanded)
        assert relevant_fact.terms[1].terms[1].name == "Bob"

    overlapping_names_mentioned = {
        "Godzilla": {"type": "Entity"},
        "Mothra": {"type": "Entity"},
        "Mecha Godzilla": {"type": "Entity"},
    }

    def test_retrieve_references_with_substring(self):
        """
        The Mentioned object must be sorted longest to shortest.
        """

        record = [
            {
                "outputs": [
                    {
                        "type": "fact",
                        "predicate": {
                            "content": "{Mecha Godzilla} threw {Mothra} at {Godzilla}"
                        },
                    }
                ]
            }
        ]

        obj, mentioned = name_index.collect_mentioned(record)
        sorted_mentioned = mentioned.sorted_by_length()

        assert obj[0]["outputs"][0] == "Mecha Godzilla threw Mothra at Godzilla"
        assert list(sorted_mentioned.items())[2] == ("Godzilla", {"type": "Entity"})
