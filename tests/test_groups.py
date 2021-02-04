from authorityspoke.statements.comparable import ContextRegister, means
from authorityspoke.statements.entities import Entity
from authorityspoke.statements.groups import ComparableGroup
from authorityspoke.statements.predicates import Predicate, Comparison
from authorityspoke.statements.statements import Statement
from authorityspoke.holdings import HoldingGroup


class TestMakeGroup:
    def test_group_from_list(self, watt_factor):
        factor_list = [watt_factor["f1"], watt_factor["f2"]]
        group = ComparableGroup(factor_list)
        assert isinstance(group, ComparableGroup)
        assert group[1] == watt_factor["f2"]

    def test_group_from_item(self, watt_factor):
        factor = watt_factor["f1"]
        group = ComparableGroup(factor)
        assert isinstance(group, ComparableGroup)
        assert group[0] == watt_factor["f1"]

    def test_make_empty_group(self):
        group = ComparableGroup()
        assert isinstance(group, ComparableGroup)
        assert len(group) == 0

    def test_factorgroup_from_factorgroup(self, watt_factor):
        factor_list = [watt_factor["f1"], watt_factor["f2"]]
        group = ComparableGroup(factor_list)
        identical_group = ComparableGroup(group)
        assert isinstance(identical_group, ComparableGroup)
        assert identical_group[0] == watt_factor["f1"]

    def test_one_factor_implies_and_has_same_context_as_other(self, watt_factor):
        assert watt_factor["f8_meters"].implies_same_context(watt_factor["f8"])

    def test_drop_implied_factors(self, watt_factor):
        group = ComparableGroup([watt_factor["f8_meters"], watt_factor["f8"]])
        shorter = group.drop_implied_factors()
        assert len(shorter) == 1
        assert watt_factor["f8_meters"] in group

    def test_drop_implied_factors_unmatched_context(self, watt_factor):
        group = ComparableGroup(
            [watt_factor["f9_swap_entities"], watt_factor["f9_miles"]]
        )
        shorter = group.drop_implied_factors()
        assert len(shorter) == 2

    def test_make_context_register(self):
        alice = Entity("Alice")
        bob = Entity("Bob")
        craig = Entity("Craig")
        dan = Entity("Dan")

        left = ComparableGroup([alice, bob])
        right = ComparableGroup([craig, dan])

        register = ContextRegister()
        register.insert_pair(alice, craig)

        gen = left._context_registers(right, comparison=means, context=register)
        answer = next(gen)
        assert answer.get("<Bob>") == dan


class TestSameFactors:
    def test_group_has_same_factors_as_identical_group(self, watt_factor):
        first_group = ComparableGroup([watt_factor["f1"], watt_factor["f3"]])
        second_group = ComparableGroup([watt_factor["f1"], watt_factor["f3"]])
        assert first_group.has_all_factors_of(second_group)

    def test_group_has_same_factors_as_included_group(self, watt_factor):
        first_group = ComparableGroup(
            [watt_factor["f1"], watt_factor["f2"], watt_factor["f3"]]
        )
        second_group = ComparableGroup([watt_factor["f1"], watt_factor["f3"]])
        assert first_group.has_all_factors_of(second_group)

    def test_group_does_not_have_same_factors_as_bigger_group(self, watt_factor):
        first_group = ComparableGroup(
            [watt_factor["f1"], watt_factor["f2"], watt_factor["f3"]]
        )
        second_group = ComparableGroup([watt_factor["f1"], watt_factor["f3"]])
        assert not second_group.has_all_factors_of(first_group)

    def test_group_shares_all_factors_with_bigger_group(self, watt_factor):
        first_group = ComparableGroup(
            [watt_factor["f1"], watt_factor["f2"], watt_factor["f3"]]
        )
        second_group = ComparableGroup([watt_factor["f1"], watt_factor["f3"]])
        assert second_group.shares_all_factors_with(first_group)

    def test_group_does_not_share_all_factors_with_smaller_group(self, watt_factor):
        first_group = ComparableGroup(
            [watt_factor["f1"], watt_factor["f2"], watt_factor["f3"]]
        )
        second_group = ComparableGroup([watt_factor["f1"], watt_factor["f3"]])
        assert not first_group.shares_all_factors_with(second_group)

    def test_group_means_identical_group(self, watt_factor):
        first_group = ComparableGroup([watt_factor["f1"], watt_factor["f3"]])
        second_group = ComparableGroup([watt_factor["f1"], watt_factor["f3"]])
        assert first_group.means(second_group)

    def test_group_does_not_mean_different_group(self, watt_factor):
        first_group = ComparableGroup(
            [watt_factor["f1"], watt_factor["f2"], watt_factor["f3"]]
        )
        second_group = ComparableGroup([watt_factor["f1"], watt_factor["f3"]])
        assert not first_group.means(second_group)
        assert not second_group.means(first_group)

    def test_register_for_matching_entities(self):
        known = ContextRegister()
        alice = Entity("Alice")
        craig = Entity("Craig")
        known.insert_pair(alice, craig)

        gen = alice._context_registers(other=craig, comparison=means, context=known)
        register = next(gen)
        assert register.get("<Alice>") == craig


