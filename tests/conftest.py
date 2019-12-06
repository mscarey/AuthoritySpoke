from typing import Any, Dict, Tuple

from anchorpoint.textselectors import TextQuoteSelector
import pytest


from authorityspoke.codes import Code
from authorityspoke.enactments import Enactment
from authorityspoke.entities import Entity
from authorityspoke.evidence import Evidence, Exhibit
from authorityspoke.factors import Factor
from authorityspoke.facts import Fact, build_fact
from authorityspoke.holdings import Holding
from authorityspoke.jurisdictions import Jurisdiction, Regime
from authorityspoke.opinions import Opinion
from authorityspoke.pleadings import Pleading, Allegation
from authorityspoke.predicates import Predicate, Q_
from authorityspoke.rules import Procedure, Rule

from authorityspoke.io import loaders, readers
from authorityspoke.io.schemas import RawHolding



@pytest.fixture(scope="class")
def make_entity() -> Dict[str, Entity]:
    return {
        "motel": Entity("Hideaway Lodge"),
        "motel_specific": Entity("Hideaway Lodge", generic=False),
        "watt": Entity("Wattenburg"),
        "trees": Entity("the stockpile of trees"),
        "trees_specific": Entity("the stockpile of trees", generic=False),
        "tree_search": Entity("officers' search of the stockpile of trees"),
        "tree_search_specific": Entity(
            "officers' search of the stockpile of trees", generic=False
        ),
        "alice": Entity("Alice"),
        "bob": Entity("Bob"),
        "craig": Entity("Craig"),
        "dan": Entity("Dan"),
        "circus": Entity("circus"),
    }


