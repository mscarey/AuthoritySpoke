import logging

from authorityspoke.factors import Fact
from authorityspoke.factors import Evidence, Exhibit

class TestExhibits:
    def test_make_exhibit_object(self, watt_factor):
        e = Exhibit(form="testimony")
        assert not e.absent

    # Equality

    def test_equality(self, make_exhibit):
        assert (
            make_exhibit["no_shooting_entity_order_testimony"].means(make_exhibit["no_shooting_testimony"]
        ))

    def test_not_equal_different_speaker(self, make_exhibit):
        assert not (
            make_exhibit["no_shooting_different_witness_testimony"].means(make_exhibit["no_shooting_testimony"]
        ))

    def test_equal_complex_statement(self, make_exhibit):
        assert (
            make_exhibit["relevant_murder_nested_swap_testimony"].means(make_exhibit["relevant_murder_testimony"])
        )

    def test_not_equal_complex_statement(self, make_exhibit):
        assert not (
            make_exhibit["relevant_murder_alice_craig_testimony"].means(make_exhibit["relevant_murder_testimony"])
        )

    # Implication

    def test_implication(self, make_exhibit, caplog):
        caplog.set_level(logging.DEBUG)
        assert (
            make_exhibit["no_shooting_testimony"]
            > make_exhibit["no_shooting_witness_unknown_testimony"]
        )

    def test_no_implication_different_speaker(self, make_exhibit):
        assert (
            not make_exhibit["no_shooting_different_witness_testimony"]
            >= make_exhibit["no_shooting_testimony"]
        )

    def test_any_exhibit_implies_generic(self, make_exhibit):
        assert make_exhibit["reciprocal_testimony"] >= make_exhibit["generic_exhibit"]

    def test_exhibit_with_features_implies_featureless(self, make_exhibit):
        assert (
            make_exhibit["reciprocal_testimony"]
            >= make_exhibit["specific_but_featureless"]
        )

    def test_exhibit_no_implication_different_form(self, make_exhibit):
        assert (
            not make_exhibit["reciprocal_testimony"]
            >= make_exhibit["reciprocal_declaration"]
        )
        assert (
            not make_exhibit["reciprocal_testimony"]
            == make_exhibit["reciprocal_declaration"]
        )

    def test_implication_more_specific_testimony(self, make_exhibit):
        assert (
            make_exhibit["reciprocal_testimony_specific"]
            > make_exhibit["reciprocal_testimony"]
        )

    def test_implication_present_and_absent_testimony(self, make_exhibit):
        assert not (
            make_exhibit["reciprocal_testimony_specific_absent"]
            > make_exhibit["reciprocal_testimony"]
        )

    def test_absent_implies_more_specific_absent(self, make_exhibit):
        assert (
            make_exhibit["reciprocal_testimony_absent"]
            > make_exhibit["reciprocal_testimony_specific_absent"]
        )

    def test_absent_does_not_imply_less_specific_absent(self, make_exhibit):
        assert not (
            make_exhibit["reciprocal_testimony_specific_absent"]
            > make_exhibit["reciprocal_testimony_absent"]
        )

    # Contradiction

    def test_conflicting_exhibits_not_contradictory(self, make_exhibit):
        assert not make_exhibit["shooting_testimony"].contradicts(
            make_exhibit["no_shooting_testimony"]
        )

    def test_absent_contradicts_same_present(self, make_exhibit):
        assert make_exhibit["no_shooting_witness_unknown_absent_testimony"].contradicts(
            make_exhibit["no_shooting_witness_unknown_testimony"]
        )

    def test_present_contradicts_same_absent(self, make_exhibit):
        assert make_exhibit["no_shooting_witness_unknown_absent_testimony"].contradicts(
            make_exhibit["no_shooting_witness_unknown_testimony"]
        )

    def test_more_specific_contradicts_absent(self, make_exhibit):
        assert make_exhibit["reciprocal_testimony_absent"].contradicts(make_exhibit["reciprocal_testimony_specific"])
        assert make_exhibit["reciprocal_testimony_specific"].contradicts(make_exhibit["reciprocal_testimony_absent"])

    def test_no_contradiction_with_factor_subclass(self, make_exhibit, watt_factor):
        assert not make_exhibit["shooting_testimony"].contradicts(watt_factor["f4"])
        assert not watt_factor["f4"].contradicts(make_exhibit["shooting_testimony"])

