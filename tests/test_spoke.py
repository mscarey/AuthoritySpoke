from copy import copy
import datetime
import json
import operator
from typing import Dict

from pint import UnitRegistry
import pytest

from enactments import Code, Enactment
from entities import Entity, Human
from evidence import Evidence
from rules import Procedure, Rule, ProceduralRule, evolve_match_list
from opinions import Opinion
from spoke import Predicate, Factor, Fact
from spoke import ureg, Q_
from spoke import check_entity_consistency  # move this back into a class?
from spoke import find_matches


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

    def test_implication_subclass(self, make_entity):
        assert make_entity["tree_search_specific"] >= make_entity["motel"]
        assert make_entity["tree_search"] > make_entity["motel"]

    def test_implication_superclass(self, make_entity):
        assert not make_entity["trees"] >= make_entity["tree_search"]

class TestPredicates:
    def test_predicate_with_wrong_number_of_entities(self):
        with pytest.raises(ValueError):
            _ = Predicate.new("{} was a motel", reciprocal=True)

    def test_predicate_with_wrong_comparison_symbol(self):
        with pytest.raises(ValueError):
            _ = (
                Predicate.new(
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
        assert (
            "distance between {} and {} was at least 20" in str(make_predicate["p8_int"])
        )
        assert (
            "distance between {} and {} was at least 20.0" in str(make_predicate["p8_float"])
        )
        assert (
            "distance between {} and {} was at least 20 foot" in str(make_predicate["p8"])
        )

    def test_negated_method(self, make_predicate):
        assert make_predicate["p7"].negated() == make_predicate["p7_opposite"]
        assert make_predicate["p3"].negated() == make_predicate["p3_false"]

    # Equality

    def test_predicate_equality(self, make_predicate):
        assert make_predicate["p1"] == make_predicate["p1_again"]

    def test_predicate_inequality(self, make_predicate):
        assert make_predicate["p2"] != make_predicate["p2_reciprocal"]

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

    def test_any_truth_value_implies_none(self, make_predicate):
        assert make_predicate["p_murder"] > make_predicate["p_murder_whether"]
        assert make_predicate["p_murder_false"] > make_predicate["p_murder_whether"]


    def test_predicate_contradictions(self, make_predicate):
        assert make_predicate["p7"].contradicts(make_predicate["p7_true"])
        assert not make_predicate["p1"].contradicts(make_predicate["p1_again"])
        assert not make_predicate["p3"].contradicts(make_predicate["p7"])

    def test_predicate_does_not_contradict_factor(self, make_predicate, watt_factor):
        assert not make_predicate["p7_true"].contradicts(watt_factor["f7"])

    def test_no_implication_with_inconsistent_dimensionality(self, make_predicate):
        assert not make_predicate["p9"] >= make_predicate["p9_acres"]
        assert not make_predicate["p9"] <= make_predicate["p9_acres"]

    def test_implication_with_no_truth_value(self, make_predicate):
        assert not make_predicate["p2_no_truth"] > make_predicate["p2"]
        assert make_predicate["p2"] > make_predicate["p2_no_truth"]

    # Contradiction

    def test_no_contradiction_with_no_truth_value(self, make_predicate):
        assert not make_predicate["p2_no_truth"].contradicts(make_predicate["p2"])
        assert not make_predicate["p2"].contradicts(make_predicate["p2_no_truth"])

    def test_no_contradiction_with_inconsistent_dimensionality(self, make_predicate):
        assert not make_predicate["p9"].contradicts(make_predicate["p9_acres"])
        assert not make_predicate["p9_acres"].contradicts(make_predicate["p9"])

class TestCodes:
    def test_making_code(self, make_code):
        const = make_code["const"]
        assert const.title == "Constitution of the United States"

    def test_get_bill_of_rights_effective_date(self, make_code):
        const = make_code["const"]
        bill_of_rights_date = datetime.date(1791, 12, 15)
        assert const.provision_effective_date("amendment-V") == bill_of_rights_date

    def test_get_14th_A_effective_date(self, make_code):
        const = make_code["const"]
        equal_protection_date = datetime.date(1868, 7, 28)
        assert const.provision_effective_date("amendment-XIV") == equal_protection_date


class TestEnactments:
    def test_make_enactment(self, make_code, make_enactment):
        search_clause = make_enactment["search_clause"]
        assert search_clause.text.endswith("shall not be violated")

    def test_code_title_in_str(self, make_enactment):
        assert "secure in their persons" in str(make_enactment["search_clause"])

    def test_equal_enactment_text(self, make_enactment):
        assert make_enactment["due_process_5"] == make_enactment["due_process_14"]

    def test_unequal_enactment_text(self, make_enactment):
        assert make_enactment["search_clause"] != make_enactment["fourth_a"]

    def test_enactment_subset(self, make_enactment):
        assert make_enactment["search_clause"] < make_enactment["fourth_a"]

    def test_enactment_subset_or_equal(self, make_enactment):
        assert make_enactment["due_process_5"] >= make_enactment["due_process_14"]

    @pytest.mark.xfail
    def test_enactment_as_factor(self, make_enactment):
        """
        Removed. Probably a remnant of an experiment in putting enactments
        under "input" "despite" and "output"
        """
        assert isinstance(make_enactment["due_process_5"], Factor)

    def test_bill_of_rights_effective_date(self, make_enactment):
        # December 15, 1791
        assert make_enactment["search_clause"].effective_date == datetime.date(
            1791, 12, 15
        )

    def test_14th_A_effective_date(self, make_enactment):
        # July 28, 1868
        assert make_enactment["due_process_14"].effective_date == datetime.date(
            1868, 7, 28
        )

    def test_compare_effective_dates(self, make_enactment):
        dp5 = make_enactment["due_process_5"]
        dp14 = make_enactment["due_process_14"]

        assert dp14.effective_date > dp5.effective_date


class TestOpinions:
    def test_load_opinion_in_Harvard_format(self):
        with open("json/watt_h.json", "r") as f:
            watt_dict = json.load(f)
        assert watt_dict["name_abbreviation"] == "Wattenburg v. United States"

    def test_opinion_features(self, make_opinion):
        assert make_opinion["watt_majority"].court == "9th-cir"
        assert "388 F.2d 853" in make_opinion["watt_majority"].citations

    def test_opinion_holding_list(self, make_opinion, real_holding):
        assert real_holding["h3"] in make_opinion["watt_majority"].holdings

    def test_opinion_entity_list(self, make_opinion, make_entity):
        assert make_entity["watt"] in make_opinion["watt_majority"].get_entities()

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
