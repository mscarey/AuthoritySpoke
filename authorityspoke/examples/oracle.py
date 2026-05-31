import copy
from typing import Literal, NotRequired, TypedDict, cast

from anchorpoint.textselectors import TextQuoteSelector
from authorityspoke import Entity, Fact, Holding, Predicate, Rule
from authorityspoke.examples.legislation import (
    COPYRIGHTABILITY_REQUIREMENT,
    IDEA_EXPRESSION_RULE,
    SHORT_PHRASES_EXCLUSION_RULE,
)
from authorityspoke.facts import AbsenceOfFactor
from authorityspoke.holdings import HoldingGroup
from authorityspoke.opinions import (
    AnchoredHoldings,
    EnactmentWithAnchors,
    HoldingWithAnchors,
    TermWithAnchors,
    TextPositionSet,
)
from authorityspoke.procedures import Procedure
from legislice.groups import EnactmentGroup

ENTITIES: dict[str, Entity] = {
    "the_java_api": Entity(name="the Java API", generic=True, plural=False),
    "the_java_language": Entity(name="the Java language", generic=True, plural=False),
    "google": Entity(name="Google", generic=True, plural=False),
    "sun_microsystems": Entity(name="Sun Microsystems", generic=True, plural=False),
    "the_java_api_contained_short_phrases": Entity(
        name="the Java API contained short phrases", generic=False, plural=False
    ),
}
ENTITY_BY_NAME = {entity.name: entity for entity in ENTITIES.values()}


class FactSpec(TypedDict):
    name: str
    content: str
    truth: bool
    terms: list[str]


FactorRef = tuple[Literal["fact", "absence"], str]


class HoldingSpec(TypedDict):
    rule_valid: bool
    decided: bool
    exclusive: bool
    mandatory: bool
    universal: bool
    enactments: list[str]
    enactments_despite: NotRequired[list[str]]
    inputs: list[FactorRef]
    despite: list[FactorRef]
    outputs: list[FactorRef]


