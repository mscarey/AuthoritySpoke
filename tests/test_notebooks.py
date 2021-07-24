"""
Tests of commands that appear in notebooks in
the notebooks/ directory
"""
from copy import deepcopy
import os

from dotenv import load_dotenv
import pytest

from authorityspoke.facts import Fact
from authorityspoke.io.downloads import CAPClient

from authorityspoke import Entity, Predicate, Comparison

load_dotenv()

CAP_API_KEY = os.getenv("CAP_API_KEY") or "wrong key"


class TestIntroduction:

    """
    Tests of commands from the "Introduction to AuthoritySpoke" notebook
    """

    client = CAPClient(api_token=CAP_API_KEY)

    @pytest.mark.vcr
    def test_download_case(self):
        oracle = self.client.read_cite(cite="750 F.3d 1339", full_case=True)
        citations = [out_citation.cite for out_citation in oracle.cites_to]
        assert "527 F.3d 1318" in citations

    def test_oracle_20_holdings(self, make_opinion_with_holding):
        assert len(make_opinion_with_holding["oracle_majority"].holdings) == 20

    def test_replace_generic_factor(self, make_opinion_with_holding):
        lotus_majority = make_opinion_with_holding["lotus_majority"]

        seinfeld_holding = lotus_majority.holdings[0].new_context(
            terms_to_replace=[
                Entity("Borland International"),
                Entity("the Lotus menu command hierarchy"),
            ],
            changes=[Entity("Carol Publishing Group"), Entity("Seinfeld")],
        )

        assert lotus_majority.holdings[0] != seinfeld_holding
        assert lotus_majority.holdings[0].means(seinfeld_holding)

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

    def test_change_rule_replacing_enactment(
        self, fake_usc_client, make_opinion_with_holding
    ):
        oracle = make_opinion_with_holding["oracle_majority"]

        works_of_authorship_passage = (
            "Copyright protection subsists, in accordance with this title, "
            + "in original works of authorship"
        )

        works_of_authorship_clause = fake_usc_client.read("/us/usc/t17/s102/a")
        works_of_authorship_clause.select(works_of_authorship_passage)
        holding_with_shorter_enactment = deepcopy(oracle.holdings[0])
        holding_with_shorter_enactment.set_enactments(works_of_authorship_clause)

        assert holding_with_shorter_enactment >= oracle.holdings[0]
        assert not oracle.holdings[0] >= holding_with_shorter_enactment

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
        assert (
            explanation.context["<the Lotus menu command hierarchy>"].name
            == "the Java API"
        )
        assert "<the Lotus menu command hierarchy> is like <the Java API>" in str(
            explanation
        )
        assert "Entity(name='the Java API'" in repr(explanation)

    def test_decision_explain_contradiction(self, make_decision_with_holding):
        oracle = make_decision_with_holding["oracle"]
        lotus = make_decision_with_holding["lotus"]
        explanation = lotus.explain_contradiction(oracle)
        lotus_like = "<the Lotus menu command hierarchy> is like <the Java API>"
        java_like = "<the Java API> is like <the Lotus menu command hierarchy>"
        assert lotus_like in str(explanation) or java_like in str(explanation)
        assert (
            "the Fact it was false that <the Lotus".lower() in str(explanation).lower()
        )

    def test_register_string(self, make_opinion_with_holding):
        oracle = make_opinion_with_holding["oracle_majority"]
        lotus = make_opinion_with_holding["lotus_majority"]
        explanation = lotus.holdings[6].explain_contradiction(oracle.holdings[10])
        string = (
            "ContextRegister(<the Lotus menu command hierarchy> is like <the Java API>)"
        )
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
        assert "it was false that <the Java API> was copyrightable" in str(new)
        assert "<the Java API> was an original work" in str(new)

    def test_only_one_explanation_for_contradiction(self, make_opinion_with_holding):
        lotus = make_opinion_with_holding["lotus_majority"]
        oracle = make_opinion_with_holding["oracle_majority"]

        gen = lotus.holdings[6].explanations_contradiction(oracle.holdings[10])
        first_explanation = next(gen)

        with pytest.raises(StopIteration):
            second_explanation = next(gen)


class TestTemplateStrings:
    """Tests from the notebook introducing template strings."""

    def test_no_line_break_in_fact_string(self):
        elaine = Entity("Elaine", generic=True)
        tax_rate_over_25 = Comparison(
            "${taxpayer}'s marginal income tax rate was", sign=">", expression=0.25
        )
        elaine_tax_rate = Fact(tax_rate_over_25, terms=elaine)
        assert "\n" not in str(elaine_tax_rate)

    def test_changing_order_of_concrete_terms_changes_meaning(self):
        ann = Entity("Ann", generic=False)
        bob = Entity("Bob", generic=False)
        parent_sentence = Predicate("$mother was ${child}'s parent")
        ann_parent = Fact(parent_sentence, terms=(ann, bob))
        bob_parent = Fact(parent_sentence, terms=(bob, ann))
        assert str(ann_parent).lower() == "the fact that Ann was Bob's parent".lower()
        assert str(bob_parent).lower() == "the fact that Bob was Ann's parent".lower()
        assert not ann_parent.means(bob_parent)
