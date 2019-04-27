"""
Tests of commands that appear in notebooks in
the notebooks/ directory
"""

from authorityspoke import Enactment, Entity

class TestIntroduction:

    """
    Tests of commands from the "Introduction to AuthoritySpoke" notebook
    """

    def test_oracle_21_holdings(self, make_opinion_with_holding):
        assert len(make_opinion_with_holding["oracle_majority"].holdings) == 21

    def test_replace_generic_factor(self, make_opinion_with_holding):
        oracle = make_opinion_with_holding["oracle_majority"]
        nosferatu_rule = oracle.holdings[0].new_context(
            {Entity('the Java API'): Entity('Nosferatu')}
        )
        assert oracle.holdings[0] == nosferatu_rule

    def test_evolve_rule_replacing_enactment(self, make_opinion_with_holding):
        oracle = make_opinion_with_holding["oracle_majority"]
        usc = oracle.holdings[0].enactments[0].code
        works_of_authorship_clause = Enactment(
            code=usc,
            section=102,
            subsection="a",
            end="works of authorship"
            )
        rule_with_shorter_enactment = oracle.holdings[0].evolve(
            {"enactments": works_of_authorship_clause}
        )
        assert rule_with_shorter_enactment >= oracle.holdings[0]
        assert not oracle.holdings[0] >= rule_with_shorter_enactment
