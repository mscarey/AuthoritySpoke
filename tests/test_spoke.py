from copy import copy
import datetime
import json
from typing import Dict

from pint import UnitRegistry
import pytest

from enactments import Code, Enactment
from entities import Entity, Human
from rules import Procedure, Rule, ProceduralRule
from opinions import Opinion
from spoke import Predicate, Factor, Fact, Evidence
from spoke import ureg, Q_
from spoke import check_entity_consistency  # move this back into a class?
from spoke import find_matches, evolve_match_list


class TestEntities:
    def test_equality_generic_entities(self, make_entity):
        e = make_entity
        assert e["e_motel"] == e["e_trees"]
        assert e["e_motel"] is not e["e_trees"]

    def test_conversion_to_generic(self, make_entity):
        e = make_entity
        assert e["e_motel_specific"].make_generic() == e["e_motel"]

    def test_same_object_after_make_generic(self, make_entity):
        e = make_entity
        motel = e["e_motel"]
        motel_b = motel.make_generic()
        assert motel is motel_b

    def test_specific_to_generic_different_object(self, make_entity):
        e = make_entity
        motel = e["e_motel_specific"]
        motel_b = motel.make_generic()
        assert not motel is motel_b

    def test_implication_generic_entities(self, make_entity):
        e = make_entity
        assert e["e_motel_specific"] > e["e_trees"]
        assert not e["e_motel_specific"] < e["e_trees"]

    def test_implication_same_except_generic(self, make_entity):
        e = make_entity
        assert e["e_motel_specific"] > e["e_motel"]
        assert not e["e_motel_specific"] < e["e_motel"]


class TestPredicates:
    def test_predicate_with_wrong_number_of_entities(self):
        with pytest.raises(ValueError):
            _ = Predicate("{} was a motel", reciprocal=True)

    def test_predicate_with_wrong_comparison_symbol(self):
        with pytest.raises(ValueError):
            _ = (
                Predicate(
                    "the height of {} was {}",
                    comparison=">>",
                    quantity=Q_("160 centimeters"),
                ),
            )

    def test_convert_false_statement_about_quantity_to_obverse(self, make_predicate):
        assert make_predicate["p7_obverse"].truth is True
        assert make_predicate["p7_obverse"].quantity == ureg.Quantity(35, "foot")
        assert make_predicate["p7"].truth is True
        assert make_predicate["p7"].comparison == "<="
        assert make_predicate["p7_obverse"].comparison == "<="

    def test_quantity_type(self, make_predicate):
        assert isinstance(make_predicate["p7"].quantity, ureg.Quantity)

    def test_quantity_string(self, make_predicate):
        assert str(make_predicate["p7"].quantity) == "35 foot"

    def test_predicate_content_comparison(self, make_predicate):
        assert make_predicate["p8_exact"].content == make_predicate["p7"].content

    def test_predicate_equality(self, make_predicate):
        assert make_predicate["p1"] == make_predicate["p1_again"]

    def test_predicate_inequality(self, make_predicate):
        assert make_predicate["p2"] != make_predicate["p2_reciprocal"]

    def test_quantity_comparison(self, make_predicate):
        assert make_predicate["p7"].quantity_comparison() == "no more than 35 foot"
        assert make_predicate["p9"].quantity_comparison() == "no more than 5 foot"
        assert make_predicate["p1"].quantity_comparison() is None

    def test_entity_orders(self, make_predicate):
        assert make_predicate["p7"].entity_orders == {(0, 1), (1, 0)}

    def test_obverse_predicates_equal(self, make_predicate):
        assert make_predicate["p7"] == make_predicate["p7_obverse"]

    def test_greater_than_because_of_quantity(self, make_predicate):
        assert make_predicate["p8_meters"] > make_predicate["p8"]
        assert make_predicate["p8_meters"] != make_predicate["p8"]

    def test_equal_float_and_int(self, make_predicate):
        assert make_predicate["p8_int"] == make_predicate["p8_float"]

    def test_greater_float_and_int(self, make_predicate):
        assert make_predicate["p8_higher_int"] > make_predicate["p8_float"]
        assert make_predicate["p8_int"] < make_predicate["p8_higher_int"]

    def test_str_for_predicate_with_number_quantity(self, make_predicate):
        assert (
            str(make_predicate["p8_int"])
            == "The distance between {} and {} was at least 20"
        )
        assert (
            str(make_predicate["p8_float"])
            == "The distance between {} and {} was at least 20.0"
        )
        assert (
            str(make_predicate["p8"])
            == "The distance between {} and {} was at least 20 foot"
        )

    def test_predicate_contradictions(self, make_predicate):
        assert make_predicate["p7"].contradicts(make_predicate["p7_true"])
        assert not make_predicate["p1"].contradicts(make_predicate["p1_again"])
        assert not make_predicate["p3"].contradicts(make_predicate["p7"])

    def test_predicate_does_not_contradict_factor(self, make_predicate, watt_factor):
        assert not make_predicate["p7_true"].contradicts(watt_factor["f7"])

    def test_no_implication_with_inconsistent_dimensionality(self, make_predicate):
        assert not make_predicate["p9"] >= make_predicate["p9_acres"]
        assert not make_predicate["p9"] <= make_predicate["p9_acres"]

    def test_implication_with_no_truth_value(self, make_predicate):
        assert not make_predicate["p2_no_truth"] > make_predicate["p2"]
        assert make_predicate["p2"] > make_predicate["p2_no_truth"]

    def test_no_contradiction_with_no_truth_value(self, make_predicate):
        assert not make_predicate["p2_no_truth"].contradicts(make_predicate["p2"])
        assert not make_predicate["p2"].contradicts(make_predicate["p2_no_truth"])

    def test_no_contradiction_with_inconsistent_dimensionality(self, make_predicate):
        assert not make_predicate["p9"].contradicts(make_predicate["p9_acres"])
        assert not make_predicate["p9_acres"].contradicts(make_predicate["p9"])

    def test_no_equality_with_inconsistent_dimensionality(self, make_predicate):
        assert make_predicate["p9"] != make_predicate["p9_acres"]

    def test_negated_method(self, make_predicate):
        assert make_predicate["p7"].negated() == make_predicate["p7_opposite"]
        assert make_predicate["p3"].negated() == make_predicate["p3_false"]


