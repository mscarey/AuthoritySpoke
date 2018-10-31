from spoke import Factor

import pytest


def test_string_representation_of_factor():
    f1 = Factor("{} was a motel")
    assert str(f1) == "Fact: {} was a motel"

def test_entity_slots_as_length_of_factor():
    f1 = Factor("{} was a motel")
    assert len(f1) == 1

def test_content_with_entities():
    """Entities are just strings for now"""

    f1 = Factor("{} was a motel")
    assert f1.content_with_entities(["rAnDoM STriNg"]) == "rAnDoM STriNg was a motel"

def test_content_with_wrong_number_of_entities():
    f1 = Factor("{} was a motel")
    with pytest.raises(ValueError):
        f1.content_with_entities(["Motel 6", "Wattenburg"])

"""
Test that holdings are considered equal if they have the same factors
and the numbers they use to refer to entities are different but in an
equivalent order.
e.g. {"F1": "121", "F2": "233"} and {"F2": "122", "F1": "313"}
"""
