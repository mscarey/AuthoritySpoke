from typing import Dict

import pytest

from authorityspoke.nettlesome.terms import ContextRegister
from authorityspoke.nettlesome.factors import AbsenceOf
from authorityspoke.nettlesome.predicates import Predicate
from authorityspoke.nettlesome.quantities import Comparison, Q_
from authorityspoke.nettlesome.statements import Statement, Assertion
from authorityspoke.nettlesome.entities import Entity


@pytest.fixture(scope="class")
def make_predicate() -> Dict[str, Predicate]:
    return {
        "make_predicate": Predicate(content="{person} committed a crime"),
        "murder": Predicate(content="{shooter} murdered {victim}"),
        "murder_whether": Predicate(content="{shooter} murdered {victim}", truth=None),
        "murder_false": Predicate(content="{shooter} murdered {victim}", truth=False),
        "irrelevant": Predicate(
            content="{evidence} is relevant to show {fact}", truth=False
        ),
        "relevant": Predicate(content="{evidence} is relevant to show {fact}"),
        "relevant_whether": Predicate(
            content="{evidence} is relevant to show {fact}", truth=None
        ),
        "shooting": Predicate(content="{shooter} shot {victim}"),
        "shooting_self": Predicate(content="{shooter} shot {shooter}"),
        "no_shooting": Predicate(content="{shooter} shot {victim}", truth=False),
        "shooting_whether": Predicate(content="{shooter} shot {victim}", truth=None),
        "plotted": Predicate(content="{plotter1} plotted with {plotter2}"),
        "crime": Predicate(content="{person1} committed a crime"),
        "no_crime": Predicate(content="{person1} committed a crime", truth=False),
        "three_entities": Predicate(
            content="{planner} told {intermediary} to hire {shooter}"
        ),
        "friends": Predicate(content="{person1} and {person2} were friends"),
        "reliable": Predicate(content="{evidence} was reliable"),
        "no_context": Predicate(content="context was included", truth=False),
        # Use the irrelevant predicates/factors to make sure they don't affect an outcome.
        "irrelevant_0": Predicate(content="{person} was a clown"),
        "irrelevant_1": Predicate(content="{person} was a bear"),
        "irrelevant_2": Predicate(content="{place} was a circus"),
        "irrelevant_3": Predicate(content="{person} performed at {place}"),
    }


@pytest.fixture(scope="class")
def make_comparison() -> Dict[str, Predicate | Comparison]:
    return {
        "small_weight": Comparison.new(
            content="the amount of gold {person} possessed was",
            sign=">=",
            expression=Q_("1 gram"),
        ),
        "large_weight": Comparison.new(
            content="the amount of gold {person} possessed was",
            sign=">=",
            expression=Q_("100 kilograms"),
        ),
        "quantity=3": Comparison.new(
            content="The number of mice was", sign="==", expression=3
        ),
        "quantity>=4": Comparison.new(
            content="The number of mice was", sign=">=", expression=4
        ),
        "quantity>5": Comparison.new(
            content="The number of mice was", sign=">", expression=5
        ),
        "acres": Comparison.new(
            content="the distance between {place1} and {place2} was",
            sign=">=",
            expression=Q_("10 acres"),
        ),
        "exact": Comparison.new(
            content="the distance between {place1} and {place2} was",
            sign="==",
            expression=Q_("25 feet"),
        ),
        "float_distance": Comparison.new(
            content="the distance between {place1} and {place2} was",
            truth=True,
            sign="<",
            expression=20.0,
        ),
        "higher_int": Comparison.new(
            content="the distance between {place1} and {place2} was",
            sign="<=",
            expression=30,
        ),
        "int_distance": Comparison.new(
            content="the distance between {place1} and {place2} was",
            truth=True,
            sign="<",
            expression=20,
        ),
        "int_higher": Comparison.new(
            content="the distance between {place1} and {place2} was",
            sign="<=",
            expression=30,
        ),
        "less": Comparison.new(
            content="the distance between {place1} and {place2} was",
            truth=True,
            sign="<",
            expression=Q_("35 feet"),
        ),
        "less_whether": Comparison.new(
            content="the distance between {place1} and {place2} was",
            truth=None,
            sign="<",
            expression=Q_("35 feet"),
        ),
        "less_than_20": Comparison.new(
            content="the distance between {place1} and {place2} was",
            truth=True,
            sign="<",
            expression=Q_("20 feet"),
        ),
        "meters": Comparison.new(
            content="the distance between {place1} and {place2} was",
            sign=">=",
            expression=Q_("10 meters"),
        ),
        "not_equal": Comparison.new(
            content="the distance between {place1} and {place2} was",
            truth=True,
            sign="!=",
            expression=Q_("35 feet"),
        ),
        "more": Comparison.new(
            content="the distance between {place1} and {place2} was",
            truth=True,
            sign=">=",
            expression=Q_("35 feet"),
        ),
        "not_more": Comparison.new(
            content="the distance between {place1} and {place2} was",
            truth=False,
            sign=">",
            expression=Q_("35 feet"),
        ),
        "way_more": Comparison.new(
            content="the distance between {place1} and {place2} was",
            truth=True,
            sign=">=",
            expression=Q_("30 miles"),
        ),
    }


