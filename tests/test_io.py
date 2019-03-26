import json

import pint
import pytest

from enactments import Enactment
from entities import Entity, Human
from evidence import Evidence
from facts import Fact
from opinions import Holding, Opinion
from rules import Procedure, Rule, ProceduralRule
from spoke import Predicate, Factor
from context import log_mentioned_context

ureg = pint.UnitRegistry()


class TestPredicateImport:
    """
    This tests a function for importing a Predicate by itself,
    but Predicate imports can also happen as part of a Fact import.
    """

    def test_import_predicate_with_quantity(self):
        story, entities = Predicate.from_string(
            "Once there was a {king} who had {> 3} castles"
        )
        assert len(entities) == 1
        assert story.content.startswith("Once")
        assert story.comparison == ">"
        assert story.quantity == 3


class TestEntityImport:
    def test_mentioned_factors(self):
        with open("input/holding_watt.json") as file:
            watt_summary = json.load(file)
        mentioned_factors = watt_summary["mentioned_factors"]
        mentioned = Opinion.get_mentioned_factors(mentioned_factors)
        assert isinstance(mentioned[0], Entity)
        assert any("Watt" in str(factor) for factor in mentioned)


class TestEnactmentImport:
    def test_enactment_import(self):
        with open("input/holding_cardenas.json") as file:
            cardenas_summary = json.load(file)
        enactment_list = cardenas_summary["holdings"][0]["enactments"]
        enactment, mentioned = Enactment.from_dict(enactment_list[0], [])
        assert "all relevant evidence is admissible" in enactment.text


class TestFactorImport:
    def test_fact_import(self):
        with open("input/holding_watt.json") as file:
            watt_summary = json.load(file)
        mentioned = watt_summary["mentioned_factors"]
        mentioned_factors = Opinion.get_mentioned_factors(mentioned)
        fact_dict = watt_summary["holdings"][0]["inputs"][1]
        new_fact, mentioned_factors = Fact.from_dict(fact_dict, mentioned_factors)
        assert "lived at <Hideaway Lodge>" in str(new_fact)
        assert isinstance(new_fact.entity_context[0], Entity)

    def test_fact_with_quantity(self):
        with open("input/holding_watt.json") as file:
            watt_summary = json.load(file)
        mentioned = watt_summary["mentioned_factors"]
        mentioned_factors = Opinion.get_mentioned_factors(mentioned)
        fact_dict = watt_summary["holdings"][1]["inputs"][3]
        new_fact, mentioned_factors = Fact.from_dict(fact_dict, mentioned_factors)
        assert "was no more than 35 foot" in str(new_fact)


