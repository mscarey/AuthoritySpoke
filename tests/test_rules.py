import logging
import pytest

from authorityspoke.enactments import Code, Enactment
from authorityspoke.factors import Predicate, Entity, Factor, Fact
from authorityspoke.factors import Evidence, Exhibit
from authorityspoke.rules import Procedure, Rule, ProceduralRule
from authorityspoke.opinions import Opinion
from authorityspoke.predicates import ureg, Q_
from authorityspoke.context import log_mentioned_context


class TestRules:
    def test_enactment_type_in_str(self, make_holding):
        assert "constitution" in str(make_holding["h1"]).lower()

    def test_no_blank_line_in_str(self, make_holding):
        assert "\n\n" not in str(make_holding["h2"])

    def test_enactment_text_in_str(self, make_holding):
        assert "secure in their persons" in str(make_holding["h1"])

    def test_None_not_in_str(self, make_holding):
        assert "None" not in str(make_holding["h2"])

    def test_new_concrete_context(self, make_holding):
        different = make_holding["h1"].new_context(
            [Entity("Castle Grayskull"), Entity("He-Man")]
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

    def test_new_context_dict_must_be_dict(self, make_holding, make_predicate):
        with pytest.raises(TypeError):
            different = make_holding["h1"].new_context(
                [make_predicate["p1"], make_predicate["p2"]]
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

    def test_string_with_line_breaks(self, make_regime):
        cardenas_holdings = Rule.from_json("holding_cardenas.json", regime=make_regime)
        assert "was addicted to heroin\n" in str(cardenas_holdings[0])

    def test_string_mentions_absence(self, make_regime):
        cardenas_holdings = Rule.from_json("holding_cardenas.json", regime=make_regime)
        assert "absence of evidence of testimony by <parole officer>" in str(
            cardenas_holdings[1]
        )

    def test_factor_properties_for_rule(self, make_regime):
        cardenas_holdings = Rule.from_json("holding_cardenas.json", regime=make_regime)
        assert len(cardenas_holdings[1].inputs) == 1
        assert len(cardenas_holdings[1].outputs) == 1
        assert len(cardenas_holdings[1].despite) == 1

    # Same Meaning

    def test_identical_holdings_equal(self, make_holding):
        assert make_holding["h1"].means(make_holding["h1_again"])

    def test_holdings_equivalent_entity_orders_equal(self, make_holding):
        """
        Test that holdings are considered equal if they have the same factors
        and the numbers they use to refer to entities are different but in an
        equivalent order.
        e.g. {"F1": "1,2,1", "F2": "2,0,0"} and {"F2": "1,2,2", "F1": "0,1,0"}
        """
        assert make_holding["h1"].means(make_holding["h1_entity_order"])

    def test_holdings_different_entities_unequal(self, make_holding):
        assert not make_holding["h1"].means(make_holding["h1_easy"])

    def test_holdings_differing_in_entity_order_equal(self, make_holding):
        assert make_holding["h1"].means(make_holding["h1_entity_order"])

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

    def test_mandatory_implies_permissive(self, make_holding):
        assert make_holding["h2_MUST"] > make_holding["h2"]
        assert not make_holding["h2"] > make_holding["h2_MUST"]

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
        assert make_holding["h1"].negated().means(make_holding["h1_opposite"])

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

    def test_no_implication_between_decided_and_undecided(self, make_holding):
        assert not make_holding["h2_undecided"] >= make_holding["h2"]
        assert not make_holding["h2"] > make_holding["h2_invalid_undecided"]

    def test_error_implication_with_procedure(self, make_holding, make_procedure):
        with pytest.raises(TypeError):
            make_holding["h2_undecided"] >= make_procedure["c2"]

    # Contradiction

    def test_error_contradiction_with_procedure(self, make_holding, make_procedure):
        with pytest.raises(TypeError):
            make_holding["h2_undecided"].contradicts(make_procedure["c2"])

    def test_holding_contradicts_invalid_version_of_self(self, make_holding):
        assert make_holding["h2"].negated().means(make_holding["h2_invalid"])
        assert make_holding["h2"].contradicts(make_holding["h2_invalid"])
        assert make_holding["h2"] >= make_holding["h2_invalid"].negated()

    def test_some_holding_consistent_with_absent_output(self, make_holding):
        assert not make_holding["h2"].contradicts(make_holding["h2_output_absent"])
        assert not make_holding["h2_output_absent"].contradicts(make_holding["h2"])

    def test_some_holding_consistent_with_false_output(self, make_holding):
        assert not make_holding["h2"].contradicts(make_holding["h2_output_false"])
        assert not make_holding["h2_output_false"].contradicts(make_holding["h2"])

    def test_some_holding_consistent_with_absent_false_output(self, make_holding):
        assert not make_holding["h2"].contradicts(
            make_holding["h2_output_absent_false"]
        )
        assert not make_holding["h2_output_absent_false"].contradicts(
            make_holding["h2"]
        )

    def test_contradicts_if_valid(self, make_holding):
        """
        This helper method should return the same value as "contradicts"
        because both holdings are valid.
        """

        assert make_holding["h2_ALL"].contradicts(
            make_holding["h2_SOME_MUST_output_false"]
        )
        assert make_holding["h2_ALL"]._contradicts_if_valid(
            make_holding["h2_SOME_MUST_output_false"]
        )

    def test_contradicts_if_valid_invalid_holding(self, make_holding):

        """
        In the current design, contradicts calls implies;
        implies calls contradicts_if_valid.
        """

        assert make_holding["h2_invalid"].contradicts(
            make_holding["h2_irrelevant_inputs"]
        ) != make_holding["h2_invalid"]._contradicts_if_valid(
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

        assert make_holding["h_nearer_means_curtilage_MUST"]._contradicts_if_valid(
            make_holding["h_near_means_no_curtilage_ALL"]
        )
        assert make_holding["h_near_means_no_curtilage_ALL"]._contradicts_if_valid(
            make_holding["h_nearer_means_curtilage_MUST"]
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

        assert not make_holding["h_near_means_no_curtilage"]._contradicts_if_valid(
            make_holding["h_nearer_means_curtilage_ALL"]
        )
        assert not make_holding["h_nearer_means_curtilage_ALL"]._contradicts_if_valid(
            make_holding["h_near_means_no_curtilage"]
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

        assert make_holding["h_near_means_no_curtilage_ALL_MUST"].contradicts(
            make_holding["h_nearer_means_curtilage"]
        )
        assert make_holding["h_nearer_means_curtilage"].contradicts(
            make_holding["h_near_means_no_curtilage_ALL_MUST"]
        )

    def test_no_contradiction_quantity_outputs(self, make_holding):
        """
        Added to try to break Procedure.contradiction_between_outputs.

        "the distance between {the stockpile of trees} and a parking area
        used by personnel and patrons of {Hideaway Lodge} was <= 5 feet"
        does not contradict
        "the distance between {circus} and a parking area used by personnel
        and patrons of {Hideaway Lodge} was > 5 feet"
        """
        assert not make_holding["h_output_distance_less"].contradicts(
            make_holding["h_output_distance_more"]
        )
        assert not make_holding["h_output_distance_more"].contradicts(
            make_holding["h_output_distance_less"]
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

        assert make_holding["h_near_means_curtilage_ALL_MUST"]._contradicts_if_valid(
            make_holding["h_far_means_no_curtilage"]
        )
        assert make_holding["h_far_means_no_curtilage"]._contradicts_if_valid(
            make_holding["h_near_means_curtilage_ALL_MUST"]
        )

    def test_always_may_contradicts_sometimes_must_not(self, make_holding):
        assert make_holding["h2_ALL"].contradicts(
            make_holding["h2_SOME_MUST_output_false"]
        )
        assert make_holding["h2_SOME_MUST_output_false"].contradicts(
            make_holding["h2_ALL"]
        )

    def test_always_may_contradicts_sometimes_must_omit_output(self, make_holding):
        assert make_holding["h2_ALL"].contradicts(
            make_holding["h2_SOME_MUST_output_absent"]
        )
        assert make_holding["h2_SOME_MUST_output_absent"].contradicts(
            make_holding["h2_ALL"]
        )

    def test_sometimes_must_contradicts_always_may_not(self, make_holding):
        assert make_holding["h2_MUST"].contradicts(
            make_holding["h2_ALL_MAY_output_false"]
        )
        assert make_holding["h2_ALL_MAY_output_false"].contradicts(
            make_holding["h2_MUST"]
        )

    def test_sometimes_must_contradicts_always_must_not(self, make_holding):
        assert make_holding["h2_MUST"].contradicts(
            make_holding["h2_ALL_MUST_output_false"]
        )
        assert make_holding["h2_ALL_MUST_output_false"].contradicts(
            make_holding["h2_MUST"]
        )

    def test_some_must_no_contradict_some_may(self, make_holding):
        assert not make_holding["h2_MUST"].contradicts(make_holding["h2"])
        assert not make_holding["h2"].contradicts(make_holding["h2_MUST"])

    def test_negation_of_h2_contradicts_holding_that_implies_h2(self, make_holding):
        assert make_holding["h2_invalid"].contradicts(
            make_holding["h2_irrelevant_inputs"]
        )
        assert make_holding["h2_irrelevant_inputs"].contradicts(
            make_holding["h2_invalid"]
        )

    def test_holding_that_implies_h2_contradicts_negation_of_h2(self, make_holding):
        """
        Tests whether "contradicts" works reciprocally in this case.
        It should be reciprocal in every case so far, but maybe not for 'decided.'"""

        assert make_holding["h2_ALL"].contradicts(
            make_holding["h2_SOME_MUST_output_false"]
        )
        assert make_holding["h2_SOME_MUST_output_false"].contradicts(
            make_holding["h2_ALL"]
        )

    def test_invalid_holding_contradicts_h2(self, make_holding):

        # You NEVER MAY follow X
        # will contradict
        # You SOMEtimes MAY follow Y
        # if X implies Y

        assert make_holding["h2_invalid"].contradicts(
            make_holding["h2_irrelevant_inputs"]
        )
        assert make_holding["h2_irrelevant_inputs"].contradicts(
            make_holding["h2_invalid"]
        )

    def test_invalidity_of_implying_holding_contradicts_implied(self, make_holding):

        # You NEVER MUST follow X
        # will contradict
        # You SOMEtimes MUST follow Y
        # if X implies Y or Y implies X

        assert make_holding["h2_MUST_invalid"].contradicts(
            make_holding["h2_irrelevant_inputs_MUST"]
        )
        assert make_holding["h2_irrelevant_inputs_MUST"].contradicts(
            make_holding["h2_MUST_invalid"]
        )

    def test_contradiction_with_ALL_MUST_and_invalid_SOME_MUST(self, make_holding):

        # You ALWAYS MUST follow X
        # will contradict
        # You NEVER MUST follow Y
        # if X implies Y or Y implies X

        assert make_holding["h2_ALL_MUST"].contradicts(
            make_holding["h2_irrelevant_inputs_MUST_invalid"]
        )
        assert make_holding["h2_irrelevant_inputs_MUST_invalid"].contradicts(
            make_holding["h2_ALL_MUST"]
        )

    def test_contradiction_with_ALL_MUST_and_invalid_ALL_MAY(self, make_holding):

        # You ALWAYS MUST follow X
        # will contradict
        # You MAY NOT ALWAYS follow Y
        # if Y implies X

        assert make_holding["h2_ALL_MUST"].contradicts(make_holding["h2_ALL_invalid"])
        assert make_holding["h2_ALL_invalid"].contradicts(make_holding["h2_ALL_MUST"])

    def test_contradiction_with_ALL_MUST_and_false_output_ALL_MAY(self, make_holding):

        # You ALWAYS MUST follow X
        # will contradict
        # You MAY NOT ALWAYS follow Y
        # if Y implies X

        assert make_holding["h2_ALL_MUST"].contradicts(
            make_holding["h2_output_false_ALL"]
        )
        assert make_holding["h2_output_false_ALL"].contradicts(
            make_holding["h2_ALL_MUST"]
        )

    def test_undecided_contradicts_holding(self, make_holding):
        """When a lower court issues a holding deciding a legal issue
        and a higher court posits that the issue should be considered
        undecided, the lower court's prior holding is "contradicted"
        in the sense of being rendered ineffective."""

        assert make_holding["h2_undecided"].contradicts(make_holding["h2"])

    def test_undecided_contradicts_holding_reverse(self, make_holding):
        """
        Remember that the "contradicts" relation is not symmetric between
        decided and undecided Rules.
        """
        assert not make_holding["h2"].contradicts(make_holding["h2_undecided"])

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
        assert not make_holding["h2_ALL"].contradicts(
            make_holding["h2_irrelevant_inputs_undecided"]
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
        assert not make_holding["h2"].contradicts(
            make_holding["h2_irrelevant_inputs_undecided"]
        )

    def test_undecided_holding_no_implied_contradiction(self, make_holding):
        assert not make_holding["h2_irrelevant_inputs_undecided"].contradicts(
            make_holding["h2_ALL_invalid"]
        )
        assert not make_holding["h2_ALL_invalid"].contradicts(
            make_holding["h2_irrelevant_inputs_undecided"]
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

    def test_no_contradiction_same_undecided_holding(self, make_holding):
        assert not make_holding["h3_ALL_undecided"].contradicts(
            make_holding["h3_ALL_undecided"]
        )

    def test_no_contradiction_holding_with_evidence(self, make_holding):
        assert not make_holding["h3_fewer_inputs_ALL_undecided"].contradicts(
            make_holding["h3_ALL"]
        )

    def test_holding_len(self, make_holding):
        assert len(make_holding["h1"]) == 2
        assert len(make_holding["h3"]) == 5