@pytest.fixture(scope="class")
def make_statement(make_predicate, make_comparison) -> Dict[str, Statement | AbsenceOf]:
    p = make_predicate
    c = make_comparison
    return {
        "irrelevant_0": Statement(
            predicate=p["irrelevant_0"], terms=[Entity(name="Craig")]
        ),
        "irrelevant_1": Statement(
            predicate=p["irrelevant_1"], terms=[Entity(name="Dan")]
        ),
        "irrelevant_2": Statement(
            predicate=p["irrelevant_2"], terms=[Entity(name="Dan")]
        ),
        "irrelevant_3": Statement(
            predicate=p["irrelevant_3"],
            terms=[Entity(name="Craig"), Entity(name="circus")],
        ),
        "irrelevant_3_new_context": Statement(
            predicate=p["irrelevant_3"],
            terms=[Entity(name="Craig"), Entity(name="Dan")],
        ),
        "irrelevant_3_context_0": Statement(
            predicate=p["irrelevant_3"],
            terms=[Entity(name="Craig"), Entity(name="Alice")],
        ),
        "crime": Statement(predicate=p["crime"], terms=[Entity(name="Alice")]),
        "crime_bob": Statement(predicate=p["crime"], terms=[Entity(name="Bob")]),
        "crime_craig": Statement(predicate=p["crime"], terms=[Entity(name="Craig")]),
        "crime_generic": Statement(
            predicate=p["crime"], terms=[Entity(name="Alice")], generic=True
        ),
        "crime_specific_person": Statement(
            predicate=p["crime"], terms=[Entity(name="Alice", generic=False)]
        ),
        "absent_no_crime": AbsenceOf(
            absent=Statement(predicate=p["no_crime"], terms=[Entity(name="Alice")])
        ),
        "no_crime": Statement(predicate=p["no_crime"], terms=[Entity(name="Alice")]),
        "no_crime_entity_order": Statement(
            predicate=p["no_crime"], terms=[Entity(name="Bob")]
        ),
        "murder": Statement(
            predicate=p["murder"], terms=[Entity(name="Alice"), Entity(name="Bob")]
        ),
        "murder_false": Statement(
            predicate=p["murder_false"],
            terms=[Entity(name="Alice"), Entity(name="Bob")],
        ),
        "murder_entity_order": Statement(
            predicate=p["murder"], terms=[Entity(name="Bob"), Entity(name="Alice")]
        ),
        "murder_craig": Statement(
            predicate=p["murder"], terms=[Entity(name="Craig"), Entity(name="Dan")]
        ),
        "murder_whether": Statement(
            predicate=p["murder_whether"],
            terms=[Entity(name="Alice"), Entity(name="Bob")],
        ),
        "shooting": Statement(
            predicate=p["shooting"], terms=[Entity(name="Alice"), Entity(name="Bob")]
        ),
        "shooting_self": Statement(
            predicate=p["shooting_self"], terms=[Entity(name="Alice")]
        ),
        "shooting_craig": Statement(
            predicate=p["shooting"], terms=[Entity(name="Craig"), Entity(name="Dan")]
        ),
        "shooting_entity_order": Statement(
            predicate=p["shooting"], terms=[Entity(name="Bob"), Entity(name="Alice")]
        ),
        "no_shooting": Statement(
            predicate=p["no_shooting"], terms=[Entity(name="Alice"), Entity(name="Bob")]
        ),
        "shooting_whether": Statement(
            predicate=p["shooting_whether"],
            terms=[Entity(name="Alice"), Entity(name="Bob")],
        ),
        "no_shooting_entity_order": Statement(
            predicate=p["no_shooting"], terms=[Entity(name="Bob"), Entity(name="Alice")]
        ),
        "plotted": Statement(
            predicate=p["plotted"], terms=[Entity(name="Alice"), Entity(name="Craig")]
        ),
        "plotted_reversed": Statement(
            predicate=p["plotted"], terms=[Entity(name="Alice"), Entity(name="Craig")]
        ),
        "three_entities": Statement(
            predicate=p["three_entities"],
            terms=[Entity(name="Alice"), Entity(name="Bob"), Entity(name="Craig")],
        ),
        "large_weight": Statement(
            predicate=c["large_weight"],
            terms=[Entity(name="Alice")],
        ),
        "large_weight_craig": Statement(
            predicate=c["large_weight"],
            terms=[Entity(name="Craig")],
        ),
        "small_weight": Statement(
            predicate=c["small_weight"],
            terms=[Entity(name="Alice")],
        ),
        "small_weight_bob": Statement(
            predicate=c["small_weight"],
            terms=[Entity(name="Bob")],
        ),
        "friends": Statement(
            predicate=p["friends"], terms=[Entity(name="Alice"), Entity(name="Bob")]
        ),
        "no_context": Statement(predicate=p["no_context"], terms=[]),
        "exact": Statement(
            predicate=c["exact"],
            terms=[Entity(name="San Francisco"), Entity(name="Oakland")],
        ),
        "less": Statement(
            predicate=c["less"],
            terms=[Entity(name="San Francisco"), Entity(name="Oakland")],
        ),
        "less_than_20": Statement(
            predicate=c["less_than_20"],
            terms=[Entity(name="San Francisco"), Entity(name="Oakland")],
        ),
        "less_whether": Statement(
            predicate=c["less_whether"],
            terms=[Entity(name="San Francisco"), Entity(name="Oakland")],
        ),
        "more": Statement(
            predicate=c["more"],
            terms=[Entity(name="San Francisco"), Entity(name="Oakland")],
        ),
        "more_atlanta": Statement(
            predicate=c["more"], terms=[Entity(name="Atlanta"), Entity(name="Marietta")]
        ),
        "more_meters": Statement(
            predicate=c["meters"],
            terms=[Entity(name="San Francisco"), Entity(name="Oakland")],
        ),
        "not_more": Statement(
            predicate=c["not_more"],
            terms=[Entity(name="San Francisco"), Entity(name="Oakland")],
        ),
        "float_distance": Statement(
            predicate=c["float_distance"],
            terms=[Entity(name="San Francisco"), Entity(name="Oakland")],
        ),
        "int_distance": Statement(
            predicate=c["int_distance"],
            terms=[Entity(name="San Francisco"), Entity(name="Oakland")],
        ),
        "higher_int": Statement(
            predicate=c["higher_int"],
            terms=[Entity(name="San Francisco"), Entity(name="Oakland")],
        ),
        "way_more": Statement(
            predicate=c["way_more"],
            terms=[Entity(name="San Francisco"), Entity(name="Oakland")],
        ),
        "absent_less": AbsenceOf(
            absent=Statement(
                predicate=c["less"],
                terms=[Entity(name="San Francisco"), Entity(name="Oakland")],
            )
        ),
        "absent_more": AbsenceOf(
            absent=Statement(
                predicate=c["more"],
                terms=[Entity(name="San Francisco"), Entity(name="Oakland")],
            )
        ),
        "absent_way_more": AbsenceOf(
            absent=Statement(
                predicate=c["way_more"],
                terms=[Entity(name="San Francisco"), Entity(name="Oakland")],
            )
        ),
    }


