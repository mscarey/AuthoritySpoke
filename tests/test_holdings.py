import pytest

from authorityspoke.io import readers
from authorityspoke.holdings import Holding


class TestHolding:
    def test_complex_string(self, make_complex_rule):
        holding = Holding(make_complex_rule["accept_murder_fact_from_relevance"])
        string = str(holding)
        assert "is relevant to show the fact that <Alice>" in string

    def test_infer_from_exclusive(self, make_opinion_with_holding):
        """
        Test that the correct inference is made from a Holding being marked
        the "exclusive" way to reach the output "{} infringed the copyright in {}"
        """
        exclusive_holding = make_opinion_with_holding["lotus_majority"].holdings[0]
        inferred = exclusive_holding.inferred_from_exclusive[0]
        assert inferred.outputs[0].content == "{} infringed the copyright in {}"
        assert inferred.outputs[0].absent


class TestSameMeaning:
    def test_identical_holdings_equal(self, make_holding):
        assert make_holding["h1"].means(make_holding["h1_again"])

    def test_negated_method(self, make_holding):
        assert make_holding["h1"].negated().means(make_holding["h1_opposite"])


class TestImplication:
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

    def test_no_undecided_holding_implication_by_MUST(self, make_holding):

        """If it's undecided whether courts MUST follow the procedure in h2,
        it still could be decided that they MAY do so"""

        assert not make_holding["h2_MUST_undecided"] >= make_holding["h2_undecided"]

    def test_no_undecided_holding_implication_of_MUST(self, make_holding):

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

    def test_no_implication_undecided_to_decided(self, make_holding):
        assert not make_holding["h2_undecided"] >= make_holding["h2"]

    def test_no_implication_decided_to_undecided(self, make_holding):
        assert not make_holding["h2"] > make_holding["h2_invalid_undecided"]

    def test_no_implication_of_procedure(self, make_holding, make_procedure):
        assert not make_holding["h2_undecided"] >= make_procedure["c2"]


class TestContradiction:
    def test_holding_contradicts_invalid_version_of_self(self, make_holding):
        assert make_holding["h2"].negated().means(make_holding["h2_invalid"])
        assert make_holding["h2"].contradicts(make_holding["h2_invalid"])
        assert make_holding["h2"] >= make_holding["h2_invalid"].negated()

    def test_contradicts_if_valid(self, make_holding):
        """
        This helper method should return the same value as "contradicts"
        because both holdings are valid.
        """

        assert make_holding["h2_ALL"].contradicts(
            make_holding["h2_SOME_MUST_output_false"]
        )
        assert make_holding["h2_ALL"].rule.contradicts(
            make_holding["h2_SOME_MUST_output_false"].rule
        )

    def test_contradicts_if_valid_invalid_holding(self, make_holding):

        """
        In the current design, Holding.contradicts calls implies;
        implies calls Rule.contradicts.
        """

        assert make_holding["h2_invalid"].contradicts(
            make_holding["h2_irrelevant_inputs"]
        )
        assert not make_holding["h2_invalid"].rule.contradicts(
            make_holding["h2_irrelevant_inputs"].rule
        )

    def test_negation_of_h2_contradicts_holding_that_implies_h2(self, make_holding):
        assert make_holding["h2_invalid"].contradicts(
            make_holding["h2_irrelevant_inputs"]
        )
        assert make_holding["h2_irrelevant_inputs"].contradicts(
            make_holding["h2_invalid"]
        )

    def test_invalid_holding_contradicts_h2(self, make_holding):
        """
        You NEVER MAY follow X
        will contradict
        You SOMEtimes MAY follow Y
        if X implies Y
        """
        assert make_holding["h2_invalid"].contradicts(
            make_holding["h2_irrelevant_inputs"]
        )
        assert make_holding["h2_irrelevant_inputs"].contradicts(
            make_holding["h2_invalid"]
        )

    def test_holding_that_implies_h2_contradicts_negation_of_h2(self, make_holding):
        """
        Tests whether "contradicts" works reciprocally in this case.
        It should be reciprocal in every case so far, but maybe not for 'decided.'
        """

        assert make_holding["h2_ALL"].contradicts(
            make_holding["h2_SOME_MUST_output_false"]
        )
        assert make_holding["h2_SOME_MUST_output_false"].contradicts(
            make_holding["h2_ALL"]
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

    def test_contradiction_with_distance(self, make_opinion_with_holding, make_holding):
        watt = make_opinion_with_holding["watt_majority"]
        must_not_rule = make_holding["h2_output_false_ALL_MUST"]
        assert list(watt.holdings)[1].contradicts(must_not_rule)

    def test_error_contradiction_with_procedure(self, make_holding, make_procedure):
        with pytest.raises(TypeError):
            make_holding["h2_undecided"].contradicts(make_procedure["c2"])


class TestUnion:
    def test_union_neither_universal(self, make_opinion_with_holding):
        feist = make_opinion_with_holding["feist_majority"]
        holdings = list(feist.holdings)
        assert (holdings[9] | holdings[7]) is None

    def test_union_and_addition_different(self, make_opinion_with_holding):
        feist = make_opinion_with_holding["feist_majority"]
        result_of_adding = feist.holdings[10] + feist.holdings[3]
        result_of_union = feist.holdings[10] | feist.holdings[3]
        assert not result_of_adding.means(result_of_union)

    def test_union_with_exclusive_flag(self, make_opinion_with_holding):
        feist = make_opinion_with_holding["feist_majority"]
        result_of_union = feist.holdings[10] | feist.holdings[3]
        assert isinstance(result_of_union, Holding)
