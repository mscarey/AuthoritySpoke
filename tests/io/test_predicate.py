from datetime import date
from decimal import Decimal

from nettlesome.predicates import Predicate

import pytest

from nettlesome.quantities import Comparison, Q_


class TestPredicateLoad:
    """
    This tests a function for importing a Predicate by itself,
    but Predicate imports can also happen as part of a Fact import.
    """

    def test_load_just_content(self):
        data = {"content": "$person was on the premises of $place"}
        p4 = Predicate(**data)
        assert p4.truth is True

    def test_load_comparison_not_ending_with_was(self):
        data = {
            "content": "the distance between $place1 and $place2 was 35 feet",
            "truth": True,
            "sign": "!=",
            "expression": "35 feet",
        }
        with pytest.raises(ValueError):
            Comparison(**data)

    def test_load_comparison(self):
        data = {
            "content": "the distance between $place1 and $place2 was",
            "truth": True,
            "sign": "!=",
            "expression": "35 feet",
        }
        p7 = Comparison(**data)
        assert p7.sign == "!="

    def test_load_and_normalize_quantity(self):
        data = {
            "content": "the distance between $place1 and $place2 was",
            "sign": "!=",
            "expression": "35 feet",
            "truth": True,
        }
        p7 = Comparison(**data)
        assert p7.sign == "!="

    def test_load_and_normalize_comparison(self):
        data = {
            "content": "the distance between $place1 and $place2 was",
            "truth": True,
            "sign": "!=",
            "expression": "35 feet",
        }
        statement = Comparison(**data)
        assert statement.sign == "!="

    def test_make_comparison_when_absent(self):
        statement = Comparison(
            **{"content": "$person's favorite number was", "expression": 42}
        )
        assert statement.sign == "=="
        assert "$person's favorite number was exactly equal to 42" in str(statement)
        assert len(statement) == 1

    def test_load_predicate_with_date_expression(self):
        data = {
            "content": "the date when $work was created was",
            "expression": "1978-01-01",
            "sign": ">=",
            "truth": True,
        }
        statement = Comparison(**data)
        assert statement.quantity == date(1978, 1, 1)


class TestPredicateDump:
    def test_dump_to_dict_with_units(self):
        predicate = Comparison(
            content="the distance between $place1 and $place2 was",
            truth=True,
            sign="<>",
            expression=Q_("35 feet"),
        )
        dumped = predicate.model_dump()
        assert dumped["quantity_range"]["quantity_magnitude"] == Decimal("35")

    def test_round_trip(self):
        statement = Comparison(
            **{"content": "{}'s favorite number was", "expression": 42}
        )
        dumped = statement.model_dump()
        new_statement = Comparison(**dumped)
        assert "{}'s favorite number was exactly equal to 42" in str(new_statement)

    def test_dump_predicate_with_date_expression(self):
        copyright_date_range = Comparison(
            content="the date when $work was created was",
            sign=">=",
            expression=date(1978, 1, 1),
        )
        dumped = copyright_date_range.model_dump()
        assert dumped["quantity_range"]["quantity"] == date(1978, 1, 1)
