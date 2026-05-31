from datetime import date
from decimal import Decimal
from pint import Quantity
import pytest
import sympy
from sympy import Interval, oo

from authorityspoke.nettlesome.predicates import Predicate
from authorityspoke.nettlesome.quantities import Comparison, DecimalRange, Q_
from authorityspoke.nettlesome.statements import Statement


class TestQuantityInterval:
    def test_comparison_with_wrong_comparison_symbol(self):
        with pytest.raises(ValueError):
            _ = Comparison.new(
                content="the height of {} was {}",
                sign=">>",
                expression=Q_("160 centimeters"),
            )

    def test_make_comparison_with_string_for_int(self):
        scones = Comparison.new(
            content="the number of scones {diner} ate was", sign="<", expression="5"
        )
        assert scones.interval == sympy.Interval(0, Decimal(5), right_open=True)

    def test_comparison_with_int(self):
        value = DecimalRange(sign="<", quantity=5)
        scones = Comparison(
            content="the number of scones {diner} ate was", quantity_range=value
        )
        assert scones.interval == sympy.Interval(0, Decimal(5), right_open=True)

    def test_comparison_with_string_for_float(self):
        scones = Comparison.new(
            content="the number of scones {diner} ate was", sign=">", expression="2.5"
        )
        assert scones.interval == sympy.Interval(2.5, oo, left_open=True)

    def test_comparison_interval_does_not_include_negatives(self):
        party = Comparison.new(
            content="the number of people at the party was", sign="<", expression=25
        )
        assert -5 not in party.interval
        assert party.quantity_range._include_negatives is False

    def test_comparison_negative_magnitude(self):
        comparison = Comparison.new(
            content="the balance in the bank account was", sign="<=", expression=-100
        )
        assert comparison.quantity_range.magnitude == Decimal(-100)
        assert comparison.quantity_range._include_negatives is True
        assert comparison.interval.end == float(-100)

    def test_comparison_negative_attr(self):
        comparison = Comparison.new(
            content="the balance in the bank account was", sign="<=", expression=-100
        )
        assert comparison.quantity_range.magnitude == Decimal(-100)
        assert comparison.quantity_range._include_negatives is True
        assert comparison.interval.end == float(-100)

    def test_comparison_interval_with_negatives(self):
        comparison = Comparison.new(
            content="the balance in the bank account was",
            sign="<=",
            expression=100,
            include_negatives=True,
        )
        assert comparison.quantity_range.magnitude == Decimal(100)
        assert comparison.quantity_range._include_negatives is True
        assert comparison.interval.start == float("-inf")
        assert comparison.interval.end == float(100)

    def test_comparison_pint_quantity(self):
        comparison = Comparison.new(
            content="the distance between {place1} and {place2} was",
            sign=">",
            expression=Q_("20 miles"),
        )
        assert comparison.quantity_range.magnitude == Decimal(20)
        assert comparison.quantity_range.quantity_units == "mile"

    def test_comparison_interval(self):
        comparison = Comparison.new(
            content="the distance between {place1} and {place2} was",
            sign=">",
            expression=Q_("20 miles"),
        )
        assert comparison.interval == Interval(Decimal(20), oo, left_open=True)
        assert "quantity_magnitude=Decimal('20')" in repr(comparison)

    def test_negated_method(self, make_comparison):
        as_false = make_comparison["exact"].negated()
        assert (
            str(as_false)
            == "that the distance between {place1} and {place2} was not equal to 25 foot"
        )

    def test_negated_method_same_meaning(self, make_comparison):
        assert make_comparison["less"].negated().means(make_comparison["more"])

    def test_no_string_as_quantity(self):
        with pytest.raises(TypeError):
            Comparison(
                "twenty miles",
            )

    def test_convert_false_statement_about_quantity_to_obverse(self):
        distance = Comparison.new(
            content="the distance between {place1} and {place2} was",
            truth=False,
            sign=">",
            expression=Q_("35 feet"),
        )
        assert distance.truth is True
        assert distance.sign == "<="
        assert isinstance(distance.quantity, Quantity)
        assert str(distance.quantity) == "35 foot"

    def test_string_for_date_as_expression(self):
        copyright_date_range = Comparison.new(
            content="the date when {work} was created was",
            sign=">=",
            expression=date(1978, 1, 1),
        )
        assert "1978" in str(copyright_date_range)

    def test_comparison_not_equal(self):
        comparison = Comparison.new(
            content="the distance between {place1} and {place2} was",
            sign="!=",
            expression=Q_("20 miles"),
        )
        assert comparison.interval == sympy.Union(
            Interval(0, Decimal(20), right_open=True),
            Interval(Decimal(20), oo, left_open=True),
        )

    def test_str_not_equal(self, make_comparison):
        assert (
            "the distance between {place1} and {place2} was not equal to 35 foot"
            in str(make_comparison["not_equal"])
        )

    def test_content_not_ending_with_was(self):
        with pytest.raises(ValueError):
            Comparison.new(
                content="{person} drove for",
                sign=">=",
                expression=Q_("20 miles"),
            )

    def test_cannot_reuse_quantity_range_for_number(self):
        dogs = Comparison.new(
            content="the number of dogs was", sign=">", expression="3 gallons"
        )
        with pytest.raises(TypeError):
            DecimalRange(quantity=dogs.quantity)

    def test_plural_in_Comparison(self):
        comparison = Comparison.new(
            content="the weights of ${the defendants} were",
            sign=">",
            expression="200 pounds",
        )
        assert comparison.content.endswith("was")


