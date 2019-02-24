from typing import Dict, Tuple

import pytest

from enactments import Code, Enactment
from entities import Entity, Event, Human
from evidence import Evidence, Exhibit
from opinions import Opinion
from rules import Procedure, ProceduralRule
from spoke import Predicate, Factor, Fact
from spoke import Q_


@pytest.fixture(scope="class")
def make_entity() -> Dict[str, Entity]:
    return {
        "motel": Entity.new("Hideaway Lodge"),
        "motel_specific": Entity("Hideaway Lodge", generic=False),
        "watt": Human("Wattenburg"),
        "trees": Entity("the stockpile of trees"),
        "trees_specific": Entity.new("the stockpile of trees", generic=False),
        "tree_search": Event("officers' search of the stockpile of trees"),
        "tree_search_specific": Event(
            "officers' search of the stockpile of trees", generic=False
        ),
        "alice": Human("Alice"),
        "bob": Human("Bob"),
        "craig": Human("Craig"),
        "dan": Human("Dan"),
        "circus": Entity("circus"),
    }


@pytest.fixture(scope="class")
def make_predicate() -> Dict[str, Predicate]:

    return {
        "p1": Predicate.new("{} was a motel"),
        "p1_again": Predicate.new("{} was a motel"),
        "p2": Predicate.new("{} operated and lived at {}"),
        "p2_reciprocal": Predicate.new("{} operated and lived at {}", reciprocal=True),
        "p2_no_truth": Predicate.new("{} operated and lived at {}", truth=None),
        "p2_false": Predicate.new("{} operated and lived at {}", truth=False),
        "p3": Predicate.new("{} was {}’s abode"),
        "p3_false": Predicate.new("{} was {}’s abode", truth=False),
        "p4": Predicate.new("{} was on the premises of {}"),
        "p5": Predicate.new("{} was a stockpile of Christmas trees"),
        "p6": Predicate.new("{} was among some standing trees"),
        "p7": Predicate.new(
            "The distance between {} and {} was {}",
            truth=False,
            reciprocal=True,
            comparison=">",
            quantity=Q_("35 feet"),
        ),
        "p7_obverse": Predicate.new(
            "The distance between {} and {} was {}",
            truth=True,
            reciprocal=True,
            comparison="<=",
            quantity=Q_("35 feet"),
        ),
        "p7_opposite": Predicate.new(
            "The distance between {} and {} was {}",
            truth=True,
            reciprocal=True,
            comparison=">",
            quantity=Q_("35 feet"),
        ),
        "p7_true": Predicate.new(
            "The distance between {} and {} was {}",
            truth=True,
            reciprocal=True,
            comparison="<",
            quantity=Q_("35 feet"),
        ),
        "p8": Predicate.new(
            "The distance between {} and {} was {}",
            reciprocal=True,
            comparison=">=",
            quantity=Q_("20 feet"),
        ),
        "p8_exact": Predicate.new(
            "The distance between {} and {} was {}",
            reciprocal=True,
            comparison="=",
            quantity=Q_("25 feet"),
        ),
        "p8_less": Predicate.new(
            "The distance between {} and {} was {}",
            reciprocal=True,
            comparison="<=",
            quantity=Q_("20 feet"),
        ),
        "p8_meters": Predicate.new(
            "The distance between {} and {} was {}",
            reciprocal=True,
            comparison=">=",
            quantity=Q_("10 meters"),
        ),
        "p8_int": Predicate.new(
            "The distance between {} and {} was {}",
            reciprocal=True,
            comparison=">=",
            quantity=20,
        ),
        "p8_float": Predicate.new(
            "The distance between {} and {} was {}",
            reciprocal=True,
            comparison=">=",
            quantity=20.0,
        ),
        "p8_higher_int": Predicate.new(
            "The distance between {} and {} was {}",
            reciprocal=True,
            comparison=">=",
            quantity=30,
        ),
        "p9": Predicate.new(
            "The distance between {} and a parking area used by personnel and patrons of {} was {}",
            comparison="<=",
            quantity=Q_("5 feet"),
        ),
        "p9_miles": Predicate.new(
            "The distance between {} and a parking area used by personnel and patrons of {} was {}",
            comparison="<=",
            quantity=Q_("5 miles"),
        ),
        "p9_acres": Predicate.new(
            "The distance between {} and a parking area used by personnel and patrons of {} was {}",
            comparison="<=",
            quantity=Q_("5 acres"),
        ),
        "p10": Predicate.new("{} was within the curtilage of {}"),
        "p10_false": Predicate.new("{} was within the curtilage of {}", truth=False),
        "p11": Predicate.new("{} was a warrantless search and seizure"),
        "p12": Predicate.new("{} was performed by federal law enforcement officers"),
        "p13": Predicate.new("{} constituted an intrusion upon {}"),
        "p14": Predicate.new("{} sought to preserve {} as private"),
        "p15": Predicate.new("{} was in an area adjacent to {}"),
        "p16": Predicate.new("{} was in an area accessible to the public"),
        "p17": Predicate.new(
            "In {}, several law enforcement officials meticulously went through {}"
        ),
        "p18": Predicate.new(
            "{} continued for {}", comparison=">=", quantity=Q_("385 minutes")
        ),
        "p19": Predicate.new("{} continued after night fell"),
        # Use the irrelevant predicates/factors to make sure they don't affect an outcome.
        "p_irrelevant_0": Predicate.new("{} was a clown"),
        "p_irrelevant_1": Predicate.new("{} was a bear"),
        "p_irrelevant_2": Predicate.new("{} was a circus"),
        "p_irrelevant_3": Predicate.new("{} performed at {}"),
        "p_crime": Predicate.new("{} committed a crime"),
        "p_murder": Predicate.new("{} murdered {}"),
        "p_murder_whether": Predicate.new("{} murdered {}", truth=None),
        "p_murder_false": Predicate.new("{} murdered {}", truth=False),
        "p_irrelevant": Predicate.new("{} is relevant to show {}", truth=False),
        "p_relevant": Predicate.new("{} is relevant to show {}"),
        "p_relevant_whether": Predicate.new("{} is relevant to show {}", truth=None),
        "p_shooting": Predicate.new("{} shot {}"),
        "p_no_shooting": Predicate.new("{} shot {}", truth=False),
        "p_shooting_whether": Predicate.new("{} shot {}", truth=None),
        "p_no_crime": Predicate.new("{} committed a crime", truth=False),
        "p_three_entities": Predicate.new("{} threw {} to {}"),
    }


