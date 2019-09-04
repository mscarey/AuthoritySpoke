from authorityspoke.evidence import Evidence, Exhibit
from authorityspoke.facts import Fact


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
        assert "in the form of testimony" in str(make_evidence["reciprocal"]).lower()


class TestEvidenceSameMeaning:
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
            make_evidence["no_shooting_no_effect_entity_order"].means(
                make_evidence["no_shooting_different_witness"]
            )
        )

    def test_not_equal_no_effect(self, make_evidence):
        assert not make_evidence["shooting_no_effect"].means(make_evidence["shooting"])
        assert not make_evidence["shooting"].means(make_evidence["shooting_no_effect"])


class TestEvidenceImplication:
    def test_implication_missing_witness(self, make_evidence):
        e = make_evidence
        assert e["no_shooting"] >= e["no_shooting_witness_unknown"]

    def test_implication_missing_effect(self, make_evidence):
        e = make_evidence
        assert e["no_shooting"] >= e["no_shooting_no_effect_entity_order"]

    def test_no_implication_of_fact(
        self, make_predicate, make_evidence, watt_mentioned
    ):
        cool_fact = Fact(make_predicate["p_no_shooting"], case_factors=watt_mentioned)
        assert not make_evidence["no_shooting"] > cool_fact
        assert not cool_fact > make_evidence["no_shooting"]


class TestEvidenceContradiction:
    def test_no_contradiction_of_fact(self, make_evidence, make_factor):
        assert not make_evidence["no_shooting"].contradicts(
            make_factor["f_no_shooting"]
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