class TestCompareQuantities:
    def test_does_not_exclude_other_quantity(self):
        comparison = Comparison.new(
            content="the distance between {place1} and {place2} was",
            sign=">",
            expression=Q_("20 miles"),
        )
        comparison_opposite = Comparison.new(
            content="the distance between {place1} and {place2} was",
            sign="<",
            expression=Q_("30 miles"),
        )
        left = comparison.quantity_range
        right = comparison_opposite.quantity_range
        assert left.contradicts(right.interval) is False

    def test_convert_quantity_of_comparison(self):
        comparison = Comparison.new(
            content="the distance between {place1} and {place2} was",
            sign=">",
            expression=Q_("20 miles"),
        )
        comparison_km = Comparison.new(
            content="the distance between {place1} and {place2} was",
            sign=">",
            expression=Q_("30 kilometers"),
        )
        result = comparison.quantity_range.get_unit_converted_interval(
            comparison_km.quantity_range
        )
        assert 18 < result.left < 19

    def test_cannot_convert_date_to_time_period(self):
        time = Comparison.new(
            content="the time {object} took to biodegrade was",
            sign=">",
            expression=Q_("2000 years"),
        )
        day = Comparison.new(
            content="the day was",
            sign="=",
            expression=date(2020, 1, 1),
        )
        with pytest.raises(TypeError):
            time.quantity_range.get_unit_converted_interval(day.quantity_range)

    def test_inconsistent_dimensionality_quantity(self):
        number = Comparison.new(
            content="the distance between {place1} and {place2} was",
            sign=">",
            expression=20,
        )
        distance = Comparison.new(
            content="the distance between {place1} and {place2} was",
            sign=">",
            expression=Q_("20 miles"),
        )
        assert not number.quantity_range.consistent_dimensionality(
            distance.quantity_range
        )
        assert not distance.quantity_range.consistent_dimensionality(
            number.quantity_range
        )

    def test_inconsistent_dimensionality_date(self):
        number = Comparison.new(
            content="the distance between {place1} and {place2} was",
            sign=">",
            expression=20,
        )
        day = Comparison.new(
            content="the distance between {place1} and {place2} was",
            sign=">",
            expression=date(2000, 1, 1),
        )
        assert not number.quantity_range.consistent_dimensionality(day.quantity_range)
        assert not day.quantity_range.consistent_dimensionality(number.quantity_range)

    def test_quantity_comparison_to_predicate(self):
        distance = Comparison.new(
            content="the distance between {place1} and {place2} was",
            sign=">",
            expression="20 miles",
        )
        predicate = Predicate(content="the distance between {place1} and {place2} was")
        assert not distance.quantity_range.implies(predicate)

    def test_compare_intervals_different_units(self):
        miles = Comparison.new(
            content="the distance was", sign="<", expression=Q_("30 miles")
        )
        kilos = Comparison.new(
            content="the distance was", sign="<", expression=Q_("40 kilometers")
        )
        assert kilos.quantity_range.implies(miles.quantity_range)

    def test_compare_tax_rate(self):
        specific_tax_rate = Comparison.new(
            content="{taxpayer}'s marginal income tax rate was",
            sign="=",
            expression=Decimal(".3"),
        )
        tax_rate_over_25 = Comparison.new(
            content="{taxpayer}'s marginal income tax rate was",
            sign=">",
            expression=Decimal(".25"),
        )
        assert specific_tax_rate.implies(tax_rate_over_25)


class TestSameMeaning:
    def test_same_meaning_float_and_int(self, make_comparison):
        """
        These now evaluate equal even though their equal quantities are different types
        """
        assert make_comparison["int_distance"].means(make_comparison["float_distance"])

    def test_no_equality_with_inconsistent_dimensionality(self, make_comparison):
        assert not make_comparison["more"].means(make_comparison["acres"])


