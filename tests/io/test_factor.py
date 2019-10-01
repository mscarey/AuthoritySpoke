import json
import os
import pathlib

import pint
import pytest

from authorityspoke.enactments import Code, Enactment
from authorityspoke.entities import Entity
from authorityspoke.io import filepaths, readers, schemas
from authorityspoke.io.loaders import load_holdings
from authorityspoke.io.dump import to_dict, to_json

ureg = pint.UnitRegistry()


class TestFactorLoad:
    def test_find_directory_for_json(self, make_regime):
        directory = pathlib.Path.cwd() / "tests"
        if directory.exists():
            os.chdir(directory)
        input_directory = filepaths.get_directory_path("holdings") / "holding_watt.json"
        assert input_directory.exists()


class TestEntityLoad:
    def test_load_entity_from_factor_schema(self):
        record = {"type": "Entity", "name": "George Washington"}
        schema = schemas.FactorSchema()
        george = schema.load(record)
        assert george.generic is True

    def test_load_entity_from_mentioned(self, make_entity):
        mentioned = {make_entity["motel"]: []}
        schema = schemas.EntitySchema()
        schema.context["mentioned"] = mentioned
        motel = schema.load("Hideaway Lodge")
        assert "Lodge" in motel.name

    def test_dump_entity_from_factor_schema(self):
        george = Entity("George Washington")
        schema = schemas.FactorSchema()
        record = schema.dump(george)
        assert record["generic"] is True
        assert record["type"] == "Entity"

    def test_load_and_dump_entity_from_entity_schema(self):
        record = {"name": "John Adams"}
        schema = schemas.EntitySchema()
        john = schema.load(record)
        assert john.generic is True
        john_dict = schema.dump(john)
        assert john_dict["name"] == "John Adams"


class TestFactLoad:
    def test_import_fact_with_entity_name_containing_another(self):
        house_fact = readers.read_fact(
            {"content": "Alice sold Alice's house for a price in dollars of > 300000"},
            mentioned={Entity(name="Alice"): [], Entity(name="Alice's house"): []},
        )
        assert any(
            context.name == "Alice's house" for context in house_fact.generic_factors
        )

    def test_import_predicate_with_quantity(self):
        story = readers.read_fact(
            {"content": "The number of castles {the king} had was > 3"}
        )
        assert len(story.predicate) == 1
        assert story.predicate.content.startswith("The number of castles")
        assert story.predicate.comparison == ">"
        assert story.predicate.quantity == 3

    def test_make_fact_from_string(self, watt_factor):
        fact_float_more = readers.read_fact(
            {
                "content": "the distance between {Ann} and {Lee} was >= 20.1",
                "reciprocal": True,
            }
        )
        fact_float_less = watt_factor["f8_int"]
        assert fact_float_more >= fact_float_less

    def test_retrieve_mentioned_during_load(self):
        """
        Test that the schema can recreate the Entity objects "Alice" and
        "Bob" from just their name strings, by having added them to
        "mentioned" when they first appeared.
        """
        relevant_json = """{"predicate": {
            "content": "{} is relevant to show {}"},
            "type": "Fact",
            "context_factors": [
                {
                    "predicate": {"content": "{} shot {}"},
                    "context_factors": [
                        {"name": "Alice", "type": "Entity"},
                        {"name": "Bob", "type": "Entity"}
                        ],
                    "type": "Fact"
                },
                {
                    "predicate": {"content": "{} murdered {}"},
                    "context_factors": ["Alice", "Bob"],
                    "type": "Fact"
                }]}"""
        schema = schemas.FactorSchema()
        relevant_fact = schema.loads(relevant_json)
        assert relevant_fact.context_factors[1].context_factors[0] == "Bob"


class TestFactDump:
    def test_dump_with_quantity(self, watt_factor):
        f8_dict = to_dict(watt_factor["f8"])
        assert f8_dict["predicate"]["quantity"] == "20 foot"

    def test_dump_complex_fact(self, make_complex_fact):
        relevant_fact = make_complex_fact["f_relevant_murder"]
        relevant_dict = to_dict(relevant_fact)
        shooting_dict = relevant_dict["context_factors"][0]
        assert shooting_dict["context_factors"][0]["name"] == "Alice"
