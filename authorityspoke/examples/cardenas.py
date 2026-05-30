import copy

from authorityspoke.holdings import HoldingGroup
from authorityspoke.opinions import (
    AnchoredHoldings,
    HoldingWithAnchors,
    TextPositionSet,
)


from legislice.groups import EnactmentGroup

from authorityspoke import Entity, Fact, Holding, Predicate, Rule
from authorityspoke.examples.legislation import (
    ATTEMPT_STATUTE,
    EVID_351,
    ROBBERY_STATUTE,
    UNDUE_PREJUDICE_RULE,
)
from authorityspoke.facts import (
    AbsenceOfFactor,
    Allegation,
    Evidence,
    Exhibit,
    Pleading,
)
from authorityspoke.procedures import Procedure

ENTITIES: dict[str, Entity] = {
    "fact_that_the_defendant_committed_an_attempted_robbery": Entity(
        name="fact that the defendant committed an attempted robbery",
        generic=False,
    ),
    "the_defendant": Entity(name="the defendant", generic=True),
    "the_people_of_california": Entity(name="The People of California", generic=True),
    "parole_officer": Entity(name="parole officer", generic=True),
}
_FACT_ADDICTED_TO_HEROIN = Fact(
    predicate=Predicate(content="${the_defendant} was addicted to heroin"),
    terms=[ENTITIES["the_defendant"]],
    name="fact that the defendant was addicted to heroin",
    generic=False,
)
_FACT_ATTEMPTED_ROBBERY = Fact(
    predicate=Predicate(content="${the_defendant} committed an attempted robbery"),
    terms=[ENTITIES["the_defendant"]],
    name="fact that the defendant committed an attempted robbery",
    generic=False,
)
_OFFICER_TESTIMONY = Exhibit(
    offered_by=ENTITIES["the_people_of_california"],
    form="testimony",
    statement=_FACT_ADDICTED_TO_HEROIN,
    statement_attribution=ENTITIES["parole_officer"],
    name="officer's testimony that the defendant was addicted to heroin",
    generic=False,
)
_FACT_PROBATIVE_VALUE_WITH_DEFENDANT = Fact(
    predicate=Predicate(
        content="the probative value of {officer_s_testimony_that_the_defendant_was_addicted_to_heroin}, in showing {fact_that_the_defendant_committed_an_attempted_robbery}, was outweighed by unfair prejudice to {the_defendant}"
    ),
    terms=[
        _OFFICER_TESTIMONY,
        _FACT_ATTEMPTED_ROBBERY,
        ENTITIES["the_defendant"],
    ],
    name="the probative value of officer's testimony that the defendant was addicted to heroin, in showing fact that the defendant committed an attempted robbery, was outweighed by unfair prejudice to the defendant",
    generic=False,
)
_FACT_RELEVANT_MOTIVE = Fact(
    predicate=Predicate(
        content="${officer_s_testimony_that_the_defendant_was_addicted_to_heroin} was relevant to show {the_defendant} had a motive to commit an attempted robbery"
    ),
    terms=[_OFFICER_TESTIMONY, ENTITIES["the_defendant"]],
    name="officer's testimony that the defendant was addicted to heroin was relevant to show the defendant had a motive to commit an attempted robbery",
    generic=False,
)
_FACT_PROBATIVE_VALUE_TO_DEFENDANT = Fact(
    predicate=Predicate(
        content="the probative value of {officer_s_testimony_that_the_defendant_was_addicted_to_heroin}, in showing {fact_that_the_defendant_committed_an_attempted_robbery}, was outweighed by unfair prejudice to defendant"
    ),
    terms=[_OFFICER_TESTIMONY, _FACT_ATTEMPTED_ROBBERY],
    name="the probative value of officer's testimony that the defendant was addicted to heroin, in showing fact that the defendant committed an attempted robbery, was outweighed by unfair prejudice to defendant",
    generic=False,
)
FACTS: list[Fact] = [
    _FACT_ADDICTED_TO_HEROIN,
    _FACT_ATTEMPTED_ROBBERY,
    _FACT_PROBATIVE_VALUE_WITH_DEFENDANT,
    _FACT_RELEVANT_MOTIVE,
    _FACT_PROBATIVE_VALUE_TO_DEFENDANT,
]


def _build_holdings() -> HoldingGroup:
    facts_by_name = {fact.name: fact for fact in FACTS}

    attempted_robbery = facts_by_name[
        "fact that the defendant committed an attempted robbery"
    ]
    probative_with_defendant = facts_by_name[
        "the probative value of officer's testimony that the defendant was addicted to heroin, in showing fact that the defendant committed an attempted robbery, was outweighed by unfair prejudice to the defendant"
    ]
    relevant_motive = facts_by_name[
        "officer's testimony that the defendant was addicted to heroin was relevant to show the defendant had a motive to commit an attempted robbery"
    ]
    probative_to_defendant = facts_by_name[
        "the probative value of officer's testimony that the defendant was addicted to heroin, in showing fact that the defendant committed an attempted robbery, was outweighed by unfair prejudice to defendant"
    ]

    attempted_robbery_charge = Allegation(
        fact=attempted_robbery,
        pleading=Pleading(
            filer=ENTITIES["the_people_of_california"],
            name="pleading filed by The People of California",
            generic=False,
        ),
        name="the attempted robbery charge",
        generic=False,
    )

    evidence_of_officer_testimony = Evidence(
        exhibit=_OFFICER_TESTIMONY,
        to_effect=attempted_robbery,
        name="evidence of officer's testimony that the defendant was addicted to heroin",
        generic=False,
    )
    no_evidence_of_officer_testimony = AbsenceOfFactor(
        absent=evidence_of_officer_testimony,
        generic=False,
    )

    enactments = EnactmentGroup(
        passages=[
            copy.deepcopy(EVID_351),
            copy.deepcopy(UNDUE_PREJUDICE_RULE),
            copy.deepcopy(ROBBERY_STATUTE),
            copy.deepcopy(ATTEMPT_STATUTE),
        ]
    )

    holding_one = Holding(
        rule=Rule(
            procedure=Procedure(
                inputs=[_OFFICER_TESTIMONY, attempted_robbery_charge],
                outputs=[probative_with_defendant],
                despite=[relevant_motive],
            ),
            enactments=copy.deepcopy(enactments),
            enactments_despite=EnactmentGroup(passages=[]),
            mandatory=True,
            universal=False,
        ),
        rule_valid=True,
        decided=True,
        exclusive=False,
        generic=False,
    )

    holding_two = Holding(
        rule=Rule(
            procedure=Procedure(
                inputs=[probative_to_defendant],
                outputs=[no_evidence_of_officer_testimony],
                despite=[relevant_motive],
            ),
            enactments=copy.deepcopy(enactments),
            enactments_despite=EnactmentGroup(passages=[]),
            mandatory=True,
            universal=False,
        ),
        rule_valid=True,
        decided=True,
        exclusive=False,
        generic=False,
    )

    return HoldingGroup([holding_one, holding_two])


ANCHORS: list[TextPositionSet] = [
    TextPositionSet(
        positions=[],
        quotes=[],
    ),
    TextPositionSet(
        positions=[],
        quotes=[],
    ),
]
HOLDINGS = _build_holdings()


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
        named_anchors=[],
        enactment_anchors=[],
    )
