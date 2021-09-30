from datetime import date
from nettlesome.predicates import Predicate

import pytest

from nettlesome.quantities import Comparison, Q_

from authorityspoke.io import schemas_yaml


class TestPredicateLoad:
    """
    This tests a function for importing a Predicate by itself,
    but Predicate imports can also happen as part of a Fact import.
    """

    def test_load_just_content(self):
        schema = schemas_yaml.PredicateSchema()
        p4 = schema.load({"content": "$person was on the premises of $place"})
        assert p4.truth is True

    def test_load_comparison_not_ending_with_was(self):
        schema = schemas_yaml.PredicateSchema()
        with pytest.raises(ValueError):
            schema.load(
                {
                    "content": "the distance between $place1 and $place2 was 35 feet",
                    "truth": True,
                    "sign": "!=",
                    "expression": "35 feet",
                }
            )

    def test_load_comparison(self):
        schema = schemas_json.PredicateSchema()
        p7 = schema.load(
            {
                "content": "the distance between $place1 and $place2 was",
                "truth": True,
                "sign": "!=",
                "expression": "35 feet",
            }
        )
        assert p7.sign == "!="

    def test_load_and_find_quantity(self):
        schema = schemas_yaml.PredicateSchema()
        p7 = schema.load(
            data={
                "content": "the distance between $place1 and $place2 was > 35 feet",
                "truth": True,
            }
        )
        assert p7.sign == ">"

    def test_load_and_normalize_quantity(self):
        schema = schemas_yaml.PredicateSchema()
        p7 = schema.load(
            data={
                "content": "the distance between $place1 and $place2 was != 35 feet",
                "truth": True,
            }
        )
        assert p7.sign == "!="

    def test_load_and_normalize_comparison(self):
        schema = schemas_json.PredicateSchema()
        p7 = schema.load(
            data={
                "content": "the distance between $place1 and $place2 was",
                "truth": True,
                "sign": "!=",
                "expression": "35 feet",
            }
        )
        assert p7.sign == "!="

    def test_read_quantity(self):
        quantity = Comparison.read_quantity("35 feet")
        assert str(quantity.units) == "foot"

    def test_make_comparison_when_absent(self):
        schema = schemas_yaml.PredicateSchema()
        statement = schema.load(
            {"content": "$person's favorite number was", "expression": 42}
        )
        assert statement.sign == "=="
        assert "$person's favorite number was exactly equal to 42" in str(statement)
        assert len(statement) == 1

    def test_load_predicate_with_date_expression(self):
        schema = schemas_yaml.PredicateSchema()
        data = {
            "content": "the date when $work was created was",
            "expression": "1978-01-01",
            "sign": ">=",
            "truth": True,
        }
        statement = schema.load(data)
        assert statement.quantity == date(1978, 1, 1)


class TestPredicateDump:
    def test_dump_to_dict_with_units(self):
        predicate = Comparison(
            content="the distance between $place1 and $place2 was",
            truth=True,
            sign="<>",
            expression=Q_("35 feet"),
        )
        dumped = predicate.dict()
        assert dumped["expression"] == "35 foot"

    def test_round_trip(self):
        statement = Predicate.load(
            {"content": "{}'s favorite number was", "expression": 42}
        )
        dumped = statement.dict()
        new_statement = Predicate(**dumped)
        assert "{}'s favorite number was exactly equal to 42" in str(new_statement)

    def test_dump_predicate_with_date_expression(self):
        copyright_date_range = Comparison(
            content="the date when $work was created was",
            sign=">=",
            expression=date(1978, 1, 1),
        )
        dumped = copyright_date_range.dict()
        assert dumped["expression"] == "1978-01-01"
