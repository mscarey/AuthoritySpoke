"""
Tests of commands that appear in notebooks in
the notebooks/ directory
"""

from authorityspoke import Entity

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