class TestImplication:
    def test_factorgroup_implies_none(self, watt_factor):
        group = ComparableGroup([watt_factor["f1"], watt_factor["f2"]])
        assert group.implies(None)

    def test_factorgroup_implication_of_empty_group(self, watt_factor):
        factor_list = [watt_factor["f1"], watt_factor["f2"]]
        group = ComparableGroup(factor_list)
        empty_group = ComparableGroup()
        assert group.implies(empty_group)

    def test_explanation_implication_of_factorgroup(self, watt_factor):
        """The returned Explanation shows that f8_meters matches up with f8."""
        left = ComparableGroup(
            [watt_factor["f9_absent_miles"], watt_factor["f8_meters"]]
        )
        right = ComparableGroup([watt_factor["f8"], watt_factor["f9_absent"]])
        explanation = left.explain_implication(right)
        assert "implies" in str(explanation).lower()


class TestAdd:
    def test_add_does_not_consolidate_factors(self, watt_factor):
        left = ComparableGroup(watt_factor["f1"])
        right = ComparableGroup(watt_factor["f1"])
        added = left + right
        assert len(added) == 2
        assert isinstance(added, ComparableGroup)

    def test_add_factor_to_factorgroup(self, watt_factor):
        left = ComparableGroup(watt_factor["f1"])
        right = watt_factor["f1"]
        added = left + right
        assert len(added) == 2
        assert isinstance(added, ComparableGroup)


class TestUnion:
    def test_factors_combined_because_of_implication(self, watt_factor):
        left = ComparableGroup(watt_factor["f8"])
        right = ComparableGroup(watt_factor["f8_meters"])
        added = left | right
        assert len(added) == 1
        assert "meter" in str(added[0])

    def test_union_with_factor_outside_group(self, watt_factor):
        left = ComparableGroup(watt_factor["f8_meters"])
        right = watt_factor["f8"]
        added = left | right
        assert len(added) == 1
        assert "10 meter" in str(added[0])

    def test_no_contradiction_because_entities_vary(self, watt_factor):
        """
        If these Factors were about the same Entity, they would contradict
        and no union would be possible.
        """
        left = ComparableGroup(watt_factor["f3_different_entity"])
        right = ComparableGroup(watt_factor["f3_absent"])
        combined = left | right
        assert len(combined) == 2


class TestConsistent:
    predicate_less_specific = Comparison(
        "${vehicle}'s speed was",
        sign="<",
        expression="30 miles per hour",
    )
    predicate_less_general = Comparison(
        "${vehicle}'s speed was",
        sign="<",
        expression="60 miles per hour",
    )
    predicate_more = Comparison(
        "${vehicle}'s speed was",
        sign=">",
        expression="55 miles per hour",
    )
    predicate_farm = Predicate("$person had a farm")
    slower_specific_statement = Statement(
        predicate_less_specific, terms=Entity("the car")
    )
    slower_general_statement = Statement(
        predicate_less_general, terms=Entity("the pickup")
    )
    faster_statement = Statement(predicate_more, terms=Entity("the pickup"))
    farm_statement = Statement(predicate_farm, terms=Entity("Old MacDonald"))

    def test_group_contradicts_single_factor(self):
        group = ComparableGroup([self.slower_specific_statement, self.farm_statement])
        register = ContextRegister()
        register.insert_pair(Entity("the car"), Entity("the pickup"))
        assert group.contradicts(self.faster_statement, context=register)

    def test_one_statement_does_not_contradict_group(self):
        group = ComparableGroup([self.slower_general_statement, self.farm_statement])
        register = ContextRegister()
        register.insert_pair(Entity("the pickup"), Entity("the pickup"))
        assert not self.faster_statement.contradicts(group, context=register)

    def test_group_inconsistent_with_single_factor(self):
        group = ComparableGroup([self.slower_specific_statement, self.farm_statement])
        register = ContextRegister()
        register.insert_pair(Entity("the car"), Entity("the pickup"))
        assert not group.consistent_with(self.faster_statement, context=register)

    def test_groups_with_one_statement_consistent(self):
        specific_group = ComparableGroup([self.slower_specific_statement])
        general_group = ComparableGroup([self.faster_statement])
        assert specific_group.consistent_with(general_group)

    def test_group_inconsistent_with_one_statement(self):
        group = ComparableGroup([self.slower_specific_statement, self.farm_statement])
        register = ContextRegister()
        register.insert_pair(Entity("the car"), Entity("the pickup"))
        assert not group.consistent_with(self.faster_statement, context=register)

    def test_one_statement_inconsistent_with_group(self):
        group = ComparableGroup([self.slower_specific_statement, self.farm_statement])
        register = ContextRegister()
        register.insert_pair(Entity("the pickup"), Entity("the car"))
        assert not self.faster_statement.consistent_with(group, context=register)

    def test_one_statement_consistent_with_group(self):
        group = ComparableGroup([self.slower_general_statement, self.farm_statement])
        register = ContextRegister()
        register.insert_pair(Entity("the pickup"), Entity("the pickup"))
        assert self.faster_statement.consistent_with(group, context=register)


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