@pytest.fixture(scope="class")
def make_complex_fact(make_predicate, make_statement) -> Dict[str, Statement]:
    p = make_predicate
    f = make_statement

    return {
        "irrelevant_murder": Statement(
            predicate=p["irrelevant"], terms=(f["shooting"], f["murder"])
        ),
        "relevant_murder": Statement(
            predicate=p["relevant"], terms=(f["shooting"], f["murder"])
        ),
        "relevant_murder_swap_entities": Statement(
            predicate=p["relevant"], terms=(f["shooting"], f["murder"])
        ),
        "relevant_murder_nested_swap": Statement(
            predicate=p["relevant"],
            terms=(f["shooting_entity_order"], f["murder_entity_order"]),
        ),
        "relevant_murder_whether": Statement(
            predicate=p["relevant"], terms=(f["shooting"], f["murder_whether"])
        ),
        "whether_relevant_murder_whether": Statement(
            predicate=p["relevant"], terms=(f["shooting_whether"], f["murder_whether"])
        ),
        "relevant_murder_swap": Statement(
            predicate=p["relevant"], terms=(f["shooting"], f["murder_entity_order"])
        ),
        "relevant_murder_craig": Statement(
            predicate=p["relevant"], terms=(f["shooting_craig"], f["murder_craig"])
        ),
        "relevant_murder_alice_craig": Statement(
            predicate=p["relevant"], terms=(f["shooting"], f["murder_craig"])
        ),
        "relevant_plotted_murder": Statement(
            predicate=p["relevant"], terms=(f["plotted"], f["murder"])
        ),
        "relevant_plotted_reversed_murder": Statement(
            predicate=p["relevant"], terms=(f["plotted_reversed"], f["murder"])
        ),
    }


