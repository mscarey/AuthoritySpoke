import copy
from decimal import Decimal
from typing import Literal, TypedDict

from anchorpoint.textselectors import TextQuoteSelector
from authorityspoke import Entity, Fact, Holding, Predicate, Rule
from authorityspoke.examples.legislation import SEARCH_CLAUSE
from authorityspoke.facts import AbsenceOfFactor, Evidence, Exhibit
from authorityspoke.holdings import HoldingGroup
from authorityspoke.opinions import (
    AnchoredHoldings,
    HoldingWithAnchors,
    TextPositionSet,
)
from authorityspoke.procedures import Procedure
from legislice.enactments import EnactmentPassage
from legislice.enactments import TextPositionSet as EnactmentTextPositionSet
from authorityspoke.groups import EnactmentGroup


class FactSpec(TypedDict):
    name: str
    predicate: dict
    terms: list[str]


FactorRef = tuple[Literal["fact", "absence"], str]


class HoldingSpec(TypedDict):
    inputs: list[FactorRef]
    despite: list[FactorRef]
    outputs: list[FactorRef]


ENTITIES: dict[str, Entity] = {
    "hideaway_lodge": Entity(name="Hideaway Lodge", generic=True, plural=False),
    "wattenburg": Entity(name="Wattenburg", generic=True, plural=False),
    "the_stockpile_of_trees": Entity(
        name="the stockpile of trees", generic=True, plural=False
    ),
    "officers_search_of_the_stockpile": Entity(
        name="officers' search of the stockpile", generic=True, plural=False
    ),
    "prosecutor": Entity(name="prosecutor", generic=True, plural=False),
}

EXHIBITS: dict[str, Exhibit] = {
    "proof_of_wattenburg_s_guilt": Exhibit(
        name="proof of Wattenburg's guilt",
        offered_by=ENTITIES["prosecutor"],
        generic=True,
    )
}

TERMS_BY_KEY: dict[str, Entity | Exhibit] = {
    **ENTITIES,
    **EXHIBITS,
}