class TestProcedures:
    def test_exception_for_wrong_type_for_procedure(self, make_predicate):
        with pytest.raises(TypeError):
            x = Procedure(inputs=make_predicate["p1"], outputs=make_predicate["p2"])

    def test_exception_for_wrong_type_in_tuple_for_procedure(self, make_predicate):
        with pytest.raises(TypeError):
            x = Procedure(inputs=(make_predicate["p1"]), outputs=(make_predicate["p2"]))

    def test_get_context_factors(self, make_procedure):
        len(make_procedure["c1"].get_context_factors()) == 2
        len(make_procedure["c2"].get_context_factors()) == 3

    def test_procedure_length(self, make_procedure):
        """Consider deleting Procedure.__len__() and this test."""
        assert len(make_procedure["c2"]) == 2
        assert len(make_procedure["c1"]) == 2

    # Equality

    def test_procedure_equality(self, make_procedure):
        assert make_procedure["c1"] == make_procedure["c1_again"]

    def test_procedure_equality_entity_order(self, make_procedure):
        assert make_procedure["c1"] == make_procedure["c1_entity_order"]

    def test_still_equal_after_swapping_reciprocal_entities(self, make_procedure):
        assert make_procedure["c2"] == make_procedure["c2_reciprocal_swap"]

    def test_foreign_match_list(self, make_procedure, watt_mentioned):
        w = watt_mentioned
        assert make_procedure["c2_irrelevant_inputs"].get_foreign_match_list(
            [{w[2]: w[1], w[3]: w[0]}, {w[1]: w[1], w[2]: w[3]}]
        ) == [{w[1]: w[2], w[0]: w[3]}, {w[1]: w[1], w[3]: w[2]}]

    def test_unequal_after_swapping_nonreciprocal_entities(self, make_procedure):
        assert make_procedure["c2"] != make_procedure["c2_nonreciprocal_swap"]

    def test_sorted_factors_from_procedure(self, watt_factor, make_procedure):
        """The factors_sorted method sorts them alphabetically by __repr__."""
        f = watt_factor
        assert make_procedure["c2"].factors_sorted() == [
            f["f9"],
            f["f7"],
            f["f8"],
            f["f5"],
            f["f6"],
            f["f4"],
            f["f10"],
        ]

    def test_procedure_string_with_entities(self, make_procedure):
        assert "Fact: <Craig> performed at <circus>" in str(
            make_procedure["c2_irrelevant_inputs"]
        )
        assert "Fact: <Dan> performed at <circus>" in str(
            make_procedure["c2_irrelevant_inputs"]
        )

    def test_entities_of_inputs_for_identical_procedure(
        self, watt_factor, make_procedure, watt_mentioned
    ):
        f = watt_factor
        c1 = make_procedure["c1"]
        c1_again = make_procedure["c1_again"]
        assert f["f1"] in c1.inputs
        assert f["f1"] in c1_again.inputs
        assert f["f1"].entity_context == (watt_mentioned[0],)
        assert f["f2"] in c1.inputs
        assert f["f2"] in c1_again.inputs
        assert f["f2"].entity_context == (watt_mentioned[1], watt_mentioned[0])

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

    def test_procedure_implication_with_exact_quantity(
        self, watt_factor, make_procedure
    ):
        """This is meant to show that the function finds the "distance is
        exactly 25" factor in c2_exact, and recognizes that factor can imply
        the "distance is more than 20" factor in c2 if they have the same entities.
        """

        f = watt_factor
        c2 = make_procedure["c2"]
        c2_exact_quantity = make_procedure["c2_exact_quantity"]
        assert c2_exact_quantity >= c2

    def test_procedure_general_quantity_does_not_imply_exact(
        self, watt_factor, make_procedure
    ):
        f = watt_factor
        c2 = make_procedure["c2"]
        c2_exact_quantity = make_procedure["c2_exact_quantity"]
        assert not c2_exact_quantity <= c2

    def test_implied_procedure_with_reciprocal_entities(self, make_procedure):
        """
        Because both procedures have a form of "The distance between {} and {} was {}"
        factor and those factors are reciprocal, the entities of one of them in reversed
        order can be used as the entities of the other, and one will still imply the other.
        (But if there had been more than two entities, only the first two would have been
        reversed.)
        """

        c2 = make_procedure["c2"]
        c2_reciprocal_swap = make_procedure["c2_reciprocal_swap"]
        assert c2 == c2_reciprocal_swap
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
        assert make_procedure["c1"] == make_procedure["c1_again"]

    def test_procedure_implies_same_procedure_fewer_inputs(self, make_procedure):

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

    def test_exhaustive_implies_input_same_as_despite_of_other(self, make_procedure):
        """
        Every input of c2_exact_in_despite is equal to or implied by
        some input of c2, and an input of c2 implies the despite of c2_exact_in_despite.
        """
        p = make_procedure
        assert p["c2_exact_in_despite"].implies_all_to_some(p["c2"])

    def test_no_exhaustive_implies_when_input_contradicts_despite(self, make_procedure):
        """
        c2_higher_quantity has the right inputs, but it also has an
        input that contradicts the despite factor of c2_exact_in_despite.
        """
        p = make_procedure
        assert not p["c2"].implies_all_to_some(p["c2_absent_despite"])

    def test_implication_with_more_outputs_than_inputs(self, make_procedure):
        p = make_procedure
        assert p["c2_irrelevant_outputs"].implies_all_to_all(p["c2"])

    def test_no_contradict_between_procedures(self, make_procedure):
        """
        It's not completely clear to me what assumptions are being made about
        the context of a procedure when comparing them with __gt__,
        implies_all_to_some, and exhaustive_contradicts.

        I don't think "contradicts" is meaningful for Procedures, but I could be wrong.
        """
        p = make_procedure
        with pytest.raises(NotImplementedError):
            assert p["c2_higher_quantity"].contradicts(p["c2_exact_in_despite"])

    def test_implication_procedures_with_same_evidence(self, make_procedure):
        c = make_procedure
        assert c["c3_fewer_inputs"].implies_all_to_all(c["c3"])


