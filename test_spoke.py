from spoke import Entity, Human
from spoke import Predicate, Factor, Fact
from spoke import Procedure, Holding, Opinion
from spoke import opinion_from_file

from typing import Dict

import pytest
import json

from pint import UnitRegistry

from spoke import ureg, Q_


@pytest.fixture
def make_entity() -> Dict[str, Entity]:
    return {
        "e_watt": Human("Wattenburg"),
        "e_motel": Entity("Hideaway Lodge"),
        "e_trees": Entity("the stockpile of trees"),
    }


@pytest.fixture
def make_predicate() -> Dict[str, Predicate]:

    return {
        "p1": Predicate("{} was a motel"),
        "p1_again": Predicate("{} was a motel"),
        "p2": Predicate("{} operated and lived at {}"),
        "p2_reciprocal": Predicate("{} operated and lived at {}", reciprocal=True),
        "p3": Predicate("{} was {}’s abode"),
        "p4": Predicate("{} was on the premises of {}"),
        "p5": Predicate("{} was a stockpile of Christmas trees"),
        "p6": Predicate("{} was among some standing trees"),
        "p7": Predicate(
            "the distance between {} and {} was {}",
            truth=False,
            reciprocal=True,
            comparison=">",
            quantity=Q_("35 feet"),
        ),
        "p7_obverse": Predicate(
            "the distance between {} and {} was {}",
            truth=True,
            reciprocal=True,
            comparison="<=",
            quantity=Q_("35 feet"),
        ),
        "p7_true": Predicate(
            "the distance between {} and {} was {}",
            truth=True,
            reciprocal=True,
            comparison="<",
            quantity=Q_("35 feet"),
        ),
        "p8": Predicate(
            "The distance between {} and {} was {}",
            reciprocal=True,
            comparison=">=",
            quantity=Q_("20 feet"),
        ),
        "p8_meters": Predicate(
            "The distance between {} and {} was {}",
            reciprocal=True,
            comparison=">=",
            quantity=Q_("10 meters"),
        ),
        "p8_int": Predicate(
            "The distance between {} and {} was {}",
            reciprocal=True,
            comparison=">=",
            quantity=20,
        ),
        "p8_float": Predicate(
            "The distance between {} and {} was {}",
            reciprocal=True,
            comparison=">=",
            quantity=20.0,
        ),
        "p8_higher_int": Predicate(
            "The distance between {} and {} was {}",
            reciprocal=True,
            comparison=">=",
            quantity=30,
        ),
        "p9": Predicate(
            "The distance between {} and a parking area used by personnel and patrons of {} was {}",
            comparison="<=",
            quantity=Q_("5 feet"),
        ),
        "p9_miles": Predicate(
            "The distance between {} and a parking area used by personnel and patrons of {} was {}",
            comparison="<=",
            quantity=Q_("5 miles"),
        ),
        "p9_acres": Predicate(
            "The distance between {} and a parking area used by personnel and patrons of {} was {}",
            comparison="<=",
            quantity=Q_("5 acres"),
        ),
        "p10": Predicate("{} was within the curtilage of {}"),
    }


@pytest.fixture
def make_factor(make_predicate) -> Dict[str, Factor]:
    p = make_predicate

    return {
        "f1": Fact(p["p1"]),
        "f1b": Fact(p["p1"]),
        "f1c": Fact(p["p1_again"]),
        "f2": Fact(p["p2"]),
        "f2_reciprocal": Fact(p["p2_reciprocal"]),
        "f3": Fact(p["p3"]),
        "f3_absent": Fact(p["p3"], absent=True),
        "f4": Fact(p["p4"]),
        "f5": Fact(p["p5"]),
        "f6": Fact(p["p6"]),
        "f7": Fact(p["p7"]),
        "f7_true": Fact(p["p7_true"]),
        "f8": Fact(p["p8"]),
        "f8_absent": Fact(p["p8"], absent=True),
        "f8_int": Fact(p["p8_int"]),
        "f8_meters": Fact(p["p8_meters"]),
        "f8_float": Fact(p["p8_float"]),
        "f8_higher_int": Fact(p["p8_higher_int"]),
        "f9": Fact(p["p9"]),
        "f9_absent": Fact(p["p9"], absent=True),
        "f9_absent_miles": Fact(p["p9_miles"], absent=True),
        "f10": Fact(p["p10"]),
    }


