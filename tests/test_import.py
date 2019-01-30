import json
from typing import Dict


from pint import UnitRegistry
import pytest

from spoke import Entity, Human
from spoke import Predicate, Factor, Fact, Evidence
from spoke import Procedure, Holding, ProceduralHolding
from spoke import Opinion, opinion_from_file
from spoke import Code, Enactment
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

class TestHoldingImport:
    """
    Maybe hold off on trying to make these tests pass until deciding
    whether to update the JSON format they rely on to match
    the format in holding_nested_factor.json
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
        This test uses the brad_majority opinion but links it to
        the completely fake Entity and Holding data from
        holding_nested_factor.json. (The data isn't based on Bradley.)
        """
        fake_case = make_opinion["brad_majority"]
        # The holdings_from_json method is designed for the old
        # JSON format and needs to be rewritten.
        fake_case.holdings_from_json("holding_nested_factor.json")
        assert len(fake_case.holdings) == 1