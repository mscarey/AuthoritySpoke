from copy import copy
import datetime
import json
from typing import Dict

from pint import UnitRegistry
import pytest

from enactments import Code, Enactment
from entities import Entity, Human
from evidence import Evidence, Exhibit
from rules import Procedure, Rule, ProceduralRule
from opinions import Opinion
from spoke import Predicate, Factor, Fact
from spoke import ureg, Q_
from spoke import check_entity_consistency
from spoke import find_matches, evolve_match_list


class TestFacts:
    def test_default_entity_context_for_fact(
        self, make_entity, make_predicate, watt_mentioned
    ):
        e = make_entity
        f2 = Fact.new(make_predicate["p1"], case_factors=watt_mentioned)
        assert f2.entity_context == (e["motel"],)

    def test_entity_context_from_case_factor_indices(
        self, make_entity, make_predicate, watt_mentioned
    ):
        """
        If you pass in integers instead of Factor objects to fill the blanks
        in the Predicate (which was the only way to do things in the first
        version of the Fact class's __init__ method), then the integers
        you pass in should be used as indices to select Factor objects
        from case_factors.
        """

        e = make_entity

        f2 = Fact.new(
            make_predicate["p2"], entity_context=(1, 0), case_factors=watt_mentioned
        )
        assert f2.entity_context == (e["watt"], e["motel"])

    def test_invalid_index_for_case_factors_in_init(self, make_predicate, make_entity):
        with pytest.raises(ValueError):
            _ = Fact.new(
                make_predicate["p1"], entity_context=2, case_factors=make_entity["watt"]
            )

    def test_convert_int_entity_context_to_tuple(self, make_predicate, watt_mentioned):
        f = Fact.new(make_predicate["p_irrelevant_1"], 3, case_factors=watt_mentioned)
        assert f.entity_context == (watt_mentioned[3],)

    def test_string_representation_of_factor(self, watt_factor):
        assert str(watt_factor["f1"]) == "Fact: <Hideaway Lodge> was a motel"
        assert (
            str(watt_factor["f3_absent"])
            == "Absent Fact: <Hideaway Lodge> was <Wattenburg>’s abode"
        )

    def test_string_representation_with_concrete_entities(self, watt_factor):
        """
        "Hideaway Lodge" is still a string representation of an Entity
        object, but it's not in angle brackets because it can't be
        replaced by another Entity object without changing the meaning
        of the Fact.
        """
        assert str(watt_factor["f1_specific"]) == "Fact: Hideaway Lodge was a motel"

    def test_new_concrete_context(self, watt_factor):
        different = watt_factor["f2"].new_context(
            [Human("He-Man"), Entity("Castle Grayskull")]
        )
        assert "<He-Man> operated" in str(different)

    def test_concrete_to_abstract(self, make_entity, make_predicate):
        motel = make_entity["motel_specific"]
        d = make_entity["watt"]
        fact = Fact.new(predicate=make_predicate["p2"], entity_context=(d, motel))
        assert "<Wattenburg> operated and lived at Hideaway Lodge" in str(fact)
        assert "<Wattenburg> operated and lived at <Hideaway Lodge>" in str(
            fact.make_generic()
        )

    def test_entity_slots_as_length_of_factor(self, watt_factor):
        assert len(watt_factor["f1"].predicate) == 1
        assert len(watt_factor["f1"]) == 1

    def test_entity_orders(self, make_entity, watt_factor):
        assert watt_factor["f7_swap_entities_4"].entity_orders == {
            (make_entity["watt"], make_entity["motel_specific"]),
            (make_entity["motel_specific"], make_entity["watt"]),
        }

    def test_predicate_with_entities(self, make_entity, watt_factor):
        assert (
            watt_factor["f1"].predicate.content_with_entities((make_entity["motel"]))
            == "<Hideaway Lodge> was a motel"
        )

    def test_factor_entity_context_does_not_match_predicate(self, make_predicate):
        with pytest.raises(ValueError):
            _ = Fact.new(make_predicate["p1"], (0, 1, 2))

    def test_reciprocal_with_wrong_number_of_entities(self, make_entity, watt_factor):
        with pytest.raises(ValueError):
            watt_factor["f1"].predicate.content_with_entities(
                (make_entity["motel"], make_entity["watt"])
            )

    def test_false_predicate_with_entities(self, make_entity, watt_factor):
        assert watt_factor["f7"].predicate_in_context(
            (make_entity["trees"], make_entity["motel"])
        ) == str(
            "Fact: The distance between <the stockpile of trees> "
            + "and <Hideaway Lodge> was no more than 35 foot"
        )

    def test_entity_and_human_in_predicate(self, make_entity, watt_factor):
        assert (
            watt_factor["f2"].predicate.content_with_entities(
                (make_entity["watt"], make_entity["motel"])
            )
            == "<Wattenburg> operated and lived at <Hideaway Lodge>"
        )

    def test_fact_label_with_entities(self, make_entity, watt_factor):
        assert (
            watt_factor["f2"].predicate_in_context(
                (make_entity["watt"], make_entity["motel"])
            )
            == "Fact: <Wattenburg> operated and lived at <Hideaway Lodge>"
        )

    def test_standard_of_proof_must_be_listed(self, make_predicate):
        with pytest.raises(ValueError):
            _ = Fact.new(make_predicate["p2"], standard_of_proof="probably so")

    def test_standard_of_proof_in_str(self, watt_factor):
        factor = watt_factor["f2_preponderance_of_evidence"]
        assert factor.standard_of_proof in str(factor)

    def test_context_register(self, make_entity, watt_factor):
        assert watt_factor["f1"].context_register(watt_factor["f1_entity_order"]) == [
            {
                make_entity["motel"]: make_entity["watt"],
                watt_factor["f1"]: watt_factor["f1_entity_order"],
            }
        ]

    def test_import_to_mapping(self, make_entity, watt_factor):
        f = watt_factor["f7"]
        assert (
            len(
                f._import_to_mapping(
                    {
                        watt_factor["f7"]: watt_factor["f7_swap_entities"],
                        make_entity["motel"]: make_entity["trees"],
                    },
                    {make_entity["trees"]: make_entity["motel"]},
                )
            )
            == 3
        )

    def test_import_to_mapping_no_change(self, make_entity, watt_factor):
        f = watt_factor["f7"]
        old_mapping = {
            watt_factor["f7"]: watt_factor["f7_swap_entities"],
            make_entity["motel"]: make_entity["trees"],
        }
        assert (
            f._import_to_mapping(
                old_mapping, {make_entity["motel"]: make_entity["trees"]}
            )
            == old_mapping
        )

    def test_import_to_mapping_conflict(self, make_entity, watt_factor):
        f = watt_factor["f7"]
        assert (
            f._import_to_mapping(
                {make_entity["motel"]: make_entity["trees"]},
                {make_entity["motel"]: make_entity["motel"]},
            )
            == False
        )

    def test_reciprocal_context_register(self, make_entity, watt_factor):
        d = watt_factor["f7"].context_register(watt_factor["f7_swap_entities"])
        assert len(d) == 2
        assert {
            make_entity["motel"]: make_entity["trees"],
            make_entity["trees"]: make_entity["motel"],
            watt_factor["f7"]: watt_factor["f7_swap_entities"],
        } in d
        assert {
            make_entity["motel"]: make_entity["motel"],
            make_entity["trees"]: make_entity["trees"],
            watt_factor["f7"]: watt_factor["f7_swap_entities"],
        } in d

    # Equality

    def test_equality_factor_from_same_predicate(self, watt_factor):
        assert watt_factor["f1"] == watt_factor["f1b"]

    def test_equality_factor_from_equal_predicate(self, watt_factor):
        assert watt_factor["f1"] == watt_factor["f1c"]

    def test_equality_because_factors_are_generic_entities(self, watt_factor):
        assert watt_factor["f1"] == watt_factor["f1_different_entity"]

    def test_unequal_because_a_factor_is_not_generic(self, watt_factor):
        assert watt_factor["f9_swap_entities_4"] != watt_factor["f9"]

    def test_generic_factors_equal(self, watt_factor):
        assert watt_factor["f2_generic"] == watt_factor["f2_false_generic"]
        assert watt_factor["f2_generic"] == watt_factor["f3_generic"]

    def test_equal_referencing_diffent_generic_factors(self, make_factor):
        assert make_factor["f_murder"] == make_factor["f_murder_craig"]

    def test_generic_and_specific_factors_unequal(self, watt_factor):
        assert watt_factor["f2"] != watt_factor["f2_generic"]

    def test_factor_reciprocal_unequal(self, watt_factor):
        assert watt_factor["f2"] != watt_factor["f2_reciprocal"]

    def test_factor_unequal_predicate_truth(self, watt_factor):
        assert watt_factor["f7"] != watt_factor["f7_opposite"]
        assert watt_factor["f7"].contradicts(watt_factor["f7_opposite"])

    def test_copies_of_identical_factor(self, make_factor):
        """
        Even if the two factors have different entity markers in self.entity_context,
        I expect them to evaluate equal because the choice of entity markers is
        arbitrary.
        """
        f = make_factor
        assert f["f_irrelevant_3"] == f["f_irrelevant_3"]
        assert f["f_irrelevant_3"] == f["f_irrelevant_3_new_context"]

    def test_equal_with_different_generic_subfactors(self, make_complex_fact):
        assert (
            make_complex_fact["f_relevant_murder"]
            == make_complex_fact["f_relevant_murder_craig"]
        )

    @pytest.mark.xfail
    def test_unequal_due_to_repeating_entity(self, make_factor):
        """I'm not convinced that a model of a Fact ever needs to include
        multiple references to the same Entity just because the name of the
        Entity appears more than once in the Predicate."""
        f = make_factor
        assert f["f_three_entities"] != f["f_repeating_entity"]

    def test_standard_of_proof_inequality(self, watt_factor):

        f = watt_factor
        assert f["f2_clear_and_convincing"] != f["f2_preponderance_of_evidence"]
        assert f["f2_clear_and_convincing"] != f["f2"]

    # Implication

    def test_specific_factor_implies_generic(self, watt_factor):
        assert watt_factor["f2"] > watt_factor["f2_generic"]

    def test_specific_implies_generic_form_of_another_fact(self, watt_factor):
        assert watt_factor["f2"] > watt_factor["f3_generic"]

    def test_specific_fact_does_not_imply_generic_entity(
        self, make_entity, watt_factor
    ):
        assert not watt_factor["f2"] > make_entity["motel"]

    def test_factor_does_not_imply_predicate(self, make_predicate, watt_factor):
        with pytest.raises(TypeError):
            assert not watt_factor["f8_meters"] > make_predicate["p8"]

    def test_factor_implies_because_of_quantity(self, watt_factor):
        assert watt_factor["f8_meters"] > watt_factor["f8"]
        assert watt_factor["f8_higher_int"] > watt_factor["f8_float"]
        assert watt_factor["f8_int"] < watt_factor["f8_higher_int"]

    def test_factor_implies_no_truth_value(self, watt_factor):
        assert watt_factor["f2"] > watt_factor["f2_no_truth"]
        assert not watt_factor["f2_no_truth"] > watt_factor["f2"]

    def test_factor_implies_because_of_exact_quantity(self, watt_factor):
        assert watt_factor["f8_exact"] > watt_factor["f7"]
        assert watt_factor["f8_exact"] >= watt_factor["f8"]

    def test_absent_factor_implies_absent_factor_with_greater_quantity(
        self, watt_factor
    ):
        assert watt_factor["f9_absent"] > watt_factor["f9_absent_miles"]

    def test_equal_factors_not_gt(self, watt_factor):
        f = watt_factor
        assert f["f7"] >= f["f7_swap_entities"]
        assert f["f7"] <= f["f7_swap_entities"]
        assert not f["f7"] > f["f7_swap_entities"]

    def test_standard_of_proof_comparison(self, watt_factor):
        f = watt_factor
        assert f["f2_clear_and_convincing"] >= f["f2_preponderance_of_evidence"]
        assert f["f2_beyond_reasonable_doubt"] >= f["f2_clear_and_convincing"]

    def test_no_implication_between_factors_with_and_without_standards(
        self, watt_factor
    ):
        f = watt_factor
        assert not f["f2_clear_and_convincing"] > f["f2"]
        assert not f["f2"] > f["f2_preponderance_of_evidence"]

    def test_implication_complex(self, make_complex_fact):
        assert (
            make_complex_fact["f_relevant_murder"]
            > make_complex_fact["f_relevant_murder_whether"]
        )

    def test_no_implication_complex(self, make_complex_fact):
        assert (
            not make_complex_fact["f_relevant_murder"]
            >= make_complex_fact["f_relevant_murder_alice_craig"]
        )

    # Contradiction

    def test_factor_does_not_contradict_predicate(self, make_predicate, watt_factor):
        with pytest.raises(TypeError):
            _ = watt_factor["f7"].contradicts(make_predicate["p7_true"])

    def test_factor_contradiction_absent_predicate(self, watt_factor):
        assert watt_factor["f3"].contradicts(watt_factor["f3_absent"])
        assert watt_factor["f3_absent"].contradicts(watt_factor["f3"])

    def test_factor_no_contradiction_no_truth_value(self, watt_factor):
        assert not watt_factor["f2"].contradicts(watt_factor["f2_no_truth"])
        assert not watt_factor["f2_no_truth"].contradicts(watt_factor["f2_false"])

    def test_absent_factor_contradicts_broader_quantity_statement(self, watt_factor):
        assert watt_factor["f8_absent"].contradicts(watt_factor["f8_meters"])
        assert watt_factor["f8_meters"].contradicts(watt_factor["f8_absent"])

    def test_absent_does_not_contradict_narrower_quantity_statement(self, watt_factor):
        assert not watt_factor["f9_absent_miles"].contradicts(watt_factor["f9"])
        assert not watt_factor["f9"].contradicts(watt_factor["f9_absent_miles"])


    def test_contradiction_complex(self, make_complex_fact):
        assert make_complex_fact["f_irrelevant_murder"].contradicts(
            make_complex_fact["f_relevant_murder_craig"]
        )

    def test_no_contradiction_complex(self, make_complex_fact):
        assert not make_complex_fact["f_irrelevant_murder"].contradicts(
            make_complex_fact["f_relevant_murder_alice_craig"]
        )

    # Consistency with Entity/Factor assignments

    def test_copy_with_foreign_context(self, watt_mentioned, watt_factor):
        w = watt_mentioned
        assert (
            watt_factor["f1"].copy_with_foreign_context({w[0]: w[2]})
            == watt_factor["f1_different_entity"]
        )

    def test_check_entity_consistency_true(self, make_entity, make_factor):
        f = make_factor
        e = make_entity
        assert check_entity_consistency(
            f["f_irrelevant_3"], f["f_irrelevant_3_new_context"], {e["dan"]: e["craig"]}
        )
        assert check_entity_consistency(
            f["f_irrelevant_3"],
            f["f_irrelevant_3_new_context"],
            {
                e["alice"]: e["bob"],
                e["bob"]: e["alice"],
                e["craig"]: e["dan"],
                e["dan"]: e["craig"],
                e["circus"]: e["circus"],
            },
        )

    def test_check_entity_consistency_false(self, make_entity, make_factor):
        assert not check_entity_consistency(
            make_factor["f_irrelevant_3"],
            make_factor["f_irrelevant_3_new_context"],
            {make_entity["circus"]: make_entity["alice"]},
        )

    def test_entity_consistency_identity_not_equality(self, make_entity, make_factor):
        assert not check_entity_consistency(
            make_factor["f_irrelevant_3"],
            make_factor["f_irrelevant_3_new_context"],
            {make_entity["dan"]: make_entity["dan"]},
        )

    def test_check_entity_consistency_type_error(self, make_factor, make_holding):
        m = make_factor
        with pytest.raises(TypeError):
            check_entity_consistency(
                m["f_irrelevant_3"], make_holding["h2"], (None, None, None, None, 0)
            )