class TestRules:
    def test_enactment_type_in_str(self, make_holding):
        assert "constitution" in str(make_holding["h1"]).lower()

    def test_enactment_text_in_str(self, make_holding):
        assert "secure in their persons" in str(make_holding["h1"])

    def test_None_not_in_str(self, make_holding):
        assert "None" not in str(make_holding["h2"])

    # Equality

    def test_identical_holdings_equal(self, make_holding):
        assert make_holding["h1"] == make_holding["h1_again"]

    def test_holdings_equivalent_entity_orders_equal(self, make_holding):
        """
        Test that holdings are considered equal if they have the same factors
        and the numbers they use to refer to entities are different but in an
        equivalent order.
        e.g. {"F1": "1,2,1", "F2": "2,0,0"} and {"F2": "1,2,2", "F1": "0,1,0"}
        """
        assert make_holding["h1"] == make_holding["h1_entity_order"]

    def test_holdings_different_entities_unequal(self, make_holding):
        assert make_holding["h1"] != make_holding["h1_easy"]

    def test_holdings_differing_in_entity_order_equal(self, make_holding):
        assert make_holding["h1"] == make_holding["h1_entity_order"]

    # Implication

    def test_holdings_more_inputs_implies_fewer(self, make_holding):
        assert make_holding["h1"] > make_holding["h1_easy"]
        assert make_holding["h2_irrelevant_inputs"] > make_holding["h2"]

    def test_holding_narrower_despite_implies_broader(self, make_holding):
        assert make_holding["h2_exact_in_despite"] > make_holding["h2"]
        assert not make_holding["h2"] > make_holding["h2_exact_in_despite"]

    def test_holdings_more_specific_quantity_implies_less_specific(self, make_holding):
        assert make_holding["h2_exact_quantity"] > make_holding["h2"]

    def test_holdings_less_specific_with_all_implies_more_specific(self, make_holding):
        assert make_holding["h2_ALL"] > make_holding["h2_exact_quantity_ALL"]
        assert not make_holding["h2_exact_quantity_ALL"] > make_holding["h2_ALL"]

    def test_specific_holding_with_all_implies_more_general_with_some(
        self, make_holding
    ):
        assert make_holding["h2_exact_quantity_ALL"] > make_holding["h2"]

    def test_all_to_all_with_reciprocal(self, make_holding):
        """This is supposed to test reciprocal predicates in despite factors
        in the Predicate.find_consistent_factors method.
        The entity order shouldn't matter because it's the mirror image of the
        normal entity order.
        """
        assert make_holding["h2_exact_in_despite_ALL"] > make_holding["h2_ALL"]
        assert (
            make_holding["h2_exact_in_despite_ALL_entity_order"]
            > make_holding["h2_ALL"]
        )

    def test_some_holding_does_not_imply_version_with_more_supporting_factors(
        self, make_holding
    ):
        """A version of h2 with some supporting factors removed does not imply
        h2.

        A SOME holding means that a court has actually applied the procedure in
        some case. If it also implied variations of itself with other supporting
        inputs added, that would mean that every SOME holding would imply every
        possible variation of itself that could be constructed by substituting
        any different set of supporting inputs."""

        assert not make_holding["h_near_means_curtilage_even_if"] >= make_holding["h2"]
        assert make_holding["h_near_means_curtilage_even_if"] <= make_holding["h2"]

    def test_negated_method(self, make_holding):
        assert make_holding["h1"].negated() == make_holding["h1_opposite"]

    def test_undecided_holding_no_implication_more_inputs(self, make_holding):

        """h2 beind undecided doesn't imply that a version of
        h2 with more supporting factors is undecided"""

        assert (
            not make_holding["h2_undecided"]
            >= make_holding["h2_irrelevant_inputs_undecided"]
        )

    def test_undecided_holding_no_implication_fewer_inputs(self, make_holding):

        """h2_irrelevant_inputs being undecided does not imply that h2
        is undecided. If courts SOMEtimes MAY use the procedure in h2,
        it may or may not be decided whether any court has been allowed
        to apply h2_irrelevant_inputs, even though it has all of h2's
        supporting factors and no more undercutting factors.
        """

        assert not (
            make_holding["h2_irrelevant_inputs_undecided"]
            >= make_holding["h2_undecided"]
        )

    def test_no_undecided_holding_implication_with_MUST(self, make_holding):

        """If it's undecided whether courts MUST follow the procedure in h2,
        it still could be decided that they MAY do so"""

        assert not make_holding["h2_MUST_undecided"] >= make_holding["h2_undecided"]

        """If it's undecided whether courts MAY follow the procedure in h2,
        the rule that they MUST do so still could have been decided to be not valid."""

        assert not make_holding["h2_undecided"] >= make_holding["h2_MUST_undecided"]

    def test_no_undecided_holding_implication_with_ALL(self, make_holding):

        """If it's undecided whether courts ALWAYS MAY follow the procedure in h2,
        it still could be decided (in the negative) whether they ALWAYS MAY
        follow a version with fewer supporting inputs."""

        assert not (
            make_holding["h_near_means_curtilage_ALL_undecided"]
            >= make_holding["h2_undecided"]
        )

    def test_undecided_implies_negation_is_undecided(self, make_holding):
        assert make_holding["h2_invalid_undecided"] >= make_holding["h2_undecided"]
        assert make_holding["h2_undecided"] >= make_holding["h2_invalid_undecided"]

    # Contradiction

    def test_holding_contradicts_invalid_version_of_self(self, make_holding):
        assert make_holding["h2"].negated() == make_holding["h2_invalid"]
        assert make_holding["h2"].contradicts(make_holding["h2_invalid"])
        assert make_holding["h2"] >= make_holding["h2_invalid"].negated()

    def test_some_holding_consistent_with_absent_output(self, make_holding):
        assert not make_holding["h2"].contradicts(make_holding["h2_output_absent"])

    def test_some_holding_consistent_with_false_output(self, make_holding):
        assert not make_holding["h2"].contradicts(make_holding["h2_output_false"])

    def test_some_holding_consistent_with_absent_false_output(self, make_holding):
        assert not make_holding["h2"].contradicts(make_holding["h2_output_false"])

    def test_contradicts_if_valid(self, make_holding):
        """
        This helper method should return the same value as "contradicts"
        because both holdings are valid.
        """

        make_holding["h2_ALL"].contradicts_if_valid(
            make_holding["h2_SOME_MUST_output_false"]
        )

    def test_contradicts_if_valid_invalid_holding(self, make_holding):

        """
        In the current design, contradicts calls implies;
        implies calls contradicts_if_valid.
        """

        assert make_holding["h2_invalid"].contradicts(
            make_holding["h2_irrelevant_inputs"]
        ) != make_holding["h2_invalid"].contradicts_if_valid(
            make_holding["h2_irrelevant_inputs"]
        )

    def test_contradicts_if_valid_some_vs_all(self, make_holding):

        """
        This test and the one below show that you can change whether two
        holdings contradict one another by exchanging the SOME/MAY from one
        with the ALL/MUST from the other.

        The assertion here is:
        In SOME cases where the distance between A and B is less than 20 feet
        the court MUST find that
        A is in the curtilage of B

        contradicts

        In ALL cases where the distance between A and B is less than 35 feet
        the court MAY find that
        A is not in the curtilage of B
        """

        assert make_holding["h_nearer_means_curtilage_MUST"].contradicts_if_valid(
            make_holding["h_near_means_no_curtilage_ALL"]
        )

    def test_contradicts_if_valid_some_vs_all_no_contradiction(self, make_holding):

        """
        This test and the one below show that you can change whether two
        holdings contradict one another by exchanging the SOME/MAY from one
        with the ALL/MUST from the other.

        The assertion here is:
        In SOME cases where the distance between A and B is less than 35 feet
        the court MAY find that
        A is not in the curtilage of B

        does not contradict

        In ALL cases where the distance between A and B is less than 20 feet
        the court MUST find that
        A is in the curtilage of B
        """

        assert not make_holding["h_near_means_no_curtilage"].contradicts_if_valid(
            make_holding["h_nearer_means_curtilage_ALL"]
        )

    def test_contradicts_if_valid_all_vs_some(self, make_holding):

        """
        The assertion here is:
        In ALL cases where the distance between A and B is less than 35 feet
        the court MUST find that
        A is not in the curtilage of B

        contradicts

        In SOME cases where the distance between A and B is less than 20 feet
        the court MAY find that
        A is in the curtilage of B
        """

        assert make_holding["h_near_means_no_curtilage_ALL_MUST"].contradicts_if_valid(
            make_holding["h_nearer_means_curtilage"]
        )

    def test_contradicts_if_valid_all_vs_all(self, make_holding):

        """
        The assertion here is:
        In ALL cases where the distance between A and B is less than 35 feet
        the court MUST find that
        A is in the curtilage of B

        contradicts

        In ALL cases where the distance between A and B is more than 20 feet
        the court MAY find that
        A is not in the curtilage of B
        """

        assert make_holding["h_near_means_curtilage_ALL_MUST"].contradicts_if_valid(
            make_holding["h_far_means_no_curtilage"]
        )

    def test_always_may_contradicts_sometimes_must_not(self, make_holding):
        assert make_holding["h2_ALL"].contradicts(
            make_holding["h2_SOME_MUST_output_false"]
        )

    def test_always_may_contradicts_sometimes_must_omit_output(self, make_holding):
        assert make_holding["h2_ALL"].contradicts(
            make_holding["h2_SOME_MUST_output_absent"]
        )

    def test_sometimes_must_contradicts_always_may_not(self, make_holding):
        assert make_holding["h2_MUST"].contradicts(
            make_holding["h2_ALL_MAY_output_false"]
        )

    def test_sometimes_must_contradicts_always_must_not(self, make_holding):
        assert make_holding["h2_MUST"].contradicts(
            make_holding["h2_ALL_MUST_output_false"]
        )

    def test_negation_of_h2_contradicts_holding_that_implies_h2(self, make_holding):
        assert make_holding["h2_invalid"].contradicts(
            make_holding["h2_irrelevant_inputs"]
        )

    def test_holding_that_implies_h2_contradicts_negation_of_h2(self, make_holding):
        """
        Tests whether "contradicts" works reciprocally in this case.
        It should be reciprocal in every case so far, but maybe not for 'decided.'"""

        assert make_holding["h2_ALL"].contradicts(
            make_holding["h2_SOME_MUST_output_false"]
        )

    def test_invalid_holding_contradicts_h2(self, make_holding):

        # You NEVER MAY follow X
        # will contradict
        # You SOMEtimes MAY follow Y
        # if X implies Y

        assert make_holding["h2_invalid"].contradicts(
            make_holding["h2_irrelevant_inputs"]
        )

    def test_invalidity_of_implying_holding_contradicts_implied(self, make_holding):

        # You NEVER MUST follow X
        # will contradict
        # You SOMEtimes MUST follow Y
        # if X implies Y or Y implies X

        assert make_holding["h2_MUST_invalid"].contradicts(
            make_holding["h2_irrelevant_inputs_MUST"]
        )

    def test_contradiction_with_ALL_MUST_and_invalid_SOME_MUST(self, make_holding):

        # You ALWAYS MUST follow X
        # will contradict
        # You NEVER MUST follow Y
        # if X implies Y or Y implies X

        assert make_holding["h2_ALL_MUST"].contradicts(
            make_holding["h2_irrelevant_inputs_MUST_invalid"]
        )

    def test_contradiction_with_ALL_MUST_and_invalid_ALL_MAY(self, make_holding):

        # You ALWAYS MUST follow X
        # will contradict
        # You MAY NOT ALWAYS follow Y
        # if Y implies X

        assert make_holding["h2_ALL_MUST"].contradicts(make_holding["h2_ALL_invalid"])

    def test_contradiction_with_ALL_MUST_and_false_output_ALL_MAY(self, make_holding):

        # You ALWAYS MUST follow X
        # will contradict
        # You MAY NOT ALWAYS follow Y
        # if Y implies X

        assert make_holding["h2_ALL_MUST"].contradicts(
            make_holding["h2_output_false_ALL"]
        )

    def test_undecided_contradicts_holding(self, make_holding):
        """When a lower court issues a holding deciding a legal issue
        and a higher court posits that the issue should be considered
        undecided, the lower court's prior holding is "contradicted"
        in the sense of being rendered ineffective."""

        assert make_holding["h2_undecided"].contradicts(make_holding["h2"])

    def test_undecided_contradicts_decided_invalid_holding(self, make_holding):
        assert make_holding["h2_undecided"].contradicts(make_holding["h2_invalid"])

    def test_no_contradiction_of_undecided_holding(self, make_holding):
        """A court's act of deciding a legal issue doesn't "contradict" another
        court's prior act of positing that the issue was undecided."""

        assert not make_holding["h2"].contradicts(make_holding["h2_undecided"])
        assert not make_holding["h2_invalid"].contradicts(make_holding["h2_undecided"])

    def test_undecided_holding_implied_contradiction(self, make_holding):
        assert make_holding["h2_irrelevant_inputs_undecided"].contradicts(
            make_holding["h2_ALL"]
        )

    def test_undecided_holding_no_implied_contradiction_with_SOME(self, make_holding):
        """Because a SOME holding doesn't imply a version of the same holding
        with added supporting inputs,

        make_holding["h2_irrelevant_inputs_undecided"]
        does not contradict
        make_holding["h2"]

        which seems questionable."""

        assert not make_holding["h2_irrelevant_inputs_undecided"].contradicts(
            make_holding["h2"]
        )

    def test_undecided_holding_no_implied_contradiction(self, make_holding):

        assert not make_holding["h2_irrelevant_inputs_undecided"].contradicts(
            make_holding["h2_ALL_invalid"]
        )

    # Enactments cited in Rules

    def test_single_enactment_converted_to_frozenset(self, make_holding):
        assert isinstance(make_holding["h2"].enactments, frozenset)

    def test_holdings_citing_different_enactment_text_unequal(self, make_holding):
        assert make_holding["h2"] != make_holding["h2_fourth_a_cite"]

    def test_holding_based_on_less_text_implies_more(self, make_holding):
        """The implied holding is based on enactment text that is a superset
        of the implying holding's enactment text."""
        assert make_holding["h2"] > make_holding["h2_fourth_a_cite"]

    def test_holding_with_enactment_cite_does_not_imply_without(self, make_holding):
        """Just because an outcome is required by enactment text doesn't mean
        the court would require it pursuant to its common law power to make laws."""
        assert not make_holding["h2"] >= make_holding["h2_without_cite"]

    def test_implication_common_law_and_constitutional(self, make_holding):
        """When a court asserts a holding as valid without legislative support,
        the court is actually making a broader statement than it would be making
        if it cited legislative support. The holding without legislative support
        doesn't depend for its validity on the enactment remaining in effect without
        being repealed.

        The relative priority of the holdings is a different
        matter. Statutory holdings trump common law holdings, and constitutional
        trumps statutory."""
        assert make_holding["h2"] <= make_holding["h2_without_cite"]

    def test_no_implication_of_holding_with_added_despite_enactment(self, make_holding):
        assert not make_holding["h2"] >= make_holding["h2_despite_due_process"]

    def test_implication_of_holding_with_removed_despite_enactment(self, make_holding):
        assert make_holding["h2_despite_due_process"] >= make_holding["h2"]

    def test_no_contradiction_when_added_enactment_makes_rule_valid(self, make_holding):
        assert not make_holding["h2_ALL_due_process"].contradicts(
            make_holding["h2_ALL_invalid"]
        )
        assert not make_holding["h2_ALL_invalid"].contradicts(
            make_holding["h2_ALL_due_process"]
        )

    def test_contradiction_with_fewer_enactments(self, make_holding):
        """This and the previous enactment contradiction test passed on their own.
        Does there need to be something about enactments in the contradicts method?"""
        assert make_holding["h2_ALL_due_process_invalid"].contradicts(
            make_holding["h2_ALL"]
        )

    def test_implication_with_evidence(self, make_holding):
        assert make_holding["h3"] > make_holding["h3_fewer_inputs"]

    def test_contradiction_with_evidence(self, make_holding):
        assert make_holding["h3_ALL_undecided"].contradicts(
            make_holding["h3_fewer_inputs_ALL"]
        )

    def test_no_contradiction_holding_with_evidence(self, make_holding):
        assert not make_holding["h3_fewer_inputs_ALL_undecided"].contradicts(
            make_holding["h3_ALL"]
        )

    def test_holding_len(self, make_holding):
        assert len(make_holding["h1"]) == 2
        assert len(make_holding["h3"]) == 4


