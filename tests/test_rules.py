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
        assert f["f1"].entity_context == (watt_mentioned[0],)
        assert f["f2"] in c1.inputs
        assert f["f2"] in c1_again.inputs
        assert f["f2"].entity_context == (watt_mentioned[1], watt_mentioned[0])

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


class TestRules:
    def test_enactment_type_in_str(self, make_holding):
        assert "constitution" in str(make_holding["h1"]).lower()

    def test_enactment_text_in_str(self, make_holding):
        assert "secure in their persons" in str(make_holding["h1"])

    def test_None_not_in_str(self, make_holding):
        assert "None" not in str(make_holding["h2"])

    def test_new_concrete_context(self, make_holding):
        different = make_holding["h1"].new_context(
            [Entity("Castle Grayskull"), Human("He-Man")]
        )
        assert "<He-Man> operated" in str(different)

    def test_new_context_non_generic(self, make_holding, watt_factor):
        different = make_holding["h1"].new_context(
            {watt_factor["f1"]: watt_factor["f7"]}
        )
        assert "the distance between <Hideaway Lodge> and" in str(different)

    def test_new_context_non_generic_from_list_error(self, make_holding, watt_factor):
        with pytest.raises(ValueError):
            different = make_holding["h1"].new_context(
                [watt_factor["f1"], watt_factor["f7"], watt_factor["f2"]]
            )

    def test_new_context_dict_must_contain_only_factors(
        self, make_holding, make_predicate
    ):
        with pytest.raises(TypeError):
            different = make_holding["h1"].new_context(
                {make_predicate["p1"]: make_predicate["p7"]}
            )

    def test_new_context_dict_must_be_dict(
        self, make_holding, make_predicate
    ):
        with pytest.raises(TypeError):
            different = make_holding["h1"].new_context(
                make_predicate["p1"]
            )


    def test_generic_factors(self, make_entity, make_holding):
        generics = make_holding["h3"].generic_factors
        assert make_entity["motel"] in generics
        assert make_entity["tree_search"] in generics

    def test_generic_factors_order(self, make_entity, make_holding):
        """The motel is mentioned in the first input in the JSON,
        so it should be first."""
        generics = make_holding["h1"].generic_factors
        assert list(generics) == [make_entity["motel"], make_entity["watt"]]

    def test_string_with_line_breaks(self, make_opinion):
        cardenas_holdings = Rule.from_json("holding_cardenas.json")
        assert "was addicted to heroin\n" in str(cardenas_holdings[0])

    def test_string_mentions_absence(self, make_opinion):
        cardenas_holdings = Rule.from_json("holding_cardenas.json")
        assert "the absence of testimony by <parole officer>" in str(
            cardenas_holdings[1]
        )

    def test_factor_properties_for_rule(self, make_opinion):
        cardenas_holdings = Rule.from_json("holding_cardenas.json")
        assert len(cardenas_holdings[1].inputs) == 1

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

    def test_all_to_all(self, make_holding):
        """This is supposed to test reciprocal predicates in despite factors."""
        assert make_holding["h2_exact_in_despite_ALL"] > make_holding["h2_ALL"]

    def test_all_to_all_reciprocal(self, make_holding, caplog):
        """
        The entity order shouldn't matter, compared to test_all_to_all,
        because it's the mirror image of the normal entity order.
        """
        caplog.set_level(logging.DEBUG)
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
        assert isinstance(make_holding["h2"].enactments, tuple)

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
