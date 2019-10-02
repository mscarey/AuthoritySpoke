import json
import os
import pathlib

import pint
import pytest

from authorityspoke.enactments import Code, Enactment
from authorityspoke.entities import Entity
from authorityspoke.io import readers, schemas, name_index
from authorityspoke.io.loaders import load_holdings
from authorityspoke.io import filepaths

ureg = pint.UnitRegistry()


class TestFactorLoad:
    def test_fact_import(self, make_regime):
        holdings = load_holdings("holding_watt.json", regime=make_regime)
        new_fact = holdings[0].inputs[1]
        assert "lived at <Hideaway Lodge>" in str(new_fact)
        assert isinstance(new_fact.context_factors[0], Entity)

    def test_fact_with_quantity(self, make_regime):
        holdings = load_holdings("holding_watt.json", regime=make_regime)
        new_fact = holdings[1].inputs[3]
        assert "was no more than 35 foot" in str(new_fact)

    def test_find_directory_for_json(self, make_regime):
        directory = pathlib.Path.cwd() / "tests"
        if directory.exists():
            os.chdir(directory)
        input_directory = filepaths.get_directory_path("holdings") / "holding_watt.json"
        assert input_directory.exists()


class TestEntityLoad:
    def test_get_entity_schema(self):
        record = {"type": "Entity", "name": "George Washington"}
        schema = schemas.get_schema_for_factor_record(record)
        assert schema.__model__ == Entity

    def test_load_entity_from_factor_schema(self):
        record = {"type": "Entity", "name": "George Washington"}
        schema = schemas.FactorSchema(partial=True, unknown="INCLUDE")
        george = schema.load(record)
        assert george.generic == True

    def test_load_and_dump_entity_from_entity_schema(self):
        record = {"name": "John Adams"}
        schema = schemas.EntitySchema()
        john = schema.load(record)
        assert john.generic is True
        john_dict = schema.dump(john)
        assert john_dict["type"] == "Entity"


class TestFactLoad:
    def test_import_fact_with_entity_name_containing_another(self):
        house_fact = readers.read_fact(
            content="Alice sold Alice's house for a price in dollars of > 300000",
            mentioned={Entity(name="Alice"): [], Entity(name="Alice's house"): []},
        )
        assert any(
            context.name == "Alice's house" for context in house_fact.generic_factors
        )

    def test_import_predicate_with_quantity(self):
        story = readers.read_fact("The number of castles {the king} had was > 3")
        assert len(story.predicate) == 1
        assert story.predicate.content.startswith("The number of castles")
        assert story.predicate.comparison == ">"
        assert story.predicate.quantity == 3

    def test_make_fact_from_string(self, watt_factor):
        fact_float_more = readers.read_fact(
            "the distance between {Ann} and {Lee} was >= 20.1", reciprocal=True
        )
        fact_float_less = watt_factor["f8_int"]
        assert fact_float_more >= fact_float_less


class TestCollectMentioned:
    def test_mentioned_from_entity(self):
        obj = {"type": "Entity", "name": "Ann"}
        mentioned = name_index.get_mentioned(obj)
        assert mentioned["Ann"]["type"] == "Entity"
