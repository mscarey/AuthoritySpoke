import pytest

from anchorpoint.textselectors import TextQuoteSelector

from authorityspoke.entities import Entity
from authorityspoke.factors import FactorIndex
from authorityspoke.facts import Fact, Predicate
from authorityspoke.holdings import HoldingGroup
from authorityspoke.io import loaders, readers
from authorityspoke.io.downloads import FakeClient
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
        assert make_entity["watt"] in make_opinion["watt_majority"].generic_factors()

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
            "generally" in anchor.exact for anchor in feist.holdings[1].factor_anchors()
        )

    def test_opinion_factor_text_anchor(self, make_opinion_with_holding):
        feist = make_opinion_with_holding["feist_majority"]
        factor_anchors = feist.holdings[0].factor_anchors()
        assert all(
            "No one may claim originality" not in anchor.exact
            for anchor in factor_anchors
        )
        assert any("as to facts" in anchor.exact for anchor in factor_anchors)

    def test_select_opinion_text_for_factor(self, make_opinion_with_holding):
        oracle = make_opinion_with_holding["oracle_majority"]
        factor = oracle.holdings[0].outputs[0]
        anchor = factor.anchors[0]
        selected = oracle.select_text(selector=anchor)
        assert selected == "copyright protection."

    def test_select_opinion_text_for_enactment(self, make_opinion_with_holding):
        oracle = make_opinion_with_holding["oracle_majority"]
        enactment = oracle.holdings[0].enactments[0]
        anchor = enactment.anchors[0]
        selected = oracle.select_text(selector=anchor)
        assert selected == "17 U.S.C. § 102(a)"

    def test_select_opinion_text_for_holding(self, make_opinion_with_holding):
        oracle = make_opinion_with_holding["oracle_majority"]
        holding = oracle.holdings[0]
        anchor = holding.anchors[0]
        selected = oracle.select_text(selector=anchor)
        assert selected == "must be “original” to qualify"

    def test_invalid_text_selector(self, make_opinion_with_holding):
        oracle = make_opinion_with_holding["oracle_majority"]
        anchor = TextQuoteSelector(exact="text not in opinion")
        with pytest.raises(ValueError):
            _ = oracle.select_text(selector=anchor)


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

    def test_new_context_wrong_number_of_changes(self, make_opinion, make_holding):
        """
        The context here (a Factor outside an iterable) only changes the first
        generic factor of the Rule being posited, which may not be what the user
        expects.
        """
        brad = make_opinion["brad_majority"]
        with pytest.raises(ValueError):
            brad.posit(make_holding["h1"], context=Entity("House on Haunted Hill"))

    def test_new_context_naming_nonexistent_factor(self, make_opinion, make_holding):
        """
        The context here (a Factor outside an iterable) only changes the first
        generic factor of the Rule being posited, which may not be what the user
        expects.
        """
        brad = make_opinion["brad_majority"]
        brad.clear_holdings()
        with pytest.raises(ValueError):
            brad.posit(
                make_holding["h1"],
                context=(Entity("House on Haunted Hill"), "nonexistent factor"),
            )

    def test_new_context_creates_equal_rule(self, make_opinion, make_response):
        watt = make_opinion["watt_majority"]
        brad = make_opinion["brad_majority"]
        client = FakeClient(responses=make_response)

        watt.clear_holdings()
        watt_raw = loaders.load_holdings("holding_watt.json")
        watt.posit(readers.read_holdings(watt_raw, client=client))

        brad.clear_holdings()
        brad_raw = loaders.load_holdings("holding_brad.json")
        brad.posit(readers.read_holdings(brad_raw, client=client))

        context_pairs = {
            "proof of Bradley's guilt": "proof of Wattenburg's guilt",
            "Bradley": "Wattenburg",
            "officers' search of the yard": "officers' search of the stockpile",
            "Bradley's marijuana patch": "the stockpile of trees",
        }
        watt.posit(brad.holdings[0], context_pairs)
        assert watt.holdings[-1].means(brad.holdings[0])

    def test_getting_factors_from_opinion(self, make_opinion, make_response):
        client = FakeClient(responses=make_response)

        watt = make_opinion["watt_majority"]
        watt.clear_holdings()
        watt_raw = loaders.load_holdings("holding_watt.json")
        holdings_to_posit = readers.read_holdings(watt_raw, client=client)
        watt.posit(holdings_to_posit)
        factors = watt.factors_by_name()
        assert "proof of Wattenburg's guilt" in factors.keys()

    def test_new_context_inferring_factors_to_change(self, make_opinion, make_response):
        """
        This changes watt's holdings; may break tests below.
        """
        watt = make_opinion["watt_majority"]
        brad = make_opinion["brad_majority"]

        client = FakeClient(responses=make_response)

        watt.clear_holdings()
        watt_raw = loaders.load_holdings("holding_watt.json")
        watt.posit(readers.read_holdings(watt_raw, client=client))

        brad.clear_holdings()
        brad_raw = loaders.load_holdings("holding_brad.json")
        brad.posit(readers.read_holdings(brad_raw, client=client))

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
            for factor in oracle.factors()
            if isinstance(factor, Fact)
            and factor.short_string
            == "the fact that <the Java API> was a scene a faire"
        ]
        assert len(scenes_a_faire) == 1  # 1 Factor

    def test_insert_duplicate_anchor_in_factor_index(self):
        api = Entity(name="the Java API", generic=True, plural=False, anchors=[])
        anchor = TextQuoteSelector(
            exact="it possesses at least some minimal degree of creativity."
        )
        fact = Fact(
            predicate=Predicate(
                "$product possessed at least some minimal degree of creativity"
            ),
            terms=[api],
            anchors=[anchor],
        )
        name = "the Java API possessed at least some minimal degree of creativity"

        factor_index = FactorIndex({name: fact})
        factor_index.insert(key=name, value=fact)
        assert len(factor_index[name].anchors) == 1

    def test_duplicate_text_in_factor_anchors(self, make_opinion_with_holding):
        """
        Test that all of the text anchors for a particular Factor appear only once.
        """

        oracle = make_opinion_with_holding["oracle_majority"]
        factors = oracle.factors()
        assert len(factors[0].anchors) == 2
        assert factors[0].anchors[0] != factors[0].anchors[1]

    def test_get_factor_from_opinion(self, make_opinion_with_holding):
        oracle = make_opinion_with_holding["oracle_majority"]
        company = oracle.get_factor_by_name("the Java API")
        assert isinstance(company, Entity)


