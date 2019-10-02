import json
import os
import pathlib

import pint
import pytest

from authorityspoke.enactments import Code, Enactment
from authorityspoke.entities import Entity
from authorityspoke.io import readers, schemas
from authorityspoke.io.loaders import load_holdings
from authorityspoke.io import filepaths

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
        assert george.generic == True

    def test_load_and_dump_entity_from_factor_schema(self):
        record = {"name": "John Adams", "type": "entity"}
        schema = schemas.FactorSchema()
        john = schema.load(record)
        assert john.generic is True
        john_dict = schema.dump(john)
        assert john_dict["type"] == "Entity"


class TestFactLoad:
    def test_import_fact_with_entity_name_containing_another(self):
        schema = schemas.FactSchema()
        schema.context["mentioned"] = {
            Entity(name="Alice"): [],
            Entity(name="Alice's house"): [],
        }
        house_fact = schema.load(
            data={
                "content": "Alice sold Alice's house for a price in dollars of > 300000"
            }
        )

        assert any(
            context.name == "Alice's house" for context in house_fact.generic_factors
        )

    def test_import_predicate_with_quantity(self):
        schema = schemas.FactSchema()
        story = schema.load(
            data={"content": "The number of castles {the king} had was > 3"}
        )
        assert len(story.predicate) == 1
        assert story.predicate.content.startswith("The number of castles")
        assert story.predicate.comparison == ">"
        assert story.predicate.quantity == 3

    def test_make_fact_from_string(self, watt_factor):
        schema = schemas.FactSchema()
        fact_float_more = schema.load(
            {
                "content": "the distance between {Ann} and {Lee} was >= 20.1",
                "reciprocal": True,
            }
        )
        fact_float_less = watt_factor["f8_int"]
        assert fact_float_more >= fact_float_less
