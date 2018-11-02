from spoke import Entity, Fact, Person, Predicate
from typing import Dict

import pytest


@pytest.fixture
def make_factor() -> Dict[str, Fact]:
    # Make predicates first
    p1 = Predicate("{} was a motel")
    p2 = Predicate("{} operated and lived at {}")

    p7 = Predicate("the distance between {} and {} was more than 35 feet",
                   reciprocal=True)
    f1 = Fact(p1)
    f2 = Fact(p2)
    f7 = Fact(p7, truth_of_predicate=False)


    return {"f1": f1, "f2": f2, "f7": f7}

@pytest.fixture
def make_entity() -> Dict[str, Entity]:
    return {"e_watt": Person("Wattenburg"),
            "e_motel": Entity("Hideaway Lodge"),
            "e_trees": Entity("a stockpile of trees")}

def test_string_representation_of_factor(make_factor):
    assert str(make_factor["f1"]) == "Fact: {} was a motel"

def test_entity_slots_as_length_of_factor(make_factor):
    assert len(make_factor["f1"].predicate) == 1

def test_predicate_with_entities(make_entity, make_factor):
    """Entities are just strings for now"""
    assert make_factor["f1"].predicate_with_entities(
        [make_entity["e_motel"]]) == "Hideaway Lodge was a motel"

def test_predicate_with_wrong_number_of_entities(make_factor):
    with pytest.raises(ValueError):
        f = Predicate("{} was a motel", reciprocal=True)

def test_reciprocal_with_wrong_number_of_entities(make_entity, make_factor):
    with pytest.raises(ValueError):
        make_factor["f1"].predicate_with_entities(
            [make_entity["e_motel"], make_entity["e_watt"]])

def test_false_predicate_with_entities(make_factor):
    assert make_factor["f7"].predicate_with_entities(
        ["the trees", "Hideaway Lodge"]) == str("It is false that the " +
        "distance between the trees and Hideaway Lodge was more than 35 feet")
    assert make_factor["f7"].predicate_with_entities(
        ["the trees", "Hideaway Lodge"]) == str("It is false that the " +
        "distance between the trees and Hideaway Lodge was more than 35 feet")

def test_entity_and_person_in_predicate(make_entity, make_factor):
    assert make_factor["f2"].predicate_with_entities(
        [make_entity["e_watt"], make_entity["e_motel"]]
        ) == "Wattenburg operated and lived at Hideaway Lodge"

"""Need a test for a fact labeled as "Fact" followed by the predicate with
entities"""

def test_holding_equality():
    """
    Test that holdings are considered equal if they have the same factors
    and the numbers they use to refer to entities are different but in an
    equivalent order.
    e.g. {"F1": "121", "F2": "233"} and {"F2": "122", "F1": "313"}
    """
    pass
