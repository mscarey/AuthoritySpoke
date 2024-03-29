"""Tests for any commands in readme.md."""

from authorityspoke.decisions import DecisionReading
import os
from dotenv import load_dotenv

load_dotenv()

from authorityspoke import CAPClient, Decision, LegisClient
from authorityspoke.io.fake_enactments import FakeClient

from authorityspoke.io.loaders import (
    load_decision,
    read_holdings_from_file,
    read_anchored_holdings_from_file,
)
from authorityspoke.io.loaders import read_holdings_from_file


class TestReadme:
    def test_posit_anchored_holdings(self, make_response):
        client = FakeClient(responses=make_response)

        oracle_dict = load_decision("oracle_h.json")
        lotus_dict = load_decision("lotus_h.json")
        oracle = Decision(**oracle_dict)
        lotus = Decision(**lotus_dict)

        oracle_ah = read_anchored_holdings_from_file(
            "holding_oracle.yaml", client=client
        )
        lotus_ah = read_anchored_holdings_from_file("holding_lotus.yaml", client=client)

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

    def test_posit_holdings(self, make_response):
        client = FakeClient(responses=make_response)

        oracle_dict = load_decision("oracle_h.json")
        lotus_dict = load_decision("lotus_h.json")
        oracle = Decision(**oracle_dict)
        lotus = Decision(**lotus_dict)

        oracle_h = read_holdings_from_file("holding_oracle.yaml", client=client)
        lotus_h = read_holdings_from_file("holding_lotus.yaml", client=client)

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
