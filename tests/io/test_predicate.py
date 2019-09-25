import pint
import pytest

from authorityspoke.predicates import Predicate
from authorityspoke.io import readers
from authorityspoke.io.dump import to_dict, to_json

ureg = pint.UnitRegistry()


class TestPredicateLoad:
    """
    This tests a function for importing a Predicate by itself,
    but Predicate imports can also happen as part of a Fact import.
    """

    def test_load_and_normalize_comparison(self):
        p7_not_equal = (
            readers.read_predicate(
                {
                    "content": "the distance between {} and {} was {}",
                    "truth": True,
                    "reciprocal": True,
                    "comparison": "!=",
                    "quantity": 35,
                    "units": "feet",
                }
            ),
        )
        assert p7_not_equal.comparison == "<>"

    def test_dump_to_dict_with_units(self):
        predicate = Predicate(
            "the distance between {} and {} was {}",
            truth=True,
            reciprocal=True,
            comparison="<>",
            quantity=ureg.Quantity("35 feet"),
        )
        dumped = to_dict(predicate)
        assert dumped["quantity"] == 35
        assert dumped["units"] == "feet"
