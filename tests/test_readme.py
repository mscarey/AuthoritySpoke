"""Tests for any commands in readme.md."""

from authorityspoke.io.loaders import load_and_read_code
from authorityspoke.io.loaders import load_and_read_decision
from authorityspoke.io.loaders import load_and_read_holdings

from authorityspoke import Regime


class TestReadme:
    def test_posit_holdings(self):

        oracle = load_and_read_decision("oracle_h.json").majority
        lotus = load_and_read_decision("lotus_h.json").majority

        usa = Regime()

        us_constitution = load_and_read_code("constitution.xml")
        usc_title_17 = load_and_read_code("usc17.xml")
        code_of_federal_regulations_title_37 = load_and_read_code("cfr37.xml")

        usa.set_code(us_constitution)
        usa.set_code(usc_title_17)
        usa.set_code(code_of_federal_regulations_title_37)

        oracle.posit(load_and_read_holdings("holding_oracle.json", regime=usa))
        lotus.posit(load_and_read_holdings("holding_lotus.json", regime=usa))

        assert lotus.contradicts(oracle)

    def test_explain_contradiction(self, make_decision_with_holding):
        lotus = make_decision_with_holding["lotus"]
        oracle = make_decision_with_holding["oracle"]
        explanation = str(lotus.explain_contradiction(oracle))
        assert (
            "<the Lotus menu command hierarchy> is like <the Java API>" in explanation
        )