class TestImplication:
    def test_comparison_implies_predicate_false(self):
        distance = Comparison.new(
            content="the distance between {place1} and {place2} was",
            sign=">",
            expression="20 miles",
        )
        predicate = Predicate(content="the distance between {place1} and {place2} was")
        assert not distance.implies(predicate)
        assert not distance.contradicts(predicate)
        assert not predicate.contradicts(distance)

    def test_comparison_gte_predicate_false(self):
        distance = Comparison.new(
            content="the distance between {place1} and {place2} was",
            sign=">",
            expression="20 miles",
        )
        predicate = Predicate(content="the distance between {place1} and {place2} was")
        assert not distance >= predicate

    def test_predicate_not_same_with_interchangeable_terms(self):
        interchangeable = Comparison.new(
            content="the distance between {place1} and {place2} was",
            sign="<",
            expression=Q_("20 feet"),
        )
        not_interchangeable = Comparison.new(
            content="the distance between {west} and {east} was",
            sign="<",
            expression=Q_("20 feet"),
        )
        assert not interchangeable.means(not_interchangeable)

    def test_error_predicate_means_statement(self, make_predicate):
        with pytest.raises(TypeError):
            make_predicate["crime"].means(Statement.new(predicate="any text"))

    def test_greater_than_because_of_quantity(self, make_comparison):
        assert make_comparison["less_than_20"] > make_comparison["less"]
        assert make_comparison["less_than_20"] != make_comparison["less"]

    def test_greater_float_and_int(self, make_comparison):
        assert make_comparison["int_distance"] > make_comparison["int_higher"]
        assert make_comparison["int_higher"] < make_comparison["int_distance"]

    def test_any_truth_value_implies_none(self, make_predicate):
        assert make_predicate["murder"] > make_predicate["murder_whether"]
        assert make_predicate["murder_false"] > make_predicate["murder_whether"]

    def test_no_implication_by_exact_quantity(self, make_comparison):
        assert not make_comparison["quantity=3"] > make_comparison["quantity>5"]

    def test_no_implication_of_exact_quantity(self, make_comparison):
        assert not make_comparison["quantity>5"] > make_comparison["quantity=3"]

    def test_no_implication_by_greater_or_equal_quantity(self, make_comparison):
        assert not make_comparison["quantity>=4"] > make_comparison["quantity>5"]

    def test_no_implication_of_greater_or_equal_quantity(self):
        less = Comparison.new(content="The number of mice was", sign=">", expression=4)
        more = Comparison.new(content="The number of mice was", sign=">=", expression=5)
        assert not less.implies(more)

    def test_no_contradiction_inconsistent_dimensions(self):
        equal = Comparison.new(
            content="{defendant}'s sentence was", sign="=", expression="8 years"
        )
        less = Comparison.new(
            content="{defendant}'s sentence was", sign="<=", expression="10 parsecs"
        )
        assert not equal.contradicts(less)
        assert not equal.implies(less)

    def test_equal_implies_greater_or_equal(self, make_comparison):
        assert make_comparison["exact"] > make_comparison["less"]

    def test_implication_with_not_equal(self, make_comparison):
        assert make_comparison["less"] > make_comparison["not_equal"]

    def test_no_implication_with_inconsistent_dimensionality(self, make_comparison):
        assert not make_comparison["less"] >= make_comparison["acres"]
        assert not make_comparison["less"] <= make_comparison["acres"]

    def test_implication_due_to_dates(self):
        copyright_date_range = Comparison.new(
            content="the date when {work} was created was",
            sign=">=",
            expression="1978-01-01",
        )
        copyright_date_specific = Comparison.new(
            content="the date when {work} was created was",
            sign="=",
            expression=date(1980, 6, 20),
        )
        assert copyright_date_specific.implies(copyright_date_range)

    def test_not_equal_does_not_imply(self):
        yards = Comparison.new(
            content="the length of the football field was",
            sign="!=",
            expression="100 yards",
        )
        meters = Comparison.new(
            content="the length of the football field was",
            sign="!=",
            expression="80 meters",
        )
        assert not yards >= meters

    def test_not_equal_implies(self):
        meters = Comparison.new(
            content="the length of the football field was",
            sign="!=",
            expression="1000 meter",
        )
        kilometers = Comparison.new(
            content="the length of the football field was",
            sign="!=",
            expression="1 kilometer",
        )
        assert meters.means(kilometers)

    def test_same_volume(self):
        volume_in_liters = Comparison.new(
            content="the volume of fuel in the tank was",
            sign="=",
            expression="10 liters",
        )
        volume_in_milliliters = Comparison.new(
            content="the volume of fuel in the tank was",
            sign="=",
            expression="10000 milliliters",
        )
        assert volume_in_liters.means(volume_in_milliliters)