FACT_SPECS: list[FactSpec] = [
    {
        "name": "false the Java API was an original work",
        "content": "{the_java_api} was an original work",
        "truth": False,
        "terms": ["the Java API"],
    },
    {
        "name": "false the Java API was copyrightable",
        "content": "{the_java_api} was copyrightable",
        "truth": False,
        "terms": ["the Java API"],
    },
    {
        "name": "the Java API was independently created by the author, as opposed to copied from other works",
        "content": "{the_java_api} was independently created by the author, as opposed to copied from other works",
        "truth": True,
        "terms": ["the Java API"],
    },
    {
        "name": "the Java API possessed at least some minimal degree of creativity",
        "content": "{the_java_api} possessed at least some minimal degree of creativity",
        "truth": True,
        "terms": ["the Java API"],
    },
    {
        "name": "the Java API was an original work",
        "content": "{the_java_api} was an original work",
        "truth": True,
        "terms": ["the Java API"],
    },
    {
        "name": "the Java API was the expression of an idea",
        "content": "{the_java_api} was the expression of an idea",
        "truth": True,
        "terms": ["the Java API"],
    },
    {
        "name": "false the Java API was an idea",
        "content": "{the_java_api} was an idea",
        "truth": False,
        "terms": ["the Java API"],
    },
    {
        "name": "the Java API was essentially the only way to express the idea that it embodied",
        "content": "{the_java_api} was essentially the only way to express the idea that it embodied",
        "truth": True,
        "terms": ["the Java API"],
    },
    {
        "name": "the Java API was a scene a faire",
        "content": "{the_java_api} was a scene a faire",
        "truth": True,
        "terms": ["the Java API"],
    },
    {
        "name": "the Java API was copyrightable",
        "content": "{the_java_api} was copyrightable",
        "truth": True,
        "terms": ["the Java API"],
    },
    {
        "name": "the Java language was a computer program",
        "content": "{the_java_language} was a computer program",
        "truth": True,
        "terms": ["the Java language"],
    },
    {
        "name": "the Java API was the source code of the Java language",
        "content": "{the_java_api} was the source code of {the_java_language}",
        "truth": True,
        "terms": ["the Java API", "the Java language"],
    },
    {
        "name": "the Java API was a literal element of the Java language",
        "content": "{the_java_api} was a literal element of {the_java_language}",
        "truth": True,
        "terms": ["the Java API", "the Java language"],
    },
    {
        "name": "the Java API was the object code of the Java language",
        "content": "{the_java_api} was the object code of {the_java_language}",
        "truth": True,
        "terms": ["the Java API", "the Java language"],
    },
    {
        "name": "the Java API was the sequence, structure, and organization of the Java language",
        "content": "{the_java_api} was the sequence, structure, and organization of {the_java_language}",
        "truth": True,
        "terms": ["the Java API", "the Java language"],
    },
    {
        "name": "the Java API was a non-literal element of the Java language",
        "content": "{the_java_api} was a non-literal element of {the_java_language}",
        "truth": True,
        "terms": ["the Java API", "the Java language"],
    },
    {
        "name": "the Java API was the user interface of the Java language",
        "content": "{the_java_api} was the user interface of {the_java_language}",
        "truth": True,
        "terms": ["the Java API", "the Java language"],
    },
    {
        "name": "false the Java API was the expression of an idea",
        "content": "{the_java_api} was the expression of an idea",
        "truth": False,
        "terms": ["the Java API"],
    },
    {
        "name": "the Java API was an idea",
        "content": "{the_java_api} was an idea",
        "truth": True,
        "terms": ["the Java API"],
    },
    {
        "name": "the Java API was a set of application programming interface declarations",
        "content": "{the_java_api} was a set of application programming interface declarations",
        "truth": True,
        "terms": ["the Java API"],
    },
    {
        "name": "false the Java API was essentially the only way to express the idea that it embodied",
        "content": "{the_java_api} was essentially the only way to express the idea that it embodied",
        "truth": False,
        "terms": ["the Java API"],
    },
    {
        "name": "the Java API was creative",
        "content": "{the_java_api} was creative",
        "truth": True,
        "terms": ["the Java API"],
    },
    {
        "name": "it was possible to use the Java language without copying the Java API",
        "content": "it was possible to use {the_java_language} without copying {the_java_api}",
        "truth": True,
        "terms": ["the Java language", "the Java API"],
    },
    {
        "name": "the Java API was a method of operation",
        "content": "{the_java_api} was a method of operation",
        "truth": True,
        "terms": ["the Java API"],
    },
    {
        "name": "the Java API contained short phrases",
        "content": "{the_java_api} contained short phrases",
        "truth": True,
        "terms": ["the Java API"],
    },
    {
        "name": "the Java API became so popular that it was the industry standard",
        "content": "{the_java_api} became so popular that it was the industry standard",
        "truth": True,
        "terms": ["the Java API"],
    },
    {
        "name": "there was a preexisting community of programmers accustomed to using the Java API",
        "content": "there was a preexisting community of programmers accustomed to using {the_java_api}",
        "truth": True,
        "terms": ["the Java API"],
    },
    {
        "name": "false Google infringed the copyright on the Java API",
        "content": "{google} infringed the copyright on {the_java_api}",
        "truth": False,
        "terms": ["Google", "the Java API"],
    },
    {
        "name": "Google infringed the copyright on the Java API",
        "content": "{google} infringed the copyright on {the_java_api}",
        "truth": True,
        "terms": ["Google", "the Java API"],
    },
    {
        "name": "Sun Microsystems created the Java API",
        "content": "{sun_microsystems} created {the_java_api}",
        "truth": True,
        "terms": ["Sun Microsystems", "the Java API"],
    },
    {
        "name": "when creating the Java API, Sun Microsystems could have selected and arranged its names and phrases in unlimited different ways",
        "content": "when creating {the_java_api}, {sun_microsystems} could have selected and arranged its names and phrases in unlimited different ways",
        "truth": True,
        "terms": ["the Java API", "Sun Microsystems"],
    },
    {
        "name": "the Java API was a literary work",
        "content": "{the_java_api} was a literary work",
        "truth": True,
        "terms": ["the Java API"],
    },
    {
        "name": "the Java API contained short phrases that were creative",
        "content": "{the_java_api_contained_short_phrases} that were creative",
        "truth": True,
        "terms": ["the Java API contained short phrases"],
    },
    {
        "name": "the Java API was an element of the Java language",
        "content": "{the_java_api} was an element of {the_java_language}",
        "truth": True,
        "terms": ["the Java API", "the Java language"],
    },
    {
        "name": "the creation of the Java API was dictated by external factors such as the mechanical specifications of the computer on which the Java language was intended to run or widely accepted programming practices within the computer industry",
        "content": "the creation of {the_java_api} was dictated by external factors such as the mechanical specifications of the computer on which {the_java_language} was intended to run or widely accepted programming practices within the computer industry",
        "truth": True,
        "terms": ["the Java API", "the Java language"],
    },
    {
        "name": "Sun Microsystems was the author of the Java API",
        "content": "{sun_microsystems} was the author of {the_java_api}",
        "truth": True,
        "terms": ["Sun Microsystems", "the Java API"],
    },
    {
        "name": "when creating the Java API, Sun Microsystems had multiple ways to express its underlying idea",
        "content": "when creating {the_java_api}, {sun_microsystems} had multiple ways to express its underlying idea",
        "truth": True,
        "terms": ["the Java API", "Sun Microsystems"],
    },
    {
        "name": "the Java API served a function",
        "content": "{the_java_api} served a function",
        "truth": True,
        "terms": ["the Java API"],
    },
    {
        "name": "the Java language was copyrightable",
        "content": "{the_java_language} was copyrightable",
        "truth": True,
        "terms": ["the Java language"],
    },
]


