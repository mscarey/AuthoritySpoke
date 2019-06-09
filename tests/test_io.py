import json
import os
import pathlib

import pint
import pytest

from authorityspoke.context import get_directory_path
from authorityspoke.enactments import Code, Enactment
from authorityspoke.factors import Entity
from authorityspoke.factors import Factor, Fact
from authorityspoke.opinions import Opinion
from authorityspoke.predicates import Predicate
from authorityspoke.rules import Rule

ureg = pint.UnitRegistry()


class TestPredicateImport:
    """
    This tests a function for importing a Predicate by itself,
    but Predicate imports can also happen as part of a Fact import.
    """

    def test_import_predicate_with_quantity(self):
        story = Fact.from_string("Once there was a {king} who had {> 3} castles")
        assert len(story.predicate) == 1
        assert story.predicate.content.startswith("Once")
        assert story.predicate.comparison == ">"
        assert story.predicate.quantity == 3


class TestEntityImport:

    def test_specific_entity(self):
        smith_dict = {
            "mentioned_factors": [
                {"type": "Entity", "name": "Smith", "generic": False},
                {"type": "Entity", "name": "Smythe"},
            ],
            "holdings": [
                {
                    "inputs": [{"type": "fact", "content": "Smith stole a car"}],
                    "outputs": [{"type": "fact", "content": "Smith committed theft"}],
                },
                {
                    "inputs": [{"type": "fact", "content": "Smythe stole a car"}],
                    "outputs": [{"type": "fact", "content": "Smythe committed theft"}],
                },
            ],
        }
        holdings = Rule.collection_from_dict(smith_dict)
        assert not holdings[1] >= holdings[0]
        assert holdings[1].generic_factors != holdings[0].generic_factors


class TestEnactmentImport:
    def test_enactment_import(self, make_regime):
        holdings = Rule.from_json("holding_cardenas.json", regime=make_regime)
        enactment_list = holdings[0].enactments
        assert "all relevant evidence is admissible" in enactment_list[0].text


class TestFactorImport:
    def test_fact_import(self, make_regime):
        holdings = Rule.from_json("holding_watt.json", regime=make_regime)
        new_fact = holdings[0].inputs[1]
        assert "lived at <Hideaway Lodge>" in str(new_fact)
        assert isinstance(new_fact.context_factors[0], Entity)

    def test_fact_with_quantity(self, make_regime):
        holdings = Rule.from_json("holding_watt.json", regime=make_regime)
        new_fact = holdings[1].inputs[3]
        assert "was no more than 35 foot" in str(new_fact)

    def test_find_directory_for_json(self, make_regime):
        directory = pathlib.Path.cwd() / "tests"
        if directory.exists():
            os.chdir(directory)
        input_directory = Rule.directory / "holding_watt.json"
        assert input_directory.exists()


