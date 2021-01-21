from copy import deepcopy
import logging
import pytest

from authorityspoke.entities import Entity
from authorityspoke.factors import ContextRegister, FactorSequence
from authorityspoke.groups import FactorGroup
from authorityspoke.procedures import Procedure
from authorityspoke.predicates import Comparison, Predicate, Q_
from authorityspoke.facts import Fact


class TestProcedures:
    def test_exception_for_wrong_type_for_procedure(self, make_predicate):
        with pytest.raises(TypeError):
            Procedure(inputs=make_predicate["p1"], outputs=make_predicate["p2"])

    def test_exception_for_wrong_type_in_tuple_for_procedure(self, make_predicate):
        with pytest.raises(TypeError):
            Procedure(inputs=(make_predicate["p1"]), outputs=(make_predicate["p2"]))

    def test_get_terms(self, make_procedure):
        # motel, watt
        assert len(make_procedure["c1"].generic_factors()) == 2
        # trees, motel
        assert len(make_procedure["c2"].generic_factors()) == 2

    def test_procedure_length(self, make_procedure):
        """Consider deleting Procedure.__len__() and this test."""
        assert len(make_procedure["c2"]) == 2
        assert len(make_procedure["c1"]) == 2

    def test_procedure_string_with_entities(self, make_procedure):
        assert "<Craig> performed at <circus>" in str(
            make_procedure["c2_irrelevant_inputs"]
        )
        assert "<Dan> performed at <circus>" in str(
            make_procedure["c2_irrelevant_inputs"]
        )

    def test_generic_factors(self, make_entity, make_procedure, make_evidence):
        """
        Finds that for factor f["f7"], it would be consistent with the
        other group of factors for f["f7"]'s two slots to be assigned
        (0, 1) or (1, 0).
        """
        e = make_entity
        factors = make_procedure["c3"].generic_factors()
        for factor in (
            e["motel"],
            e["tree_search"],
            e["trees"],
            e["watt"],
            make_evidence["crime_absent"],
        ):
            assert factor in factors

    def test_type_of_terms(self, make_procedure):
        assert isinstance(make_procedure["c3"].terms, FactorSequence)

    def test_entities_of_inputs_for_identical_procedure(
        self, watt_factor, make_procedure, watt_mentioned
    ):
        f = watt_factor
        c1 = make_procedure["c1"]
        c1_again = make_procedure["c1_again"]
        assert f["f1"] in c1.inputs
        assert f["f1"] in c1_again.inputs
        assert f["f1"].terms == (watt_mentioned[0],)
        assert f["f2"] in c1.inputs
        assert f["f2"] in c1_again.inputs
        assert f["f2"].terms == (watt_mentioned[1], watt_mentioned[0])

    def test_wrong_role_for_added_factor(self, watt_factor, make_procedure):
        with pytest.raises(ValueError):
            _ = make_procedure["c1"].add_factor(
                incoming=watt_factor["f8"], role="generic"
            )


class TestProcedureSameMeaning:
    def test_procedure_equality(self, make_procedure, caplog):
        caplog.set_level(logging.DEBUG)
        assert make_procedure["c1"].means(make_procedure["c1_again"])

    def test_procedure_equality_entity_order(self, make_procedure):
        assert make_procedure["c1"].means(make_procedure["c1_entity_order"])

    def test_still_equal_after_swapping_reciprocal_entities(
        self, make_procedure, caplog
    ):
        caplog.set_level(logging.DEBUG)
        assert make_procedure["c2"].means(make_procedure["c2_reciprocal_swap"])

    def test_unequal_after_swapping_nonreciprocal_entities(self, make_procedure):
        assert not make_procedure["c2"].means(make_procedure["c2_nonreciprocal_swap"])

    def test_same_meaning_no_context(self, make_procedure):
        assert make_procedure["c_no_context"].means(make_procedure["c_no_context"])


