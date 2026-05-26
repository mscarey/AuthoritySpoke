import copy
import datetime
from decimal import Decimal
from typing import Any, cast

from authorityspoke.holdings import HoldingGroup
from authorityspoke.opinions import AnchoredHoldings
from authorityspoke import Entity, Fact, Holding, Predicate, Rule
from authorityspoke.facts import AbsenceOfFactor, Evidence, Exhibit
from authorityspoke.procedures import Procedure

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

HOLDINGS = HoldingGroup(holdings=[])

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
                                "absent": {
                                    "generic": False,
                                    "exhibit": {
                                        "generic": True,
                                        "offered_by": {
                                            "generic": True,
                                            "name": "the prosecution",
                                            "plural": False,
                                        },
                                        "form": None,
                                        "statement": None,
                                        "statement_attribution": None,
                                        "name": "proof of Bradley's guilt",
                                    },
                                    "to_effect": {
                                        "generic": False,
                                        "predicate": {
                                            "content": "Bradley committed a crime",
                                            "truth": True,
                                        },
                                        "terms": [],
                                        "name": "fact that Bradley committed a crime",
                                        "standard_of_proof": None,
                                    },
                                    "name": "absence of evidence of Bradley's guilt",
                                },
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "was a "
                                    "warrantless "
                                    "search and "
                                    "seizure",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    }
                                ],
                                "name": "officers' search of the "
                                "yard was a warrantless "
                                "search and seizure",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley_s_house} was a house",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    }
                                ],
                                "name": "Bradley's house was a house",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley} lived at ${bradley_s_house}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    },
                                ],
                                "name": "Bradley lived at Bradley's house",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "was "
                                    "performed "
                                    "by law "
                                    "enforcement "
                                    "officers",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    }
                                ],
                                "name": "officers' search of the "
                                "yard was performed by law "
                                "enforcement officers",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "was "
                                    "performed "
                                    "in the "
                                    "grounds "
                                    "around "
                                    "${bradley_s_house}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    },
                                ],
                                "name": "officers' search of the "
                                "yard was performed in the "
                                "grounds around Bradley's "
                                "house",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley} "
                                    "exhibited "
                                    "an "
                                    "expectation "
                                    "of privacy "
                                    "in "
                                    "${bradley_s_marijuana_patch}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "Bradley exhibited an "
                                "expectation of privacy in "
                                "Bradley's marijuana patch",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "it was "
                                    "reasonable "
                                    "for "
                                    "${bradley} "
                                    "to hold an "
                                    "expectation "
                                    "of privacy "
                                    "in "
                                    "${bradley_s_marijuana_patch}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "it was reasonable for "
                                "Bradley to hold an "
                                "expectation of privacy in "
                                "Bradley's marijuana patch",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "violated "
                                    "${bradley}'s "
                                    "expectation "
                                    "of privacy "
                                    "in "
                                    "${bradley_s_marijuana_patch}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "officers' search of the "
                                "yard violated Bradley's "
                                "expectation of privacy in "
                                "Bradley's marijuana patch",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "was an "
                                    "unreasonable "
                                    "governmental "
                                    "intrusion "
                                    "upon "
                                    "${bradley_s_marijuana_patch}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "officers' search of the "
                                "yard was an unreasonable "
                                "governmental intrusion upon "
                                "Bradley's marijuana patch",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${proof_of_bradley_s_guilt} "
                                    "was "
                                    "derived "
                                    "from "
                                    "${officers_search_of_the_yard}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "offered_by": {
                                            "generic": True,
                                            "name": "the prosecution",
                                            "plural": False,
                                        },
                                        "form": None,
                                        "statement": None,
                                        "statement_attribution": None,
                                        "name": "proof of Bradley's guilt",
                                    },
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    },
                                ],
                                "name": "proof of Bradley's guilt "
                                "was derived from officers' "
                                "search of the yard",
                                "standard_of_proof": None,
                            },
                        ],
                        "despite": [],
                        "name": "",
                    },
                    "enactments": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/const/amendment/IV",
                                    "start_date": datetime.date(1791, 12, 15),
                                    "heading": "AMENDMENT IV.",
                                    "text_version": {
                                        "content": "The "
                                        "right "
                                        "of "
                                        "the "
                                        "people "
                                        "to "
                                        "be "
                                        "secure "
                                        "in "
                                        "their "
                                        "persons, "
                                        "houses, "
                                        "papers, "
                                        "and "
                                        "effects, "
                                        "against "
                                        "unreasonable "
                                        "searches "
                                        "and "
                                        "seizures, "
                                        "shall "
                                        "not "
                                        "be "
                                        "violated, "
                                        "and "
                                        "no "
                                        "Warrants "
                                        "shall "
                                        "issue, "
                                        "but "
                                        "upon "
                                        "probable "
                                        "cause, "
                                        "supported "
                                        "by "
                                        "Oath "
                                        "or "
                                        "affirmation, "
                                        "and "
                                        "particularly "
                                        "describing "
                                        "the "
                                        "place "
                                        "to "
                                        "be "
                                        "searched, "
                                        "and "
                                        "the "
                                        "persons "
                                        "or "
                                        "things "
                                        "to "
                                        "be "
                                        "seized.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735706/",
                                        "id": 735706,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/amendment/IV",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "",
                                            "prefix": "",
                                            "suffix": ", and no Warrants shall issue",
                                        }
                                    ],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us/const/amendment/XIV/1",
                                    "start_date": datetime.date(1868, 7, 28),
                                    "heading": "Citizenship: "
                                    "security "
                                    "and "
                                    "equal "
                                    "protection "
                                    "of "
                                    "citizens.",
                                    "text_version": {
                                        "content": "All "
                                        "persons "
                                        "born "
                                        "or "
                                        "naturalized "
                                        "in "
                                        "the "
                                        "United "
                                        "States, "
                                        "and "
                                        "subject "
                                        "to "
                                        "the "
                                        "jurisdiction "
                                        "thereof, "
                                        "are "
                                        "citizens "
                                        "of "
                                        "the "
                                        "United "
                                        "States "
                                        "and "
                                        "of "
                                        "the "
                                        "State "
                                        "wherein "
                                        "they "
                                        "reside. "
                                        "No "
                                        "State "
                                        "shall "
                                        "make "
                                        "or "
                                        "enforce "
                                        "any "
                                        "law "
                                        "which "
                                        "shall "
                                        "abridge "
                                        "the "
                                        "privileges "
                                        "or "
                                        "immunities "
                                        "of "
                                        "citizens "
                                        "of "
                                        "the "
                                        "United "
                                        "States; "
                                        "nor "
                                        "shall "
                                        "any "
                                        "State "
                                        "deprive "
                                        "any "
                                        "person "
                                        "of "
                                        "life, "
                                        "liberty, "
                                        "or "
                                        "property, "
                                        "without "
                                        "due "
                                        "process "
                                        "of "
                                        "law; "
                                        "nor "
                                        "deny "
                                        "to "
                                        "any "
                                        "person "
                                        "within "
                                        "its "
                                        "jurisdiction "
                                        "the "
                                        "equal "
                                        "protection "
                                        "of "
                                        "the "
                                        "laws.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735717/",
                                        "id": 735717,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/amendment/XIV/1",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "",
                                            "prefix": "immunities "
                                            "of "
                                            "citizens "
                                            "of "
                                            "the "
                                            "United "
                                            "States; ",
                                            "suffix": " nor deny to any person",
                                        }
                                    ],
                                },
                            },
                        ]
                    },
                    "enactments_despite": {"passages": []},
                    "mandatory": True,
                    "universal": True,
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
                                "exhibit": {
                                    "generic": True,
                                    "offered_by": {
                                        "generic": True,
                                        "name": "the prosecution",
                                        "plural": False,
                                    },
                                    "form": None,
                                    "statement": None,
                                    "statement_attribution": None,
                                    "name": "proof of Bradley's guilt",
                                },
                                "to_effect": {
                                    "generic": False,
                                    "predicate": {
                                        "content": "Bradley committed a crime",
                                        "truth": True,
                                    },
                                    "terms": [],
                                    "name": "fact that Bradley committed a crime",
                                    "standard_of_proof": None,
                                },
                                "name": "absence of evidence of Bradley's guilt",
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "was a "
                                    "warrantless "
                                    "search and "
                                    "seizure",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    }
                                ],
                                "name": "officers' search of the "
                                "yard was a warrantless "
                                "search and seizure",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley_s_house} was a house",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    }
                                ],
                                "name": "Bradley's house was a house",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley} lived at ${bradley_s_house}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    },
                                ],
                                "name": "Bradley lived at Bradley's house",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "was "
                                    "performed "
                                    "by law "
                                    "enforcement "
                                    "officers",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    }
                                ],
                                "name": "officers' search of the "
                                "yard was performed by law "
                                "enforcement officers",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "was "
                                    "performed "
                                    "in the "
                                    "grounds "
                                    "around "
                                    "${bradley_s_house}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    },
                                ],
                                "name": "officers' search of the "
                                "yard was performed in the "
                                "grounds around Bradley's "
                                "house",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "it was "
                                    "reasonable "
                                    "for "
                                    "${bradley} "
                                    "to hold an "
                                    "expectation "
                                    "of privacy "
                                    "in "
                                    "${bradley_s_marijuana_patch}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "it was reasonable for "
                                "Bradley to hold an "
                                "expectation of privacy in "
                                "Bradley's marijuana patch",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "violated "
                                    "${bradley}'s "
                                    "expectation "
                                    "of privacy "
                                    "in "
                                    "${bradley_s_marijuana_patch}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "officers' search of the "
                                "yard violated Bradley's "
                                "expectation of privacy in "
                                "Bradley's marijuana patch",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "was an "
                                    "unreasonable "
                                    "governmental "
                                    "intrusion "
                                    "upon "
                                    "${bradley_s_marijuana_patch}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "officers' search of the "
                                "yard was an unreasonable "
                                "governmental intrusion upon "
                                "Bradley's marijuana patch",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${proof_of_bradley_s_guilt} "
                                    "was "
                                    "derived "
                                    "from "
                                    "${officers_search_of_the_yard}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "offered_by": {
                                            "generic": True,
                                            "name": "the prosecution",
                                            "plural": False,
                                        },
                                        "form": None,
                                        "statement": None,
                                        "statement_attribution": None,
                                        "name": "proof of Bradley's guilt",
                                    },
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    },
                                ],
                                "name": "proof of Bradley's guilt "
                                "was derived from officers' "
                                "search of the yard",
                                "standard_of_proof": None,
                            },
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley} "
                                    "exhibited "
                                    "an "
                                    "expectation "
                                    "of "
                                    "privacy "
                                    "in "
                                    "${bradley_s_marijuana_patch}",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "false Bradley exhibited an "
                                "expectation of privacy in "
                                "Bradley's marijuana patch",
                                "standard_of_proof": None,
                            }
                        ],
                        "name": "",
                    },
                    "enactments": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/const/amendment/IV",
                                    "start_date": datetime.date(1791, 12, 15),
                                    "heading": "AMENDMENT IV.",
                                    "text_version": {
                                        "content": "The "
                                        "right "
                                        "of "
                                        "the "
                                        "people "
                                        "to "
                                        "be "
                                        "secure "
                                        "in "
                                        "their "
                                        "persons, "
                                        "houses, "
                                        "papers, "
                                        "and "
                                        "effects, "
                                        "against "
                                        "unreasonable "
                                        "searches "
                                        "and "
                                        "seizures, "
                                        "shall "
                                        "not "
                                        "be "
                                        "violated, "
                                        "and "
                                        "no "
                                        "Warrants "
                                        "shall "
                                        "issue, "
                                        "but "
                                        "upon "
                                        "probable "
                                        "cause, "
                                        "supported "
                                        "by "
                                        "Oath "
                                        "or "
                                        "affirmation, "
                                        "and "
                                        "particularly "
                                        "describing "
                                        "the "
                                        "place "
                                        "to "
                                        "be "
                                        "searched, "
                                        "and "
                                        "the "
                                        "persons "
                                        "or "
                                        "things "
                                        "to "
                                        "be "
                                        "seized.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735706/",
                                        "id": 735706,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/amendment/IV",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "",
                                            "prefix": "",
                                            "suffix": ", and no Warrants shall issue",
                                        }
                                    ],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us/const/amendment/XIV/1",
                                    "start_date": datetime.date(1868, 7, 28),
                                    "heading": "Citizenship: "
                                    "security "
                                    "and "
                                    "equal "
                                    "protection "
                                    "of "
                                    "citizens.",
                                    "text_version": {
                                        "content": "All "
                                        "persons "
                                        "born "
                                        "or "
                                        "naturalized "
                                        "in "
                                        "the "
                                        "United "
                                        "States, "
                                        "and "
                                        "subject "
                                        "to "
                                        "the "
                                        "jurisdiction "
                                        "thereof, "
                                        "are "
                                        "citizens "
                                        "of "
                                        "the "
                                        "United "
                                        "States "
                                        "and "
                                        "of "
                                        "the "
                                        "State "
                                        "wherein "
                                        "they "
                                        "reside. "
                                        "No "
                                        "State "
                                        "shall "
                                        "make "
                                        "or "
                                        "enforce "
                                        "any "
                                        "law "
                                        "which "
                                        "shall "
                                        "abridge "
                                        "the "
                                        "privileges "
                                        "or "
                                        "immunities "
                                        "of "
                                        "citizens "
                                        "of "
                                        "the "
                                        "United "
                                        "States; "
                                        "nor "
                                        "shall "
                                        "any "
                                        "State "
                                        "deprive "
                                        "any "
                                        "person "
                                        "of "
                                        "life, "
                                        "liberty, "
                                        "or "
                                        "property, "
                                        "without "
                                        "due "
                                        "process "
                                        "of "
                                        "law; "
                                        "nor "
                                        "deny "
                                        "to "
                                        "any "
                                        "person "
                                        "within "
                                        "its "
                                        "jurisdiction "
                                        "the "
                                        "equal "
                                        "protection "
                                        "of "
                                        "the "
                                        "laws.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735717/",
                                        "id": 735717,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/amendment/XIV/1",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "",
                                            "prefix": "immunities "
                                            "of "
                                            "citizens "
                                            "of "
                                            "the "
                                            "United "
                                            "States; ",
                                            "suffix": " nor deny to any person",
                                        }
                                    ],
                                },
                            },
                        ]
                    },
                    "enactments_despite": {"passages": []},
                    "mandatory": True,
                    "universal": True,
                    "name": None,
                },
                "rule_valid": False,
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
                                "exhibit": {
                                    "generic": True,
                                    "offered_by": {
                                        "generic": True,
                                        "name": "the prosecution",
                                        "plural": False,
                                    },
                                    "form": None,
                                    "statement": None,
                                    "statement_attribution": None,
                                    "name": "proof of Bradley's guilt",
                                },
                                "to_effect": {
                                    "generic": False,
                                    "predicate": {
                                        "content": "Bradley committed a crime",
                                        "truth": True,
                                    },
                                    "terms": [],
                                    "name": "fact that Bradley committed a crime",
                                    "standard_of_proof": None,
                                },
                                "name": "absence of evidence of Bradley's guilt",
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "was a "
                                    "warrantless "
                                    "search and "
                                    "seizure",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    }
                                ],
                                "name": "officers' search of the "
                                "yard was a warrantless "
                                "search and seizure",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley_s_house} was a house",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    }
                                ],
                                "name": "Bradley's house was a house",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley} lived at ${bradley_s_house}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    },
                                ],
                                "name": "Bradley lived at Bradley's house",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "was "
                                    "performed "
                                    "by law "
                                    "enforcement "
                                    "officers",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    }
                                ],
                                "name": "officers' search of the "
                                "yard was performed by law "
                                "enforcement officers",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "was "
                                    "performed "
                                    "in the "
                                    "grounds "
                                    "around "
                                    "${bradley_s_house}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    },
                                ],
                                "name": "officers' search of the "
                                "yard was performed in the "
                                "grounds around Bradley's "
                                "house",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley} "
                                    "exhibited "
                                    "an "
                                    "expectation "
                                    "of privacy "
                                    "in "
                                    "${bradley_s_marijuana_patch}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "Bradley exhibited an "
                                "expectation of privacy in "
                                "Bradley's marijuana patch",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "violated "
                                    "${bradley}'s "
                                    "expectation "
                                    "of privacy "
                                    "in "
                                    "${bradley_s_marijuana_patch}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "officers' search of the "
                                "yard violated Bradley's "
                                "expectation of privacy in "
                                "Bradley's marijuana patch",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "was an "
                                    "unreasonable "
                                    "intrusion "
                                    "upon "
                                    "${bradley_s_marijuana_patch}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "officers' search of the "
                                "yard was an unreasonable "
                                "intrusion upon Bradley's "
                                "marijuana patch",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${proof_of_bradley_s_guilt} "
                                    "was "
                                    "derived "
                                    "from "
                                    "${officers_search_of_the_yard}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "offered_by": {
                                            "generic": True,
                                            "name": "the prosecution",
                                            "plural": False,
                                        },
                                        "form": None,
                                        "statement": None,
                                        "statement_attribution": None,
                                        "name": "proof of Bradley's guilt",
                                    },
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    },
                                ],
                                "name": "proof of Bradley's guilt "
                                "was derived from officers' "
                                "search of the yard",
                                "standard_of_proof": None,
                            },
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "it was "
                                    "reasonable "
                                    "for "
                                    "${bradley} "
                                    "to hold "
                                    "an "
                                    "expectation "
                                    "of "
                                    "privacy "
                                    "in "
                                    "${bradley_s_marijuana_patch}",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "false it was reasonable "
                                "for Bradley to hold an "
                                "expectation of privacy in "
                                "Bradley's marijuana patch",
                                "standard_of_proof": None,
                            }
                        ],
                        "name": "",
                    },
                    "enactments": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/const/amendment/IV",
                                    "start_date": datetime.date(1791, 12, 15),
                                    "heading": "AMENDMENT IV.",
                                    "text_version": {
                                        "content": "The "
                                        "right "
                                        "of "
                                        "the "
                                        "people "
                                        "to "
                                        "be "
                                        "secure "
                                        "in "
                                        "their "
                                        "persons, "
                                        "houses, "
                                        "papers, "
                                        "and "
                                        "effects, "
                                        "against "
                                        "unreasonable "
                                        "searches "
                                        "and "
                                        "seizures, "
                                        "shall "
                                        "not "
                                        "be "
                                        "violated, "
                                        "and "
                                        "no "
                                        "Warrants "
                                        "shall "
                                        "issue, "
                                        "but "
                                        "upon "
                                        "probable "
                                        "cause, "
                                        "supported "
                                        "by "
                                        "Oath "
                                        "or "
                                        "affirmation, "
                                        "and "
                                        "particularly "
                                        "describing "
                                        "the "
                                        "place "
                                        "to "
                                        "be "
                                        "searched, "
                                        "and "
                                        "the "
                                        "persons "
                                        "or "
                                        "things "
                                        "to "
                                        "be "
                                        "seized.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735706/",
                                        "id": 735706,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/amendment/IV",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "",
                                            "prefix": "",
                                            "suffix": ", and no Warrants shall issue",
                                        }
                                    ],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us/const/amendment/XIV/1",
                                    "start_date": datetime.date(1868, 7, 28),
                                    "heading": "Citizenship: "
                                    "security "
                                    "and "
                                    "equal "
                                    "protection "
                                    "of "
                                    "citizens.",
                                    "text_version": {
                                        "content": "All "
                                        "persons "
                                        "born "
                                        "or "
                                        "naturalized "
                                        "in "
                                        "the "
                                        "United "
                                        "States, "
                                        "and "
                                        "subject "
                                        "to "
                                        "the "
                                        "jurisdiction "
                                        "thereof, "
                                        "are "
                                        "citizens "
                                        "of "
                                        "the "
                                        "United "
                                        "States "
                                        "and "
                                        "of "
                                        "the "
                                        "State "
                                        "wherein "
                                        "they "
                                        "reside. "
                                        "No "
                                        "State "
                                        "shall "
                                        "make "
                                        "or "
                                        "enforce "
                                        "any "
                                        "law "
                                        "which "
                                        "shall "
                                        "abridge "
                                        "the "
                                        "privileges "
                                        "or "
                                        "immunities "
                                        "of "
                                        "citizens "
                                        "of "
                                        "the "
                                        "United "
                                        "States; "
                                        "nor "
                                        "shall "
                                        "any "
                                        "State "
                                        "deprive "
                                        "any "
                                        "person "
                                        "of "
                                        "life, "
                                        "liberty, "
                                        "or "
                                        "property, "
                                        "without "
                                        "due "
                                        "process "
                                        "of "
                                        "law; "
                                        "nor "
                                        "deny "
                                        "to "
                                        "any "
                                        "person "
                                        "within "
                                        "its "
                                        "jurisdiction "
                                        "the "
                                        "equal "
                                        "protection "
                                        "of "
                                        "the "
                                        "laws.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735717/",
                                        "id": 735717,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/amendment/XIV/1",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "",
                                            "prefix": "immunities "
                                            "of "
                                            "citizens "
                                            "of "
                                            "the "
                                            "United "
                                            "States; ",
                                            "suffix": " nor deny to any person",
                                        }
                                    ],
                                },
                            },
                        ]
                    },
                    "enactments_despite": {"passages": []},
                    "mandatory": True,
                    "universal": True,
                    "name": None,
                },
                "rule_valid": False,
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
                                "exhibit": {
                                    "generic": True,
                                    "offered_by": {
                                        "generic": True,
                                        "name": "the prosecution",
                                        "plural": False,
                                    },
                                    "form": None,
                                    "statement": None,
                                    "statement_attribution": None,
                                    "name": "proof of Bradley's guilt",
                                },
                                "to_effect": {
                                    "generic": False,
                                    "predicate": {
                                        "content": "Bradley committed a crime",
                                        "truth": True,
                                    },
                                    "terms": [],
                                    "name": "fact that Bradley committed a crime",
                                    "standard_of_proof": None,
                                },
                                "name": "absence of evidence of Bradley's guilt",
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "was a "
                                    "warrantless "
                                    "search and "
                                    "seizure",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    }
                                ],
                                "name": "officers' search of the "
                                "yard was a warrantless "
                                "search and seizure",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley_s_house} was a house",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    }
                                ],
                                "name": "Bradley's house was a house",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley} lived at ${bradley_s_house}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    },
                                ],
                                "name": "Bradley lived at Bradley's house",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "was "
                                    "performed "
                                    "by law "
                                    "enforcement "
                                    "officers",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    }
                                ],
                                "name": "officers' search of the "
                                "yard was performed by law "
                                "enforcement officers",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "was "
                                    "performed "
                                    "in the "
                                    "grounds "
                                    "around "
                                    "${bradley_s_house}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    },
                                ],
                                "name": "officers' search of the "
                                "yard was performed in the "
                                "grounds around Bradley's "
                                "house",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley} "
                                    "exhibited "
                                    "an "
                                    "expectation "
                                    "of privacy "
                                    "in "
                                    "${bradley_s_marijuana_patch}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "Bradley exhibited an "
                                "expectation of privacy in "
                                "Bradley's marijuana patch",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "it was "
                                    "reasonable "
                                    "for "
                                    "${bradley} "
                                    "to hold an "
                                    "expectation "
                                    "of privacy "
                                    "in "
                                    "${bradley_s_marijuana_patch}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "it was reasonable for "
                                "Bradley to hold an "
                                "expectation of privacy in "
                                "Bradley's marijuana patch",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "was an "
                                    "unreasonable "
                                    "governmental "
                                    "intrusion "
                                    "upon "
                                    "${bradley_s_marijuana_patch}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "officers' search of the "
                                "yard was an unreasonable "
                                "governmental intrusion upon "
                                "Bradley's marijuana patch",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${proof_of_bradley_s_guilt} "
                                    "was "
                                    "derived "
                                    "from "
                                    "${officers_search_of_the_yard}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "offered_by": {
                                            "generic": True,
                                            "name": "the prosecution",
                                            "plural": False,
                                        },
                                        "form": None,
                                        "statement": None,
                                        "statement_attribution": None,
                                        "name": "proof of Bradley's guilt",
                                    },
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    },
                                ],
                                "name": "proof of Bradley's guilt "
                                "was derived from officers' "
                                "search of the yard",
                                "standard_of_proof": None,
                            },
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "violated "
                                    "${bradley}'s "
                                    "expectation "
                                    "of "
                                    "privacy "
                                    "in "
                                    "${bradley_s_marijuana_patch}",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "false officers' search of "
                                "the yard violated "
                                "Bradley's expectation of "
                                "privacy in Bradley's "
                                "marijuana patch",
                                "standard_of_proof": None,
                            }
                        ],
                        "name": "",
                    },
                    "enactments": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/const/amendment/IV",
                                    "start_date": datetime.date(1791, 12, 15),
                                    "heading": "AMENDMENT IV.",
                                    "text_version": {
                                        "content": "The "
                                        "right "
                                        "of "
                                        "the "
                                        "people "
                                        "to "
                                        "be "
                                        "secure "
                                        "in "
                                        "their "
                                        "persons, "
                                        "houses, "
                                        "papers, "
                                        "and "
                                        "effects, "
                                        "against "
                                        "unreasonable "
                                        "searches "
                                        "and "
                                        "seizures, "
                                        "shall "
                                        "not "
                                        "be "
                                        "violated, "
                                        "and "
                                        "no "
                                        "Warrants "
                                        "shall "
                                        "issue, "
                                        "but "
                                        "upon "
                                        "probable "
                                        "cause, "
                                        "supported "
                                        "by "
                                        "Oath "
                                        "or "
                                        "affirmation, "
                                        "and "
                                        "particularly "
                                        "describing "
                                        "the "
                                        "place "
                                        "to "
                                        "be "
                                        "searched, "
                                        "and "
                                        "the "
                                        "persons "
                                        "or "
                                        "things "
                                        "to "
                                        "be "
                                        "seized.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735706/",
                                        "id": 735706,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/amendment/IV",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "",
                                            "prefix": "",
                                            "suffix": ", and no Warrants shall issue",
                                        }
                                    ],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us/const/amendment/XIV/1",
                                    "start_date": datetime.date(1868, 7, 28),
                                    "heading": "Citizenship: "
                                    "security "
                                    "and "
                                    "equal "
                                    "protection "
                                    "of "
                                    "citizens.",
                                    "text_version": {
                                        "content": "All "
                                        "persons "
                                        "born "
                                        "or "
                                        "naturalized "
                                        "in "
                                        "the "
                                        "United "
                                        "States, "
                                        "and "
                                        "subject "
                                        "to "
                                        "the "
                                        "jurisdiction "
                                        "thereof, "
                                        "are "
                                        "citizens "
                                        "of "
                                        "the "
                                        "United "
                                        "States "
                                        "and "
                                        "of "
                                        "the "
                                        "State "
                                        "wherein "
                                        "they "
                                        "reside. "
                                        "No "
                                        "State "
                                        "shall "
                                        "make "
                                        "or "
                                        "enforce "
                                        "any "
                                        "law "
                                        "which "
                                        "shall "
                                        "abridge "
                                        "the "
                                        "privileges "
                                        "or "
                                        "immunities "
                                        "of "
                                        "citizens "
                                        "of "
                                        "the "
                                        "United "
                                        "States; "
                                        "nor "
                                        "shall "
                                        "any "
                                        "State "
                                        "deprive "
                                        "any "
                                        "person "
                                        "of "
                                        "life, "
                                        "liberty, "
                                        "or "
                                        "property, "
                                        "without "
                                        "due "
                                        "process "
                                        "of "
                                        "law; "
                                        "nor "
                                        "deny "
                                        "to "
                                        "any "
                                        "person "
                                        "within "
                                        "its "
                                        "jurisdiction "
                                        "the "
                                        "equal "
                                        "protection "
                                        "of "
                                        "the "
                                        "laws.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735717/",
                                        "id": 735717,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/amendment/XIV/1",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "",
                                            "prefix": "immunities "
                                            "of "
                                            "citizens "
                                            "of "
                                            "the "
                                            "United "
                                            "States; ",
                                            "suffix": " nor deny to any person",
                                        }
                                    ],
                                },
                            },
                        ]
                    },
                    "enactments_despite": {"passages": []},
                    "mandatory": True,
                    "universal": True,
                    "name": None,
                },
                "rule_valid": False,
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
                                "exhibit": {
                                    "generic": True,
                                    "offered_by": {
                                        "generic": True,
                                        "name": "the prosecution",
                                        "plural": False,
                                    },
                                    "form": None,
                                    "statement": None,
                                    "statement_attribution": None,
                                    "name": "proof of Bradley's guilt",
                                },
                                "to_effect": {
                                    "generic": False,
                                    "predicate": {
                                        "content": "Bradley committed a crime",
                                        "truth": True,
                                    },
                                    "terms": [],
                                    "name": "fact that Bradley committed a crime",
                                    "standard_of_proof": None,
                                },
                                "name": "absence of evidence of Bradley's guilt",
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "was a "
                                    "warrantless "
                                    "search and "
                                    "seizure",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    }
                                ],
                                "name": "officers' search of the "
                                "yard was a warrantless "
                                "search and seizure",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley_s_house} was a house",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    }
                                ],
                                "name": "Bradley's house was a house",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley} lived at ${bradley_s_house}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    },
                                ],
                                "name": "Bradley lived at Bradley's house",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "was "
                                    "performed "
                                    "by law "
                                    "enforcement "
                                    "officers",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    }
                                ],
                                "name": "officers' search of the "
                                "yard was performed by law "
                                "enforcement officers",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "was "
                                    "performed "
                                    "in the "
                                    "grounds "
                                    "around "
                                    "${bradley_s_house}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    },
                                ],
                                "name": "officers' search of the "
                                "yard was performed in the "
                                "grounds around Bradley's "
                                "house",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley} "
                                    "exhibited "
                                    "an "
                                    "expectation "
                                    "of privacy "
                                    "in "
                                    "${bradley_s_marijuana_patch}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "Bradley exhibited an "
                                "expectation of privacy in "
                                "Bradley's marijuana patch",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "it was "
                                    "reasonable "
                                    "for "
                                    "${bradley} "
                                    "to hold an "
                                    "expectation "
                                    "of privacy "
                                    "in "
                                    "${bradley_s_marijuana_patch}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "it was reasonable for "
                                "Bradley to hold an "
                                "expectation of privacy in "
                                "Bradley's marijuana patch",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "violated "
                                    "${bradley}'s "
                                    "expectation "
                                    "of privacy "
                                    "in "
                                    "${bradley_s_marijuana_patch}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "officers' search of the "
                                "yard violated Bradley's "
                                "expectation of privacy in "
                                "Bradley's marijuana patch",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${proof_of_bradley_s_guilt} "
                                    "was "
                                    "derived "
                                    "from "
                                    "${officers_search_of_the_yard}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "offered_by": {
                                            "generic": True,
                                            "name": "the prosecution",
                                            "plural": False,
                                        },
                                        "form": None,
                                        "statement": None,
                                        "statement_attribution": None,
                                        "name": "proof of Bradley's guilt",
                                    },
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    },
                                ],
                                "name": "proof of Bradley's guilt "
                                "was derived from officers' "
                                "search of the yard",
                                "standard_of_proof": None,
                            },
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_yard} "
                                    "was an "
                                    "unreasonable "
                                    "governmental "
                                    "intrusion "
                                    "upon "
                                    "${bradley_s_marijuana_patch}",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the yard",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "false officers' search of "
                                "the yard was an "
                                "unreasonable governmental "
                                "intrusion upon Bradley's "
                                "marijuana patch",
                                "standard_of_proof": None,
                            }
                        ],
                        "name": "",
                    },
                    "enactments": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/const/amendment/IV",
                                    "start_date": datetime.date(1791, 12, 15),
                                    "heading": "AMENDMENT IV.",
                                    "text_version": {
                                        "content": "The "
                                        "right "
                                        "of "
                                        "the "
                                        "people "
                                        "to "
                                        "be "
                                        "secure "
                                        "in "
                                        "their "
                                        "persons, "
                                        "houses, "
                                        "papers, "
                                        "and "
                                        "effects, "
                                        "against "
                                        "unreasonable "
                                        "searches "
                                        "and "
                                        "seizures, "
                                        "shall "
                                        "not "
                                        "be "
                                        "violated, "
                                        "and "
                                        "no "
                                        "Warrants "
                                        "shall "
                                        "issue, "
                                        "but "
                                        "upon "
                                        "probable "
                                        "cause, "
                                        "supported "
                                        "by "
                                        "Oath "
                                        "or "
                                        "affirmation, "
                                        "and "
                                        "particularly "
                                        "describing "
                                        "the "
                                        "place "
                                        "to "
                                        "be "
                                        "searched, "
                                        "and "
                                        "the "
                                        "persons "
                                        "or "
                                        "things "
                                        "to "
                                        "be "
                                        "seized.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735706/",
                                        "id": 735706,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/amendment/IV",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "",
                                            "prefix": "",
                                            "suffix": ", and no Warrants shall issue",
                                        }
                                    ],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us/const/amendment/XIV/1",
                                    "start_date": datetime.date(1868, 7, 28),
                                    "heading": "Citizenship: "
                                    "security "
                                    "and "
                                    "equal "
                                    "protection "
                                    "of "
                                    "citizens.",
                                    "text_version": {
                                        "content": "All "
                                        "persons "
                                        "born "
                                        "or "
                                        "naturalized "
                                        "in "
                                        "the "
                                        "United "
                                        "States, "
                                        "and "
                                        "subject "
                                        "to "
                                        "the "
                                        "jurisdiction "
                                        "thereof, "
                                        "are "
                                        "citizens "
                                        "of "
                                        "the "
                                        "United "
                                        "States "
                                        "and "
                                        "of "
                                        "the "
                                        "State "
                                        "wherein "
                                        "they "
                                        "reside. "
                                        "No "
                                        "State "
                                        "shall "
                                        "make "
                                        "or "
                                        "enforce "
                                        "any "
                                        "law "
                                        "which "
                                        "shall "
                                        "abridge "
                                        "the "
                                        "privileges "
                                        "or "
                                        "immunities "
                                        "of "
                                        "citizens "
                                        "of "
                                        "the "
                                        "United "
                                        "States; "
                                        "nor "
                                        "shall "
                                        "any "
                                        "State "
                                        "deprive "
                                        "any "
                                        "person "
                                        "of "
                                        "life, "
                                        "liberty, "
                                        "or "
                                        "property, "
                                        "without "
                                        "due "
                                        "process "
                                        "of "
                                        "law; "
                                        "nor "
                                        "deny "
                                        "to "
                                        "any "
                                        "person "
                                        "within "
                                        "its "
                                        "jurisdiction "
                                        "the "
                                        "equal "
                                        "protection "
                                        "of "
                                        "the "
                                        "laws.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735717/",
                                        "id": 735717,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/amendment/XIV/1",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "",
                                            "prefix": "immunities "
                                            "of "
                                            "citizens "
                                            "of "
                                            "the "
                                            "United "
                                            "States; ",
                                            "suffix": " nor deny to any person",
                                        }
                                    ],
                                },
                            },
                        ]
                    },
                    "enactments_despite": {"passages": []},
                    "mandatory": True,
                    "universal": True,
                    "name": None,
                },
                "rule_valid": False,
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
                                "predicate": {
                                    "content": "${bradley} "
                                    "exhibited "
                                    "an "
                                    "expectation "
                                    "of "
                                    "privacy "
                                    "in "
                                    "${bradley_s_marijuana_patch}",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "false Bradley exhibited an "
                                "expectation of privacy in "
                                "Bradley's marijuana patch",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "the number "
                                    "of "
                                    "marijuana "
                                    "plants in "
                                    "${bradley_s_marijuana_patch} "
                                    "was",
                                    "truth": True,
                                    "quantity_range": {
                                        "sign": ">=",
                                        "include_negatives": None,
                                        "quantity": Decimal("3"),
                                    },
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    }
                                ],
                                "name": "the number of marijuana "
                                "plants in Bradley's "
                                "marijuana patch was >= 3",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley_s_marijuana_patch} "
                                    "was in a "
                                    "yard "
                                    "accessible "
                                    "from a "
                                    "house that "
                                    "did not "
                                    "belong to "
                                    "${bradley}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                ],
                                "name": "Bradley's marijuana patch "
                                "was in a yard accessible "
                                "from a house that did not "
                                "belong to Bradley",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley_s_marijuana_patch} "
                                    "was "
                                    "entirely "
                                    "hidden by "
                                    "foliage",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    }
                                ],
                                "name": "false Bradley's marijuana "
                                "patch was entirely hidden "
                                "by foliage",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "absent": {
                                    "generic": False,
                                    "predicate": {
                                        "content": "${bradley_s_marijuana_patch} "
                                        "was "
                                        "covered "
                                        "by "
                                        "nontransparent "
                                        "material",
                                        "truth": True,
                                    },
                                    "terms": [
                                        {
                                            "generic": True,
                                            "name": "Bradley's marijuana patch",
                                            "plural": False,
                                        }
                                    ],
                                    "name": "Bradley's "
                                    "marijuana patch "
                                    "was covered by "
                                    "nontransparent "
                                    "material",
                                    "standard_of_proof": None,
                                },
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "the "
                                    "distance "
                                    "from which "
                                    "part of "
                                    "${bradley_s_marijuana_patch} "
                                    "could be "
                                    "seen "
                                    "plainly "
                                    "was",
                                    "truth": True,
                                    "quantity_range": {
                                        "sign": ">=",
                                        "include_negatives": None,
                                        "quantity_magnitude": Decimal("1"),
                                        "quantity_units": "foot",
                                    },
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    }
                                ],
                                "name": "the distance from which "
                                "part of Bradley's marijuana "
                                "patch could be seen plainly "
                                "was >= 1 foot",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "the "
                                    "distance "
                                    "between "
                                    "${bradley_s_marijuana_patch} "
                                    "and "
                                    "${bradley_s_house} "
                                    "was",
                                    "truth": True,
                                    "quantity_range": {
                                        "sign": ">=",
                                        "include_negatives": None,
                                        "quantity_magnitude": Decimal("20"),
                                        "quantity_units": "foot",
                                    },
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    },
                                ],
                                "name": "the distance between "
                                "Bradley's marijuana patch "
                                "and Bradley's house was >= "
                                "20 feet",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "a house "
                                    "that did "
                                    "not belong "
                                    "to "
                                    "${bradley} "
                                    "had access "
                                    "to the "
                                    "rear yard "
                                    "where "
                                    "${bradley_s_marijuana_patch} "
                                    "was "
                                    "located",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "a house that did not belong "
                                "to Bradley had access to "
                                "the rear yard where "
                                "Bradley's marijuana patch "
                                "was located",
                                "standard_of_proof": None,
                            },
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley_s_house} was a house",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    }
                                ],
                                "name": "Bradley's house was a house",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley} lived at ${bradley_s_house}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    },
                                ],
                                "name": "Bradley lived at Bradley's house",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley_s_marijuana_patch} "
                                    "was "
                                    "partially "
                                    "hidden by "
                                    "foliage",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    }
                                ],
                                "name": "Bradley's marijuana patch "
                                "was partially hidden by "
                                "foliage",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley_s_marijuana_patch} "
                                    "was in "
                                    "the "
                                    "fenced "
                                    "rear yard "
                                    "of "
                                    "${bradley_s_house}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    },
                                ],
                                "name": "Bradley's marijuana patch "
                                "was in the fenced rear "
                                "yard of Bradley's house",
                                "standard_of_proof": None,
                            },
                        ],
                        "name": "",
                    },
                    "enactments": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/const/amendment/IV",
                                    "start_date": datetime.date(1791, 12, 15),
                                    "heading": "AMENDMENT IV.",
                                    "text_version": {
                                        "content": "The "
                                        "right "
                                        "of "
                                        "the "
                                        "people "
                                        "to "
                                        "be "
                                        "secure "
                                        "in "
                                        "their "
                                        "persons, "
                                        "houses, "
                                        "papers, "
                                        "and "
                                        "effects, "
                                        "against "
                                        "unreasonable "
                                        "searches "
                                        "and "
                                        "seizures, "
                                        "shall "
                                        "not "
                                        "be "
                                        "violated, "
                                        "and "
                                        "no "
                                        "Warrants "
                                        "shall "
                                        "issue, "
                                        "but "
                                        "upon "
                                        "probable "
                                        "cause, "
                                        "supported "
                                        "by "
                                        "Oath "
                                        "or "
                                        "affirmation, "
                                        "and "
                                        "particularly "
                                        "describing "
                                        "the "
                                        "place "
                                        "to "
                                        "be "
                                        "searched, "
                                        "and "
                                        "the "
                                        "persons "
                                        "or "
                                        "things "
                                        "to "
                                        "be "
                                        "seized.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735706/",
                                        "id": 735706,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/amendment/IV",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "",
                                            "prefix": "",
                                            "suffix": ", and no Warrants shall issue",
                                        }
                                    ],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us/const/amendment/XIV/1",
                                    "start_date": datetime.date(1868, 7, 28),
                                    "heading": "Citizenship: "
                                    "security "
                                    "and "
                                    "equal "
                                    "protection "
                                    "of "
                                    "citizens.",
                                    "text_version": {
                                        "content": "All "
                                        "persons "
                                        "born "
                                        "or "
                                        "naturalized "
                                        "in "
                                        "the "
                                        "United "
                                        "States, "
                                        "and "
                                        "subject "
                                        "to "
                                        "the "
                                        "jurisdiction "
                                        "thereof, "
                                        "are "
                                        "citizens "
                                        "of "
                                        "the "
                                        "United "
                                        "States "
                                        "and "
                                        "of "
                                        "the "
                                        "State "
                                        "wherein "
                                        "they "
                                        "reside. "
                                        "No "
                                        "State "
                                        "shall "
                                        "make "
                                        "or "
                                        "enforce "
                                        "any "
                                        "law "
                                        "which "
                                        "shall "
                                        "abridge "
                                        "the "
                                        "privileges "
                                        "or "
                                        "immunities "
                                        "of "
                                        "citizens "
                                        "of "
                                        "the "
                                        "United "
                                        "States; "
                                        "nor "
                                        "shall "
                                        "any "
                                        "State "
                                        "deprive "
                                        "any "
                                        "person "
                                        "of "
                                        "life, "
                                        "liberty, "
                                        "or "
                                        "property, "
                                        "without "
                                        "due "
                                        "process "
                                        "of "
                                        "law; "
                                        "nor "
                                        "deny "
                                        "to "
                                        "any "
                                        "person "
                                        "within "
                                        "its "
                                        "jurisdiction "
                                        "the "
                                        "equal "
                                        "protection "
                                        "of "
                                        "the "
                                        "laws.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735717/",
                                        "id": 735717,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/amendment/XIV/1",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "",
                                            "prefix": "immunities "
                                            "of "
                                            "citizens "
                                            "of "
                                            "the "
                                            "United "
                                            "States; ",
                                            "suffix": " nor deny to any person",
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
                                "predicate": {
                                    "content": "it was "
                                    "reasonable "
                                    "for "
                                    "${bradley} "
                                    "to "
                                    "exhibit "
                                    "an "
                                    "expectation "
                                    "of "
                                    "privacy "
                                    "in "
                                    "${bradley_s_marijuana_patch}",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "false it was reasonable "
                                "for Bradley to exhibit an "
                                "expectation of privacy in "
                                "Bradley's marijuana patch",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "the number "
                                    "of "
                                    "marijuana "
                                    "plants in "
                                    "${bradley_s_marijuana_patch} "
                                    "was",
                                    "truth": True,
                                    "quantity_range": {
                                        "sign": ">=",
                                        "include_negatives": None,
                                        "quantity": Decimal("3"),
                                    },
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    }
                                ],
                                "name": "the number of marijuana "
                                "plants in Bradley's "
                                "marijuana patch was >= 3",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley_s_marijuana_patch} "
                                    "was in a "
                                    "yard "
                                    "accessible "
                                    "from a "
                                    "house that "
                                    "did not "
                                    "belong to "
                                    "${bradley}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                ],
                                "name": "Bradley's marijuana patch "
                                "was in a yard accessible "
                                "from a house that did not "
                                "belong to Bradley",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley_s_marijuana_patch} "
                                    "was "
                                    "entirely "
                                    "hidden by "
                                    "foliage",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    }
                                ],
                                "name": "false Bradley's marijuana "
                                "patch was entirely hidden "
                                "by foliage",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "absent": {
                                    "generic": False,
                                    "predicate": {
                                        "content": "${bradley_s_marijuana_patch} "
                                        "was "
                                        "covered "
                                        "by "
                                        "nontransparent "
                                        "material",
                                        "truth": True,
                                    },
                                    "terms": [
                                        {
                                            "generic": True,
                                            "name": "Bradley's marijuana patch",
                                            "plural": False,
                                        }
                                    ],
                                    "name": "Bradley's "
                                    "marijuana patch "
                                    "was covered by "
                                    "nontransparent "
                                    "material",
                                    "standard_of_proof": None,
                                },
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "the "
                                    "distance "
                                    "from which "
                                    "part of "
                                    "${bradley_s_marijuana_patch} "
                                    "could be "
                                    "seen "
                                    "plainly "
                                    "was",
                                    "truth": True,
                                    "quantity_range": {
                                        "sign": ">=",
                                        "include_negatives": None,
                                        "quantity_magnitude": Decimal("1"),
                                        "quantity_units": "foot",
                                    },
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    }
                                ],
                                "name": "the distance from which "
                                "part of Bradley's marijuana "
                                "patch could be seen plainly "
                                "was >= 1 foot",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "the "
                                    "distance "
                                    "between "
                                    "${bradley_s_marijuana_patch} "
                                    "and "
                                    "${bradley_s_house} "
                                    "was",
                                    "truth": True,
                                    "quantity_range": {
                                        "sign": ">=",
                                        "include_negatives": None,
                                        "quantity_magnitude": Decimal("20"),
                                        "quantity_units": "foot",
                                    },
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    },
                                ],
                                "name": "the distance between "
                                "Bradley's marijuana patch "
                                "and Bradley's house was >= "
                                "20 feet",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "a house "
                                    "that did "
                                    "not belong "
                                    "to "
                                    "${bradley} "
                                    "had access "
                                    "to the "
                                    "rear yard "
                                    "where "
                                    "${bradley_s_marijuana_patch} "
                                    "was "
                                    "located",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                ],
                                "name": "a house that did not belong "
                                "to Bradley had access to "
                                "the rear yard where "
                                "Bradley's marijuana patch "
                                "was located",
                                "standard_of_proof": None,
                            },
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley_s_house} was a house",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    }
                                ],
                                "name": "Bradley's house was a house",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley} lived at ${bradley_s_house}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    },
                                ],
                                "name": "Bradley lived at Bradley's house",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley_s_marijuana_patch} "
                                    "was "
                                    "partially "
                                    "hidden by "
                                    "foliage",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    }
                                ],
                                "name": "Bradley's marijuana patch "
                                "was partially hidden by "
                                "foliage",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${bradley_s_marijuana_patch} "
                                    "was in "
                                    "the "
                                    "fenced "
                                    "rear yard "
                                    "of "
                                    "${bradley_s_house}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Bradley's marijuana patch",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Bradley's house",
                                        "plural": False,
                                    },
                                ],
                                "name": "Bradley's marijuana patch "
                                "was in the fenced rear "
                                "yard of Bradley's house",
                                "standard_of_proof": None,
                            },
                        ],
                        "name": "",
                    },
                    "enactments": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/const/amendment/IV",
                                    "start_date": datetime.date(1791, 12, 15),
                                    "heading": "AMENDMENT IV.",
                                    "text_version": {
                                        "content": "The "
                                        "right "
                                        "of "
                                        "the "
                                        "people "
                                        "to "
                                        "be "
                                        "secure "
                                        "in "
                                        "their "
                                        "persons, "
                                        "houses, "
                                        "papers, "
                                        "and "
                                        "effects, "
                                        "against "
                                        "unreasonable "
                                        "searches "
                                        "and "
                                        "seizures, "
                                        "shall "
                                        "not "
                                        "be "
                                        "violated, "
                                        "and "
                                        "no "
                                        "Warrants "
                                        "shall "
                                        "issue, "
                                        "but "
                                        "upon "
                                        "probable "
                                        "cause, "
                                        "supported "
                                        "by "
                                        "Oath "
                                        "or "
                                        "affirmation, "
                                        "and "
                                        "particularly "
                                        "describing "
                                        "the "
                                        "place "
                                        "to "
                                        "be "
                                        "searched, "
                                        "and "
                                        "the "
                                        "persons "
                                        "or "
                                        "things "
                                        "to "
                                        "be "
                                        "seized.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735706/",
                                        "id": 735706,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/amendment/IV",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "",
                                            "prefix": "",
                                            "suffix": ", and no Warrants shall issue",
                                        }
                                    ],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us/const/amendment/XIV/1",
                                    "start_date": datetime.date(1868, 7, 28),
                                    "heading": "Citizenship: "
                                    "security "
                                    "and "
                                    "equal "
                                    "protection "
                                    "of "
                                    "citizens.",
                                    "text_version": {
                                        "content": "All "
                                        "persons "
                                        "born "
                                        "or "
                                        "naturalized "
                                        "in "
                                        "the "
                                        "United "
                                        "States, "
                                        "and "
                                        "subject "
                                        "to "
                                        "the "
                                        "jurisdiction "
                                        "thereof, "
                                        "are "
                                        "citizens "
                                        "of "
                                        "the "
                                        "United "
                                        "States "
                                        "and "
                                        "of "
                                        "the "
                                        "State "
                                        "wherein "
                                        "they "
                                        "reside. "
                                        "No "
                                        "State "
                                        "shall "
                                        "make "
                                        "or "
                                        "enforce "
                                        "any "
                                        "law "
                                        "which "
                                        "shall "
                                        "abridge "
                                        "the "
                                        "privileges "
                                        "or "
                                        "immunities "
                                        "of "
                                        "citizens "
                                        "of "
                                        "the "
                                        "United "
                                        "States; "
                                        "nor "
                                        "shall "
                                        "any "
                                        "State "
                                        "deprive "
                                        "any "
                                        "person "
                                        "of "
                                        "life, "
                                        "liberty, "
                                        "or "
                                        "property, "
                                        "without "
                                        "due "
                                        "process "
                                        "of "
                                        "law; "
                                        "nor "
                                        "deny "
                                        "to "
                                        "any "
                                        "person "
                                        "within "
                                        "its "
                                        "jurisdiction "
                                        "the "
                                        "equal "
                                        "protection "
                                        "of "
                                        "the "
                                        "laws.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735717/",
                                        "id": 735717,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/amendment/XIV/1",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "",
                                            "prefix": "immunities "
                                            "of "
                                            "citizens "
                                            "of "
                                            "the "
                                            "United "
                                            "States; ",
                                            "suffix": " nor deny to any person",
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


def anchored_holdings() -> AnchoredHoldings:
    """Build AnchoredHoldings for the Brad case from Python model data."""
    return AnchoredHoldings.model_validate(copy.deepcopy(RAW_ANCHORED_HOLDINGS))


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
        predicate: dict[str, Any] = {"content": content, "truth": truth}
        if sign is not None:
            predicate["sign"] = sign
            predicate["expression"] = expression
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
        "${officers_search_of_the_yard} was a warrantless search and seizure",
        [e["officers_search_of_the_yard"]],
        "officers' search of the yard was a warrantless search and seizure",
    )
    f2 = fact(
        "${bradley_s_house} was a house",
        [e["bradley_s_house"]],
        "Bradley's house was a house",
    )
    f3 = fact(
        "${bradley} lived at ${bradley_s_house}",
        [e["bradley"], e["bradley_s_house"]],
        "Bradley lived at Bradley's house",
    )
    f4 = fact(
        "${officers_search_of_the_yard} was performed by law enforcement officers",
        [e["officers_search_of_the_yard"]],
        "officers' search of the yard was performed by law enforcement officers",
    )
    f5 = fact(
        "${officers_search_of_the_yard} was performed in the grounds around ${bradley_s_house}",
        [e["officers_search_of_the_yard"], e["bradley_s_house"]],
        "officers' search of the yard was performed in the grounds around Bradley's house",
    )
    f6 = fact(
        "${bradley} exhibited an expectation of privacy in ${bradley_s_marijuana_patch}",
        [e["bradley"], e["bradley_s_marijuana_patch"]],
        "Bradley exhibited an expectation of privacy in Bradley's marijuana patch",
    )
    f7 = fact(
        "it was reasonable for ${bradley} to hold an expectation of privacy in ${bradley_s_marijuana_patch}",
        [e["bradley"], e["bradley_s_marijuana_patch"]],
        "it was reasonable for Bradley to hold an expectation of privacy in Bradley's marijuana patch",
    )
    f8 = fact(
        "${officers_search_of_the_yard} violated ${bradley}'s expectation of privacy in ${bradley_s_marijuana_patch}",
        [
            e["officers_search_of_the_yard"],
            e["bradley"],
            e["bradley_s_marijuana_patch"],
        ],
        "officers' search of the yard violated Bradley's expectation of privacy in Bradley's marijuana patch",
    )
    f9 = fact(
        "${officers_search_of_the_yard} was an unreasonable governmental intrusion upon ${bradley_s_marijuana_patch}",
        [e["officers_search_of_the_yard"], e["bradley_s_marijuana_patch"]],
        "officers' search of the yard was an unreasonable governmental intrusion upon Bradley's marijuana patch",
    )
    f10 = fact(
        "${proof_of_bradley_s_guilt} was derived from ${officers_search_of_the_yard}",
        [proof_exhibit, e["officers_search_of_the_yard"]],
        "proof of Bradley's guilt was derived from officers' search of the yard",
    )
    f12 = fact(
        "${bradley} exhibited an expectation of privacy in ${bradley_s_marijuana_patch}",
        [e["bradley"], e["bradley_s_marijuana_patch"]],
        "false Bradley exhibited an expectation of privacy in Bradley's marijuana patch",
        truth=False,
    )
    f14 = fact(
        "${officers_search_of_the_yard} was an unreasonable intrusion upon ${bradley_s_marijuana_patch}",
        [e["officers_search_of_the_yard"], e["bradley_s_marijuana_patch"]],
        "officers' search of the yard was an unreasonable intrusion upon Bradley's marijuana patch",
    )
    f15 = fact(
        "it was reasonable for ${bradley} to hold an expectation of privacy in ${bradley_s_marijuana_patch}",
        [e["bradley"], e["bradley_s_marijuana_patch"]],
        "false it was reasonable for Bradley to hold an expectation of privacy in Bradley's marijuana patch",
        truth=False,
    )
    f16 = fact(
        "${officers_search_of_the_yard} violated ${bradley}'s expectation of privacy in ${bradley_s_marijuana_patch}",
        [
            e["officers_search_of_the_yard"],
            e["bradley"],
            e["bradley_s_marijuana_patch"],
        ],
        "false officers' search of the yard violated Bradley's expectation of privacy in Bradley's marijuana patch",
        truth=False,
    )
    f17 = fact(
        "${officers_search_of_the_yard} was an unreasonable governmental intrusion upon ${bradley_s_marijuana_patch}",
        [e["officers_search_of_the_yard"], e["bradley_s_marijuana_patch"]],
        "false officers' search of the yard was an unreasonable governmental intrusion upon Bradley's marijuana patch",
        truth=False,
    )
    f18 = fact(
        "the number of marijuana plants in ${bradley_s_marijuana_patch} was",
        [e["bradley_s_marijuana_patch"]],
        "the number of marijuana plants in Bradley's marijuana patch was >= 3",
        sign=">=",
        expression=3,
    )
    f19 = fact(
        "${bradley_s_marijuana_patch} was in a yard accessible from a house that did not belong to ${bradley}",
        [e["bradley_s_marijuana_patch"], e["bradley"]],
        "Bradley's marijuana patch was in a yard accessible from a house that did not belong to Bradley",
    )
    f20 = fact(
        "${bradley_s_marijuana_patch} was entirely hidden by foliage",
        [e["bradley_s_marijuana_patch"]],
        "false Bradley's marijuana patch was entirely hidden by foliage",
        truth=False,
    )
    f21_absent = AbsenceOfFactor(
        absent=fact(
            "${bradley_s_marijuana_patch} was covered by nontransparent material",
            [e["bradley_s_marijuana_patch"]],
            "Bradley's marijuana patch was covered by nontransparent material",
        )
    )
    f22 = fact(
        "the distance from which part of ${bradley_s_marijuana_patch} could be seen plainly was",
        [e["bradley_s_marijuana_patch"]],
        "the distance from which part of Bradley's marijuana patch could be seen plainly was >= 1 foot",
        sign=">=",
        expression="1 foot",
    )
    f23 = fact(
        "the distance between ${bradley_s_marijuana_patch} and ${bradley_s_house} was",
        [e["bradley_s_marijuana_patch"], e["bradley_s_house"]],
        "the distance between Bradley's marijuana patch and Bradley's house was >= 20 feet",
        sign=">=",
        expression="20 feet",
    )
    f24 = fact(
        "a house that did not belong to ${bradley} had access to the rear yard where ${bradley_s_marijuana_patch} was located",
        [e["bradley"], e["bradley_s_marijuana_patch"]],
        "a house that did not belong to Bradley had access to the rear yard where Bradley's marijuana patch was located",
    )
    f25 = fact(
        "${bradley_s_marijuana_patch} was partially hidden by foliage",
        [e["bradley_s_marijuana_patch"]],
        "Bradley's marijuana patch was partially hidden by foliage",
    )
    f26 = fact(
        "${bradley_s_marijuana_patch} was in the fenced rear yard of ${bradley_s_house}",
        [e["bradley_s_marijuana_patch"], e["bradley_s_house"]],
        "Bradley's marijuana patch was in the fenced rear yard of Bradley's house",
    )
    f27 = fact(
        "it was reasonable for ${bradley} to exhibit an expectation of privacy in ${bradley_s_marijuana_patch}",
        [e["bradley"], e["bradley_s_marijuana_patch"]],
        "false it was reasonable for Bradley to exhibit an expectation of privacy in Bradley's marijuana patch",
        truth=False,
    )

    base_enactments = copy.deepcopy(anchored_holdings().holdings[0].holding.enactments)

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
