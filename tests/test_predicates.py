from datetime import date
from typing import Type
import pytest
import sympy
from sympy import Interval, oo


from nettlesome.entities import Entity
from nettlesome.predicates import Predicate
from nettlesome.quantities import Comparison, Q_, Quantity


class TestComparisons:
    def test_comparison_with_wrong_comparison_symbol(self):
        with pytest.raises(ValueError):
            _ = Comparison(
                "the height of {} was {}",
                sign=">>",
                expression=Q_("160 centimeters"),
            )

    def test_comparison_interval(self):
        comparison = Comparison(
            "the distance between $place1 and $place2 was",
            sign=">",
            expression=Q_("20 miles"),
        )
        assert comparison.interval == Interval(20, oo, left_open=True)

    def test_comparison_not_equal(self):
        comparison = Comparison(
            "the distance between $place1 and $place2 was",
            sign="!=",
            expression=Q_("20 miles"),
        )
        assert comparison.interval == sympy.Union(
            Interval(0, 20, right_open=True), Interval(20, oo, left_open=True)
        )


class TestPredicates:
    def test_no_sign_allowed_for_predicate(self):
        with pytest.raises(TypeError):
            Predicate(
                "the date when $work was created was",
                sign=">=",
                expression=date(1978, 1, 1),
            )

    def test_term_positions(self):
        predicate = Predicate(
            content="$organizer1 and $organizer2 planned for $player1 to play $game with $player2."
        )
        assert predicate.term_positions() == {
            "organizer1": {0, 1},
            "organizer2": {0, 1},
            "player1": {2, 4},
            "game": {3},
            "player2": {2, 4},
        }

    def test_term_positions_with_repetition(self):
        predicate = Predicate(
            content="$organizer1 and $organizer2 planned for $organizer1 to play $game with $organizer2."
        )
        assert predicate.term_positions() == {
            "organizer1": {0, 1},
            "organizer2": {0, 1},
            "game": {2},
        }

    def test_term_permutations(self):
        predicate = Predicate(
            content="$organizer1 and $organizer2 planned for $player1 to play $game with $player2."
        )
        assert predicate.term_index_permutations() == [
            (0, 1, 2, 3, 4),
            (0, 1, 4, 3, 2),
            (1, 0, 2, 3, 4),
            (1, 0, 4, 3, 2),
        ]

    def test_term_permutations_with_repetition(self):
        predicate = Predicate(
            content="$organizer1 and $organizer2 planned for $organizer1 to play $game with $organizer2."
        )
        assert predicate.term_index_permutations() == [
            (0, 1, 2),
            (1, 0, 2),
        ]

    def test_convert_false_statement_about_quantity_to_obverse(self, make_predicate):
        assert make_predicate["p7_obverse"].truth is True
        assert make_predicate["p7_obverse"].quantity == Q_(35, "foot")
        assert make_predicate["p7"].truth is True
        assert make_predicate["p7"].sign == "<="
        assert 'sign="<="' in repr(make_predicate["p7"])
        assert make_predicate["p7_obverse"].sign == "<="

    def test_quantity_type(self, make_predicate):
        assert isinstance(make_predicate["p7"].quantity, Quantity)

    def test_string_for_date_as_expression(self):
        copyright_date_range = Comparison(
            "the date when $work was created was",
            sign=">=",
            expression=date(1978, 1, 1),
        )
        assert str(copyright_date_range).endswith("1978-01-01")

    def test_quantity_string(self, make_predicate):
        assert str(make_predicate["p7"].quantity) == "35 foot"

    def test_predicate_content_comparison(self, make_predicate):
        assert make_predicate["p8_exact"].content == make_predicate["p7"].content

    def test_expression_comparison(self, make_predicate):
        assert str(make_predicate["p7"].quantity_range) == "no more than 35 foot"
        assert str(make_predicate["p9"].quantity_range) == "no more than 5 foot"

    def test_predicate_has_no_expression_comparison(self, make_predicate):
        with pytest.raises(AttributeError):
            make_predicate["p1"].expression_comparison() == ""

    def test_context_slots(self, make_predicate):
        assert len(make_predicate["p7"]) == 2

    def test_str_for_predicate_with_number_quantity(self, make_predicate):
        assert "distance between $place1 and $place2 was at least 20" in str(
            make_predicate["p8_int"]
        )
        assert "distance between $place1 and $place2 was at least 20.0" in str(
            make_predicate["p8_float"]
        )
        assert "distance between $place1 and $place2 was at least 20 foot" in str(
            make_predicate["p8"]
        )

    def test_template_singular_by_default(self):
        predicate = Predicate("$people were in $city")
        assert str(predicate.template) == 'StatementTemplate("$people was in $city")'

    @pytest.mark.parametrize(
        "context, expected",
        [
            (
                [Entity(name="the book", plural=False)],
                "<the book> was names, towns,",
            ),
            (
                [Entity(name="the book's listings", plural=True)],
                "<the book's listings> were names, towns,",
            ),
        ],
    )
    def test_make_str_plural(self, context, expected):
        phrase = (
            "$thing were names, towns, and telephone numbers of telephone subscribers"
        )
        predicate = Predicate(phrase)
        with_context = predicate._content_with_terms(context)
        assert with_context.startswith(expected)

    def test_str_not_equal(self, make_predicate):
        assert (
            "the distance between $place1 and $place2 was not equal to 35 foot"
            in str(make_predicate["p7_not_equal"])
        )

    def test_negated_method(self, make_predicate):
        assert make_predicate["p7"].negated().means(make_predicate["p7_opposite"])
        assert make_predicate["p3"].negated().means(make_predicate["p3_false"])


