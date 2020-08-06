"""Tests for any commands in readme.md."""

from legislice.download import JSONRepository

from authorityspoke.io.loaders import load_and_read_code
from authorityspoke.io.loaders import load_and_read_decision
from authorityspoke.io.loaders import load_and_read_holdings

from authorityspoke import Regime


class TestReadme:
    def test_posit_holdings(self, make_response):
        client = JSONRepository(responses=make_response)

        oracle = load_and_read_decision("oracle_h.json").majority
        lotus = load_and_read_decision("lotus_h.json").majority

        oracle.posit(load_and_read_holdings("holding_oracle.json", client=client))
        lotus.posit(load_and_read_holdings("holding_lotus.json", client=client))

        assert lotus.contradicts(oracle)

    def test_explain_contradiction(self, make_decision_with_holding):
        lotus = make_decision_with_holding["lotus"]
        oracle = make_decision_with_holding["oracle"]
        explanation = str(lotus.explain_contradiction(oracle))
        assert (
            "<the Lotus menu command hierarchy> is like <the Java API>" in explanation
        )