@pytest.fixture
def make_procedure(make_factor) -> Dict[str, Procedure]:
    f = make_factor

    return {
        "c1": Procedure(
            outputs={f["f3"]: (0, 1)}, inputs={f["f1"]: (0,), f["f2"]: (1, 0)}
        ),
        "c1_again": Procedure(
            outputs={f["f3"]: (1, 0)}, inputs={f["f2"]: (0, 1), f["f1"]: (1,)}
        ),
        "c1_easy": Procedure(outputs={f["f3"]: (0, 1)}, inputs={f["f2"]: (1, 0)}),
        "c2": Procedure(
            outputs={f["f10"]: (0, 1)},
            inputs={
                f["f4"]: (0, 1),
                f["f5"]: (0,),
                f["f6"]: (0,),
                f["f7"]: (0, 1),
                f["f9"]: (0, 1),
            },
            even_if={f["f8"]: (0, 1)},
        ),
        "c2_reciprocal_swap": Procedure(
            outputs={f["f10"]: (0, 1)},
            inputs={
                f["f4"]: (0, 1),
                f["f5"]: (0,),
                f["f6"]: (0,),
                f["f7"]: (1, 0),
                f["f9"]: (0, 1),
            },
            even_if={f["f8"]: (0, 1)},
        ),
        "c2_nonreciprocal_swap": Procedure(
            outputs={f["f10"]: (0, 1)},
            inputs={
                f["f4"]: (1, 0),
                f["f5"]: (0,),
                f["f6"]: (0,),
                f["f7"]: (0, 1),
                f["f9"]: (0, 1),
            },
            even_if={f["f8"]: (0, 1)},
        ),
    }


@pytest.fixture
def make_holding(make_factor) -> Dict[str, Holding]:
    f1 = make_factor["f1"]
    f2 = make_factor["f2"]
    f3 = make_factor["f3"]

    return {
        "h1": Holding(Procedure(outputs={f3: (0, 1)}, inputs={f1: (0,), f2: (1, 0)})),
        "h1_again": Holding(
            Procedure(outputs={f3: (0, 1)}, inputs={f1: (0,), f2: (1, 0)})
        ),
        "h1_different": Holding(
            Procedure(outputs={f3: (0, 1)}, inputs={f1: (0,), f2: (0, 1)})
        ),
        "h1_really_the_same": Holding(
            Procedure(outputs={f3: (1, 0)}, inputs={f1: (1,), f2: (0, 1)})
        ),
    }


@pytest.fixture
def make_opinion() -> Dict[str, Opinion]:
    test_cases = ("watt", "brad")
    opinions = {}
    for case in test_cases:
        for opinion in opinion_from_file(f"json/{case}_h.json"):
            opinions[f"{case}_{opinion.position}"] = opinion
    return opinions


class TestPredicates:
    def test_predicate_with_wrong_number_of_entities(self):
        with pytest.raises(ValueError):
            f = Predicate("{} was a motel", reciprocal=True)

    def test_predicate_with_wrong_comparison_symbol(self):
        with pytest.raises(ValueError):
            h = (
                Predicate(
                    "the height of {} was {}",
                    comparison=">>",
                    quantity=Q_("160 centimeters"),
                ),
            )

    def test_convert_false_statement_about_quantity_to_obverse(self, make_predicate):
        assert make_predicate["p7_obverse"].truth is True
        assert make_predicate["p7_obverse"].quantity == ureg.Quantity(35, "foot")
        assert make_predicate["p7"].truth is True
        assert make_predicate["p7"].comparison == "<="
        assert make_predicate["p7_obverse"].comparison == "<="

    def test_quantity_type(self, make_predicate):
        assert type(make_predicate["p7"].quantity) == ureg.Quantity

    def test_quantity_string(self, make_predicate):
        assert str(make_predicate["p7"].quantity) == "35 foot"

    def test_predicate_equality(self, make_predicate):
        assert make_predicate["p1"] == make_predicate["p1_again"]

    def test_predicate_inequality(self, make_predicate):
        assert make_predicate["p2"] != make_predicate["p2_reciprocal"]

    def test_quantity_comparison(self, make_predicate):
        assert make_predicate["p7"].quantity_comparison() == "no more than 35 foot"
        assert make_predicate["p9"].quantity_comparison() == "no more than 5 foot"
        assert make_predicate["p1"].quantity_comparison() is None

    def test_obverse_predicates_equal(self, make_predicate):
        assert make_predicate["p7"] == make_predicate["p7_obverse"]

    def test_greater_than_because_of_quantity(self, make_predicate):
        assert make_predicate["p8_meters"] > make_predicate["p8"]

    def test_equal_float_and_int(self, make_predicate):
        assert make_predicate["p8_int"] == make_predicate["p8_float"]

    def test_greater_float_and_int(self, make_predicate):
        assert make_predicate["p8_higher_int"] > make_predicate["p8_float"]
        assert make_predicate["p8_int"] < make_predicate["p8_higher_int"]

    def test_str_for_predicate_with_number_quantity(self, make_predicate):
        assert (
            str(make_predicate["p8_int"])
            == "The distance between {} and {} was at least 20"
        )
        assert (
            str(make_predicate["p8_float"])
            == "The distance between {} and {} was at least 20.0"
        )
        assert (
            str(make_predicate["p8"])
            == "The distance between {} and {} was at least 20 foot"
        )

    def test_predicate_contradictions(self, make_predicate):
        assert make_predicate["p7"].contradicts(make_predicate["p7_true"])
        assert not make_predicate["p1"].contradicts(make_predicate["p1_again"])
        assert not make_predicate["p3"].contradicts(make_predicate["p7"])

    def test_predicate_does_not_contradict_factor(self, make_predicate, make_factor):
        assert not make_predicate["p7_true"].contradicts(make_factor["f7"])

    def test_no_implication_with_inconsistent_dimensionality(self, make_predicate):
        assert not make_predicate["p9"] > make_predicate["p9_acres"]
        assert not make_predicate["p9"] < make_predicate["p9_acres"]

    def test_no_contradiction_with_inconsistent_dimensionality(self, make_predicate):
        assert not make_predicate["p9"].contradicts(make_predicate["p9_acres"])
        assert not make_predicate["p9_acres"].contradicts(make_predicate["p9"])

    def test_no_equality_with_inconsistent_dimensionality(self, make_predicate):
        assert make_predicate["p9"] != make_predicate["p9_acres"]


