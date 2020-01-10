import pytest

from authorityspoke.entities import Entity
from authorityspoke.explanations import Explanation
from authorityspoke.factors import ContextRegister, FactorSequence
from authorityspoke.holdings import Holding


class TestHolding:
    def test_complex_string(self, make_complex_rule):
        holding = Holding(make_complex_rule["accept_murder_fact_from_relevance"])
        string = " ".join([x.strip() for x in str(holding).splitlines()])
        assert "is relevant to show the fact that <Alice>" in string.replace("/n", " ")

    def test_string_indentation(self, make_opinion_with_holding):
        """
        Test that the text of an Evidence string is indented even
        when it appears in a Holding.
        """
        lotus = make_opinion_with_holding["lotus_majority"]
        assert "    OF:\n" in str(lotus.holdings[2])

    def test_infer_from_exclusive(self, make_opinion_with_holding):
        """
        Test that the correct inference is made from a Holding being marked
        the "exclusive" way to reach the output "{} infringed the copyright in {}"
        """
        exclusive_holding = make_opinion_with_holding["lotus_majority"].holdings[0]
        inferred = exclusive_holding.inferred_from_exclusive[0]
        assert inferred.outputs[0].content == "{} infringed the copyright in {}"
        assert inferred.outputs[0].absent

    def test_infer_from_not_exclusive(self, make_holding):
        """
        For a Holding with `exclusive=False`, inferred_from_exclusive
        should return an empty list.
        """
        assert not make_holding["h1"].inferred_from_exclusive

    def test_type_of_context_factors(self, make_holding):
        assert isinstance(make_holding["h1"].context_factors, FactorSequence)