class TestCodes:
    def test_making_code(self, make_code):
        const = make_code["const"]
        assert const.title == "Constitution of the United States"

    def test_get_bill_of_rights_effective_date(self, make_code):
        const = make_code["const"]
        bill_of_rights_date = datetime.date(1791, 12, 15)
        assert const.provision_effective_date("amendment-V") == bill_of_rights_date

    def test_get_14th_A_effective_date(self, make_code):
        const = make_code["const"]
        equal_protection_date = datetime.date(1868, 7, 28)
        assert const.provision_effective_date("amendment-XIV") == equal_protection_date


class TestEnactments:
    def test_make_enactment(self, make_code, make_enactment):
        search_clause = make_enactment["search_clause"]
        assert search_clause.text.endswith("shall not be violated")

    def test_code_title_in_str(self, make_enactment):
        assert "secure in their persons" in str(make_enactment["search_clause"])

    def test_equal_enactment_text(self, make_enactment):
        assert make_enactment["due_process_5"] == make_enactment["due_process_14"]

    def test_unequal_enactment_text(self, make_enactment):
        assert make_enactment["search_clause"] != make_enactment["fourth_a"]

    def test_enactment_subset(self, make_enactment):
        assert make_enactment["search_clause"] < make_enactment["fourth_a"]

    def test_enactment_subset_or_equal(self, make_enactment):
        assert make_enactment["due_process_5"] >= make_enactment["due_process_14"]

    @pytest.mark.xfail
    def test_enactment_as_factor(self, make_enactment):
        """
        Removed. Probably a remnant of an experiment in putting enactments
        under "input" "despite" and "output"
        """
        assert isinstance(make_enactment["due_process_5"], Factor)

    def test_bill_of_rights_effective_date(self, make_enactment):
        # December 15, 1791
        assert make_enactment["search_clause"].effective_date == datetime.date(
            1791, 12, 15
        )

    def test_14th_A_effective_date(self, make_enactment):
        # July 28, 1868
        assert make_enactment["due_process_14"].effective_date == datetime.date(
            1868, 7, 28
        )

    def test_compare_effective_dates(self, make_enactment):
        dp5 = make_enactment["due_process_5"]
        dp14 = make_enactment["due_process_14"]

        assert dp14.effective_date > dp5.effective_date


