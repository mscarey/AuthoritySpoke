import json
from typing import Dict


from pint import UnitRegistry
import pytest

from enactments import Code, Enactment
from spoke import Entity, Human
from spoke import Predicate, Factor, Fact, Evidence
from spoke import Procedure, Rule, ProceduralRule
from spoke import Opinion, opinion_from_file
from spoke import ureg, Q_
from spoke import check_entity_consistency
from spoke import find_matches, evolve_match_list


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
    def test_enactment_import(self, make_opinion):
        cardenas = make_opinion["cardenas_majority"]
        entities, d = cardenas.dict_from_input_json("holding_cardenas.json")
        enactment_list = d[0]["enactments"]
        enactment = Enactment.from_dict(enactment_list[0])
        assert "all relevant evidence is admissible" in enactment.text


class TestRuleImport:
    """
    Maybe hold off on trying to make these tests pass until deciding
    whether to update the JSON format they rely on to match
    the format in holding_cardenas.json
    """

    def test_import_some_holdings(self, make_opinion):
        watt = make_opinion["watt_majority"]
        holdings = watt.holdings_from_json("holding_watt.json")
        assert len(watt.holdings) == 4
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
        cardenas.holdings_from_json("holding_cardenas.json")
        assert len(cardenas.holdings) == 2
