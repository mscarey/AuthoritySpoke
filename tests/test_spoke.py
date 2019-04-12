import datetime
import json
import operator

from pint import UnitRegistry
import pytest

from authorityspoke.entities import Human, Event
from authorityspoke.factors import Predicate, Factor, Entity, Fact
from authorityspoke.opinions import Opinion
from authorityspoke.factors import ureg, Q_


class TestEntities:
    def test_conversion_to_generic(self, make_entity):
        e = make_entity
        assert e["motel_specific"].make_generic() == e["motel"]

    def test_same_object_after_make_generic(self, make_entity):
        e = make_entity
        motel = e["motel"]
        motel_b = motel.make_generic()
        assert motel is motel_b

    def test_context_register(self, make_entity):
        """
        Class "Human" implies "Entity" but not vice versa.
        """
        motel = make_entity["motel"]
        watt = make_entity["watt"]
        empty_update = motel.context_register(watt, operator.ge)
        assert not any(register is not None for register in empty_update)

        update = motel.context_register(watt, operator.le)
        assert any(register == {motel: watt, watt: motel} for register in update)

    def test_new_context(self, make_entity):
        changes = {
            make_entity["motel"]: Entity("Death Star"),
            make_entity["watt"]: Human("Darth Vader"),
        }
        motel = make_entity["motel"]
        assert motel.new_context(changes) == changes[make_entity["motel"]]

    # Equality

    def test_specific_to_generic_different_object(self, make_entity):
        e = make_entity
        motel = e["motel_specific"]
        motel_b = motel.make_generic()
        assert not motel is motel_b
        assert not motel == motel_b

    def test_equality_generic_entities(self, make_entity):
        e = make_entity
        assert e["motel"] == e["trees"]
        assert e["motel"] is not e["trees"]

    def test_generic_human_and_event_not_equal(self, make_entity):
        """Neither is a subclass of the other."""
        assert make_entity["tree_search"] != make_entity["watt"]

    def test_generic_human_and_entity_not_equal(self, make_entity):
        """Human is a subclass of Entity."""
        assert make_entity["motel"] != make_entity["watt"]

    # Implication

    def test_implication_generic_entities(self, make_entity):
        assert make_entity["motel_specific"] > make_entity["trees"]
        assert not make_entity["motel_specific"] < make_entity["trees"]

    def test_implication_same_except_generic(self, make_entity):
        assert make_entity["motel_specific"] > make_entity["motel"]
        assert not make_entity["motel_specific"] < make_entity["motel"]

    def test_same_entity_not_ge(self, make_entity):
        assert not make_entity["motel"] > make_entity["motel"]

    def test_implication_subclass(self, make_entity):
        assert make_entity["tree_search_specific"] >= make_entity["motel"]
        assert make_entity["tree_search"] > make_entity["motel"]

    def test_implication_superclass(self, make_entity):
        assert not make_entity["trees"] >= make_entity["tree_search"]

    # Contradiction

    def test_error_contradiction_with_non_factor(self, make_entity, make_predicate):
        with pytest.raises(TypeError):
            assert make_entity["trees"].contradicts(make_predicate["p3"])

    def test_no_contradiction_of_other_factor(self, make_entity, watt_factor):
        assert not make_entity["trees"].contradicts(make_entity["watt"])
        assert not make_entity["trees"].contradicts(watt_factor["f1"])