@pytest.fixture(scope="class")
def make_assertion(make_complex_fact, make_statement) -> Dict[str, Assertion]:
    return {
        "generic_authority": Assertion(
            statement=make_complex_fact["relevant_plotted_murder"],
            authority=Entity(name="a lawyer"),
        ),
        "generic_authority_reversed": Assertion(
            statement=make_complex_fact["relevant_plotted_reversed_murder"],
            authority=Entity(name="a lawyer"),
        ),
        "specific_authority": Assertion(
            statement=make_complex_fact["relevant_plotted_murder"],
            authority=Entity(name="Clarence Darrow", generic=False),
        ),
        "specific_authority_reversed": Assertion(
            statement=make_complex_fact["relevant_plotted_reversed_murder"],
            authority=Entity(name="Clarence Darrow", generic=False),
        ),
        "no_authority": Assertion(
            statement=make_complex_fact["relevant_plotted_murder"]
        ),
        "no_authority_reversed": Assertion(
            statement=make_complex_fact["relevant_plotted_reversed_murder"]
        ),
        "plotted_per_alice": Assertion(
            statement=make_statement["plotted"], authority=Entity(name="Alice")
        ),
        "plotted_per_bob": Assertion(
            statement=make_statement["plotted"], authority=Entity(name="Bob")
        ),
        "plotted_per_craig": Assertion(
            statement=make_statement["plotted"], authority=Entity(name="Craig")
        ),
    }


@pytest.fixture(scope="function")
def make_context_register() -> ContextRegister:
    context_names = ContextRegister()
    context_names.insert_pair(key=Entity(name="Alice"), value=Entity(name="Craig"))
    context_names.insert_pair(key=Entity(name="Bob"), value=Entity(name="Dan"))
    return context_names
