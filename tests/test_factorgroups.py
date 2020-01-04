import operator

from authorityspoke.factors import FactorGroup, Analogy


class TestMakeGroup:
    def test_group_from_list(self, watt_factor):
        factor_list = [watt_factor["f1"], watt_factor["f2"]]
        group = FactorGroup(factor_list)
        assert isinstance(group, FactorGroup)
        assert group[1] == watt_factor["f2"]

    def test_group_from_item(self, watt_factor):
        factor = watt_factor["f1"]
        group = FactorGroup(factor)
        assert isinstance(group, FactorGroup)
        assert group[0] == watt_factor["f1"]

    def test_make_empty_group(self):
        group = FactorGroup()
        assert isinstance(group, FactorGroup)
        assert len(group) == 0

    def test_factorgroup_from_factorgroup(self, watt_factor):
        factor_list = [watt_factor["f1"], watt_factor["f2"]]
        group = FactorGroup(factor_list)
        identical_group = FactorGroup(group)
        assert isinstance(identical_group, FactorGroup)
        assert identical_group[0] == watt_factor["f1"]


class TestImplication:
    def test_factorgroup_implication_of_empty_group(self, watt_factor):
        factor_list = [watt_factor["f1"], watt_factor["f2"]]
        group = FactorGroup(factor_list)
        empty_group = FactorGroup()
        assert group.implies(empty_group)
