import pytest

from authorityspoke.entities import Entity
from authorityspoke.facts import Fact
from authorityspoke.io import anchors, loaders, readers
from authorityspoke.opinions import Opinion


class TestOpinions:
    def test_opinion_features(self, make_decision):
        assert make_decision["watt"].court == "9th-cir"
        assert make_decision["watt"].citations[0].cite == "388 F.2d 853"

    def test_repr(self, make_opinion):
        assert "HAMLEY, Circuit Judge" in repr(make_opinion["watt_majority"])

    def test_repr_excludes_text(self, make_opinion):
        """
        reprs would be way too long if they could contain the
        full opinion text.
        """
        assert "text" not in repr(make_opinion["watt_majority"])

    def test_opinion_author(self, make_opinion):
        assert make_opinion["watt_majority"].author == "HAMLEY, Circuit Judge"
        assert make_opinion["brad_majority"].author == "BURKE, J."
        assert (
            make_opinion["brad_concurring-in-part-and-dissenting-in-part"].author
            == "TOBRINER, J."
        )

    def test_opinion_holding_list(self, make_opinion, real_holding):
        watt = make_opinion["watt_majority"]
        h3_specific = real_holding["h3"]
        watt.posit(h3_specific)
        assert h3_specific in watt.holdings

    def test_opinion_entity_list(
        self, make_opinion, real_holding, make_entity, make_evidence
    ):
        watt = make_opinion["watt_majority"]
        h = real_holding
        e = make_entity

        watt.posit(h["h1"], context=(e["motel"], e["watt"]))
        watt.posit(h["h2"], context=(e["trees"], e["motel"]))
        watt.posit(
            h["h3"],
            context=(
                make_evidence["generic"],
                e["motel"],
                e["watt"],
                e["trees"],
                e["tree_search"],
            ),
        )
        watt.posit(
            h["h4"], context=(e["trees"], e["tree_search"], e["motel"], e["watt"])
        )
        assert make_entity["watt"] in make_opinion["watt_majority"].generic_factors

    def test_opinion_date(self, make_decision):
        """
        This no longer tests whether two Opinions from the same Decision
        have the same date, because the date field has been moved to the
        Decision class.
        """
        assert make_decision["watt"].date < make_decision["brad"].date

    def test_opinion_string(self, make_opinion):
        opinion = make_opinion["cardenas_majority"]
        assert str(opinion).lower() == "majority opinion by bird, c. j."


class TestOpinionText:
    def test_opinion_text(self, make_opinion):
        assert (
            "Feist responded that such efforts were economically "
            + "impractical and, in any event, unnecessary"
        ) in make_opinion["feist_majority"].text

    def test_opinion_text_anchor(self, make_opinion_with_holding):
        feist = make_opinion_with_holding["feist_majority"]
        assert any(
            "generally" in anchor.exact
            for anchor in feist.get_anchors(feist.holdings[1])
        )

    def test_opinion_factor_text_anchor(self, make_opinion_with_holding):
        feist = make_opinion_with_holding["feist_majority"]
        anchors = feist.get_anchors(feist.holdings[0])
        assert all(
            "No one may claim originality" not in anchor.exact for anchor in anchors
        )
        assert any("as to facts" in anchor.exact for anchor in anchors)

    def test_select_opinion_text_for_factor(self, make_opinion_with_holding):
        oracle = make_opinion_with_holding["oracle_majority"]
        factor = oracle.holdings[0].outputs[0]
        anchor = oracle.factors[factor][0]
        selected = oracle.select_text(selector=anchor)
        assert selected == "copyright protection."

    def test_select_opinion_text_for_enactment(self, make_opinion_with_holding):
        oracle = make_opinion_with_holding["oracle_majority"]
        enactment = oracle.holdings[0].enactments[0]
        anchor = oracle.factors[enactment][0]
        selected = oracle.select_text(selector=anchor)
        assert selected == "17 U.S.C. § 102(a)"

    def test_select_opinion_text_for_holding(self, make_opinion_with_holding):
        oracle = make_opinion_with_holding["oracle_majority"]
        holding = oracle.holdings[0]
        anchor = oracle.holding_anchors[holding][0]
        selected = oracle.select_text(selector=anchor)
        assert selected == "must be “original” to qualify"


