from authorityspoke.groups import ComparableGroup, FactorGroup
from authorityspoke.holdings import HoldingGroup


class TestMakeGroup:
    def test_group_from_list(self, watt_factor):
        factor_list = [watt_factor["f1"], watt_factor["f2"]]
        group = FactorGroup(factor_list)
        assert isinstance(group, ComparableGroup)
        assert group[1] == watt_factor["f2"]

    def test_group_from_item(self, watt_factor):
        factor = watt_factor["f1"]
        group = FactorGroup(factor)
        assert isinstance(group, ComparableGroup)
        assert group[0] == watt_factor["f1"]

    def test_make_empty_group(self):
        group = FactorGroup()
        assert isinstance(group, ComparableGroup)
        assert len(group) == 0

    def test_factorgroup_from_factorgroup(self, watt_factor):
        factor_list = [watt_factor["f1"], watt_factor["f2"]]
        group = FactorGroup(factor_list)
        identical_group = FactorGroup(group)
        assert isinstance(identical_group, ComparableGroup)
        assert identical_group[0] == watt_factor["f1"]

    def test_drop_implied_factors(self, watt_factor):
        group = FactorGroup([watt_factor["f8_meters"], watt_factor["f8"]])
        shorter = group.drop_implied_factors()
        assert len(shorter) == 1
        assert watt_factor["f8_meters"] in group

    def test_drop_implied_factors_unmatched_context(self, watt_factor):
        group = FactorGroup([watt_factor["f9_swap_entities"], watt_factor["f9_miles"]])
        shorter = group.drop_implied_factors()
        assert len(shorter) == 2


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
    def test_factorgroup_implies_none(self, watt_factor):
        group = FactorGroup([watt_factor["f1"], watt_factor["f2"]])
        assert group.implies(None)

    def test_factorgroup_implication_of_empty_group(self, watt_factor):
        factor_list = [watt_factor["f1"], watt_factor["f2"]]
        group = FactorGroup(factor_list)
        empty_group = FactorGroup()
        assert group.implies(empty_group)

    def test_explanation_implication_of_factorgroup(self, watt_factor):
        """The returned Explanation shows that f8_meters matches up with f8."""
        left = FactorGroup([watt_factor["f9_absent_miles"], watt_factor["f8_meters"]])
        right = FactorGroup([watt_factor["f8"], watt_factor["f9_absent"]])
        explanation = left.explain_implication(right)
        assert "implies" in str(explanation).lower()


class TestAdd:
    def test_add_does_not_consolidate_factors(self, watt_factor):
        left = FactorGroup(watt_factor["f1"])
        right = FactorGroup(watt_factor["f1"])
        added = left + right
        assert len(added) == 2
        assert isinstance(added, ComparableGroup)

    def test_add_factor_to_factorgroup(self, watt_factor):
        left = FactorGroup(watt_factor["f1"])
        right = watt_factor["f1"]
        added = left + right
        assert len(added) == 2
        assert isinstance(added, ComparableGroup)


class TestUnion:
    def test_factors_combined_because_of_implication(self, watt_factor):
        left = FactorGroup(watt_factor["f8"])
        right = FactorGroup(watt_factor["f8_meters"])
        added = left | right
        assert len(added) == 1
        assert "meter" in str(added)

    def test_union_with_factor_outside_group(self, watt_factor):
        left = FactorGroup(watt_factor["f8_meters"])
        right = watt_factor["f8"]
        added = left | right
        assert len(added) == 1
        assert "10 meter" in str(added[0])

    def test_no_contradiction_because_entities_vary(self, watt_factor):
        """
        If these Factors were about the same Entity, they would contradict
        and no union would be possible.
        """
        left = FactorGroup(watt_factor["f3_different_entity"])
        right = FactorGroup(watt_factor["f3_absent"])
        combined = left | right
        assert len(combined) == 2


class TestHoldingImplication:
    def test_explain_holdinggroup_implication(self, make_holding):
        left = HoldingGroup([make_holding["h1"], make_holding["h2_ALL"]])
        right = HoldingGroup([make_holding["h2"]])
        explanation = left.explain_implication(right)
        assert "implies" in str(explanation).lower()