FACT_SPECS: list[FactSpec] = [
    {
        "name": "Hideaway Lodge was a motel",
        "predicate": {"content": "{hideaway_lodge} was a motel", "truth": True},
        "terms": ["hideaway_lodge"],
    },
    {
        "name": "Wattenburg lived at Hideaway Lodge",
        "predicate": {
            "content": "{wattenburg} lived at {hideaway_lodge}",
            "truth": True,
        },
        "terms": ["wattenburg", "hideaway_lodge"],
    },
    {
        "name": "Wattenburg operated Hideaway Lodge as a business",
        "predicate": {
            "content": "{wattenburg} operated {hideaway_lodge} as a business",
            "truth": True,
        },
        "terms": ["wattenburg", "hideaway_lodge"],
    },
    {
        "name": "Hideaway Lodge was Wattenburg’s abode",
        "predicate": {
            "content": "{hideaway_lodge} was {wattenburg}’s abode",
            "truth": True,
        },
        "terms": ["hideaway_lodge", "wattenburg"],
    },
    {
        "name": "the stockpile of trees was on the premises of Hideaway Lodge",
        "predicate": {
            "content": "{the_stockpile_of_trees} was on the premises of {hideaway_lodge}",
            "truth": True,
        },
        "terms": ["the_stockpile_of_trees", "hideaway_lodge"],
    },
    {
        "name": "the stockpile of trees was a stockpile of Christmas trees",
        "predicate": {
            "content": "{the_stockpile_of_trees} was a stockpile of Christmas trees",
            "truth": True,
        },
        "terms": ["the_stockpile_of_trees"],
    },
    {
        "name": "the stockpile of trees was among some standing trees",
        "predicate": {
            "content": "{the_stockpile_of_trees} was among some standing trees",
            "truth": True,
        },
        "terms": ["the_stockpile_of_trees"],
    },
    {
        "name": "long distance",
        "predicate": {
            "content": "the distance between {place1} and {place2} was",
            "truth": True,
            "quantity_range": {
                "sign": "<=",
                "include_negatives": None,
                "quantity_magnitude": Decimal("35"),
                "quantity_units": "foot",
            },
        },
        "terms": ["the_stockpile_of_trees", "hideaway_lodge"],
    },
    {
        "name": "the distance between the stockpile of trees and a parking area used by personnel and patrons of Hideaway Lodge was <= 5 feet",
        "predicate": {
            "content": "the distance between {the_stockpile_of_trees} and a parking area used by personnel and patrons of {hideaway_lodge} was",
            "truth": True,
            "quantity_range": {
                "sign": "<=",
                "include_negatives": None,
                "quantity_magnitude": Decimal("5"),
                "quantity_units": "foot",
            },
        },
        "terms": ["the_stockpile_of_trees", "hideaway_lodge"],
    },
    {
        "name": "the distance between the stockpile of trees and Hideaway Lodge was >= 20 feet",
        "predicate": {
            "content": "the distance between {place1} and {place2} was",
            "truth": True,
            "quantity_range": {
                "sign": ">=",
                "include_negatives": None,
                "quantity_magnitude": Decimal("20"),
                "quantity_units": "foot",
            },
        },
        "terms": ["the_stockpile_of_trees", "hideaway_lodge"],
    },
    {
        "name": "the stockpile of trees was within the curtilage of Hideaway Lodge",
        "predicate": {
            "content": "{the_stockpile_of_trees} was within the curtilage of {hideaway_lodge}",
            "truth": True,
        },
        "terms": ["the_stockpile_of_trees", "hideaway_lodge"],
    },
    {
        "name": "officers' search of the stockpile was a warrantless search and seizure",
        "predicate": {
            "content": "{officers_search_of_the_stockpile} was a warrantless search and seizure",
            "truth": True,
        },
        "terms": ["officers_search_of_the_stockpile"],
    },
    {
        "name": "officers' search of the stockpile was performed by law enforcement officers",
        "predicate": {
            "content": "{officers_search_of_the_stockpile} was performed by law enforcement officers",
            "truth": True,
        },
        "terms": ["officers_search_of_the_stockpile"],
    },
    {
        "name": "officers' search of the stockpile was performed by federal officers",
        "predicate": {
            "content": "{officers_search_of_the_stockpile} was performed by federal officers",
            "truth": True,
        },
        "terms": ["officers_search_of_the_stockpile"],
    },
    {
        "name": "in officers' search of the stockpile, several law enforcement officials meticulously went through the stockpile of trees",
        "predicate": {
            "content": "in {officers_search_of_the_stockpile}, several law enforcement officials meticulously went through {the_stockpile_of_trees}",
            "truth": True,
        },
        "terms": ["officers_search_of_the_stockpile", "the_stockpile_of_trees"],
    },
    {
        "name": "the time duration of officers' search of the stockpile was >= 385 minutes",
        "predicate": {
            "content": "the time duration of {officers_search_of_the_stockpile} was",
            "truth": True,
            "quantity_range": {
                "sign": ">=",
                "include_negatives": None,
                "quantity_magnitude": Decimal("385"),
                "quantity_units": "minute",
            },
        },
        "terms": ["officers_search_of_the_stockpile"],
    },
    {
        "name": "officers' search of the stockpile constituted an intrusion upon the stockpile of trees",
        "predicate": {
            "content": "{officers_search_of_the_stockpile} constituted an intrusion upon {the_stockpile_of_trees}",
            "truth": True,
        },
        "terms": ["officers_search_of_the_stockpile", "the_stockpile_of_trees"],
    },
    {
        "name": "Hideaway Lodge was Wattenburg's abode",
        "predicate": {
            "content": "{hideaway_lodge} was {wattenburg}'s abode",
            "truth": True,
        },
        "terms": ["hideaway_lodge", "wattenburg"],
    },
    {
        "name": "Wattenburg sought to preserve the stockpile of trees as private",
        "predicate": {
            "content": "{wattenburg} sought to preserve {the_stockpile_of_trees} as private",
            "truth": True,
        },
        "terms": ["wattenburg", "the_stockpile_of_trees"],
    },
    {
        "name": "the stockpile of trees was in an area accessible to the public",
        "predicate": {
            "content": "{the_stockpile_of_trees} was in an area accessible to the public",
            "truth": True,
        },
        "terms": ["the_stockpile_of_trees"],
    },
    {
        "name": "the distance between the the stockpile of trees and Hideaway Lodge was >= 20 feet",
        "predicate": {
            "content": "the distance between the {place1} and {place2} was",
            "truth": True,
            "quantity_range": {
                "sign": ">=",
                "include_negatives": None,
                "quantity_magnitude": Decimal("20"),
                "quantity_units": "foot",
            },
        },
        "terms": ["the_stockpile_of_trees", "hideaway_lodge"],
    },
    {
        "name": "proof of Wattenburg's guilt was derived from officers' search of the stockpile",
        "predicate": {
            "content": "{proof_of_wattenburg_s_guilt} was derived from {officers_search_of_the_stockpile}",
            "truth": True,
        },
        "terms": ["proof_of_wattenburg_s_guilt", "officers_search_of_the_stockpile"],
    },
]


