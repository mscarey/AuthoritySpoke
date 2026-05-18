import copy
import datetime
from decimal import Decimal

from authorityspoke.opinions import AnchoredHoldings

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