class TestFactors:
    def test_string_representation_of_factor(self, make_factor):
        assert str(make_factor["f1"]) == "Fact: {} was a motel"
        assert str(make_factor["f3_absent"]) == "Absent Fact: {} was {}’s abode"

    def test_entity_slots_as_length_of_factor(self, make_factor):
        assert len(make_factor["f1"].predicate) == 1

    def test_predicate_with_entities(self, make_entity, make_factor):
        assert (
            make_factor["f1"].predicate.content_with_entities((make_entity["e_motel"]))
            == "Hideaway Lodge was a motel"
        )

    def test_reciprocal_with_wrong_number_of_entities(self, make_entity, make_factor):
        with pytest.raises(ValueError):
            make_factor["f1"].predicate.content_with_entities(
                (make_entity["e_motel"], make_entity["e_watt"])
            )

    def test_false_predicate_with_entities(self, make_entity, make_factor):
        assert make_factor["f7"].predicate_in_context(
            (make_entity["e_trees"], make_entity["e_motel"])
        ) == str(
            "Fact: the distance between the stockpile of trees "
            + "and Hideaway Lodge was no more than 35 foot"
        )

    def test_entity_and_human_in_predicate(self, make_entity, make_factor):
        assert (
            make_factor["f2"].predicate.content_with_entities(
                (make_entity["e_watt"], make_entity["e_motel"])
            )
            == "Wattenburg operated and lived at Hideaway Lodge"
        )

    def test_fact_label_with_entities(self, make_entity, make_factor):
        assert (
            make_factor["f2"].predicate_in_context(
                (make_entity["e_watt"], make_entity["e_motel"])
            )
            == "Fact: Wattenburg operated and lived at Hideaway Lodge"
        )

    def test_factor_equality(self, make_factor):
        assert make_factor["f1"] == make_factor["f1b"]
        assert make_factor["f1"] == make_factor["f1c"]

    def test_factor_reciprocal_unequal(self, make_factor):
        assert make_factor["f2"] != make_factor["f2_reciprocal"]

    def test_factor_unequal_predicate_truth(self, make_factor):
        assert make_factor["f7"] != make_factor["f7_true"]
        assert make_factor["f7"].contradicts(make_factor["f7_true"])

    def test_factor_does_not_contradict_predicate(self, make_predicate, make_factor):
        assert not make_factor["f7"].contradicts(make_predicate["p7_true"])

    def test_factor_contradiction_absent_predicate(self, make_factor):
        assert make_factor["f3"].contradicts(make_factor["f3_absent"])
        assert make_factor["f3_absent"].contradicts(make_factor["f3"])

    def test_factor_does_not_imply_predicate(self, make_predicate, make_factor):
        assert not make_factor["f8_meters"] > make_predicate["p8"]

    def test_factor_implies_because_of_quantity(self, make_factor):
        assert make_factor["f8_meters"] > make_factor["f8"]
        assert make_factor["f8_higher_int"] > make_factor["f8_float"]
        assert make_factor["f8_int"] < make_factor["f8_higher_int"]

    def test_absent_factor_implies_absent_factor_with_greater_quantity(
        self, make_factor
    ):
        assert make_factor["f9_absent"] > make_factor["f9_absent_miles"]

    def test_absent_factor_contradicts_broader_quantity_statement(self, make_factor):
        assert make_factor["f8_absent"].contradicts(make_factor["f8_meters"])
        assert make_factor["f8_meters"].contradicts(make_factor["f8_absent"])
        assert make_factor["f9_absent_miles"].contradicts(make_factor["f9"])
        assert make_factor["f9"].contradicts(make_factor["f9_absent_miles"])


