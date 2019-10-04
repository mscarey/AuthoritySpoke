import pint
import pytest

from authorityspoke.predicates import Predicate
from authorityspoke.io import readers, schemas
from authorityspoke.io.dump import to_dict, to_json

ureg = pint.UnitRegistry()


class TestPredicateLoad:
    """
    This tests a function for importing a Predicate by itself,
    but Predicate imports can also happen as part of a Fact import.
    """

    def test_load_just_content(self):
        schema = schemas.PredicateSchema()
        p4 = schema.load({"content": "{} was on the premises of {}"})
        assert p4.truth is True
        assert p4.comparison == ""

    def test_load_comparison(self):
        schema = schemas.PredicateSchema()
        p7 = schema.load(
            {
                "content": "the distance between {} and {} was {}",
                "truth": True,
                "reciprocal": True,
                "comparison": "!=",
                "quantity": "35 feet",
            }
        )
        assert p7.comparison == "<>"

    def test_load_and_find_quantity(self):
        schema = schemas.PredicateSchema()
        p7 = schema.load(
            data={
                "content": "the distance between {} and {} was > 35 feet",
                "truth": True,
                "reciprocal": True,
            }
        )
        assert p7.comparison == ">"

    def test_load_and_normalize_quantity(self):
        schema = schemas.PredicateSchema()
        p7 = schema.load(
            data={
                "content": "the distance between {} and {} was != 35 feet",
                "truth": True,
                "reciprocal": True,
            }
        )
        assert p7.comparison == "<>"

    def test_load_and_normalize_comparison(self):
        schema = schemas.PredicateSchema()
        p7 = schema.load(
            data={
                "content": "the distance between {} and {} was {}",
                "truth": True,
                "reciprocal": True,
                "comparison": "!=",
                "quantity": "35 feet",
            }
        )
        assert p7.comparison == "<>"

    def test_read_quantity(self):
        quantity = schemas.read_quantity("35 feet")
        assert str(quantity.units) == "foot"

    def test_make_comparison_when_absent(self):
        schema = schemas.PredicateSchema()
        statement = schema.load(
            {"content": "{}'s favorite number is {}", "quantity": 42}
        )
        assert statement.comparison == "="
        assert "{}'s favorite number is exactly equal to 42" in str(statement)
        assert len(statement) == 1


class TestPredicateDump:
    def test_dump_to_dict_with_units(self):
        predicate = Predicate(
            "the distance between {} and {} was {}",
            truth=True,
            reciprocal=True,
            comparison="<>",
            quantity=ureg.Quantity("35 feet"),
        )
        dumped = to_dict(predicate)
        assert dumped["quantity"] == "35 foot"

    def test_round_trip(self):
        schema = schemas.PredicateSchema()
        statement = schema.load(
            {"content": "{}'s favorite number is {}", "quantity": 42}
        )
        dumped = to_dict(statement)
        new_statement = readers.read_predicate(dumped)
        assert "{}'s favorite number is exactly equal to 42" in str(new_statement)
