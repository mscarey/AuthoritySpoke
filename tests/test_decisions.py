from authorityspoke.holdings import HoldingGroup
from authorityspoke.opinions import OpinionReading
from copy import deepcopy
from datetime import date
import datetime
import os

import pytest

from authorityspoke.decisions import Decision, DecisionReading, Opinion
from authorityspoke.io.loaders import read_anchored_holdings_from_file


class TestDecision:
    def test_decision_string(self, make_decision):
        decision = make_decision["cardenas"]
        assert str(decision) == "People v. Cardenas, 31 Cal. 3d 897 (1982-07-08)"

    def test_decision_no_opinions(self):
        decision = Decision(decision_date=date(2000, 2, 2))
        reading = DecisionReading(decision=decision)
        assert reading.majority is None
        assert not reading.implied_by(None)

    def test_decision_reading_with_opinion_instead_of_decision(self, make_opinion):
        with pytest.raises(TypeError):
            DecisionReading(decision=make_opinion["lotus_majority"])

    def test_posit_holdings(self, make_decision, make_holding):
        """
        "Positing" Holdings causes the Holdings to be assigned to the Decision's
        majority Opinion.
        """

        watt = make_decision["watt"]
        reading = DecisionReading(decision=watt)
        reading.posit([make_holding["h1"], make_holding["h2"]])
        assert reading.majority.holdings[-1] == make_holding["h2"]

    def test_make_reading_with_holdings(self, make_decision, make_holding):
        watt = make_decision["watt"]
        holdings = HoldingGroup([make_holding["h1"], make_holding["h2"]])
        reading = DecisionReading(decision=watt, holdings=holdings)
        assert reading.majority.holdings[-1] == make_holding["h2"]

    def test_make_reading_with_anchored_holdings(
        self, make_decision, make_anchored_holding
    ):
        watt = make_decision["watt"]
        holding = make_anchored_holding["lotus"]
        reading = DecisionReading(decision=watt, holdings=holding)
        assert (
            str(reading.majority.holdings[0].inputs[0]).lower()
            == "the fact that <the lotus menu command hierarchy> was copyrightable"
        )
        assert reading.majority.opinion_author.startswith("HAMLEY")
        assert reading.decision.opinions[0].author.startswith("HAMLEY")

    def test_need_reading_to_posit_holding(self, make_holding):
        decision = Decision(decision_date=(datetime.date(1900, 1, 1)))
        with pytest.raises(AttributeError):
            decision.posit(make_holding["h1"])

    def test_decision_reading_has_opinion_readings(self, make_decision, make_holding):
        watt = make_decision["watt"]
        reading = DecisionReading(decision=watt)
        reading.posit(make_holding["h1"])
        hamley = "hamley, circuit judge"
        assert reading.opinion_readings[0].opinion_author.lower() == hamley
        assert reading.opinion_readings[0].holdings[0].means(make_holding["h1"])

    def test_decision_posits_holding(self, fake_usc_client, make_decision):
        lotus_analysis = read_anchored_holdings_from_file(
            "holding_lotus.yaml", client=fake_usc_client
        )
        lotus_reading = DecisionReading(decision=make_decision["lotus"])
        lotus_reading.posit(lotus_analysis)
        assert len(lotus_reading.majority.holdings) == len(lotus_analysis.holdings)
        assert str(lotus_reading).startswith("Reading for Lotus Development Corp.")

    def test_decision_with_opinion_reading_posits_holding(self, fake_usc_client):
        lotus_analysis = read_anchored_holdings_from_file(
            "holding_lotus.yaml", client=fake_usc_client
        )
        decision_reading = DecisionReading(
            decision=Decision(decision_date=date(2000, 2, 2)),
            opinion_readings=[OpinionReading(opinion_type="plurality")],
        )
        decision_reading.posit(lotus_analysis)
        assert len(decision_reading.holdings) == len(lotus_analysis.holdings)

    def test_error_decision_with_no_majority_posits_holding(self, fake_usc_client):
        lotus_analysis = read_anchored_holdings_from_file(
            "holding_lotus.yaml", client=fake_usc_client
        )
        reading1 = OpinionReading(opinion_type="plurality")
        reading2 = OpinionReading(opinion_type="concurring")
        decision_reading = DecisionReading(
            decision=Decision(decision_date=date(2000, 2, 2)),
            opinion_readings=[reading1, reading2],
        )
        with pytest.raises(AttributeError):
            decision_reading.posit(lotus_analysis)