class TestProcedure:
    def test_procedure_equality(self, make_procedure):
        assert make_procedure["c1"] == make_procedure["c1_again"]

    def test_still_equal_after_swapping_reciprocal_entities(self, make_procedure):
        assert make_procedure["c2"] == (make_procedure["c2_reciprocal_swap"])

    def test_unequal_after_swapping_nonreciprocal_entities(self, make_procedure):
        assert make_procedure["c2"] != (make_procedure["c2_nonreciprocal_swap"])

    def test_sorted_entities_from_procedure(self, make_predicate, make_procedure):

        """The sorted_entities method sorts them alphabetically by __repr__."""

        assert make_procedure["c2"].sorted_entities() == [
            Fact(
                predicate=Predicate(
                    content="The distance between {} and a parking area used by personnel and patrons of {} was {}",
                    truth=True,
                    reciprocal=False,
                    comparison="<=",
                    quantity=ureg.Quantity(5, "foot"),
                ),
                absent=False,
            ),
            Fact(
                predicate=Predicate(
                    content="The distance between {} and {} was {}",
                    truth=True,
                    reciprocal=True,
                    comparison=">=",
                    quantity=ureg.Quantity(20, "foot"),
                ),
                absent=False,
            ),
            Fact(
                predicate=Predicate(
                    content="the distance between {} and {} was {}",
                    truth=False,
                    reciprocal=True,
                    comparison=">",
                    quantity=ureg.Quantity(35, "foot"),
                ),
                absent=False,
            ),
            Fact(
                predicate=Predicate(
                    content="{} was a stockpile of Christmas trees",
                    truth=True,
                    reciprocal=False,
                ),
                absent=False,
            ),
            Fact(
                predicate=Predicate(
                    content="{} was among some standing trees",
                    truth=True,
                    reciprocal=False,
                ),
                absent=False,
            ),
            Fact(
                predicate=Predicate(
                    content="{} was on the premises of {}", truth=True, reciprocal=False
                ),
                absent=False,
            ),
            Fact(
                predicate=Predicate(
                    content="{} was within the curtilage of {}",
                    truth=True,
                    reciprocal=False,
                ),
                absent=False,
            ),
        ]

    def test_entity_permutations(self, make_procedure):
        """
        "The distance between {the trees} and {the hotel} was at least 20 feet"
        and "...was at least 35 feet" can be swapped to say
        "The distance between {the hotel} and {the trees}"
        but otherwise the order of entities has to be the same.
        """
        assert make_procedure["c2"].get_entity_permutations() == {
            (0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1),
            (0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1),
            (0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1),
            (0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1),
        }

    def test_implies_same_output_fewer_inputs(self, make_procedure):
        assert make_procedure["c1_easy"] > (make_procedure["c1"])


class TestHoldings:
    def test_identical_holdings_equal(self, make_holding):
        assert make_holding["h1"] == make_holding["h1_again"]

    def test_holdings_different_entities_unequal(self, make_holding):
        assert make_holding["h1"] != make_holding["h1_different"]

    def test_holdings_differing_in_entity_order_equal(self, make_holding):
        """
        Test that holdings are considered equal if they have the same factors
        and the numbers they use to refer to entities are different but in an
        equivalent order.
        e.g. {"F1": "121", "F2": "233"} and {"F2": "122", "F1": "313"}
        """
        assert make_holding["h1"] == make_holding["h1_really_the_same"]


class TestOpinions:
    def test_load_opinion_in_Harvard_format(self):
        with open("json/watt_h.json", "r") as f:
            watt_dict = json.load(f)
        assert watt_dict["name_abbreviation"] == "Wattenburg v. United States"

    def test_opinion_features(self, make_opinion):
        assert make_opinion["watt_majority"].court == "9th-cir"
        assert "388 F.2d 853" in make_opinion["watt_majority"].citations

    def test_opinion_date(self, make_opinion):
        assert (
            make_opinion["watt_majority"].decision_date
            < make_opinion["brad_majority"].decision_date
        )
        assert (
            make_opinion["brad_majority"].decision_date
            == make_opinion[
                "brad_concurring-in-part-and-dissenting-in-part"
            ].decision_date
        )

    def test_opinion_author(self, make_opinion):
        assert make_opinion["watt_majority"].author == "HAMLEY, Circuit Judge"
        assert make_opinion["brad_majority"].author == "BURKE, J."
        assert (
            make_opinion["brad_concurring-in-part-and-dissenting-in-part"].author
            == "TOBRINER, J."
        )
