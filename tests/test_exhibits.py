import logging

from authorityspoke.evidence import Exhibit


class TestExhibits:
    def test_make_exhibit_object(self):
        e = Exhibit(form="testimony")
        assert not e.absent


class TestExhibitsSameMeaning:
    def test_equality(self, make_exhibit):
        assert make_exhibit["no_shooting_entity_order_testimony"].means(
            make_exhibit["no_shooting_testimony"]
        )

    def test_not_equal_different_speaker(self, make_exhibit):
        assert not (
            make_exhibit["no_shooting_different_witness_testimony"].means(
                make_exhibit["no_shooting_testimony"]
            )
        )

    def test_equal_complex_statement(self, make_exhibit):
        assert make_exhibit["relevant_murder_nested_swap_testimony"].means(
            make_exhibit["relevant_murder_testimony"]
        )

    def test_not_equal_complex_statement(self, make_exhibit):
        alice_craig = str(make_exhibit["relevant_murder_alice_craig_testimony"])
        other = str(make_exhibit["relevant_murder_testimony"])

        assert not (
            make_exhibit["relevant_murder_alice_craig_testimony"].means(
                make_exhibit["relevant_murder_testimony"]
            )
        )

    def test_not_equal_different_form(self, make_exhibit):
        assert not make_exhibit["shooting_affidavit"].means(
            make_exhibit["shooting_testimony"]
        )


class TestExhibitsImplication:
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

    def test_implication_fact_with_quantity(self, make_exhibit):
        specific_testimony = make_exhibit["large_weight_testimony"]
        vague_testimony = make_exhibit["small_weight_testimony"]
        assert specific_testimony >= vague_testimony

    def test_implication_fact_with_quantity(self, make_fact_about_exhibit):
        specific_testimony_reliable = make_fact_about_exhibit["f_reliable_large_weight"]
        vague_testimony_reliable = make_fact_about_exhibit["f_reliable_small_weight"]
        assert specific_testimony_reliable >= vague_testimony_reliable


class TestExhibitsContradiction:
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
        assert make_exhibit["reciprocal_testimony_absent"].contradicts(
            make_exhibit["reciprocal_testimony_specific"]
        )
        assert make_exhibit["reciprocal_testimony_specific"].contradicts(
            make_exhibit["reciprocal_testimony_absent"]
        )

    def test_no_contradiction_with_factor_subclass(self, make_exhibit, watt_factor):
        assert not make_exhibit["shooting_testimony"].contradicts(watt_factor["f4"])
        assert not watt_factor["f4"].contradicts(make_exhibit["shooting_testimony"])