class TestImplication:
    def test_implication_of_decision_with_one_of_same_holdings(
        self, make_decision, make_decision_with_holding
    ):
        decision = make_decision["oracle"]
        oracle = DecisionReading(decision=decision)
        oracle_with_holdings = make_decision_with_holding["oracle"]
        oracle.posit(oracle_with_holdings.holdings[0])
        assert len(oracle.holdings) == 1
        assert len(oracle_with_holdings.holdings) > 10
        assert oracle_with_holdings >= oracle

    def test_decision_implied_by_holding(self, make_decision, make_holding):
        decision = make_decision["watt"]
        reading = DecisionReading(decision=decision)
        holding = make_holding["h1"]
        reading.posit(holding)
        assert reading.implied_by(holding)

    def test_decision_explain_implication(
        self, make_decision_with_holding, make_holding
    ):
        decision = make_decision_with_holding["watt"]
        holding = decision.holdings[0]
        explanation = decision.explain_implication(holding)
        assert explanation

    def test_decision_no_explanation_implication(self, make_decision_with_holding):
        watt = make_decision_with_holding["watt"]
        oracle = make_decision_with_holding["oracle"]
        explanation = watt.explain_implication(oracle)
        assert explanation is None

    def test_typeerror_to_compare_with_factor(
        self, make_decision_with_holding, make_factor
    ):
        watt = make_decision_with_holding["watt"]
        factor = make_factor["f_no_shooting"]
        with pytest.raises(TypeError):
            watt.explain_implication(factor)

    def test_decision_implies_decision_without_holdings(
        self, make_decision_with_holding, make_decision
    ):
        oracle = make_decision_with_holding["oracle"]
        blank = make_decision["lotus"]
        blank_reading = DecisionReading(decision=blank)
        explanation = oracle.explain_implication(blank_reading)
        assert not explanation.reasons

    def test_no_holdings_of_blank_decision(self):
        blank = Decision(decision_date=datetime.date(2000, 1, 2))
        reading = DecisionReading(decision=blank)
        assert len(reading.holdings) == 0

    # @pytest.mark.skip(reason="slow")
    def test_decision_implies_its_opinion(self, make_decision_with_holding):
        cardenas = make_decision_with_holding["cardenas"]
        assert cardenas >= cardenas.majority
        assert cardenas > cardenas.majority

    # @pytest.mark.skip(reason="slow")
    def test_opinion_implies_its_decision(self, make_decision_with_holding):
        cardenas = make_decision_with_holding["cardenas"]
        assert cardenas.implied_by(cardenas.majority)

    def test_decision_implies_holding_and_rule(self, make_decision_with_holding):
        """Adding a new input makes the new Holding less specific than the original one."""

        oracle = make_decision_with_holding["oracle"]
        holding = deepcopy(oracle.holdings[1])
        new_inputs = holding.inputs + [oracle.holdings[0].inputs[0]]
        holding.set_inputs(new_inputs)
        assert oracle.implies(holding)
        assert oracle.implies(holding.rule)

    def test_decision_does_not_imply_procedure(
        self, make_procedure, make_decision_with_holding
    ):
        oracle = make_decision_with_holding["oracle"]
        assert not oracle.implies(make_procedure["c1"])

    def test_opinion_implies_decision(self, make_decision_with_holding):
        watt = make_decision_with_holding["watt"]
        assert watt.opinion_readings[0].implies(watt)

    def test_rule_implied_by_decision(self, make_decision_with_holding):
        oracle = make_decision_with_holding["oracle"]
        explanation = oracle.explain_implication(oracle.holdings[0].rule)
        assert len(explanation.reasons) == 3

    def test_decision_not_implied_by_rule(self, make_decision_with_holding):
        oracle = make_decision_with_holding["oracle"]
        explanation = oracle.explain_implied_by(oracle.holdings[0].rule)
        assert explanation is None


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

    def test_cannot_check_contradiction_of_str(self, make_decision_with_holding):
        oracle = make_decision_with_holding["oracle"]
        feist = make_decision_with_holding["feist"]
        with pytest.raises(TypeError):
            oracle.explain_contradiction("feist")

    def test_no_contradiction_with_plurality(self, make_decision_with_holding):
        oracle = make_decision_with_holding["oracle"]
        other = Decision(
            decision_date=datetime.date(2020, 1, 1),
            opinions=[Opinion(position="plurality")],
        )
        reading = DecisionReading(decision=other)
        assert not oracle.contradicts(reading)

    def test_no_contradiction_of_majority_without_holdings(
        self, make_decision_with_holding
    ):
        oracle = make_decision_with_holding["oracle"]
        other = Decision(decision_date=datetime.date(2020, 1, 1))
        other.opinions.append(Opinion(position="majority"))
        reading = DecisionReading(decision=other)
        assert not oracle.contradicts(reading)

    def test_decision_contradicts_holding(self, make_decision_with_holding):
        oracle = make_decision_with_holding["oracle"]
        holding = oracle.holdings[0].negated()
        assert oracle.contradicts(holding)