class TestSameMeaning:
    def test_predicate_equality(self, make_predicate):
        assert make_predicate["p1"].means(make_predicate["p1_again"])

    def test_predicate_inequality(self, make_predicate, watt_factor):
        assert not make_predicate["p2"].means(make_predicate["p2_reflexive"])

    def test_error_predicate_means_fact(self, make_predicate, watt_factor):
        with pytest.raises(TypeError):
            make_predicate["p2"].means(watt_factor["f2"])

    def test_obverse_predicates_equal(self, make_predicate):
        assert make_predicate["p7"].means(make_predicate["p7_obverse"])

    def test_equal_float_and_int(self, make_predicate):
        """
        These now evaluate equal even though their equal quantities are different types
        """
        assert make_predicate["p8_int"].means(make_predicate["p8_float"])

    def test_same_meaning_float_and_int(self, make_predicate):
        """
        The Predicate means method considers equal quantities of different types to have the same meaning.
        """
        assert make_predicate["p8_int"].means(make_predicate["p8_float"])

    def test_no_equality_with_inconsistent_dimensionality(self, make_predicate):
        assert not make_predicate["p9"].means(make_predicate["p9_acres"])

    def test_different_truth_value_prevents_equality(self, make_predicate):
        assert not make_predicate["p_murder"].means(make_predicate["p_murder_whether"])
        assert not make_predicate["p_murder_false"].means(
            make_predicate["p_murder_whether"]
        )
        assert not make_predicate["p_murder_false"].means(make_predicate["p_murder"])

    def test_predicate_does_not_mean_fact(self, make_predicate, watt_factor):
        with pytest.raises(TypeError):
            make_predicate["p8"].means(watt_factor["f8"])

    def test_term_placeholders_do_not_change_result(self):
        left = Predicate(
            content="$organizer1 and $organizer2 planned for $player1 to play $game with $player2."
        )
        right = Predicate(
            content="$promoter1 and $promoter2 planned for $player1 to play $chess with $player2."
        )
        assert left.means(right)

    def test_term_positions_change_result(self):
        left = Predicate(
            content="$organizer1 and $organizer2 planned for $player1 to play $game with $player2."
        )
        right = Predicate(
            content="$organizer1 and $organizer2 planned for $organizer1 to play $game with $organizer2."
        )
        assert not left.means(right)