@pytest.fixture(scope="class")
def watt_mentioned(make_entity) -> Tuple[Entity, ...]:
    e = make_entity
    return (e["motel"], e["watt"], e["trees"], e["tree_search"], e["motel_specific"])


@pytest.fixture(scope="class")
def watt_factor(make_predicate, make_entity, watt_mentioned) -> Dict[str, Factor]:
    p = make_predicate
    e = make_entity

    c = watt_mentioned

    return {
        "f1": Fact.new(p["p1"], case_factors=c),
        "f2": Fact.new(p["p2"], (1, 0), case_factors=c),
        "f3": Fact.new(p["p3"], case_factors=c),
        "f4": Fact.new(p["p4"], (2, 0), case_factors=c),
        "f5": Fact.new(p["p5"], 2, case_factors=c),
        "f6": Fact.new(p["p6"], 2, case_factors=c),
        "f7": Fact.new(p["p7"], (0, 2), case_factors=c),
        "f8": Fact.new(p["p8"], (0, 2), case_factors=c),
        "f9": Fact.new(p["p9"], (2, 0), case_factors=c),
        "f10": Fact.new(p["p10"], (2, 0), case_factors=c),
        "f1_entity_order": Fact.new(p["p1"], (1,), case_factors=c),
        "f1_different_entity": Fact.new(p["p1"], (2,), case_factors=c),
        "f1_specific": Fact.new(p["p1"], (4,), case_factors=c),
        "f1b": Fact.new(p["p1"], case_factors=c),
        "f1c": Fact.new(p["p1_again"], case_factors=c),
        "f2_preponderance_of_evidence": Fact.new(
            p["p2"],
            (1, 0),
            standard_of_proof="preponderance of evidence",
            case_factors=c,
        ),
        "f2_clear_and_convincing": Fact.new(
            p["p2"], (1, 0), standard_of_proof="clear and convincing", case_factors=c
        ),
        "f2_beyond_reasonable_doubt": Fact.new(
            p["p2"], (1, 0), standard_of_proof="beyond reasonable doubt", case_factors=c
        ),
        "f2_different_entity": Fact.new(p["p2"], (1, 2), case_factors=c),
        "f2_entity_order": Fact.new(p["p2"], case_factors=c),
        "f2_no_truth": Fact.new(p["p2_no_truth"], (1, 0), case_factors=c),
        "f2_false": Fact.new(p["p2_false"], case_factors=c),
        "f2_reciprocal": Fact.new(p["p2_reciprocal"], case_factors=c),
        "f2_generic": Fact.new(p["p2"], generic=True, case_factors=c),
        "f2_false_generic": Fact.new(p["p2_false"], generic=True, case_factors=c),
        "f3_generic": Fact.new(p["p3"], generic=True, case_factors=c),
        "f3_different_entity": Fact.new(p["p3"], (2, 1), case_factors=c),
        "f3_entity_order": Fact.new(p["p3"], (1, 0), case_factors=c),
        "f3_absent": Fact.new(p["p3"], absent=True, case_factors=c),
        "f4_h4": Fact.new(p["p4"], (3, 0), case_factors=c),
        "f4_swap_entities": Fact.new(p["p4"], (0, 2), case_factors=c),
        "f4_swap_entities_4": Fact.new(p["p4"], (1, 4), case_factors=c),
        "f5_h4": Fact.new(p["p5"], (3,), case_factors=c),
        "f5_swap_entities": Fact.new(p["p5"], (0,), case_factors=c),
        "f6_swap_entities": Fact.new(p["p6"], (0,), case_factors=c),
        "f7_opposite": Fact.new(p["p7_opposite"], (0, 2), case_factors=c),
        "f7_swap_entities": Fact.new(p["p7"], (2, 0), case_factors=c),
        "f7_swap_entities_4": Fact.new(p["p7"], (1, 4), case_factors=c),
        "f7_true": Fact.new(p["p7_true"], (0, 2), case_factors=c),
        "f8_absent": Fact.new(p["p8"], (0, 2), absent=True, case_factors=c),
        "f8_exact": Fact.new(p["p8_exact"], (0, 2), case_factors=c),
        "f8_exact_swap_entities": Fact.new(p["p8_exact"], (1, 0), case_factors=c),
        "f8_float": Fact.new(p["p8_float"], (0, 2), case_factors=c),
        "f8_higher_int": Fact.new(p["p8_higher_int"], (0, 2), case_factors=c),
        "f8_int": Fact.new(p["p8_int"], (0, 2), case_factors=c),
        "f8_less": Fact.new(p["p8_less"], (0, 2), case_factors=c),
        "f8_meters": Fact.new(p["p8_meters"], (0, 2), case_factors=c),
        "f9_absent": Fact.new(p["p9"], absent=True, case_factors=c),
        "f9_absent_miles": Fact.new(p["p9_miles"], absent=True, case_factors=c),
        "f9_swap_entities": Fact.new(p["p9"], (0, 2), case_factors=c),
        "f9_swap_entities_4": Fact.new(p["p9"], (1, 4), case_factors=c),
        "f10_absent": Fact.new(p["p10"], absent=True, case_factors=c),
        "f10_false": Fact.new(p["p10_false"], case_factors=c),
        "f10_absent_false": Fact.new(p["p10_false"], absent=True, case_factors=c),
        "f10_swap_entities": Fact.new(p["p10"], (0, 2), case_factors=c),
        "f10_swap_entities_4": Fact.new(p["p10"], (1, 4), case_factors=c),
        "f11": Fact.new(p["p11"], 2, case_factors=c),
        "f12": Fact.new(p["p12"], 2, case_factors=c),
        "f13": Fact.new(p["p13"], (2, 3), case_factors=c),
        "f14": Fact.new(p["p14"], (1, 3), case_factors=c),
        "f15": Fact.new(p["p15"], (3, 0), case_factors=c),
        "f16": Fact.new(p["p16"], 3, case_factors=c),
        "f17": Fact.new(p["p17"], (2, 3), case_factors=c),
        "f18": Fact.new(p["p18"], 2, case_factors=c),
        "f19": Fact.new(p["p19"], 2, case_factors=c),
    }


