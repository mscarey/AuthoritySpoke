import json
import os
import pathlib

from pydantic import ValidationError
from legislice import Enactment
from nettlesome.entities import Entity
from nettlesome.terms import TermSequence
from nettlesome.predicates import Predicate
from nettlesome.quantities import Comparison, QuantityRange

import pytest

from authorityspoke.facts import Fact, Exhibit, Evidence
from authorityspoke.io.name_index import index_names
from authorityspoke.io import readers
from authorityspoke.io import schemas_yaml
from authorityspoke.io.loaders import load_holdings
from authorityspoke.io import filepaths
from authorityspoke.io.text_expansion import expand_shorthand


class TestFactorFileLoad:
    def test_find_directory_for_json(self):
        directory = pathlib.Path.cwd() / "tests"
        if directory.exists():
            os.chdir(directory)
        input_directory = filepaths.get_directory_path("holdings") / "holding_watt.yaml"
        assert input_directory.exists()


class TestEntityLoad:
    def test_get_entity_schema(self):
        record = {"name": "George Washington"}
        obj = Entity(**record)
        assert obj.name == "George Washington"
        assert isinstance(obj, Entity)

    def test_load_entity_from_factor_schema(self):
        record = {"name": "George Washington"}
        george = Entity(**record)
        assert george.generic is True

    def test_load_and_dump_entity_from_entity_schema(self):

        record = {"name": "John Adams"}
        john = Entity(**record)
        assert john.generic is True
        john_dict = john.dict()
        assert john_dict["generic"] is True


class TestFactLoad:
    house_data = {
        "content": "the price in dollars at which {Alice} sold {Alice's house} was > 300000"
    }
    story_data = {"content": "The number of castles {the king} had was > 3"}

    def test_import_fact_with_entity_name_containing_another(self):
        expanded = expand_shorthand(self.house_data)
        record, mentioned = index_names(expanded)

        assert mentioned["Alice's house"]["type"] == "Entity"

    def test_import_predicate_with_quantity(self):
        story = readers.read_fact(self.story_data)
        assert len(story.predicate) == 1
        assert story.predicate.content.startswith("The number of castles")
        assert story.predicate.sign == ">"
        assert story.predicate.quantity == 3

    def test_make_fact_from_string(self, watt_factor):
        fact_float_data = {
            "content": "the distance between $person0 and $person1 was >= 20.1",
            "terms": [
                {"type": "Entity", "name": "Ann"},
                {"type": "Entity", "name": "Lee"},
            ],
        }
        fact_float_more = expand_shorthand(fact_float_data)
        fact_float_more = readers.read_fact(fact_float_more)
        fact_float_less = watt_factor["f8_int"]
        assert fact_float_more >= fact_float_less


class TestFactorLoad:
    def test_load_factor_marked_reciprocal(self):
        fact = Fact(
            predicate=Comparison(
                content="the distance between $place1 and $place2 was",
                sign="<",
                expression="5 miles",
            ),
            terms=TermSequence(
                [Entity(name="the apartment"), Entity(name="the office")]
            ),
        )
        assert hasattr(fact.predicate.quantity, "dimensionality")
        data = {
            "type": "fact",
            "content": "the distance between ${place1} and ${place2} was",
            "sign": "<",
            "expression": "5 miles",
            "terms": [
                {"type": "entity", "name": "the office"},
                {"type": "entity", "name": "the apartment"},
            ],
        }
        loaded_fact = readers.read_factor(data)
        assert loaded_fact.means(fact)

    def test_import_fact_with_factor_schema(self):
        loaded = load_holdings("holding_cardenas.yaml")
        entity = readers.read_factor(loaded[0]["inputs"][0])
        inner_context = entity.terms[0].terms[0]
        assert inner_context.name == "the defendant"

    def test_import_facts_with_factor_schema(self):
        loaded = load_holdings("holding_cardenas.yaml")
        factor = readers.read_factors(loaded[0]["inputs"])[1].terms[0]
        assert (
            factor.predicate.content
            == "${the_defendant} committed an attempted robbery"
        )


class TestFactDump:
    def test_dump_with_quantity(self, watt_factor):
        f8_dict = watt_factor["f8"].dict()
        assert f8_dict["predicate"]["expression"] == "20 foot"

    def test_dump_complex_fact(self, make_complex_fact):
        relevant_fact = make_complex_fact["f_relevant_murder"]
        relevant_dict = relevant_fact.dict()
        shooting_dict = relevant_dict["terms"][0]
        assert shooting_dict["terms"][0]["name"] == "Alice"


class TestExhibitLoad:
    def test_load_exhibit_with_bracketed_names(self):
        fact_data = {
            "content": "the distance that $officer pursued $suspect was >= 5 miles",
            "terms": [
                {"type": "Entity", "name": "Officer Lin"},
                {"type": "Entity", "name": "Al"},
            ],
        }
        exhibit_data = {
            "form": "testimony",
            "statement": fact_data,
            "statement_attribution": {"name": "Officer Lin"},
        }
        schema = schemas_yaml.ExhibitSchema()
        exhibit = schema.load(exhibit_data)
        assert str(exhibit) == (
            "the testimony attributed to <Officer Lin>, "
            "asserting the fact that the distance that <Officer Lin> "
            "pursued <Al> was at least 5 mile,"
        )


class TestExhibitDump:
    def test_dump_exhibit(self, make_exhibit):
        exhibit = make_exhibit["shooting_affidavit"]
        dumped = exhibit.dict()
        assert dumped["statement"]["terms"][0]["name"] == "Alice"

    def test_dump_and_load_exhibit(self, make_exhibit):
        exhibit = make_exhibit["no_shooting_entity_order_testimony"]
        dumped = exhibit.dict()
        loaded = Exhibit(**dumped)
        assert loaded.form == "testimony"
        assert loaded.statement_attribution.name == "Bob"


class TestEvidenceLoad:
    def test_wrong_schema(self, make_evidence):
        fact_dict = load_holdings("holding_cardenas.yaml")[1]["inputs"][0]
        with pytest.raises(ValidationError):
            Evidence(**fact_dict)


class TestEvidenceDump:
    def test_dump_evidence(self, make_evidence):
        evidence = make_evidence["shooting"]
        dumped = evidence.dict()
        assert dumped["exhibit"]["statement_attribution"]["name"] == "Alice"


class TestPleading:
    def test_pleading_short_string(self, make_pleading):
        pleading = make_pleading["craig"]
        assert pleading.short_string == "the pleading filed by <Craig>"


class TestPleadingDump:
    def test_dump_pleading(self, make_pleading):
        pleading = make_pleading["craig"]
        dumped = pleading.dict()
        assert dumped["filer"]["name"] == "Craig"


class TestAllegationDump:
    def test_dump_allegation(self, make_allegation):
        allegation = make_allegation["shooting"]
        dumped = allegation.dict()
        assert dumped["fact"]["terms"][0]["name"] == "Alice"
