from authorityspoke.io import dump, loaders, readers
from authorityspoke.jurisdictions import Regime


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
        assert beard_rules[0].outputs.content == "{the suspected beard} was a beard"

    def test_index_names(self, make_regime):
        rules, mentioned = loaders.load_rules_with_index(
            "beard_rules.json", regime=make_regime
        )
        key = "the Department of Beards granted the defendant's beard exemption"
        assert mentioned[key]["context_factors"][0] == "the Department of Beards"