@pytest.fixture(scope="class")
def make_factor(make_predicate, make_entity) -> Dict[str, Factor]:
    p = make_predicate
    e = make_entity

    c = (e["alice"], e["bob"], e["craig"], e["dan"], e["circus"])

    return {
        "f_irrelevant_0": Fact.new(p["p_irrelevant_0"], (2,), case_factors=c),
        "f_irrelevant_1": Fact.new(p["p_irrelevant_1"], (3,), case_factors=c),
        "f_irrelevant_2": Fact.new(p["p_irrelevant_2"], (4,), case_factors=c),
        "f_irrelevant_3": Fact.new(p["p_irrelevant_3"], (2, 4), case_factors=c),
        "f_irrelevant_3_new_context": Fact.new(
            p["p_irrelevant_3"], (3, 4), case_factors=c
        ),
        "f_irrelevant_3_context_0": Fact.new(
            p["p_irrelevant_3"], (3, 0), case_factors=c
        ),
        "f_crime": Fact.new(p["p_crime"], case_factors=c),
        "f_no_crime": Fact.new(p["p_no_crime"], case_factors=c),
        "f_no_crime_entity_order": Fact.new(p["p_no_crime"], (1,), case_factors=c),
        "f_murder": Fact.new(p["p_murder"], case_factors=c),
        "f_no_murder": Fact.new(p["p_murder_false"], case_factors=c),
        "f_murder_entity_swap": Fact.new(p["p_murder"], (1, 0), case_factors=c),
        "f_murder_craig": Fact.new(p["p_murder"], (2, 3), case_factors=c),
        "f_murder_whether": Fact.new(p["p_murder_whether"], case_factors=c),
        "f_shooting": Fact.new(p["p_shooting"], case_factors=c),
        "f_shooting_craig": Fact.new(p["p_shooting"], (2, 3), case_factors=c),
        "f_shooting_entity_order": Fact.new(
            p["p_shooting"], (1, 0), case_factors=c
        ),
        "f_no_shooting": Fact.new(p["p_no_shooting"], case_factors=c),
        "f_shooting_whether": Fact.new(p["p_shooting_whether"], case_factors=c),
        "f_no_shooting_entity_order": Fact.new(
            p["p_no_shooting"], (1, 0), case_factors=c
        ),
        "f_three_entities": Fact.new(p["p_three_entities"], (0, 1, 2), case_factors=c),
        "f_repeating_entity": Fact.new(
            p["p_three_entities"], (0, 1, 0), case_factors=c
        ),
    }