def _build_facts() -> list[Fact]:
    facts = []
    for spec in FACT_SPECS:
        facts.append(
            Fact.model_validate(
                {
                    "predicate": spec["predicate"],
                    "terms": [
                        TERMS_BY_KEY[name].model_dump() for name in spec["terms"]
                    ],
                    "name": spec["name"],
                    "generic": False,
                }
            )
        )
    return facts


FACTS: list[Fact] = _build_facts()
FACTS_BY_NAME = {fact.name: fact for fact in FACTS}

WATTENBURG_COMMITTED_A_CRIME = Fact(
    predicate=Predicate(content="{wattenburg} committed a crime", truth=True),
    terms=[ENTITIES["wattenburg"]],
    name="Wattenburg committed a crime",
    generic=False,
)

EVIDENCE_OF_GUILT = Evidence(
    exhibit=EXHIBITS["proof_of_wattenburg_s_guilt"],
    to_effect=WATTENBURG_COMMITTED_A_CRIME,
    name="evidence of proof of Wattenburg's guilt to the effect that Wattenburg committed a crime",
    generic=False,
)

ABSENCES: dict[str, AbsenceOfFactor] = {
    "no_evidence_of_guilt": AbsenceOfFactor(absent=EVIDENCE_OF_GUILT, generic=False),
}

FOURTH_AMENDMENT_SEARCH_PROTECTION = EnactmentPassage(
    enactment=copy.deepcopy(SEARCH_CLAUSE.enactment),
    selection=EnactmentTextPositionSet(
        positions=[],
        quotes=[
            TextQuoteSelector(
                exact="The right of the people to be secure in their persons, houses, papers, and effects, against unreasonable searches and seizures, shall not be violated",
                prefix="",
                suffix="",
            )
        ],
    ),
)

