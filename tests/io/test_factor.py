import json
import os
import pathlib

from marshmallow import ValidationError
from legislice import Enactment
import pytest

from authorityspoke.codes import Code
from authorityspoke.entities import Entity
from authorityspoke.io import readers, schemas, name_index
from authorityspoke.io.loaders import load_holdings
from authorityspoke.io import filepaths
from authorityspoke.io.dump import to_dict, to_json
from authorityspoke.io.text_expansion import expand_shorthand


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
        assert george.generic is True

    def test_load_entity_from_mentioned(self):
        mentioned = name_index.Mentioned({"Lee": {"type": "entity"}})
        schema = schemas.EntitySchema()
        schema.context["mentioned"] = mentioned
        lee = schema.load("Lee")
        assert lee.name == "Lee"

    def test_dump_entity_from_factor_schema(self):
        george = Entity("George Washington")
        schema = schemas.FactorSchema()
        record = schema.dump(george)
        assert record["generic"] is True
        assert record["type"] == "Entity"

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
    house_data = {
        "content": "{Alice} sold {Alice's house} for a price in dollars of > 300000"
    }
    story_data = {"content": "The number of castles {the king} had was > 3"}

    def test_import_fact_with_entity_name_containing_another(self):
        expanded = expand_shorthand(self.house_data)
        house_fact = readers.read_fact(expanded)
        assert house_fact.context_factors[1].name == "Alice's house"

    def test_import_predicate_with_quantity(self):
        story = expand_shorthand(self.story_data)
        story = readers.read_fact(story)
        assert len(story.predicate) == 1
        assert story.predicate.content.startswith("The number of castles")
        assert story.predicate.comparison == ">"
        assert story.predicate.quantity == 3

    def test_make_fact_from_string(self, watt_factor):
        fact_float_data = {
            "content": "the distance between {Ann} and {Lee} was >= 20.1",
            "reciprocal": True,
        }
        fact_float_more = expand_shorthand(fact_float_data)
        fact_float_more = readers.read_fact(fact_float_more)
        fact_float_less = watt_factor["f8_int"]
        assert fact_float_more >= fact_float_less


class TestFactorLoad:
    def test_import_fact_with_factor_schema(self):
        loaded = load_holdings("holding_cardenas.json")
        entity = readers.read_factor(loaded[0]["inputs"][0])
        inner_context = entity.context_factors[0].context_factors[0]
        assert inner_context.name == "the defendant"

    def test_import_facts_with_factor_schema(self):
        loaded = load_holdings("holding_cardenas.json")
        factor = readers.read_factors(loaded[0]["inputs"])[1].context_factors[0]
        assert factor.content == "{} committed an attempted robbery"


class TestFactDump:
    def test_dump_with_quantity(self, watt_factor):
        f8_dict = to_dict(watt_factor["f8"])
        assert f8_dict["predicate"]["quantity"] == "20 foot"

    def test_dump_complex_fact(self, make_complex_fact):
        relevant_fact = make_complex_fact["f_relevant_murder"]
        relevant_dict = to_dict(relevant_fact)
        shooting_dict = relevant_dict["context_factors"][0]
        assert shooting_dict["context_factors"][0]["name"] == "Alice"


class TestExhibitDump:
    def test_dump_exhibit(self, make_exhibit):
        exhibit = make_exhibit["shooting_affidavit"]
        schema = schemas.ExhibitSchema()
        dumped = schema.dump(exhibit)
        assert dumped["statement"]["context_factors"][0]["name"] == "Alice"

    def test_dump_and_load_exhibit(self, make_exhibit):
        exhibit = make_exhibit["no_shooting_entity_order_testimony"]
        schema = schemas.ExhibitSchema()
        dumped = schema.dump(exhibit)
        loaded = schema.load(dumped)
        assert loaded.form == "testimony"
        assert loaded.statement_attribution.name == "Bob"


class TestEvidenceLoad:
    def test_wrong_schema(self, make_evidence):
        fact_dict = load_holdings("holding_cardenas.json")[1]["inputs"][0]
        wrong_schema = schemas.EvidenceSchema()
        with pytest.raises(ValidationError):
            wrong_schema.load(fact_dict)


class TestEvidenceDump:
    def test_dump_evidence(self, make_evidence):
        evidence = make_evidence["shooting"]
        schema = schemas.EvidenceSchema()
        dumped = schema.dump(evidence)
        assert dumped["exhibit"]["statement_attribution"]["name"] == "Alice"


class TestPleadingDump:
    def test_dump_pleading(self, make_pleading):
        pleading = make_pleading["craig"]
        schema = schemas.PleadingSchema()
        dumped = schema.dump(pleading)
        assert dumped["filer"]["name"] == "Craig"


class TestAllegationDump:
    def test_dump_allegation(self, make_allegation):
        allegation = make_allegation["shooting"]
        schema = schemas.AllegationSchema()
        dumped = schema.dump(allegation)
        assert dumped["statement"]["context_factors"][0]["name"] == "Alice"