@pytest.fixture(scope="class")
def make_complex_fact(make_predicate, make_factor) -> Dict[str, Evidence]:
    p = make_predicate
    f = make_factor

    return {
        "f_irrelevant_murder": Fact.new(
            p["p_irrelevant"], (f["f_shooting"], f["f_murder"])
        ),
        "f_relevant_murder": Fact.new(
            p["p_relevant"], (f["f_shooting"], f["f_murder"])
        ),
        "f_relevant_murder_swap_entities": Fact.new(
            p["p_relevant"], (f["f_shooting"], f["f_murder"])
        ),
        "f_relevant_murder_nested_swap": Fact.new(
            p["p_relevant"], (f['f_shooting_entity_order'], f['f_murder_entity_swap'])
        ),
        "f_relevant_murder_whether": Fact.new(
            p["p_relevant"], (f["f_shooting"], f["f_murder_whether"])
        ),
        "f_whether_relevant_murder_whether": Fact.new(
            p["p_relevant"], (f["f_shooting_whether"], f["f_murder_whether"])
        ),
        "f_relevant_murder_swap": Fact.new(
            p["p_relevant"], (f["f_shooting"], f["f_murder_entity_swap"])
        ),
        "f_relevant_murder_craig": Fact.new(
            p["p_relevant"], (f["f_shooting_craig"], f["f_murder_craig"])
        ),
        "f_relevant_murder_alice_craig": Fact.new(
            p["p_relevant"], (f["f_shooting"], f["f_murder_craig"])
        ),
    }


@pytest.fixture(scope="class")
def make_exhibit(
    make_entity, make_predicate, make_factor, watt_factor, make_complex_fact
) -> Dict[str, Exhibit]:
    e = make_entity
    f = make_factor
    p = make_predicate
    w = watt_factor
    x = make_complex_fact

    return {
        "shooting_testimony": Exhibit(
            form="testimony", statement=f["f_shooting"], stated_by=e["alice"]
        ),
        "no_shooting_testimony": Exhibit(
            form="testimony", statement=f["f_no_shooting"], stated_by=e["alice"]
        ),
        "no_shooting_entity_order_testimony": Exhibit(
            form="testimony",
            statement=f["f_no_shooting_entity_order"],
            stated_by=e["bob"],
        ),
        "no_shooting_witness_unknown_testimony": Exhibit(
            form="testimony", statement=f["f_no_shooting"]
        ),
        "no_shooting_witness_unknown_absent_testimony": Exhibit(
            form="testimony", statement=f["f_no_shooting"], absent=True
        ),
        "no_shooting_no_effect_entity_order_testimony": Exhibit(
            form="testimony",
            statement=f["f_no_shooting_entity_order"],
            stated_by=e["bob"],
        ),
        "no_shooting_different_witness_testimony": Exhibit(
            form="testimony", statement=f["f_no_shooting"], stated_by=e["bob"]
        ),
        "reciprocal_testimony": Exhibit(
            form="testimony", statement=w["f8"], stated_by=e["craig"]
        ),
        "reciprocal_testimony_specific": Exhibit(
            form="testimony", statement=w["f8_meters"], stated_by=e["craig"]
        ),
        "relevant_murder_testimony": Exhibit(
            form="testimony", statement=x["f_relevant_murder"], stated_by=e["alice"]
        ),
        "relevant_murder_nested_swap_testimony": Exhibit(
            form="testimony", statement=x["f_relevant_murder_nested_swap"], stated_by=e["bob"]
        ),
        "relevant_murder_alice_craig_testimony": Exhibit(
            form="testimony", statement=x["f_relevant_murder_alice_craig"], stated_by=e["alice"]
        ),
        "generic_exhibit": Exhibit(),
    }


