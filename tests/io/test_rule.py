import os

from dotenv import load_dotenv
import pytest

from legislice.download import Client

from authorityspoke.io import dump, loaders, name_index, readers
from authorityspoke.evidence import Exhibit
from authorityspoke.rules import Rule
from authorityspoke.io.downloads import FakeClient

load_dotenv()

TOKEN = os.getenv("LEGISLICE_API_TOKEN")


class TestRuleDump:
    def test_dump_rule(self, make_rule):
        rule = make_rule["h2"]
        dumped = dump.to_dict(rule)
        content = dumped["procedure"]["inputs"][0]["predicate"]["content"]
        assert content == "$thing was on the premises of $place"

    def test_dump_and_read_rule(self, make_rule, make_response):
        client = FakeClient(responses=make_response)
        rule = make_rule["h2"]
        dumped = dump.to_dict(rule)
        loaded = readers.read_rule(dumped, client=client)
        content = loaded.despite[0].predicate.content
        assert "the distance between $place1 and $place2 was" in content


class TestLoadRules:
    """
    Tests loading Rules, possibly for linking to legislation without
    reference to any Opinion or Holding.
    """

    client = Client(api_token=TOKEN)

    def test_loading_rules(self, fake_beard_client):
        beard_rules, mentioned = loaders.load_rules_with_index(
            "beard_rules.json", client=fake_beard_client
        )
        assert beard_rules[0].outputs[0].content == "{} was a beard"

    def test_imported_rule_is_type_rule(self, fake_beard_client):
        beard_rules, mentioned = loaders.load_rules_with_index(
            "beard_rules.json", client=fake_beard_client
        )
        assert isinstance(beard_rules[0], Rule)

    def test_rule_short_string(self, fake_beard_client):
        beard_rules, mentioned = loaders.load_rules_with_index(
            "beard_rules.json", client=fake_beard_client
        )
        assert beard_rules[0].short_string.lower().startswith("the rule")

    def test_index_names_from_sibling_inputs(self):
        raw_rules = loaders.load_holdings("beard_rules.json")
        indexed_rules, mentioned = name_index.index_names(raw_rules[0]["inputs"])
        key = "the suspected beard occurred on or below the chin"
        assert mentioned[key]["context_factors"][0] == "the suspected beard"

    def test_rule_with_exhibit_as_context_factor(self, fake_beard_client):
        rules, mentioned = loaders.load_rules_with_index(
            "beard_rules.json", client=fake_beard_client
        )
        exhibit = rules[5].inputs[0].context_factors[2]
        assert isinstance(exhibit, Exhibit)

    def test_load_rules_and_index_names(self, fake_beard_client):
        rules, mentioned = loaders.load_rules_with_index(
            "beard_rules.json", client=fake_beard_client
        )
        key = "the Department of Beards granted the defendant's beard exemption"
        assert mentioned[key]["context_factors"][0] == "the Department of Beards"

    def test_read_rules_without_regime(self, fake_beard_client):
        beard_dictionary = loaders.load_holdings("beard_rules.json")
        beard_rules = readers.read_rules(beard_dictionary, client=fake_beard_client)
        assert beard_rules[0].inputs[0].short_string == (
            "the fact that <the suspected beard> was facial hair"
        )