class TestImplication:
    def test_greater_than_because_of_quantity(self, make_predicate):
        assert make_predicate["p8_meters"] > make_predicate["p8"]
        assert make_predicate["p8_meters"] != make_predicate["p8"]

    def test_greater_float_and_int(self, make_predicate):
        assert make_predicate["p8_higher_int"] > make_predicate["p8_float"]
        assert make_predicate["p8_int"] < make_predicate["p8_higher_int"]

    def test_any_truth_value_implies_none(self, make_predicate):
        assert make_predicate["p_murder"] > make_predicate["p_murder_whether"]
        assert make_predicate["p_murder_false"] > make_predicate["p_murder_whether"]

    def test_no_implication_by_exact_quantity(self, make_predicate):
        assert not make_predicate["p_quantity=3"] > make_predicate["p_quantity>5"]

    def test_no_implication_of_exact_quantity(self, make_predicate):
        assert not make_predicate["p_quantity>5"] > make_predicate["p_quantity=3"]

    def test_no_implication_by_greater_or_equal_quantity(self, make_predicate):
        assert not make_predicate["p_quantity>=4"] > make_predicate["p_quantity>5"]

    def test_no_implication_of_greater_or_equal_quantity(self):
        less = Comparison(content="The number of mice was", sign=">", expression=4)
        more = Comparison(content="The number of mice was", sign=">=", expression=5)
        assert not less.implies(more)

    def test_no_contradiction_inconsistent_dimensions(self):
        equal = Comparison(
            "${defendant}'s sentence was", sign="=", expression="8 years"
        )
        less = Comparison(
            "${defendant}'s sentence was", sign="<=", expression="10 parsecs"
        )
        assert not equal.contradicts(less)
        assert not equal.implies(less)

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

    def test_predicate_cannot_imply_factor(self, make_predicate, watt_factor):
        assert not make_predicate["p7_true"] > watt_factor["f7"]

    def test_implication_due_to_dates(self):
        copyright_date_range = Comparison(
            "the date when $work was created was",
            sign=">=",
            expression=date(1978, 1, 1),
        )
        copyright_date_specific = Comparison(
            "the date when $work was created was",
            sign="=",
            expression=date(1980, 6, 20),
        )
        assert copyright_date_specific.implies(copyright_date_range)


class TestContradiction:
    def test_predicate_no_contradictions(self, make_predicate):
        assert not make_predicate["p7"].contradicts(make_predicate["p7_true"])
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

    def test_contradiction_with_quantity(self, make_predicate):
        assert make_predicate["p8_less"].contradicts(make_predicate["p8_meters"])

    def test_contradictory_date_ranges(self):
        later = Comparison(
            "the date $dentist became a licensed dentist was",
            sign=">",
            expression=date(2010, 1, 1),
        )
        earlier = Comparison(
            "the date $dentist became a licensed dentist was",
            sign="<",
            expression=date(1990, 1, 1),
        )
        assert later.contradicts(earlier)
        assert earlier.contradicts(later)

    def test_no_contradiction_without_truth_value(self):
        later = Comparison(
            "the date $dentist became a licensed dentist was",
            sign=">",
            expression=date(2010, 1, 1),
            truth=None,
        )
        earlier = Comparison(
            "the date $dentist became a licensed dentist was",
            sign="<",
            expression=date(1990, 1, 1),
        )
        assert not later.contradicts(earlier)
        assert not earlier.contradicts(later)

    def test_no_contradiction_date_and_time_period(self):
        later = Comparison(
            "the date $dentist became a licensed dentist was",
            sign=">",
            expression=date(2010, 1, 1),
        )
        earlier = Comparison(
            "the date $dentist became a licensed dentist was",
            sign="<",
            expression="2000 years",
        )
        assert not later.contradicts(earlier)
        assert not earlier.contradicts(later)

    def test_no_contradiction_irrelevant_quantities(self):
        more_cows = Comparison(
            "the number of cows $person owned was",
            sign=">",
            expression=10,
        )
        fewer_horses = Comparison(
            "the number of horses $person owned was",
            sign="<",
            expression=3,
        )
        assert not more_cows.contradicts(fewer_horses)
        assert not fewer_horses.contradicts(more_cows)

    def test_no_contradiction_of_predicate(self):
        more_cows = Comparison(
            "the number of cows $person owned was",
            sign=">",
            expression=10,
        )
        no_cows = Predicate("the number of cows $person owned was", truth=False)
        assert not more_cows.contradicts(no_cows)
        assert not no_cows.contradicts(more_cows)


class TestQuantities:
    def test_does_not_exclude_other_quantity(self):
        comparison = Comparison(
            "the distance between $place1 and $place2 was",
            sign=">",
            expression=Q_("20 miles"),
        )
        comparison_opposite = Comparison(
            "the distance between $place1 and $place2 was",
            sign="<",
            expression=Q_("30 miles"),
        )
        assert not comparison.contradicts(comparison_opposite)

    def test_convert_quantity_of_Comparison(self):
        comparison = Comparison(
            "the distance between $place1 and $place2 was",
            sign=">",
            expression=Q_("20 miles"),
        )
        comparison_km = Comparison(
            "the distance between $place1 and $place2 was",
            sign=">",
            expression=Q_("30 kilometers"),
        )
        assert comparison > comparison_km

    def test_quantity_comparison_to_predicate(self):
        distance = Comparison(
            "the distance between $place1 and $place2 was",
            sign=">",
            expression="20 miles",
        )
        predicate = Predicate("the distance between $place1 and $place2 was")
        assert not distance >= predicate