class TestProcedureImplication:
    def test_entities_of_implied_inputs_for_implied_procedure(
        self, watt_factor, make_procedure
    ):
        f = watt_factor
        c1_easy = make_procedure["c1_easy"]
        c1_order = make_procedure["c1_entity_order"]
        assert f["f2"] in c1_easy.inputs
        assert f["f1"] not in c1_easy.inputs

    def test_factor_implication_with_exact_quantity(self, watt_factor, make_procedure):
        """This test is mostly to demonstrate the relationships
        between the Factors in the Procedures that will be
        tested below."""
        f = watt_factor
        assert f["f7"] in make_procedure["c2"].inputs
        assert f["f7"] not in make_procedure["c2_exact_quantity"].inputs
        assert f["f8_exact"] in make_procedure["c2_exact_quantity"].inputs
        assert f["f8_exact"] > f["f7"]
        assert not f["f7"] >= f["f8_exact"]

    def test_procedure_implication_with_exact_quantity(self, make_procedure):
        """This is meant to show that the function finds the "distance is
        exactly 25" factor in c2_exact, and recognizes that factor can imply
        the "distance is more than 20" factor in c2 if they have the same entities.
        """

        c2 = make_procedure["c2"]
        c2_exact_quantity = make_procedure["c2_exact_quantity"]
        assert c2_exact_quantity.implies(c2)

    def test_procedure_general_quantity_does_not_imply_exact(
        self, watt_factor, make_procedure
    ):

        c2 = make_procedure["c2"]
        c2_exact_quantity = make_procedure["c2_exact_quantity"]
        assert not c2_exact_quantity <= c2

    def test_implied_procedure_with_reciprocal_entities(self, make_procedure):
        """
        Because both procedures have a form of "the distance between $place1 and $place2 was"
        factor and those factors are reciprocal, the entities of one of them in reversed
        order can be used as the entities of the other, and one will still imply the other.
        (But if there had been more than two entities, only the first two would have been
        reversed.)
        """

        c2 = make_procedure["c2"]
        c2_reciprocal_swap = make_procedure["c2_reciprocal_swap"]
        assert c2.means(c2_reciprocal_swap)
        assert c2 >= c2_reciprocal_swap

    def test_entities_of_implied_quantity_outputs_for_implied_procedure(
        self, make_procedure
    ):
        """
        If c2_narrow was "self" and c2_broad was "other", the output of
        c2_broad (with f["f8_int"]) would be implied by the output of
        c2_narrow (with f["f8_higher_int"]).
        """

        c2_broad = make_procedure["c2_broad_output"]
        c2_narrow = make_procedure["c2_narrow_output"]

        assert c2_narrow > c2_broad

    def test_procedure_implies_identical_procedure(self, make_procedure):
        assert make_procedure["c1"] >= make_procedure["c1_again"]
        assert make_procedure["c1"].means(make_procedure["c1_again"])

    def test_procedure_implies_same_procedure_fewer_inputs(
        self, make_procedure, caplog
    ):
        caplog.set_level(logging.DEBUG)
        assert make_procedure["c1_easy"] < make_procedure["c1"]
        assert make_procedure["c1_easy"] <= make_procedure["c1"]
        assert make_procedure["c1_easy"] != make_procedure["c1"]

    def test_procedure_implies_reordered_entities_fewer_inputs(self, make_procedure):

        assert make_procedure["c1_entity_order"] > make_procedure["c1_easy"]
        assert make_procedure["c1_easy"] < make_procedure["c1_entity_order"]
        assert make_procedure["c1_easy"] != make_procedure["c1_entity_order"]

    def test_procedure_exact_quantity_in_despite_implication(self, make_procedure):
        assert make_procedure["c2_exact_in_despite"] > make_procedure["c2"]

    def test_procedure_implication_despite_irrelevant_factors(self, make_procedure):
        assert make_procedure["c2"] < make_procedure["c2_irrelevant_inputs"]

    def test_implies_all_to_some(self, make_procedure):
        assert make_procedure["c2"].implies_all_to_some(
            make_procedure["c2_irrelevant_despite"]
        )
        assert not make_procedure["c2"] > make_procedure["c2_irrelevant_despite"]

    def test_all_to_some_implies_input_same_as_despite_of_other(self, make_procedure):
        """
        Every input of c2_exact_in_despite is equal to or implied by
        some input of c2, and an input of c2 implies the despite of c2_exact_in_despite.
        """
        p = make_procedure
        assert p["c2_exact_in_despite"].implies_all_to_some(p["c2"])

    def test_no_all_to_some_implies_input_contradicts_despite(self, make_procedure):
        """
        c2_higher_quantity has the right inputs, but it also has an
        input that contradicts the despite factor of c2_exact_in_despite.
        """
        p = make_procedure
        assert not p["c2_higher_quantity"].implies_all_to_some(p["c2_exact_in_despite"])

    def test_all_to_some_implication_added_despite_factors(self, make_procedure):

        assert not make_procedure["c2"].implies_all_to_some(
            make_procedure["c2_absent_despite"]
        )

    def test_implication_with_more_outputs_than_inputs(self, make_procedure):
        p = make_procedure
        assert p["c2_irrelevant_outputs"].implies_all_to_all(p["c2"])

    def test_fewer_inputs_implies_all_to_all(self, make_procedure):
        c = make_procedure
        assert c["c3_fewer_inputs"].implies_all_to_all(c["c3"])

    def test_all_to_all_implies_reciprocal(self, make_procedure, caplog):
        """
        These are the same Procedures below in
        test_implication_all_to_all_reciprocal
        """
        caplog.set_level(logging.DEBUG)
        assert make_procedure["c2_exact_in_despite_entity_order"].implies_all_to_all(
            make_procedure["c2"]
        )

    def test_no_implication_of_other_factor(self, make_procedure, watt_factor):
        assert not make_procedure["c1"].implies_all_to_all(watt_factor["f1"])
        assert not make_procedure["c1"].implies_all_to_some(watt_factor["f1"])