@pytest.fixture(scope="class")
def make_evidence(make_predicate, make_factor, watt_factor) -> Dict[str, Evidence]:
    p = make_predicate
    f = make_factor
    w = watt_factor
    return {
        "shooting": Evidence(
            Exhibit("shooting_testimony"),
            to_effect=f["f_crime"],
        ),
        "no_shooting": Evidence(
            Exhibit("no_shooting_testimony"),
            to_effect=f["f_no_crime"],
        ),
        "no_shooting_absent": Evidence(
            Exhibit("no_shooting_testimony"),
            to_effect=f["f_no_crime"],
            absent=True,
        ),
        "no_shooting_entity_order": Evidence(
            Exhibit("no_shooting_entity_order_testimony"),
            to_effect=f["f_no_crime_entity_order"],
        ),
        "no_shooting_witness_unknown": Evidence(
            Exhibit("no_shooting_witness_unknown_testimony"), to_effect=f["f_no_crime"]
        ),
        # Here the Exhibit is absent, not the Evidence. Pointless distinction?
        "no_shooting_witness_unknown_absent": Evidence(
            Exhibit("no_shooting_witness_unknown_absent_testimony"),
            to_effect=f["f_no_crime"],
        ),
        "no_shooting_no_effect_entity_order": Evidence(
            Exhibit("no_shooting_no_effect_entity_order_testimony")
        ),
        "no_shooting_different_witness": Evidence(
            Exhibit("no_shooting_different_witness_testimony"),
            to_effect=f["f_no_crime"],
        ),
        "reciprocal": Evidence(
            Exhibit("reciprocal_testimony"), to_effect=f["f_no_crime"]
        ),
        "crime": Evidence(Exhibit("generic_exhibit"), generic=True),
        "crime_absent": Evidence(Exhibit("generic_exhibit"), absent=True, generic=True),
    }

@pytest.fixture(scope="module")
def make_code() -> Dict[str, Code]:
    return {"const": Code("constitution.xml")}


@pytest.fixture(scope="module")
def make_enactment(make_code) -> Dict[str, Enactment]:
    const = make_code["const"]

    return {
        "search_clause": Enactment(const, "amendment-IV", end="violated"),
        "fourth_a": Enactment(const, "amendment-IV"),
        "due_process_5": Enactment(
            const,
            "amendment-V",
            start="life, liberty, or property",
            end="due process of law",
        ),
        "due_process_14": Enactment(
            const,
            "amendment-XIV-1",
            start="life, liberty, or property",
            end="due process of law",
        ),
    }