class TestOpinions:
    def test_load_opinion_in_Harvard_format(self):
        with open("json/watt_h.json", "r") as f:
            watt_dict = json.load(f)
        assert watt_dict["name_abbreviation"] == "Wattenburg v. United States"

    def test_opinion_features(self, make_opinion):
        assert make_opinion["watt_majority"].court == "9th-cir"
        assert "388 F.2d 853" in make_opinion["watt_majority"].citations

    def test_opinion_holding_list(self, make_opinion, real_holding):
        assert real_holding["h3"] in make_opinion["watt_majority"].holdings

    def test_opinion_entity_list(self, make_opinion, make_entity):
        assert make_entity["e_watt"] in make_opinion["watt_majority"].get_entities()

    def test_opinion_date(self, make_opinion):
        assert (
            make_opinion["watt_majority"].decision_date
            < make_opinion["brad_majority"].decision_date
        )
        assert (
            make_opinion["brad_majority"].decision_date
            == make_opinion[
                "brad_concurring-in-part-and-dissenting-in-part"
            ].decision_date
        )

    def test_opinion_author(self, make_opinion):
        assert make_opinion["watt_majority"].author == "HAMLEY, Circuit Judge"
        assert make_opinion["brad_majority"].author == "BURKE, J."
        assert (
            make_opinion["brad_concurring-in-part-and-dissenting-in-part"].author
            == "TOBRINER, J."
        )
