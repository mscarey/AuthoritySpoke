"""Tests for any commands in readme.md."""

from authorityspoke.decisions import DecisionReading
import os
from dotenv import load_dotenv

load_dotenv()

from authorityspoke import CAPClient, Decision
from authorityspoke.io.fake_enactments import FakeClient

from authorityspoke.io.loaders import (
    load_decision,
    read_anchored_holdings_from_file,
)
from authorityspoke.io.loaders import read_holdings_from_file


class TestReadme:
    def test_posit_holdings(self, make_response):
        client = FakeClient(responses=make_response)

        oracle_dict = load_decision("oracle_h.json")
        lotus_dict = load_decision("lotus_h.json")
        oracle = Decision(**oracle_dict)
        lotus = Decision(**lotus_dict)

        (
            oracle_holdings,
            oracle_anchors,
            oracle_named_anchors,
            oracle_e,
        ) = read_anchored_holdings_from_file("holding_oracle.json", client=client)
        (
            lotus_holdings,
            lotus_anchors,
            lotus_named_anchors,
            lotus_e,
        ) = read_anchored_holdings_from_file("holding_lotus.json", client=client)

        oracle_reading = DecisionReading(oracle)
        lotus_reading = DecisionReading(lotus)

        oracle_reading.posit(
            holdings=oracle_holdings,
            holding_anchors=oracle_anchors,
            named_anchors=oracle_named_anchors,
            enactment_anchors=oracle_e,
        )
        lotus_reading.posit(
            holdings=lotus_holdings,
            holding_anchors=lotus_anchors,
            named_anchors=lotus_named_anchors,
            enactment_anchors=lotus_e,
        )

        assert lotus_reading.contradicts(oracle_reading)

    def test_explain_contradiction(self, make_decision_with_holding):
        lotus = make_decision_with_holding["lotus"]
        oracle = make_decision_with_holding["oracle"]
        explanation = str(lotus.explain_contradiction(oracle))
        lotus_like = "<the Lotus menu command hierarchy> is like <the Java API>"
        java_like = "<the Java API> is like <the Lotus menu command hierarchy>"
        assert lotus_like in explanation or java_like in explanation
