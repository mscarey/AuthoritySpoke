import copy
import datetime

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


def anchored_holdings() -> AnchoredHoldings:
    """Build AnchoredHoldings for the Cardenas case from Python model data."""
    return AnchoredHoldings.model_validate(copy.deepcopy(RAW_ANCHORED_HOLDINGS))
