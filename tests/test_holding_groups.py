import pytest

from authorityspoke.holdings import HoldingGroup


class TestMakeHoldingGroup:
    def test_all_members_must_be_holdings(self, make_rule):
        with pytest.raises(TypeError):
            HoldingGroup([make_rule["h1"]])


class TestHoldingGroupImplies:
    def test_explain_holdinggroup_implication(self, make_holding):
        left = HoldingGroup([make_holding["h1"], make_holding["h2_ALL"]])
        right = HoldingGroup([make_holding["h2"]])
        explanation = left.explain_implication(right)
        assert "implies" in str(explanation).lower()

    def test_implication_of_holding(self, make_holding):
        left = HoldingGroup([make_holding["h1"], make_holding["h2_ALL"]])
        right = make_holding["h2"]
        assert left.implies(right)

    def test_implication_of_rule(self, make_holding, make_rule):
        left = HoldingGroup([make_holding["h1"], make_holding["h2_ALL"]])
        right = make_rule["h2"]
        assert left.implies(right)

    def test_implication_of_none(self, make_holding):
        left = HoldingGroup([make_holding["h1"], make_holding["h2_ALL"]])
        right = None
        assert left.implies(right)
