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
            f = Predicate("{} was a motel", reciprocal=True)

    def test_predicate_with_wrong_comparison_symbol(self):
        with pytest.raises(ValueError):
            h = (
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
        assert type(make_predicate["p7"].quantity) == ureg.Quantity

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

    def test_predicate_does_not_contradict_factor(self, make_predicate, make_factor):
        assert not make_predicate["p7_true"].contradicts(make_factor["f7"])

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



class TestFacts:
    def test_default_entity_context_for_fact(self, make_predicate):
        f2 = Fact(make_predicate["p2"])
        assert f2.entity_context == (0, 1)

    def test_convert_int_entity_context_to_tuple(self, make_predicate):
        f = Fact(make_predicate["p_irrelevant_1"], 3)
        assert f.entity_context == (3,)

    def test_string_representation_of_factor(self, make_factor):
        assert str(make_factor["f1"]) == "Fact: <0> was a motel"
        assert str(make_factor["f3_absent"]) == "Absent Fact: <0> was <1>’s abode"

    def test_abstract_to_concrete(self, make_factor):
        different = make_factor["f2"].make_concrete([
            Human("He-Man"),
            Entity("Castle Grayskull")])

        assert "He-Man operated" in str(different)

    def test_concrete_to_abstract(self, make_entity, make_predicate):
        motel = make_entity["e_motel"]
        d = make_entity["e_watt"]
        fact = Fact(
            predicate=make_predicate["p2"],
            entity_context=(d, motel)
        )
        assert "Wattenburg operated and lived" in str(fact)
        assert "{} operated and lived" in str(fact.make_generic())

    def test_entity_slots_as_length_of_factor(self, make_factor):
        assert len(make_factor["f1"].predicate) == 1
        assert len(make_factor["f1"]) == 1

    def test_entity_orders(self, make_factor):
        assert make_factor["f7_swap_entities_4"].entity_orders == {(1, 4), (4, 1)}

    def test_predicate_with_entities(self, make_entity, make_factor):
        assert (
            make_factor["f1"].predicate.content_with_entities((make_entity["e_motel"]))
            == "Hideaway Lodge was a motel"
        )

    def test_factor_entity_context_does_not_match_predicate(self, make_predicate):
        with pytest.raises(ValueError):
            x = Fact(make_predicate["p1"], (0, 1, 2))

    def test_reciprocal_with_wrong_number_of_entities(self, make_entity, make_factor):
        with pytest.raises(ValueError):
            make_factor["f1"].predicate.content_with_entities(
                (make_entity["e_motel"], make_entity["e_watt"])
            )

    def test_false_predicate_with_entities(self, make_entity, make_factor):
        assert make_factor["f7"].predicate_in_context(
            (make_entity["e_trees"], make_entity["e_motel"])
        ) == str(
            "Fact: The distance between the stockpile of trees "
            + "and Hideaway Lodge was no more than 35 foot"
        )

    def test_entity_and_human_in_predicate(self, make_entity, make_factor):
        assert (
            make_factor["f2"].predicate.content_with_entities(
                (make_entity["e_watt"], make_entity["e_motel"])
            )
            == "Wattenburg operated and lived at Hideaway Lodge"
        )

    def test_fact_label_with_entities(self, make_entity, make_factor):
        assert (
            make_factor["f2"].predicate_in_context(
                (make_entity["e_watt"], make_entity["e_motel"])
            )
            == "Fact: Wattenburg operated and lived at Hideaway Lodge"
        )

    def test_factor_equality(self, make_factor):
        assert make_factor["f1"] == make_factor["f1b"]
        assert make_factor["f1"] == make_factor["f1c"]
        assert make_factor["f9_swap_entities_4"] == make_factor["f9"]

    def test_generic_factors_equal(self, make_factor):
        assert make_factor["f2_generic"] == make_factor["f2_false_generic"]
        assert make_factor["f2_generic"] == make_factor["f3_generic"]

    def test_generic_and_specific_factors_unequal(self, make_factor):
        assert make_factor["f2"] != make_factor["f2_generic"]

    def test_specific_factor_implies_generic(self, make_factor):
        assert make_factor["f2"] > make_factor["f2_generic"]
        assert make_factor["f2"] > make_factor["f3_generic"]

    def test_specific_fact_does_not_imply_generic_entity(self, make_entity, make_factor):
        assert not make_factor["f2"] > make_entity["e_motel"]

    def test_factor_reciprocal_unequal(self, make_factor):
        assert make_factor["f2"] != make_factor["f2_reciprocal"]

    @pytest.mark.xfail
    def test_unequal_due_to_repeating_entity(self, make_factor):
        """I'm not convinced that a model of a Fact ever needs to include
        multiple references to the same Entity just because the name of the
        Entity appears more than once in the Predicate."""
        f = make_factor
        assert f["f_three_entities"] != f["f_repeating_entity"]

    def test_factor_unequal_predicate_truth(self, make_factor):
        assert make_factor["f7"] != make_factor["f7_true"]
        assert make_factor["f7"].contradicts(make_factor["f7_true"])

    def test_factor_does_not_contradict_predicate(self, make_predicate, make_factor):
        with pytest.raises(TypeError):
            a = make_factor["f7"].contradicts(make_predicate["p7_true"])

    def test_factor_contradiction_absent_predicate(self, make_factor):
        assert make_factor["f3"].contradicts(make_factor["f3_absent"])
        assert make_factor["f3_absent"].contradicts(make_factor["f3"])

    def test_factor_does_not_imply_predicate(self, make_predicate, make_factor):
        with pytest.raises(TypeError):
            assert not make_factor["f8_meters"] > make_predicate["p8"]

    def test_factor_implies_because_of_quantity(self, make_factor):
        assert make_factor["f8_meters"] > make_factor["f8"]
        assert make_factor["f8_higher_int"] > make_factor["f8_float"]
        assert make_factor["f8_int"] < make_factor["f8_higher_int"]

    def test_factor_implies_no_truth_value(self, make_factor):
        assert make_factor["f2"] > make_factor["f2_no_truth"]
        assert not make_factor["f2_no_truth"] > make_factor["f2"]

    def test_factor_implies_because_of_exact_quantity(self, make_factor):
        assert make_factor["f8_exact"] > make_factor["f7"]
        assert make_factor["f8_exact"] >= make_factor["f8"]

    def test_absent_factor_implies_absent_factor_with_greater_quantity(
        self, make_factor
    ):
        assert make_factor["f9_absent"] > make_factor["f9_absent_miles"]

    def test_factor_no_contradiction_no_truth_value(self, make_factor):
        assert not make_factor["f2"].contradicts(make_factor["f2_no_truth"])
        assert not make_factor["f2_no_truth"].contradicts(make_factor["f2_false"])

    def test_absent_factor_contradicts_broader_quantity_statement(self, make_factor):
        assert make_factor["f8_absent"].contradicts(make_factor["f8_meters"])
        assert make_factor["f8_meters"].contradicts(make_factor["f8_absent"])
        assert make_factor["f9_absent_miles"].contradicts(make_factor["f9"])
        assert make_factor["f9"].contradicts(make_factor["f9_absent_miles"])

    def test_copies_of_identical_factor(self, make_factor):
        """
        Even if the two factors have different entity markers in self.entity_context,
        I expect them to evaluate equal because the choice of entity markers is
        arbitrary.
        """
        f = make_factor
        assert f["f_irrelevant_3"] == f["f_irrelevant_3"]
        assert f["f_irrelevant_3"] == f["f_irrelevant_3_new_context"]

    def test_equal_factors_not_gt(self, make_factor):
        f = make_factor
        assert f["f_irrelevant_3"] >= f["f_irrelevant_3_new_context"]
        assert f["f_irrelevant_3"] <= f["f_irrelevant_3_new_context"]
        assert not f["f_irrelevant_3"] > f["f_irrelevant_3_new_context"]

    def test_check_entity_consistency_true(self, make_factor):
        f = make_factor
        assert check_entity_consistency(
            f["f_irrelevant_3"],
            f["f_irrelevant_3_new_context"],
            (None, None, None, 2, None),
        )
        assert check_entity_consistency(
            f["f_irrelevant_3"], f["f_irrelevant_3_new_context"], (1, 0, 3, 2, 4)
        )

    def test_check_entity_consistency_false(self, make_factor):
        f = make_factor
        assert not check_entity_consistency(
            f["f_irrelevant_3"],
            f["f_irrelevant_3_new_context"],
            (None, None, None, None, 0),
        )
        assert not check_entity_consistency(
            f["f_irrelevant_3"],
            f["f_irrelevant_3_new_context"],
            (None, None, None, 3, None),
        )

    def test_check_entity_consistency_type_error(self, make_factor, make_holding):
        f = make_factor
        with pytest.raises(TypeError):
            check_entity_consistency(
                f["f_irrelevant_3"], make_holding["h2"], (None, None, None, None, 0)
            )

    def test_consistent_entity_combinations(self, make_factor):
        """
        Finds that for factor f["f7"], it would be consistent with the
        other group of factors for f["f7"]'s two slots to be assigned
        (0, 1) or (1, 0).
        """

        f = make_factor
        assert f["f7"].consistent_entity_combinations(
            factors_from_other_procedure=[
                f["f4"],
                f["f5"],
                f["f6"],
                f["f7"],
                f["f8"],
                f["f9"],
            ],
            matches=(0, 1, None, None, None),
        ) == [{0: 0, 1: 1}, {0: 1, 1: 0}]

    def test_standard_of_proof_comparison(self, make_factor):

        f = make_factor
        assert f["f2_clear_and_convincing"] >= f["f2_preponderance_of_evidence"]
        assert f["f2_beyond_reasonable_doubt"] >= f["f2_clear_and_convincing"]

    def test_standard_of_proof_inequality(self, make_factor):

        f = make_factor
        assert f["f2_clear_and_convincing"] != f["f2_preponderance_of_evidence"]
        assert f["f2_clear_and_convincing"] != f["f2"]

    def test_no_implication_between_factors_with_and_without_standards(
        self, make_factor
    ):

        f = make_factor
        assert not f["f2_clear_and_convincing"] > f["f2"]
        assert not f["f2"] > f["f2_preponderance_of_evidence"]

    def test_standard_of_proof_must_be_listed(self, make_predicate):
        with pytest.raises(ValueError):
            f = Fact(make_predicate["p2"], standard_of_proof="probably so")

    def test_standard_of_proof_in_str(self, make_factor):
        factor = make_factor["f2_preponderance_of_evidence"]
        assert factor.standard_of_proof in str(factor)


class TestEvidence:
    def test_make_evidence_object(self, make_factor):
        e = Evidence(form="testimony", to_effect=make_factor["f2"])
        assert not e.absent

    def test_default_len_based_on_unique_entity_slots(
        self, make_predicate, make_factor
    ):
        """same as e["e_no_shooting"]"""

        e = Evidence(
            form="testimony",
            to_effect=Fact(Predicate("{} commited a crime", truth=False)),
            statement=Fact(Predicate("{} did not shoot {}")),
            stated_by=0,
        )
        assert len(e) == 2

    def test_get_entity_orders(self, make_evidence):
        # TODO: check this after making Evidence.__str__ method
        assert make_evidence["e_no_shooting"].entity_orders == {(0, 1, 0, 0)}
        assert make_evidence["e_reciprocal"].entity_orders == {
            (0, 1, 0, 2),
            (1, 0, 0, 2),
        }

    def test_get_entity_orders_no_statement(self, make_factor):
        e = Evidence(
            form="testimony", to_effect=make_factor["f_no_crime"], derived_from=1
        )
        assert e.entity_orders == {(0, 1)}

    def test_evidence_str(self, make_evidence):
        assert str(make_evidence["e_reciprocal"]).startswith(
            "Testimony, with a statement by <2>"
        )

    def test_equality_with_entity_order(self, make_predicate, make_evidence):
        e = make_evidence
        assert e["e_no_shooting"] == e["e_no_shooting_entity_order"]

    def test_equality_with_no_statement(self, make_evidence):
        assert make_evidence["e_crime"] == make_evidence["e_crime"]

    def test_unequal_due_to_entity_order(self, make_evidence):
        e = make_evidence
        assert e["e_no_shooting"] != e["e_no_shooting_different_witness"]

    def test_unequal_different_attributes(self, make_evidence):
        assert (
            make_evidence["e_no_shooting_no_effect_entity_order"]
            != make_evidence["e_no_shooting_derived_from_entity_order"]
        )

    def test_implication_missing_witness(self, make_evidence):
        e = make_evidence
        assert e["e_no_shooting"] >= e["e_no_shooting_witness_unknown"]

    def test_implication_missing_effect(self, make_evidence):
        e = make_evidence
        assert e["e_no_shooting"] >= e["e_no_shooting_no_effect_entity_order"]

    def test_no_implication_of_fact(self, make_predicate, make_evidence):
        assert not make_evidence["e_no_shooting"] > Fact(
            make_predicate["p_no_shooting"]
        )
        assert (
            not Fact(make_predicate["p_no_shooting"]) > make_evidence["e_no_shooting"]
        )

    def test_no_contradiction_of_fact(self, make_predicate, make_evidence):
        assert not make_evidence["e_no_shooting"].contradicts(
            Fact(make_predicate["p_no_shooting"])
        )

    def test_no_contradiction_from_supporting_contradictory_facts(self, make_evidence):
        assert not make_evidence["e_no_shooting"].contradicts(
            make_evidence["e_shooting"]
        )

    def test_contradiction_of_absent_version_of_self(self, make_evidence):
        e = make_evidence
        assert e["e_no_shooting"].contradicts(e["e_no_shooting_absent"])

    def test_contradict_absent_version_of_implied_factor(self, make_evidence):
        e = make_evidence
        assert e["e_no_shooting_witness_unknown_absent"].contradicts(e["e_no_shooting"])
        assert e["e_no_shooting"].contradicts(e["e_no_shooting_witness_unknown_absent"])

    def test_no_contradiction_absent_same_witness(self, make_evidence):
        e = make_evidence
        assert not e["e_no_shooting_absent"].contradicts(
            e["e_no_shooting_witness_unknown"]
        )
        assert not e["e_no_shooting_witness_unknown"].contradicts(
            e["e_no_shooting_absent"]
        )
        assert not e["e_no_shooting_absent"].contradicts(
            e["e_no_shooting_different_witness"]
        )

    def test_no_contradiction_of_implied_factor(self, make_evidence):
        e = make_evidence
        assert not e["e_no_shooting"].contradicts(e["e_no_shooting_witness_unknown"])

    def test_implication_procedures_with_same_evidence(self, make_procedure):
        c = make_procedure
        assert c["c3_fewer_inputs"].implies_all_to_all(c["c3"])


class TestProcedures:
    def test_exception_for_wrong_type_for_procedure(self, make_predicate):
        with pytest.raises(TypeError):
            x = Procedure(inputs=make_predicate["p1"], outputs=make_predicate["p2"])

    def test_exception_for_wrong_type_in_tuple_for_procedure(self, make_predicate):
        with pytest.raises(TypeError):
            x = Procedure(inputs=(make_predicate["p1"]), outputs=(make_predicate["p2"]))

    def test_procedure_equality(self, make_procedure):
        assert make_procedure["c1"] == make_procedure["c1_again"]
        assert make_procedure["c1"] == make_procedure["c1_entity_order"]

    def test_still_equal_after_swapping_reciprocal_entities(self, make_procedure):
        assert make_procedure["c2"] == make_procedure["c2_reciprocal_swap"]

    def test_foreign_match_list(self, make_procedure):
        assert make_procedure["c2_irrelevant_inputs"].get_foreign_match_list(
            frozenset([(None, None, 1, 0, None), (None, 1, 3, None, None)])
        ) == frozenset([(3, 2, None, None, None), (None, 1, None, 2, None)])

    def test_unequal_after_swapping_nonreciprocal_entities(self, make_procedure):
        assert make_procedure["c2"] != make_procedure["c2_nonreciprocal_swap"]

    def test_procedure_length(self, make_procedure):
        assert len(make_procedure["c1"]) == 2
        assert len(make_procedure["c2"]) == 2

    def test_sorted_factors_from_procedure(self, make_predicate, make_procedure):

        """The factors_sorted method sorts them alphabetically by __repr__."""

        assert make_procedure["c2"].factors_sorted() == [
            Fact(
                predicate=Predicate(
                    content="The distance between {} and a parking area used by personnel and patrons of {} was {}",
                    truth=True,
                    reciprocal=False,
                    comparison="<=",
                    quantity=ureg.Quantity(5, "foot"),
                ),
                absent=False,
            ),
            Fact(
                predicate=Predicate(
                    content="The distance between {} and {} was {}",
                    truth=False,
                    reciprocal=True,
                    comparison=">",
                    quantity=ureg.Quantity(35, "foot"),
                ),
                absent=False,
            ),
            Fact(
                predicate=Predicate(
                    content="The distance between {} and {} was {}",
                    truth=True,
                    reciprocal=True,
                    comparison=">=",
                    quantity=ureg.Quantity(20, "foot"),
                ),
                absent=False,
            ),
            Fact(
                predicate=Predicate(
                    content="{} was a stockpile of Christmas trees",
                    truth=True,
                    reciprocal=False,
                ),
                absent=False,
            ),
            Fact(
                predicate=Predicate(
                    content="{} was among some standing trees",
                    truth=True,
                    reciprocal=False,
                ),
                absent=False,
            ),
            Fact(
                predicate=Predicate(
                    content="{} was on the premises of {}", truth=True, reciprocal=False
                ),
                absent=False,
            ),
            Fact(
                predicate=Predicate(
                    content="{} was within the curtilage of {}",
                    truth=True,
                    reciprocal=False,
                ),
                absent=False,
            ),
        ]

    def test_procedure_string_with_entities(self, make_procedure):
        assert "Fact: <2> performed at <4>" in str(
            make_procedure["c2_irrelevant_inputs"]
        )
        assert "Fact: <3> performed at <4>" in str(
            make_procedure["c2_irrelevant_inputs"]
        )

    def test_entities_of_inputs_for_identical_procedure(
        self, make_factor, make_procedure
    ):
        f = make_factor
        c1 = make_procedure["c1"]
        c1_again = make_procedure["c1_again"]
        assert f["f1"] in c1.inputs
        assert f["f1"] in c1_again.inputs
        assert f["f1"].entity_context == (0,)
        assert f["f2"] in c1.inputs
        assert f["f2"] in c1_again.inputs
        assert f["f2"].entity_context == (1, 0)

    def test_entities_of_implied_inputs_for_implied_procedure(
        self, make_factor, make_procedure
    ):
        f = make_factor
        c1_easy = make_procedure["c1_easy"]
        c1_order = make_procedure["c1_entity_order"]
        assert any(factor == f["f2"] for factor in c1_easy.inputs)
        assert all(factor != f["f1"] for factor in c1_easy.inputs)

    def test_procedure_implication_with_exact_quantity(
        self, make_factor, make_procedure
    ):
        """This is meant to show that the function finds the "distance is
        exactly 25" factor in c2_exact, and recognizes that factor can imply
        the "distance is more than 20" factor in c2 if they have the same entities.
        """

        f = make_factor
        c2 = make_procedure["c2"]
        c2_exact_quantity = make_procedure["c2_exact_quantity"]

        assert f["f7"] in c2.inputs
        assert f["f7"] not in c2_exact_quantity.inputs
        assert f["f8_exact"] > f["f7"]
        assert c2 <= c2_exact_quantity
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
        assert make_holding["h3_ALL_undecided"].contradicts(make_holding["h3_fewer_inputs_ALL"])

    def test_no_contradiction_holding_with_evidence(self, make_holding):
        assert not make_holding["h3_fewer_inputs_ALL_undecided"].contradicts(make_holding["h3_ALL"])

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
