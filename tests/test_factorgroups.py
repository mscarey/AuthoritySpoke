from authorityspoke.procedures import FactorGroup


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