class TestPredicates:
    def test_predicate_with_wrong_number_of_entities(self):
        with pytest.raises(ValueError):
            _ = Predicate("{} was a motel", reciprocal=True)

    def test_predicate_with_wrong_comparison_symbol(self):
        with pytest.raises(ValueError):
            _ = Predicate(
                "the height of {} was {}",
                comparison=">>",
                quantity=Q_("160 centimeters"),
            )

    def test_convert_false_statement_about_quantity_to_obverse(self, make_predicate):
        assert make_predicate["p7_obverse"].truth is True
        assert make_predicate["p7_obverse"].quantity == ureg.Quantity(35, "foot")
        assert make_predicate["p7"].truth is True
        assert make_predicate["p7"].comparison == "<="
        assert make_predicate["p7_obverse"].comparison == "<="

    def test_quantity_type(self, make_predicate):
        assert isinstance(make_predicate["p7"].quantity, ureg.Quantity)

    def test_quantity_string(self, make_predicate):
        assert str(make_predicate["p7"].quantity) == "35 foot"

    def test_predicate_content_comparison(self, make_predicate):
        assert make_predicate["p8_exact"].content == make_predicate["p7"].content

    def test_quantity_comparison(self, make_predicate):
        assert make_predicate["p7"].quantity_comparison() == "no more than 35 foot"
        assert make_predicate["p9"].quantity_comparison() == "no more than 5 foot"
        assert make_predicate["p1"].quantity_comparison() is None

    def test_context_slots(self, make_predicate):
        assert make_predicate["p7"].context_slots == 2

    def test_str_for_predicate_with_number_quantity(self, make_predicate):
        assert "distance between {} and {} was at least 20" in str(
            make_predicate["p8_int"]
        )
        assert "distance between {} and {} was at least 20.0" in str(
            make_predicate["p8_float"]
        )
        assert "distance between {} and {} was at least 20 foot" in str(
            make_predicate["p8"]
        )

    def test_negated_method(self, make_predicate):
        assert make_predicate["p7"].negated() == make_predicate["p7_opposite"]
        assert make_predicate["p3"].negated() == make_predicate["p3_false"]

    # Equality

    def test_predicate_equality(self, make_predicate):
        assert make_predicate["p1"] == make_predicate["p1_again"]

    def test_predicate_inequality(self, make_predicate, watt_factor):
        assert make_predicate["p2"] != make_predicate["p2_reciprocal"]
        assert make_predicate["p2"] != watt_factor["f2"]

    def test_obverse_predicates_equal(self, make_predicate):
        assert make_predicate["p7"] == make_predicate["p7_obverse"]

    def test_equal_float_and_int(self, make_predicate):
        assert make_predicate["p8_int"] == make_predicate["p8_float"]

    def test_no_equality_with_inconsistent_dimensionality(self, make_predicate):
        assert make_predicate["p9"] != make_predicate["p9_acres"]

    def test_different_truth_value_prevents_equality(self, make_predicate):
        assert make_predicate["p_murder"] != make_predicate["p_murder_whether"]
        assert make_predicate["p_murder_false"] != make_predicate["p_murder_whether"]
        assert make_predicate["p_murder_false"] != make_predicate["p_murder"]

    # Implication

    def test_greater_than_because_of_quantity(self, make_predicate):
        assert make_predicate["p8_meters"] > make_predicate["p8"]
        assert make_predicate["p8_meters"] != make_predicate["p8"]

    def test_greater_float_and_int(self, make_predicate):
        assert make_predicate["p8_higher_int"] > make_predicate["p8_float"]
        assert make_predicate["p8_int"] < make_predicate["p8_higher_int"]
        p8_float_more = Predicate.from_string(
            "the distance between {Ann} and {Lee} was {>= 20.1}", reciprocal=True
        )[0]
        assert p8_float_more > make_predicate["p8_int"]

    def test_any_truth_value_implies_none(self, make_predicate):
        assert make_predicate["p_murder"] > make_predicate["p_murder_whether"]
        assert make_predicate["p_murder_false"] > make_predicate["p_murder_whether"]

    def test_equal_implies_greater_or_equal(self, make_predicate):
        assert make_predicate["p9_exact"] > make_predicate["p9"]

    def test_implication_with_not_equal(self, make_predicate):
        assert make_predicate["p7_opposite"] > make_predicate["p7_not_equal"]

    def test_no_implication_with_inconsistent_dimensionality(self, make_predicate):
        assert not make_predicate["p9"] >= make_predicate["p9_acres"]
        assert not make_predicate["p9"] <= make_predicate["p9_acres"]

    def test_implication_with_no_truth_value(self, make_predicate):
        assert not make_predicate["p2_no_truth"] > make_predicate["p2"]
        assert make_predicate["p2"] > make_predicate["p2_no_truth"]

    def test_error_predicate_imply_factor(self, make_predicate, watt_factor):
        with pytest.raises(TypeError):
            assert make_predicate["p7_true"] > (watt_factor["f7"])
        with pytest.raises(TypeError):
            assert make_predicate["p7_true"] >= (watt_factor["f7"])

    def test_predicate_implies_none(self, make_predicate):
        assert make_predicate["p7_true"] > None

    # Contradiction

    def test_predicate_contradictions(self, make_predicate):
        assert make_predicate["p7"].contradicts(make_predicate["p7_true"])
        assert not make_predicate["p1"].contradicts(make_predicate["p1_again"])
        assert not make_predicate["p3"].contradicts(make_predicate["p7"])

    def test_contradiction_with_exact(self, make_predicate):
        assert make_predicate["p8_exact"].contradicts(make_predicate["p8_less"])
        assert make_predicate["p8_less"].contradicts(make_predicate["p8_exact"])

    def test_error_predicate_contradict_factor(self, make_predicate, watt_factor):
        with pytest.raises(TypeError):
            make_predicate["p7_true"].contradicts(watt_factor["f7"])

    def test_no_contradiction_with_no_truth_value(self, make_predicate):
        assert not make_predicate["p2_no_truth"].contradicts(make_predicate["p2"])
        assert not make_predicate["p2"].contradicts(make_predicate["p2_no_truth"])

    def test_no_contradiction_with_inconsistent_dimensionality(self, make_predicate):
        assert not make_predicate["p9"].contradicts(make_predicate["p9_acres"])
        assert not make_predicate["p9_acres"].contradicts(make_predicate["p9"])

    def test_no_contradiction_of_none(self, make_predicate):
        assert not make_predicate["p7_true"].contradicts(None)

    def test_contradiction_with_quantity(self, make_predicate):
        assert make_predicate["p8_less"].contradicts(make_predicate["p8_meters"])
