from authorityspoke.io import dump, loaders, name_index, readers
from authorityspoke.jurisdictions import Regime
from authorityspoke.evidence import Exhibit
from authorityspoke.rules import Rule


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

    def test_loading_code(self):
        beard_code = loaders.load_and_read_code("beard_tax_act.xml")
        assert beard_code.jurisdiction == "au"

    def test_loading_rules(self, make_regime):
        beard_rules, mentioned = loaders.load_rules_with_index(
            "beard_rules.json", regime=make_regime
        )
        assert beard_rules[0].outputs[0].content == "{} was a beard"

    def test_imported_rule_is_type_rule(self, make_regime):
        beard_rules, mentioned = loaders.load_rules_with_index(
            "beard_rules.json", regime=make_regime
        )
        assert isinstance(beard_rules[0], Rule)

    def test_rule_short_string(self, make_regime):
        beard_rules, mentioned = loaders.load_rules_with_index(
            "beard_rules.json", regime=make_regime
        )
        assert beard_rules[0].short_string.lower().startswith("the rule")

    def test_index_names_from_sibling_inputs(self, make_regime):
        raw_rules = loaders.load_holdings("beard_rules.json")
        indexed_rules, mentioned = name_index.index_names(raw_rules[0]["inputs"])
        key = "the suspected beard occurred on or below the chin"
        assert mentioned[key]["context_factors"][0] == "the suspected beard"

    def test_rule_with_exhibit_as_context_factor(self, make_regime):
        rules, mentioned = loaders.load_rules_with_index(
            "beard_rules.json", regime=make_regime
        )
        exhibit = rules[4].inputs[0].context_factors[2]
        assert isinstance(exhibit, Exhibit)

    def test_load_rules_and_index_names(self, make_regime):
        rules, mentioned = loaders.load_rules_with_index(
            "beard_rules.json", regime=make_regime
        )
        key = "the Department of Beards granted the defendant's beard exemption"
        assert mentioned[key]["context_factors"][0] == "the Department of Beards"

    def test_read_rules_without_regime(self, make_code):
        beard_dictionary = loaders.load_holdings("beard_rules.json")
        beard_code = make_code["beard_act"]
        beard_rules = readers.read_rules(beard_dictionary, beard_code)
        assert beard_rules[0].inputs[0].short_string == (
            "the fact that <the suspected beard> was facial hair"
        )