def _build_facts() -> list[Fact]:
    facts = []
    for spec in FACT_SPECS:
        facts.append(
            Fact(
                predicate=Predicate(content=spec["content"], truth=spec["truth"]),
                terms=[ENTITY_BY_NAME[name] for name in spec["terms"]],
                name=spec["name"],
                generic=False,
            )
        )
    return facts


FACTS: list[Fact] = _build_facts()
FACTS_BY_NAME = {fact.name: fact for fact in FACTS}


def _quote(exact: str, prefix: str = "", suffix: str = "") -> dict[str, str]:
    return {"exact": exact, "prefix": prefix, "suffix": suffix}


def _anchor(
    quotes: list[dict[str, str]], positions: list[dict[str, int | None]] | None = None
) -> TextPositionSet:
    return TextPositionSet.model_validate(
        {"positions": positions or [], "quotes": quotes}
    )


def _enactment_anchor(
    passage,
    quotes: list[dict[str, str]],
    positions: list[dict[str, int | None]] | None = None,
) -> EnactmentWithAnchors:
    return EnactmentWithAnchors.model_validate(
        {"passage": passage, "anchors": _anchor(quotes, positions=positions)}
    )


HOLDING_SPECS: list[HoldingSpec] = [
    {
        "rule_valid": True,
        "decided": True,
        "exclusive": False,
        "mandatory": True,
        "universal": False,
        "enactments": ["/us/usc/t17/s102/a"],
        "inputs": [("fact", "false the Java API was an original work")],
        "despite": [],
        "outputs": [("fact", "false the Java API was copyrightable")],
    },
    {
        "rule_valid": True,
        "decided": True,
        "exclusive": False,
        "mandatory": True,
        "universal": True,
        "enactments": ["/us/usc/t17/s102/a"],
        "inputs": [
            (
                "fact",
                "the Java API was independently created by the author, as opposed to copied from other works",
            ),
            (
                "fact",
                "the Java API possessed at least some minimal degree of creativity",
            ),
        ],
        "despite": [],
        "outputs": [("fact", "the Java API was an original work")],
    },
    {
        "rule_valid": True,
        "decided": True,
        "exclusive": False,
        "mandatory": True,
        "universal": False,
        "enactments": ["/us/usc/t17/s102/a"],
        "inputs": [
            ("fact", "the Java API was an original work"),
            ("fact", "the Java API was the expression of an idea"),
            ("fact", "false the Java API was an idea"),
        ],
        "despite": [
            (
                "fact",
                "the Java API was essentially the only way to express the idea that it embodied",
            ),
            ("fact", "the Java API was a scene a faire"),
        ],
        "outputs": [("fact", "the Java API was copyrightable")],
    },
    {
        "rule_valid": True,
        "decided": True,
        "exclusive": False,
        "mandatory": True,
        "universal": True,
        "enactments": ["/us/usc/t17/s102/a", "/us/usc/t17/s102/b"],
        "inputs": [
            ("fact", "the Java language was a computer program"),
            ("fact", "the Java API was the source code of the Java language"),
        ],
        "despite": [],
        "outputs": [
            ("fact", "the Java API was a literal element of the Java language")
        ],
    },
    {
        "rule_valid": True,
        "decided": True,
        "exclusive": False,
        "mandatory": True,
        "universal": True,
        "enactments": ["/us/usc/t17/s102/a", "/us/usc/t17/s102/b"],
        "inputs": [
            ("fact", "the Java language was a computer program"),
            ("fact", "the Java API was the object code of the Java language"),
        ],
        "despite": [],
        "outputs": [
            ("fact", "the Java API was a literal element of the Java language")
        ],
    },
    {
        "rule_valid": True,
        "decided": True,
        "exclusive": False,
        "mandatory": True,
        "universal": False,
        "enactments": ["/us/usc/t17/s102/a"],
        "inputs": [
            ("fact", "the Java language was a computer program"),
            ("fact", "the Java API was a literal element of the Java language"),
        ],
        "despite": [],
        "outputs": [("fact", "the Java API was copyrightable")],
    },
    {
        "rule_valid": True,
        "decided": True,
        "exclusive": False,
        "mandatory": True,
        "universal": True,
        "enactments": ["/us/usc/t17/s102/a", "/us/usc/t17/s102/b"],
        "inputs": [
            ("fact", "the Java language was a computer program"),
            (
                "fact",
                "the Java API was the sequence, structure, and organization of the Java language",
            ),
        ],
        "despite": [],
        "outputs": [
            ("fact", "the Java API was a non-literal element of the Java language")
        ],
    },
    {
        "rule_valid": True,
        "decided": True,
        "exclusive": False,
        "mandatory": True,
        "universal": True,
        "enactments": ["/us/usc/t17/s102/a", "/us/usc/t17/s102/b"],
        "inputs": [
            ("fact", "the Java language was a computer program"),
            ("fact", "the Java API was the user interface of the Java language"),
        ],
        "despite": [],
        "outputs": [
            ("fact", "the Java API was a non-literal element of the Java language")
        ],
    },
    {
        "rule_valid": True,
        "decided": True,
        "exclusive": False,
        "mandatory": True,
        "universal": False,
        "enactments": ["/us/usc/t17/s102/a"],
        "inputs": [
            ("fact", "the Java language was a computer program"),
            ("fact", "the Java API was a non-literal element of the Java language"),
            ("fact", "the Java API was the expression of an idea"),
            ("fact", "false the Java API was an idea"),
        ],
        "despite": [],
        "outputs": [("fact", "the Java API was copyrightable")],
    },
    {
        "rule_valid": True,
        "decided": True,
        "exclusive": False,
        "mandatory": True,
        "universal": False,
        "enactments": ["/us/usc/t17/s102/b"],
        "inputs": [
            ("fact", "the Java language was a computer program"),
            ("fact", "the Java API was a non-literal element of the Java language"),
            ("fact", "false the Java API was the expression of an idea"),
            ("fact", "the Java API was an idea"),
        ],
        "despite": [],
        "outputs": [("fact", "false the Java API was copyrightable")],
    },
    {
        "rule_valid": True,
        "decided": True,
        "exclusive": False,
        "mandatory": True,
        "universal": False,
        "enactments": ["/us/usc/t17/s102/a"],
        "enactments_despite": ["/us/usc/t17/s102/b", "/us/cfr/t37/s202.1"],
        "inputs": [
            ("fact", "the Java language was a computer program"),
            (
                "fact",
                "the Java API was a set of application programming interface declarations",
            ),
            ("fact", "the Java API was an original work"),
            ("fact", "the Java API was a non-literal element of the Java language"),
            ("fact", "the Java API was the expression of an idea"),
            (
                "fact",
                "false the Java API was essentially the only way to express the idea that it embodied",
            ),
            ("fact", "the Java API was creative"),
            (
                "fact",
                "it was possible to use the Java language without copying the Java API",
            ),
        ],
        "despite": [
            ("fact", "the Java API was a method of operation"),
            ("fact", "the Java API contained short phrases"),
            (
                "fact",
                "the Java API became so popular that it was the industry standard",
            ),
            (
                "fact",
                "there was a preexisting community of programmers accustomed to using the Java API",
            ),
        ],
        "outputs": [("fact", "the Java API was copyrightable")],
    },
    {
        "rule_valid": True,
        "decided": True,
        "exclusive": False,
        "mandatory": True,
        "universal": False,
        "enactments": ["/us/usc/t17/s102/b"],
        "inputs": [("fact", "the Java API was a scene a faire")],
        "despite": [("fact", "the Java API was copyrightable")],
        "outputs": [("fact", "false Google infringed the copyright on the Java API")],
    },
    {
        "rule_valid": True,
        "decided": True,
        "exclusive": False,
        "mandatory": True,
        "universal": False,
        "enactments": ["/us/usc/t17/s102/b"],
        "inputs": [
            (
                "fact",
                "the Java API was essentially the only way to express the idea that it embodied",
            )
        ],
        "despite": [("fact", "the Java API was copyrightable")],
        "outputs": [("fact", "false Google infringed the copyright on the Java API")],
    },
    {
        "rule_valid": True,
        "decided": True,
        "exclusive": False,
        "mandatory": True,
        "universal": False,
        "enactments": ["/us/usc/t17/s102/b"],
        "inputs": [
            ("fact", "the Java API was copyrightable"),
            (
                "absence",
                "the Java API was essentially the only way to express the idea that it embodied",
            ),
            ("absence", "the Java API was a scene a faire"),
        ],
        "despite": [],
        "outputs": [("fact", "Google infringed the copyright on the Java API")],
    },
    {
        "rule_valid": True,
        "decided": True,
        "exclusive": False,
        "mandatory": True,
        "universal": False,
        "enactments": ["/us/usc/t17/s102/a"],
        "inputs": [
            ("fact", "Sun Microsystems created the Java API"),
            (
                "fact",
                "when creating the Java API, Sun Microsystems could have selected and arranged its names and phrases in unlimited different ways",
            ),
        ],
        "despite": [],
        "outputs": [
            (
                "fact",
                "false the Java API was essentially the only way to express the idea that it embodied",
            )
        ],
    },
    {
        "rule_valid": True,
        "decided": True,
        "exclusive": False,
        "mandatory": True,
        "universal": False,
        "enactments": ["/us/usc/t17/s102/a"],
        "inputs": [
            ("fact", "the Java API was a literary work"),
            ("fact", "the Java API contained short phrases that were creative"),
        ],
        "despite": [("fact", "the Java API contained short phrases")],
        "outputs": [("fact", "the Java API was copyrightable")],
    },
    {
        "rule_valid": True,
        "decided": True,
        "exclusive": False,
        "mandatory": False,
        "universal": False,
        "enactments": ["/us/usc/t17/s102/b"],
        "inputs": [
            ("fact", "the Java language was a computer program"),
            ("fact", "the Java API was an element of the Java language"),
            (
                "fact",
                "the creation of the Java API was dictated by external factors such as the mechanical specifications of the computer on which the Java language was intended to run or widely accepted programming practices within the computer industry",
            ),
        ],
        "despite": [],
        "outputs": [("fact", "the Java API was a scene a faire")],
    },
    {
        "rule_valid": True,
        "decided": True,
        "exclusive": False,
        "mandatory": False,
        "universal": False,
        "enactments": ["/us/usc/t17/s102/a"],
        "inputs": [
            ("fact", "the Java language was a computer program"),
            (
                "fact",
                "the Java API was the sequence, structure, and organization of the Java language",
            ),
            ("fact", "the Java API was the expression of an idea"),
            ("fact", "false the Java API was an idea"),
        ],
        "despite": [],
        "outputs": [("fact", "the Java API was copyrightable")],
    },
    {
        "rule_valid": True,
        "decided": True,
        "exclusive": False,
        "mandatory": True,
        "universal": True,
        "enactments": ["/us/usc/t17/s102/a"],
        "inputs": [
            ("fact", "the Java API was an original work"),
            ("fact", "Sun Microsystems was the author of the Java API"),
            (
                "fact",
                "when creating the Java API, Sun Microsystems had multiple ways to express its underlying idea",
            ),
        ],
        "despite": [("fact", "the Java API served a function")],
        "outputs": [("fact", "the Java API was copyrightable")],
    },
    {
        "rule_valid": True,
        "decided": True,
        "exclusive": False,
        "mandatory": False,
        "universal": False,
        "enactments": ["/us/usc/t17/s102/a"],
        "inputs": [("fact", "the Java language was a computer program")],
        "despite": [],
        "outputs": [("fact", "the Java language was copyrightable")],
    },
]


