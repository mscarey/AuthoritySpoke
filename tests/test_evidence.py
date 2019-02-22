from copy import copy
import datetime
import json
from typing import Dict

from pint import UnitRegistry
import pytest

from enactments import Code, Enactment
from entities import Entity, Human
from evidence import Evidence, Exhibit
from rules import Procedure, Rule, ProceduralRule
from opinions import Opinion
from spoke import Predicate, Factor, Fact
from spoke import ureg, Q_
from spoke import check_entity_consistency
from spoke import find_matches, evolve_match_list

class TestExhibits:
    def test_make_evidence_object(self, watt_factor):
        e = Exhibit(form="testimony")
        assert not e.absent

class TestEvidence:
    def test_make_evidence_object(self, watt_factor):
        e = Evidence(Exhibit(form="testimony"), to_effect=watt_factor["f2"])
        assert not e.absent

    def test_default_len_based_on_unique_entity_slots(self, make_entity, make_factor):
        """same as e["no_shooting"]"""

        e = Evidence(
            form="testimony",
            to_effect=make_factor["f_no_crime"],
            statement=make_factor["f_no_shooting"],
            stated_by=make_entity["alice"],
        )
        assert len(e) == 2

    def test_get_entity_orders(self, make_evidence):
        # TODO: check this after making Evidence.__str__ method
        assert make_evidence["no_shooting"].entity_orders == {(0, 1, 0, 0)}
        assert make_evidence["reciprocal"].entity_orders == {(0, 1, 0, 2), (1, 0, 0, 2)}

    def test_get_entity_orders_no_statement(self, make_factor):
        e = Evidence(
            Exhibit(form="testimony"), to_effect=make_factor["f_no_crime"]
        )
        assert e.entity_orders == {(0, 1)}

    def test_evidence_str(self, make_evidence):
        assert str(make_evidence["reciprocal"]).startswith(
            "Testimony, with a statement by <2>"
        )

    def test_equality_with_entity_order(self, make_predicate, make_evidence):
        e = make_evidence
        assert e["no_shooting"] == e["no_shooting_entity_order"]

    def test_equality_with_no_statement(self, make_evidence):
        assert make_evidence["crime"] == make_evidence["crime"]

    def test_unequal_due_to_entity_order(self, make_evidence):
        e = make_evidence
        assert e["no_shooting"] != e["no_shooting_different_witness"]

    def test_unequal_different_attributes(self, make_evidence):
        assert (
            make_evidence["no_shooting_no_effect_entity_order"]
            != make_evidence["no_shooting_different_witness"]
        )

    def test_implication_missing_witness(self, make_evidence):
        e = make_evidence
        assert e["no_shooting"] >= e["no_shooting_witness_unknown"]

    def test_implication_missing_effect(self, make_evidence):
        e = make_evidence
        assert e["no_shooting"] >= e["no_shooting_no_effect_entity_order"]

    def test_no_implication_of_fact(self, make_predicate, make_evidence):
        assert not make_evidence["no_shooting"] > Fact.new(
            make_predicate["p_no_shooting"]
        )
        assert (
            not Fact.new(make_predicate["p_no_shooting"]) > make_evidence["no_shooting"]
        )

    def test_no_contradiction_of_fact(self, make_predicate, make_evidence):
        assert not make_evidence["no_shooting"].contradicts(
            Fact.new(make_predicate["p_no_shooting"])
        )

    def test_no_contradiction_from_supporting_contradictory_facts(self, make_evidence):
        assert not make_evidence["no_shooting"].contradicts(make_evidence["shooting"])

    def test_contradiction_of_absent_version_of_self(self, make_evidence):
        e = make_evidence
        assert e["no_shooting"].contradicts(e["no_shooting_absent"])

    def test_contradict_absent_version_of_implied_factor(self, make_evidence):
        e = make_evidence
        assert e["no_shooting_witness_unknown_absent"].contradicts(e["no_shooting"])
        assert e["no_shooting"].contradicts(e["no_shooting_witness_unknown_absent"])

    def test_no_contradiction_absent_same_witness(self, make_evidence):
        e = make_evidence
        assert not e["no_shooting_absent"].contradicts(e["no_shooting_witness_unknown"])
        assert not e["no_shooting_witness_unknown"].contradicts(e["no_shooting_absent"])
        assert not e["no_shooting_absent"].contradicts(
            e["no_shooting_different_witness"]
        )

    def test_no_contradiction_of_implied_factor(self, make_evidence):
        e = make_evidence
        assert not e["no_shooting"].contradicts(e["no_shooting_witness_unknown"])