class TestRuleImport:
    """
    Maybe hold off on trying to make these tests pass until deciding
    whether to update the JSON format they rely on to match
    the format in holding_cardenas.json
    """

    def test_import_some_holdings(self, make_opinion_with_holding):
        """
        Don't expect the holdings imported from the JSON to
        exactly match the holdings created for testing in conftest.
        """
        lotus = make_opinion_with_holding["lotus_majority"]
        assert len(lotus.holdings) == 12

    def test_enactment_has_subsection(self, make_opinion_with_holding):
        lotus = make_opinion_with_holding["lotus_majority"]
        assert lotus.holdings[8].enactments[0].selector.path.split("/")[-1] == "b"

    def test_enactment_text_limited_to_subsection(self, make_opinion_with_holding):
        lotus = make_opinion_with_holding["lotus_majority"]
        assert "architectural works" not in str(lotus.holdings[8].enactments[0])

    @pytest.mark.xfail
    def test_imported_holding_same_as_test_object(self, real_holding, make_opinion):
        """
        These objects were once the same, but now the JSON treats
        "lived at" at "operated" as separate Factors.
        """

        watt = make_opinion["watt_majority"]
        watt_holdings = Rule.from_json("holding_watt.json")
        assert watt_holdings[0] == real_holding["h1"]

    def test_same_enactment_objects_equal(self, make_opinion_with_holding):
        """
        Don't expect the holdings imported from the JSON to
        exactly match the holdings created for testing in conftest.
        """
        watt = make_opinion_with_holding["watt_majority"]
        assert watt.holdings[0].enactments[0] == watt.holdings[1].enactments[0]

    def test_different_enactments_same_code(self, make_opinion_with_holding):
        """
        Don't expect the holdings imported from the JSON to
        exactly match the holdings created for testing in conftest.
        """
        lotus = make_opinion_with_holding["lotus_majority"]
        assert (
            lotus.holdings[0].enactments[0].code == lotus.holdings[1].enactments[0].code
        )
        assert (
            lotus.holdings[0].enactments[0].code is lotus.holdings[1].enactments[0].code
        )

    def test_same_enactment_in_two_opinions(self, make_regime, make_opinion):
        watt = make_opinion["watt_majority"]
        watt_holdings = Rule.from_json("holding_watt.json", regime=make_regime)
        brad = make_opinion["brad_majority"]
        brad_holdings = Rule.from_json("holding_brad.json", regime=make_regime)
        assert any(
            watt_holdings[0].enactments[0].means(brad_enactment)
            for brad_enactment in brad_holdings[0].enactments
        )

    def test_same_object_for_enactment_in_import(self, make_opinion, make_regime):
        """
        The JSON for Bradley repeats identical fields to create the same Factor
        for multiple Rules, instead of using the "name" field as a shortcut.
        This tests whether the from_json method uses the same Factor object anyway,
        as if the JSON file had referred to the object by its name field.
        """
        brad = make_opinion["brad_majority"]
        brad_holdings = Rule.from_json("holding_brad.json", regime=make_regime)
        assert any(brad_holdings[6].inputs[0] == x for x in brad_holdings[5].inputs)
        assert any(brad_holdings[6].inputs[0] is x for x in brad_holdings[5].inputs)

    def test_use_int_not_pint_without_dimension(self, make_regime, make_opinion):

        brad = make_opinion["brad_majority"]
        brad_holdings = Rule.from_json("holding_brad.json", regime=make_regime)
        assert "dimensionless" not in str(brad_holdings[6])
        assert isinstance(brad_holdings[6].inputs[0].predicate.quantity, int)

    def test_opinion_posits_holding(self, make_opinion, make_regime):
        brad = make_opinion["brad_majority"]
        brad_holdings = Rule.from_json("holding_brad.json", regime=make_regime)
        for rule in brad_holdings:
            brad.posit(rule)
        assert "warrantless search and seizure" in str(brad.holdings[0])

    def test_opinion_posits_holding_tuple_context(
        self, make_opinion, make_regime, make_entity
    ):
        """
        Having the Watt case posit a holding from the Brad
        case, but with generic factors from Watt.
        """
        watt = make_opinion["watt_majority"]
        brad_holdings = Rule.from_json("holding_brad.json", regime=make_regime)
        context_holding = brad_holdings[6].new_context(
            [make_entity["watt"], make_entity["trees"], make_entity["motel"]]
        )
        watt.posit(context_holding)
        assert (
            "the number of marijuana plants in <the stockpile of trees> was at least 3"
            in str(watt.holdings[-1])
        )

    def test_opinion_posits_holding_dict_context(
        self, make_opinion, make_regime, make_entity
    ):
        """
        Having the Watt case posit a holding from the Brad
        case, but replacing one generic factor with a factor
        from Watt.
        """
        watt = make_opinion["watt_majority"]
        brad_holdings = Rule.from_json("holding_brad.json", regime=make_regime)
        context_holding = brad_holdings[6].new_context(
            {brad_holdings[6].generic_factors[0]: make_entity["watt"]}
        )
        # resetting holdings because of class scope of fixture
        watt.holdings = []
        watt.posit(context_holding)
        string = str(context_holding)
        assert "<Wattenburg> lived at <Bradley's house>" in string
        assert "<Wattenburg> lived at <Bradley's house>" in str(watt.holdings[0])

    def test_holding_with_non_generic_value(
        self, make_opinion, make_regime, make_entity
    ):
        """
        This test originally required a ValueError, but why should it?
        """
        watt = make_opinion["watt_majority"]
        brad_holdings = Rule.from_json("holding_brad.json", regime=make_regime)
        context_change = brad_holdings[6].new_context(
            {brad_holdings[6].generic_factors[1]: make_entity["trees_specific"]}
        )
        string = str(context_change)
        assert "plants in the stockpile of trees was at least 3" in string

    def test_error_because_string_does_not_match_factor_name(self):
        rule_dict = {
            "mentioned_factors": [
                {"type": "Entity", "name": "the dog"},
                {"type": "Human", "name": "the man"},
            ],
            "holdings": [
                {
                    "inputs": ["this factor hasn't been mentioned"],
                    "outputs": [{"type": "fact", "content": "the dog bit the man"}],
                    "enactments": [
                        {"code": "constitution.xml", "section": "amendment-IV"}
                    ],
                    "mandatory": True,
                }
            ],
        }
        with pytest.raises(ValueError):
            Rule.collection_from_dict(rule_dict)

    def test_error_classname_does_not_exist(self):
        rule_dict = {
            "holdings": [
                {
                    "inputs": [
                        {
                            "type": "RidiculousFakeClassName",
                            "content": "officers' search of the yard was a warrantless search and seizure",
                        }
                    ],
                    "outputs": [{"type": "fact", "content": "the dog bit the man"}],
                    "enactments": [
                        {"code": "constitution.xml", "section": "amendment-IV"}
                    ],
                }
            ]
        }
        with pytest.raises(ValueError):
            Rule.collection_from_dict(rule_dict)


class TestNestedFactorImport:
    def test_import_holding(self, make_regime):
        """
        Based on this text:
        This testimony tended “only remotely” to prove that appellant
        had committed the attempted robbery of money from the 7-Eleven
        store. In addition, the probative value of the evidence was
        substantially outweighed by the inflammatory effect of the
        testimony on the jury. Hence, admission of the testimony
        concerning appellant’s use of narcotics was improper.
        """
        cardenas_holdings = Rule.from_json("holding_cardenas.json", regime=make_regime)
        assert len(cardenas_holdings) == 2