@pytest.fixture(scope="class")
def make_procedure(make_evidence, make_factor, watt_factor) -> Dict[str, Procedure]:
    e = make_evidence
    f = watt_factor
    m = make_factor

    return {
        "c1": Procedure(outputs=(f["f3"],), inputs=(f["f1"], f["f2"])),
        "c2": Procedure(
            outputs=(f["f10"],),
            inputs=(f["f4"], f["f5"], f["f6"], f["f7"], f["f9"]),
            despite=(f["f8"],),
        ),
        "c3": Procedure(
            outputs=e["crime_absent"],
            inputs=(f["f3"], f["f11"], f["f12"], f["f13"], f["f14"], f["f15"]),
            despite=(f["f16"]),
        ),
        "c4": Procedure(
            outputs=f["f13"],
            inputs=(
                f["f1"],
                f["f2"],
                f["f4_h4"],
                f["f5_h4"],
                f["f11"],
                f["f12"],
                f["f17"],
                f["f18"],
                f["f19"],
            ),
        ),
        "c1_again": Procedure(outputs=(f["f3"],), inputs=(f["f1"], f["f2"])),
        "c1_entity_order": Procedure(
            outputs=(f["f3_different_entity"],),
            inputs=(f["f2_different_entity"], f["f1_different_entity"]),
        ),
        "c1_easy": Procedure(outputs=(f["f3"],), inputs=(f["f2"])),
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
                m["f_irrelevant_0"],
                m["f_irrelevant_1"],
                m["f_irrelevant_2"],
                m["f_irrelevant_3"],
                m["f_irrelevant_3_new_context"],
            ),
            despite=(f["f8"],),
        ),
        "c2_irrelevant_outputs": Procedure(
            outputs=(
                f["f10_swap_entities"],
                m["f_irrelevant_0"],
                m["f_irrelevant_1"],
                m["f_irrelevant_2"],
                m["f_irrelevant_3"],
                m["f_irrelevant_3_context_0"],
            ),
            inputs=(
                f["f4_swap_entities"],
                f["f5_swap_entities"],
                f["f6_swap_entities"],
                f["f7_swap_entities"],
                f["f9_swap_entities"],
            ),
        ),
        "c2_irrelevant_despite": Procedure(
            outputs=(f["f10"],),
            inputs=(f["f4"], f["f5"], f["f6"], f["f7"], f["f9"]),
            despite=(
                f["f8"],
                m["f_irrelevant_0"],
                m["f_irrelevant_1"],
                m["f_irrelevant_2"],
                m["f_irrelevant_3"],
                m["f_irrelevant_3_new_context"],
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
        "c_near_means_curtilage_even_if": Procedure(
            outputs=(f["f10"],), inputs=(f["f7"]), despite=(f["f8"])
        ),
        "c_far_means_no_curtilage": Procedure(
            outputs=(f["f10_false"],), inputs=(f["f8"])
        ),
        "c3_fewer_inputs": Procedure(
            outputs=e["crime_absent"],
            inputs=(f["f3"], f["f11"], f["f12"], f["f15"]),
            despite=(f["f16"]),
        ),
    }


@pytest.fixture(scope="class")
def real_holding(make_procedure, make_enactment) -> Dict[str, ProceduralRule]:
    """These holdings can be changed in case they don't accurately reflect
    what's in real cases, or in case there are API improvements that
    allow them to become more accurate. I'll try not to write any tests
    that depend on them remaining the same."""

    c = make_procedure
    e = make_enactment

    return {
        "h1": ProceduralRule(c["c1"], enactments=e["search_clause"], mandatory=True),
        "h2": ProceduralRule(c["c2"], enactments=e["search_clause"], mandatory=True),
        "h3": ProceduralRule(c["c3"], enactments=e["search_clause"], mandatory=True),
        "h4": ProceduralRule(c["c4"], enactments=e["search_clause"], mandatory=True),
    }


@pytest.fixture(scope="class")
def make_holding(make_procedure, make_enactment) -> Dict[str, ProceduralRule]:
    c = make_procedure
    e = make_enactment

    return {
        "h1": ProceduralRule(c["c1"], enactments=e["search_clause"]),
        "h2": ProceduralRule(c["c2"], enactments=e["search_clause"]),
        "h3": ProceduralRule(c["c3"], enactments=e["search_clause"]),
        "h1_again": ProceduralRule(c["c1"], enactments=e["search_clause"]),
        "h1_entity_order": ProceduralRule(
            c["c1_entity_order"], enactments=e["search_clause"]
        ),
        "h1_easy": ProceduralRule(c["c1_easy"], enactments=e["search_clause"]),
        "h1_opposite": ProceduralRule(
            c["c1"], enactments=e["search_clause"], rule_valid=False
        ),
        "h2_without_cite": ProceduralRule(c["c2"]),
        "h2_fourth_a_cite": ProceduralRule(c["c2"], enactments=e["fourth_a"]),
        "h2_despite_due_process": ProceduralRule(
            c["c2"],
            enactments=e["search_clause"],
            enactments_despite=e["due_process_5"],
        ),
        "h2_ALL_due_process": ProceduralRule(
            c["c2"],
            enactments=(e["search_clause"], e["due_process_5"]),
            mandatory=False,
            universal=True,
            rule_valid=True,
        ),
        "h2_ALL_due_process_invalid": ProceduralRule(
            c["c2"],
            enactments=(e["search_clause"], e["due_process_5"]),
            mandatory=False,
            universal=True,
            rule_valid=False,
        ),
        "h2_ALL": ProceduralRule(
            c["c2"], enactments=e["search_clause"], mandatory=False, universal=True
        ),
        "h2_ALL_invalid": ProceduralRule(
            c["c2"],
            enactments=e["search_clause"],
            mandatory=False,
            universal=True,
            rule_valid=False,
        ),
        "h2_ALL_MAY_output_false": ProceduralRule(
            c["c2_output_false"],
            enactments=e["search_clause"],
            mandatory=False,
            universal=True,
        ),
        "h2_ALL_MUST": ProceduralRule(
            c["c2"], enactments=e["search_clause"], mandatory=True, universal=True
        ),
        "h2_ALL_MUST_output_false": ProceduralRule(
            c["c2_output_false"],
            enactments=e["search_clause"],
            mandatory=True,
            universal=True,
        ),
        "h2_exact_quantity": ProceduralRule(
            c["c2_exact_quantity"], enactments=e["search_clause"]
        ),
        "h2_invalid": ProceduralRule(
            c["c2"], enactments=e["search_clause"], rule_valid=False
        ),
        "h2_irrelevant_inputs": ProceduralRule(
            c["c2_irrelevant_inputs"], enactments=e["search_clause"]
        ),
        "h2_irrelevant_inputs_invalid": ProceduralRule(
            c["c2_irrelevant_inputs"], enactments=e["search_clause"], rule_valid=False
        ),
        "h2_irrelevant_inputs_ALL_MUST": ProceduralRule(
            c["c2_irrelevant_inputs"],
            enactments=e["search_clause"],
            mandatory=True,
            universal=True,
        ),
        "h2_irrelevant_inputs_ALL_MUST_invalid": ProceduralRule(
            c["c2_irrelevant_inputs"],
            enactments=e["search_clause"],
            mandatory=True,
            universal=True,
            rule_valid=False,
        ),
        "h2_irrelevant_inputs_ALL_invalid": ProceduralRule(
            c["c2_irrelevant_inputs"],
            enactments=e["search_clause"],
            universal=True,
            rule_valid=False,
        ),
        "h2_irrelevant_inputs_MUST": ProceduralRule(
            c["c2_irrelevant_inputs"], enactments=e["search_clause"], mandatory=True
        ),
        "h2_irrelevant_inputs_MUST_invalid": ProceduralRule(
            c["c2_irrelevant_inputs"],
            enactments=e["search_clause"],
            mandatory=True,
            rule_valid=False,
        ),
        "h2_reciprocal_swap": ProceduralRule(
            c["c2_reciprocal_swap"], enactments=e["search_clause"]
        ),
        "h2_exact_in_despite": ProceduralRule(
            c["c2_exact_in_despite"], enactments=e["search_clause"]
        ),
        "h2_exact_in_despite_ALL": ProceduralRule(
            c["c2_exact_in_despite"],
            enactments=e["search_clause"],
            mandatory=False,
            universal=True,
        ),
        "h2_exact_in_despite_ALL_entity_order": ProceduralRule(
            c["c2_exact_in_despite_entity_order"],
            enactments=e["search_clause"],
            mandatory=False,
            universal=True,
        ),
        "h2_exact_quantity_ALL": ProceduralRule(
            c["c2_exact_quantity"],
            enactments=e["search_clause"],
            mandatory=False,
            universal=True,
        ),
        "h2_invalid_undecided": ProceduralRule(
            c["c2"], enactments=e["search_clause"], rule_valid=False, decided=False
        ),
        "h2_MUST": ProceduralRule(
            c["c2"], enactments=e["search_clause"], mandatory=True, universal=False
        ),
        "h2_MUST_invalid": ProceduralRule(
            c["c2"], enactments=e["search_clause"], mandatory=True, rule_valid=False
        ),
        "h2_output_absent": ProceduralRule(
            c["c2_output_absent"], enactments=e["search_clause"]
        ),
        "h2_output_false": ProceduralRule(
            c["c2_output_false"], enactments=e["search_clause"]
        ),
        "h2_output_false_ALL": ProceduralRule(
            c["c2_output_false"], enactments=e["search_clause"], universal=True
        ),
        "h2_output_absent_false": ProceduralRule(
            c["c2_output_absent_false"], enactments=e["search_clause"]
        ),
        "h2_SOME_MUST_output_false": ProceduralRule(
            c["c2_output_false"],
            enactments=e["search_clause"],
            mandatory=True,
            universal=False,
        ),
        "h2_SOME_MUST_output_absent": ProceduralRule(
            c["c2_output_absent"],
            enactments=e["search_clause"],
            mandatory=True,
            universal=False,
        ),
        "h2_undecided": ProceduralRule(
            c["c2"], enactments=e["search_clause"], decided=False
        ),
        "h2_irrelevant_inputs_undecided": ProceduralRule(
            c["c2_irrelevant_inputs"], enactments=e["search_clause"], decided=False
        ),
        "h2_MUST_undecided": ProceduralRule(
            c["c2"], enactments=e["search_clause"], mandatory=True, decided=False
        ),
        "h3_ALL": ProceduralRule(
            c["c3"], enactments=e["search_clause"], universal=True
        ),
        "h3_fewer_inputs": ProceduralRule(
            c["c3_fewer_inputs"], enactments=e["search_clause"]
        ),
        "h3_undecided": ProceduralRule(
            c["c3"], enactments=e["search_clause"], decided=False
        ),
        "h3_ALL_undecided": ProceduralRule(
            c["c3"], enactments=e["search_clause"], decided=False, universal=True
        ),
        "h3_fewer_inputs_ALL": ProceduralRule(
            c["c3_fewer_inputs"], enactments=e["search_clause"], universal=True
        ),
        "h3_fewer_inputs_undecided": ProceduralRule(
            c["c3_fewer_inputs"], enactments=e["search_clause"], decided=False
        ),
        "h3_fewer_inputs_ALL_undecided": ProceduralRule(
            c["c3_fewer_inputs"],
            enactments=e["search_clause"],
            universal=True,
            decided=False,
        ),
        "h_near_means_curtilage": ProceduralRule(
            c["c_near_means_curtilage"], enactments=e["search_clause"]
        ),
        "h_near_means_curtilage_even_if": ProceduralRule(
            c["c_near_means_curtilage_even_if"], enactments=e["search_clause"]
        ),
        "h_near_means_curtilage_ALL_MUST": ProceduralRule(
            c["c_near_means_curtilage"],
            enactments=e["search_clause"],
            mandatory=True,
            universal=True,
        ),
        "h_near_means_curtilage_ALL_undecided": ProceduralRule(
            c["c_near_means_curtilage"],
            enactments=e["search_clause"],
            universal=True,
            decided=False,
        ),
        "h_near_means_no_curtilage": ProceduralRule(
            c["c_near_means_no_curtilage"], enactments=e["search_clause"]
        ),
        "h_near_means_no_curtilage_ALL": ProceduralRule(
            c["c_near_means_no_curtilage"],
            enactments=e["search_clause"],
            universal=True,
        ),
        "h_near_means_no_curtilage_ALL_MUST": ProceduralRule(
            c["c_near_means_no_curtilage"],
            enactments=e["search_clause"],
            mandatory=True,
            universal=True,
        ),
        "h_nearer_means_curtilage": ProceduralRule(
            c["c_nearer_means_curtilage"], enactments=e["search_clause"]
        ),
        "h_nearer_means_curtilage_ALL": ProceduralRule(
            c["c_nearer_means_curtilage"], enactments=e["search_clause"], universal=True
        ),
        "h_nearer_means_curtilage_MUST": ProceduralRule(
            c["c_nearer_means_curtilage"], enactments=e["search_clause"], mandatory=True
        ),
        "h_far_means_no_curtilage": ProceduralRule(c["c_far_means_no_curtilage"]),
        "h_far_means_no_curtilage_ALL": ProceduralRule(
            c["c_far_means_no_curtilage"], enactments=e["search_clause"], universal=True
        ),
    }


@pytest.fixture(scope="class")
def make_opinion(make_entity, real_holding) -> Dict[str, Opinion]:
    h = real_holding
    e = make_entity

    test_cases = ("brad", "cardenas", "watt")
    opinions = {}
    for case in test_cases:
        for opinion in Opinion.from_file(f"json/{case}_h.json"):
            opinions[f"{case}_{opinion.position}"] = opinion
    opinions["watt_majority"].posits(h["h1"], (e["motel"], e["watt"]))
    opinions["watt_majority"].posits(h["h2"], (e["trees"], e["motel"]))
    opinions["watt_majority"].posits(
        h["h3"], (e["motel"], e["watt"], e["tree_search"], e["trees"])
    )
    opinions["watt_majority"].posits(
        h["h4"], (e["motel"], e["watt"], e["tree_search"], e["trees"])
    )
    return opinions
