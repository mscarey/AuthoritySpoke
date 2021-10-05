from nettlesome.terms import (
    ContextRegister,
    consistent_with,
    contradicts,
    means,
)

from nettlesome.entities import Entity
from nettlesome.groups import FactorGroup
from nettlesome.predicates import Predicate
from nettlesome.quantities import Comparison
from nettlesome.statements import Statement

from authorityspoke.facts import Fact


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

    def test_one_factor_implies_and_has_same_context_as_other(self, watt_factor):
        assert watt_factor["f8_meters"].implies_same_context(watt_factor["f8"])

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
        assert means(first_group, second_group)

    def test_group_does_not_mean_different_group(self, watt_factor):
        first_group = FactorGroup(
            [watt_factor["f1"], watt_factor["f2"], watt_factor["f3"]]
        )
        second_group = FactorGroup([watt_factor["f1"], watt_factor["f3"]])
        assert not first_group.means(second_group)
        assert not second_group.means(first_group)

    def test_register_for_matching_entities(self):
        known = ContextRegister()
        alice = Entity(name="Alice")
        craig = Entity(name="Craig")
        known.insert_pair(alice, craig)

        gen = alice._context_registers(other=craig, comparison=means, context=known)
        register = next(gen)
        assert register.get("<Alice>") == craig


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


class TestContradiction:
    def test_contradiction_of_group(self):
        lived_at = Predicate(content="$person lived at $residence")
        bob_lived = Fact(
            lived_at, terms=[Entity(name="Bob"), Entity(name="Bob's house")]
        )
        carl_lived = Fact(
            lived_at, terms=[Entity(name="Carl"), Entity(name="Carl's house")]
        )
        distance_long = Comparison(
            content="the distance from the center of $city to $residence was",
            sign=">=",
            expression="50 miles",
        )
        statement_long = Fact(
            distance_long, terms=[Entity(name="Houston"), Entity(name="Bob's house")]
        )
        distance_short = Comparison(
            content="the distance from the center of $city to $residence was",
            sign="<=",
            expression="10 kilometers",
        )
        statement_short = Fact(
            distance_short, terms=[Entity(name="El Paso"), Entity(name="Carl's house")]
        )
        left = FactorGroup([bob_lived, statement_long])
        right = FactorGroup([carl_lived, statement_short])
        explanation = left.explain_contradiction(right)
        assert explanation.context["<Houston>"].name == "El Paso"
        assert contradicts(left, right)


class TestAdd:
    def test_add_does_not_consolidate_factors(self, watt_factor):
        left = FactorGroup(watt_factor["f1"])
        right = FactorGroup(watt_factor["f1"])
        added = left + right
        assert len(added) == 2
        assert isinstance(added, FactorGroup)

    def test_add_factor_to_factorgroup(self, watt_factor):
        left = FactorGroup(watt_factor["f1"])
        right = watt_factor["f1"]
        added = left + right
        assert len(added) == 2
        assert isinstance(added, FactorGroup)


class TestUnion:
    def test_factors_combined_because_of_implication(self, watt_factor):
        left = FactorGroup(watt_factor["f8"])
        right = FactorGroup(watt_factor["f8_meters"])
        added = left | right
        assert len(added) == 1
        assert "meter" in str(added[0])

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


class TestConsistent:
    predicate_less_specific = Comparison(
        content="${vehicle}'s speed was",
        sign="<",
        expression="30 miles per hour",
    )
    predicate_less_general = Comparison(
        content="${vehicle}'s speed was",
        sign="<",
        expression="60 miles per hour",
    )
    predicate_more = Comparison(
        content="${vehicle}'s speed was",
        sign=">",
        expression="55 miles per hour",
    )
    predicate_farm = Predicate(content="$person had a farm")
    slower_specific_statement = Fact(
        predicate=predicate_less_specific, terms=Entity(name="the car")
    )
    slower_general_statement = Fact(
        predicate=predicate_less_general, terms=Entity(name="the pickup")
    )
    faster_statement = Fact(predicate=predicate_more, terms=Entity(name="the pickup"))
    farm_statement = Fact(predicate=predicate_farm, terms=Entity(name="Old MacDonald"))

    def test_group_contradicts_single_factor(self):
        group = FactorGroup([self.slower_specific_statement, self.farm_statement])
        register = ContextRegister()
        register.insert_pair(Entity(name="the car"), Entity(name="the pickup"))
        assert group.contradicts(self.faster_statement, context=register)

    def test_one_statement_does_not_contradict_group(self):
        group = FactorGroup([self.slower_general_statement, self.farm_statement])
        register = ContextRegister()
        register.insert_pair(Entity(name="the pickup"), Entity(name="the pickup"))
        assert not self.faster_statement.contradicts(group, context=register)

    def test_group_inconsistent_with_single_factor(self):
        group = FactorGroup([self.slower_specific_statement, self.farm_statement])
        register = ContextRegister()
        register.insert_pair(Entity(name="the car"), Entity(name="the pickup"))
        assert not group.consistent_with(self.faster_statement, context=register)
        assert not consistent_with(group, self.faster_statement, context=register)

    def test_groups_with_one_statement_consistent(self):
        specific_group = FactorGroup([self.slower_specific_statement])
        general_group = FactorGroup([self.faster_statement])
        assert specific_group.consistent_with(general_group)
        assert consistent_with(specific_group, general_group)
        assert repr(specific_group).startswith("FactorGroup([")

    def test_group_inconsistent_with_one_statement(self):
        group = FactorGroup([self.slower_specific_statement, self.farm_statement])
        register = ContextRegister()
        register.insert_pair(Entity(name="the car"), Entity(name="the pickup"))
        assert not group.consistent_with(self.faster_statement, context=register)

    def test_one_statement_inconsistent_with_group(self):
        group = FactorGroup([self.slower_specific_statement, self.farm_statement])
        register = ContextRegister()
        register.insert_pair(Entity(name="the pickup"), Entity(name="the car"))
        assert not self.faster_statement.consistent_with(group, context=register)

    def test_one_statement_consistent_with_group(self):
        group = FactorGroup([self.slower_general_statement, self.farm_statement])
        register = ContextRegister()
        register.insert_pair(Entity(name="the pickup"), Entity(name="the pickup"))
        assert self.faster_statement.consistent_with(group, context=register)

    def test_no_contradiction_of_none(self):
        group = FactorGroup([self.slower_general_statement, self.farm_statement])
        assert not group.contradicts(None)

    def test_consistent_with_none(self):
        group = FactorGroup([self.slower_general_statement, self.farm_statement])
        assert group.consistent_with(None)
