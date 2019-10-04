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
    def test_find_directory_for_json(self, make_regime):
        directory = pathlib.Path.cwd() / "tests"
        if directory.exists():
            os.chdir(directory)
        input_directory = filepaths.get_directory_path("holdings") / "holding_watt.json"
        assert input_directory.exists()


class TestEntityLoad:
    def test_get_entity_schema(self):
        record = {"type": "Entity", "name": "George Washington"}
        schema = schemas.FactorSchema()
        obj = schema.load(record)
        assert obj.name == "George Washington"
        assert isinstance(obj, Entity)

    def test_load_entity_from_factor_schema(self):
        record = {"type": "Entity", "name": "George Washington"}
        schema = schemas.FactorSchema()
        george = schema.load(record)
        assert george.generic == True

    def test_load_and_dump_entity_from_entity_schema(self):
        """
        When this object is loaded with the EntitySchema, it becomes
        an Entity with default values.

        When it's dumped with FactorSchema instead of EntitySchema,
        it receives a "type" field to specify which type of Factor
        it is.
        """
        record = {"name": "John Adams"}
        schema = schemas.EntitySchema()
        john = schema.load(record)
        assert john.generic is True
        factor_schema = schemas.FactorSchema()
        john_dict = factor_schema.dump(john)
        assert john_dict["type"] == "Entity"


class TestFactLoad:
    def test_import_fact_with_entity_name_containing_another(self):
        house_fact = readers.read_fact(
            {
                "content": "{Alice} sold {Alice's house} for a price in dollars of > 300000"
            }
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


class TestCollectMentioned:
    def test_mentioned_from_entity(self):
        obj = {"type": "Entity", "name": "Ann"}
        obj, mentioned = name_index.collect_mentioned(obj)
        assert mentioned["Ann"]["type"] == "Entity"

    def test_insert_in_mentioned_does_not_change_obj(self):
        mentioned = name_index.Mentioned()
        obj = {"type": "Entity", "name": "Remainer"}
        mentioned.insert_by_name(obj)
        assert obj["name"] == "Remainer"
        assert "name" not in mentioned["Remainer"].keys()

    relevant_dict = {
        "content": "{} is relevant to show {}",
        "type": "Fact",
        "name": "relevant fact",
        "context_factors": [
            {"content": "{Short Name} shot {Longer Name}", "type": "Fact"},
            {
                "content": "{} murdered {}",
                "context_factors": ["Short Name", "Longer Name"],
                "type": "Fact",
            },
        ],
    }

    def test_expand_shorthand(self):
        obj = name_index.expand_shorthand_mentioned(self.relevant_dict)
        assert obj["context_factors"][0]["context_factors"][0]["name"] == "Short Name"

    def test_mentioned_from_fact_and_entities(self):
        obj = name_index.expand_shorthand_mentioned(self.relevant_dict)
        obj, mentioned = name_index.collect_mentioned(self.relevant_dict)
        assert mentioned["relevant fact"]["type"] == "Fact"
        shooting = mentioned["relevant fact"]["context_factors"][0]
        assert shooting["context_factors"][0]["name"] == "Short Name"

    def test_mentioned_ordered_by_length(self):
        obj, mentioned = name_index.index_names(self.relevant_dict)
        shortest = mentioned.popitem()
        assert shortest[0] == "Short Name"
