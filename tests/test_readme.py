"""Tests for any commands in readme.md."""

from authorityspoke.io.downloads import FakeClient

from authorityspoke.io.loaders import load_and_read_decision, load_holdings_with_anchors
from authorityspoke.io.loaders import load_and_read_holdings


class TestReadme:
    def test_posit_holdings(self, make_response):
        client = FakeClient(responses=make_response)

        oracle = load_and_read_decision("oracle_h.json").majority
        lotus = load_and_read_decision("lotus_h.json").majority

        (
            oracle_holdings,
            oracle_anchors,
            oracle_named_anchors,
        ) = load_holdings_with_anchors("holding_oracle.json", client=client)
        lotus_holdings, lotus_anchors, lotus_named_anchors = load_holdings_with_anchors(
            "holding_lotus.json", client=client
        )

        oracle.posit(
            holdings=oracle_holdings,
            holding_anchors=oracle_anchors,
            named_anchors=oracle_named_anchors,
        )
        lotus.posit(
            holdings=lotus_holdings,
            holding_anchors=lotus_anchors,
            named_anchors=lotus_named_anchors,
        )

        assert lotus.contradicts(oracle)

    def test_explain_contradiction(self, make_decision_with_holding):
        lotus = make_decision_with_holding["lotus"]
        oracle = make_decision_with_holding["oracle"]
        explanation = str(lotus.explain_contradiction(oracle))
        assert (
            "<the Lotus menu command hierarchy> is like <the Java API>" in explanation
        )