class TestProcedureContradiction:
    def test_no_contradict_between_procedures(self, make_procedure):
        """
        I don't think some-to-some contradiction is possible for Procedures
        """
        p = make_procedure
        with pytest.raises(NotImplementedError):
            assert p["c2_higher_quantity"].contradicts(p["c2_exact_in_despite"])

    def test_no_contradiction_of_other_type(self, make_procedure, watt_factor):
        assert not make_procedure["c1"].contradicts_some_to_all(watt_factor["f1"])

    def test_contradiction_some_to_all(self, watt_factor):
        within_curtilage = Procedure(
            inputs=(watt_factor["f9"],),
            outputs=watt_factor["f10"],
        )
        not_within_curtilage = Procedure(
            inputs=(watt_factor["f9"],),
            outputs=watt_factor["f10_false"],
        )
        assert not_within_curtilage.contradicts_some_to_all(within_curtilage)


class TestProcedureUnion:
    def test_simple_union(self, make_opinion_with_holding):
        feist = make_opinion_with_holding["feist_majority"]
        procedure_from_union = feist.holdings[0].procedure | feist.holdings[2].procedure
        procedure_from_adding = (
            feist.holdings[0].procedure + feist.holdings[2].procedure.inputs[0]
        )
        assert procedure_from_union.means(procedure_from_adding)
        assert procedure_from_union.means_same_context(procedure_from_adding)


p_small_weight = Comparison(
    "the amount of gold $person possessed was", sign="<", expression=Q_("1 gram")
)
p_large_weight = Comparison(
    "the amount of gold $person possessed was",
    sign=">=",
    expression=Q_("100 kilograms"),
)
alice = Entity("Alice")
bob = Entity("Bob")
craig = Entity("Craig")
dan = Entity("Dan")
alice_rich = Fact(p_large_weight, terms=alice)
bob_poor = Fact(p_small_weight, terms=bob)
craig_rich = Fact(p_large_weight, terms=craig)
dan_poor = Fact(p_small_weight, terms=dan)


class TestFactorGroups:
    def test_consistent_factor_groups(self):
        """
        Verifies that the factor groups are considered "consistent"
        even though it would be possible to make an analogy that would
        make the statements contradict.
        """
        assert FactorGroup([alice_rich, bob_poor]).consistent_with(
            FactorGroup([dan_poor, craig_rich])
        )

    def test_consistent_factor_groups_with_context(self):
        alice_like_craig = ContextRegister()
        alice_like_craig.insert_pair(alice, craig)
        assert FactorGroup([alice_rich, bob_poor]).consistent_with(
            FactorGroup([dan_poor, craig_rich]),
            context=alice_like_craig,
        )

    def test_not_all_factors_match(self):
        alice_like_craig = ContextRegister()
        alice_like_craig.insert_pair(alice, craig)

        assert alice_rich.all_generic_factors_match(
            craig_rich, context=alice_like_craig
        )

    def test_inconsistent_factor_groups(self):
        """
        If Alice is considered analagous to Dan the two sets of
        statements would be inconsistent, but not if
        Alice is considered analagous to Craig.
        """
        alice_like_dan = ContextRegister()
        alice_like_dan.insert_pair(alice, dan)

        assert not FactorGroup([alice_rich, bob_poor]).consistent_with(
            FactorGroup([dan_poor, craig_rich]), context=alice_like_dan
        )

    def test_contradictory_factor_groups(self):
        """
        Verifies that the factor groups are considered "consistent"
        even though it would be possible to make an analogy that would
        make the statements contradict.

        If Alice is considered analagous to Dan the two sets of
        statements would be contradictory, but not if
        Alice is considered analagous to Craig.
        """
        assert FactorGroup([alice_rich, bob_poor]).contradicts(
            FactorGroup([craig_rich, dan_poor])
        )

    def test_not_contradictory_factor_groups(self):
        """
        Because the ContextRegister matches up the two contexts
        consistently, it's impossible to reach a contradiction.
        """
        alice_like_craig = ContextRegister()
        alice_like_craig.insert_pair(alice, craig)

        assert not FactorGroup((alice_rich, bob_poor)).contradicts(
            FactorGroup((dan_poor, craig_rich)),
            context=alice_like_craig,
        )


class TestEvolve:
    def test_evolve_context_to_absent(self, make_procedure):
        procedure = make_procedure["c1"]
        evolved = deepcopy(procedure)
        evolved.outputs[0].absent = True
        assert procedure.outputs[0].contradicts(evolved.outputs[0])