class TestImplication:
    def test_no_implication(self, make_opinion_with_holding):
        watt = make_opinion_with_holding["watt_majority"]
        brad = make_opinion_with_holding["brad_majority"]
        assert not watt >= brad

    def test_posit_list_of_holdings_and_imply(self, make_opinion, make_response):
        watt = make_opinion["watt_majority"]
        brad = make_opinion["brad_majority"]
        client = FakeClient(responses=make_response)
        some_rules_raw = loaders.load_holdings(filename="holding_watt.json")
        some_rules = readers.read_holdings(some_rules_raw, client=client)
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

    def test_opinion_implied_by_rule(self, make_opinion, make_holding, make_rule):
        watt = make_opinion["oracle_majority"]
        watt.clear_holdings()
        watt.posit(make_holding["h2"])
        assert watt.implied_by(make_rule["h2_despite_due_process"])
        assert not watt.implies(make_rule["h2_despite_due_process"])

    def test_opinion_implies_holding_group(self, make_opinion_with_holding):
        watt = make_opinion_with_holding["watt_majority"]
        holdings = watt.holdings[:2]
        assert isinstance(holdings, HoldingGroup)
        assert watt.implies(holdings)


class TestContradiction:
    def test_contradiction_of_holding(
        self, make_opinion_with_holding, e_search_clause, make_holding
    ):
        assert make_opinion_with_holding["watt_majority"].contradicts(
            make_holding["h2_output_false_ALL_MUST"] + e_search_clause
        )

    def test_explain_opinion_contradicting_holding(self, make_opinion_with_holding):
        oracle = make_opinion_with_holding["oracle_majority"]
        lotus = make_opinion_with_holding["lotus_majority"]
        explanation = oracle.explain_contradiction(lotus.holdings[6])
        assert (
            "<the java api> is like <the lotus menu command hierarchy>"
            in str(explanation).lower()
        )

    def test_explain_opinion_contradicting_rule(self, make_opinion_with_holding):
        oracle = make_opinion_with_holding["oracle_majority"]
        lotus = make_opinion_with_holding["lotus_majority"]
        explanation = oracle.explain_contradiction(lotus.holdings[6].rule)
        assert (
            "<the java api> is like <the lotus menu command hierarchy>"
            in str(explanation).lower()
        )

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
        assert "contradicts" in str(explanation).lower()

    def test_error_contradiction_with_procedure(self, make_opinion, make_procedure):
        assert not make_opinion["watt_majority"].contradicts(make_procedure["c1"])
