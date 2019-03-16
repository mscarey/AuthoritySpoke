import json

import pint

from enactments import Enactment
from entities import Entity, Human
from evidence import Evidence
from facts import Fact
from opinions import Opinion
from rules import Procedure, Rule, ProceduralRule
from spoke import Predicate, Factor
from file_import import log_mentioned_context

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
        assert isinstance(mentioned[1], Human)
        assert "Watt" in str(mentioned[1])


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
        assert "<Wattenburg> operated and lived at <Hideaway Lodge>" in str(new_fact)
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
        assert len(watt.holdings) == 5
        assert holdings == watt.holdings

    def test_imported_holding_same_as_test_object(self, make_holding, make_opinion):
        watt = make_opinion["watt_majority"]
        watt.holdings_from_json("holding_watt.json")
        assert any(h == make_holding["h1"] for h in watt.holdings)

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
        cardenas.holdings_from_json("holding_cardenas.json")
        assert len(cardenas.holdings) == 2
