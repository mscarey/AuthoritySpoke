"""Tests for any commands in readme.md."""

from dotenv import load_dotenv

from authorityspoke.decisions import DecisionReading
from authorityspoke.examples import lotus as lotus_example
from authorityspoke.examples import oracle as oracle_example
from authorityspoke.examples.lotus import anchored_holdings as lotus_holdings
from authorityspoke.examples.oracle import anchored_holdings as oracle_holdings

load_dotenv()


class TestReadme:
    def test_posit_anchored_holdings(self, make_decision):
        oracle = make_decision["oracle"]
        lotus = make_decision["lotus"]

        oracle_ah = oracle_holdings()
        lotus_ah = lotus_holdings()

        oracle_reading = DecisionReading(decision=oracle)
        lotus_reading = DecisionReading(decision=lotus)

        oracle_reading.posit(
            holdings=oracle_ah.holdings,
            named_anchors=oracle_ah.named_anchors,
            enactment_anchors=oracle_ah.enactment_anchors,
        )
        lotus_reading.posit(
            holdings=lotus_ah.holdings,
            named_anchors=lotus_ah.named_anchors,
            enactment_anchors=lotus_ah.enactment_anchors,
        )

        assert lotus_reading.contradicts(oracle_reading)

    def test_posit_holdings(self, make_decision):
        oracle = make_decision["oracle"]
        lotus = make_decision["lotus"]

        oracle_h = oracle_example.HOLDINGS
        lotus_h = lotus_example.HOLDINGS

        oracle_reading = DecisionReading(decision=oracle)
        lotus_reading = DecisionReading(decision=lotus)

        oracle_reading.posit(holdings=oracle_h)
        lotus_reading.posit(holdings=lotus_h)

        assert lotus_reading.contradicts(oracle_reading)

    def test_explain_contradiction(self, make_decision_with_holding):
        lotus = make_decision_with_holding["lotus"]
        oracle = make_decision_with_holding["oracle"]
        explanation = str(lotus.explain_contradiction(oracle))
        lotus_like = "<the Lotus menu command hierarchy> is like <the Java API>"
        java_like = "<the Java API> is like <the Lotus menu command hierarchy>"
        assert lotus_like in explanation or java_like in explanation
