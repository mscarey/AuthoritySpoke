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


class TestSameFactors:
    def test_group_has_same_factors_as_identical_group(self, watt_factor):
        first_group = FactorGroup([watt_factor["f1"], watt_factor["f3"]])
        second_group = FactorGroup([watt_factor["f1"], watt_factor["f3"]])
        assert first_group.has_all_factors_of(second_group)

    def test_group_has_same_factors_as_included_group(self, watt_factor):
        first_group = FactorGroup(
            [watt_factor["f1"], watt_factor["f2"], watt_factor["f3"]]
        )
        second_group = FactorGroup([watt_factor["f1"], watt_factor["f3"]])
        assert first_group.has_all_factors_of(second_group)

    def test_group_does_not_have_same_factors_as_bigger_group(self, watt_factor):
        first_group = FactorGroup(
            [watt_factor["f1"], watt_factor["f2"], watt_factor["f3"]]
        )
        second_group = FactorGroup([watt_factor["f1"], watt_factor["f3"]])
        assert not second_group.has_all_factors_of(first_group)

    def test_group_shares_all_factors_with_bigger_group(self, watt_factor):
        first_group = FactorGroup(
            [watt_factor["f1"], watt_factor["f2"], watt_factor["f3"]]
        )
        second_group = FactorGroup([watt_factor["f1"], watt_factor["f3"]])
        assert second_group.shares_all_factors_with(first_group)

    def test_group_does_not_share_all_factors_with_smaller_group(self, watt_factor):
        first_group = FactorGroup(
            [watt_factor["f1"], watt_factor["f2"], watt_factor["f3"]]
        )
        second_group = FactorGroup([watt_factor["f1"], watt_factor["f3"]])
        assert not first_group.shares_all_factors_with(second_group)

    def test_group_means_identical_group(self, watt_factor):
        first_group = FactorGroup([watt_factor["f1"], watt_factor["f3"]])
        second_group = FactorGroup([watt_factor["f1"], watt_factor["f3"]])
        assert first_group.means(second_group)

    def test_group_does_not_mean_different_group(self, watt_factor):
        first_group = FactorGroup(
            [watt_factor["f1"], watt_factor["f2"], watt_factor["f3"]]
        )
        second_group = FactorGroup([watt_factor["f1"], watt_factor["f3"]])
        assert not first_group.means(second_group)
        assert not second_group.means(first_group)


class TestImplication:
    def test_factorgroup_implication_of_empty_group(self, watt_factor):
        factor_list = [watt_factor["f1"], watt_factor["f2"]]
        group = FactorGroup(factor_list)
        empty_group = FactorGroup()
        assert group.implies(empty_group)