@pytest.fixture(scope="class")
def make_predicate() -> Dict[str, Predicate]:

    return {
        "p1": Predicate("{} was a motel"),
        "p1_again": Predicate("{} was a motel"),
        "p2": Predicate("{} operated and lived at {}"),
        "p2_reciprocal": Predicate("{} operated and lived at {}", reciprocal=True),
        "p2_no_truth": Predicate("{} operated and lived at {}", truth=None),
        "p2_false": Predicate("{} operated and lived at {}", truth=False),
        "p3": Predicate("{} was {}’s abode"),
        "p3_false": Predicate("{} was {}’s abode", truth=False),
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
        "p7_opposite": Predicate(
            "the distance between {} and {} was {}",
            truth=True,
            reciprocal=True,
            comparison=">",
            quantity=Q_("35 feet"),
        ),
        "p7_not_equal": Predicate(
            "the distance between {} and {} was {}",
            truth=True,
            reciprocal=True,
            comparison="<>",
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
            "the distance between {} and {} was {}",
            reciprocal=True,
            comparison=">=",
            quantity=Q_("20 feet"),
        ),
        "p8_exact": Predicate(
            "the distance between {} and {} was {}",
            reciprocal=True,
            comparison="==",
            quantity=Q_("25 feet"),
        ),
        "p8_less": Predicate(
            "the distance between {} and {} was {}",
            reciprocal=True,
            comparison="<=",
            quantity=Q_("20 feet"),
        ),
        "p8_meters": Predicate(
            "the distance between {} and {} was {}",
            reciprocal=True,
            comparison=">=",
            quantity=Q_("10 meters"),
        ),
        "p8_int": Predicate(
            "the distance between {} and {} was {}",
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
            "the distance between {} and {} was {}",
            reciprocal=True,
            comparison=">=",
            quantity=30,
        ),
        "p9": Predicate(
            "the distance between {} and a parking area used by personnel and patrons of {} was {}",
            comparison="<=",
            quantity=Q_("5 feet"),
        ),
        "p9_exact": Predicate(
            "the distance between {} and a parking area used by personnel and patrons of {} was {}",
            comparison="=",
            quantity=Q_("5 feet"),
        ),
        "p9_miles": Predicate(
            "the distance between {} and a parking area used by personnel and patrons of {} was {}",
            comparison="<=",
            quantity=Q_("5 miles"),
        ),
        "p9_more": Predicate(
            "the distance between {} and a parking area used by personnel and patrons of {} was {}",
            comparison=">",
            quantity=Q_("5 feet"),
        ),
        "p9_acres": Predicate(
            "the distance between {} and a parking area used by personnel and patrons of {} was {}",
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
        # Use the irrelevant predicates/factors to make sure they don't affect an outcome.
        "p_irrelevant_0": Predicate("{} was a clown"),
        "p_irrelevant_1": Predicate("{} was a bear"),
        "p_irrelevant_2": Predicate("{} was a circus"),
        "p_irrelevant_3": Predicate("{} performed at {}"),
        "p_crime": Predicate("{} committed a crime"),
        "p_murder": Predicate("{} murdered {}"),
        "p_murder_whether": Predicate("{} murdered {}", truth=None),
        "p_murder_false": Predicate("{} murdered {}", truth=False),
        "p_irrelevant": Predicate("{} is relevant to show {}", truth=False),
        "p_relevant": Predicate("{} is relevant to show {}"),
        "p_relevant_whether": Predicate("{} is relevant to show {}", truth=None),
        "p_shooting": Predicate("{} shot {}"),
        "p_shooting_self": Predicate("{0} shot {0}"),
        "p_no_shooting": Predicate("{} shot {}", truth=False),
        "p_shooting_whether": Predicate("{} shot {}", truth=None),
        "p_no_crime": Predicate("{} committed a crime", truth=False),
        "p_three_entities": Predicate("{} told {} to hire {}"),
        "p_small_weight": Predicate(
            "the amount of gold {} possessed was {}",
            comparison=">=",
            quantity=Q_("1 gram"),
        ),
        "p_large_weight": Predicate(
            "the amount of gold {} possessed was {}",
            comparison=">=",
            quantity=Q_("100 kilograms"),
        ),
        "p_friends": Predicate("{} and {} were friends", reciprocal=True),
        "p_reliable": Predicate("{} was reliable"),
        "p_quantity=3": Predicate(
            "The number of mice was {}", comparison="==", quantity=3
        ),
        "p_quantity>=4": Predicate(
            "The number of mice was {}", comparison=">=", quantity=4
        ),
        "p_quantity>5": Predicate(
            "The number of mice was {}", comparison=">", quantity=5
        ),
    }


@pytest.fixture(scope="class")
def watt_mentioned(make_entity) -> Tuple[Entity, ...]:
    e = make_entity
    return (e["motel"], e["watt"], e["trees"], e["tree_search"], e["motel_specific"])


@pytest.fixture(scope="class")
def watt_factor(make_predicate, make_entity, watt_mentioned) -> Dict[str, Factor]:
    p = make_predicate

    c = watt_mentioned

    return {
        "f1": build_fact(p["p1"], case_factors=c),
        "f2": build_fact(p["p2"], (1, 0), case_factors=c),
        "f3": build_fact(p["p3"], case_factors=c),
        "f4": build_fact(p["p4"], (2, 0), case_factors=c),
        "f5": build_fact(p["p5"], 2, case_factors=c),
        "f6": build_fact(p["p6"], 2, case_factors=c),
        "f7": build_fact(p["p7"], (0, 2), case_factors=c),
        "f8": build_fact(p["p8"], (0, 2), case_factors=c),
        "f9": build_fact(p["p9"], (2, 0), case_factors=c),
        "f10": build_fact(p["p10"], (2, 0), case_factors=c),
        "f1_entity_order": build_fact(p["p1"], (1,), case_factors=c),
        "f1_different_entity": build_fact(p["p1"], (2,), case_factors=c),
        "f1_specific": build_fact(p["p1"], (4,), case_factors=c),
        "f1b": build_fact(p["p1"], case_factors=c),
        "f1c": build_fact(p["p1_again"], case_factors=c),
        "f2_preponderance_of_evidence": build_fact(
            p["p2"],
            (1, 0),
            standard_of_proof="preponderance of evidence",
            case_factors=c,
        ),
        "f2_clear_and_convincing": build_fact(
            p["p2"], (1, 0), standard_of_proof="clear and convincing", case_factors=c
        ),
        "f2_beyond_reasonable_doubt": build_fact(
            p["p2"], (1, 0), standard_of_proof="beyond reasonable doubt", case_factors=c
        ),
        "f2_different_entity": build_fact(p["p2"], (1, 2), case_factors=c),
        "f2_entity_order": build_fact(p["p2"], case_factors=c),
        "f2_no_truth": build_fact(p["p2_no_truth"], (1, 0), case_factors=c),
        "f2_false": build_fact(p["p2_false"], case_factors=c),
        "f2_false_absent": build_fact(p["p2_false"], absent=True, case_factors=c),
        "f2_reciprocal": build_fact(p["p2_reciprocal"], case_factors=c),
        "f2_generic": build_fact(p["p2"], generic=True, case_factors=c),
        "f2_false_generic": build_fact(p["p2_false"], generic=True, case_factors=c),
        "f3_generic": build_fact(p["p3"], generic=True, case_factors=c),
        "f3_different_entity": build_fact(p["p3"], (2, 1), case_factors=c),
        "f3_entity_order": build_fact(p["p3"], (1, 0), case_factors=c),
        "f3_absent": build_fact(p["p3"], absent=True, case_factors=c),
        "f4_h4": build_fact(p["p4"], (3, 0), case_factors=c),
        "f4_swap_entities": build_fact(p["p4"], (0, 2), case_factors=c),
        "f4_swap_entities_4": build_fact(p["p4"], (1, 4), case_factors=c),
        "f5_h4": build_fact(p["p5"], (3,), case_factors=c),
        "f5_swap_entities": build_fact(p["p5"], (0,), case_factors=c),
        "f6_swap_entities": build_fact(p["p6"], (0,), case_factors=c),
        "f7_opposite": build_fact(p["p7_opposite"], (0, 2), case_factors=c),
        "f7_swap_entities": build_fact(p["p7"], (2, 0), case_factors=c),
        "f7_swap_entities_4": build_fact(p["p7"], (1, 4), case_factors=c),
        "f7_true": build_fact(p["p7_true"], (0, 2), case_factors=c),
        "f8_absent": build_fact(p["p8"], (0, 2), absent=True, case_factors=c),
        "f8_exact": build_fact(p["p8_exact"], (0, 2), case_factors=c),
        "f8_exact_swap_entities": build_fact(p["p8_exact"], (2, 0), case_factors=c),
        "f8_float": build_fact(p["p8_float"], (0, 2), case_factors=c),
        "f8_higher_int": build_fact(p["p8_higher_int"], (0, 2), case_factors=c),
        "f8_int": build_fact(p["p8_int"], (0, 2), case_factors=c),
        "f8_less": build_fact(p["p8_less"], (0, 2), case_factors=c),
        "f8_less_absent": build_fact(p["p8_less"], (0, 2), absent=True, case_factors=c),
        "f8_meters": build_fact(p["p8_meters"], (0, 2), case_factors=c),
        "f9_absent": build_fact(p["p9"], (2, 0), absent=True, case_factors=c),
        "f9_miles": build_fact(p["p9_miles"], (2, 0), case_factors=c),
        "f9_absent_miles": build_fact(
            p["p9_miles"], (2, 0), absent=True, case_factors=c
        ),
        "f9_more_swap_entities": Fact(
            p["p9_more"], (make_entity["circus"], make_entity["motel"])
        ),
        "f9_swap_entities": build_fact(p["p9"], (0, 2), case_factors=c),
        "f9_swap_entities_4": build_fact(p["p9"], (1, 4), case_factors=c),
        "f10_absent": build_fact(p["p10"], (2, 0), absent=True, case_factors=c),
        "f10_false": build_fact(p["p10_false"], (2, 0), case_factors=c),
        "f10_absent_false": build_fact(p["p10_false"], absent=True, case_factors=c),
        "f10_swap_entities": build_fact(p["p10"], (0, 2), case_factors=c),
        "f10_swap_entities_4": build_fact(p["p10"], (1, 4), case_factors=c),
        "f11": build_fact(p["p11"], 3, case_factors=c),
        "f12": build_fact(p["p12"], 3, case_factors=c),
        "f13": build_fact(p["p13"], (3, 2), case_factors=c),
        "f14": build_fact(p["p14"], (1, 2), case_factors=c),
        "f15": build_fact(p["p15"], (2, 0), case_factors=c),
        "f16": build_fact(p["p16"], 2, case_factors=c),
        "f17": build_fact(p["p17"], (2, 3), case_factors=c),
        "f18": build_fact(p["p18"], 2, case_factors=c),
        "f19": build_fact(p["p19"], 2, case_factors=c),
    }


@pytest.fixture(scope="class")
def make_factor(make_predicate, make_entity) -> Dict[str, Factor]:
    p = make_predicate
    e = make_entity

    c = (e["alice"], e["bob"], e["craig"], e["dan"], e["circus"])

    return {
        "f_irrelevant_0": build_fact(p["p_irrelevant_0"], (2,), case_factors=c),
        "f_irrelevant_1": build_fact(p["p_irrelevant_1"], (3,), case_factors=c),
        "f_irrelevant_2": build_fact(p["p_irrelevant_2"], (4,), case_factors=c),
        "f_irrelevant_3": build_fact(p["p_irrelevant_3"], (2, 4), case_factors=c),
        "f_irrelevant_3_new_context": build_fact(
            p["p_irrelevant_3"], (3, 4), case_factors=c
        ),
        "f_irrelevant_3_context_0": build_fact(
            p["p_irrelevant_3"], (3, 0), case_factors=c
        ),
        "f_crime": build_fact(p["p_crime"], case_factors=c),
        "f_watt_crime": build_fact(p["p_crime"], case_factors=make_entity["watt"]),
        "f_no_crime": build_fact(p["p_no_crime"], case_factors=c),
        "f_no_crime_entity_order": build_fact(p["p_no_crime"], (1,), case_factors=c),
        "f_murder": build_fact(p["p_murder"], case_factors=c),
        "f_no_murder": build_fact(p["p_murder_false"], case_factors=c),
        "f_murder_entity_swap": build_fact(p["p_murder"], (1, 0), case_factors=c),
        "f_murder_craig": build_fact(p["p_murder"], (2, 3), case_factors=c),
        "f_murder_whether": build_fact(p["p_murder_whether"], case_factors=c),
        "f_shooting": build_fact(p["p_shooting"], case_factors=c),
        "f_shooting_self": build_fact(p["p_shooting_self"], case_factors=c),
        "f_shooting_craig": build_fact(p["p_shooting"], (2, 3), case_factors=c),
        "f_shooting_craig_poe": build_fact(
            p["p_shooting"],
            (2, 3),
            case_factors=c,
            standard_of_proof="preponderance of evidence",
        ),
        "f_shooting_craig_brd": build_fact(
            p["p_shooting"],
            (2, 3),
            case_factors=c,
            standard_of_proof="beyond reasonable doubt",
        ),
        "f_shooting_entity_order": build_fact(p["p_shooting"], (1, 0), case_factors=c),
        "f_no_shooting": build_fact(p["p_no_shooting"], case_factors=c),
        "f_shooting_whether": build_fact(p["p_shooting_whether"], case_factors=c),
        "f_no_shooting_entity_order": build_fact(
            p["p_no_shooting"], (1, 0), case_factors=c
        ),
        "f_three_entities": build_fact(
            p["p_three_entities"], (0, 1, 2), case_factors=c
        ),
        "f_repeating_entity": build_fact(
            p["p_three_entities"], (0, 1, 0), case_factors=c
        ),
        "f_large_weight": build_fact(p["p_large_weight"], (0,), case_factors=c),
        "f_small_weight": build_fact(p["p_small_weight"], (0,), case_factors=c),
        "f_friends": build_fact(p["p_friends"], (0, 1), case_factors=c),
    }


@pytest.fixture(scope="class")
def make_exhibit(
    make_entity, make_predicate, make_factor, watt_factor, make_complex_fact
) -> Dict[str, Exhibit]:
    e = make_entity
    f = make_factor
    w = watt_factor
    c = make_complex_fact

    return {
        "shooting_affidavit": Exhibit(
            form="affidavit", statement=f["f_shooting"], stated_by=e["alice"]
        ),
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
        "no_shooting_different_witness_testimony": Exhibit(
            form="testimony", statement=f["f_no_shooting"], stated_by=e["bob"]
        ),
        "reciprocal_testimony": Exhibit(
            form="testimony", statement=w["f8"], stated_by=e["craig"]
        ),
        "reciprocal_declaration": Exhibit(
            form="declaration", statement=w["f8"], stated_by=e["craig"]
        ),
        "reciprocal_testimony_absent": Exhibit(
            form="testimony", statement=w["f8"], stated_by=e["craig"], absent=True
        ),
        "reciprocal_testimony_less": Exhibit(
            form="testimony", statement=w["f8_less"], stated_by=e["craig"]
        ),
        "reciprocal_testimony_specific": Exhibit(
            form="testimony", statement=w["f8_meters"], stated_by=e["craig"]
        ),
        "reciprocal_testimony_specific_absent": Exhibit(
            form="testimony",
            statement=w["f8_meters"],
            stated_by=e["craig"],
            absent=True,
        ),
        "relevant_murder_testimony": Exhibit(
            form="testimony", statement=c["f_relevant_murder"], stated_by=e["alice"]
        ),
        "relevant_murder_nested_swap_testimony": Exhibit(
            form="testimony",
            statement=c["f_relevant_murder_nested_swap"],
            stated_by=e["bob"],
        ),
        "relevant_murder_alice_craig_testimony": Exhibit(
            form="testimony",
            statement=c["f_relevant_murder_alice_craig"],
            stated_by=e["alice"],
        ),
        "large_weight_testimony": Exhibit(
            form="testimony", statement=f["f_large_weight"], stated_by=e["bob"]
        ),
        "small_weight_testimony": Exhibit(
            form="testimony", statement=f["f_small_weight"], stated_by=e["bob"]
        ),
        "generic_exhibit": Exhibit(generic=True),
        "specific_but_featureless": Exhibit(),
        "testimony_no_statement": Exhibit(form="testimony"),
    }


@pytest.fixture(scope="class")
def make_complex_fact(make_predicate, make_factor) -> Dict[str, Fact]:
    p = make_predicate
    f = make_factor

    return {
        "f_irrelevant_murder": Fact(
            p["p_irrelevant"], (f["f_shooting"], f["f_murder"])
        ),
        "f_relevant_murder": Fact(p["p_relevant"], (f["f_shooting"], f["f_murder"])),
        "f_relevant_murder_swap_entities": Fact(
            p["p_relevant"], (f["f_shooting"], f["f_murder"])
        ),
        "f_relevant_murder_nested_swap": Fact(
            p["p_relevant"], (f["f_shooting_entity_order"], f["f_murder_entity_swap"])
        ),
        "f_relevant_murder_whether": Fact(
            p["p_relevant"], (f["f_shooting"], f["f_murder_whether"])
        ),
        "f_whether_relevant_murder_whether": Fact(
            p["p_relevant"], (f["f_shooting_whether"], f["f_murder_whether"])
        ),
        "f_relevant_murder_swap": Fact(
            p["p_relevant"], (f["f_shooting"], f["f_murder_entity_swap"])
        ),
        "f_relevant_murder_craig": Fact(
            p["p_relevant"], (f["f_shooting_craig"], f["f_murder_craig"])
        ),
        "f_relevant_murder_alice_craig": Fact(
            p["p_relevant"], (f["f_shooting"], f["f_murder_craig"])
        ),
    }


@pytest.fixture(scope="class")
def make_fact_about_exhibit(make_predicate, make_exhibit) -> Dict[str, Evidence]:
    p = make_predicate
    e = make_exhibit
    return {
        "f_reliable_large_weight": Fact(
            p["p_reliable"], (e["large_weight_testimony"],)
        ),
        "f_reliable_small_weight": Fact(
            p["p_reliable"], (e["small_weight_testimony"],)
        ),
    }


@pytest.fixture(scope="class")
def make_complex_rule(
    make_factor, make_exhibit, make_complex_fact, make_fact_about_exhibit
) -> Dict[str, Rule]:
    return {
        "accept_relevance_testimony": Rule(Procedure(
            inputs=make_exhibit["relevant_murder_testimony"],
            outputs=make_complex_fact["f_relevant_murder"],)
        ),
        "accept_relevance_testimony_ALL": Rule(Procedure(
            inputs=make_exhibit["relevant_murder_testimony"],
            outputs=make_complex_fact["f_relevant_murder"]),
            universal=True,
        ),
        "accept_murder_fact_from_relevance": Rule(Procedure(
            inputs=make_complex_fact["f_relevant_murder"],
            outputs=make_factor["f_murder"],)
        ),
        "accept_murder_fact_from_relevance_and_shooting": Rule(Procedure(
            inputs=[make_complex_fact["f_relevant_murder"], make_factor["f_shooting"]],
            outputs=make_factor["f_murder"],)
        ),
        "accept_murder_fact_from_relevance_and_shooting_craig": Rule(Procedure(
            inputs=[make_complex_fact["f_relevant_murder_craig"], make_factor["f_shooting_craig"]],
            outputs=make_factor["f_murder_craig"],)
        ),
        "accept_small_weight_reliable": Rule(Procedure(
            inputs=[make_factor["f_small_weight"], make_factor["f_friends"]],
            outputs=make_fact_about_exhibit["f_reliable_small_weight"]),
            universal=True,
        ),
        "accept_small_weight_reliable_more_evidence": Rule(Procedure(
            inputs=[make_factor["f_large_weight"], make_factor["f_friends"]],
            outputs=make_fact_about_exhibit["f_reliable_small_weight"]),
            universal=True,
        ),
        "accept_large_weight_reliable": Rule(Procedure(
            inputs=[make_factor["f_small_weight"], make_factor["f_friends"]],
            outputs=make_fact_about_exhibit["f_reliable_large_weight"]),
            universal=True,
        ),
    }


@pytest.fixture(scope="class")
def make_evidence(
    make_predicate, make_factor, watt_factor, make_exhibit
) -> Dict[str, Evidence]:
    p = make_predicate
    f = make_factor
    w = watt_factor
    x = make_exhibit
    return {
        "shooting": Evidence(x["shooting_testimony"], to_effect=f["f_crime"]),
        "shooting_no_effect": Evidence(x["shooting_testimony"]),
        "no_shooting": Evidence(x["no_shooting_testimony"], to_effect=f["f_no_crime"]),
        "no_shooting_absent": Evidence(
            x["no_shooting_testimony"], to_effect=f["f_no_crime"], absent=True
        ),
        "no_shooting_entity_order": Evidence(
            x["no_shooting_entity_order_testimony"],
            to_effect=f["f_no_crime_entity_order"],
        ),
        "no_shooting_witness_unknown": Evidence(
            x["no_shooting_witness_unknown_testimony"], to_effect=f["f_no_crime"]
        ),
        "no_shooting_witness_unknown_absent": Evidence(
            x["no_shooting_witness_unknown_testimony"],
            to_effect=f["f_no_crime"],
            absent=True,
        ),
        # Here the Exhibit is absent, not the Evidence. Pointless distinction?
        "no_shooting_witness_unknown_absent_exhibit": Evidence(
            x["no_shooting_witness_unknown_absent_testimony"], to_effect=f["f_no_crime"]
        ),
        "no_shooting_no_effect_entity_order": Evidence(
            x["no_shooting_entity_order_testimony"]
        ),
        "no_shooting_different_witness": Evidence(
            x["no_shooting_different_witness_testimony"], to_effect=f["f_no_crime"]
        ),
        "reciprocal": Evidence(x["reciprocal_testimony"], to_effect=f["f_no_crime"]),
        "crime": Evidence(
            x["generic_exhibit"], to_effect=f["f_watt_crime"], generic=True
        ),
        "crime_absent": Evidence(
            x["generic_exhibit"], to_effect=f["f_watt_crime"], absent=True, generic=True
        ),
        "generic": Evidence(x["generic_exhibit"], generic=True),
        "generic_absent": Evidence(x["generic_exhibit"], absent=True, generic=True),
    }

@pytest.fixture(scope="class")
def make_pleading(make_entity) -> Dict[str, Dict[str, Pleading]]:
    return {
        "craig": Pleading(filer=make_entity["craig"])
    }

@pytest.fixture(scope="class")
def make_allegation(make_pleading, make_factor) -> Dict[str, Dict[str, Allegation]]:
    return {
        "shooting": Allegation(statement=make_factor["f_shooting"], pleading=make_pleading["craig"])
    }

@pytest.fixture(scope="module")
def make_selector() -> Dict[str, TextQuoteSelector]:
    return {
        "bad_selector": TextQuoteSelector(exact="text that doesn't exist in the code"),
        "preexisting material": TextQuoteSelector(
            exact=(
                "protection for a work employing preexisting material in which "
                + "copyright subsists does not extend to any part of the work in "
                + "which such material has been used unlawfully."
            )
        ),
        "copyright": TextQuoteSelector(suffix="idea, procedure,"),
        "copyright_requires_originality": TextQuoteSelector(
            suffix="fixed in any tangible"
        ),
    }

@pytest.fixture(scope="module")
def make_regime() -> Dict[str, Code]:
    usa = Regime()
    for filename in (
        "constitution.xml",
        "usc17.xml",
        "cfr37.xml",
        "ca_evidence.html",
        "ca_penal.html",
    ):
        xml = loaders.load_code(filename=filename)
        usa.set_code(readers.read_code(xml))
    return usa

@pytest.fixture(scope="module")
def make_code(make_regime) -> Dict[str, Code]:
    return {
        "const": make_regime.get_code("/us/const"),
        "usc17": make_regime.get_code("/us/usc/t17"),
        "cfr37": make_regime.get_code("/us/cfr/t37"),
        "ca_evid": make_regime.get_code("/us-ca/evid"),
        "ca_pen": make_regime.get_code("/us-ca/pen"),
    }


@pytest.fixture(scope="module")
def make_enactment(make_code, make_selector, make_regime) -> Dict[str, Enactment]:
    return {
        "copyright": readers.read_enactment(
            {"selector": make_selector["copyright"],
            "source": "/us/usc/t17/s102/b"},
            code=make_code["usc17"],
            regime=make_regime,
        ),
        "copyright_requires_originality": readers.read_enactment(
            {"selector": make_selector["copyright_requires_originality"],
            "source": "/us/usc/t17/s102/a"},
            regime=make_regime,
        ),
        "securing_for_authors": Enactment(
            selector=TextQuoteSelector(
                exact=("To promote the Progress of Science and "
                + "useful Arts, by securing for limited Times to Authors")),
            source="/us/const/article-I/8/8",
            code=make_code["const"],
        ),
        "and_inventors": Enactment(
            selector=TextQuoteSelector(
                exact="and Inventors"
            ),
            source="/us/const/article-I/8/8",
            code=make_code["const"],
        ),
        "right_to_writings": Enactment(
            selector=TextQuoteSelector(
                exact="the exclusive Right to their respective Writings",
            ),
            source="/us/const/article-I/8/8",
            code=make_code["const"],
        ),
        "commerce_vague_path": Enactment(
            selector=TextQuoteSelector(
                exact="No Preference shall be given by any Regulation of Commerce",
            ),
            code=make_code["const"],
            source="/us/const/article-I",
        ),
        "search_clause": readers.read_enactment(
            {"exact": (
                    "The right of the people to be secure in their persons, "
                    + "houses, papers, and effects, against unreasonable searches "
                    + "and seizures, shall not be violated"
                ),
            "source": "/us/const/amendment-IV"},
            regime=make_regime,
        ),
        "warrants_clause": readers.read_enactment(
            {"exact": "shall not be violated, and no Warrants shall issue,",
            "source": "/us/const/amendment-IV"},
            regime=make_regime,
        ),
        "fourth_a": readers.read_enactment(  # whole section, no selector
            {"source": "/us/const/amendment-IV"},
            regime=make_regime,
        ),
        "due_process_5": readers.read_enactment(
            {"exact": "life, liberty, or property, without due process of law",
            "source": "/us/const/amendment-V"},
            regime=make_regime,
        ),
        "due_process_14": readers.read_enactment(
            {"exact": "life, liberty, or property, without due process of law",
            "source": "/us/const/amendment-XIV-1"},
            regime=make_regime,
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
            outputs=(f["f3_entity_order"],),
            inputs=(f["f2_entity_order"], f["f1_entity_order"]),
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
            inputs=(f["f4"], f["f5"], f["f6"], f["f7"], f["f8_meters"], f["f9"]),
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
                f["f10"],
                m["f_irrelevant_0"],
                m["f_irrelevant_1"],
                m["f_irrelevant_2"],
                m["f_irrelevant_3"],
                m["f_irrelevant_3_context_0"],
            ),
            inputs=(f["f4"], f["f5"], f["f6"], f["f7"], f["f9"]),
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
        "c_output_distance_less": Procedure(outputs=(f["f9"]), inputs=(f["f1"])),
        "c_output_distance_more": Procedure(
            outputs=(f["f9_more_swap_entities"]), inputs=(f["f1"])
        ),
    }


@pytest.fixture(scope="class")
def real_holding(make_procedure, make_enactment) -> Dict[str, Rule]:
    """These holdings can be changed in case they don't accurately reflect
    what's in real cases, or in case there are API improvements that
    allow them to become more accurate. I'll try not to write any tests
    that depend on them remaining the same."""

    c = make_procedure
    e = make_enactment

    return {
        "h1": Holding(
            rule=Rule(c["c1"], enactments=e["search_clause"], mandatory=True)
        ),
        "h2": Holding(
            rule=Rule(c["c2"], enactments=e["search_clause"], mandatory=True)
        ),
        "h3": Holding(
            rule=Rule(c["c3"], enactments=e["search_clause"], mandatory=True)
        ),
        "h4": Holding(
            rule=Rule(c["c4"], enactments=e["search_clause"], mandatory=True)
        ),
    }


@pytest.fixture(scope="class")
def make_rule(make_procedure, make_enactment) -> Dict[str, Rule]:
    c = make_procedure
    e = make_enactment

    return {
        "h1": Rule(c["c1"], enactments=e["search_clause"]),
        "h2": Rule(c["c2"], enactments=e["search_clause"]),
        "h3": Rule(c["c3"], enactments=e["search_clause"]),
        "h1_again": Rule(c["c1"], enactments=e["search_clause"]),
        "h1_entity_order": Rule(c["c1_entity_order"], enactments=e["search_clause"]),
        "h1_easy": Rule(c["c1_easy"], enactments=e["search_clause"]),
        "h2_without_cite": Rule(c["c2"]),
        "h2_fourth_a_cite": Rule(c["c2"], enactments=e["fourth_a"]),
        "h2_despite_due_process": Rule(
            c["c2"],
            enactments=e["search_clause"],
            enactments_despite=e["due_process_5"],
        ),
        "h2_ALL_due_process": Rule(
            c["c2"],
            enactments=(e["search_clause"], e["due_process_5"]),
            mandatory=False,
            universal=True,
        ),
        "h2_ALL": Rule(
            c["c2"], enactments=e["search_clause"], mandatory=False, universal=True
        ),
        "h2_ALL_MAY_output_false": Rule(
            c["c2_output_false"],
            enactments=e["search_clause"],
            mandatory=False,
            universal=True,
        ),
        "h2_ALL_MUST": Rule(
            c["c2"], enactments=e["search_clause"], mandatory=True, universal=True
        ),
        "h2_ALL_MUST_output_false": Rule(
            c["c2_output_false"],
            enactments=e["search_clause"],
            mandatory=True,
            universal=True,
        ),
        "h2_exact_quantity": Rule(
            c["c2_exact_quantity"], enactments=e["search_clause"]
        ),
        "h2_irrelevant_inputs": Rule(
            c["c2_irrelevant_inputs"], enactments=e["search_clause"]
        ),
        "h2_irrelevant_inputs_ALL": Rule(
            c["c2_irrelevant_inputs"], enactments=e["search_clause"], universal=True
        ),
        "h2_irrelevant_inputs_MUST": Rule(
            c["c2_irrelevant_inputs"], enactments=e["search_clause"], mandatory=True
        ),
        "h2_irrelevant_inputs_ALL_MUST": Rule(
            c["c2_irrelevant_inputs"],
            enactments=e["search_clause"],
            mandatory=True,
            universal=True,
        ),
        "h2_reciprocal_swap": Rule(
            c["c2_reciprocal_swap"], enactments=e["search_clause"]
        ),
        "h2_exact_in_despite": Rule(
            c["c2_exact_in_despite"], enactments=e["search_clause"]
        ),
        "h2_exact_in_despite_ALL": Rule(
            c["c2_exact_in_despite"],
            enactments=e["search_clause"],
            mandatory=False,
            universal=True,
        ),
        "h2_exact_in_despite_ALL_entity_order": Rule(
            c["c2_exact_in_despite_entity_order"],
            enactments=e["search_clause"],
            mandatory=False,
            universal=True,
        ),
        "h2_exact_quantity_ALL": Rule(
            c["c2_exact_quantity"],
            enactments=e["search_clause"],
            mandatory=False,
            universal=True,
        ),
        "h2_MUST": Rule(
            c["c2"], enactments=e["search_clause"], mandatory=True, universal=False
        ),
        "h2_output_absent": Rule(c["c2_output_absent"], enactments=e["search_clause"]),
        "h2_output_false": Rule(c["c2_output_false"], enactments=e["search_clause"]),
        "h2_output_false_ALL": Rule(
            c["c2_output_false"], enactments=e["search_clause"], universal=True
        ),
        "h2_output_false_ALL_MUST": Rule(
            c["c2_output_false"],
            enactments=e["search_clause"],
            mandatory=True,
            universal=True,
        ),
        "h2_output_absent_false": Rule(
            c["c2_output_absent_false"], enactments=e["search_clause"]
        ),
        "h2_SOME_MUST_output_false": Rule(
            c["c2_output_false"],
            enactments=e["search_clause"],
            mandatory=True,
            universal=False,
        ),
        "h2_SOME_MUST_output_absent": Rule(
            c["c2_output_absent"],
            enactments=e["search_clause"],
            mandatory=True,
            universal=False,
        ),
        "h3_ALL": Rule(c["c3"], enactments=e["search_clause"], universal=True),
        "h3_fewer_inputs": Rule(c["c3_fewer_inputs"], enactments=e["search_clause"]),
        "h3_fewer_inputs_ALL": Rule(
            c["c3_fewer_inputs"], enactments=e["search_clause"], universal=True
        ),
        "h_near_means_curtilage": Rule(
            c["c_near_means_curtilage"], enactments=e["search_clause"]
        ),
        "h_near_means_curtilage_even_if": Rule(
            c["c_near_means_curtilage_even_if"], enactments=e["search_clause"]
        ),
        "h_near_means_curtilage_ALL": Rule(
            c["c_near_means_curtilage"], enactments=e["search_clause"], universal=True
        ),
        "h_near_means_curtilage_ALL_MUST": Rule(
            c["c_near_means_curtilage"],
            enactments=e["search_clause"],
            mandatory=True,
            universal=True,
        ),
        "h_near_means_no_curtilage": Rule(
            c["c_near_means_no_curtilage"], enactments=e["search_clause"]
        ),
        "h_near_means_no_curtilage_ALL": Rule(
            c["c_near_means_no_curtilage"],
            enactments=e["search_clause"],
            universal=True,
        ),
        "h_near_means_no_curtilage_ALL_MUST": Rule(
            c["c_near_means_no_curtilage"],
            enactments=e["search_clause"],
            mandatory=True,
            universal=True,
        ),
        "h_nearer_means_curtilage": Rule(
            c["c_nearer_means_curtilage"], enactments=e["search_clause"]
        ),
        "h_nearer_means_curtilage_ALL": Rule(
            c["c_nearer_means_curtilage"], enactments=e["search_clause"], universal=True
        ),
        "h_nearer_means_curtilage_MUST": Rule(
            c["c_nearer_means_curtilage"], enactments=e["search_clause"], mandatory=True
        ),
        "h_far_means_no_curtilage": Rule(c["c_far_means_no_curtilage"]),
        "h_far_means_no_curtilage_ALL": Rule(
            c["c_far_means_no_curtilage"], enactments=e["search_clause"], universal=True
        ),
        "h_output_distance_less": Rule(
            c["c_output_distance_less"], universal=True, mandatory=True
        ),
        "h_output_distance_more": Rule(c["c_output_distance_more"]),
    }


@pytest.fixture(scope="class")
def make_holding(make_rule) -> Dict[str, Holding]:
    holdings: Dict[str, Holding] = {}
    for name, rule in make_rule.items():
        holdings[name] = Holding(rule=rule)

    new_holdings = {
        "h1_opposite": Holding(rule=make_rule["h1"], rule_valid=False),
        "h2_undecided": Holding(rule=make_rule["h2"], decided=False),
        "h2_invalid_undecided": Holding(
            rule=make_rule["h2"], rule_valid=False, decided=False
        ),
        "h2_MUST_undecided": Holding(rule=make_rule["h2_MUST"], decided=False),
        "h2_MUST_invalid": Holding(rule=make_rule["h2_MUST"], rule_valid=False),
        "h2_invalid": Holding(rule=make_rule["h2"], rule_valid=False),
        "h2_ALL_invalid": Holding(rule=make_rule["h2_ALL"], rule_valid=False),
        "h2_irrelevant_inputs_undecided": Holding(
            rule=make_rule["h2_irrelevant_inputs"], decided=False
        ),
        "h2_irrelevant_inputs_invalid": Holding(
            rule=make_rule["h2_irrelevant_inputs"], rule_valid=False
        ),
        "h2_irrelevant_inputs_ALL_invalid": Holding(
            rule=make_rule["h2_irrelevant_inputs_ALL"], rule_valid=False
        ),
        "h2_irrelevant_inputs_ALL_MUST_invalid": Holding(
            rule=make_rule["h2_irrelevant_inputs_ALL_MUST"], rule_valid=False
        ),
        "h2_irrelevant_inputs_MUST_invalid": Holding(
            rule=make_rule["h2_irrelevant_inputs_MUST"], rule_valid=False
        ),
        "h2_ALL_due_process_invalid": Holding(
            rule=make_rule["h2_ALL_due_process"], rule_valid=False
        ),
        "h3_undecided": Holding(rule=make_rule["h3"], decided=False),
        "h3_ALL_undecided": Holding(rule=make_rule["h3_ALL"], decided=False),
        "h3_fewer_inputs_undecided": Holding(
            rule=make_rule["h3_fewer_inputs"], decided=False
        ),
        "h3_fewer_inputs_ALL_undecided": Holding(
            rule=make_rule["h3_fewer_inputs_ALL"], decided=False
        ),
        "h_near_means_curtilage_ALL_undecided": Holding(
            rule=make_rule["h_near_means_curtilage_ALL"], decided=False
        ),
    }

    holdings.update(new_holdings)
    return holdings


TEST_CASES = ("brad", "cardenas", "feist", "lotus", "oracle", "watt")

def load_decisions_for_fixtures():
    decisions = {}
    for case in TEST_CASES:
        decision = loaders.load_decision(f"{case}_h.json")
        built = readers.read_decision(decision)
        decisions[case] = built
    return decisions

@pytest.fixture(scope="class")
def make_decision():
    return load_decisions_for_fixtures()

@pytest.fixture(scope="class")
def make_decision_with_holding(make_decision, make_regime):
    decisions = load_decisions_for_fixtures()
    for case in TEST_CASES:
        holdings, holding_anchors, named_anchors = loaders.load_holdings_with_anchors(f"holding_{case}.json", regime=make_regime)
        decisions[case].majority.posit(holdings, holding_anchors=holding_anchors, named_anchors=named_anchors)
    return decisions

@pytest.fixture(scope="class")
def make_opinion(make_decision) -> Dict[str, Opinion]:
    opinions = {}
    for case in TEST_CASES:
        for opinion in make_decision[case].opinions:
            opinions[f"{case}_{opinion.position}"] = opinion
    return opinions

@pytest.fixture(scope="class")
def make_opinion_with_holding(make_decision_with_holding) -> Dict[str, Opinion]:
    opinions = {}
    for case in TEST_CASES:
        for opinion in make_decision_with_holding[case].opinions:
            opinions[f"{case}_{opinion.position}"] = opinion
    return opinions

@pytest.fixture(scope="class")
def make_analysis() -> Dict[str, Dict[str, Any]]:
    """Example user analysis data."""
    analysis = {}
    analysis["minimal"] = [
            {
                "outputs": {
                    "type": "fact",
                    "content": "{Bradley} made a minimal holding object",
                    "anchors": "upholding searches in |open fields or grounds|around a house",
                },
                "anchors": "Thus,|we hold|that this rule is correct."
            }

        ]
    analysis["no anchors"] = [
            {
                "outputs": {
                    "type": "fact",
                    "content": "this holding has no text anchors",
                }
            }
        ]
    return analysis
