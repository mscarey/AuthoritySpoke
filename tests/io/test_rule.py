import os

from dotenv import load_dotenv
import pytest

from legislice.download import Client

from authorityspoke.io import loaders, name_index, readers
from authorityspoke.facts import Exhibit
from authorityspoke.rules import Rule
from authorityspoke.io.fake_enactments import FakeClient

load_dotenv()

TOKEN = os.getenv("LEGISLICE_API_TOKEN")


class TestRuleDump:
    def test_dump_rule(self, make_rule):
        rule = make_rule["h2"]
        dumped = rule.dict()
        content = dumped["procedure"]["inputs"][0]["predicate"]["content"]
        assert content == "$thing was on the premises of $place"

    def test_dump_and_read_rule(self, make_procedure, e_search_clause):
        rule = Rule(procedure=make_procedure["c2"], enactments=e_search_clause)
        dumped = rule.dict()
        loaded = Rule(**dumped)
        content = loaded.despite[0].predicate.content
        assert "the distance between $place1 and $place2 was" in content


class TestLoadRules:
    """
    Tests loading Rules, possibly for linking to legislation without
    reference to any Opinion or Holding.
    """

    client = Client(api_token=TOKEN)

    def test_loading_rules(self, fake_beard_client):
        beard_rules = loaders.read_holdings_from_file(
            "beard_rules.yaml", client=fake_beard_client
        )
        assert (
            beard_rules[0].outputs[0].predicate.content
            == "${the_suspected_beard} was a beard"
        )

    def test_imported_rule_is_type_rule(self, fake_beard_client):
        beard_rules = loaders.read_holdings_from_file(
            "beard_rules.yaml", client=fake_beard_client
        )
        assert isinstance(beard_rules[0].rule, Rule)

    def test_rule_short_string(self, fake_beard_client):
        beard_rules = loaders.read_holdings_from_file(
            "beard_rules.yaml", client=fake_beard_client
        )
        assert beard_rules[0].rule.short_string.lower().startswith("the rule")

    def test_index_names_from_sibling_inputs(self):
        raw_rules = loaders.load_holdings("beard_rules.yaml")
        indexed_rules, mentioned = name_index.index_names(raw_rules[0]["inputs"])
        key = "the suspected beard occurred on or below the chin"
        assert mentioned[key]["terms"][0] == "the suspected beard"

    def test_rule_with_exhibit_as_context_factor(self, fake_beard_client):
        rules = loaders.read_holdings_from_file(
            "beard_rules.yaml", client=fake_beard_client
        )
        exhibit = rules[5].inputs[0].terms[2]
        assert isinstance(exhibit, Exhibit)

    def test_read_rules_without_regime(self, fake_beard_client):
        beard_rules = loaders.read_holdings_from_file(
            "beard_rules.yaml", client=fake_beard_client
        )
        assert beard_rules[0].inputs[0].short_string == (
            "the fact that <the suspected beard> was facial hair"
        )

    def test_correct_context_after_loading_rules(self, fake_beard_client):
        beard_rules = loaders.read_holdings_from_file(
            "beard_rules.yaml", client=fake_beard_client
        )
        elements_of_offense = beard_rules[11]
        assert len(elements_of_offense.despite) == 1
        assert (
            elements_of_offense.despite[0].generic_terms()[0].name
            == "the Department of Beards"
        )

    def test_load_any_enactments(self, fake_beard_client):
        beard_dictionary = loaders.load_holdings("beard_rules.yaml")
        shorter = [beard_dictionary[0]]
        beard_rules = readers.read_holdings(shorter, client=fake_beard_client)
        assert beard_rules[0].enactments[0].selected_text() == "the beard"

    @pytest.mark.vcr
    def test_generic_terms_after_adding_rules(self, fake_beard_client):
        beard_dictionary = loaders.load_holdings("beard_rules.yaml")
        beard_rules = readers.read_holdings(beard_dictionary, client=fake_beard_client)
        loan_is_transfer = beard_rules[7]
        elements_of_offense = beard_rules[11]
        loan_without_exceptions = (
            loan_is_transfer
            + elements_of_offense.inputs[1]
            + elements_of_offense.inputs[2]
            + elements_of_offense.enactments[1]
        )
        loan_establishes_offense = loan_without_exceptions + elements_of_offense
        assert str(loan_establishes_offense.outputs[0]) == (
            "the fact that <the defendant> committed the offense of improper "
            "transfer of beardcoin"
        )
        assert len(loan_establishes_offense.despite) == 1
        assert (
            loan_establishes_offense.despite[0].generic_terms()[0].name
            == "the Department of Beards"
        )
