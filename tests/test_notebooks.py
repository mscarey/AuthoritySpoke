"""
Tests of commands that appear in notebooks in
the notebooks/ directory
"""

from authorityspoke import Enactment
from authorityspoke.entities import Entity
from authorityspoke.selectors import TextQuoteSelector


class TestIntroduction:

    """
    Tests of commands from the "Introduction to AuthoritySpoke" notebook
    """

    def test_oracle_20_holdings(self, make_opinion_with_holding):
        assert len(make_opinion_with_holding["oracle_majority"].holdings) == 20

    def test_replace_generic_factor(self, make_opinion_with_holding):
        lotus_majority = make_opinion_with_holding["lotus_majority"]
        nosferatu_rule = lotus_majority.holdings[0].new_context(
            {
                Entity("Borland International"): Entity("Prana Film"),
                Entity("the Lotus menu command hierarchy"): Entity("Dracula"),
            }
        )
        assert lotus_majority.holdings[0] != nosferatu_rule
        assert lotus_majority.holdings[0].means(nosferatu_rule)

    def test_inferred_holdings_after_exclusive_holding(self, make_opinion_with_holding):
        """
        Test that when a holding is marked "exclusive" in the JSON input,
        that holding is added first to the Opinion's set of holdings, and
        any other inferred holdings, about the absence of the output from
        the original holding, are added later.
        """
        lotus_majority = make_opinion_with_holding["lotus_majority"]
        assert lotus_majority.holdings[0].outputs[0].absent is False
        assert lotus_majority.holdings[1].outputs[0].absent is True

    def test_evolve_rule_replacing_enactment(
        self, make_regime, make_opinion_with_holding
    ):
        oracle = make_opinion_with_holding["oracle_majority"]
        usc = oracle.holdings[0].enactments[0].code
        works_of_authorship_selector = TextQuoteSelector(
            path="/us/usc/t17/s102/a",
            exact=(
                "Copyright protection subsists, in accordance with this title,"
                + " in original works of authorship"
            ),
        )
        works_of_authorship_clause = Enactment(
            selector=works_of_authorship_selector, regime=make_regime
        )
        rule_with_shorter_enactment = oracle.holdings[0].evolve(
            {"enactments": works_of_authorship_clause}
        )
        assert rule_with_shorter_enactment >= oracle.holdings[0]
        assert not oracle.holdings[0] >= rule_with_shorter_enactment

    def test_opinion_contradiction(self, make_opinion_with_holding):
        oracle = make_opinion_with_holding["oracle_majority"]
        lotus_majority = make_opinion_with_holding["lotus_majority"]
        assert oracle.contradicts(lotus_majority)
        assert lotus_majority.contradicts(oracle)

    def test_specific_holding_contradiction(self, make_opinion_with_holding):
        """
        Check the specific Holdings that should be causing a
        contradiction to be found between the Opinions.
        """
        oracle = make_opinion_with_holding["oracle_majority"]
        lotus = make_opinion_with_holding["lotus_majority"]
        assert oracle.holdings[10].contradicts(lotus.holdings[8])
