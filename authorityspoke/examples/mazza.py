import copy
from datetime import date

from anchorpoint.textselectors import TextQuoteSelector
from authorityspoke import Entity, Fact, Holding, Predicate, Rule
from authorityspoke.opinions import (
    AnchoredHoldings,
    EnactmentWithAnchors,
    HoldingWithAnchors,
    TermWithAnchors,
    TextPositionSet,
)
from authorityspoke.examples.legislation import (
    DOMESTIC_FINANCIAL_INSTITUTION_PROVISION,
    STATE_MONEY_TRANSMITTING_LICENSE_PROVISION,
)
from authorityspoke.procedures import Procedure
from legislice.enactments import (
    Enactment,
    EnactmentPassage,
    TextPositionSet as EnactmentTextPositionSet,
    TextVersion,
)
from legislice.groups import EnactmentGroup

ENTITIES: dict[str, Entity] = {
    "mazza_alaluf": Entity(name="Mazza-Alaluf", generic=True, plural=False),
    "turismo_costa_brava": Entity(
        name="Turismo Costa Brava", generic=True, plural=False
    ),
}

FACT_USED_BUSINESS_TO_COMMIT = Fact(
    predicate=Predicate(
        content="{mazza_alaluf} used {mazza_alaluf}'s business {turismo_costa_brava} to commit the New York offense of engaging in the business of receiving money for transmission or transmitting the same, without a license therefor"
    ),
    terms=[ENTITIES["mazza_alaluf"], ENTITIES["turismo_costa_brava"]],
    name=(
        "Mazza-Alaluf used Mazza-Alaluf's business Turismo Costa Brava to commit the "
        "New York offense of engaging in the business of receiving money for transmission "
        "or transmitting the same, without a license therefor"
    ),
    generic=False,
)
FACT_OPERATED_WITHOUT_LICENSE = Fact(
    predicate=Predicate(
        content="{mazza_alaluf} operated {turismo_costa_brava} without an appropriate money transmitting license in a State where such operation was punishable as a misdemeanor or a felony under State law"
    ),
    terms=[ENTITIES["mazza_alaluf"], ENTITIES["turismo_costa_brava"]],
    name="operated without license",
    generic=False,
)
FACT_MAZZA_OPERATED_AS_BUSINESS = Fact(
    predicate=Predicate(
        content="{mazza_alaluf} operated {turismo_costa_brava} as a business"
    ),
    terms=[ENTITIES["mazza_alaluf"], ENTITIES["turismo_costa_brava"]],
    name="Mazza-Alaluf operated Turismo Costa Brava as a business",
    generic=False,
)
FACT_TURISMO_MONEY_TRANSMITTING = Fact(
    predicate=Predicate(
        content="{turismo_costa_brava} was a money transmitting business"
    ),
    terms=[ENTITIES["turismo_costa_brava"]],
    name="Turismo Costa Brava was a money transmitting business",
    generic=False,
)
FACT_TURISMO_DOMESTIC_FINANCIAL_INSTITUTION = Fact(
    predicate=Predicate(
        content="{turismo_costa_brava} was a domestic financial institution",
        truth=False,
    ),
    terms=[ENTITIES["turismo_costa_brava"]],
    name="Turismo Costa Brava was a domestic financial institution",
    generic=False,
)
FACT_MAZZA_COMMITTED_OFFENSE = Fact(
    predicate=Predicate(
        content="{mazza_alaluf} committed the offense of conducting a money transmitting business without a license required by state law"
    ),
    terms=[ENTITIES["mazza_alaluf"]],
    name=(
        "Mazza-Alaluf committed the offense of conducting a money transmitting business "
        "without a license required by state law"
    ),
    generic=False,
)

