"""
Tests of commands that appear in notebooks in
the notebooks/ directory
"""

import os

from anchorpoint.textselectors import TextQuoteSelector
from dotenv import load_dotenv
from legislice.mock_clients import JSONRepository
import pytest

from authorityspoke import Enactment
from authorityspoke.io.downloads import download_case
from authorityspoke.io.readers import read_decision
from authorityspoke.factors import ContextRegister
from authorityspoke.entities import Entity

load_dotenv()

CAP_API_KEY = os.getenv("CAP_API_KEY")


class TestIntroduction:

    """
    Tests of commands from the "Introduction to AuthoritySpoke" notebook
    """

    @pytest.mark.vcr
    def test_download_case(self):
        oracle_download = download_case(
            cite="750 F.3d 1339", full_case=True, api_key=CAP_API_KEY
        )
        oracle = read_decision(oracle_download)
        assert oracle.cites_to[0].cite == "527 F.3d 1318"

    def test_oracle_20_holdings(self, make_opinion_with_holding):
        assert len(make_opinion_with_holding["oracle_majority"].holdings) == 20

    def test_replace_generic_factor(self, make_opinion_with_holding):
        lotus_majority = make_opinion_with_holding["lotus_majority"]
        context = ContextRegister.from_lists(
            [
                Entity("Borland International"),
                Entity("the Lotus menu command hierarchy"),
            ],
            [Entity("Prana Film"), Entity("Dracula")],
        )
        nosferatu_rule = lotus_majority.holdings[0].new_context(context)
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

    @pytest.mark.vcr
    def test_evolve_rule_replacing_enactment(
        self, make_opinion_with_holding, make_response
    ):
        oracle = make_opinion_with_holding["oracle_majority"]
        usc = oracle.holdings[0].enactments[0].code
        works_of_authorship_selector = TextQuoteSelector(
            exact=(
                "Copyright protection subsists, in accordance with this title,"
                + " in original works of authorship"
            )
        )
        client = JSONRepository(responses=make_response)
        works_of_authorship_clause = client.read("/us/usc/t17/s102/a")
        works_of_authorship_clause.select(works_of_authorship_selector)
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

    def test_opinion_explain_contradiction(self, make_opinion_with_holding):
        """
        The notebook now uses Decisions instead of this.
        """
        oracle = make_opinion_with_holding["oracle_majority"]
        lotus = make_opinion_with_holding["lotus_majority"]
        explanation = lotus.holdings[6].explain_contradiction(oracle.holdings[10])
        expected = ContextRegister()
        expected.insert_pair(
            Entity("the Lotus menu command hierarchy"), Entity("the Java API")
        )
        assert explanation.context == expected
        assert "<the Lotus menu command hierarchy> is like <the Java API>" in str(
            explanation
        )
        assert "Entity(name='the Java API'" in repr(explanation)

    def test_decision_explain_contradiction(self, make_decision_with_holding):
        oracle = make_decision_with_holding["oracle"]
        lotus = make_decision_with_holding["lotus"]
        explanation = lotus.explain_contradiction(oracle)
        assert "<the Lotus menu command hierarchy> is like <the Java API>" in str(
            explanation
        )
        assert "the Fact it is false that <the Lotus" in str(explanation)

    def test_register_string(self, make_opinion_with_holding):
        oracle = make_opinion_with_holding["oracle_majority"]
        lotus = make_opinion_with_holding["lotus_majority"]
        explanation = lotus.holdings[6].explain_contradiction(oracle.holdings[10])
        string = "ContextRegister(<the Lotus menu command hierarchy> -> <the Java API>)"
        assert str(explanation.context) == string

    def test_specific_holding_contradiction(self, make_opinion_with_holding):
        """
        Check the specific Holdings that should be causing a
        contradiction to be found between the Opinions.
        """
        oracle = make_opinion_with_holding["oracle_majority"]
        lotus = make_opinion_with_holding["lotus_majority"]
        assert oracle.holdings[10].contradicts(lotus.holdings[6])

    def test_addition_some_to_some(self, make_opinion_with_holding):
        """
        Demonstrates that adding two SOME Holdings returns None,
        same as two SOME Rules.
        """

        oracle = make_opinion_with_holding["oracle_majority"]
        feist = make_opinion_with_holding["feist_majority"]
        listings_not_original = feist.holdings[10]
        original_not_copyrightable = oracle.holdings[0]
        assert listings_not_original + original_not_copyrightable is None

    def test_adding_holdings(self, make_opinion_with_holding):
        feist = make_opinion_with_holding["feist_majority"]
        listings_not_original = feist.holdings[10]
        unoriginal_not_copyrightable = feist.holdings[3]
        listings_not_copyrightable = (
            listings_not_original + unoriginal_not_copyrightable
        )
        not_copyrightable = unoriginal_not_copyrightable.outputs[0]
        assert listings_not_copyrightable.outputs[1].short_string == (
            "absence of the fact that <Rural's telephone"
            " listings> were copyrightable"
        )
        assert (
            "act that <Rural's telephone listings> were names, towns, "
            + "and telephone numbers of telephone subscribers"
        ) in listings_not_copyrightable.inputs[0].short_string

    def test_union_holdings_from_different_cases(self, make_opinion_with_holding):
        oracle = make_opinion_with_holding["oracle_majority"]
        feist = make_opinion_with_holding["feist_majority"]
        new = oracle.holdings[1] | feist.holdings[2]
        assert "it is false that <the Java API> was copyrightable" in str(new)
        assert "<the Java API> was an original work" in str(new)


class TestCreateHoldingData:
    def test_holding_has_name_param(self, make_opinion_with_holding):
        """
        If this needs to change, be sure to update the notebook too.
        """
        oracle = make_opinion_with_holding["oracle_majority"]
        assert oracle.holdings[0].enactments[0].name == "copyright protection provision"