class TestContradiction:
    def test_not_more_does_not_contradict_less(self, make_comparison):
        assert not make_comparison["not_more"].contradicts(make_comparison["less"])

    def test_predicate_does_not_contradict(self, make_comparison):
        irrelevant = Predicate(content="things happened")
        assert not irrelevant.contradicts(make_comparison["less"])

    def test_contradiction_by_exact(self, make_comparison):
        assert make_comparison["exact"].contradicts(make_comparison["less_than_20"])
        assert make_comparison["less_than_20"].contradicts(make_comparison["exact"])

    def test_contradiction_by_equal_quantity(self, make_comparison):
        assert make_comparison["quantity=3"].contradicts(make_comparison["quantity>5"])

    def test_contradiction_of_equal_quantity(self, make_comparison):
        assert make_comparison["quantity>5"].contradicts(make_comparison["quantity=3"])

    def test_no_contradiction_by_greater_or_equal_quantity(self, make_comparison):
        assert not make_comparison["quantity>=4"].contradicts(
            make_comparison["quantity>5"]
        )

    def test_no_contradiction_of_greater_or_equal_quantity(self, make_comparison):
        assert not make_comparison["quantity>5"].contradicts(
            make_comparison["quantity>=4"]
        )

    def test_no_contradiction_with_inconsistent_dimensionality(self, make_comparison):
        assert not make_comparison["meters"].contradicts(make_comparison["acres"])
        assert not make_comparison["acres"].contradicts(make_comparison["meters"])

    def test_contradiction_with_quantity(self, make_comparison):
        assert make_comparison["less_than_20"].contradicts(make_comparison["meters"])

    def test_contradictory_date_ranges(self):
        later = Comparison.new(
            content="the date {dentist} became a licensed dentist was",
            sign=">",
            expression=date(2010, 1, 1),
        )
        earlier = Comparison.new(
            content="the date {dentist} became a licensed dentist was",
            sign="<",
            expression=date(1990, 1, 1),
        )
        assert later.contradicts(earlier)
        assert earlier.contradicts(later)

    def test_no_contradiction_without_truth_value(self):
        later = Comparison.new(
            content="the date {dentist} became a licensed dentist was",
            sign=">",
            expression=date(2010, 1, 1),
            truth=None,
        )
        earlier = Comparison.new(
            content="the date {dentist} became a licensed dentist was",
            sign="<",
            expression=date(1990, 1, 1),
        )
        assert not later.contradicts(earlier)
        assert not earlier.contradicts(later)

    def test_no_contradiction_date_and_time_period(self):
        later = Comparison.new(
            content="the date {dentist} became a licensed dentist was",
            sign=">",
            expression=date(2010, 1, 1),
        )
        earlier = Comparison.new(
            content="the date {dentist} became a licensed dentist was",
            sign="<",
            expression="2000 years",
        )
        assert not later.contradicts(earlier)
        assert not earlier.contradicts(later)

    def test_no_contradiction_irrelevant_quantities(self):
        more_cows = Comparison.new(
            content="the number of cows {person} owned was",
            sign=">",
            expression=10,
        )
        fewer_horses = Comparison.new(
            content="the number of horses {person} owned was",
            sign="<",
            expression=3,
        )
        assert not more_cows.contradicts(fewer_horses)
        assert not fewer_horses.contradicts(more_cows)

    def test_no_contradiction_of_predicate(self):
        more_cows = Comparison.new(
            content="the number of cows {person} owned was",
            sign=">",
            expression=10,
        )
        no_cows = Predicate(
            content="the number of cows {person} owned was", truth=False
        )
        assert not more_cows.contradicts(no_cows)
        assert not no_cows.contradicts(more_cows)

    def test_contradiction_exact_different_unit(self):
        acres = Comparison.new(
            content="the size of the farm was", sign=">", expression=Q_("2000 acres")
        )
        kilometers = Comparison.new(
            content="the size of the farm was",
            sign="=",
            expression=Q_("2 square kilometers"),
        )
        assert acres.contradicts(kilometers)

    def test_no_contradiction_exact_different_unit(self):
        acres = Comparison.new(
            content="the size of the farm was", sign=">", expression=Q_("20 acres")
        )
        kilometers = Comparison.new(
            content="the size of the farm was",
            sign="=",
            expression=Q_("100 square kilometers"),
        )
        assert not acres.contradicts(kilometers)

    def test_reuse_quantity_range_for_contradiction(self):
        dogs = Comparison.new(content="the number of dogs was", sign=">", expression=3)
        cats = Comparison(
            content="the number of cats was", quantity_range=dogs.quantity_range
        )
        fewer_cats = Comparison.new(
            content="the number of cats was", sign="<", expression=3
        )
        assert cats.contradicts(fewer_cats)
