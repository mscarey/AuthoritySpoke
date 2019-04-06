import logging
import pytest

from authorityspoke.enactments import Code, Enactment
from authorityspoke.entities import Human, Event
from authorityspoke.factors import Predicate, Factor, Entity, Fact
from authorityspoke.factors import Evidence, Exhibit
from authorityspoke.rules import Procedure, Rule, ProceduralRule
from authorityspoke.opinions import Opinion
from authorityspoke.factors import ureg, Q_
from authorityspoke.context import log_mentioned_context



class TestProcedures:
    def test_exception_for_wrong_type_for_procedure(self, make_predicate):
        with pytest.raises(TypeError):
            Procedure(inputs=make_predicate["p1"], outputs=make_predicate["p2"])

    def test_exception_for_wrong_type_in_tuple_for_procedure(self, make_predicate):
        with pytest.raises(TypeError):
            Procedure(inputs=(make_predicate["p1"]), outputs=(make_predicate["p2"]))

    def test_get_context_factors(self, make_procedure):
        # motel, watt
        assert len(make_procedure["c1"].generic_factors) == 2
        # trees, motel
        assert len(make_procedure["c2"].generic_factors) == 2

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

    def test_foreign_match_list(self, make_procedure, watt_mentioned):
        w = watt_mentioned
        assert make_procedure["c2_irrelevant_inputs"].get_foreign_match_list(
            [{w[2]: w[1], w[3]: w[0]}, {w[1]: w[1], w[2]: w[3]}]
        ) == [{w[1]: w[2], w[0]: w[3]}, {w[1]: w[1], w[3]: w[2]}]

    def test_generic_factors(
        self, watt_factor, make_entity, make_evidence, make_procedure
    ):
        """
        Finds that for factor f["f7"], it would be consistent with the
        other group of factors for f["f7"]'s two slots to be assigned
        (0, 1) or (1, 0).
        """
        e = make_entity
        f = watt_factor
        c = make_procedure
        assert set(make_procedure["c3"].generic_factors) == {
            e["motel"],
            e["tree_search"],
            e["trees"],
            e["watt"],
            make_evidence["crime_absent"],
        }

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

    def test_entities_of_inputs_for_identical_procedure(
        self, watt_factor, make_procedure, watt_mentioned
    ):
        f = watt_factor
        c1 = make_procedure["c1"]
        c1_again = make_procedure["c1_again"]
        assert f["f1"] in c1.inputs
        assert f["f1"] in c1_again.inputs
        assert f["f1"].context_factors == (watt_mentioned[0],)
        assert f["f2"] in c1.inputs
        assert f["f2"] in c1_again.inputs
        assert f["f2"].context_factors == (watt_mentioned[1], watt_mentioned[0])

    # Equality

    def test_procedure_equality(self, make_procedure, caplog):
        caplog.set_level(logging.DEBUG)
        assert make_procedure["c1"] == make_procedure["c1_again"]

    def test_procedure_equality_entity_order(self, make_procedure):
        assert make_procedure["c1"] == make_procedure["c1_entity_order"]

    def test_still_equal_after_swapping_reciprocal_entities(
        self, make_procedure, caplog
    ):
        caplog.set_level(logging.DEBUG)
        assert make_procedure["c2"] == make_procedure["c2_reciprocal_swap"]

    def test_unequal_after_swapping_nonreciprocal_entities(self, make_procedure):
        assert make_procedure["c2"] != make_procedure["c2_nonreciprocal_swap"]

    # Implication

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
        assert c2_exact_quantity >= c2

    def test_procedure_general_quantity_does_not_imply_exact(
        self, watt_factor, make_procedure
    ):

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

    # Contradiction

    def test_no_contradict_between_procedures(self, make_procedure):
        """
        I don't think some-to-some contradiction is possible for Procedures
        """
        p = make_procedure
        with pytest.raises(NotImplementedError):
            assert p["c2_higher_quantity"].contradicts(p["c2_exact_in_despite"])