def _build_holdings() -> HoldingGroup:
    facts_by_name = {fact.name: fact for fact in FACTS}

    oracle_copyrightability_requirement = copy.deepcopy(COPYRIGHTABILITY_REQUIREMENT)
    oracle_copyrightability_requirement.selection = TextPositionSet(
        quotes=[
            TextQuoteSelector(
                exact="Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.",
                prefix="",
                suffix="",
            )
        ]
    )

    enactment_by_node = {
        "/us/usc/t17/s102/a": oracle_copyrightability_requirement,
        "/us/usc/t17/s102/b": IDEA_EXPRESSION_RULE,
        "/us/cfr/t37/s202.1": SHORT_PHRASES_EXCLUSION_RULE,
    }

    def make_factor(ref_type: str, fact_name: str):
        if ref_type == "absence":
            return AbsenceOfFactor(absent=facts_by_name[fact_name], generic=False)
        return facts_by_name[fact_name]

    holdings = []
    for spec in HOLDING_SPECS:
        holdings.append(
            Holding(
                rule=Rule(
                    procedure=Procedure(
                        inputs=[
                            make_factor(ref_type, name)
                            for ref_type, name in spec["inputs"]
                        ],
                        despite=[
                            make_factor(ref_type, name)
                            for ref_type, name in spec["despite"]
                        ],
                        outputs=[
                            make_factor(ref_type, name)
                            for ref_type, name in spec["outputs"]
                        ],
                    ),
                    enactments=EnactmentGroup(
                        passages=[
                            copy.deepcopy(enactment_by_node[node])
                            for node in spec["enactments"]
                        ]
                    ),
                    enactments_despite=EnactmentGroup(
                        passages=[
                            copy.deepcopy(enactment_by_node[node])
                            for node in spec.get("enactments_despite", [])
                        ]
                    ),
                    mandatory=spec["mandatory"],
                    universal=spec["universal"],
                ),
                rule_valid=spec["rule_valid"],
                decided=spec["decided"],
                exclusive=spec["exclusive"],
            )
        )

    return HoldingGroup(holdings)


