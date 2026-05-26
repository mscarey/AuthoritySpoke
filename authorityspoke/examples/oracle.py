import copy
import datetime

from authorityspoke import Entity
from authorityspoke.holdings import HoldingGroup
from authorityspoke.opinions import AnchoredHoldings, HoldingWithAnchors

HOLDINGS = HoldingGroup(holdings=[])
ENTITIES: dict[str, Entity] = {}

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
                                    "content": "${the_java_api} was copyrightable",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "false the Java API was copyrightable",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} was an original work",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "false the Java API was an original work",
                                "standard_of_proof": None,
                            }
                        ],
                        "despite": [],
                        "name": "",
                    },
                    "enactments": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/a",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Copyright "
                                        "protection "
                                        "subsists, "
                                        "in "
                                        "accordance "
                                        "with "
                                        "this "
                                        "title, "
                                        "in "
                                        "original "
                                        "works "
                                        "of "
                                        "authorship "
                                        "fixed "
                                        "in "
                                        "any "
                                        "tangible "
                                        "medium "
                                        "of "
                                        "expression, "
                                        "now "
                                        "known "
                                        "or "
                                        "later "
                                        "developed, "
                                        "from "
                                        "which "
                                        "they "
                                        "can "
                                        "be "
                                        "perceived, "
                                        "reproduced, "
                                        "or "
                                        "otherwise "
                                        "communicated, "
                                        "either "
                                        "directly "
                                        "or "
                                        "with "
                                        "the "
                                        "aid "
                                        "of "
                                        "a "
                                        "machine "
                                        "or "
                                        "device. "
                                        "Works "
                                        "of "
                                        "authorship "
                                        "include "
                                        "the "
                                        "following "
                                        "categories:",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030579/",
                                        "id": 1030579,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/a",
                                    "children": [
                                        {
                                            "node": "/us/usc/t17/s102/a/1",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "literary works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030571/",
                                                "id": 1030571,
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
                                            "node": "/us/usc/t17/s102/a/2",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "musical "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "words;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030572/",
                                                "id": 1030572,
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
                                            "node": "/us/usc/t17/s102/a/3",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "dramatic "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "music;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030573/",
                                                "id": 1030573,
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
                                            "node": "/us/usc/t17/s102/a/4",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pantomimes "
                                                "and "
                                                "choreographic "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030574/",
                                                "id": 1030574,
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
                                            "node": "/us/usc/t17/s102/a/5",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pictorial, "
                                                "graphic, "
                                                "and "
                                                "sculptural "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030575/",
                                                "id": 1030575,
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
                                            "node": "/us/usc/t17/s102/a/6",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "motion "
                                                "pictures "
                                                "and "
                                                "other "
                                                "audiovisual "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030576/",
                                                "id": 1030576,
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
                                            "node": "/us/usc/t17/s102/a/7",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "sound recordings; and",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030577/",
                                                "id": 1030577,
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
                                            "node": "/us/usc/t17/s102/a/8",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "architectural works.",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030578/",
                                                "id": 1030578,
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
                                            "exact": "Copyright "
                                            "protection "
                                            "subsists, "
                                            "in "
                                            "accordance "
                                            "with "
                                            "this "
                                            "title, "
                                            "in "
                                            "original "
                                            "works "
                                            "of "
                                            "authorship "
                                            "fixed "
                                            "in "
                                            "any "
                                            "tangible "
                                            "medium "
                                            "of "
                                            "expression, "
                                            "now "
                                            "known "
                                            "or "
                                            "later "
                                            "developed, "
                                            "from "
                                            "which "
                                            "they "
                                            "can "
                                            "be "
                                            "perceived, "
                                            "reproduced, "
                                            "or "
                                            "otherwise "
                                            "communicated, "
                                            "either "
                                            "directly "
                                            "or "
                                            "with "
                                            "the "
                                            "aid "
                                            "of "
                                            "a "
                                            "machine "
                                            "or "
                                            "device.",
                                            "prefix": "",
                                            "suffix": "",
                                        }
                                    ],
                                },
                            }
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
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "must be “original” to qualify",
                        "prefix": "By statute, a work ",
                        "suffix": " for",
                    }
                ],
            },
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
                                    "content": "${the_java_api} was an original work",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was an original work",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was "
                                    "independently "
                                    "created by "
                                    "the "
                                    "author, as "
                                    "opposed to "
                                    "copied "
                                    "from other "
                                    "works",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was "
                                "independently created by "
                                "the author, as opposed to "
                                "copied from other works",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "possessed "
                                    "at least "
                                    "some "
                                    "minimal "
                                    "degree of "
                                    "creativity",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API possessed at "
                                "least some minimal degree "
                                "of creativity",
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
                                    "node": "/us/usc/t17/s102/a",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Copyright "
                                        "protection "
                                        "subsists, "
                                        "in "
                                        "accordance "
                                        "with "
                                        "this "
                                        "title, "
                                        "in "
                                        "original "
                                        "works "
                                        "of "
                                        "authorship "
                                        "fixed "
                                        "in "
                                        "any "
                                        "tangible "
                                        "medium "
                                        "of "
                                        "expression, "
                                        "now "
                                        "known "
                                        "or "
                                        "later "
                                        "developed, "
                                        "from "
                                        "which "
                                        "they "
                                        "can "
                                        "be "
                                        "perceived, "
                                        "reproduced, "
                                        "or "
                                        "otherwise "
                                        "communicated, "
                                        "either "
                                        "directly "
                                        "or "
                                        "with "
                                        "the "
                                        "aid "
                                        "of "
                                        "a "
                                        "machine "
                                        "or "
                                        "device. "
                                        "Works "
                                        "of "
                                        "authorship "
                                        "include "
                                        "the "
                                        "following "
                                        "categories:",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030579/",
                                        "id": 1030579,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/a",
                                    "children": [
                                        {
                                            "node": "/us/usc/t17/s102/a/1",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "literary works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030571/",
                                                "id": 1030571,
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
                                            "node": "/us/usc/t17/s102/a/2",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "musical "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "words;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030572/",
                                                "id": 1030572,
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
                                            "node": "/us/usc/t17/s102/a/3",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "dramatic "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "music;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030573/",
                                                "id": 1030573,
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
                                            "node": "/us/usc/t17/s102/a/4",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pantomimes "
                                                "and "
                                                "choreographic "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030574/",
                                                "id": 1030574,
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
                                            "node": "/us/usc/t17/s102/a/5",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pictorial, "
                                                "graphic, "
                                                "and "
                                                "sculptural "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030575/",
                                                "id": 1030575,
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
                                            "node": "/us/usc/t17/s102/a/6",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "motion "
                                                "pictures "
                                                "and "
                                                "other "
                                                "audiovisual "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030576/",
                                                "id": 1030576,
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
                                            "node": "/us/usc/t17/s102/a/7",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "sound recordings; and",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030577/",
                                                "id": 1030577,
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
                                            "node": "/us/usc/t17/s102/a/8",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "architectural works.",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030578/",
                                                "id": 1030578,
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
                                            "exact": "Copyright "
                                            "protection "
                                            "subsists, "
                                            "in "
                                            "accordance "
                                            "with "
                                            "this "
                                            "title, "
                                            "in "
                                            "original "
                                            "works "
                                            "of "
                                            "authorship "
                                            "fixed "
                                            "in "
                                            "any "
                                            "tangible "
                                            "medium "
                                            "of "
                                            "expression, "
                                            "now "
                                            "known "
                                            "or "
                                            "later "
                                            "developed, "
                                            "from "
                                            "which "
                                            "they "
                                            "can "
                                            "be "
                                            "perceived, "
                                            "reproduced, "
                                            "or "
                                            "otherwise "
                                            "communicated, "
                                            "either "
                                            "directly "
                                            "or "
                                            "with "
                                            "the "
                                            "aid "
                                            "of "
                                            "a "
                                            "machine "
                                            "or "
                                            "device.",
                                            "prefix": "",
                                            "suffix": "",
                                        }
                                    ],
                                },
                            }
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
                                "predicate": {
                                    "content": "${the_java_api} was copyrightable",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was copyrightable",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} was an original work",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was an original work",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was the "
                                    "expression "
                                    "of an idea",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was the expression of an idea",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} was an idea",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "false the Java API was an idea",
                                "standard_of_proof": None,
                            },
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was "
                                    "essentially "
                                    "the only "
                                    "way to "
                                    "express "
                                    "the idea "
                                    "that it "
                                    "embodied",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was "
                                "essentially the only way "
                                "to express the idea that "
                                "it embodied",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} was a scene a faire",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was a scene a faire",
                                "standard_of_proof": None,
                            },
                        ],
                        "name": "",
                    },
                    "enactments": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/a",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Copyright "
                                        "protection "
                                        "subsists, "
                                        "in "
                                        "accordance "
                                        "with "
                                        "this "
                                        "title, "
                                        "in "
                                        "original "
                                        "works "
                                        "of "
                                        "authorship "
                                        "fixed "
                                        "in "
                                        "any "
                                        "tangible "
                                        "medium "
                                        "of "
                                        "expression, "
                                        "now "
                                        "known "
                                        "or "
                                        "later "
                                        "developed, "
                                        "from "
                                        "which "
                                        "they "
                                        "can "
                                        "be "
                                        "perceived, "
                                        "reproduced, "
                                        "or "
                                        "otherwise "
                                        "communicated, "
                                        "either "
                                        "directly "
                                        "or "
                                        "with "
                                        "the "
                                        "aid "
                                        "of "
                                        "a "
                                        "machine "
                                        "or "
                                        "device. "
                                        "Works "
                                        "of "
                                        "authorship "
                                        "include "
                                        "the "
                                        "following "
                                        "categories:",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030579/",
                                        "id": 1030579,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/a",
                                    "children": [
                                        {
                                            "node": "/us/usc/t17/s102/a/1",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "literary works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030571/",
                                                "id": 1030571,
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
                                            "node": "/us/usc/t17/s102/a/2",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "musical "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "words;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030572/",
                                                "id": 1030572,
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
                                            "node": "/us/usc/t17/s102/a/3",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "dramatic "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "music;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030573/",
                                                "id": 1030573,
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
                                            "node": "/us/usc/t17/s102/a/4",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pantomimes "
                                                "and "
                                                "choreographic "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030574/",
                                                "id": 1030574,
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
                                            "node": "/us/usc/t17/s102/a/5",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pictorial, "
                                                "graphic, "
                                                "and "
                                                "sculptural "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030575/",
                                                "id": 1030575,
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
                                            "node": "/us/usc/t17/s102/a/6",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "motion "
                                                "pictures "
                                                "and "
                                                "other "
                                                "audiovisual "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030576/",
                                                "id": 1030576,
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
                                            "node": "/us/usc/t17/s102/a/7",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "sound recordings; and",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030577/",
                                                "id": 1030577,
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
                                            "node": "/us/usc/t17/s102/a/8",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "architectural works.",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030578/",
                                                "id": 1030578,
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
                                            "exact": "Copyright "
                                            "protection "
                                            "subsists, "
                                            "in "
                                            "accordance "
                                            "with "
                                            "this "
                                            "title, "
                                            "in "
                                            "original "
                                            "works "
                                            "of "
                                            "authorship "
                                            "fixed "
                                            "in "
                                            "any "
                                            "tangible "
                                            "medium "
                                            "of "
                                            "expression, "
                                            "now "
                                            "known "
                                            "or "
                                            "later "
                                            "developed, "
                                            "from "
                                            "which "
                                            "they "
                                            "can "
                                            "be "
                                            "perceived, "
                                            "reproduced, "
                                            "or "
                                            "otherwise "
                                            "communicated, "
                                            "either "
                                            "directly "
                                            "or "
                                            "with "
                                            "the "
                                            "aid "
                                            "of "
                                            "a "
                                            "machine "
                                            "or "
                                            "device.",
                                            "prefix": "",
                                            "suffix": "",
                                        }
                                    ],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "In "
                                        "no "
                                        "case "
                                        "does "
                                        "copyright "
                                        "protection "
                                        "for "
                                        "an "
                                        "original "
                                        "work "
                                        "of "
                                        "authorship "
                                        "extend "
                                        "to "
                                        "any "
                                        "idea, "
                                        "procedure, "
                                        "process, "
                                        "system, "
                                        "method "
                                        "of "
                                        "operation, "
                                        "concept, "
                                        "principle, "
                                        "or "
                                        "discovery, "
                                        "regardless "
                                        "of "
                                        "the "
                                        "form "
                                        "in "
                                        "which "
                                        "it "
                                        "is "
                                        "described, "
                                        "explained, "
                                        "illustrated, "
                                        "or "
                                        "embodied "
                                        "in "
                                        "such "
                                        "work.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030580/",
                                        "id": 1030580,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [{"start": 0, "end": None}],
                                    "quotes": [],
                                },
                            }
                        ]
                    },
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
                                    "content": "${the_java_api} "
                                    "was a "
                                    "literal "
                                    "element "
                                    "of "
                                    "${the_java_language}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    },
                                ],
                                "name": "the Java API was a literal "
                                "element of the Java "
                                "language",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_language} "
                                    "was a "
                                    "computer "
                                    "program",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java language was a computer program",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was the "
                                    "source "
                                    "code of "
                                    "${the_java_language}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    },
                                ],
                                "name": "the Java API was the source "
                                "code of the Java language",
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
                                    "node": "/us/usc/t17/s102/a",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Copyright "
                                        "protection "
                                        "subsists, "
                                        "in "
                                        "accordance "
                                        "with "
                                        "this "
                                        "title, "
                                        "in "
                                        "original "
                                        "works "
                                        "of "
                                        "authorship "
                                        "fixed "
                                        "in "
                                        "any "
                                        "tangible "
                                        "medium "
                                        "of "
                                        "expression, "
                                        "now "
                                        "known "
                                        "or "
                                        "later "
                                        "developed, "
                                        "from "
                                        "which "
                                        "they "
                                        "can "
                                        "be "
                                        "perceived, "
                                        "reproduced, "
                                        "or "
                                        "otherwise "
                                        "communicated, "
                                        "either "
                                        "directly "
                                        "or "
                                        "with "
                                        "the "
                                        "aid "
                                        "of "
                                        "a "
                                        "machine "
                                        "or "
                                        "device. "
                                        "Works "
                                        "of "
                                        "authorship "
                                        "include "
                                        "the "
                                        "following "
                                        "categories:",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030579/",
                                        "id": 1030579,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/a",
                                    "children": [
                                        {
                                            "node": "/us/usc/t17/s102/a/1",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "literary works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030571/",
                                                "id": 1030571,
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
                                            "node": "/us/usc/t17/s102/a/2",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "musical "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "words;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030572/",
                                                "id": 1030572,
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
                                            "node": "/us/usc/t17/s102/a/3",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "dramatic "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "music;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030573/",
                                                "id": 1030573,
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
                                            "node": "/us/usc/t17/s102/a/4",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pantomimes "
                                                "and "
                                                "choreographic "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030574/",
                                                "id": 1030574,
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
                                            "node": "/us/usc/t17/s102/a/5",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pictorial, "
                                                "graphic, "
                                                "and "
                                                "sculptural "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030575/",
                                                "id": 1030575,
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
                                            "node": "/us/usc/t17/s102/a/6",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "motion "
                                                "pictures "
                                                "and "
                                                "other "
                                                "audiovisual "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030576/",
                                                "id": 1030576,
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
                                            "node": "/us/usc/t17/s102/a/7",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "sound recordings; and",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030577/",
                                                "id": 1030577,
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
                                            "node": "/us/usc/t17/s102/a/8",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "architectural works.",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030578/",
                                                "id": 1030578,
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
                                            "exact": "Copyright "
                                            "protection "
                                            "subsists, "
                                            "in "
                                            "accordance "
                                            "with "
                                            "this "
                                            "title, "
                                            "in "
                                            "original "
                                            "works "
                                            "of "
                                            "authorship "
                                            "fixed "
                                            "in "
                                            "any "
                                            "tangible "
                                            "medium "
                                            "of "
                                            "expression, "
                                            "now "
                                            "known "
                                            "or "
                                            "later "
                                            "developed, "
                                            "from "
                                            "which "
                                            "they "
                                            "can "
                                            "be "
                                            "perceived, "
                                            "reproduced, "
                                            "or "
                                            "otherwise "
                                            "communicated, "
                                            "either "
                                            "directly "
                                            "or "
                                            "with "
                                            "the "
                                            "aid "
                                            "of "
                                            "a "
                                            "machine "
                                            "or "
                                            "device.",
                                            "prefix": "",
                                            "suffix": "",
                                        }
                                    ],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "In "
                                        "no "
                                        "case "
                                        "does "
                                        "copyright "
                                        "protection "
                                        "for "
                                        "an "
                                        "original "
                                        "work "
                                        "of "
                                        "authorship "
                                        "extend "
                                        "to "
                                        "any "
                                        "idea, "
                                        "procedure, "
                                        "process, "
                                        "system, "
                                        "method "
                                        "of "
                                        "operation, "
                                        "concept, "
                                        "principle, "
                                        "or "
                                        "discovery, "
                                        "regardless "
                                        "of "
                                        "the "
                                        "form "
                                        "in "
                                        "which "
                                        "it "
                                        "is "
                                        "described, "
                                        "explained, "
                                        "illustrated, "
                                        "or "
                                        "embodied "
                                        "in "
                                        "such "
                                        "work.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030580/",
                                        "id": 1030580,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [{"start": 0, "end": None}],
                                    "quotes": [],
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
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was a "
                                    "literal "
                                    "element "
                                    "of "
                                    "${the_java_language}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    },
                                ],
                                "name": "the Java API was a literal "
                                "element of the Java "
                                "language",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_language} "
                                    "was a "
                                    "computer "
                                    "program",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java language was a computer program",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was the "
                                    "object "
                                    "code of "
                                    "${the_java_language}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    },
                                ],
                                "name": "the Java API was the object "
                                "code of the Java language",
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
                                    "node": "/us/usc/t17/s102/a",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Copyright "
                                        "protection "
                                        "subsists, "
                                        "in "
                                        "accordance "
                                        "with "
                                        "this "
                                        "title, "
                                        "in "
                                        "original "
                                        "works "
                                        "of "
                                        "authorship "
                                        "fixed "
                                        "in "
                                        "any "
                                        "tangible "
                                        "medium "
                                        "of "
                                        "expression, "
                                        "now "
                                        "known "
                                        "or "
                                        "later "
                                        "developed, "
                                        "from "
                                        "which "
                                        "they "
                                        "can "
                                        "be "
                                        "perceived, "
                                        "reproduced, "
                                        "or "
                                        "otherwise "
                                        "communicated, "
                                        "either "
                                        "directly "
                                        "or "
                                        "with "
                                        "the "
                                        "aid "
                                        "of "
                                        "a "
                                        "machine "
                                        "or "
                                        "device. "
                                        "Works "
                                        "of "
                                        "authorship "
                                        "include "
                                        "the "
                                        "following "
                                        "categories:",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030579/",
                                        "id": 1030579,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/a",
                                    "children": [
                                        {
                                            "node": "/us/usc/t17/s102/a/1",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "literary works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030571/",
                                                "id": 1030571,
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
                                            "node": "/us/usc/t17/s102/a/2",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "musical "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "words;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030572/",
                                                "id": 1030572,
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
                                            "node": "/us/usc/t17/s102/a/3",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "dramatic "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "music;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030573/",
                                                "id": 1030573,
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
                                            "node": "/us/usc/t17/s102/a/4",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pantomimes "
                                                "and "
                                                "choreographic "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030574/",
                                                "id": 1030574,
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
                                            "node": "/us/usc/t17/s102/a/5",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pictorial, "
                                                "graphic, "
                                                "and "
                                                "sculptural "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030575/",
                                                "id": 1030575,
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
                                            "node": "/us/usc/t17/s102/a/6",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "motion "
                                                "pictures "
                                                "and "
                                                "other "
                                                "audiovisual "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030576/",
                                                "id": 1030576,
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
                                            "node": "/us/usc/t17/s102/a/7",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "sound recordings; and",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030577/",
                                                "id": 1030577,
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
                                            "node": "/us/usc/t17/s102/a/8",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "architectural works.",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030578/",
                                                "id": 1030578,
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
                                            "exact": "Copyright "
                                            "protection "
                                            "subsists, "
                                            "in "
                                            "accordance "
                                            "with "
                                            "this "
                                            "title, "
                                            "in "
                                            "original "
                                            "works "
                                            "of "
                                            "authorship "
                                            "fixed "
                                            "in "
                                            "any "
                                            "tangible "
                                            "medium "
                                            "of "
                                            "expression, "
                                            "now "
                                            "known "
                                            "or "
                                            "later "
                                            "developed, "
                                            "from "
                                            "which "
                                            "they "
                                            "can "
                                            "be "
                                            "perceived, "
                                            "reproduced, "
                                            "or "
                                            "otherwise "
                                            "communicated, "
                                            "either "
                                            "directly "
                                            "or "
                                            "with "
                                            "the "
                                            "aid "
                                            "of "
                                            "a "
                                            "machine "
                                            "or "
                                            "device.",
                                            "prefix": "",
                                            "suffix": "",
                                        }
                                    ],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "In "
                                        "no "
                                        "case "
                                        "does "
                                        "copyright "
                                        "protection "
                                        "for "
                                        "an "
                                        "original "
                                        "work "
                                        "of "
                                        "authorship "
                                        "extend "
                                        "to "
                                        "any "
                                        "idea, "
                                        "procedure, "
                                        "process, "
                                        "system, "
                                        "method "
                                        "of "
                                        "operation, "
                                        "concept, "
                                        "principle, "
                                        "or "
                                        "discovery, "
                                        "regardless "
                                        "of "
                                        "the "
                                        "form "
                                        "in "
                                        "which "
                                        "it "
                                        "is "
                                        "described, "
                                        "explained, "
                                        "illustrated, "
                                        "or "
                                        "embodied "
                                        "in "
                                        "such "
                                        "work.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030580/",
                                        "id": 1030580,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [{"start": 0, "end": None}],
                                    "quotes": [],
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
                                "predicate": {
                                    "content": "${the_java_api} was copyrightable",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was copyrightable",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_language} "
                                    "was a "
                                    "computer "
                                    "program",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java language was a computer program",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was a "
                                    "literal "
                                    "element of "
                                    "${the_java_language}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    },
                                ],
                                "name": "the Java API was a literal "
                                "element of the Java "
                                "language",
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
                                    "node": "/us/usc/t17/s102/a",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Copyright "
                                        "protection "
                                        "subsists, "
                                        "in "
                                        "accordance "
                                        "with "
                                        "this "
                                        "title, "
                                        "in "
                                        "original "
                                        "works "
                                        "of "
                                        "authorship "
                                        "fixed "
                                        "in "
                                        "any "
                                        "tangible "
                                        "medium "
                                        "of "
                                        "expression, "
                                        "now "
                                        "known "
                                        "or "
                                        "later "
                                        "developed, "
                                        "from "
                                        "which "
                                        "they "
                                        "can "
                                        "be "
                                        "perceived, "
                                        "reproduced, "
                                        "or "
                                        "otherwise "
                                        "communicated, "
                                        "either "
                                        "directly "
                                        "or "
                                        "with "
                                        "the "
                                        "aid "
                                        "of "
                                        "a "
                                        "machine "
                                        "or "
                                        "device. "
                                        "Works "
                                        "of "
                                        "authorship "
                                        "include "
                                        "the "
                                        "following "
                                        "categories:",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030579/",
                                        "id": 1030579,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/a",
                                    "children": [
                                        {
                                            "node": "/us/usc/t17/s102/a/1",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "literary works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030571/",
                                                "id": 1030571,
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
                                            "node": "/us/usc/t17/s102/a/2",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "musical "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "words;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030572/",
                                                "id": 1030572,
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
                                            "node": "/us/usc/t17/s102/a/3",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "dramatic "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "music;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030573/",
                                                "id": 1030573,
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
                                            "node": "/us/usc/t17/s102/a/4",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pantomimes "
                                                "and "
                                                "choreographic "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030574/",
                                                "id": 1030574,
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
                                            "node": "/us/usc/t17/s102/a/5",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pictorial, "
                                                "graphic, "
                                                "and "
                                                "sculptural "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030575/",
                                                "id": 1030575,
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
                                            "node": "/us/usc/t17/s102/a/6",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "motion "
                                                "pictures "
                                                "and "
                                                "other "
                                                "audiovisual "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030576/",
                                                "id": 1030576,
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
                                            "node": "/us/usc/t17/s102/a/7",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "sound recordings; and",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030577/",
                                                "id": 1030577,
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
                                            "node": "/us/usc/t17/s102/a/8",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "architectural works.",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030578/",
                                                "id": 1030578,
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
                                            "exact": "Copyright "
                                            "protection "
                                            "subsists, "
                                            "in "
                                            "accordance "
                                            "with "
                                            "this "
                                            "title, "
                                            "in "
                                            "original "
                                            "works "
                                            "of "
                                            "authorship "
                                            "fixed "
                                            "in "
                                            "any "
                                            "tangible "
                                            "medium "
                                            "of "
                                            "expression, "
                                            "now "
                                            "known "
                                            "or "
                                            "later "
                                            "developed, "
                                            "from "
                                            "which "
                                            "they "
                                            "can "
                                            "be "
                                            "perceived, "
                                            "reproduced, "
                                            "or "
                                            "otherwise "
                                            "communicated, "
                                            "either "
                                            "directly "
                                            "or "
                                            "with "
                                            "the "
                                            "aid "
                                            "of "
                                            "a "
                                            "machine "
                                            "or "
                                            "device.",
                                            "prefix": "",
                                            "suffix": "",
                                        }
                                    ],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "In "
                                        "no "
                                        "case "
                                        "does "
                                        "copyright "
                                        "protection "
                                        "for "
                                        "an "
                                        "original "
                                        "work "
                                        "of "
                                        "authorship "
                                        "extend "
                                        "to "
                                        "any "
                                        "idea, "
                                        "procedure, "
                                        "process, "
                                        "system, "
                                        "method "
                                        "of "
                                        "operation, "
                                        "concept, "
                                        "principle, "
                                        "or "
                                        "discovery, "
                                        "regardless "
                                        "of "
                                        "the "
                                        "form "
                                        "in "
                                        "which "
                                        "it "
                                        "is "
                                        "described, "
                                        "explained, "
                                        "illustrated, "
                                        "or "
                                        "embodied "
                                        "in "
                                        "such "
                                        "work.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030580/",
                                        "id": 1030580,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [{"start": 0, "end": None}],
                                    "quotes": [],
                                },
                            }
                        ]
                    },
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
                                    "content": "${the_java_api} "
                                    "was a "
                                    "non-literal "
                                    "element "
                                    "of "
                                    "${the_java_language}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    },
                                ],
                                "name": "the Java API was a "
                                "non-literal element of the "
                                "Java language",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_language} "
                                    "was a "
                                    "computer "
                                    "program",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java language was a computer program",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was the "
                                    "sequence, "
                                    "structure, "
                                    "and "
                                    "organization "
                                    "of "
                                    "${the_java_language}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    },
                                ],
                                "name": "the Java API was the "
                                "sequence, structure, and "
                                "organization of the Java "
                                "language",
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
                                    "node": "/us/usc/t17/s102/a",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Copyright "
                                        "protection "
                                        "subsists, "
                                        "in "
                                        "accordance "
                                        "with "
                                        "this "
                                        "title, "
                                        "in "
                                        "original "
                                        "works "
                                        "of "
                                        "authorship "
                                        "fixed "
                                        "in "
                                        "any "
                                        "tangible "
                                        "medium "
                                        "of "
                                        "expression, "
                                        "now "
                                        "known "
                                        "or "
                                        "later "
                                        "developed, "
                                        "from "
                                        "which "
                                        "they "
                                        "can "
                                        "be "
                                        "perceived, "
                                        "reproduced, "
                                        "or "
                                        "otherwise "
                                        "communicated, "
                                        "either "
                                        "directly "
                                        "or "
                                        "with "
                                        "the "
                                        "aid "
                                        "of "
                                        "a "
                                        "machine "
                                        "or "
                                        "device. "
                                        "Works "
                                        "of "
                                        "authorship "
                                        "include "
                                        "the "
                                        "following "
                                        "categories:",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030579/",
                                        "id": 1030579,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/a",
                                    "children": [
                                        {
                                            "node": "/us/usc/t17/s102/a/1",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "literary works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030571/",
                                                "id": 1030571,
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
                                            "node": "/us/usc/t17/s102/a/2",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "musical "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "words;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030572/",
                                                "id": 1030572,
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
                                            "node": "/us/usc/t17/s102/a/3",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "dramatic "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "music;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030573/",
                                                "id": 1030573,
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
                                            "node": "/us/usc/t17/s102/a/4",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pantomimes "
                                                "and "
                                                "choreographic "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030574/",
                                                "id": 1030574,
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
                                            "node": "/us/usc/t17/s102/a/5",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pictorial, "
                                                "graphic, "
                                                "and "
                                                "sculptural "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030575/",
                                                "id": 1030575,
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
                                            "node": "/us/usc/t17/s102/a/6",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "motion "
                                                "pictures "
                                                "and "
                                                "other "
                                                "audiovisual "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030576/",
                                                "id": 1030576,
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
                                            "node": "/us/usc/t17/s102/a/7",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "sound recordings; and",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030577/",
                                                "id": 1030577,
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
                                            "node": "/us/usc/t17/s102/a/8",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "architectural works.",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030578/",
                                                "id": 1030578,
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
                                            "exact": "Copyright "
                                            "protection "
                                            "subsists, "
                                            "in "
                                            "accordance "
                                            "with "
                                            "this "
                                            "title, "
                                            "in "
                                            "original "
                                            "works "
                                            "of "
                                            "authorship "
                                            "fixed "
                                            "in "
                                            "any "
                                            "tangible "
                                            "medium "
                                            "of "
                                            "expression, "
                                            "now "
                                            "known "
                                            "or "
                                            "later "
                                            "developed, "
                                            "from "
                                            "which "
                                            "they "
                                            "can "
                                            "be "
                                            "perceived, "
                                            "reproduced, "
                                            "or "
                                            "otherwise "
                                            "communicated, "
                                            "either "
                                            "directly "
                                            "or "
                                            "with "
                                            "the "
                                            "aid "
                                            "of "
                                            "a "
                                            "machine "
                                            "or "
                                            "device.",
                                            "prefix": "",
                                            "suffix": "",
                                        }
                                    ],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "In "
                                        "no "
                                        "case "
                                        "does "
                                        "copyright "
                                        "protection "
                                        "for "
                                        "an "
                                        "original "
                                        "work "
                                        "of "
                                        "authorship "
                                        "extend "
                                        "to "
                                        "any "
                                        "idea, "
                                        "procedure, "
                                        "process, "
                                        "system, "
                                        "method "
                                        "of "
                                        "operation, "
                                        "concept, "
                                        "principle, "
                                        "or "
                                        "discovery, "
                                        "regardless "
                                        "of "
                                        "the "
                                        "form "
                                        "in "
                                        "which "
                                        "it "
                                        "is "
                                        "described, "
                                        "explained, "
                                        "illustrated, "
                                        "or "
                                        "embodied "
                                        "in "
                                        "such "
                                        "work.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030580/",
                                        "id": 1030580,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [{"start": 0, "end": None}],
                                    "quotes": [],
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
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was a "
                                    "non-literal "
                                    "element "
                                    "of "
                                    "${the_java_language}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    },
                                ],
                                "name": "the Java API was a "
                                "non-literal element of the "
                                "Java language",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_language} "
                                    "was a "
                                    "computer "
                                    "program",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java language was a computer program",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was the "
                                    "user "
                                    "interface "
                                    "of "
                                    "${the_java_language}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    },
                                ],
                                "name": "the Java API was the user "
                                "interface of the Java "
                                "language",
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
                                    "node": "/us/usc/t17/s102/a",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Copyright "
                                        "protection "
                                        "subsists, "
                                        "in "
                                        "accordance "
                                        "with "
                                        "this "
                                        "title, "
                                        "in "
                                        "original "
                                        "works "
                                        "of "
                                        "authorship "
                                        "fixed "
                                        "in "
                                        "any "
                                        "tangible "
                                        "medium "
                                        "of "
                                        "expression, "
                                        "now "
                                        "known "
                                        "or "
                                        "later "
                                        "developed, "
                                        "from "
                                        "which "
                                        "they "
                                        "can "
                                        "be "
                                        "perceived, "
                                        "reproduced, "
                                        "or "
                                        "otherwise "
                                        "communicated, "
                                        "either "
                                        "directly "
                                        "or "
                                        "with "
                                        "the "
                                        "aid "
                                        "of "
                                        "a "
                                        "machine "
                                        "or "
                                        "device. "
                                        "Works "
                                        "of "
                                        "authorship "
                                        "include "
                                        "the "
                                        "following "
                                        "categories:",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030579/",
                                        "id": 1030579,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/a",
                                    "children": [
                                        {
                                            "node": "/us/usc/t17/s102/a/1",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "literary works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030571/",
                                                "id": 1030571,
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
                                            "node": "/us/usc/t17/s102/a/2",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "musical "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "words;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030572/",
                                                "id": 1030572,
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
                                            "node": "/us/usc/t17/s102/a/3",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "dramatic "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "music;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030573/",
                                                "id": 1030573,
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
                                            "node": "/us/usc/t17/s102/a/4",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pantomimes "
                                                "and "
                                                "choreographic "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030574/",
                                                "id": 1030574,
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
                                            "node": "/us/usc/t17/s102/a/5",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pictorial, "
                                                "graphic, "
                                                "and "
                                                "sculptural "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030575/",
                                                "id": 1030575,
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
                                            "node": "/us/usc/t17/s102/a/6",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "motion "
                                                "pictures "
                                                "and "
                                                "other "
                                                "audiovisual "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030576/",
                                                "id": 1030576,
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
                                            "node": "/us/usc/t17/s102/a/7",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "sound recordings; and",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030577/",
                                                "id": 1030577,
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
                                            "node": "/us/usc/t17/s102/a/8",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "architectural works.",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030578/",
                                                "id": 1030578,
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
                                            "exact": "Copyright "
                                            "protection "
                                            "subsists, "
                                            "in "
                                            "accordance "
                                            "with "
                                            "this "
                                            "title, "
                                            "in "
                                            "original "
                                            "works "
                                            "of "
                                            "authorship "
                                            "fixed "
                                            "in "
                                            "any "
                                            "tangible "
                                            "medium "
                                            "of "
                                            "expression, "
                                            "now "
                                            "known "
                                            "or "
                                            "later "
                                            "developed, "
                                            "from "
                                            "which "
                                            "they "
                                            "can "
                                            "be "
                                            "perceived, "
                                            "reproduced, "
                                            "or "
                                            "otherwise "
                                            "communicated, "
                                            "either "
                                            "directly "
                                            "or "
                                            "with "
                                            "the "
                                            "aid "
                                            "of "
                                            "a "
                                            "machine "
                                            "or "
                                            "device.",
                                            "prefix": "",
                                            "suffix": "",
                                        }
                                    ],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "In "
                                        "no "
                                        "case "
                                        "does "
                                        "copyright "
                                        "protection "
                                        "for "
                                        "an "
                                        "original "
                                        "work "
                                        "of "
                                        "authorship "
                                        "extend "
                                        "to "
                                        "any "
                                        "idea, "
                                        "procedure, "
                                        "process, "
                                        "system, "
                                        "method "
                                        "of "
                                        "operation, "
                                        "concept, "
                                        "principle, "
                                        "or "
                                        "discovery, "
                                        "regardless "
                                        "of "
                                        "the "
                                        "form "
                                        "in "
                                        "which "
                                        "it "
                                        "is "
                                        "described, "
                                        "explained, "
                                        "illustrated, "
                                        "or "
                                        "embodied "
                                        "in "
                                        "such "
                                        "work.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030580/",
                                        "id": 1030580,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [{"start": 0, "end": None}],
                                    "quotes": [],
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
                                "predicate": {
                                    "content": "${the_java_api} was copyrightable",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was copyrightable",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_language} "
                                    "was a "
                                    "computer "
                                    "program",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java language was a computer program",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was a "
                                    "non-literal "
                                    "element of "
                                    "${the_java_language}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    },
                                ],
                                "name": "the Java API was a "
                                "non-literal element of the "
                                "Java language",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was the "
                                    "expression "
                                    "of an idea",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was the expression of an idea",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} was an idea",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "false the Java API was an idea",
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
                                    "node": "/us/usc/t17/s102/a",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Copyright "
                                        "protection "
                                        "subsists, "
                                        "in "
                                        "accordance "
                                        "with "
                                        "this "
                                        "title, "
                                        "in "
                                        "original "
                                        "works "
                                        "of "
                                        "authorship "
                                        "fixed "
                                        "in "
                                        "any "
                                        "tangible "
                                        "medium "
                                        "of "
                                        "expression, "
                                        "now "
                                        "known "
                                        "or "
                                        "later "
                                        "developed, "
                                        "from "
                                        "which "
                                        "they "
                                        "can "
                                        "be "
                                        "perceived, "
                                        "reproduced, "
                                        "or "
                                        "otherwise "
                                        "communicated, "
                                        "either "
                                        "directly "
                                        "or "
                                        "with "
                                        "the "
                                        "aid "
                                        "of "
                                        "a "
                                        "machine "
                                        "or "
                                        "device. "
                                        "Works "
                                        "of "
                                        "authorship "
                                        "include "
                                        "the "
                                        "following "
                                        "categories:",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030579/",
                                        "id": 1030579,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/a",
                                    "children": [
                                        {
                                            "node": "/us/usc/t17/s102/a/1",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "literary works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030571/",
                                                "id": 1030571,
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
                                            "node": "/us/usc/t17/s102/a/2",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "musical "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "words;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030572/",
                                                "id": 1030572,
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
                                            "node": "/us/usc/t17/s102/a/3",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "dramatic "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "music;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030573/",
                                                "id": 1030573,
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
                                            "node": "/us/usc/t17/s102/a/4",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pantomimes "
                                                "and "
                                                "choreographic "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030574/",
                                                "id": 1030574,
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
                                            "node": "/us/usc/t17/s102/a/5",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pictorial, "
                                                "graphic, "
                                                "and "
                                                "sculptural "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030575/",
                                                "id": 1030575,
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
                                            "node": "/us/usc/t17/s102/a/6",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "motion "
                                                "pictures "
                                                "and "
                                                "other "
                                                "audiovisual "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030576/",
                                                "id": 1030576,
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
                                            "node": "/us/usc/t17/s102/a/7",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "sound recordings; and",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030577/",
                                                "id": 1030577,
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
                                            "node": "/us/usc/t17/s102/a/8",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "architectural works.",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030578/",
                                                "id": 1030578,
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
                                            "exact": "Copyright "
                                            "protection "
                                            "subsists, "
                                            "in "
                                            "accordance "
                                            "with "
                                            "this "
                                            "title, "
                                            "in "
                                            "original "
                                            "works "
                                            "of "
                                            "authorship "
                                            "fixed "
                                            "in "
                                            "any "
                                            "tangible "
                                            "medium "
                                            "of "
                                            "expression, "
                                            "now "
                                            "known "
                                            "or "
                                            "later "
                                            "developed, "
                                            "from "
                                            "which "
                                            "they "
                                            "can "
                                            "be "
                                            "perceived, "
                                            "reproduced, "
                                            "or "
                                            "otherwise "
                                            "communicated, "
                                            "either "
                                            "directly "
                                            "or "
                                            "with "
                                            "the "
                                            "aid "
                                            "of "
                                            "a "
                                            "machine "
                                            "or "
                                            "device.",
                                            "prefix": "",
                                            "suffix": "",
                                        }
                                    ],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "In "
                                        "no "
                                        "case "
                                        "does "
                                        "copyright "
                                        "protection "
                                        "for "
                                        "an "
                                        "original "
                                        "work "
                                        "of "
                                        "authorship "
                                        "extend "
                                        "to "
                                        "any "
                                        "idea, "
                                        "procedure, "
                                        "process, "
                                        "system, "
                                        "method "
                                        "of "
                                        "operation, "
                                        "concept, "
                                        "principle, "
                                        "or "
                                        "discovery, "
                                        "regardless "
                                        "of "
                                        "the "
                                        "form "
                                        "in "
                                        "which "
                                        "it "
                                        "is "
                                        "described, "
                                        "explained, "
                                        "illustrated, "
                                        "or "
                                        "embodied "
                                        "in "
                                        "such "
                                        "work.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030580/",
                                        "id": 1030580,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [{"start": 0, "end": None}],
                                    "quotes": [],
                                },
                            }
                        ]
                    },
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
                                    "content": "${the_java_api} was copyrightable",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "false the Java API was copyrightable",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_language} "
                                    "was a "
                                    "computer "
                                    "program",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java language was a computer program",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was a "
                                    "non-literal "
                                    "element of "
                                    "${the_java_language}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    },
                                ],
                                "name": "the Java API was a "
                                "non-literal element of the "
                                "Java language",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was the "
                                    "expression "
                                    "of an idea",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "false the Java API was the "
                                "expression of an idea",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} was an idea",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was an idea",
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
                                    "node": "/us/usc/t17/s102/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "In "
                                        "no "
                                        "case "
                                        "does "
                                        "copyright "
                                        "protection "
                                        "for "
                                        "an "
                                        "original "
                                        "work "
                                        "of "
                                        "authorship "
                                        "extend "
                                        "to "
                                        "any "
                                        "idea, "
                                        "procedure, "
                                        "process, "
                                        "system, "
                                        "method "
                                        "of "
                                        "operation, "
                                        "concept, "
                                        "principle, "
                                        "or "
                                        "discovery, "
                                        "regardless "
                                        "of "
                                        "the "
                                        "form "
                                        "in "
                                        "which "
                                        "it "
                                        "is "
                                        "described, "
                                        "explained, "
                                        "illustrated, "
                                        "or "
                                        "embodied "
                                        "in "
                                        "such "
                                        "work.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030580/",
                                        "id": 1030580,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [{"start": 0, "end": None}],
                                    "quotes": [],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/a",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Copyright "
                                        "protection "
                                        "subsists, "
                                        "in "
                                        "accordance "
                                        "with "
                                        "this "
                                        "title, "
                                        "in "
                                        "original "
                                        "works "
                                        "of "
                                        "authorship "
                                        "fixed "
                                        "in "
                                        "any "
                                        "tangible "
                                        "medium "
                                        "of "
                                        "expression, "
                                        "now "
                                        "known "
                                        "or "
                                        "later "
                                        "developed, "
                                        "from "
                                        "which "
                                        "they "
                                        "can "
                                        "be "
                                        "perceived, "
                                        "reproduced, "
                                        "or "
                                        "otherwise "
                                        "communicated, "
                                        "either "
                                        "directly "
                                        "or "
                                        "with "
                                        "the "
                                        "aid "
                                        "of "
                                        "a "
                                        "machine "
                                        "or "
                                        "device. "
                                        "Works "
                                        "of "
                                        "authorship "
                                        "include "
                                        "the "
                                        "following "
                                        "categories:",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030579/",
                                        "id": 1030579,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/a",
                                    "children": [
                                        {
                                            "node": "/us/usc/t17/s102/a/1",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "literary works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030571/",
                                                "id": 1030571,
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
                                            "node": "/us/usc/t17/s102/a/2",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "musical "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "words;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030572/",
                                                "id": 1030572,
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
                                            "node": "/us/usc/t17/s102/a/3",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "dramatic "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "music;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030573/",
                                                "id": 1030573,
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
                                            "node": "/us/usc/t17/s102/a/4",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pantomimes "
                                                "and "
                                                "choreographic "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030574/",
                                                "id": 1030574,
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
                                            "node": "/us/usc/t17/s102/a/5",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pictorial, "
                                                "graphic, "
                                                "and "
                                                "sculptural "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030575/",
                                                "id": 1030575,
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
                                            "node": "/us/usc/t17/s102/a/6",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "motion "
                                                "pictures "
                                                "and "
                                                "other "
                                                "audiovisual "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030576/",
                                                "id": 1030576,
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
                                            "node": "/us/usc/t17/s102/a/7",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "sound recordings; and",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030577/",
                                                "id": 1030577,
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
                                            "node": "/us/usc/t17/s102/a/8",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "architectural works.",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030578/",
                                                "id": 1030578,
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
                                            "exact": "Copyright "
                                            "protection "
                                            "subsists, "
                                            "in "
                                            "accordance "
                                            "with "
                                            "this "
                                            "title, "
                                            "in "
                                            "original "
                                            "works "
                                            "of "
                                            "authorship "
                                            "fixed "
                                            "in "
                                            "any "
                                            "tangible "
                                            "medium "
                                            "of "
                                            "expression, "
                                            "now "
                                            "known "
                                            "or "
                                            "later "
                                            "developed, "
                                            "from "
                                            "which "
                                            "they "
                                            "can "
                                            "be "
                                            "perceived, "
                                            "reproduced, "
                                            "or "
                                            "otherwise "
                                            "communicated, "
                                            "either "
                                            "directly "
                                            "or "
                                            "with "
                                            "the "
                                            "aid "
                                            "of "
                                            "a "
                                            "machine "
                                            "or "
                                            "device.",
                                            "prefix": "",
                                            "suffix": "",
                                        }
                                    ],
                                },
                            }
                        ]
                    },
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
                                    "content": "${the_java_api} was copyrightable",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was copyrightable",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_language} "
                                    "was a "
                                    "computer "
                                    "program",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java language was a computer program",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was a set "
                                    "of "
                                    "application "
                                    "programming "
                                    "interface "
                                    "declarations",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was a set of "
                                "application programming "
                                "interface declarations",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} was an original work",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was an original work",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was a "
                                    "non-literal "
                                    "element of "
                                    "${the_java_language}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    },
                                ],
                                "name": "the Java API was a "
                                "non-literal element of the "
                                "Java language",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was the "
                                    "expression "
                                    "of an idea",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was the expression of an idea",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was "
                                    "essentially "
                                    "the only "
                                    "way to "
                                    "express "
                                    "the idea "
                                    "that it "
                                    "embodied",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "false the Java API was "
                                "essentially the only way to "
                                "express the idea that it "
                                "embodied",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} was creative",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was creative",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "it was "
                                    "possible "
                                    "to use "
                                    "${the_java_language} "
                                    "without "
                                    "copying "
                                    "${the_java_api}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                ],
                                "name": "it was possible to use the "
                                "Java language without "
                                "copying the Java API",
                                "standard_of_proof": None,
                            },
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was a "
                                    "method of "
                                    "operation",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was a method of operation",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "contained "
                                    "short "
                                    "phrases",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API contained short phrases",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "became so "
                                    "popular "
                                    "that it "
                                    "was the "
                                    "industry "
                                    "standard",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API became so "
                                "popular that it was the "
                                "industry standard",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "there was "
                                    "a "
                                    "preexisting "
                                    "community "
                                    "of "
                                    "programmers "
                                    "accustomed "
                                    "to using "
                                    "${the_java_api}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "there was a preexisting "
                                "community of programmers "
                                "accustomed to using the "
                                "Java API",
                                "standard_of_proof": None,
                            },
                        ],
                        "name": "",
                    },
                    "enactments": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/a",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Copyright "
                                        "protection "
                                        "subsists, "
                                        "in "
                                        "accordance "
                                        "with "
                                        "this "
                                        "title, "
                                        "in "
                                        "original "
                                        "works "
                                        "of "
                                        "authorship "
                                        "fixed "
                                        "in "
                                        "any "
                                        "tangible "
                                        "medium "
                                        "of "
                                        "expression, "
                                        "now "
                                        "known "
                                        "or "
                                        "later "
                                        "developed, "
                                        "from "
                                        "which "
                                        "they "
                                        "can "
                                        "be "
                                        "perceived, "
                                        "reproduced, "
                                        "or "
                                        "otherwise "
                                        "communicated, "
                                        "either "
                                        "directly "
                                        "or "
                                        "with "
                                        "the "
                                        "aid "
                                        "of "
                                        "a "
                                        "machine "
                                        "or "
                                        "device. "
                                        "Works "
                                        "of "
                                        "authorship "
                                        "include "
                                        "the "
                                        "following "
                                        "categories:",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030579/",
                                        "id": 1030579,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/a",
                                    "children": [
                                        {
                                            "node": "/us/usc/t17/s102/a/1",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "literary works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030571/",
                                                "id": 1030571,
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
                                            "node": "/us/usc/t17/s102/a/2",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "musical "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "words;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030572/",
                                                "id": 1030572,
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
                                            "node": "/us/usc/t17/s102/a/3",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "dramatic "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "music;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030573/",
                                                "id": 1030573,
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
                                            "node": "/us/usc/t17/s102/a/4",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pantomimes "
                                                "and "
                                                "choreographic "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030574/",
                                                "id": 1030574,
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
                                            "node": "/us/usc/t17/s102/a/5",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pictorial, "
                                                "graphic, "
                                                "and "
                                                "sculptural "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030575/",
                                                "id": 1030575,
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
                                            "node": "/us/usc/t17/s102/a/6",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "motion "
                                                "pictures "
                                                "and "
                                                "other "
                                                "audiovisual "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030576/",
                                                "id": 1030576,
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
                                            "node": "/us/usc/t17/s102/a/7",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "sound recordings; and",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030577/",
                                                "id": 1030577,
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
                                            "node": "/us/usc/t17/s102/a/8",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "architectural works.",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030578/",
                                                "id": 1030578,
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
                                            "exact": "Copyright "
                                            "protection "
                                            "subsists, "
                                            "in "
                                            "accordance "
                                            "with "
                                            "this "
                                            "title, "
                                            "in "
                                            "original "
                                            "works "
                                            "of "
                                            "authorship "
                                            "fixed "
                                            "in "
                                            "any "
                                            "tangible "
                                            "medium "
                                            "of "
                                            "expression, "
                                            "now "
                                            "known "
                                            "or "
                                            "later "
                                            "developed, "
                                            "from "
                                            "which "
                                            "they "
                                            "can "
                                            "be "
                                            "perceived, "
                                            "reproduced, "
                                            "or "
                                            "otherwise "
                                            "communicated, "
                                            "either "
                                            "directly "
                                            "or "
                                            "with "
                                            "the "
                                            "aid "
                                            "of "
                                            "a "
                                            "machine "
                                            "or "
                                            "device.",
                                            "prefix": "",
                                            "suffix": "",
                                        }
                                    ],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "In "
                                        "no "
                                        "case "
                                        "does "
                                        "copyright "
                                        "protection "
                                        "for "
                                        "an "
                                        "original "
                                        "work "
                                        "of "
                                        "authorship "
                                        "extend "
                                        "to "
                                        "any "
                                        "idea, "
                                        "procedure, "
                                        "process, "
                                        "system, "
                                        "method "
                                        "of "
                                        "operation, "
                                        "concept, "
                                        "principle, "
                                        "or "
                                        "discovery, "
                                        "regardless "
                                        "of "
                                        "the "
                                        "form "
                                        "in "
                                        "which "
                                        "it "
                                        "is "
                                        "described, "
                                        "explained, "
                                        "illustrated, "
                                        "or "
                                        "embodied "
                                        "in "
                                        "such "
                                        "work.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030580/",
                                        "id": 1030580,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "In "
                                            "no "
                                            "case "
                                            "does "
                                            "copyright "
                                            "protection "
                                            "for "
                                            "an "
                                            "original "
                                            "work "
                                            "of "
                                            "authorship "
                                            "extend "
                                            "to "
                                            "any",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                        {
                                            "exact": "method of operation",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                    ],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us/cfr/t37/s202.1",
                                    "start_date": datetime.date(1992, 2, 21),
                                    "heading": "Material not subject to copyright.",
                                    "text_version": {
                                        "content": "The "
                                        "following "
                                        "are "
                                        "examples "
                                        "of "
                                        "works "
                                        "not "
                                        "subject "
                                        "to "
                                        "copyright "
                                        "and "
                                        "applications "
                                        "for "
                                        "registration "
                                        "of "
                                        "such "
                                        "works "
                                        "cannot "
                                        "be "
                                        "entertained:",
                                        "url": None,
                                        "id": None,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/cfr/t37/s202.1@1992-02-21",
                                    "children": [
                                        {
                                            "node": "/us/cfr/t37/s202.1/a",
                                            "start_date": datetime.date(1992, 2, 21),
                                            "heading": "",
                                            "text_version": {
                                                "content": "Words "
                                                "and "
                                                "short "
                                                "phrases "
                                                "such "
                                                "as "
                                                "names, "
                                                "titles, "
                                                "and "
                                                "slogans; "
                                                "familiar "
                                                "symbols "
                                                "or "
                                                "designs; "
                                                "mere "
                                                "variations "
                                                "of "
                                                "typographic "
                                                "ornamentation, "
                                                "lettering "
                                                "or "
                                                "coloring; "
                                                "mere "
                                                "listing "
                                                "of "
                                                "ingredients "
                                                "or "
                                                "contents;",
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
                                            "node": "/us/cfr/t37/s202.1/b",
                                            "start_date": datetime.date(1992, 2, 21),
                                            "heading": "",
                                            "text_version": {
                                                "content": "Ideas, "
                                                "plans, "
                                                "methods, "
                                                "systems, "
                                                "or "
                                                "devices, "
                                                "as "
                                                "distinguished "
                                                "from "
                                                "the "
                                                "particular "
                                                "manner "
                                                "in "
                                                "which "
                                                "they "
                                                "are "
                                                "expressed "
                                                "or "
                                                "described "
                                                "in "
                                                "a "
                                                "writing;  ",
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
                                            "node": "/us/cfr/t37/s202.1/c",
                                            "start_date": datetime.date(1992, 2, 21),
                                            "heading": "",
                                            "text_version": {
                                                "content": "Blank "
                                                "forms, "
                                                "such "
                                                "as "
                                                "time "
                                                "cards, "
                                                "graph "
                                                "paper, "
                                                "account "
                                                "books, "
                                                "diaries, "
                                                "bank "
                                                "checks, "
                                                "scorecards, "
                                                "address "
                                                "books, "
                                                "report "
                                                "forms, "
                                                "order "
                                                "forms "
                                                "and "
                                                "the "
                                                "like, "
                                                "which "
                                                "are "
                                                "designed "
                                                "for "
                                                "recording "
                                                "information "
                                                "and "
                                                "do "
                                                "not "
                                                "in "
                                                "themselves "
                                                "convey "
                                                "information;",
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
                                            "node": "/us/cfr/t37/s202.1/d",
                                            "start_date": datetime.date(1992, 2, 21),
                                            "heading": "",
                                            "text_version": {
                                                "content": "Works "
                                                "consisting "
                                                "entirely "
                                                "of "
                                                "information "
                                                "that "
                                                "is "
                                                "common "
                                                "property "
                                                "containing "
                                                "no "
                                                "original "
                                                "authorship, "
                                                "such "
                                                "as, "
                                                "for "
                                                "example: "
                                                "Standard "
                                                "calendars, "
                                                "height "
                                                "and "
                                                "weight "
                                                "charts, "
                                                "tape "
                                                "measures "
                                                "and "
                                                "rulers, "
                                                "schedules "
                                                "of "
                                                "sporting "
                                                "events, "
                                                "and "
                                                "lists "
                                                "or "
                                                "tables "
                                                "taken "
                                                "from "
                                                "public "
                                                "documents "
                                                "or "
                                                "other "
                                                "common "
                                                "sources.",
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
                                            "node": "/us/cfr/t37/s202.1/e",
                                            "start_date": datetime.date(1992, 2, 21),
                                            "heading": "",
                                            "text_version": {
                                                "content": "Typeface as typeface.",
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
                                            "suffix": "familiar symbols or designs",
                                        }
                                    ],
                                },
                            },
                        ]
                    },
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
                                    "content": "${google} "
                                    "infringed "
                                    "the "
                                    "copyright "
                                    "on "
                                    "${the_java_api}",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Google",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                ],
                                "name": "false Google infringed the "
                                "copyright on the Java API",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} was a scene a faire",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was a scene a faire",
                                "standard_of_proof": None,
                            }
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} was copyrightable",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was copyrightable",
                                "standard_of_proof": None,
                            }
                        ],
                        "name": "",
                    },
                    "enactments": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "In "
                                        "no "
                                        "case "
                                        "does "
                                        "copyright "
                                        "protection "
                                        "for "
                                        "an "
                                        "original "
                                        "work "
                                        "of "
                                        "authorship "
                                        "extend "
                                        "to "
                                        "any "
                                        "idea, "
                                        "procedure, "
                                        "process, "
                                        "system, "
                                        "method "
                                        "of "
                                        "operation, "
                                        "concept, "
                                        "principle, "
                                        "or "
                                        "discovery, "
                                        "regardless "
                                        "of "
                                        "the "
                                        "form "
                                        "in "
                                        "which "
                                        "it "
                                        "is "
                                        "described, "
                                        "explained, "
                                        "illustrated, "
                                        "or "
                                        "embodied "
                                        "in "
                                        "such "
                                        "work.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030580/",
                                        "id": 1030580,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [{"start": 0, "end": None}],
                                    "quotes": [],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/a",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Copyright "
                                        "protection "
                                        "subsists, "
                                        "in "
                                        "accordance "
                                        "with "
                                        "this "
                                        "title, "
                                        "in "
                                        "original "
                                        "works "
                                        "of "
                                        "authorship "
                                        "fixed "
                                        "in "
                                        "any "
                                        "tangible "
                                        "medium "
                                        "of "
                                        "expression, "
                                        "now "
                                        "known "
                                        "or "
                                        "later "
                                        "developed, "
                                        "from "
                                        "which "
                                        "they "
                                        "can "
                                        "be "
                                        "perceived, "
                                        "reproduced, "
                                        "or "
                                        "otherwise "
                                        "communicated, "
                                        "either "
                                        "directly "
                                        "or "
                                        "with "
                                        "the "
                                        "aid "
                                        "of "
                                        "a "
                                        "machine "
                                        "or "
                                        "device. "
                                        "Works "
                                        "of "
                                        "authorship "
                                        "include "
                                        "the "
                                        "following "
                                        "categories:",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030579/",
                                        "id": 1030579,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/a",
                                    "children": [
                                        {
                                            "node": "/us/usc/t17/s102/a/1",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "literary works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030571/",
                                                "id": 1030571,
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
                                            "node": "/us/usc/t17/s102/a/2",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "musical "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "words;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030572/",
                                                "id": 1030572,
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
                                            "node": "/us/usc/t17/s102/a/3",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "dramatic "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "music;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030573/",
                                                "id": 1030573,
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
                                            "node": "/us/usc/t17/s102/a/4",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pantomimes "
                                                "and "
                                                "choreographic "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030574/",
                                                "id": 1030574,
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
                                            "node": "/us/usc/t17/s102/a/5",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pictorial, "
                                                "graphic, "
                                                "and "
                                                "sculptural "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030575/",
                                                "id": 1030575,
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
                                            "node": "/us/usc/t17/s102/a/6",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "motion "
                                                "pictures "
                                                "and "
                                                "other "
                                                "audiovisual "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030576/",
                                                "id": 1030576,
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
                                            "node": "/us/usc/t17/s102/a/7",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "sound recordings; and",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030577/",
                                                "id": 1030577,
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
                                            "node": "/us/usc/t17/s102/a/8",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "architectural works.",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030578/",
                                                "id": 1030578,
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
                                            "exact": "Copyright "
                                            "protection "
                                            "subsists, "
                                            "in "
                                            "accordance "
                                            "with "
                                            "this "
                                            "title, "
                                            "in "
                                            "original "
                                            "works "
                                            "of "
                                            "authorship "
                                            "fixed "
                                            "in "
                                            "any "
                                            "tangible "
                                            "medium "
                                            "of "
                                            "expression, "
                                            "now "
                                            "known "
                                            "or "
                                            "later "
                                            "developed, "
                                            "from "
                                            "which "
                                            "they "
                                            "can "
                                            "be "
                                            "perceived, "
                                            "reproduced, "
                                            "or "
                                            "otherwise "
                                            "communicated, "
                                            "either "
                                            "directly "
                                            "or "
                                            "with "
                                            "the "
                                            "aid "
                                            "of "
                                            "a "
                                            "machine "
                                            "or "
                                            "device.",
                                            "prefix": "",
                                            "suffix": "",
                                        }
                                    ],
                                },
                            }
                        ]
                    },
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
                                    "content": "${google} "
                                    "infringed "
                                    "the "
                                    "copyright "
                                    "on "
                                    "${the_java_api}",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Google",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                ],
                                "name": "false Google infringed the "
                                "copyright on the Java API",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was "
                                    "essentially "
                                    "the only "
                                    "way to "
                                    "express "
                                    "the idea "
                                    "that it "
                                    "embodied",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was "
                                "essentially the only way to "
                                "express the idea that it "
                                "embodied",
                                "standard_of_proof": None,
                            }
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} was copyrightable",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was copyrightable",
                                "standard_of_proof": None,
                            }
                        ],
                        "name": "",
                    },
                    "enactments": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "In "
                                        "no "
                                        "case "
                                        "does "
                                        "copyright "
                                        "protection "
                                        "for "
                                        "an "
                                        "original "
                                        "work "
                                        "of "
                                        "authorship "
                                        "extend "
                                        "to "
                                        "any "
                                        "idea, "
                                        "procedure, "
                                        "process, "
                                        "system, "
                                        "method "
                                        "of "
                                        "operation, "
                                        "concept, "
                                        "principle, "
                                        "or "
                                        "discovery, "
                                        "regardless "
                                        "of "
                                        "the "
                                        "form "
                                        "in "
                                        "which "
                                        "it "
                                        "is "
                                        "described, "
                                        "explained, "
                                        "illustrated, "
                                        "or "
                                        "embodied "
                                        "in "
                                        "such "
                                        "work.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030580/",
                                        "id": 1030580,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [{"start": 0, "end": None}],
                                    "quotes": [],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/a",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Copyright "
                                        "protection "
                                        "subsists, "
                                        "in "
                                        "accordance "
                                        "with "
                                        "this "
                                        "title, "
                                        "in "
                                        "original "
                                        "works "
                                        "of "
                                        "authorship "
                                        "fixed "
                                        "in "
                                        "any "
                                        "tangible "
                                        "medium "
                                        "of "
                                        "expression, "
                                        "now "
                                        "known "
                                        "or "
                                        "later "
                                        "developed, "
                                        "from "
                                        "which "
                                        "they "
                                        "can "
                                        "be "
                                        "perceived, "
                                        "reproduced, "
                                        "or "
                                        "otherwise "
                                        "communicated, "
                                        "either "
                                        "directly "
                                        "or "
                                        "with "
                                        "the "
                                        "aid "
                                        "of "
                                        "a "
                                        "machine "
                                        "or "
                                        "device. "
                                        "Works "
                                        "of "
                                        "authorship "
                                        "include "
                                        "the "
                                        "following "
                                        "categories:",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030579/",
                                        "id": 1030579,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/a",
                                    "children": [
                                        {
                                            "node": "/us/usc/t17/s102/a/1",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "literary works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030571/",
                                                "id": 1030571,
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
                                            "node": "/us/usc/t17/s102/a/2",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "musical "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "words;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030572/",
                                                "id": 1030572,
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
                                            "node": "/us/usc/t17/s102/a/3",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "dramatic "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "music;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030573/",
                                                "id": 1030573,
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
                                            "node": "/us/usc/t17/s102/a/4",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pantomimes "
                                                "and "
                                                "choreographic "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030574/",
                                                "id": 1030574,
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
                                            "node": "/us/usc/t17/s102/a/5",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pictorial, "
                                                "graphic, "
                                                "and "
                                                "sculptural "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030575/",
                                                "id": 1030575,
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
                                            "node": "/us/usc/t17/s102/a/6",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "motion "
                                                "pictures "
                                                "and "
                                                "other "
                                                "audiovisual "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030576/",
                                                "id": 1030576,
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
                                            "node": "/us/usc/t17/s102/a/7",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "sound recordings; and",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030577/",
                                                "id": 1030577,
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
                                            "node": "/us/usc/t17/s102/a/8",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "architectural works.",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030578/",
                                                "id": 1030578,
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
                                            "exact": "Copyright "
                                            "protection "
                                            "subsists, "
                                            "in "
                                            "accordance "
                                            "with "
                                            "this "
                                            "title, "
                                            "in "
                                            "original "
                                            "works "
                                            "of "
                                            "authorship "
                                            "fixed "
                                            "in "
                                            "any "
                                            "tangible "
                                            "medium "
                                            "of "
                                            "expression, "
                                            "now "
                                            "known "
                                            "or "
                                            "later "
                                            "developed, "
                                            "from "
                                            "which "
                                            "they "
                                            "can "
                                            "be "
                                            "perceived, "
                                            "reproduced, "
                                            "or "
                                            "otherwise "
                                            "communicated, "
                                            "either "
                                            "directly "
                                            "or "
                                            "with "
                                            "the "
                                            "aid "
                                            "of "
                                            "a "
                                            "machine "
                                            "or "
                                            "device.",
                                            "prefix": "",
                                            "suffix": "",
                                        }
                                    ],
                                },
                            }
                        ]
                    },
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
                                    "content": "${google} "
                                    "infringed "
                                    "the "
                                    "copyright "
                                    "on "
                                    "${the_java_api}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Google",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                ],
                                "name": "Google infringed the "
                                "copyright on the Java API",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} was copyrightable",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was copyrightable",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "absent": {
                                    "generic": False,
                                    "predicate": {
                                        "content": "${the_java_api} "
                                        "was "
                                        "essentially "
                                        "the "
                                        "only "
                                        "way "
                                        "to "
                                        "express "
                                        "the "
                                        "idea "
                                        "that "
                                        "it "
                                        "embodied",
                                        "truth": True,
                                    },
                                    "terms": [
                                        {
                                            "generic": True,
                                            "name": "the Java API",
                                            "plural": False,
                                        }
                                    ],
                                    "name": "the Java API was "
                                    "essentially the "
                                    "only way to "
                                    "express the idea "
                                    "that it embodied",
                                    "standard_of_proof": None,
                                },
                            },
                            {
                                "generic": False,
                                "absent": {
                                    "generic": False,
                                    "predicate": {
                                        "content": "${the_java_api} "
                                        "was "
                                        "a "
                                        "scene "
                                        "a "
                                        "faire",
                                        "truth": True,
                                    },
                                    "terms": [
                                        {
                                            "generic": True,
                                            "name": "the Java API",
                                            "plural": False,
                                        }
                                    ],
                                    "name": "the Java API was a scene a faire",
                                    "standard_of_proof": None,
                                },
                            },
                        ],
                        "despite": [],
                        "name": "",
                    },
                    "enactments": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "In "
                                        "no "
                                        "case "
                                        "does "
                                        "copyright "
                                        "protection "
                                        "for "
                                        "an "
                                        "original "
                                        "work "
                                        "of "
                                        "authorship "
                                        "extend "
                                        "to "
                                        "any "
                                        "idea, "
                                        "procedure, "
                                        "process, "
                                        "system, "
                                        "method "
                                        "of "
                                        "operation, "
                                        "concept, "
                                        "principle, "
                                        "or "
                                        "discovery, "
                                        "regardless "
                                        "of "
                                        "the "
                                        "form "
                                        "in "
                                        "which "
                                        "it "
                                        "is "
                                        "described, "
                                        "explained, "
                                        "illustrated, "
                                        "or "
                                        "embodied "
                                        "in "
                                        "such "
                                        "work.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030580/",
                                        "id": 1030580,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [{"start": 0, "end": None}],
                                    "quotes": [],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/a",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Copyright "
                                        "protection "
                                        "subsists, "
                                        "in "
                                        "accordance "
                                        "with "
                                        "this "
                                        "title, "
                                        "in "
                                        "original "
                                        "works "
                                        "of "
                                        "authorship "
                                        "fixed "
                                        "in "
                                        "any "
                                        "tangible "
                                        "medium "
                                        "of "
                                        "expression, "
                                        "now "
                                        "known "
                                        "or "
                                        "later "
                                        "developed, "
                                        "from "
                                        "which "
                                        "they "
                                        "can "
                                        "be "
                                        "perceived, "
                                        "reproduced, "
                                        "or "
                                        "otherwise "
                                        "communicated, "
                                        "either "
                                        "directly "
                                        "or "
                                        "with "
                                        "the "
                                        "aid "
                                        "of "
                                        "a "
                                        "machine "
                                        "or "
                                        "device. "
                                        "Works "
                                        "of "
                                        "authorship "
                                        "include "
                                        "the "
                                        "following "
                                        "categories:",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030579/",
                                        "id": 1030579,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/a",
                                    "children": [
                                        {
                                            "node": "/us/usc/t17/s102/a/1",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "literary works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030571/",
                                                "id": 1030571,
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
                                            "node": "/us/usc/t17/s102/a/2",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "musical "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "words;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030572/",
                                                "id": 1030572,
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
                                            "node": "/us/usc/t17/s102/a/3",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "dramatic "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "music;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030573/",
                                                "id": 1030573,
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
                                            "node": "/us/usc/t17/s102/a/4",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pantomimes "
                                                "and "
                                                "choreographic "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030574/",
                                                "id": 1030574,
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
                                            "node": "/us/usc/t17/s102/a/5",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pictorial, "
                                                "graphic, "
                                                "and "
                                                "sculptural "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030575/",
                                                "id": 1030575,
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
                                            "node": "/us/usc/t17/s102/a/6",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "motion "
                                                "pictures "
                                                "and "
                                                "other "
                                                "audiovisual "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030576/",
                                                "id": 1030576,
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
                                            "node": "/us/usc/t17/s102/a/7",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "sound recordings; and",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030577/",
                                                "id": 1030577,
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
                                            "node": "/us/usc/t17/s102/a/8",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "architectural works.",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030578/",
                                                "id": 1030578,
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
                                            "exact": "Copyright "
                                            "protection "
                                            "subsists, "
                                            "in "
                                            "accordance "
                                            "with "
                                            "this "
                                            "title, "
                                            "in "
                                            "original "
                                            "works "
                                            "of "
                                            "authorship "
                                            "fixed "
                                            "in "
                                            "any "
                                            "tangible "
                                            "medium "
                                            "of "
                                            "expression, "
                                            "now "
                                            "known "
                                            "or "
                                            "later "
                                            "developed, "
                                            "from "
                                            "which "
                                            "they "
                                            "can "
                                            "be "
                                            "perceived, "
                                            "reproduced, "
                                            "or "
                                            "otherwise "
                                            "communicated, "
                                            "either "
                                            "directly "
                                            "or "
                                            "with "
                                            "the "
                                            "aid "
                                            "of "
                                            "a "
                                            "machine "
                                            "or "
                                            "device.",
                                            "prefix": "",
                                            "suffix": "",
                                        }
                                    ],
                                },
                            }
                        ]
                    },
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
                                    "content": "${the_java_api} "
                                    "was "
                                    "essentially "
                                    "the only "
                                    "way to "
                                    "express "
                                    "the idea "
                                    "that it "
                                    "embodied",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "false the Java API was "
                                "essentially the only way "
                                "to express the idea that "
                                "it embodied",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${sun_microsystems} "
                                    "created "
                                    "${the_java_api}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Sun Microsystems",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                ],
                                "name": "Sun Microsystems created the Java API",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "when "
                                    "creating "
                                    "${the_java_api}, "
                                    "${sun_microsystems} "
                                    "could have "
                                    "selected "
                                    "and "
                                    "arranged "
                                    "its names "
                                    "and "
                                    "phrases in "
                                    "unlimited "
                                    "different "
                                    "ways",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Sun Microsystems",
                                        "plural": False,
                                    },
                                ],
                                "name": "when creating the Java API, "
                                "Sun Microsystems could have "
                                "selected and arranged its "
                                "names and phrases in "
                                "unlimited different ways",
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
                                    "node": "/us/usc/t17/s102/a",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Copyright "
                                        "protection "
                                        "subsists, "
                                        "in "
                                        "accordance "
                                        "with "
                                        "this "
                                        "title, "
                                        "in "
                                        "original "
                                        "works "
                                        "of "
                                        "authorship "
                                        "fixed "
                                        "in "
                                        "any "
                                        "tangible "
                                        "medium "
                                        "of "
                                        "expression, "
                                        "now "
                                        "known "
                                        "or "
                                        "later "
                                        "developed, "
                                        "from "
                                        "which "
                                        "they "
                                        "can "
                                        "be "
                                        "perceived, "
                                        "reproduced, "
                                        "or "
                                        "otherwise "
                                        "communicated, "
                                        "either "
                                        "directly "
                                        "or "
                                        "with "
                                        "the "
                                        "aid "
                                        "of "
                                        "a "
                                        "machine "
                                        "or "
                                        "device. "
                                        "Works "
                                        "of "
                                        "authorship "
                                        "include "
                                        "the "
                                        "following "
                                        "categories:",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030579/",
                                        "id": 1030579,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/a",
                                    "children": [
                                        {
                                            "node": "/us/usc/t17/s102/a/1",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "literary works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030571/",
                                                "id": 1030571,
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
                                            "node": "/us/usc/t17/s102/a/2",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "musical "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "words;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030572/",
                                                "id": 1030572,
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
                                            "node": "/us/usc/t17/s102/a/3",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "dramatic "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "music;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030573/",
                                                "id": 1030573,
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
                                            "node": "/us/usc/t17/s102/a/4",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pantomimes "
                                                "and "
                                                "choreographic "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030574/",
                                                "id": 1030574,
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
                                            "node": "/us/usc/t17/s102/a/5",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pictorial, "
                                                "graphic, "
                                                "and "
                                                "sculptural "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030575/",
                                                "id": 1030575,
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
                                            "node": "/us/usc/t17/s102/a/6",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "motion "
                                                "pictures "
                                                "and "
                                                "other "
                                                "audiovisual "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030576/",
                                                "id": 1030576,
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
                                            "node": "/us/usc/t17/s102/a/7",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "sound recordings; and",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030577/",
                                                "id": 1030577,
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
                                            "node": "/us/usc/t17/s102/a/8",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "architectural works.",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030578/",
                                                "id": 1030578,
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
                                            "exact": "Copyright "
                                            "protection "
                                            "subsists, "
                                            "in "
                                            "accordance "
                                            "with "
                                            "this "
                                            "title, "
                                            "in "
                                            "original "
                                            "works "
                                            "of "
                                            "authorship "
                                            "fixed "
                                            "in "
                                            "any "
                                            "tangible "
                                            "medium "
                                            "of "
                                            "expression, "
                                            "now "
                                            "known "
                                            "or "
                                            "later "
                                            "developed, "
                                            "from "
                                            "which "
                                            "they "
                                            "can "
                                            "be "
                                            "perceived, "
                                            "reproduced, "
                                            "or "
                                            "otherwise "
                                            "communicated, "
                                            "either "
                                            "directly "
                                            "or "
                                            "with "
                                            "the "
                                            "aid "
                                            "of "
                                            "a "
                                            "machine "
                                            "or "
                                            "device.",
                                            "prefix": "",
                                            "suffix": "",
                                        }
                                    ],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "In "
                                        "no "
                                        "case "
                                        "does "
                                        "copyright "
                                        "protection "
                                        "for "
                                        "an "
                                        "original "
                                        "work "
                                        "of "
                                        "authorship "
                                        "extend "
                                        "to "
                                        "any "
                                        "idea, "
                                        "procedure, "
                                        "process, "
                                        "system, "
                                        "method "
                                        "of "
                                        "operation, "
                                        "concept, "
                                        "principle, "
                                        "or "
                                        "discovery, "
                                        "regardless "
                                        "of "
                                        "the "
                                        "form "
                                        "in "
                                        "which "
                                        "it "
                                        "is "
                                        "described, "
                                        "explained, "
                                        "illustrated, "
                                        "or "
                                        "embodied "
                                        "in "
                                        "such "
                                        "work.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030580/",
                                        "id": 1030580,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [{"start": 0, "end": None}],
                                    "quotes": [],
                                },
                            }
                        ]
                    },
                    "mandatory": True,
                    "universal": False,
                    "name": None,
                },
                "rule_valid": True,
                "decided": True,
                "exclusive": False,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "Oracle had “unlimited options as to the selection "
                        "and arrangement of the 7000 lines Google copied.",
                        "prefix": "",
                        "suffix": "",
                    }
                ],
            },
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
                                    "content": "${the_java_api} was copyrightable",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was copyrightable",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} was a literary work",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was a literary work",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api_contained_short_phrases} "
                                    "that were "
                                    "creative",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": False,
                                        "predicate": {
                                            "content": "${the_java_api} "
                                            "contained "
                                            "short "
                                            "phrases",
                                            "truth": True,
                                        },
                                        "terms": [
                                            {
                                                "generic": True,
                                                "name": "the Java API",
                                                "plural": False,
                                            }
                                        ],
                                        "name": "the Java API contained short phrases",
                                        "standard_of_proof": None,
                                    }
                                ],
                                "name": "the Java API contained "
                                "short phrases that were "
                                "creative",
                                "standard_of_proof": None,
                            },
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "contained "
                                    "short "
                                    "phrases",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API contained short phrases",
                                "standard_of_proof": None,
                            }
                        ],
                        "name": "",
                    },
                    "enactments": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/a",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Copyright "
                                        "protection "
                                        "subsists, "
                                        "in "
                                        "accordance "
                                        "with "
                                        "this "
                                        "title, "
                                        "in "
                                        "original "
                                        "works "
                                        "of "
                                        "authorship "
                                        "fixed "
                                        "in "
                                        "any "
                                        "tangible "
                                        "medium "
                                        "of "
                                        "expression, "
                                        "now "
                                        "known "
                                        "or "
                                        "later "
                                        "developed, "
                                        "from "
                                        "which "
                                        "they "
                                        "can "
                                        "be "
                                        "perceived, "
                                        "reproduced, "
                                        "or "
                                        "otherwise "
                                        "communicated, "
                                        "either "
                                        "directly "
                                        "or "
                                        "with "
                                        "the "
                                        "aid "
                                        "of "
                                        "a "
                                        "machine "
                                        "or "
                                        "device. "
                                        "Works "
                                        "of "
                                        "authorship "
                                        "include "
                                        "the "
                                        "following "
                                        "categories:",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030579/",
                                        "id": 1030579,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/a",
                                    "children": [
                                        {
                                            "node": "/us/usc/t17/s102/a/1",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "literary works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030571/",
                                                "id": 1030571,
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
                                            "node": "/us/usc/t17/s102/a/2",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "musical "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "words;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030572/",
                                                "id": 1030572,
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
                                            "node": "/us/usc/t17/s102/a/3",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "dramatic "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "music;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030573/",
                                                "id": 1030573,
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
                                            "node": "/us/usc/t17/s102/a/4",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pantomimes "
                                                "and "
                                                "choreographic "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030574/",
                                                "id": 1030574,
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
                                            "node": "/us/usc/t17/s102/a/5",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pictorial, "
                                                "graphic, "
                                                "and "
                                                "sculptural "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030575/",
                                                "id": 1030575,
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
                                            "node": "/us/usc/t17/s102/a/6",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "motion "
                                                "pictures "
                                                "and "
                                                "other "
                                                "audiovisual "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030576/",
                                                "id": 1030576,
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
                                            "node": "/us/usc/t17/s102/a/7",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "sound recordings; and",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030577/",
                                                "id": 1030577,
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
                                            "node": "/us/usc/t17/s102/a/8",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "architectural works.",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030578/",
                                                "id": 1030578,
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
                                            "exact": "Copyright "
                                            "protection "
                                            "subsists, "
                                            "in "
                                            "accordance "
                                            "with "
                                            "this "
                                            "title, "
                                            "in "
                                            "original "
                                            "works "
                                            "of "
                                            "authorship "
                                            "fixed "
                                            "in "
                                            "any "
                                            "tangible "
                                            "medium "
                                            "of "
                                            "expression, "
                                            "now "
                                            "known "
                                            "or "
                                            "later "
                                            "developed, "
                                            "from "
                                            "which "
                                            "they "
                                            "can "
                                            "be "
                                            "perceived, "
                                            "reproduced, "
                                            "or "
                                            "otherwise "
                                            "communicated, "
                                            "either "
                                            "directly "
                                            "or "
                                            "with "
                                            "the "
                                            "aid "
                                            "of "
                                            "a "
                                            "machine "
                                            "or "
                                            "device.",
                                            "prefix": "",
                                            "suffix": "",
                                        }
                                    ],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "In "
                                        "no "
                                        "case "
                                        "does "
                                        "copyright "
                                        "protection "
                                        "for "
                                        "an "
                                        "original "
                                        "work "
                                        "of "
                                        "authorship "
                                        "extend "
                                        "to "
                                        "any "
                                        "idea, "
                                        "procedure, "
                                        "process, "
                                        "system, "
                                        "method "
                                        "of "
                                        "operation, "
                                        "concept, "
                                        "principle, "
                                        "or "
                                        "discovery, "
                                        "regardless "
                                        "of "
                                        "the "
                                        "form "
                                        "in "
                                        "which "
                                        "it "
                                        "is "
                                        "described, "
                                        "explained, "
                                        "illustrated, "
                                        "or "
                                        "embodied "
                                        "in "
                                        "such "
                                        "work.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030580/",
                                        "id": 1030580,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [{"start": 0, "end": None}],
                                    "quotes": [],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us/cfr/t37/s202.1",
                                    "start_date": datetime.date(1992, 2, 21),
                                    "heading": "Material not subject to copyright.",
                                    "text_version": {
                                        "content": "The "
                                        "following "
                                        "are "
                                        "examples "
                                        "of "
                                        "works "
                                        "not "
                                        "subject "
                                        "to "
                                        "copyright "
                                        "and "
                                        "applications "
                                        "for "
                                        "registration "
                                        "of "
                                        "such "
                                        "works "
                                        "cannot "
                                        "be "
                                        "entertained:",
                                        "url": None,
                                        "id": None,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/cfr/t37/s202.1@1992-02-21",
                                    "children": [
                                        {
                                            "node": "/us/cfr/t37/s202.1/a",
                                            "start_date": datetime.date(1992, 2, 21),
                                            "heading": "",
                                            "text_version": {
                                                "content": "Words "
                                                "and "
                                                "short "
                                                "phrases "
                                                "such "
                                                "as "
                                                "names, "
                                                "titles, "
                                                "and "
                                                "slogans; "
                                                "familiar "
                                                "symbols "
                                                "or "
                                                "designs; "
                                                "mere "
                                                "variations "
                                                "of "
                                                "typographic "
                                                "ornamentation, "
                                                "lettering "
                                                "or "
                                                "coloring; "
                                                "mere "
                                                "listing "
                                                "of "
                                                "ingredients "
                                                "or "
                                                "contents;",
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
                                            "node": "/us/cfr/t37/s202.1/b",
                                            "start_date": datetime.date(1992, 2, 21),
                                            "heading": "",
                                            "text_version": {
                                                "content": "Ideas, "
                                                "plans, "
                                                "methods, "
                                                "systems, "
                                                "or "
                                                "devices, "
                                                "as "
                                                "distinguished "
                                                "from "
                                                "the "
                                                "particular "
                                                "manner "
                                                "in "
                                                "which "
                                                "they "
                                                "are "
                                                "expressed "
                                                "or "
                                                "described "
                                                "in "
                                                "a "
                                                "writing;  ",
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
                                            "node": "/us/cfr/t37/s202.1/c",
                                            "start_date": datetime.date(1992, 2, 21),
                                            "heading": "",
                                            "text_version": {
                                                "content": "Blank "
                                                "forms, "
                                                "such "
                                                "as "
                                                "time "
                                                "cards, "
                                                "graph "
                                                "paper, "
                                                "account "
                                                "books, "
                                                "diaries, "
                                                "bank "
                                                "checks, "
                                                "scorecards, "
                                                "address "
                                                "books, "
                                                "report "
                                                "forms, "
                                                "order "
                                                "forms "
                                                "and "
                                                "the "
                                                "like, "
                                                "which "
                                                "are "
                                                "designed "
                                                "for "
                                                "recording "
                                                "information "
                                                "and "
                                                "do "
                                                "not "
                                                "in "
                                                "themselves "
                                                "convey "
                                                "information;",
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
                                            "node": "/us/cfr/t37/s202.1/d",
                                            "start_date": datetime.date(1992, 2, 21),
                                            "heading": "",
                                            "text_version": {
                                                "content": "Works "
                                                "consisting "
                                                "entirely "
                                                "of "
                                                "information "
                                                "that "
                                                "is "
                                                "common "
                                                "property "
                                                "containing "
                                                "no "
                                                "original "
                                                "authorship, "
                                                "such "
                                                "as, "
                                                "for "
                                                "example: "
                                                "Standard "
                                                "calendars, "
                                                "height "
                                                "and "
                                                "weight "
                                                "charts, "
                                                "tape "
                                                "measures "
                                                "and "
                                                "rulers, "
                                                "schedules "
                                                "of "
                                                "sporting "
                                                "events, "
                                                "and "
                                                "lists "
                                                "or "
                                                "tables "
                                                "taken "
                                                "from "
                                                "public "
                                                "documents "
                                                "or "
                                                "other "
                                                "common "
                                                "sources.",
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
                                            "node": "/us/cfr/t37/s202.1/e",
                                            "start_date": datetime.date(1992, 2, 21),
                                            "heading": "",
                                            "text_version": {
                                                "content": "Typeface as typeface.",
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
                                            "suffix": "familiar symbols or designs",
                                        }
                                    ],
                                },
                            },
                        ]
                    },
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
                                    "content": "${the_java_api} was a scene a faire",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was a scene a faire",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_language} "
                                    "was a "
                                    "computer "
                                    "program",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java language was a computer program",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was an "
                                    "element of "
                                    "${the_java_language}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    },
                                ],
                                "name": "the Java API was an element "
                                "of the Java language",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "the "
                                    "creation "
                                    "of "
                                    "${the_java_api} "
                                    "was "
                                    "dictated "
                                    "by "
                                    "external "
                                    "factors "
                                    "such as "
                                    "the "
                                    "mechanical "
                                    "specifications "
                                    "of the "
                                    "computer "
                                    "on which "
                                    "${the_java_language} "
                                    "was "
                                    "intended "
                                    "to run or "
                                    "widely "
                                    "accepted "
                                    "programming "
                                    "practices "
                                    "within the "
                                    "computer "
                                    "industry",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    },
                                ],
                                "name": "the creation of the Java "
                                "API was dictated by "
                                "external factors such as "
                                "the mechanical "
                                "specifications of the "
                                "computer on which the Java "
                                "language was intended to "
                                "run or widely accepted "
                                "programming practices "
                                "within the computer "
                                "industry",
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
                                    "node": "/us/usc/t17/s102/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "In "
                                        "no "
                                        "case "
                                        "does "
                                        "copyright "
                                        "protection "
                                        "for "
                                        "an "
                                        "original "
                                        "work "
                                        "of "
                                        "authorship "
                                        "extend "
                                        "to "
                                        "any "
                                        "idea, "
                                        "procedure, "
                                        "process, "
                                        "system, "
                                        "method "
                                        "of "
                                        "operation, "
                                        "concept, "
                                        "principle, "
                                        "or "
                                        "discovery, "
                                        "regardless "
                                        "of "
                                        "the "
                                        "form "
                                        "in "
                                        "which "
                                        "it "
                                        "is "
                                        "described, "
                                        "explained, "
                                        "illustrated, "
                                        "or "
                                        "embodied "
                                        "in "
                                        "such "
                                        "work.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030580/",
                                        "id": 1030580,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [{"start": 0, "end": None}],
                                    "quotes": [],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/a",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Copyright "
                                        "protection "
                                        "subsists, "
                                        "in "
                                        "accordance "
                                        "with "
                                        "this "
                                        "title, "
                                        "in "
                                        "original "
                                        "works "
                                        "of "
                                        "authorship "
                                        "fixed "
                                        "in "
                                        "any "
                                        "tangible "
                                        "medium "
                                        "of "
                                        "expression, "
                                        "now "
                                        "known "
                                        "or "
                                        "later "
                                        "developed, "
                                        "from "
                                        "which "
                                        "they "
                                        "can "
                                        "be "
                                        "perceived, "
                                        "reproduced, "
                                        "or "
                                        "otherwise "
                                        "communicated, "
                                        "either "
                                        "directly "
                                        "or "
                                        "with "
                                        "the "
                                        "aid "
                                        "of "
                                        "a "
                                        "machine "
                                        "or "
                                        "device. "
                                        "Works "
                                        "of "
                                        "authorship "
                                        "include "
                                        "the "
                                        "following "
                                        "categories:",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030579/",
                                        "id": 1030579,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/a",
                                    "children": [
                                        {
                                            "node": "/us/usc/t17/s102/a/1",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "literary works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030571/",
                                                "id": 1030571,
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
                                            "node": "/us/usc/t17/s102/a/2",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "musical "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "words;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030572/",
                                                "id": 1030572,
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
                                            "node": "/us/usc/t17/s102/a/3",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "dramatic "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "music;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030573/",
                                                "id": 1030573,
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
                                            "node": "/us/usc/t17/s102/a/4",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pantomimes "
                                                "and "
                                                "choreographic "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030574/",
                                                "id": 1030574,
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
                                            "node": "/us/usc/t17/s102/a/5",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pictorial, "
                                                "graphic, "
                                                "and "
                                                "sculptural "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030575/",
                                                "id": 1030575,
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
                                            "node": "/us/usc/t17/s102/a/6",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "motion "
                                                "pictures "
                                                "and "
                                                "other "
                                                "audiovisual "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030576/",
                                                "id": 1030576,
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
                                            "node": "/us/usc/t17/s102/a/7",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "sound recordings; and",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030577/",
                                                "id": 1030577,
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
                                            "node": "/us/usc/t17/s102/a/8",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "architectural works.",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030578/",
                                                "id": 1030578,
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
                                            "exact": "Copyright "
                                            "protection "
                                            "subsists, "
                                            "in "
                                            "accordance "
                                            "with "
                                            "this "
                                            "title, "
                                            "in "
                                            "original "
                                            "works "
                                            "of "
                                            "authorship "
                                            "fixed "
                                            "in "
                                            "any "
                                            "tangible "
                                            "medium "
                                            "of "
                                            "expression, "
                                            "now "
                                            "known "
                                            "or "
                                            "later "
                                            "developed, "
                                            "from "
                                            "which "
                                            "they "
                                            "can "
                                            "be "
                                            "perceived, "
                                            "reproduced, "
                                            "or "
                                            "otherwise "
                                            "communicated, "
                                            "either "
                                            "directly "
                                            "or "
                                            "with "
                                            "the "
                                            "aid "
                                            "of "
                                            "a "
                                            "machine "
                                            "or "
                                            "device.",
                                            "prefix": "",
                                            "suffix": "",
                                        }
                                    ],
                                },
                            }
                        ]
                    },
                    "mandatory": False,
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
                                    "content": "${the_java_api} was copyrightable",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was copyrightable",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_language} "
                                    "was a "
                                    "computer "
                                    "program",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java language was a computer program",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was the "
                                    "sequence, "
                                    "structure, "
                                    "and "
                                    "organization "
                                    "of "
                                    "${the_java_language}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    },
                                ],
                                "name": "the Java API was the "
                                "sequence, structure, and "
                                "organization of the Java "
                                "language",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} "
                                    "was the "
                                    "expression "
                                    "of an idea",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was the expression of an idea",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} was an idea",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "false the Java API was an idea",
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
                                    "node": "/us/usc/t17/s102/a",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Copyright "
                                        "protection "
                                        "subsists, "
                                        "in "
                                        "accordance "
                                        "with "
                                        "this "
                                        "title, "
                                        "in "
                                        "original "
                                        "works "
                                        "of "
                                        "authorship "
                                        "fixed "
                                        "in "
                                        "any "
                                        "tangible "
                                        "medium "
                                        "of "
                                        "expression, "
                                        "now "
                                        "known "
                                        "or "
                                        "later "
                                        "developed, "
                                        "from "
                                        "which "
                                        "they "
                                        "can "
                                        "be "
                                        "perceived, "
                                        "reproduced, "
                                        "or "
                                        "otherwise "
                                        "communicated, "
                                        "either "
                                        "directly "
                                        "or "
                                        "with "
                                        "the "
                                        "aid "
                                        "of "
                                        "a "
                                        "machine "
                                        "or "
                                        "device. "
                                        "Works "
                                        "of "
                                        "authorship "
                                        "include "
                                        "the "
                                        "following "
                                        "categories:",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030579/",
                                        "id": 1030579,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/a",
                                    "children": [
                                        {
                                            "node": "/us/usc/t17/s102/a/1",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "literary works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030571/",
                                                "id": 1030571,
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
                                            "node": "/us/usc/t17/s102/a/2",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "musical "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "words;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030572/",
                                                "id": 1030572,
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
                                            "node": "/us/usc/t17/s102/a/3",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "dramatic "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "music;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030573/",
                                                "id": 1030573,
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
                                            "node": "/us/usc/t17/s102/a/4",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pantomimes "
                                                "and "
                                                "choreographic "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030574/",
                                                "id": 1030574,
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
                                            "node": "/us/usc/t17/s102/a/5",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pictorial, "
                                                "graphic, "
                                                "and "
                                                "sculptural "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030575/",
                                                "id": 1030575,
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
                                            "node": "/us/usc/t17/s102/a/6",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "motion "
                                                "pictures "
                                                "and "
                                                "other "
                                                "audiovisual "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030576/",
                                                "id": 1030576,
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
                                            "node": "/us/usc/t17/s102/a/7",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "sound recordings; and",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030577/",
                                                "id": 1030577,
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
                                            "node": "/us/usc/t17/s102/a/8",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "architectural works.",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030578/",
                                                "id": 1030578,
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
                                            "exact": "Copyright "
                                            "protection "
                                            "subsists, "
                                            "in "
                                            "accordance "
                                            "with "
                                            "this "
                                            "title, "
                                            "in "
                                            "original "
                                            "works "
                                            "of "
                                            "authorship "
                                            "fixed "
                                            "in "
                                            "any "
                                            "tangible "
                                            "medium "
                                            "of "
                                            "expression, "
                                            "now "
                                            "known "
                                            "or "
                                            "later "
                                            "developed, "
                                            "from "
                                            "which "
                                            "they "
                                            "can "
                                            "be "
                                            "perceived, "
                                            "reproduced, "
                                            "or "
                                            "otherwise "
                                            "communicated, "
                                            "either "
                                            "directly "
                                            "or "
                                            "with "
                                            "the "
                                            "aid "
                                            "of "
                                            "a "
                                            "machine "
                                            "or "
                                            "device.",
                                            "prefix": "",
                                            "suffix": "",
                                        }
                                    ],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "In "
                                        "no "
                                        "case "
                                        "does "
                                        "copyright "
                                        "protection "
                                        "for "
                                        "an "
                                        "original "
                                        "work "
                                        "of "
                                        "authorship "
                                        "extend "
                                        "to "
                                        "any "
                                        "idea, "
                                        "procedure, "
                                        "process, "
                                        "system, "
                                        "method "
                                        "of "
                                        "operation, "
                                        "concept, "
                                        "principle, "
                                        "or "
                                        "discovery, "
                                        "regardless "
                                        "of "
                                        "the "
                                        "form "
                                        "in "
                                        "which "
                                        "it "
                                        "is "
                                        "described, "
                                        "explained, "
                                        "illustrated, "
                                        "or "
                                        "embodied "
                                        "in "
                                        "such "
                                        "work.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030580/",
                                        "id": 1030580,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [{"start": 0, "end": None}],
                                    "quotes": [],
                                },
                            }
                        ]
                    },
                    "mandatory": False,
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
                                    "content": "${the_java_api} was copyrightable",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was copyrightable",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} was an original work",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API was an original work",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${sun_microsystems} "
                                    "was the "
                                    "author of "
                                    "${the_java_api}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Sun Microsystems",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                ],
                                "name": "Sun Microsystems was the "
                                "author of the Java API",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "when "
                                    "creating "
                                    "${the_java_api}, "
                                    "${sun_microsystems} "
                                    "had "
                                    "multiple "
                                    "ways to "
                                    "express "
                                    "its "
                                    "underlying "
                                    "idea",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Sun Microsystems",
                                        "plural": False,
                                    },
                                ],
                                "name": "when creating the Java API, "
                                "Sun Microsystems had "
                                "multiple ways to express "
                                "its underlying idea",
                                "standard_of_proof": None,
                            },
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_api} served a function",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java API",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java API served a function",
                                "standard_of_proof": None,
                            }
                        ],
                        "name": "",
                    },
                    "enactments": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/a",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Copyright "
                                        "protection "
                                        "subsists, "
                                        "in "
                                        "accordance "
                                        "with "
                                        "this "
                                        "title, "
                                        "in "
                                        "original "
                                        "works "
                                        "of "
                                        "authorship "
                                        "fixed "
                                        "in "
                                        "any "
                                        "tangible "
                                        "medium "
                                        "of "
                                        "expression, "
                                        "now "
                                        "known "
                                        "or "
                                        "later "
                                        "developed, "
                                        "from "
                                        "which "
                                        "they "
                                        "can "
                                        "be "
                                        "perceived, "
                                        "reproduced, "
                                        "or "
                                        "otherwise "
                                        "communicated, "
                                        "either "
                                        "directly "
                                        "or "
                                        "with "
                                        "the "
                                        "aid "
                                        "of "
                                        "a "
                                        "machine "
                                        "or "
                                        "device. "
                                        "Works "
                                        "of "
                                        "authorship "
                                        "include "
                                        "the "
                                        "following "
                                        "categories:",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030579/",
                                        "id": 1030579,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/a",
                                    "children": [
                                        {
                                            "node": "/us/usc/t17/s102/a/1",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "literary works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030571/",
                                                "id": 1030571,
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
                                            "node": "/us/usc/t17/s102/a/2",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "musical "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "words;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030572/",
                                                "id": 1030572,
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
                                            "node": "/us/usc/t17/s102/a/3",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "dramatic "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "music;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030573/",
                                                "id": 1030573,
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
                                            "node": "/us/usc/t17/s102/a/4",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pantomimes "
                                                "and "
                                                "choreographic "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030574/",
                                                "id": 1030574,
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
                                            "node": "/us/usc/t17/s102/a/5",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pictorial, "
                                                "graphic, "
                                                "and "
                                                "sculptural "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030575/",
                                                "id": 1030575,
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
                                            "node": "/us/usc/t17/s102/a/6",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "motion "
                                                "pictures "
                                                "and "
                                                "other "
                                                "audiovisual "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030576/",
                                                "id": 1030576,
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
                                            "node": "/us/usc/t17/s102/a/7",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "sound recordings; and",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030577/",
                                                "id": 1030577,
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
                                            "node": "/us/usc/t17/s102/a/8",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "architectural works.",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030578/",
                                                "id": 1030578,
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
                                            "exact": "Copyright "
                                            "protection "
                                            "subsists, "
                                            "in "
                                            "accordance "
                                            "with "
                                            "this "
                                            "title, "
                                            "in "
                                            "original "
                                            "works "
                                            "of "
                                            "authorship "
                                            "fixed "
                                            "in "
                                            "any "
                                            "tangible "
                                            "medium "
                                            "of "
                                            "expression, "
                                            "now "
                                            "known "
                                            "or "
                                            "later "
                                            "developed, "
                                            "from "
                                            "which "
                                            "they "
                                            "can "
                                            "be "
                                            "perceived, "
                                            "reproduced, "
                                            "or "
                                            "otherwise "
                                            "communicated, "
                                            "either "
                                            "directly "
                                            "or "
                                            "with "
                                            "the "
                                            "aid "
                                            "of "
                                            "a "
                                            "machine "
                                            "or "
                                            "device.",
                                            "prefix": "",
                                            "suffix": "",
                                        }
                                    ],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "In "
                                        "no "
                                        "case "
                                        "does "
                                        "copyright "
                                        "protection "
                                        "for "
                                        "an "
                                        "original "
                                        "work "
                                        "of "
                                        "authorship "
                                        "extend "
                                        "to "
                                        "any "
                                        "idea, "
                                        "procedure, "
                                        "process, "
                                        "system, "
                                        "method "
                                        "of "
                                        "operation, "
                                        "concept, "
                                        "principle, "
                                        "or "
                                        "discovery, "
                                        "regardless "
                                        "of "
                                        "the "
                                        "form "
                                        "in "
                                        "which "
                                        "it "
                                        "is "
                                        "described, "
                                        "explained, "
                                        "illustrated, "
                                        "or "
                                        "embodied "
                                        "in "
                                        "such "
                                        "work.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030580/",
                                        "id": 1030580,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [{"start": 0, "end": None}],
                                    "quotes": [],
                                },
                            }
                        ]
                    },
                    "mandatory": True,
                    "universal": True,
                    "name": None,
                },
                "rule_valid": True,
                "decided": True,
                "exclusive": False,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "as long as the author had multiple ways to "
                        "express the underlying idea",
                        "prefix": "",
                        "suffix": "",
                    }
                ],
            },
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
                                    "content": "${the_java_language} was copyrightable",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java language was copyrightable",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_java_language} "
                                    "was a "
                                    "computer "
                                    "program",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Java language",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Java language was a computer program",
                                "standard_of_proof": None,
                            }
                        ],
                        "despite": [],
                        "name": "",
                    },
                    "enactments": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/a",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "Copyright "
                                        "protection "
                                        "subsists, "
                                        "in "
                                        "accordance "
                                        "with "
                                        "this "
                                        "title, "
                                        "in "
                                        "original "
                                        "works "
                                        "of "
                                        "authorship "
                                        "fixed "
                                        "in "
                                        "any "
                                        "tangible "
                                        "medium "
                                        "of "
                                        "expression, "
                                        "now "
                                        "known "
                                        "or "
                                        "later "
                                        "developed, "
                                        "from "
                                        "which "
                                        "they "
                                        "can "
                                        "be "
                                        "perceived, "
                                        "reproduced, "
                                        "or "
                                        "otherwise "
                                        "communicated, "
                                        "either "
                                        "directly "
                                        "or "
                                        "with "
                                        "the "
                                        "aid "
                                        "of "
                                        "a "
                                        "machine "
                                        "or "
                                        "device. "
                                        "Works "
                                        "of "
                                        "authorship "
                                        "include "
                                        "the "
                                        "following "
                                        "categories:",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030579/",
                                        "id": 1030579,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/a",
                                    "children": [
                                        {
                                            "node": "/us/usc/t17/s102/a/1",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "literary works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030571/",
                                                "id": 1030571,
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
                                            "node": "/us/usc/t17/s102/a/2",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "musical "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "words;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030572/",
                                                "id": 1030572,
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
                                            "node": "/us/usc/t17/s102/a/3",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "dramatic "
                                                "works, "
                                                "including "
                                                "any "
                                                "accompanying "
                                                "music;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030573/",
                                                "id": 1030573,
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
                                            "node": "/us/usc/t17/s102/a/4",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pantomimes "
                                                "and "
                                                "choreographic "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030574/",
                                                "id": 1030574,
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
                                            "node": "/us/usc/t17/s102/a/5",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "pictorial, "
                                                "graphic, "
                                                "and "
                                                "sculptural "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030575/",
                                                "id": 1030575,
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
                                            "node": "/us/usc/t17/s102/a/6",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "motion "
                                                "pictures "
                                                "and "
                                                "other "
                                                "audiovisual "
                                                "works;",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030576/",
                                                "id": 1030576,
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
                                            "node": "/us/usc/t17/s102/a/7",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "sound recordings; and",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030577/",
                                                "id": 1030577,
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
                                            "node": "/us/usc/t17/s102/a/8",
                                            "start_date": datetime.date(2013, 7, 18),
                                            "heading": "",
                                            "text_version": {
                                                "content": "architectural works.",
                                                "url": "https://authorityspoke.com/api/v1/textversions/1030578/",
                                                "id": 1030578,
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
                                            "exact": "Copyright "
                                            "protection "
                                            "subsists, "
                                            "in "
                                            "accordance "
                                            "with "
                                            "this "
                                            "title, "
                                            "in "
                                            "original "
                                            "works "
                                            "of "
                                            "authorship "
                                            "fixed "
                                            "in "
                                            "any "
                                            "tangible "
                                            "medium "
                                            "of "
                                            "expression, "
                                            "now "
                                            "known "
                                            "or "
                                            "later "
                                            "developed, "
                                            "from "
                                            "which "
                                            "they "
                                            "can "
                                            "be "
                                            "perceived, "
                                            "reproduced, "
                                            "or "
                                            "otherwise "
                                            "communicated, "
                                            "either "
                                            "directly "
                                            "or "
                                            "with "
                                            "the "
                                            "aid "
                                            "of "
                                            "a "
                                            "machine "
                                            "or "
                                            "device.",
                                            "prefix": "",
                                            "suffix": "",
                                        }
                                    ],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s102/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "In "
                                        "no "
                                        "case "
                                        "does "
                                        "copyright "
                                        "protection "
                                        "for "
                                        "an "
                                        "original "
                                        "work "
                                        "of "
                                        "authorship "
                                        "extend "
                                        "to "
                                        "any "
                                        "idea, "
                                        "procedure, "
                                        "process, "
                                        "system, "
                                        "method "
                                        "of "
                                        "operation, "
                                        "concept, "
                                        "principle, "
                                        "or "
                                        "discovery, "
                                        "regardless "
                                        "of "
                                        "the "
                                        "form "
                                        "in "
                                        "which "
                                        "it "
                                        "is "
                                        "described, "
                                        "explained, "
                                        "illustrated, "
                                        "or "
                                        "embodied "
                                        "in "
                                        "such "
                                        "work.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030580/",
                                        "id": 1030580,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s102/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [{"start": 0, "end": None}],
                                    "quotes": [],
                                },
                            }
                        ]
                    },
                    "mandatory": False,
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
    "named_anchors": [
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "the creation of ${the_java_api} was "
                    "dictated by external factors such as the "
                    "mechanical specifications of the computer "
                    "on which ${the_java_language} was intended "
                    "to run or widely accepted programming "
                    "practices within the computer industry",
                    "truth": True,
                },
                "terms": [
                    {"generic": True, "name": "the Java API", "plural": False},
                    {"generic": True, "name": "the Java language", "plural": False},
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "that are dictated by external factors such "
                        "as ‘the mechanical specifications of the "
                        "computer on which a particular program is "
                        "intended to run’ or ‘widely accepted "
                        "programming practices within the computer "
                        "industry.",
                        "prefix": "",
                        "suffix": "",
                    }
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${the_java_api} was independently created "
                    "by the author, as opposed to copied from "
                    "other works",
                    "truth": True,
                },
                "terms": [{"generic": True, "name": "the Java API", "plural": False}],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "the work was independently created by the "
                        "author (as opposed to copied from other "
                        "works)",
                        "prefix": "",
                        "suffix": "",
                    }
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${the_java_api} was essentially the only "
                    "way to express the idea that it embodied",
                    "truth": False,
                },
                "terms": [{"generic": True, "name": "the Java API", "plural": False}],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "we agree that merger cannot bar copyright "
                        "protection for any lines of declaring source "
                        "code unless Sun/Oracle had only one way, or "
                        "a limited number of ways, to write them",
                        "prefix": "",
                        "suffix": "",
                    },
                    {
                        "exact": "Oracle had “unlimited options as to the "
                        "selection and arrangement of the 7000 lines "
                        "Google copied.",
                        "prefix": "",
                        "suffix": "",
                    },
                    {
                        "exact": "merger does not apply on the record before us",
                        "prefix": "",
                        "suffix": "",
                    },
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "there was a preexisting community of "
                    "programmers accustomed to using "
                    "${the_java_api}",
                    "truth": True,
                },
                "terms": [{"generic": True, "name": "the Java API", "plural": False}],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "the preexisting community of programmers who "
                        "were accustomed to using the Java API "
                        "packages",
                        "prefix": "",
                        "suffix": "",
                    }
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${the_java_api} was the sequence, "
                    "structure, and organization of "
                    "${the_java_language}",
                    "truth": True,
                },
                "terms": [
                    {"generic": True, "name": "the Java API", "plural": False},
                    {"generic": True, "name": "the Java language", "plural": False},
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "the program’s sequence, structure, and organization,",
                        "prefix": "include, among other things,",
                        "suffix": "as well as",
                    },
                    {"exact": "c", "prefix": "", "suffix": ""},
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${the_java_api} was essentially the only "
                    "way to express the idea that it embodied",
                    "truth": True,
                },
                "terms": [{"generic": True, "name": "the Java API", "plural": False}],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "merger",
                        "prefix": "concepts of",
                        "suffix": "and scenes a faire",
                    },
                    {
                        "exact": "concepts of merger",
                        "prefix": "",
                        "suffix": " and scenes a faire are affirmative "
                        "defenses to claims of infringement.",
                    },
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${the_java_api} was a set of application "
                    "programming interface declarations",
                    "truth": True,
                },
                "terms": [{"generic": True, "name": "the Java API", "plural": False}],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "literal elements of its API packages — the "
                        "7,000 lines of declaring source code",
                        "prefix": "",
                        "suffix": "",
                    }
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "it was possible to use ${the_java_language} "
                    "without copying ${the_java_api}",
                    "truth": True,
                },
                "terms": [
                    {"generic": True, "name": "the Java language", "plural": False},
                    {"generic": True, "name": "the Java API", "plural": False},
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "Google did not need to copy the structure, "
                        "sequence, and organization of the Java API "
                        "packages to write programs in the Java "
                        "language",
                        "prefix": "",
                        "suffix": "",
                    }
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${the_java_api} possessed at least some "
                    "minimal degree of creativity",
                    "truth": True,
                },
                "terms": [{"generic": True, "name": "the Java API", "plural": False}],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "it possesses at least some minimal degree of "
                        "creativity.",
                        "prefix": "",
                        "suffix": "",
                    }
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${the_java_api} became so popular that it "
                    "was the industry standard",
                    "truth": True,
                },
                "terms": [{"generic": True, "name": "the Java API", "plural": False}],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "the Java API packages because they had "
                        "become the effective industry standard",
                        "prefix": "",
                        "suffix": "",
                    }
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${the_java_api} was a non-literal element "
                    "of ${the_java_language}",
                    "truth": True,
                },
                "terms": [
                    {"generic": True, "name": "the Java API", "plural": False},
                    {"generic": True, "name": "the Java language", "plural": False},
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "The non-literal components of a computer program",
                        "prefix": "",
                        "suffix": "include,",
                    }
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${the_java_api} was a literal element of "
                    "${the_java_language}",
                    "truth": True,
                },
                "terms": [
                    {"generic": True, "name": "the Java API", "plural": False},
                    {"generic": True, "name": "the Java language", "plural": False},
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": " elements",
                        "prefix": "the scene a faire doctrine denies "
                        "protection to program",
                        "suffix": "",
                    },
                    {
                        "exact": "The literal elements of a computer program are",
                        "prefix": "",
                        "suffix": "",
                    },
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${the_java_api_contained_short_phrases} "
                    "that were creative",
                    "truth": True,
                },
                "terms": [
                    {
                        "generic": False,
                        "predicate": {
                            "content": "${the_java_api} contained short phrases",
                            "truth": True,
                        },
                        "terms": [
                            {"generic": True, "name": "the Java API", "plural": False}
                        ],
                        "name": "the Java API contained short phrases",
                        "standard_of_proof": None,
                    }
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "whether those phrases are creative.",
                        "prefix": "",
                        "suffix": "",
                    }
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${the_java_api} was the source code of "
                    "${the_java_language}",
                    "truth": True,
                },
                "terms": [
                    {"generic": True, "name": "the Java API", "plural": False},
                    {"generic": True, "name": "the Java language", "plural": False},
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "are the source code",
                        "prefix": "",
                        "suffix": "and object code.",
                    }
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${the_java_api} was the object code of "
                    "${the_java_language}",
                    "truth": True,
                },
                "terms": [
                    {"generic": True, "name": "the Java API", "plural": False},
                    {"generic": True, "name": "the Java language", "plural": False},
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "object code.",
                        "prefix": "are the source code and ",
                        "suffix": "",
                    }
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${google} infringed the copyright on ${the_java_api}",
                    "truth": False,
                },
                "terms": [
                    {"generic": True, "name": "Google", "plural": False},
                    {"generic": True, "name": "the Java API", "plural": False},
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "affirmative defenses to claims of infringement.",
                        "prefix": "concepts of merger and scenes a faire are",
                        "suffix": "",
                    }
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${the_java_api} was the expression of an idea",
                    "truth": True,
                },
                "terms": [{"generic": True, "name": "the Java API", "plural": False}],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "whether, on the particular facts of each "
                        "case, the component in question qualifies as",
                        "prefix": "",
                        "suffix": "",
                    },
                    {
                        "exact": "expression of an idea,",
                        "prefix": "an ",
                        "suffix": " or an idea itself.",
                    },
                    {
                        "exact": "the expression of an idea",
                        "prefix": "Copyright protection extends only to ",
                        "suffix": "",
                    },
                    {
                        "exact": "the component in question qualifies as an "
                        "expression of an idea",
                        "prefix": "",
                        "suffix": "",
                    },
                    {
                        "exact": "where it qualifies as an expression of an idea",
                        "prefix": "",
                        "suffix": ", rather than the idea itself.",
                    },
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${the_java_language} was a computer program",
                    "truth": True,
                },
                "terms": [
                    {"generic": True, "name": "the Java language", "plural": False}
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "a computer program",
                        "prefix": "The literal elements of ",
                        "suffix": "are",
                    },
                    {
                        "exact": "program",
                        "prefix": "the scene a faire doctrine denies protection to ",
                        "suffix": " elements",
                    },
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${the_java_api} was a method of operation",
                    "truth": True,
                },
                "terms": [{"generic": True, "name": "the Java API", "plural": False}],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "although an element of a work may be "
                        "characterized as a method of operation",
                        "prefix": "",
                        "suffix": "",
                    }
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${sun_microsystems} created ${the_java_api}",
                    "truth": True,
                },
                "terms": [
                    {"generic": True, "name": "Sun Microsystems", "plural": False},
                    {"generic": True, "name": "the Java API", "plural": False},
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "Sun Microsystems, Inc. (“Sun”) developed the "
                        "Java “platform” for computer programming",
                        "prefix": "",
                        "suffix": "",
                    }
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${the_java_api} was copyrightable",
                    "truth": False,
                },
                "terms": [{"generic": True, "name": "the Java API", "plural": False}],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "copyrightability",
                        "prefix": "questions regarding originality are "
                        "considered questions of ",
                        "suffix": "",
                    }
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${the_java_api} contained short phrases",
                    "truth": True,
                },
                "terms": [{"generic": True, "name": "the Java API", "plural": False}],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "whether the work at issue contains short phrases",
                        "prefix": "",
                        "suffix": "",
                    },
                    {
                        "exact": "the work at issue contains short phrases",
                        "prefix": "purposes is not whether ",
                        "suffix": "",
                    },
                    {
                        "exact": "whether the work at issue contains short phrases",
                        "prefix": "",
                        "suffix": "",
                    },
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${the_java_api} was an original work",
                    "truth": True,
                },
                "terms": [{"generic": True, "name": "the Java API", "plural": False}],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {"exact": "a work must be “original”", "prefix": "", "suffix": ""},
                    {
                        "exact": "Original, as the term is used in copyright",
                        "prefix": "",
                        "suffix": "",
                    },
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${the_java_api} was a scene a faire",
                    "truth": True,
                },
                "terms": [{"generic": True, "name": "the Java API", "plural": False}],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "scenes a faire",
                        "prefix": "concepts of merger and ",
                        "suffix": "",
                    },
                    {
                        "exact": "scenes a faire",
                        "prefix": "concepts of merger and ",
                        "suffix": " are affirmative defenses to claims of "
                        "infringement.",
                    },
                    {
                        "exact": "the scene a faire doctrine denies protection",
                        "prefix": "",
                        "suffix": "",
                    },
                    {"exact": "c", "prefix": "", "suffix": ""},
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${the_java_api} was a literary work",
                    "truth": True,
                },
                "terms": [{"generic": True, "name": "the Java API", "plural": False}],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {"exact": "as literary works often do", "prefix": "", "suffix": ""}
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "absent": {
                    "generic": False,
                    "predicate": {
                        "content": "${the_java_api} was essentially "
                        "the only way to express the idea "
                        "that it embodied",
                        "truth": True,
                    },
                    "terms": [
                        {"generic": True, "name": "the Java API", "plural": False}
                    ],
                    "name": "the Java API was essentially the only way to "
                    "express the idea that it embodied",
                    "standard_of_proof": None,
                },
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "concepts of merger",
                        "prefix": "",
                        "suffix": " and scenes a faire are affirmative defenses ",
                    }
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {"content": "${the_java_api} was an idea", "truth": False},
                "terms": [{"generic": True, "name": "the Java API", "plural": False}],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "whether, on the particular facts of each "
                        "case, the component in question qualifies as "
                        "an expression of an idea",
                        "prefix": "",
                        "suffix": "",
                    },
                    {
                        "exact": "not to the underlying idea itself",
                        "prefix": "",
                        "suffix": "",
                    },
                    {
                        "exact": "the component in question qualifies as",
                        "prefix": "",
                        "suffix": " an expression of an idea,",
                    },
                    {"exact": "an idea itself.", "prefix": "or ", "suffix": ""},
                    {
                        "exact": "rather than the idea itself.",
                        "prefix": "where it qualifies as an expression of an idea, ",
                        "suffix": "",
                    },
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${the_java_api} was copyrightable",
                    "truth": True,
                },
                "terms": [{"generic": True, "name": "the Java API", "plural": False}],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "that element may nevertheless contain "
                        "expression that is eligible for copyright "
                        "protection",
                        "prefix": "",
                        "suffix": "",
                    },
                    {
                        "exact": "is eligible for copyright protection",
                        "prefix": "structure, sequence, and organization of a "
                        "computer program ",
                        "suffix": "",
                    },
                    {
                        "exact": "copyright protection.",
                        "prefix": "must be “original” to qualify for ",
                        "suffix": "",
                    },
                    {
                        "exact": "whether the non-literal elements of a "
                        "program “are protected",
                        "prefix": "",
                        "suffix": "",
                    },
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${the_java_api} served a function",
                    "truth": True,
                },
                "terms": [{"generic": True, "name": "the Java API", "plural": False}],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "an original work — even one that serves a function",
                        "prefix": "",
                        "suffix": "",
                    }
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {"content": "${the_java_api} was creative", "truth": True},
                "terms": [{"generic": True, "name": "the Java API", "plural": False}],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "it is undisputed here that the declaring "
                        "code and the structure and organization of "
                        "the API packages are both creative",
                        "prefix": "",
                        "suffix": "",
                    }
                ],
            },
        },
    ],
    "enactment_anchors": [
        {
            "passage": {
                "enactment": {
                    "node": "/us/usc/t17/s102/a",
                    "start_date": datetime.date(2013, 7, 18),
                    "heading": "",
                    "text_version": {
                        "content": "Copyright "
                        "protection "
                        "subsists, in "
                        "accordance with "
                        "this title, in "
                        "original works of "
                        "authorship fixed in "
                        "any tangible medium "
                        "of expression, now "
                        "known or later "
                        "developed, from "
                        "which they can be "
                        "perceived, "
                        "reproduced, or "
                        "otherwise "
                        "communicated, "
                        "either directly or "
                        "with the aid of a "
                        "machine or device. "
                        "Works of authorship "
                        "include the "
                        "following "
                        "categories:",
                        "url": "https://authorityspoke.com/api/v1/textversions/1030579/",
                        "id": 1030579,
                    },
                    "end_date": None,
                    "first_published": None,
                    "earliest_in_db": None,
                    "anchors": [],
                    "citations": [],
                    "name": "/us/usc/t17/s102/a",
                    "children": [
                        {
                            "node": "/us/usc/t17/s102/a/1",
                            "start_date": datetime.date(2013, 7, 18),
                            "heading": "",
                            "text_version": {
                                "content": "literary works;",
                                "url": "https://authorityspoke.com/api/v1/textversions/1030571/",
                                "id": 1030571,
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
                            "node": "/us/usc/t17/s102/a/2",
                            "start_date": datetime.date(2013, 7, 18),
                            "heading": "",
                            "text_version": {
                                "content": "musical "
                                "works, "
                                "including "
                                "any "
                                "accompanying "
                                "words;",
                                "url": "https://authorityspoke.com/api/v1/textversions/1030572/",
                                "id": 1030572,
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
                            "node": "/us/usc/t17/s102/a/3",
                            "start_date": datetime.date(2013, 7, 18),
                            "heading": "",
                            "text_version": {
                                "content": "dramatic "
                                "works, "
                                "including "
                                "any "
                                "accompanying "
                                "music;",
                                "url": "https://authorityspoke.com/api/v1/textversions/1030573/",
                                "id": 1030573,
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
                            "node": "/us/usc/t17/s102/a/4",
                            "start_date": datetime.date(2013, 7, 18),
                            "heading": "",
                            "text_version": {
                                "content": "pantomimes and choreographic works;",
                                "url": "https://authorityspoke.com/api/v1/textversions/1030574/",
                                "id": 1030574,
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
                            "node": "/us/usc/t17/s102/a/5",
                            "start_date": datetime.date(2013, 7, 18),
                            "heading": "",
                            "text_version": {
                                "content": "pictorial, graphic, and sculptural works;",
                                "url": "https://authorityspoke.com/api/v1/textversions/1030575/",
                                "id": 1030575,
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
                            "node": "/us/usc/t17/s102/a/6",
                            "start_date": datetime.date(2013, 7, 18),
                            "heading": "",
                            "text_version": {
                                "content": "motion "
                                "pictures "
                                "and "
                                "other "
                                "audiovisual "
                                "works;",
                                "url": "https://authorityspoke.com/api/v1/textversions/1030576/",
                                "id": 1030576,
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
                            "node": "/us/usc/t17/s102/a/7",
                            "start_date": datetime.date(2013, 7, 18),
                            "heading": "",
                            "text_version": {
                                "content": "sound recordings; and",
                                "url": "https://authorityspoke.com/api/v1/textversions/1030577/",
                                "id": 1030577,
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
                            "node": "/us/usc/t17/s102/a/8",
                            "start_date": datetime.date(2013, 7, 18),
                            "heading": "",
                            "text_version": {
                                "content": "architectural works.",
                                "url": "https://authorityspoke.com/api/v1/textversions/1030578/",
                                "id": 1030578,
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
                            "exact": "Copyright protection "
                            "subsists, in accordance "
                            "with this title, in "
                            "original works of "
                            "authorship fixed in any "
                            "tangible medium of "
                            "expression, now known or "
                            "later developed, from "
                            "which they can be "
                            "perceived, reproduced, or "
                            "otherwise communicated, "
                            "either directly or with "
                            "the aid of a machine or "
                            "device.",
                            "prefix": "",
                            "suffix": "",
                        }
                    ],
                },
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "17 U.S.C. § 102(a)",
                        "prefix": "qualify for copyright protection. ",
                        "suffix": ".",
                    }
                ],
            },
        }
    ],
}


def _holdings_from_raw() -> HoldingGroup:
    parsed = AnchoredHoldings.model_validate(copy.deepcopy(RAW_ANCHORED_HOLDINGS))
    return HoldingGroup([item.holding for item in parsed.holdings])


def _entity_key(name: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in name).strip("_")


def _build_entities(holdings: HoldingGroup) -> dict[str, Entity]:
    entities: dict[str, Entity] = {}
    for holding in holdings:
        for term in holding.rule.recursive_terms.values():
            if isinstance(term, Entity):
                key = _entity_key(term.name)
                if key not in entities:
                    entities[key] = copy.deepcopy(term)
    return entities


HOLDINGS = _holdings_from_raw()
ENTITIES = _build_entities(HOLDINGS)


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
