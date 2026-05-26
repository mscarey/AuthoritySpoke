import copy
import datetime

from authorityspoke.holdings import HoldingGroup
from authorityspoke.opinions import AnchoredHoldings, HoldingWithAnchors

from typing import Any, cast

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

HOLDINGS = HoldingGroup(holdings=[])
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
        content="the probative value of ${officer_s_testimony_that_the_defendant_was_addicted_to_heroin}, in showing ${fact_that_the_defendant_committed_an_attempted_robbery}, was outweighed by unfair prejudice to ${the_defendant}"
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
        content="${officer_s_testimony_that_the_defendant_was_addicted_to_heroin} was relevant to show ${the_defendant} had a motive to commit an attempted robbery"
    ),
    terms=[_OFFICER_TESTIMONY, ENTITIES["the_defendant"]],
    name="officer's testimony that the defendant was addicted to heroin was relevant to show the defendant had a motive to commit an attempted robbery",
    generic=False,
)
_FACT_PROBATIVE_VALUE_TO_DEFENDANT = Fact(
    predicate=Predicate(
        content="the probative value of ${officer_s_testimony_that_the_defendant_was_addicted_to_heroin}, in showing ${fact_that_the_defendant_committed_an_attempted_robbery}, was outweighed by unfair prejudice to defendant"
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

HOLDINGS = HoldingGroup()


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


RAW_ANCHORED_HOLDINGS = {
    "holdings": [
        {
            "holding": {
                "generic": False,
                "rule": {
                    "generic": False,
                    "procedure": {
                        "outputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "the "
                                    "probative "
                                    "value of "
                                    "${officer_s_testimony_that_the_defendant_was_addicted_to_heroin}, "
                                    "in "
                                    "showing "
                                    "${fact_that_the_defendant_committed_an_attempted_robbery}, "
                                    "was "
                                    "outweighed "
                                    "by unfair "
                                    "prejudice "
                                    "to "
                                    "${the_defendant}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": False,
                                        "offered_by": {
                                            "generic": True,
                                            "name": "The People of California",
                                            "plural": False,
                                        },
                                        "form": "testimony",
                                        "statement": {
                                            "generic": False,
                                            "predicate": {
                                                "content": "${the_defendant} "
                                                "was "
                                                "addicted "
                                                "to "
                                                "heroin",
                                                "truth": True,
                                            },
                                            "terms": [
                                                {
                                                    "generic": True,
                                                    "name": "the defendant",
                                                    "plural": False,
                                                }
                                            ],
                                            "name": "fact "
                                            "that "
                                            "the "
                                            "defendant "
                                            "was "
                                            "addicted "
                                            "to "
                                            "heroin",
                                            "standard_of_proof": None,
                                        },
                                        "statement_attribution": {
                                            "generic": True,
                                            "name": "parole officer",
                                            "plural": False,
                                        },
                                        "name": "officer's "
                                        "testimony that "
                                        "the defendant "
                                        "was addicted to "
                                        "heroin",
                                    },
                                    {
                                        "generic": False,
                                        "predicate": {
                                            "content": "${the_defendant} "
                                            "committed "
                                            "an "
                                            "attempted "
                                            "robbery",
                                            "truth": True,
                                        },
                                        "terms": [
                                            {
                                                "generic": True,
                                                "name": "the defendant",
                                                "plural": False,
                                            }
                                        ],
                                        "name": "fact that the "
                                        "defendant "
                                        "committed an "
                                        "attempted "
                                        "robbery",
                                        "standard_of_proof": None,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the defendant",
                                        "plural": False,
                                    },
                                ],
                                "name": "the probative value of "
                                "officer's testimony that "
                                "the defendant was addicted "
                                "to heroin, in showing fact "
                                "that the defendant "
                                "committed an attempted "
                                "robbery, was outweighed by "
                                "unfair prejudice to the "
                                "defendant",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "offered_by": {
                                    "generic": True,
                                    "name": "The People of California",
                                    "plural": False,
                                },
                                "form": "testimony",
                                "statement": {
                                    "generic": False,
                                    "predicate": {
                                        "content": "${the_defendant} "
                                        "was "
                                        "addicted "
                                        "to "
                                        "heroin",
                                        "truth": True,
                                    },
                                    "terms": [
                                        {
                                            "generic": True,
                                            "name": "the defendant",
                                            "plural": False,
                                        }
                                    ],
                                    "name": "fact that the "
                                    "defendant was "
                                    "addicted to "
                                    "heroin",
                                    "standard_of_proof": None,
                                },
                                "statement_attribution": {
                                    "generic": True,
                                    "name": "parole officer",
                                    "plural": False,
                                },
                                "name": "officer's testimony that "
                                "the defendant was addicted "
                                "to heroin",
                            },
                            {
                                "generic": False,
                                "fact": {
                                    "generic": False,
                                    "predicate": {
                                        "content": "${the_defendant} "
                                        "committed "
                                        "an "
                                        "attempted "
                                        "robbery",
                                        "truth": True,
                                    },
                                    "terms": [
                                        {
                                            "generic": True,
                                            "name": "the defendant",
                                            "plural": False,
                                        }
                                    ],
                                    "name": "fact that the "
                                    "defendant "
                                    "committed an "
                                    "attempted robbery",
                                    "standard_of_proof": None,
                                },
                                "pleading": {
                                    "generic": False,
                                    "filer": {
                                        "generic": True,
                                        "name": "The People of California",
                                        "plural": False,
                                    },
                                    "name": "pleading filed "
                                    "by The People "
                                    "of California",
                                },
                                "name": "the attempted robbery charge",
                            },
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officer_s_testimony_that_the_defendant_was_addicted_to_heroin} "
                                    "was "
                                    "relevant "
                                    "to show "
                                    "${the_defendant} "
                                    "had a "
                                    "motive to "
                                    "commit an "
                                    "attempted "
                                    "robbery",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": False,
                                        "offered_by": {
                                            "generic": True,
                                            "name": "The People of California",
                                            "plural": False,
                                        },
                                        "form": "testimony",
                                        "statement": {
                                            "generic": False,
                                            "predicate": {
                                                "content": "${the_defendant} "
                                                "was "
                                                "addicted "
                                                "to "
                                                "heroin",
                                                "truth": True,
                                            },
                                            "terms": [
                                                {
                                                    "generic": True,
                                                    "name": "the defendant",
                                                    "plural": False,
                                                }
                                            ],
                                            "name": "fact "
                                            "that "
                                            "the "
                                            "defendant "
                                            "was "
                                            "addicted "
                                            "to "
                                            "heroin",
                                            "standard_of_proof": None,
                                        },
                                        "statement_attribution": {
                                            "generic": True,
                                            "name": "parole officer",
                                            "plural": False,
                                        },
                                        "name": "officer's "
                                        "testimony that "
                                        "the defendant "
                                        "was addicted to "
                                        "heroin",
                                    },
                                    {
                                        "generic": True,
                                        "name": "the defendant",
                                        "plural": False,
                                    },
                                ],
                                "name": "officer's testimony that "
                                "the defendant was addicted "
                                "to heroin was relevant to "
                                "show the defendant had a "
                                "motive to commit an "
                                "attempted robbery",
                                "standard_of_proof": None,
                            }
                        ],
                        "name": "",
                    },
                    "enactments": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us-ca/code/evid/s351",
                                    "start_date": datetime.date(1966, 1, 1),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Except "
                                        "as "
                                        "otherwise "
                                        "provided "
                                        "by "
                                        "statute, "
                                        "all "
                                        "relevant "
                                        "evidence "
                                        "is "
                                        "admissible.",
                                        "url": None,
                                        "id": None,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us-ca/code/evid/s351@1966-01-01",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [{"start": 0, "end": None}],
                                    "quotes": [],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us-ca/code/evid/s352",
                                    "start_date": datetime.date(1966, 1, 1),
                                    "heading": "",
                                    "text_version": {
                                        "content": "The "
                                        "court "
                                        "in "
                                        "its "
                                        "discretion "
                                        "may "
                                        "exclude "
                                        "evidence "
                                        "if "
                                        "its "
                                        "probative "
                                        "value "
                                        "is "
                                        "substantially "
                                        "outweighed "
                                        "by "
                                        "the "
                                        "probability "
                                        "that "
                                        "its "
                                        "admission "
                                        "will",
                                        "url": None,
                                        "id": None,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us-ca/code/evid/s352@1966-01-01",
                                    "children": [
                                        {
                                            "node": "/us-ca/code/evid/s352/a",
                                            "start_date": datetime.date(1966, 1, 1),
                                            "heading": "",
                                            "text_version": {
                                                "content": "necessitate "
                                                "undue "
                                                "consumption "
                                                "of "
                                                "time "
                                                "or",
                                                "url": None,
                                                "id": None,
                                            },
                                            "end_date": None,
                                            "first_published": None,
                                            "earliest_in_db": None,
                                            "anchors": [],
                                            "citations": [],
                                            "name": "",
                                            "children": [],
                                        },
                                        {
                                            "node": "/us-ca/code/evid/s352/b",
                                            "start_date": datetime.date(1966, 1, 1),
                                            "heading": "",
                                            "text_version": {
                                                "content": "create "
                                                "substantial "
                                                "danger "
                                                "of "
                                                "undue "
                                                "prejudice, "
                                                "of "
                                                "confusing "
                                                "the "
                                                "issues, "
                                                "or "
                                                "of "
                                                "misleading "
                                                "the "
                                                "jury.",
                                                "url": None,
                                                "id": None,
                                            },
                                            "end_date": None,
                                            "first_published": None,
                                            "earliest_in_db": None,
                                            "anchors": [],
                                            "citations": [],
                                            "name": "",
                                            "children": [],
                                        },
                                    ],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "",
                                            "prefix": "",
                                            "suffix": "necessitate undue",
                                        },
                                        {
                                            "exact": "create "
                                            "substantial "
                                            "danger "
                                            "of "
                                            "undue "
                                            "prejudice",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                    ],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us-ca/code/pen/s211",
                                    "start_date": datetime.date(1873, 1, 1),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Robbery "
                                        "is "
                                        "the "
                                        "felonious "
                                        "taking "
                                        "of "
                                        "personal "
                                        "property "
                                        "in "
                                        "the "
                                        "possession "
                                        "of "
                                        "another, "
                                        "from "
                                        "his "
                                        "person "
                                        "or "
                                        "immediate "
                                        "presence, "
                                        "and "
                                        "against "
                                        "his "
                                        "will, "
                                        "accomplished "
                                        "by "
                                        "means "
                                        "of "
                                        "force "
                                        "or "
                                        "fear.",
                                        "url": None,
                                        "id": None,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us-ca/code/pen/s211@1873-01-01",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [{"start": 0, "end": None}],
                                    "quotes": [],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us-ca/code/pen/s664",
                                    "start_date": datetime.date(2011, 4, 4),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Every "
                                        "person "
                                        "who "
                                        "attempts "
                                        "to "
                                        "commit "
                                        "any "
                                        "crime, "
                                        "but "
                                        "fails, "
                                        "or "
                                        "is "
                                        "prevented "
                                        "or "
                                        "intercepted "
                                        "in "
                                        "its "
                                        "perpetration, "
                                        "shall "
                                        "be "
                                        "punished "
                                        "where "
                                        "no "
                                        "provision "
                                        "is "
                                        "made "
                                        "by "
                                        "law "
                                        "for "
                                        "the "
                                        "punishment "
                                        "of "
                                        "those "
                                        "attempts, "
                                        "[text "
                                        "omitted]",
                                        "url": None,
                                        "id": None,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us-ca/code/pen/s664@2011-04-04",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "",
                                            "prefix": "",
                                            "suffix": "where no provision is",
                                        }
                                    ],
                                },
                            },
                        ]
                    },
                    "enactments_despite": {"passages": []},
                    "mandatory": True,
                    "universal": False,
                    "name": None,
                },
                "rule_valid": True,
                "decided": True,
                "exclusive": False,
            },
            "anchors": {"positions": [], "quotes": []},
        },
        {
            "holding": {
                "generic": False,
                "rule": {
                    "generic": False,
                    "procedure": {
                        "outputs": [
                            {
                                "generic": False,
                                "absent": {
                                    "generic": False,
                                    "exhibit": {
                                        "generic": False,
                                        "offered_by": {
                                            "generic": True,
                                            "name": "The People of California",
                                            "plural": False,
                                        },
                                        "form": "testimony",
                                        "statement": {
                                            "generic": False,
                                            "predicate": {
                                                "content": "${the_defendant} "
                                                "was "
                                                "addicted "
                                                "to "
                                                "heroin",
                                                "truth": True,
                                            },
                                            "terms": [
                                                {
                                                    "generic": True,
                                                    "name": "the defendant",
                                                    "plural": False,
                                                }
                                            ],
                                            "name": "fact "
                                            "that "
                                            "the "
                                            "defendant "
                                            "was "
                                            "addicted "
                                            "to "
                                            "heroin",
                                            "standard_of_proof": None,
                                        },
                                        "statement_attribution": {
                                            "generic": True,
                                            "name": "parole officer",
                                            "plural": False,
                                        },
                                        "name": "officer's "
                                        "testimony "
                                        "that "
                                        "the "
                                        "defendant "
                                        "was "
                                        "addicted "
                                        "to "
                                        "heroin",
                                    },
                                    "to_effect": {
                                        "generic": False,
                                        "predicate": {
                                            "content": "${the_defendant} "
                                            "committed "
                                            "an "
                                            "attempted "
                                            "robbery",
                                            "truth": True,
                                        },
                                        "terms": [
                                            {
                                                "generic": True,
                                                "name": "the defendant",
                                                "plural": False,
                                            }
                                        ],
                                        "name": "fact "
                                        "that "
                                        "the "
                                        "defendant "
                                        "committed "
                                        "an "
                                        "attempted "
                                        "robbery",
                                        "standard_of_proof": None,
                                    },
                                    "name": "evidence of "
                                    "officer's "
                                    "testimony that "
                                    "the defendant "
                                    "was addicted to "
                                    "heroin",
                                },
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "the "
                                    "probative "
                                    "value of "
                                    "${officer_s_testimony_that_the_defendant_was_addicted_to_heroin}, "
                                    "in showing "
                                    "${fact_that_the_defendant_committed_an_attempted_robbery}, "
                                    "was "
                                    "outweighed "
                                    "by unfair "
                                    "prejudice "
                                    "to "
                                    "defendant",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": False,
                                        "offered_by": {
                                            "generic": True,
                                            "name": "The People of California",
                                            "plural": False,
                                        },
                                        "form": "testimony",
                                        "statement": {
                                            "generic": False,
                                            "predicate": {
                                                "content": "${the_defendant} "
                                                "was "
                                                "addicted "
                                                "to "
                                                "heroin",
                                                "truth": True,
                                            },
                                            "terms": [
                                                {
                                                    "generic": True,
                                                    "name": "the defendant",
                                                    "plural": False,
                                                }
                                            ],
                                            "name": "fact "
                                            "that "
                                            "the "
                                            "defendant "
                                            "was "
                                            "addicted "
                                            "to "
                                            "heroin",
                                            "standard_of_proof": None,
                                        },
                                        "statement_attribution": {
                                            "generic": True,
                                            "name": "parole officer",
                                            "plural": False,
                                        },
                                        "name": "officer's "
                                        "testimony that "
                                        "the defendant "
                                        "was addicted to "
                                        "heroin",
                                    },
                                    {
                                        "generic": False,
                                        "predicate": {
                                            "content": "${the_defendant} "
                                            "committed "
                                            "an "
                                            "attempted "
                                            "robbery",
                                            "truth": True,
                                        },
                                        "terms": [
                                            {
                                                "generic": True,
                                                "name": "the defendant",
                                                "plural": False,
                                            }
                                        ],
                                        "name": "fact that the "
                                        "defendant "
                                        "committed an "
                                        "attempted "
                                        "robbery",
                                        "standard_of_proof": None,
                                    },
                                ],
                                "name": "the probative value of "
                                "officer's testimony that "
                                "the defendant was addicted "
                                "to heroin, in showing fact "
                                "that the defendant "
                                "committed an attempted "
                                "robbery, was outweighed by "
                                "unfair prejudice to "
                                "defendant",
                                "standard_of_proof": None,
                            }
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officer_s_testimony_that_the_defendant_was_addicted_to_heroin} "
                                    "was "
                                    "relevant "
                                    "to show "
                                    "${the_defendant} "
                                    "had a "
                                    "motive to "
                                    "commit an "
                                    "attempted "
                                    "robbery",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": False,
                                        "offered_by": {
                                            "generic": True,
                                            "name": "The People of California",
                                            "plural": False,
                                        },
                                        "form": "testimony",
                                        "statement": {
                                            "generic": False,
                                            "predicate": {
                                                "content": "${the_defendant} "
                                                "was "
                                                "addicted "
                                                "to "
                                                "heroin",
                                                "truth": True,
                                            },
                                            "terms": [
                                                {
                                                    "generic": True,
                                                    "name": "the defendant",
                                                    "plural": False,
                                                }
                                            ],
                                            "name": "fact "
                                            "that "
                                            "the "
                                            "defendant "
                                            "was "
                                            "addicted "
                                            "to "
                                            "heroin",
                                            "standard_of_proof": None,
                                        },
                                        "statement_attribution": {
                                            "generic": True,
                                            "name": "parole officer",
                                            "plural": False,
                                        },
                                        "name": "officer's "
                                        "testimony that "
                                        "the defendant "
                                        "was addicted to "
                                        "heroin",
                                    },
                                    {
                                        "generic": True,
                                        "name": "the defendant",
                                        "plural": False,
                                    },
                                ],
                                "name": "officer's testimony that "
                                "the defendant was addicted "
                                "to heroin was relevant to "
                                "show the defendant had a "
                                "motive to commit an "
                                "attempted robbery",
                                "standard_of_proof": None,
                            }
                        ],
                        "name": "",
                    },
                    "enactments": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us-ca/code/evid/s351",
                                    "start_date": datetime.date(1966, 1, 1),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Except "
                                        "as "
                                        "otherwise "
                                        "provided "
                                        "by "
                                        "statute, "
                                        "all "
                                        "relevant "
                                        "evidence "
                                        "is "
                                        "admissible.",
                                        "url": None,
                                        "id": None,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us-ca/code/evid/s351@1966-01-01",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [{"start": 0, "end": None}],
                                    "quotes": [],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us-ca/code/evid/s352",
                                    "start_date": datetime.date(1966, 1, 1),
                                    "heading": "",
                                    "text_version": {
                                        "content": "The "
                                        "court "
                                        "in "
                                        "its "
                                        "discretion "
                                        "may "
                                        "exclude "
                                        "evidence "
                                        "if "
                                        "its "
                                        "probative "
                                        "value "
                                        "is "
                                        "substantially "
                                        "outweighed "
                                        "by "
                                        "the "
                                        "probability "
                                        "that "
                                        "its "
                                        "admission "
                                        "will",
                                        "url": None,
                                        "id": None,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us-ca/code/evid/s352@1966-01-01",
                                    "children": [
                                        {
                                            "node": "/us-ca/code/evid/s352/a",
                                            "start_date": datetime.date(1966, 1, 1),
                                            "heading": "",
                                            "text_version": {
                                                "content": "necessitate "
                                                "undue "
                                                "consumption "
                                                "of "
                                                "time "
                                                "or",
                                                "url": None,
                                                "id": None,
                                            },
                                            "end_date": None,
                                            "first_published": None,
                                            "earliest_in_db": None,
                                            "anchors": [],
                                            "citations": [],
                                            "name": "",
                                            "children": [],
                                        },
                                        {
                                            "node": "/us-ca/code/evid/s352/b",
                                            "start_date": datetime.date(1966, 1, 1),
                                            "heading": "",
                                            "text_version": {
                                                "content": "create "
                                                "substantial "
                                                "danger "
                                                "of "
                                                "undue "
                                                "prejudice, "
                                                "of "
                                                "confusing "
                                                "the "
                                                "issues, "
                                                "or "
                                                "of "
                                                "misleading "
                                                "the "
                                                "jury.",
                                                "url": None,
                                                "id": None,
                                            },
                                            "end_date": None,
                                            "first_published": None,
                                            "earliest_in_db": None,
                                            "anchors": [],
                                            "citations": [],
                                            "name": "",
                                            "children": [],
                                        },
                                    ],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "",
                                            "prefix": "",
                                            "suffix": "necessitate undue",
                                        },
                                        {
                                            "exact": "create "
                                            "substantial "
                                            "danger "
                                            "of "
                                            "undue "
                                            "prejudice",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                    ],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us-ca/code/pen/s211",
                                    "start_date": datetime.date(1873, 1, 1),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Robbery "
                                        "is "
                                        "the "
                                        "felonious "
                                        "taking "
                                        "of "
                                        "personal "
                                        "property "
                                        "in "
                                        "the "
                                        "possession "
                                        "of "
                                        "another, "
                                        "from "
                                        "his "
                                        "person "
                                        "or "
                                        "immediate "
                                        "presence, "
                                        "and "
                                        "against "
                                        "his "
                                        "will, "
                                        "accomplished "
                                        "by "
                                        "means "
                                        "of "
                                        "force "
                                        "or "
                                        "fear.",
                                        "url": None,
                                        "id": None,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us-ca/code/pen/s211@1873-01-01",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [{"start": 0, "end": None}],
                                    "quotes": [],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us-ca/code/pen/s664",
                                    "start_date": datetime.date(2011, 4, 4),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Every "
                                        "person "
                                        "who "
                                        "attempts "
                                        "to "
                                        "commit "
                                        "any "
                                        "crime, "
                                        "but "
                                        "fails, "
                                        "or "
                                        "is "
                                        "prevented "
                                        "or "
                                        "intercepted "
                                        "in "
                                        "its "
                                        "perpetration, "
                                        "shall "
                                        "be "
                                        "punished "
                                        "where "
                                        "no "
                                        "provision "
                                        "is "
                                        "made "
                                        "by "
                                        "law "
                                        "for "
                                        "the "
                                        "punishment "
                                        "of "
                                        "those "
                                        "attempts, "
                                        "[text "
                                        "omitted]",
                                        "url": None,
                                        "id": None,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us-ca/code/pen/s664@2011-04-04",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "",
                                            "prefix": "",
                                            "suffix": "where no provision is",
                                        }
                                    ],
                                },
                            },
                        ]
                    },
                    "enactments_despite": {"passages": []},
                    "mandatory": True,
                    "universal": False,
                    "name": None,
                },
                "rule_valid": True,
                "decided": True,
                "exclusive": False,
            },
            "anchors": {"positions": [], "quotes": []},
        },
    ],
    "named_anchors": [],
    "enactment_anchors": [],
}


HOLDINGS = _build_holdings()


def anchored_holdings() -> AnchoredHoldings:
    """Build AnchoredHoldings from this module's HOLDINGS collection."""
    parsed = AnchoredHoldings.model_validate(copy.deepcopy(RAW_ANCHORED_HOLDINGS))
    return AnchoredHoldings(
        holdings=[
            HoldingWithAnchors(
                holding=copy.deepcopy(holding),
                anchors=copy.deepcopy(parsed.holdings[index].anchors),
            )
            for index, holding in enumerate(HOLDINGS)
        ],
        named_anchors=copy.deepcopy(parsed.named_anchors),
        enactment_anchors=copy.deepcopy(parsed.enactment_anchors),
    )