HOLDING_SPECS: list[HoldingSpec] = [
    {
        "inputs": [
            ("fact", "Hideaway Lodge was a motel"),
            ("fact", "Wattenburg lived at Hideaway Lodge"),
            ("fact", "Wattenburg operated Hideaway Lodge as a business"),
        ],
        "despite": [],
        "outputs": [("fact", "Hideaway Lodge was Wattenburg’s abode")],
    },
    {
        "inputs": [
            ("fact", "the stockpile of trees was on the premises of Hideaway Lodge"),
            ("fact", "the stockpile of trees was a stockpile of Christmas trees"),
            ("fact", "the stockpile of trees was among some standing trees"),
            ("fact", "long distance"),
            (
                "fact",
                "the distance between the stockpile of trees and a parking area used by personnel and patrons of Hideaway Lodge was <= 5 feet",
            ),
        ],
        "despite": [
            (
                "fact",
                "the distance between the stockpile of trees and Hideaway Lodge was >= 20 feet",
            )
        ],
        "outputs": [
            (
                "fact",
                "the stockpile of trees was within the curtilage of Hideaway Lodge",
            )
        ],
    },
    {
        "inputs": [
            ("fact", "Hideaway Lodge was a motel"),
            ("fact", "the stockpile of trees was on the premises of Hideaway Lodge"),
            ("fact", "the stockpile of trees was a stockpile of Christmas trees"),
            (
                "fact",
                "officers' search of the stockpile was a warrantless search and seizure",
            ),
            (
                "fact",
                "officers' search of the stockpile was performed by law enforcement officers",
            ),
            (
                "fact",
                "officers' search of the stockpile was performed by federal officers",
            ),
            (
                "fact",
                "in officers' search of the stockpile, several law enforcement officials meticulously went through the stockpile of trees",
            ),
            (
                "fact",
                "the time duration of officers' search of the stockpile was >= 385 minutes",
            ),
        ],
        "despite": [],
        "outputs": [
            (
                "fact",
                "officers' search of the stockpile constituted an intrusion upon the stockpile of trees",
            )
        ],
    },
    {
        "inputs": [
            ("fact", "Hideaway Lodge was Wattenburg's abode"),
            ("fact", "the stockpile of trees was on the premises of Hideaway Lodge"),
            ("fact", "the stockpile of trees was a stockpile of Christmas trees"),
            ("fact", "the stockpile of trees was among some standing trees"),
            ("fact", "long distance"),
            (
                "fact",
                "the distance between the stockpile of trees and a parking area used by personnel and patrons of Hideaway Lodge was <= 5 feet",
            ),
        ],
        "despite": [],
        "outputs": [
            ("fact", "Wattenburg sought to preserve the stockpile of trees as private")
        ],
    },
    {
        "inputs": [
            ("fact", "Hideaway Lodge was Wattenburg’s abode"),
            (
                "fact",
                "officers' search of the stockpile was a warrantless search and seizure",
            ),
            (
                "fact",
                "officers' search of the stockpile was performed by law enforcement officers",
            ),
            (
                "fact",
                "officers' search of the stockpile was performed by federal officers",
            ),
            (
                "fact",
                "officers' search of the stockpile constituted an intrusion upon the stockpile of trees",
            ),
            ("fact", "the stockpile of trees was on the premises of Hideaway Lodge"),
            ("fact", "Wattenburg sought to preserve the stockpile of trees as private"),
            ("fact", "long distance"),
            (
                "fact",
                "proof of Wattenburg's guilt was derived from officers' search of the stockpile",
            ),
        ],
        "despite": [
            ("fact", "the stockpile of trees was in an area accessible to the public"),
            (
                "fact",
                "the distance between the the stockpile of trees and Hideaway Lodge was >= 20 feet",
            ),
        ],
        "outputs": [("absence", "no_evidence_of_guilt")],
    },
]


def _resolve_factor(ref: FactorRef):
    kind, name = ref
    if kind == "fact":
        return FACTS_BY_NAME[name]
    if kind == "absence":
        return ABSENCES[name]
    raise ValueError(f"unknown factor kind: {kind}")


def _build_holdings() -> list[Holding]:
    holdings: list[Holding] = []
    for spec in HOLDING_SPECS:
        holdings.append(
            Holding(
                generic=False,
                rule=Rule(
                    generic=False,
                    procedure=Procedure(
                        inputs=[_resolve_factor(ref) for ref in spec["inputs"]],
                        despite=[_resolve_factor(ref) for ref in spec["despite"]],
                        outputs=[_resolve_factor(ref) for ref in spec["outputs"]],
                    ),
                    enactments=EnactmentGroup(
                        passages=[copy.deepcopy(FOURTH_AMENDMENT_SEARCH_PROTECTION)]
                    ),
                    mandatory=True,
                    universal=False,
                ),
                rule_valid=True,
                decided=True,
                exclusive=False,
            )
        )
    return holdings


HOLDINGS = HoldingGroup(_build_holdings())

ANCHORS: list[TextPositionSet] = [
    TextPositionSet(positions=[], quotes=[]) for _ in HOLDINGS
]

NAMED_ANCHORS = []
ENACTMENT_ANCHORS = []


def anchored_holdings() -> AnchoredHoldings:
    """Build AnchoredHoldings from this module's HOLDINGS collection."""
    return AnchoredHoldings(
        holdings=[
            HoldingWithAnchors(
                holding=copy.deepcopy(holding),
                anchors=copy.deepcopy(ANCHORS[index]),
            )
            for index, holding in enumerate(HOLDINGS)
        ],
        named_anchors=copy.deepcopy(NAMED_ANCHORS),
        enactment_anchors=copy.deepcopy(ENACTMENT_ANCHORS),
    )
