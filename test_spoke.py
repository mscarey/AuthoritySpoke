from spoke import Factor
from typing import Dict

import pytest


@pytest.fixture
def make_factor() -> Dict[str, Factor]:
    f1 = Factor("{} was a motel")
    f7 = Factor("the distance between {} and {} was more than 35 feet",
                truth_of_predicate=False, reciprocal=True)
    return {"f1": f1, "f7": f7}

def test_string_representation_of_factor(make_factor):
    assert str(make_factor["f1"]) == "Fact: {} was a motel"

def test_entity_slots_as_length_of_factor(make_factor):
    assert len(make_factor["f1"]) == 1

def test_predicate_with_entities(make_factor):
    """Entities are just strings for now"""
    assert make_factor["f1"].predicate_with_entities(
        ["rAnDoM STriNg"]) == "rAnDoM STriNg was a motel"

def test_predicate_with_wrong_number_of_entities(make_factor):
    with pytest.raises(ValueError):
        f = Factor("{} was a motel", reciprocal=True)

def test_reciprocal_with_wrong_number_of_entities(make_factor):
    with pytest.raises(ValueError):
        make_factor["f1"].predicate_with_entities(["Motel 6", "Wattenburg"])

def test_false_predicate_with_entities(make_factor):
    assert make_factor["f7"].predicate_with_entities(
        ["the trees", "Hideaway Lodge"]) == str("It is false that the " +
        "distance between the trees and Hideaway Lodge was more than 35 feet")

def test_holding_equality():
    """
    Test that holdings are considered equal if they have the same factors
    and the numbers they use to refer to entities are different but in an
    equivalent order.
    e.g. {"F1": "121", "F2": "233"} and {"F2": "122", "F1": "313"}
    """
    pass