class TestOpinionHoldings:
    def test_positing_non_rule_error(self, make_opinion, make_procedure):
        with pytest.raises(TypeError):
            make_opinion["watt_majority"].posit(make_procedure["c1"])

    def test_error_posit_with_no_rule_source(self, make_opinion):
        with pytest.raises(TypeError):
            make_opinion["watt_majority"].posit()

    def test_posit_rule(self, make_opinion, make_rule, make_holding):
        """
        "Positing" a Rule causes the Rule to be converted to a Holding first.
        So the Opinion implies the corresponding Holding.
        """

        watt = make_opinion["watt_majority"]
        watt.posit(make_rule["h1"])
        assert watt.implies(make_holding["h1"])

    def test_new_context_non_iterable_changes(self, make_opinion, make_holding):
        """
        The context here (a Factor outside an iterable) only changes the first
        generic factor of the Rule being posited, which may not be what the user
        expects.
        """
        brad = make_opinion["brad_majority"]
        brad.posit(make_holding["h1"], context=Entity("House on Haunted Hill"))
        assert "Haunted Hill" in str(brad.holdings[0])

    def test_new_context_naming_nonexistent_factor(self, make_opinion, make_holding):
        """
        The context here (a Factor outside an iterable) only changes the first
        generic factor of the Rule being posited, which may not be what the user
        expects.
        """
        brad = make_opinion["brad_majority"]
        with pytest.raises(ValueError):
            brad.posit(
                make_holding["h1"],
                context=(Entity("House on Haunted Hill"), "nonexistent factor"),
            )

    def test_new_context_creates_equal_rule(self, make_opinion, make_regime):
        watt = make_opinion["watt_majority"]
        brad = make_opinion["brad_majority"]

        watt.clear_holdings()
        watt_raw = loaders.load_holdings("holding_watt.json")
        watt.posit(readers.read_holdings(watt_raw, regime=make_regime))

        brad.clear_holdings()
        brad_raw = loaders.load_holdings("holding_brad.json")
        brad.posit(readers.read_holdings(brad_raw, regime=make_regime))

        context_pairs = {
            "proof of Bradley's guilt": "proof of Wattenburg's guilt",
            "Bradley": "Wattenburg",
            "officers' search of the yard": "officers' search of the stockpile",
            "Bradley's marijuana patch": "the stockpile of trees",
        }
        watt.posit(brad.holdings[0], context_pairs)
        assert watt.holdings[-1].means(brad.holdings[0])

    def test_new_context_inferring_factors_to_change(self, make_opinion, make_regime):
        """
        This changes watt's holdings; may break tests below.
        """

        watt = make_opinion["watt_majority"]
        brad = make_opinion["brad_majority"]

        watt.clear_holdings()
        watt_raw = loaders.load_holdings("holding_watt.json")
        watt.posit(readers.read_holdings(watt_raw, regime=make_regime))

        brad.clear_holdings()
        brad_raw = loaders.load_holdings("holding_brad.json")
        brad.posit(readers.read_holdings(brad_raw, regime=make_regime))

        context_items = [
            "proof of Wattenburg's guilt",
            "Wattenburg",
            "officers' search of the stockpile",
            "Hideaway Lodge",
            "the stockpile of trees",
        ]
        watt.posit(brad.holdings[0], context=context_items)
        assert watt.holdings[-1].means(brad.holdings[0])


class TestOpinionFactors:
    def test_only_one_factor_with_same_content(self, make_opinion_with_holding):
        """
        Tests that a particular Factor appears only once, and that all
        three of the text anchors for that Factor appear in the value
        for the Factor in Opinion.factors.
        """

        oracle = make_opinion_with_holding["oracle_majority"]
        scenes_a_faire = [
            factor
            for factor in oracle.factors.items()
            if isinstance(factor[0], Fact)
            and factor[0].short_string
            == "the fact that <the Java API> was a scene a faire"
        ]
        assert len(scenes_a_faire) == 1  # 1 Factor
        assert len(scenes_a_faire[0][1]) == 3


class TestImplication:
    def test_no_implication(self, make_opinion_with_holding):
        watt = make_opinion_with_holding["watt_majority"]
        brad = make_opinion_with_holding["brad_majority"]
        assert not watt >= brad

    def test_posit_list_of_holdings_and_imply(self, make_opinion, make_regime):
        watt = make_opinion["watt_majority"]
        brad = make_opinion["brad_majority"]
        some_rules_raw = loaders.load_holdings(filename="holding_watt.json")
        some_rules = readers.read_holdings(some_rules_raw, regime=make_regime)
        for case in (watt, brad):
            case.clear_holdings()
            case.posit(some_rules[:3])
        watt.posit(some_rules[3])
        assert watt > brad
        assert not brad >= watt

    def test_opinion_implies_holding(self, make_opinion, make_holding):
        watt = make_opinion["watt_majority"]
        watt.posit(make_holding["h2_invalid_undecided"])
        assert watt >= make_holding["h2_undecided"]
        assert watt > make_holding["h2_undecided"]

    def test_opinion_does_not_imply_holding(self, make_opinion, make_holding):
        watt = make_opinion["watt_majority"]
        watt.clear_holdings()
        watt.posit(make_holding["h2_irrelevant_inputs_undecided"])
        assert not watt >= make_holding["h2_undecided"]
        assert not watt > make_holding["h2_undecided"]


class TestContradiction:
    def test_contradiction_of_holding(
        self, make_opinion_with_holding, make_enactment, make_holding
    ):
        assert make_opinion_with_holding["watt_majority"].contradicts(
            make_holding["h2_output_false_ALL_MUST"] + make_enactment["search_clause"]
        )

    def test_explain_opinion_contradicting_holding(self, make_opinion_with_holding):
        oracle = make_opinion_with_holding["oracle_majority"]
        lotus = make_opinion_with_holding["lotus_majority"]
        explanation = oracle.explain_contradiction(lotus.holdings[6])
        assert "an explanation" in str(explanation).lower()

    def test_contradiction_of_decision(
        self, make_opinion_with_holding, make_decision_with_holding
    ):
        assert make_opinion_with_holding["oracle_majority"].contradicts(
            make_decision_with_holding["lotus"]
        )

    def test_explain_opinion_contradicting_decision(
        self, make_opinion_with_holding, make_decision_with_holding
    ):
        oracle_majority = make_opinion_with_holding["oracle_majority"]
        lotus = make_decision_with_holding["lotus"]
        explanation = oracle_majority.explain_contradiction(lotus)
        assert "an explanation" in str(explanation).lower()

    def test_error_contradiction_with_procedure(self, make_opinion, make_procedure):
        with pytest.raises(TypeError):
            make_opinion["watt_majority"].contradicts(make_procedure["c1"])
