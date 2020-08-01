import os

from dotenv import load_dotenv
import pytest

from authorityspoke.io import dump, loaders, name_index, readers
from authorityspoke.evidence import Exhibit
from authorityspoke.rules import Rule


from legislice.download import Client

load_dotenv()

TOKEN = os.getenv("LEGISLICE_API_TOKEN")


class TestRuleDump:
    def test_dump_rule(self, make_rule):
        rule = make_rule["h2"]
        dumped = dump.to_dict(rule)
        content = dumped["procedure"]["inputs"][0]["predicate"]["content"]
        assert content == "{} was on the premises of {}"

    def test_dump_and_read_rule(self, make_rule, make_regime):
        rule = make_rule["h2"]
        dumped = dump.to_dict(rule)
        loaded = readers.read_rule(dumped, regime=make_regime)
        content = loaded.despite[0].predicate.content
        assert "the distance between {} and {} was" in content


class TestLoadRules:
    """
    Tests loading Rules, possibly for linking to legislation without
    reference to any Opinion or Holding.
    """

    client = Client(api_token=TOKEN)

    @pytest.mark.vcr
    def test_loading_rules(self):
        beard_rules = loaders.load_rules_with_index(
            "beard_rules.json", client=self.client
        )
        assert beard_rules[0].outputs[0].content == "{} was a beard"

    @pytest.mark.vcr
    def test_imported_rule_is_type_rule(self):
        beard_rules = loaders.load_rules_with_index(
            "beard_rules.json", client=self.client
        )
        assert isinstance(beard_rules[0], Rule)

    @pytest.mark.vcr
    def test_rule_short_string(self):
        beard_rules, mentioned = loaders.load_rules_with_index(
            "beard_rules.json", client=self.client
        )
        assert beard_rules[0].short_string.lower().startswith("the rule")

    def test_index_names_from_sibling_inputs(self):
        raw_rules = loaders.load_holdings("beard_rules.json")
        indexed_rules, mentioned = name_index.index_names(raw_rules[0]["inputs"])
        key = "the suspected beard occurred on or below the chin"
        assert mentioned[key]["context_factors"][0] == "the suspected beard"

    @pytest.mark.vcr
    def test_rule_with_exhibit_as_context_factor(self):
        rules, mentioned = loaders.load_rules_with_index(
            "beard_rules.json", client=self.client
        )
        exhibit = rules[5].inputs[0].context_factors[2]
        assert isinstance(exhibit, Exhibit)

    @pytest.mark.vcr
    def test_load_rules_and_index_names(self):
        rules, mentioned = loaders.load_rules_with_index(
            "beard_rules.json", client=self.client
        )
        key = "the Department of Beards granted the defendant's beard exemption"
        assert mentioned[key]["context_factors"][0] == "the Department of Beards"

    @pytest.mark.vcr
    def test_read_rules_without_regime(self):
        beard_dictionary = loaders.load_holdings("beard_rules.json")
        beard_rules = readers.read_rules(beard_dictionary, client=self.client)
        assert beard_rules[0].inputs[0].short_string == (
            "the fact that <the suspected beard> was facial hair"
        )
