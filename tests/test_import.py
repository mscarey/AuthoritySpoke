import json

from enactments import Enactment
from entities import Entity, Human
from evidence import Evidence
from facts import Fact
from opinions import Opinion
from rules import Procedure, Rule, ProceduralRule
from spoke import Predicate, Factor


class TestPredicateImport:
    def test_import_predicate_with_quantity(self):
        story, entities = Predicate.from_string(
            "Once there was a {king} who had {> 3} castles"
        )
        assert len(entities) == 1
        assert story.content.startswith("Once")
        assert story.comparison == ">"
        assert story.quantity == 3


class TestEnactmentImport:
    def test_enactment_import(self):
        with open("input/holding_cardenas.json") as file:
            cardenas_summary = json.load(file)
        enactment_list = cardenas_summary["holdings"][0]["enactments"]
        enactment = Enactment.from_dict(enactment_list[0])
        assert "all relevant evidence is admissible" in enactment.text


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
        # The holdings_from_json method is designed for the old
        # JSON format and needs to be rewritten.

        # Not working in part because it has no way to parse a string
        # containing Factor names, to make either a new Factor or a dict
        # that can be converted to the new Factor
        cardenas.holdings_from_json("holding_cardenas.json")
        assert len(cardenas.holdings) == 2