HOLDINGS = _build_holdings()

ANCHORS: list[TextPositionSet] = [
    _anchor(
        positions=[],
        quotes=[
            {
                "exact": "must be “original” to qualify",
                "prefix": "By statute, a work ",
                "suffix": " for",
            }
        ],
    ),
    _anchor([], []),
    _anchor(
        positions=[],
        quotes=[
            {
                "exact": "Oracle had “unlimited options as to the selection and arrangement of the 7000 lines Google copied.",
                "prefix": "",
                "suffix": "",
            }
        ],
    ),
    _anchor([], []),
    _anchor([], []),
    _anchor([], []),
    _anchor([], []),
    _anchor([], []),
    _anchor(
        positions=[],
        quotes=[
            {
                "exact": "as long as the author had multiple ways to express the underlying idea",
                "prefix": "",
                "suffix": "",
            }
        ],
    ),
    _anchor([], []),
    _anchor([], []),
    _anchor([], []),
    _anchor([], []),
    _anchor([], []),
    _anchor([], []),
    _anchor([], []),
    _anchor([], []),
    _anchor([], []),
    _anchor(
        positions=[],
        quotes=[
            {
                "exact": "the program’s sequence, structure, and organization,",
                "prefix": "include, among other things,",
                "suffix": "as well as",
            },
            {"exact": "c", "prefix": "", "suffix": ""},
        ],
    ),
    _anchor([], []),
]

NAMED_ANCHORS = [
    TermWithAnchors.model_validate(
        {
            "term": FACTS_BY_NAME["the Java API was copyrightable"],
            "anchors": _anchor(
                [
                    _quote(
                        "copyright protection.",
                        "must be “original” to qualify for ",
                        "",
                    )
                ]
            ),
        }
    )
]

ENACTMENT_ANCHORS = [
    _enactment_anchor(
        copy.deepcopy(cast(Holding, HOLDINGS[0]).rule.enactments.passages[0]),
        [_quote("17 U.S.C. § 102(a)", "qualify for copyright protection. ", ".")],
    )
]


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