class TestRuleImport:
    """
    Maybe hold off on trying to make these tests pass until deciding
    whether to update the JSON format they rely on to match
    the format in holding_cardenas.json
    """

    def test_import_some_holdings(self, make_opinion):
        """
        Don't expect the holdings imported from the JSON to
        exactly match the holdings created for testing in conftest.
        """
        watt = make_opinion["watt_majority"]
        holdings = watt.holdings_from_json("holding_watt.json")
        assert len(holdings) == 5

    @pytest.mark.xfail
    def test_imported_holding_same_as_test_object(self, real_holding, make_opinion):
        """
        These objects were once the same, but now the JSON treats
        "lived at" at "operated" as separate Factors.
        """

        watt = make_opinion["watt_majority"]
        watt_holdings = watt.holdings_from_json("holding_watt.json")
        assert watt_holdings[0] == real_holding["h1"]

    def test_same_enactment_objects_equal(self, make_opinion):
        """
        Don't expect the holdings imported from the JSON to
        exactly match the holdings created for testing in conftest.
        """
        watt = make_opinion["watt_majority"]
        holdings = watt.holdings_from_json("holding_watt.json")
        assert holdings[0].enactments[0] == holdings[1].enactments[0]

    def test_same_code_object_in_multiple_enactments(self, make_opinion):
        """
        Don't expect the holdings imported from the JSON to
        exactly match the holdings created for testing in conftest.
        """
        watt = make_opinion["watt_majority"]
        holdings = watt.holdings_from_json("holding_watt.json")
        assert holdings[0].enactments[0].code == holdings[1].enactments[0].code

    def test_same_enactment_in_two_opinions(self, make_opinion):
        watt = make_opinion["watt_majority"]
        watt_holdings = watt.holdings_from_json("holding_watt.json")
        brad = make_opinion["brad_majority"]
        brad_holdings = brad.holdings_from_json("holding_brad.json")
        assert any(
            watt_holdings[0].enactments[0] == brad_enactment
            for brad_enactment in brad_holdings[0].enactments
        )

    def test_same_object_for_enactment_in_import(self, make_opinion):
        """
        The JSON for Bradley repeats identical fields to create the same Factor
        for multiple Rules, instead of using the "name" field as a shortcut.
        This tests whether the from_json method uses the same Factor object anyway,
        as if the JSON file had referred to the object by its name field.
        """
        brad = make_opinion["brad_majority"]
        brad_holdings = brad.holdings_from_json("holding_brad.json")
        assert any(brad_holdings[6].inputs[0] == x for x in brad_holdings[5].inputs)
        assert any(brad_holdings[6].inputs[0] is x for x in brad_holdings[5].inputs)

    def test_use_int_not_pint_without_dimension(self, make_opinion):

        brad = make_opinion["brad_majority"]
        brad_holdings = brad.holdings_from_json("holding_brad.json")
        assert "dimensionless" not in str(brad_holdings[6])
        assert isinstance(brad_holdings[6].inputs[0].predicate.quantity, int)

    def test_opinion_posits_holding(self, make_opinion):
        brad = make_opinion["brad_majority"]
        brad_holdings = brad.holdings_from_json("holding_brad.json")
        for rule in brad_holdings:
            context_holding = Holding(rule)
            brad.posits(context_holding)
        assert "warrantless search and seizure" in str(brad.holdings[0])

    def test_opinion_posits_holding_tuple_context(self, make_opinion, make_entity):
        """
        Having the Watt case posit a holding from the Brad
        case, but with generic factors from Watt.
        """
        watt = make_opinion["watt_majority"]
        brad_holdings = watt.holdings_from_json("holding_brad.json")
        context_holding = Holding(
            brad_holdings[6],
            (make_entity["watt"], make_entity["trees"], make_entity["motel"]),
        )
        watt.posits(context_holding)
        assert "TK" in str(watt.holdings[0])

    def test_opinion_posits_holding_dict_context(self, make_opinion, make_entity):
        """
        Having the Watt case posit a holding from the Brad
        case, but replacing one generic factor with a factor
        from Watt.
        """
        watt = make_opinion["watt_majority"]
        brad_holdings = watt.holdings_from_json("holding_brad.json")
        context_holding = Holding(
            brad_holdings[6], context={brad_holdings[6].generic_factors[0]: make_entity["watt"]}
        )
        watt.posits(context_holding)
        assert "TK" in str(watt.holdings[0])

    def test_holding_with_key_not_in_generic_context_raises_error(
        self, make_opinion, make_entity
    ):
        watt = make_opinion["watt_majority"]
        brad_holdings = watt.holdings_from_json("holding_brad.json")
        with pytest.raises(ValueError):
            Holding(brad_holdings[6], context={make_entity["trees"]: make_entity["motel"]})

    def test_holding_with_non_generic_value_raises_error(
        self, make_opinion, make_entity
    ):
        watt = make_opinion["watt_majority"]
        brad_holdings = watt.holdings_from_json("holding_brad.json")
        with pytest.raises(ValueError):
            Holding(
                brad_holdings[6],
                context={brad_holdings[6].generic_factors[0]: make_entity["trees_specific"]},
            )


class TestNestedFactorImport:
    def test_import_holding(self, make_opinion):
        """
        Based on this text:
        This testimony tended “only remotely” to prove that appellant
        had committed the attempted robbery of money from the 7-Eleven
        store. In addition, the probative value of the evidence was
        substantially outweighed by the inflammatory effect of the
        testimony on the jury. Hence, admission of the testimony
        concerning appellant’s use of narcotics was improper.
        """
        cardenas = make_opinion["cardenas_majority"]
        cardenas_holdings = cardenas.holdings_from_json("holding_cardenas.json")
        assert len(cardenas_holdings) == 2
