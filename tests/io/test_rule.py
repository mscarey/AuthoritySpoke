from authorityspoke.io import dump, readers, schemas


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
