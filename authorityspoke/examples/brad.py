import copy
from typing import Any, cast

from legislice.groups import EnactmentGroup

from authorityspoke.holdings import HoldingGroup
from authorityspoke.opinions import AnchoredHoldings, HoldingWithAnchors
from authorityspoke import Comparison, Entity, Fact, Holding, Predicate, Rule
from authorityspoke.facts import AbsenceOfFactor, Evidence, Exhibit
from authorityspoke.procedures import Procedure
from authorityspoke.examples.legislation import DUE_PROCESS_CLAUSE, SEARCH_CLAUSE

ENTITIES = {
    "bradley": Entity(
        generic=True,
        name="Bradley",
        plural=False,
    ),
    "bradley_s_house": Entity(
        generic=True,
        name="Bradley's house",
        plural=False,
    ),
    "bradley_s_marijuana_patch": Entity(
        generic=True,
        name="Bradley's marijuana patch",
        plural=False,
    ),
    "officers_search_of_the_yard": Entity(
        generic=True,
        name="officers' search of the yard",
        plural=False,
    ),
    "the_prosecution": Entity(
        generic=True,
        name="the prosecution",
        plural=False,
    ),
}


def _build_holdings() -> HoldingGroup:
    e = ENTITIES

    def fact(
        content: str,
        terms: list[Any],
        name: str,
        truth: bool = True,
        sign: str | None = None,
        expression: str | int | None = None,
    ) -> Fact:
        predicate: Predicate | Comparison = Predicate(content=content, truth=truth)
        if sign is not None:
            predicate = Comparison.new(
                content=content, truth=truth, sign=sign, expression=expression
            )
        return Fact(predicate=cast(Any, predicate), terms=terms, name=name)

    committed_crime = Fact(
        predicate=Predicate(content="Bradley committed a crime"),
        terms=[],
        name="fact that Bradley committed a crime",
    )
    proof_exhibit = Exhibit(
        offered_by=e["the_prosecution"],
        name="proof of Bradley's guilt",
        generic=True,
    )
    evidence_of_guilt = Evidence(
        exhibit=proof_exhibit,
        to_effect=committed_crime,
        name="absence of evidence of Bradley's guilt",
    )
    no_evidence_of_guilt = AbsenceOfFactor(absent=evidence_of_guilt)

    f1 = fact(
        "{officers_search_of_the_yard} was a warrantless search and seizure",
        [e["officers_search_of_the_yard"]],
        "officers' search of the yard was a warrantless search and seizure",
    )
    f2 = fact(
        "{bradley_s_house} was a house",
        [e["bradley_s_house"]],
        "Bradley's house was a house",
    )
    f3 = fact(
        "{bradley} lived at {bradley_s_house}",
        [e["bradley"], e["bradley_s_house"]],
        "Bradley lived at Bradley's house",
    )
    f4 = fact(
        "{officers_search_of_the_yard} was performed by law enforcement officers",
        [e["officers_search_of_the_yard"]],
        "officers' search of the yard was performed by law enforcement officers",
    )
    f5 = fact(
        "{officers_search_of_the_yard} was performed in the grounds around {bradley_s_house}",
        [e["officers_search_of_the_yard"], e["bradley_s_house"]],
        "officers' search of the yard was performed in the grounds around Bradley's house",
    )
    f6 = fact(
        "{bradley} exhibited an expectation of privacy in {bradley_s_marijuana_patch}",
        [e["bradley"], e["bradley_s_marijuana_patch"]],
        "Bradley exhibited an expectation of privacy in Bradley's marijuana patch",
    )
    f7 = fact(
        "it was reasonable for {bradley} to hold an expectation of privacy in {bradley_s_marijuana_patch}",
        [e["bradley"], e["bradley_s_marijuana_patch"]],
        "it was reasonable for Bradley to hold an expectation of privacy in Bradley's marijuana patch",
    )
    f8 = fact(
        "{officers_search_of_the_yard} violated {bradley}'s expectation of privacy in {bradley_s_marijuana_patch}",
        [
            e["officers_search_of_the_yard"],
            e["bradley"],
            e["bradley_s_marijuana_patch"],
        ],
        "officers' search of the yard violated Bradley's expectation of privacy in Bradley's marijuana patch",
    )
    f9 = fact(
        "{officers_search_of_the_yard} was an unreasonable governmental intrusion upon {bradley_s_marijuana_patch}",
        [e["officers_search_of_the_yard"], e["bradley_s_marijuana_patch"]],
        "officers' search of the yard was an unreasonable governmental intrusion upon Bradley's marijuana patch",
    )
    f10 = fact(
        "{proof_of_bradley_s_guilt} was derived from {officers_search_of_the_yard}",
        [proof_exhibit, e["officers_search_of_the_yard"]],
        "proof of Bradley's guilt was derived from officers' search of the yard",
    )
    f12 = fact(
        "{bradley} exhibited an expectation of privacy in {bradley_s_marijuana_patch}",
        [e["bradley"], e["bradley_s_marijuana_patch"]],
        "false Bradley exhibited an expectation of privacy in Bradley's marijuana patch",
        truth=False,
    )
    f14 = fact(
        "{officers_search_of_the_yard} was an unreasonable intrusion upon {bradley_s_marijuana_patch}",
        [e["officers_search_of_the_yard"], e["bradley_s_marijuana_patch"]],
        "officers' search of the yard was an unreasonable intrusion upon Bradley's marijuana patch",
    )
    f15 = fact(
        "it was reasonable for {bradley} to hold an expectation of privacy in {bradley_s_marijuana_patch}",
        [e["bradley"], e["bradley_s_marijuana_patch"]],
        "false it was reasonable for Bradley to hold an expectation of privacy in Bradley's marijuana patch",
        truth=False,
    )
    f16 = fact(
        "{officers_search_of_the_yard} violated {bradley}'s expectation of privacy in {bradley_s_marijuana_patch}",
        [
            e["officers_search_of_the_yard"],
            e["bradley"],
            e["bradley_s_marijuana_patch"],
        ],
        "false officers' search of the yard violated Bradley's expectation of privacy in Bradley's marijuana patch",
        truth=False,
    )
    f17 = fact(
        "{officers_search_of_the_yard} was an unreasonable governmental intrusion upon {bradley_s_marijuana_patch}",
        [e["officers_search_of_the_yard"], e["bradley_s_marijuana_patch"]],
        "false officers' search of the yard was an unreasonable governmental intrusion upon Bradley's marijuana patch",
        truth=False,
    )
    f18 = fact(
        "the number of marijuana plants in {bradley_s_marijuana_patch} was",
        [e["bradley_s_marijuana_patch"]],
        "the number of marijuana plants in Bradley's marijuana patch was >= 3",
        sign=">=",
        expression=3,
    )
    f19 = fact(
        "{bradley_s_marijuana_patch} was in a yard accessible from a house that did not belong to {bradley}",
        [e["bradley_s_marijuana_patch"], e["bradley"]],
        "Bradley's marijuana patch was in a yard accessible from a house that did not belong to Bradley",
    )
    f20 = fact(
        "{bradley_s_marijuana_patch} was entirely hidden by foliage",
        [e["bradley_s_marijuana_patch"]],
        "false Bradley's marijuana patch was entirely hidden by foliage",
        truth=False,
    )
    f21_absent = AbsenceOfFactor(
        absent=fact(
            "{bradley_s_marijuana_patch} was covered by nontransparent material",
            [e["bradley_s_marijuana_patch"]],
            "Bradley's marijuana patch was covered by nontransparent material",
        )
    )
    f22 = fact(
        "the distance from which part of {bradley_s_marijuana_patch} could be seen plainly was",
        [e["bradley_s_marijuana_patch"]],
        "the distance from which part of Bradley's marijuana patch could be seen plainly was >= 1 foot",
        sign=">=",
        expression="1 foot",
    )
    f23 = fact(
        "the distance between {bradley_s_marijuana_patch} and {bradley_s_house} was",
        [e["bradley_s_marijuana_patch"], e["bradley_s_house"]],
        "the distance between Bradley's marijuana patch and Bradley's house was >= 20 feet",
        sign=">=",
        expression="20 feet",
    )
    f24 = fact(
        "a house that did not belong to {bradley} had access to the rear yard where {bradley_s_marijuana_patch} was located",
        [e["bradley"], e["bradley_s_marijuana_patch"]],
        "a house that did not belong to Bradley had access to the rear yard where Bradley's marijuana patch was located",
    )
    f25 = fact(
        "{bradley_s_marijuana_patch} was partially hidden by foliage",
        [e["bradley_s_marijuana_patch"]],
        "Bradley's marijuana patch was partially hidden by foliage",
    )
    f26 = fact(
        "{bradley_s_marijuana_patch} was in the fenced rear yard of {bradley_s_house}",
        [e["bradley_s_marijuana_patch"], e["bradley_s_house"]],
        "Bradley's marijuana patch was in the fenced rear yard of Bradley's house",
    )
    f27 = fact(
        "it was reasonable for {bradley} to exhibit an expectation of privacy in {bradley_s_marijuana_patch}",
        [e["bradley"], e["bradley_s_marijuana_patch"]],
        "false it was reasonable for Bradley to exhibit an expectation of privacy in Bradley's marijuana patch",
        truth=False,
    )

    base_enactments = EnactmentGroup(passages=[SEARCH_CLAUSE, DUE_PROCESS_CLAUSE])

    def rule(
        inputs: list,
        outputs: list,
        despite: list | None = None,
        universal: bool = False,
        mandatory: bool = True,
    ) -> Rule:
        return Rule(
            procedure=Procedure(inputs=inputs, outputs=outputs, despite=despite or []),
            enactments=copy.deepcopy(base_enactments),
            mandatory=mandatory,
            universal=universal,
        )

    holdings = [
        Holding(
            rule=rule(
                inputs=[f1, f2, f3, f4, f5, f6, f7, f8, f9, f10],
                outputs=[no_evidence_of_guilt],
                universal=True,
            )
        ),
        Holding(
            rule=rule(
                inputs=[f1, f2, f3, f4, f5, f7, f8, f9, f10],
                despite=[f12],
                outputs=[evidence_of_guilt],
                universal=True,
            ),
            rule_valid=False,
        ),
        Holding(
            rule=rule(
                inputs=[f1, f2, f3, f4, f5, f6, f8, f14, f10],
                despite=[f15],
                outputs=[evidence_of_guilt],
                universal=True,
            ),
            rule_valid=False,
        ),
        Holding(
            rule=rule(
                inputs=[f1, f2, f3, f4, f5, f6, f7, f9, f10],
                despite=[f16],
                outputs=[evidence_of_guilt],
                universal=True,
            ),
            rule_valid=False,
        ),
        Holding(
            rule=rule(
                inputs=[f1, f2, f3, f4, f5, f6, f7, f8, f10],
                despite=[f17],
                outputs=[evidence_of_guilt],
                universal=True,
            ),
            rule_valid=False,
        ),
        Holding(
            rule=rule(
                inputs=[f18, f19, f20, f21_absent, f22, f23, f24],
                despite=[f2, f3, f25, f26],
                outputs=[f12],
            )
        ),
        Holding(
            rule=rule(
                inputs=[f18, f19, f20, f21_absent, f22, f23, f24],
                despite=[f2, f3, f25, f26],
                outputs=[f27],
            )
        ),
    ]

    return HoldingGroup(holdings=holdings)


HOLDINGS = _build_holdings()


def anchored_holdings() -> AnchoredHoldings:
    """Build AnchoredHoldings for the Brad case from Python model data."""
    return AnchoredHoldings(
        holdings=[
            HoldingWithAnchors(holding=copy.deepcopy(holding)) for holding in HOLDINGS
        ],
        named_anchors=[],
        enactment_anchors=[],
    )