class TestSameMeaning:
    def test_identical_holdings_equal(self, make_holding):
        assert make_holding["h1"].means(make_holding["h1_again"])

    def test_holding_does_not_mean_None(self, make_holding):
        assert not make_holding["h1"].means(None)

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

    def test_holding_implies_opinion_with_no_holdings(
        self, make_opinion_with_holding, make_opinion
    ):
        lotus = make_opinion["lotus_majority"]
        holding = make_opinion_with_holding["oracle_majority"].holdings[0]
        assert holding.implies(
            lotus,
            context=ContextRegister(
                {Entity("the Java API"): Entity("the Lotus menu command hierarchy")}
            ),
        )

    def test_holding_implies_none(self, make_holding):
        assert make_holding["h3"] >= None

    def test_holding_implies_rule(self, make_holding, make_rule):
        assert make_holding["h3"] >= make_rule["h3"]

    def test_implication_due_to_always(self, make_decision_with_holding):
        """
        A "MUST ALWAYS" Holding about copyrightability implies that
        things "MAY SOMETIMES" be copyrightable if they're computer
        programs. Makes sense in this context, but it would also
        have found implication of "Socrates is human, thus Socrates
        may sometimes be copyrightable."

        This goes back to the issue that new Holdings can't be
        generated just because they'd be implied if they existed.
        """
        oracle = make_decision_with_holding["oracle"]
        assert oracle.holdings[18].implies(oracle.holdings[19])

    def test_explain_implication(self, make_decision_with_holding):
        oracle = make_decision_with_holding["oracle"]
        explanation = oracle.holdings[18].explain_implication(oracle.holdings[19])
        assert "implication" in str(explanation).lower()

    def test_explanation_same_generic_factor(self, make_decision_with_holding):
        """
        Test that the ContextRegister makes sense when the same generic
        Factors occur in Holdings on both sides of the "implies" relationship.
        """
        oracle = make_decision_with_holding["oracle"]
        language = Entity("the Java language")
        new_context = oracle.holdings[18].new_context(
            {Entity("the Java API"): language}
        )
        explanation = new_context.explain_implication(oracle.holdings[19])
        assert explanation.context[language] == language


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

    def test_holding_contradicts_opinion(self, make_opinion_with_holding):
        oracle = make_opinion_with_holding["oracle_majority"]
        lotus = make_opinion_with_holding["lotus_majority"]
        assert lotus.holdings[6].contradicts(
            oracle,
            context=ContextRegister(
                {Entity("the Lotus menu command hierarchy"): Entity("the Java API")}
            ),
        )

    def test_explain_holding_contradicting_opinion(self, make_opinion_with_holding):
        oracle = make_opinion_with_holding["oracle_majority"]
        lotus = make_opinion_with_holding["lotus_majority"]
        explanation = lotus.holdings[6].explain_contradiction(oracle)
        assert "an explanation" in str(explanation).lower()

    def test_no_holding_contradiction_explanations(self, make_opinion_with_holding):
        lotus = make_opinion_with_holding["lotus_majority"]
        explanation = lotus.holdings[1].explain_contradiction(lotus.holdings[2])
        assert explanation is None

    def test_holding_does_not_contradict_fact(self, make_holding, watt_factor):
        assert not make_holding["h1"].contradicts(watt_factor["f1"])
        assert not watt_factor["f1"].contradicts(make_holding["h1"])

    def test_error_no_contradiction_test(self, make_holding):
        with pytest.raises(TypeError):
            _ = make_holding["h1"].contradicts(ContextRegister({}))

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

    # Contradiction of undecided Holdings

    def test_no_contradiction_same_undecided_holding(self, make_holding):
        assert not make_holding["h3_ALL_undecided"].contradicts(
            make_holding["h3_ALL_undecided"]
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

    def test_contradiction_with_evidence(self, make_holding):
        assert make_holding["h3_ALL_undecided"].contradicts(
            make_holding["h3_fewer_inputs_ALL"]
        )

    def test_no_contradiction_holding_with_evidence(self, make_holding):
        assert not make_holding["h3_fewer_inputs_ALL_undecided"].contradicts(
            make_holding["h3_ALL"]
        )

    # Contradiction of other types

    def test_contradiction_with_procedure(self, make_holding, make_procedure):
        """
        This test previously required a TypeError, but on second
        thought the command expresses a pretty clear intention to
        convert the Procedure to a Holding.
        """
        assert make_holding["h2_undecided"].contradicts(make_procedure["c2"])


class TestAddition:
    def test_adding_same_ALL_holdings_results_in_same(self, make_opinion_with_holding):
        brad = make_opinion_with_holding["brad_majority"]
        assert brad.holdings[0] + brad.holdings[0] == brad.holdings[0]

    def test_adding_same_SOME_holdings_results_in_None(self, make_opinion_with_holding):
        watt = make_opinion_with_holding["watt_majority"]
        assert watt.holdings[0] + watt.holdings[0] is None

    def test_add_rule_to_holding(self, make_opinion_with_holding):
        lotus = make_opinion_with_holding["lotus_majority"]
        oracle = make_opinion_with_holding["oracle_majority"]
        rule_from_lotus = lotus.holdings[0].inferred_from_exclusive[0].rule
        new_holding = oracle.holdings[0] + rule_from_lotus
        output_strings = (
            "the fact it is false that <the Java API> was copyrightable",
            "absence of the fact that <Borland International> "
            + "infringed the copyright in <the Java API>",
        )
        for output in new_holding.outputs:
            assert output.short_string in output_strings

    def test_add_exclusive_holding(self, make_opinion_with_holding):
        """
        The Rule will be interpreted as a Holding and will be added to
        one of the nonexclusive Holdings that can be inferred from the
        exclusive Holding.
        """
        feist = make_opinion_with_holding["feist_majority"]
        new_holding = feist.holdings[10] + feist.holdings[3]
        output_strings = (
            "the fact it is false that <Rural's telephone listings> were an original work",
            "absence of the fact that <Rural's telephone listings> were copyrightable",
        )
        for output in new_holding.outputs:
            assert output.short_string in output_strings


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

    def test_no_union_with_opinion(self, make_holding, make_opinion_with_holding):
        holding = make_holding["h1"]
        feist = make_opinion_with_holding["feist_majority"]
        with pytest.raises(TypeError):
            _ = holding | feist

    def test_union_with_rule(self, make_opinion_with_holding):
        feist = make_opinion_with_holding["feist_majority"]
        rule = feist.holdings[3].inferred_from_exclusive[0].rule
        new_holding = feist.holdings[10] | rule
        assert isinstance(new_holding, Holding)

    def test_no_union_with_an_undecided_holding(self, make_holding):
        left = make_holding["h1"].evolve("decided")
        right = make_holding["h1"]
        assert left | right is None

    def test_union_with_two_undecided_holdings(self, make_holding):
        narrow_undecided = make_holding["h2_ALL_MUST"].evolve("decided")
        broad_undecided = make_holding["h2"].evolve("decided")
        new = narrow_undecided | broad_undecided
        assert new == broad_undecided
        assert broad_undecided | narrow_undecided == broad_undecided

    def test_union_unrelated_undecided(self, make_holding):
        left = make_holding["h1"].evolve("decided")
        right = make_holding["h2"].evolve("decided")
        assert left | right is None