FACTS = [
    FACT_USED_BUSINESS_TO_COMMIT,
    FACT_OPERATED_WITHOUT_LICENSE,
    FACT_MAZZA_OPERATED_AS_BUSINESS,
    FACT_TURISMO_MONEY_TRANSMITTING,
    FACT_TURISMO_DOMESTIC_FINANCIAL_INSTITUTION,
    FACT_MAZZA_COMMITTED_OFFENSE,
]
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
    passage: EnactmentPassage,
    quotes: list[dict[str, str]],
    positions: list[dict[str, int | None]] | None = None,
) -> EnactmentWithAnchors:
    return EnactmentWithAnchors.model_validate(
        {"passage": passage, "anchors": _anchor(quotes, positions=positions)}
    )


HOLDINGS: list[Holding] = [
    Holding(
        rule=Rule(
            procedure=Procedure(
                inputs=[FACT_USED_BUSINESS_TO_COMMIT],
                outputs=[FACT_OPERATED_WITHOUT_LICENSE],
            ),
            enactments=EnactmentGroup(
                passages=[copy.deepcopy(STATE_MONEY_TRANSMITTING_LICENSE_PROVISION)]
            ),
            mandatory=False,
            universal=True,
        ),
        rule_valid=True,
        decided=True,
        exclusive=False,
        generic=False,
    ),
    Holding(
        rule=Rule(
            procedure=Procedure(
                inputs=[
                    FACT_OPERATED_WITHOUT_LICENSE,
                    FACT_MAZZA_OPERATED_AS_BUSINESS,
                    FACT_TURISMO_MONEY_TRANSMITTING,
                ],
                despite=[FACT_TURISMO_DOMESTIC_FINANCIAL_INSTITUTION],
                outputs=[FACT_MAZZA_COMMITTED_OFFENSE],
            ),
            enactments=EnactmentGroup(
                passages=[copy.deepcopy(STATE_MONEY_TRANSMITTING_LICENSE_PROVISION)]
            ),
            enactments_despite=EnactmentGroup(
                passages=[copy.deepcopy(DOMESTIC_FINANCIAL_INSTITUTION_PROVISION)]
            ),
            mandatory=True,
            universal=True,
        ),
        rule_valid=True,
        decided=True,
        exclusive=False,
        generic=False,
    ),
]

ANCHORS = [
    _anchor([]),
    _anchor(
        [
            _quote(
                "",
                prefix="Accordingly, we conclude that the",
                suffix="In any event",
            )
        ]
    ),
]

NAMED_ANCHORS = [
    TermWithAnchors.model_validate(
        {
            "term": FACT_OPERATED_WITHOUT_LICENSE,
            "anchors": _anchor(
                [
                    _quote(
                        "we conclude that sufficient evidence supports Mazza-Alaluf's convictions under 18 U.S.C. § 1960(b)(1)(A) for conspiring to operate and operating a money transmitting business without appropriate state licenses."
                    )
                ]
            ),
        }
    ),
    TermWithAnchors.model_validate(
        {
            "term": FACT_TURISMO_MONEY_TRANSMITTING,
            "anchors": _anchor(
                [
                    _quote(
                        "record evidence that Turismo conducted substantial money transmitting business in the three states"
                    )
                ]
            ),
        }
    ),
    TermWithAnchors.model_validate(
        {
            "term": FACT_TURISMO_DOMESTIC_FINANCIAL_INSTITUTION,
            "anchors": _anchor(
                [
                    _quote(
                        'without respect to whether or not Turismo was a "domestic financial institution"'
                    )
                ]
            ),
        }
    ),
]

ENACTMENT_ANCHORS = [
    _enactment_anchor(
        copy.deepcopy(STATE_MONEY_TRANSMITTING_LICENSE_PROVISION),
        [_quote("state money transmitting licenses, see |18 U.S.C. § 1960(b)(1)(A)|")],
    ),
    _enactment_anchor(
        copy.deepcopy(DOMESTIC_FINANCIAL_INSTITUTION_PROVISION),
        [_quote('§ 5312(b)(1) (defining "domestic financial institution")')],
    ),
]


def anchored_holdings() -> AnchoredHoldings:
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