class TestEvidence:
    def test_make_evidence_object(self, watt_factor):
        e = Evidence(Exhibit(form="testimony"), to_effect=watt_factor["f2"])
        assert not e.absent

    def test_default_len_based_on_unique_entity_slots(self, make_entity, make_factor):
        """same as e["no_shooting"]"""

        e = Evidence(
            Exhibit(
                form="testimony",
                statement=make_factor["f_no_shooting"],
                stated_by=make_entity["alice"],
            ),
            to_effect=make_factor["f_no_crime"],
        )
        assert not e.generic


    def test_no_extra_space_around_exhibit_in_string(self, make_opinion_with_holding):
        """
        Don't expect the holdings imported from the JSON to
        exactly match the holdings created for testing in conftest.
        """

        lotus = make_opinion_with_holding["lotus_majority"]
        assert " , " not in str(lotus.holdings[4].inputs[0])

    def test_get_entity_orders(self, make_evidence):
        # TODO: check this after making Evidence.__str__ method
        context = make_evidence["no_shooting"].exhibit.statement.context_factors
        assert "Alice" in str(context[0])
        assert "Bob" in str(context[1])

    def test_get_entity_orders_no_statement(self, make_factor):
        e = Evidence(Exhibit(form="testimony"), to_effect=make_factor["f_no_crime"])
        assert len(e.to_effect.context_factors) == 1

    def test_evidence_str(self, make_evidence):
        assert str(make_evidence["reciprocal"]).lower().startswith("evidence of testimony by")

    def test_equality_with_entity_order(self, make_predicate, make_evidence):
        e = make_evidence
        assert e["no_shooting"].means(e["no_shooting_entity_order"])

    def test_equality_with_no_statement(self, make_evidence):
        assert make_evidence["crime"].means(make_evidence["crime"])

    def test_unequal_due_to_entity_order(self, make_evidence):
        e = make_evidence
        assert not e["no_shooting"].means(e["no_shooting_different_witness"])

    def test_unequal_different_attributes(self, make_evidence):
        assert not (
            make_evidence["no_shooting_no_effect_entity_order"].means(make_evidence["no_shooting_different_witness"]
        ))

    def test_implication_missing_witness(self, make_evidence):
        e = make_evidence
        assert e["no_shooting"] >= e["no_shooting_witness_unknown"]

    def test_implication_missing_effect(self, make_evidence):
        e = make_evidence
        assert e["no_shooting"] >= e["no_shooting_no_effect_entity_order"]

    def test_no_implication_of_fact(
        self, make_predicate, make_evidence, watt_mentioned
    ):
        cool_fact = Fact(
            make_predicate["p_no_shooting"], case_factors=watt_mentioned
        )
        assert not make_evidence["no_shooting"] > cool_fact
        assert not cool_fact > make_evidence["no_shooting"]

    def test_no_contradiction_of_fact(
        self, make_predicate, make_evidence, watt_mentioned
    ):
        assert not make_evidence["no_shooting"].contradicts(
            Fact(make_predicate["p_no_shooting"], case_factors=watt_mentioned)
        )

    def test_no_contradiction_from_supporting_contradictory_facts(self, make_evidence):
        assert not make_evidence["no_shooting"].contradicts(make_evidence["shooting"])

    def test_contradiction_of_absent_version_of_self(self, make_evidence):
        e = make_evidence
        assert e["no_shooting"].contradicts(e["no_shooting_absent"])

    def test_contradict_absent_version_of_implied_factor(self, make_evidence):
        e = make_evidence
        assert e["no_shooting_witness_unknown_absent"].contradicts(e["no_shooting"])
        assert e["no_shooting"].contradicts(e["no_shooting_witness_unknown_absent"])

    def test_no_contradiction_absent_same_witness(self, make_evidence):
        e = make_evidence
        assert not e["no_shooting_absent"].contradicts(e["no_shooting_witness_unknown"])
        assert not e["no_shooting_witness_unknown"].contradicts(e["no_shooting_absent"])
        assert not e["no_shooting_absent"].contradicts(
            e["no_shooting_different_witness"]
        )

    def test_no_contradiction_of_implied_factor(self, make_evidence):
        e = make_evidence
        assert not e["no_shooting"].contradicts(e["no_shooting_witness_unknown"])
