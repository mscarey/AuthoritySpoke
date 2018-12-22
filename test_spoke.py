from copy import copy
import json
from typing import Dict


from pint import UnitRegistry
import pytest

from spoke import Entity, Human
from spoke import Predicate, Factor, Fact
from spoke import Procedure, Holding, ProceduralHolding
from spoke import Opinion, opinion_from_file
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
        "p3_false": Predicate("{} was {}’s abode", truth=False),
        "p4": Predicate("{} was on the premises of {}"),
        "p5": Predicate("{} was a stockpile of Christmas trees"),
        "p6": Predicate("{} was among some standing trees"),
        "p7": Predicate(
            "The distance between {} and {} was {}",
            truth=False,
            reciprocal=True,
            comparison=">",
            quantity=Q_("35 feet"),
        ),
        "p7_obverse": Predicate(
            "The distance between {} and {} was {}",
            truth=True,
            reciprocal=True,
            comparison="<=",
            quantity=Q_("35 feet"),
        ),
        "p7_opposite": Predicate(
            "The distance between {} and {} was {}",
            truth=True,
            reciprocal=True,
            comparison=">",
            quantity=Q_("35 feet"),
        ),
        "p7_true": Predicate(
            "The distance between {} and {} was {}",
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
        "p8_exact": Predicate(
            "The distance between {} and {} was {}",
            reciprocal=True,
            comparison="=",
            quantity=Q_("25 feet"),
        ),
        "p8_less": Predicate(
            "The distance between {} and {} was {}",
            reciprocal=True,
            comparison="<=",
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
        "p10_false": Predicate("{} was within the curtilage of {}", truth=False),
        "p11": Predicate("{} was a warrantless search and seizure"),
        "p12": Predicate("{} was performed by federal law enforcement officers"),
        "p13": Predicate("{} constituted an intrusion upon {}"),
        "p14": Predicate("{} sought to preserve {} as private"),
        "p15": Predicate("{} was in an area adjacent to {}"),
        "p16": Predicate("{} was in an area accessible to the public"),
        "p17": Predicate(
            "In {}, several law enforcement officials meticulously went through {}"
        ),
        "p18": Predicate(
            "{} continued for {}", comparison=">=", quantity=Q_("385 minutes")
        ),
        "p19": Predicate("{} continued after night fell"),
        "p_irrelevant_0": Predicate("{} was a clown"),
        "p_irrelevant_1": Predicate("{} was a bear"),
        "p_irrelevant_2": Predicate("{} was a circus"),
        "p_irrelevant_3": Predicate("{} performed at {}"),
    }


@pytest.fixture
def make_factor(make_predicate) -> Dict[str, Factor]:
    p = make_predicate

    return {
        "f1": Fact(p["p1"]),
        "f1_entity_order": Fact(p["p1"], (1,)),
        "f1b": Fact(p["p1"]),
        "f1c": Fact(p["p1_again"]),
        "f2": Fact(p["p2"], (1, 0)),
        "f2_entity_order": Fact(p["p2"]),
        "f2_reciprocal": Fact(p["p2_reciprocal"]),
        "f3": Fact(p["p3"]),
        "f3_entity_order": Fact(p["p3"], (1, 0)),
        "f3_absent": Fact(p["p3"], absent=True),
        "f4": Fact(p["p4"]),
        "f4_swap_entities": Fact(p["p4"], (1, 0)),
        "f5": Fact(p["p5"]),
        "f5_swap_entities": Fact(p["p5"], (1,)),
        "f6": Fact(p["p6"]),
        "f6_swap_entities": Fact(p["p6"], (1,)),
        "f7": Fact(p["p7"]),
        "f7_swap_entities": Fact(p["p7"], (1, 0)),
        "f7_true": Fact(p["p7_true"]),
        "f8": Fact(p["p8"]),
        "f8_absent": Fact(p["p8"], absent=True),
        "f8_exact": Fact(p["p8_exact"]),
        "f8_exact_swap_entities": Fact(p["p8_exact"], (1, 0)),
        "f8_float": Fact(p["p8_float"]),
        "f8_higher_int": Fact(p["p8_higher_int"]),
        "f8_int": Fact(p["p8_int"]),
        "f8_less": Fact(p["p8_less"]),
        "f8_meters": Fact(p["p8_meters"]),
        "f9": Fact(p["p9"]),
        "f9_absent": Fact(p["p9"], absent=True),
        "f9_absent_miles": Fact(p["p9_miles"], absent=True),
        "f9_swap_entities": Fact(p["p9"], (1, 0)),
        "f10": Fact(p["p10"]),
        "f10_absent": Fact(p["p10"], absent=True),
        "f10_false": Fact(p["p10_false"]),
        "f10_absent_false": Fact(p["p10_false"], absent=True),
        "f10_swap_entities": Fact(p["p10"], (1, 0)),
        "f11": Fact(p["p11"]),
        "f12": Fact(p["p12"]),
        "f13": Fact(p["p13"]),
        "f14": Fact(p["p14"]),
        "f15": Fact(p["p15"]),
        "f16": Fact(p["p16"]),
        "f17": Fact(p["p17"]),
        "f18": Fact(p["p18"]),
        "f19": Fact(p["p19"]),
        "f_irrelevant_0": Fact(p["p_irrelevant_0"], (2,)),
        "f_irrelevant_1": Fact(p["p_irrelevant_1"], (3,)),
        "f_irrelevant_2": Fact(p["p_irrelevant_2"], (4,)),
        "f_irrelevant_3": Fact(p["p_irrelevant_3"], (2, 4)),
        "f_irrelevant_3_new_context": Fact(p["p_irrelevant_3"], (3, 4)),
    }


@pytest.fixture
def make_procedure(make_factor) -> Dict[str, Procedure]:
    f = make_factor

    return {
        "c1": Procedure(outputs=(f["f3"],), inputs=(f["f1"], f["f2"])),
        "c1_again": Procedure(outputs=(f["f3"],), inputs=(f["f1"], f["f2"])),
        "c1_entity_order": Procedure(
            outputs=(f["f3_entity_order"],),
            inputs=(f["f2_entity_order"], f["f1_entity_order"]),
        ),
        "c1_easy": Procedure(outputs=(f["f3"],), inputs=(f["f2"])),
        "c2": Procedure(
            outputs=(f["f10"],),
            inputs=(f["f4"], f["f5"], f["f6"], f["f7"], f["f9"]),
            despite=(f["f8"],),
        ),
        "c2_absent_despite": Procedure(
            outputs=(f["f10"],),
            inputs=(f["f4"], f["f5"], f["f6"], f["f7"]),
            despite=(f["f8_exact"], f["f9_absent"]),
        ),
        "c2_exact_quantity": Procedure(
            outputs=(f["f10"],),
            inputs=(f["f4"], f["f5"], f["f6"], f["f8_exact"], f["f9"]),
        ),
        "c2_higher_quantity": Procedure(
            outputs=(f["f10"],),
            inputs=(f["f4"], f["f5"], f["f6"], f["f7"], f["f8_higher_int"], f["f9"]),
        ),
        "c2_exact_in_despite": Procedure(
            outputs=(f["f10"],),
            inputs=(f["f4"], f["f5"], f["f6"], f["f7"], f["f9"]),
            despite=(f["f8_exact"],),
        ),
        "c2_exact_in_despite_entity_order": Procedure(
            outputs=(f["f10_swap_entities"],),
            inputs=(
                f["f4_swap_entities"],
                f["f5_swap_entities"],
                f["f6_swap_entities"],
                f["f7_swap_entities"],
                f["f9_swap_entities"],
            ),
            despite=(f["f8_exact_swap_entities"],),
        ),
        "c2_irrelevant_inputs": Procedure(
            outputs=(f["f10"],),
            inputs=(
                f["f4"],
                f["f5"],
                f["f6"],
                f["f7"],
                f["f9"],
                f["f_irrelevant_0"],
                f["f_irrelevant_1"],
                f["f_irrelevant_2"],
                f["f_irrelevant_3"],
                f["f_irrelevant_3_new_context"],
            ),
            despite=(f["f8"],),
        ),
        "c2_irrelevant_despite": Procedure(
            outputs=(f["f10"],),
            inputs=(f["f4"], f["f5"], f["f6"], f["f7"], f["f9"]),
            despite=(
                f["f8"],
                f["f_irrelevant_0"],
                f["f_irrelevant_1"],
                f["f_irrelevant_2"],
                f["f_irrelevant_3"],
                f["f_irrelevant_3_new_context"],
            ),
        ),
        "c2_reciprocal_swap": Procedure(
            outputs=(f["f10"],),
            inputs=(f["f4"], f["f5"], f["f6"], f["f7_swap_entities"], f["f9"]),
            despite=(f["f8"],),
        ),
        "c2_nonreciprocal_swap": Procedure(
            outputs=(f["f10"],),
            inputs=(f["f4_swap_entities"], f["f5"], f["f6"], f["f7"], f["f9"]),
            despite=(f["f8"],),
        ),
        "c2_broad_output": Procedure(
            outputs=(f["f8_int"],), inputs=(f["f4"], f["f5"], f["f6"], f["f7"], f["f9"])
        ),
        "c2_narrow_output": Procedure(
            outputs=(f["f8_higher_int"],),
            inputs=(f["f4"], f["f5"], f["f6"], f["f7"], f["f9"]),
        ),
        "c2_output_absent": Procedure(
            outputs=(f["f10_absent"],),
            inputs=(f["f4"], f["f5"], f["f6"], f["f7"], f["f9"]),
            despite=(f["f8"],),
        ),
        "c2_output_false": Procedure(
            outputs=(f["f10_false"],),
            inputs=(f["f4"], f["f5"], f["f6"], f["f7"], f["f9"]),
            despite=(f["f8"],),
        ),
        "c2_output_absent_false": Procedure(
            outputs=(f["f10_absent_false"],),
            inputs=(f["f4"], f["f5"], f["f6"], f["f7"], f["f9"]),
            despite=(f["f8"],),
        ),
        "c_near_means_no_curtilage": Procedure(
            outputs=(f["f10_false"],), inputs=(f["f7_true"])
        ),
        "c_nearer_means_curtilage": Procedure(
            outputs=(f["f10"],), inputs=(f["f8_less"])
        ),
        "c_near_means_curtilage": Procedure(outputs=(f["f10"],), inputs=(f["f7"])),
        "c_far_means_no_curtilage": Procedure(
            outputs=(f["f10_false"],), inputs=(f["f8"])
        ),
        # "c3": Procedure(
        #    outputs=f["f20"],
        #    inputs=(f["f3"], f["f11"], f["12"], f["13"], f["14"], f["15"]),
        #    despite=(f["f16"]),
        # )
    }


@pytest.fixture
def make_holding(make_procedure) -> Dict[str, ProceduralHolding]:
    c = make_procedure

    return {
        "h1": ProceduralHolding(c["c1"]),
        "h1_again": ProceduralHolding(c["c1"]),
        "h1_entity_order": ProceduralHolding(c["c1_entity_order"]),
        "h1_easy": ProceduralHolding(c["c1_easy"]),
        "h1_opposite": ProceduralHolding(c["c1"], rule_valid=False),
        "h2": ProceduralHolding(c["c2"]),
        "h2_ALL": ProceduralHolding(c["c2"], mandatory=False, universal=True),
        "h2_ALL_MAY_output_false": ProceduralHolding(
            c["c2_output_false"], mandatory=False, universal=True
        ),
        "h2_ALL_MUST_output_false": ProceduralHolding(
            c["c2_output_false"], mandatory=True, universal=True
        ),
        "h2_exact_quantity": ProceduralHolding(c["c2_exact_quantity"]),
        "h2_invalid": ProceduralHolding(c["c2"], rule_valid=False),
        "h2_irrelevant_inputs": ProceduralHolding(c["c2_irrelevant_inputs"]),
        "h2_irrelevant_inputs_invalid": ProceduralHolding(
            c["c2_irrelevant_inputs"], rule_valid=False
        ),
        "h2_irrelevant_inputs_ALL_MUST": ProceduralHolding(
            c["c2_irrelevant_inputs"], mandatory=True, universal=True
        ),
        "h2_irrelevant_inputs_ALL_MUST_invalid": ProceduralHolding(
            c["c2_irrelevant_inputs"], mandatory=True, universal=True, rule_valid=False
        ),
        "h2_irrelevant_inputs_ALL_invalid": ProceduralHolding(
            c["c2_irrelevant_inputs"], universal=True, rule_valid=False
        ),
        "h2_irrelevant_inputs_MUST_invalid": ProceduralHolding(
            c["c2_irrelevant_inputs"], mandatory=True, rule_valid=False
        ),
        "h2_reciprocal_swap": ProceduralHolding(c["c2_reciprocal_swap"]),
        "h2_exact_in_despite": ProceduralHolding(c["c2_exact_in_despite"]),
        "h2_exact_in_despite_ALL": ProceduralHolding(
            c["c2_exact_in_despite"], mandatory=False, universal=True
        ),
        "h2_exact_in_despite_ALL_entity_order": ProceduralHolding(
            c["c2_exact_in_despite_entity_order"], mandatory=False, universal=True
        ),
        "h2_exact_quantity_ALL": ProceduralHolding(
            c["c2_exact_quantity"], mandatory=False, universal=True
        ),
        "h2_MUST": ProceduralHolding(c["c2"], mandatory=True, universal=False),
        "h2_MUST_invalid": ProceduralHolding(c["c2"], mandatory=True, rule_valid=False),
        "h2_output_absent": ProceduralHolding(c["c2_output_absent"]),
        "h2_output_false": ProceduralHolding(c["c2_output_false"]),
        "h2_output_absent_false": ProceduralHolding(c["c2_output_absent_false"]),
        "h2_SOME_MUST_output_false": ProceduralHolding(
            c["c2_output_false"], mandatory=True, universal=False
        ),
        "h2_SOME_MUST_output_absent": ProceduralHolding(
            c["c2_output_absent"], mandatory=True, universal=False
        ),
        "h_near_means_no_curtilage": ProceduralHolding(c["c_near_means_no_curtilage"]),
        "h_nearer_means_curtilage_ALL": ProceduralHolding(
            c["c_nearer_means_curtilage"], mandatory=True, universal=True
        ),
        "h_near_means_no_curtilage_ALL": ProceduralHolding(
            c["c_near_means_no_curtilage"], mandatory=True, universal=True
        ),
        "h_nearer_means_curtilage": ProceduralHolding(
            c["c_nearer_means_curtilage"], mandatory=True, universal=True
        ),
        "h_far_means_no_curtilage": ProceduralHolding(
            c["c_far_means_no_curtilage"], mandatory=True, universal=True
        ),
        "h_near_means_curtilage": ProceduralHolding(
            c["c_near_means_curtilage"], mandatory=True, universal=True
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

    def test_predicate_content_comparison(self, make_predicate):
        assert make_predicate["p8_exact"].content == make_predicate["p7"].content

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
        assert make_predicate["p8_meters"] != make_predicate["p8"]

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
        assert not make_predicate["p9"] >= make_predicate["p9_acres"]
        assert not make_predicate["p9"] <= make_predicate["p9_acres"]

    def test_no_contradiction_with_inconsistent_dimensionality(self, make_predicate):
        assert not make_predicate["p9"].contradicts(make_predicate["p9_acres"])
        assert not make_predicate["p9_acres"].contradicts(make_predicate["p9"])

    def test_no_equality_with_inconsistent_dimensionality(self, make_predicate):
        assert make_predicate["p9"] != make_predicate["p9_acres"]

    def test_negated_method(self, make_predicate):
        assert make_predicate["p7"].negated() == make_predicate["p7_opposite"]
        assert make_predicate["p3"].negated() == make_predicate["p3_false"]


class TestFactors:
    def test_default_entity_context_for_fact(self, make_predicate):
        f2 = Fact(make_predicate["p2"])
        assert f2.entity_context == (0, 1)

    def test_convert_int_entity_context_to_tuple(self, make_predicate):
        f = Fact(make_predicate["p_irrelevant_1"], 3)
        assert f.entity_context == (3,)

    def test_string_representation_of_factor(self, make_factor):
        assert str(make_factor["f1"]) == "Fact: 0 was a motel"
        assert str(make_factor["f3_absent"]) == "Absent Fact: 0 was 1’s abode"

    def test_entity_slots_as_length_of_factor(self, make_factor):
        assert len(make_factor["f1"].predicate) == 1
        assert len(make_factor["f1"]) == 1

    def test_predicate_with_entities(self, make_entity, make_factor):
        assert (
            make_factor["f1"].predicate.content_with_entities((make_entity["e_motel"]))
            == "Hideaway Lodge was a motel"
        )

    def test_factor_entity_context_does_not_match_predicate(self, make_predicate):
        with pytest.raises(ValueError):
            x = Fact(make_predicate["p1"], (0, 1, 2))

    def test_reciprocal_with_wrong_number_of_entities(self, make_entity, make_factor):
        with pytest.raises(ValueError):
            make_factor["f1"].predicate.content_with_entities(
                (make_entity["e_motel"], make_entity["e_watt"])
            )

    def test_false_predicate_with_entities(self, make_entity, make_factor):
        assert make_factor["f7"].predicate_in_context(
            (make_entity["e_trees"], make_entity["e_motel"])
        ) == str(
            "Fact: The distance between the stockpile of trees "
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

    def test_factor_implies_because_of_exact_quantity(self, make_factor):
        assert make_factor["f8_exact"] > make_factor["f7"]
        assert make_factor["f8_exact"] >= make_factor["f8"]

    def test_absent_factor_implies_absent_factor_with_greater_quantity(
        self, make_factor
    ):
        assert make_factor["f9_absent"] > make_factor["f9_absent_miles"]

    def test_absent_factor_contradicts_broader_quantity_statement(self, make_factor):
        assert make_factor["f8_absent"].contradicts(make_factor["f8_meters"])
        assert make_factor["f8_meters"].contradicts(make_factor["f8_absent"])
        assert make_factor["f9_absent_miles"].contradicts(make_factor["f9"])
        assert make_factor["f9"].contradicts(make_factor["f9_absent_miles"])

    def test_copies_of_identical_factor(self, make_factor):
        """
        Even if the two factors have different entity markers in self.entity_context,
        I expect them to evaluate equal because the choice of entity markers is
        arbitrary.
        """
        f = make_factor
        assert f["f_irrelevant_3"] == f["f_irrelevant_3"]
        assert f["f_irrelevant_3"] == f["f_irrelevant_3_new_context"]

    def test_equal_factors_not_gt(self, make_factor):
        f = make_factor
        assert f["f_irrelevant_3"] >= f["f_irrelevant_3_new_context"]
        assert f["f_irrelevant_3"] <= f["f_irrelevant_3_new_context"]
        assert not f["f_irrelevant_3"] > f["f_irrelevant_3_new_context"]

    def test_check_entity_consistency_true(self, make_factor):
        f = make_factor
        assert f["f_irrelevant_3"].check_entity_consistency(
            f["f_irrelevant_3_new_context"], (None, None, None, 2, None)
        )
        assert f["f_irrelevant_3"].check_entity_consistency(
            f["f_irrelevant_3_new_context"], (1, 0, 3, 2, 4)
        )

    def test_check_entity_consistency_false(self, make_factor):
        f = make_factor
        assert not f["f_irrelevant_3"].check_entity_consistency(
            f["f_irrelevant_3_new_context"], (None, None, None, None, 0)
        )
        assert not f["f_irrelevant_3"].check_entity_consistency(
            f["f_irrelevant_3_new_context"], (None, None, None, 3, None)
        )

    def test_check_entity_consistency_type_error(self, make_factor, make_holding):
        f = make_factor
        with pytest.raises(TypeError):
            f["f_irrelevant_3"].check_entity_consistency(
                make_holding["h2"], (None, None, None, None, 0)
            )

    def test_consistent_entity_combinations(self, make_factor):
        """
        Finds that for factor f["f7"], it would be consistent with the
        other group of factors for f["f7"]'s two slots to be assigned
        (0, 1) or (1, 0).
        """

        f = make_factor
        assert f["f7"].consistent_entity_combinations(
            factors_from_other_procedure=[
                f["f4"],
                f["f5"],
                f["f6"],
                f["f7"],
                f["f8"],
                f["f9"],
            ],
            matches=(0, 1, None, None, None),
        ) == [{0: 0, 1: 1}, {0: 1, 1: 0}]


class TestProcedure:
    def test_exception_for_wrong_type_for_procedure(self, make_predicate):
        with pytest.raises(TypeError):
            x = Procedure(inputs=make_predicate["p1"], outputs=make_predicate["p2"])

    def test_exception_for_wrong_type_in_tuple_for_procedure(self, make_predicate):
        with pytest.raises(TypeError):
            x = Procedure(inputs=(make_predicate["p1"]), outputs=(make_predicate["p2"]))

    def test_procedure_equality(self, make_procedure):
        assert make_procedure["c1"] == make_procedure["c1_again"]
        assert make_procedure["c1"] == make_procedure["c1_entity_order"]

    def test_still_equal_after_swapping_reciprocal_entities(self, make_procedure):
        assert make_procedure["c2"] == (make_procedure["c2_reciprocal_swap"])

    def test_unequal_after_swapping_nonreciprocal_entities(self, make_procedure):
        assert make_procedure["c2"] != (make_procedure["c2_nonreciprocal_swap"])

    def test_procedure_length(self, make_procedure):
        assert len(make_procedure["c1"]) == 2
        assert len(make_procedure["c2"]) == 2

    def test_sorted_factors_from_procedure(self, make_predicate, make_procedure):

        """The sorted_factors method sorts them alphabetically by __repr__."""

        assert make_procedure["c2"].sorted_factors() == [
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
                    truth=False,
                    reciprocal=True,
                    comparison=">",
                    quantity=ureg.Quantity(35, "foot"),
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

    def test_procedure_string_with_entities(self, make_procedure):
        assert "Fact: 2 performed at 4" in str(make_procedure["c2_irrelevant_inputs"])
        assert "Fact: 3 performed at 4" in str(make_procedure["c2_irrelevant_inputs"])

    def test_entities_of_inputs_for_identical_procedure(
        self, make_factor, make_procedure
    ):
        f = make_factor
        c1 = make_procedure["c1"]
        c1_again = make_procedure["c1_again"]
        assert f["f1"] in c1.inputs
        assert f["f1"] in c1_again.inputs
        assert f["f1"].entity_context == (0,)
        assert f["f2"] in c1.inputs
        assert f["f2"] in c1_again.inputs
        assert f["f2"].entity_context == (1, 0)

    def test_entities_of_implied_inputs_for_implied_procedure(
        self, make_factor, make_procedure
    ):
        f = make_factor
        c1_easy = make_procedure["c1_easy"]
        c1_order = make_procedure["c1_entity_order"]
        assert any(factor == f["f2"] for factor in c1_easy.inputs)
        assert all(factor != f["f1"] for factor in c1_easy.inputs)

    def test_procedure_implication_with_exact_quantity(
        self, make_factor, make_procedure
    ):
        """This is meant to show that the function finds the "distance is
        exactly 25" factor in c2_exact, and recognizes that factor can imply
        the "distance is more than 20" factor in c2 if they have the same entities.
        """

        f = make_factor
        c2 = make_procedure["c2"]
        c2_exact_quantity = make_procedure["c2_exact_quantity"]

        assert f["f7"] in c2.inputs
        assert f["f7"] not in c2_exact_quantity.inputs
        assert f["f8_exact"] > f["f7"]
        assert c2 <= c2_exact_quantity
        assert not c2_exact_quantity <= c2

    def test_implied_procedure_with_reciprocal_entities(self, make_procedure):
        """
        Because both procedures have a form of "The distance between {} and {} was {}"
        factor and those factors are reciprocal, the entities of one of them in reversed
        order can be used as the entities of the other, and one will still imply the other.
        (But if there had been more than two entities, only the first two would have been
        reversed.)
        """

        c2 = make_procedure["c2"]
        c2_reciprocal_swap = make_procedure["c2_reciprocal_swap"]
        assert c2 == c2_reciprocal_swap
        assert c2 >= c2_reciprocal_swap

    def test_entities_of_implied_quantity_outputs_for_implied_procedure(
        self, make_procedure
    ):
        """
        If c2_narrow was "self" and c2_broad was "other", the output of
        c2_broad (with f["f8_int"]) would be implied by the output of
        c2_narrow (with f["f8_higher_int"]).
        """

        c2_broad = make_procedure["c2_broad_output"]
        c2_narrow = make_procedure["c2_narrow_output"]

        assert c2_narrow > c2_broad

    def test_procedure_implies_identical_procedure(self, make_procedure):
        assert make_procedure["c1"] >= make_procedure["c1_again"]
        assert make_procedure["c1"] == make_procedure["c1_again"]

    def test_procedure_implies_same_procedure_fewer_inputs(self, make_procedure):

        assert make_procedure["c1_easy"] < make_procedure["c1"]
        assert make_procedure["c1_easy"] <= make_procedure["c1"]
        assert make_procedure["c1_easy"] != make_procedure["c1"]

    def test_procedure_implies_reordered_entities_fewer_inputs(self, make_procedure):

        assert make_procedure["c1_entity_order"] > make_procedure["c1_easy"]
        assert make_procedure["c1_easy"] < make_procedure["c1_entity_order"]
        assert make_procedure["c1_easy"] != make_procedure["c1_entity_order"]

    def test_procedure_exact_quantity_in_despite_implication(self, make_procedure):
        assert make_procedure["c2_exact_in_despite"] > make_procedure["c2"]

    def test_procedure_implication_despite_irrelevant_factors(self, make_procedure):
        assert make_procedure["c2"] < make_procedure["c2_irrelevant_inputs"]

    def test_implies_all_to_some(self, make_procedure):
        assert make_procedure["c2"].implies_all_to_some(
            make_procedure["c2_irrelevant_despite"]
        )
        assert not make_procedure["c2"] > make_procedure["c2_irrelevant_despite"]

    def test_exhaustive_implies_input_same_as_despite_of_other(self, make_procedure):
        """
        Every input of c2_exact_in_despite is equal to or implied by
        some input of c2, and an input of c2 implies the despite of c2_exact_in_despite.
        """
        p = make_procedure
        assert p["c2_exact_in_despite"].implies_all_to_some(p["c2"])

    def test_no_exhaustive_implies_when_input_contradicts_despite(self, make_procedure):
        """
        c2_higher_quantity has the right inputs, but it also has an
        input that contradicts the despite factor of c2_exact_in_despite.
        """
        p = make_procedure
        assert not p["c2"].implies_all_to_some(p["c2_absent_despite"])

    def test_no_contradict_between_procedures(self, make_procedure):
        """
        It's not completely clear to me what assumptions are being made about
        the context of a procedure when comparing them with __gt__,
        implies_all_to_some, and exhaustive_contradicts.

        I don't think "contradicts" is meaningful for Procedures, but I could be wrong.
        """
        p = make_procedure
        with pytest.raises(NotImplementedError):
            assert p["c2_higher_quantity"].contradicts(p["c2_exact_in_despite"])


class TestHoldings:

    # Equality

    def test_identical_holdings_equal(self, make_holding):
        assert make_holding["h1"] == make_holding["h1_again"]

    def test_holdings_equivalent_entity_orders_equal(self, make_holding):
        """
        Test that holdings are considered equal if they have the same factors
        and the numbers they use to refer to entities are different but in an
        equivalent order.
        e.g. {"F1": "1,2,1", "F2": "2,0,0"} and {"F2": "1,2,2", "F1": "0,1,0"}
        """
        assert make_holding["h1"] == make_holding["h1_entity_order"]

    def test_holdings_different_entities_unequal(self, make_holding):
        assert make_holding["h1"] != make_holding["h1_easy"]

    def test_holdings_differing_in_entity_order_equal(self, make_holding):
        assert make_holding["h1"] == make_holding["h1_entity_order"]

    # Implication

    def test_holdings_more_inputs_implies_fewer(self, make_holding):
        assert make_holding["h1"] > make_holding["h1_easy"]
        assert make_holding["h2_irrelevant_inputs"] > make_holding["h2"]

    def test_holding_narrower_despite_implies_broader(self, make_holding):
        assert make_holding["h2_exact_in_despite"] > make_holding["h2"]
        assert not make_holding["h2"] > make_holding["h2_exact_in_despite"]

    def test_holdings_more_specific_quantity_implies_less_specific(self, make_holding):
        assert make_holding["h2_exact_quantity"] > make_holding["h2"]

    def test_holdings_less_specific_with_all_implies_more_specific(self, make_holding):
        assert make_holding["h2_ALL"] > make_holding["h2_exact_quantity_ALL"]
        assert not make_holding["h2_exact_quantity_ALL"] > make_holding["h2_ALL"]

    def test_specific_holding_with_all_implies_more_general_with_some(
        self, make_holding
    ):
        assert make_holding["h2_exact_quantity_ALL"] > make_holding["h2"]

    def test_all_to_all_with_reciprocal(self, make_holding):
        """This is supposed to test reciprocal predicates in despite factors
        in the Predicate.find_consistent_factors method.
        The entity order shouldn't matter because it's the mirror image of the
        normal entity order.
        """
        assert make_holding["h2_exact_in_despite_ALL"] > make_holding["h2_ALL"]
        assert (
            make_holding["h2_exact_in_despite_ALL_entity_order"]
            > make_holding["h2_ALL"]
        )

    def test_negated_method(self, make_holding):
        assert make_holding["h1"].negated() == make_holding["h1_opposite"]

    # Contradiction

    def test_holding_contradicts_invalid_version_of_self(self, make_holding):
        assert make_holding["h2"].negated() == make_holding["h2_invalid"]
        assert make_holding["h2"].contradicts(make_holding["h2_invalid"])
        assert make_holding["h2"] >= make_holding["h2_invalid"].negated()

    def test_some_holding_consistent_with_absent_output(self, make_holding):
        assert not make_holding["h2"].contradicts(make_holding["h2_output_absent"])

    def test_some_holding_consistent_with_false_output(self, make_holding):
        assert not make_holding["h2"].contradicts(make_holding["h2_output_false"])

    def test_some_holding_consistent_with_absent_false_output(self, make_holding):
        assert not make_holding["h2"].contradicts(make_holding["h2_output_false"])

    def test_contradicts_if_valid(self, make_holding):
        """
        This helper method should return the same value as "contradicts"
        because both holdings are valid.
        """

        make_holding["h2_ALL"].contradicts_if_valid(
            make_holding["h2_SOME_MUST_output_false"]
        )

    def test_contradicts_if_valid_invalid_holding(self, make_holding):

        """
        In the current design, contradicts calls implies;
        implies calls contradicts_if_valid.
        """

        assert make_holding["h2_irrelevant_inputs_invalid"].contradicts(
            make_holding["h2"]
        ) != make_holding["h2_irrelevant_inputs_invalid"].contradicts_if_valid(
            make_holding["h2"]
        )

    def test_contradicts_if_valid_some_vs_all(self, make_holding):

        """
        This test and the one below show that you can change whether two
        holdings contradict one another by exchanging the SOME/MAY from one
        with the ALL/MUST from the other.

        The assertion here is:
        In SOME cases where the distance between A and B is less than 35 feet
        the court MAY find that
        A is not in the curtilage of B

        does not contradict

        In ALL cases where the distance between A and B is less than 20 feet
        the court MUST find that
        A is in the curtilage of B
        """

        assert make_holding["h_near_means_no_curtilage"].contradicts_if_valid(
            make_holding["h_nearer_means_curtilage_ALL"]
        )

    def test_contradicts_if_valid_all_vs_some(self, make_holding):

        """
        The assertion here is:
        In ALL cases where the distance between A and B is less than 35 feet
        the court MUST find that
        A is not in the curtilage of B

        contradicts

        In SOME cases where the distance between A and B is less than 20 feet
        the court MAY find that
        A is in the curtilage of B
        """

        assert make_holding["h_near_means_no_curtilage_ALL"].contradicts_if_valid(
            make_holding["h_nearer_means_curtilage"]
        )

    def test_contradicts_if_valid_all_vs_all(self, make_holding):

        """
        The assertion here is:
        In ALL cases where the distance between A and B is less than 35 feet
        the court MUST find that
        A is in the curtilage of B

        contradicts

        In ALL cases where the distance between A and B is more than 20 feet
        the court MAY find that
        A is not in the curtilage of B
        """

        assert make_holding["h_near_means_curtilage"].contradicts_if_valid(
            make_holding["h_far_means_no_curtilage"]
        )

    def test_always_may_contradicts_sometimes_must_not(self, make_holding):
        assert make_holding["h2_ALL"].contradicts(
            make_holding["h2_SOME_MUST_output_false"]
        )

    def test_always_may_contradicts_sometimes_must_omit_output(self, make_holding):
        assert make_holding["h2_ALL"].contradicts(
            make_holding["h2_SOME_MUST_output_absent"]
        )

    def test_sometimes_must_contradicts_always_may_not(self, make_holding):
        assert make_holding["h2_MUST"].contradicts(
            make_holding["h2_ALL_MAY_output_false"]
        )

    def test_sometimes_must_contradicts_always_must_not(self, make_holding):
        assert make_holding["h2_MUST"].contradicts(
            make_holding["h2_ALL_MUST_output_false"]
        )

    def test_negation_of_h2_contradicts_holding_that_implies_h2(self, make_holding):
        assert make_holding["h2_invalid"].contradicts(
            make_holding["h2_irrelevant_inputs"]
        )

    def test_holding_that_implies_h2_contradicts_negation_of_h2(self, make_holding):
        """
        Tests whether "contradicts" works reciprocally in this case.
        It should be reciprocal in every case so far, but maybe not for 'decided.'"""

        assert make_holding["h2_ALL"].contradicts(
            make_holding["h2_SOME_MUST_output_false"]
        )

    def test_invalid_holding_contradicts_h2(self, make_holding):

        # You NEVER MAY follow X
        # will contradict
        # You SOMEtimes MAY follow Y
        # if X implies Y or Y implies X

        assert make_holding["h2_irrelevant_inputs_invalid"].contradicts(
            make_holding["h2"]
        )

    def test_invalidity_of_holding_that_implies_h2_contradicts_h2_with_MUST(
        self, make_holding
    ):

        # You NEVER MUST follow X
        # will contradict
        # You SOMEtimes MUST follow Y
        # if X implies Y or Y implies X

        assert make_holding["h2_irrelevant_inputs_MUST_invalid"].contradicts(
            make_holding["h2_MUST"]
        )

    def test_contradiction_with_ALL_MUST_and_invalid_SOME_MUST(self, make_holding):

        # You ALWAYS MUST follow X
        # will contradict
        # You NEVER MUST follow Y
        # if X implies Y or Y implies X

        assert make_holding["h2_irrelevant_inputs_ALL_MUST"].contradicts(
            make_holding["h2_MUST_invalid"]
        )


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
