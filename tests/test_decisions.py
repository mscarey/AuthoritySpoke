import pytest


class TestDecision:
    def test_decision_string(self, make_decision):
        decision = make_decision["cardenas"]
        assert str(decision) == "People v. Cardenas, 31 Cal. 3d 897 (1982-07-08)"

    def test_posit_holdings(self, make_decision, make_holding):
        """
        "Positing" Holdings causes the Holdings to be assigned to the Decision's
        majority Opinion.
        """

        watt = make_decision["watt"]
        watt.posit([make_holding["h1"], make_holding["h2"]])
        assert watt.majority.holdings[-1] == make_holding["h2"]


class TestImplication:
    def test_implication_of_decision_with_one_of_same_holdings(
        self, make_decision, make_decision_with_holding
    ):
        oracle = make_decision["oracle"]
        oracle_with_holdings = make_decision_with_holding["oracle"]
        oracle.posit(oracle_with_holdings.holdings[0])
        assert len(oracle.holdings) == 1
        assert len(oracle_with_holdings.holdings) > 10
        assert oracle_with_holdings >= oracle

    def test_opinion_implied_by_holding(self, make_decision, make_holding):
        opinion = make_decision["watt"]
        holding = make_holding["h1"]
        opinion.posit(holding)
        assert opinion.implied_by(holding)

    # @pytest.mark.skip(reason="slow")
    def test_decision_implies_its_opinion(self, make_decision_with_holding):
        cardenas = make_decision_with_holding["cardenas"]
        assert cardenas >= cardenas.majority

    # @pytest.mark.skip(reason="slow")
    def test_opinion_implies_its_decision(self, make_decision_with_holding):
        cardenas = make_decision_with_holding["cardenas"]
        assert cardenas.implied_by(cardenas.majority)


class TestContradiction:
    def test_oracle_contradicts_lotus(self, make_decision_with_holding):
        """
        This is the same example from the "Introduction" notebook.
        """
        oracle = make_decision_with_holding["oracle"]
        lotus = make_decision_with_holding["lotus"]
        assert oracle.contradicts(lotus)

    def test_no_contradiction_explanations(self, make_decision_with_holding):
        oracle = make_decision_with_holding["oracle"]
        feist = make_decision_with_holding["feist"]
        explanation = oracle.explain_contradiction(feist)
        assert explanation is None
