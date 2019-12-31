import pytest

from authorityspoke.predicates import Predicate, Q_


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
        assert make_predicate["p7_obverse"].quantity == Q_(35, "foot")
        assert make_predicate["p7"].truth is True
        assert make_predicate["p7"].comparison == "<="
        assert make_predicate["p7_obverse"].comparison == "<="

    def test_quantity_type(self, make_predicate):
        assert isinstance(make_predicate["p7"].quantity, Q_)

    def test_quantity_string(self, make_predicate):
        assert str(make_predicate["p7"].quantity) == "35 foot"

    def test_predicate_content_comparison(self, make_predicate):
        assert make_predicate["p8_exact"].content == make_predicate["p7"].content

    def test_quantity_comparison(self, make_predicate):
        assert make_predicate["p7"].quantity_comparison() == "no more than 35 foot"
        assert make_predicate["p9"].quantity_comparison() == "no more than 5 foot"
        assert make_predicate["p1"].quantity_comparison() == ""

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

    @pytest.mark.parametrize(
        "sentence, index, expected",
        [
            (
                "{} was names, towns, and telephone numbers of telephone subscribers",
                0,
                "{} were names, towns,",
            ),
            (
                "all of {} and {} was at the meeting",
                0,
                "all of {} and {} was at the meeting",
            ),
            (
                "all of {} and {} was at the meeting",
                1,
                "all of {} and {} were at the meeting",
            ),
        ],
    )
    def test_make_str_plural(self, sentence, index, expected):
        plural_version = Predicate.make_context_plural(sentence=sentence, index=index)
        assert plural_version.startswith(expected)

    def test_str_not_equal(self, make_predicate):
        assert "the distance between {} and {} was not equal to 35 foot" in str(
            make_predicate["p7_not_equal"]
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
        """
        These don't evaluate equal because they don't have the same
        string, but the :meth:`.Predicate.means` method considers them
        to have the same meaning.
        """
        assert not make_predicate["p8_int"] == make_predicate["p8_float"]
        assert make_predicate["p8_int"].means(make_predicate["p8_float"])

    def test_no_equality_with_inconsistent_dimensionality(self, make_predicate):
        assert make_predicate["p9"] != make_predicate["p9_acres"]

    def test_different_truth_value_prevents_equality(self, make_predicate):
        assert make_predicate["p_murder"] != make_predicate["p_murder_whether"]
        assert make_predicate["p_murder_false"] != make_predicate["p_murder_whether"]
        assert make_predicate["p_murder_false"] != make_predicate["p_murder"]

    def test_predicate_does_not_mean_fact(self, make_predicate, watt_factor):
        assert not make_predicate["p8"].means(watt_factor["f8"])

    # Implication

    def test_greater_than_because_of_quantity(self, make_predicate):
        assert make_predicate["p8_meters"] > make_predicate["p8"]
        assert make_predicate["p8_meters"] != make_predicate["p8"]

    def test_greater_float_and_int(self, make_predicate):
        assert make_predicate["p8_higher_int"] > make_predicate["p8_float"]
        assert make_predicate["p8_int"] < make_predicate["p8_higher_int"]

    def test_any_truth_value_implies_none(self, make_predicate):
        assert make_predicate["p_murder"] > make_predicate["p_murder_whether"]
        assert make_predicate["p_murder_false"] > make_predicate["p_murder_whether"]

    def test_no_implication_by_equal_quantity(self, make_predicate):
        assert not make_predicate["p_quantity=3"] > make_predicate["p_quantity>5"]

    def test_no_implication_of_equal_quantity(self, make_predicate):
        assert not make_predicate["p_quantity>5"] > make_predicate["p_quantity=3"]

    def test_no_implication_by_greater_or_equal_quantity(self, make_predicate):
        assert not make_predicate["p_quantity>=4"] > make_predicate["p_quantity>5"]

    def test_no_implication_of_greater_or_equal_quantity(self):
        less = Predicate(
            content="The number of mice was {}", comparison=">", quantity=4
        )
        more = Predicate(
            content="The number of mice was {}", comparison=">=", quantity=5
        )
        assert not less.implies(more)

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

    def test_contradiction_by_exact(self, make_predicate):
        assert make_predicate["p8_exact"].contradicts(make_predicate["p8_less"])

    def test_contradiction_of_exact(self, make_predicate):
        assert make_predicate["p8_less"].contradicts(make_predicate["p8_exact"])

    def test_contradiction_by_equal_quantity(self, make_predicate):
        assert make_predicate["p_quantity=3"].contradicts(
            make_predicate["p_quantity>5"]
        )

    def test_contradiction_of_equal_quantity(self, make_predicate):
        assert make_predicate["p_quantity>5"].contradicts(
            make_predicate["p_quantity=3"]
        )

    def test_no_contradiction_by_greater_or_equal_quantity(self, make_predicate):
        assert not make_predicate["p_quantity>=4"].contradicts(
            make_predicate["p_quantity>5"]
        )

    def test_no_contradiction_of_greater_or_equal_quantity(self, make_predicate):
        assert not make_predicate["p_quantity>5"].contradicts(
            make_predicate["p_quantity>=4"]
        )

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
