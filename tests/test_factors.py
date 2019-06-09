import logging
import operator

import pytest

from authorityspoke.factors import Entity, Factor, Fact, means
from authorityspoke.rules import Rule, ProceduralRule
from authorityspoke.opinions import Opinion
from authorityspoke.predicates import ureg, Q_


class TestFacts:
    def test_default_context_factors_for_fact(
        self, make_entity, make_predicate, watt_mentioned
    ):
        e = make_entity
        f2 = Fact(make_predicate["p1"], case_factors=watt_mentioned)
        assert f2.context_factors == (e["motel"],)

    def test_context_factors_from_case_factor_indices(
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

        f2 = Fact(
            make_predicate["p2"], context_factors=(1, 0), case_factors=watt_mentioned
        )
        assert f2.context_factors == (e["watt"], e["motel"])

    def test_mix_of_factors_and_indices_in_init(
        self, make_entity, make_predicate, watt_mentioned
    ):
        e = make_entity
        f2 = Fact(
            make_predicate["p2"],
            context_factors=(1, e["trees"]),
            case_factors=watt_mentioned,
        )
        assert f2.context_factors == (e["watt"], e["trees"])

    def test_make_fact_from_string(self, watt_factor):
        fact_float_more = Fact.from_string(
            "the distance between {Ann} and {Lee} was {>= 20.1}", reciprocal=True
        )
        fact_float_less = watt_factor["f8_int"]
        assert fact_float_more > fact_float_less

    def test_wrong_type_in_context_factors_in_init(
        self, make_entity, make_predicate, watt_mentioned
    ):
        e = make_entity
        with pytest.raises(TypeError):
            f2 = Fact(
                make_predicate["p2"],
                context_factors=(1, "nonsense"),
                case_factors=watt_mentioned,
            )

    def test_invalid_index_for_case_factors_in_init(self, make_predicate, make_entity):
        with pytest.raises(ValueError):
            _ = Fact(
                make_predicate["p1"],
                context_factors=2,
                case_factors=make_entity["watt"],
            )

    def test_convert_int_context_factors_to_tuple(self, make_predicate, watt_mentioned):
        f = Fact(make_predicate["p_irrelevant_1"], 3, case_factors=watt_mentioned)
        assert f.context_factors == (watt_mentioned[3],)

    def test_string_representation_of_factor(self, watt_factor):
        assert "<Hideaway Lodge> was a motel" in str(watt_factor["f1"])
        assert "absence of fact" in str(watt_factor["f3_absent"])

    def test_string_no_truth_value(self, watt_factor):
        assert "whether" in str(watt_factor["f2_no_truth"])

    def test_string_representation_with_concrete_entities(self, watt_factor):
        """
        "Hideaway Lodge" is still a string representation of an Entity
        object, but it's not in angle brackets because it can't be
        replaced by another Entity object without changing the meaning
        of the Fact.
        """
        assert "Hideaway Lodge was a motel" in str(watt_factor["f1_specific"])

    def test_new_context_replace_fact(self, make_entity, watt_factor):
        changes = {
            make_entity["watt"]: Entity("Darth Vader"),
            watt_factor["f2"]: watt_factor["f10"],
        }
        assert "was within the curtilage of <Hideaway Lodge>" in str(
            watt_factor["f2"].new_context(changes)
        )

    def test_get_factor_from_recursive_search(self, make_opinion_with_holding):
        factor_list = list(
            make_opinion_with_holding["cardenas_majority"].holdings[0].recursive_factors
        )
        factor = factor_list[1]
        assert any(
            factor == Entity("parole officer") and factor.name == "parole officer"
            for factor in factor_list
        )

    def test_new_context_from_factor(self, watt_factor):
        different = watt_factor["f1"].new_context(
            Entity("Great Northern", generic=False)
        )
        assert "Great Northern was a motel" in str(different)

    def test_new_concrete_context(self, make_entity, watt_factor):
        different = watt_factor["f2"].new_context(
            {
                make_entity["watt"]: Entity("Darth Vader"),
                make_entity["motel"]: Entity("Death Star"),
            }
        )
        assert "<Darth Vader> operated" in str(different)

    def test_concrete_to_abstract(self, make_entity, make_predicate):
        motel = make_entity["motel_specific"]
        d = make_entity["watt"]
        fact = Fact(predicate=make_predicate["p2"], context_factors=(d, motel))
        assert "<Wattenburg> operated and lived at Hideaway Lodge" in str(fact)
        assert "<Wattenburg> operated and lived at Hideaway Lodge>" in str(
            fact.make_generic()
        )

    def test_entity_slots_as_length_of_factor(self, watt_factor):
        assert len(watt_factor["f1"].predicate) == 1
        assert len(watt_factor["f1"]) == 1

    def test_context_factors_reciprocal(self, make_entity, watt_factor):
        """Predicate.new() no longer coerces the order of self.context_factors.
        Instead, Fact.entity_orders() returns every possible order."""

        motel_near_watt = watt_factor["f7_swap_entities_4"]
        assert len(motel_near_watt.interchangeable_factors[0]) == 2
        assert (
            make_entity["motel_specific"] in motel_near_watt.interchangeable_factors[0]
        )

    def test_predicate_with_entities(self, make_entity, watt_factor):
        assert (
            watt_factor["f1"].predicate.content_with_entities((make_entity["motel"]))
            == "<Hideaway Lodge> was a motel"
        )

    def test_factor_context_factors_does_not_match_predicate(self, make_predicate):
        with pytest.raises(ValueError):
            _ = Fact(make_predicate["p1"], (0, 1, 2))

    def test_reciprocal_with_wrong_number_of_entities(self, make_entity, watt_factor):
        with pytest.raises(ValueError):
            watt_factor["f1"].predicate.content_with_entities(
                (make_entity["motel"], make_entity["watt"])
            )

    def test_false_predicate_with_entities(self, make_entity, watt_factor):
        assert watt_factor["f7"].predicate_in_context(
            (make_entity["trees"], make_entity["motel"])
        ) == str(
            "Fact: the distance between <the stockpile of trees> "
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
            _ = Fact(make_predicate["p2"], standard_of_proof="probably so")

    def test_standard_of_proof_in_str(self, watt_factor):
        factor = watt_factor["f2_preponderance_of_evidence"]
        assert factor.standard_of_proof in str(factor)

    def test_context_register_empty(self, make_complex_fact, watt_factor):
        """
        Yields no context_register because the Entity in f1 doesn't imply
        the Fact in f_relevant_murder.
        """
        with pytest.raises(StopIteration):
            next(
                watt_factor["f1"]._context_registers(make_complex_fact["f_relevant_murder"], operator.ge)
            )

    def test_context_register_valid(self, make_entity, watt_factor):
        assert next(
            watt_factor["f1"]._context_registers(
                watt_factor["f1_entity_order"], operator.le
            )
        ) == {
            make_entity["watt"]: make_entity["motel"],
            make_entity["motel"]: make_entity["watt"],
        }

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
        old_mapping = {make_entity["motel"]: make_entity["trees"]}
        assert dict(
            f._import_to_mapping(
                old_mapping, {make_entity["motel"]: make_entity["trees"]}
            )
        ) == {
            make_entity["motel"]: make_entity["trees"],
            make_entity["trees"]: make_entity["motel"],
        }

    def test_import_to_mapping_conflict(self, make_entity, watt_factor):
        assert (
            watt_factor["f7"]._import_to_mapping(
                {make_entity["motel"]: make_entity["trees"]},
                {make_entity["motel"]: make_entity["motel"]},
            )
            is None
        )

    def test_import_to_mapping_reciprocal(self, watt_factor, caplog):
        caplog.set_level(logging.DEBUG)
        mapping = Factor._import_to_mapping(
            {watt_factor["f7"]: watt_factor["f7"]},
            {watt_factor["f7_swap_entities"]: watt_factor["f7_swap_entities"]},
        )
        assert mapping[watt_factor["f7"]] == watt_factor["f7"]

    def test_registers_for_interchangeable_context(self, make_entity, watt_factor):
        """
        The entity equality test is causing Python to think the
        correct object is in the output when it isn't.
        It's probably also the issue preventing the correct object
        from being in the output.

        Try putting Entity's custom hash method back? Will that help?
        """

        matches = {
            make_entity["motel"]: make_entity["trees"],
            make_entity["trees"]: make_entity["motel"],
            make_entity["watt"]: make_entity["watt"],
        }
        new_matches = [
            match
            for match in watt_factor["f7"]._registers_for_interchangeable_context(
                matches
            )
        ]
        assert {
            make_entity["trees"]: make_entity["trees"],
            make_entity["motel"]: make_entity["motel"],
            make_entity["watt"]: make_entity["watt"],
        } in new_matches

    # Equality

    def test_equality_factor_from_same_predicate(self, watt_factor):
        assert watt_factor["f1"].means(watt_factor["f1b"])

    def test_equality_factor_from_equal_predicate(self, watt_factor):
        assert watt_factor["f1"].means(watt_factor["f1c"])

    def test_equality_because_factors_are_generic_entities(self, watt_factor):
        assert watt_factor["f1"].means(watt_factor["f1_different_entity"])

    def test_unequal_because_a_factor_is_not_generic(self, watt_factor):
        assert not watt_factor["f9_swap_entities_4"].means(watt_factor["f9"])

    def test_generic_factors_equal(self, watt_factor):
        assert watt_factor["f2_generic"].means(watt_factor["f2_false_generic"])
        assert watt_factor["f2_generic"].means(watt_factor["f3_generic"])

    def test_equal_referencing_diffent_generic_factors(self, make_factor):
        assert make_factor["f_murder"].means(make_factor["f_murder_craig"])

    def test_generic_and_specific_factors_unequal(self, watt_factor):
        assert not watt_factor["f2"].means(watt_factor["f2_generic"])

    def test_factor_reciprocal_unequal(self, watt_factor):
        assert not watt_factor["f2"].means(watt_factor["f2_reciprocal"])

    def test_factor_different_predicate_truth_unequal(self, watt_factor):
        assert not watt_factor["f7"].means(watt_factor["f7_opposite"])

    def test_copies_of_identical_factor(self, make_factor):
        """
        Even if the two factors have different entity markers in self.context_factors,
        I expect them to evaluate equal because the choice of entity markers is
        arbitrary.
        """
        f = make_factor
        assert f["f_irrelevant_3"].means(f["f_irrelevant_3"])
        assert f["f_irrelevant_3"].means(f["f_irrelevant_3_new_context"])

    def test_equal_with_different_generic_subfactors(self, make_complex_fact):
        assert make_complex_fact["f_relevant_murder"].means(
            make_complex_fact["f_relevant_murder_craig"]
        )

    def test_reciprocal_context_register(self, watt_factor):
        """
        This test describes two objects with the same meaning that have been
        made in two different ways, each with a different id and repr.
        """
        assert watt_factor["f7"].means(watt_factor["f7_swap_entities"])

    @pytest.mark.xfail
    def test_unequal_due_to_repeating_entity(self, make_factor):
        """I'm not convinced that a model of a Fact ever needs to include
        multiple references to the same Entity just because the name of the
        Entity appears more than once in the Predicate."""
        f = make_factor
        assert not f["f_three_entities"].means(f["f_repeating_entity"])

    def test_standard_of_proof_inequality(self, watt_factor):

        f = watt_factor
        assert not f["f2_clear_and_convincing"].means(f["f2_preponderance_of_evidence"])
        assert not f["f2_clear_and_convincing"].means(f["f2"])

    # Implication

    def test_specific_factor_implies_generic(self, watt_factor):
        assert watt_factor["f2"] > watt_factor["f2_generic"]
        assert not watt_factor["f2_generic"] > watt_factor["f2"]

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

    def test_implication_standard_of_proof(self, make_factor):
        assert (
            not make_factor["f_shooting_craig_poe"]
            > make_factor["f_shooting_craig_brd"]
        )
        assert make_factor["f_shooting_craig_brd"] > make_factor["f_shooting_craig_poe"]

    def test_factor_implies_because_of_exact_quantity(self, watt_factor):
        assert watt_factor["f8_exact"] > watt_factor["f7"]
        assert watt_factor["f8_exact"] >= watt_factor["f8"]

    def test_no_implication_pint_quantity_and_int(self, watt_factor):
        assert not watt_factor["f8"] > watt_factor["f8_int"]
        assert not watt_factor["f8"] < watt_factor["f8_int"]

    def test_absent_factor_implies_absent_factor_with_lesser_quantity(
        self, watt_factor
    ):
        assert watt_factor["f9_absent_miles"] > watt_factor["f9_absent"]

    def test_equal_factors_not_gt(self, watt_factor):
        f = watt_factor
        assert f["f7"] >= f["f7"]
        assert f["f7"] <= f["f7"]
        assert not f["f7"] > f["f7"]

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

    def test_factor_different_predicate_truth_contradicts(self, watt_factor):
        assert watt_factor["f7"].contradicts(watt_factor["f7_opposite"])
        assert watt_factor["f7_opposite"].contradicts(watt_factor["f7"])

    def test_same_predicate_true_vs_false(self, watt_factor):
        assert watt_factor["f10"].contradicts(watt_factor["f10_false"])

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

    def test_no_contradiction_of_None(self, watt_factor):
        assert not watt_factor["f1"].contradicts(None)

    # Consistency with Entity/Factor assignments

    def test_copy_with_foreign_context(self, watt_mentioned, watt_factor):
        w = watt_mentioned
        assert (
            watt_factor["f1"]
            .new_context({w[0]: w[2]})
            .means(watt_factor["f1_different_entity"])
        )

    def test_check_entity_consistency_true(self, make_entity, make_factor):
        left = make_factor["f_irrelevant_3"]
        right = make_factor["f_irrelevant_3_new_context"]
        e = make_entity
        easy_update = left.update_context_register(right, {e["dan"]: e["craig"]}, means)
        harder_update = left.update_context_register(
            right,
            {
                e["alice"]: e["bob"],
                e["bob"]: e["alice"],
                e["craig"]: e["dan"],
                e["dan"]: e["craig"],
                e["circus"]: e["circus"],
            },
            means,
        )
        assert any(register is not None for register in easy_update)
        assert any(register is not None for register in harder_update)

    def test_check_entity_consistency_false(self, make_entity, make_factor):
        update = make_factor["f_irrelevant_3"].update_context_register(
            make_factor["f_irrelevant_3_new_context"],
            {make_entity["circus"]: make_entity["alice"]},
            means,
        )
        assert not any(register is not None for register in update)

    def test_entity_consistency_identity_not_equality(self, make_entity, make_factor):

        update = make_factor["f_irrelevant_3"].update_context_register(
            make_factor["f_irrelevant_3_new_context"],
            {make_entity["dan"]: make_entity["dan"]},
            means,
        )
        assert not any(register is not None for register in update)

    def test_check_entity_consistency_type_error(
        self, make_entity, make_factor, make_predicate
    ):
        """
        There would be no TypeError if it used operator.eq
        instead of .gt. The comparison would just return False.
        """
        m = make_factor
        update = make_factor["f_irrelevant_3"].update_context_register(
            make_predicate["p2"], {make_entity["dan"]: make_entity["dan"]}, operator.gt
        )
        with pytest.raises(TypeError):
            any(register is not None for register in update)
