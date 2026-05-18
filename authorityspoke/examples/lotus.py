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
                                    "content": "${borland_international} "
                                    "infringed "
                                    "the "
                                    "copyright "
                                    "in "
                                    "${the_lotus_menu_command_hierarchy}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Borland International",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Lotus menu command hierarchy",
                                        "plural": False,
                                    },
                                ],
                                "name": "Borland International "
                                "infringed the copyright in "
                                "the Lotus menu command "
                                "hierarchy",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_lotus_menu_command_hierarchy} "
                                    "was "
                                    "copyrightable",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Lotus menu command hierarchy",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Lotus menu command "
                                "hierarchy was copyrightable",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${borland_international} "
                                    "copied "
                                    "constituent "
                                    "elements "
                                    "of "
                                    "${the_lotus_menu_command_hierarchy} "
                                    "that were "
                                    "original",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Borland International",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Lotus menu command hierarchy",
                                        "plural": False,
                                    },
                                ],
                                "name": "Borland International "
                                "copied constituent elements "
                                "of the Lotus menu command "
                                "hierarchy that were "
                                "original",
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
                                            "exact": "",
                                            "prefix": "",
                                            "suffix": "Works of authorship include",
                                        }
                                    ],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {"passages": []},
                    "mandatory": False,
                    "universal": False,
                    "name": None,
                },
                "rule_valid": True,
                "decided": True,
                "exclusive": True,
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
                                    "predicate": {
                                        "content": "${the_lotus_menu_command_hierarchy} "
                                        "was "
                                        "copyrightable",
                                        "truth": True,
                                    },
                                    "terms": [
                                        {
                                            "generic": True,
                                            "name": "the Lotus menu command hierarchy",
                                            "plural": False,
                                        }
                                    ],
                                    "name": "the Lotus menu "
                                    "command "
                                    "hierarchy was "
                                    "copyrightable",
                                    "standard_of_proof": None,
                                },
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "absent": {
                                    "generic": False,
                                    "predicate": {
                                        "content": "${the_lotus_menu_command_hierarchy} "
                                        "was "
                                        "an "
                                        "original "
                                        "work",
                                        "truth": True,
                                    },
                                    "terms": [
                                        {
                                            "generic": True,
                                            "name": "the Lotus menu command hierarchy",
                                            "plural": False,
                                        }
                                    ],
                                    "name": "the Lotus menu "
                                    "command "
                                    "hierarchy was an "
                                    "original work",
                                    "standard_of_proof": None,
                                },
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
                                            "exact": "",
                                            "prefix": "",
                                            "suffix": "Works of authorship include",
                                        }
                                    ],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {"passages": []},
                    "mandatory": False,
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
                                    "content": "${the_lotus_menu_command_hierarchy} "
                                    "was "
                                    "copyrightable",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Lotus menu command hierarchy",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Lotus menu command "
                                "hierarchy was "
                                "copyrightable",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "exhibit": {
                                    "generic": False,
                                    "offered_by": {
                                        "generic": True,
                                        "name": "Lotus Development Corporation",
                                        "plural": False,
                                    },
                                    "form": "certificate of copyright registration",
                                    "statement": None,
                                    "statement_attribution": None,
                                    "name": "Lotus's copyright registration",
                                },
                                "to_effect": {
                                    "generic": False,
                                    "predicate": {
                                        "content": "${lotus_development_corporation} "
                                        "registered "
                                        "a "
                                        "copyright "
                                        "covering "
                                        "${the_lotus_menu_command_hierarchy}",
                                        "truth": True,
                                    },
                                    "terms": [
                                        {
                                            "generic": True,
                                            "name": "Lotus Development Corporation",
                                            "plural": False,
                                        },
                                        {
                                            "generic": True,
                                            "name": "the Lotus menu command hierarchy",
                                            "plural": False,
                                        },
                                    ],
                                    "name": "Lotus "
                                    "Development "
                                    "Corporation "
                                    "registered a "
                                    "copyright "
                                    "covering the "
                                    "Lotus menu "
                                    "command "
                                    "hierarchy",
                                    "standard_of_proof": None,
                                },
                                "name": "evidence of Lotus's copyright registration",
                            },
                            {
                                "generic": False,
                                "absent": {
                                    "generic": False,
                                    "predicate": {
                                        "content": "${the_lotus_menu_command_hierarchy} "
                                        "was "
                                        "copyrightable",
                                        "truth": False,
                                    },
                                    "terms": [
                                        {
                                            "generic": True,
                                            "name": "the Lotus menu command hierarchy",
                                            "plural": False,
                                        }
                                    ],
                                    "name": "false the Lotus "
                                    "menu command "
                                    "hierarchy was "
                                    "copyrightable",
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
                                    "node": "/us/usc/t17/s410/c",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "In "
                                        "any "
                                        "judicial "
                                        "proceedings "
                                        "the "
                                        "certificate "
                                        "of "
                                        "a "
                                        "registration "
                                        "made "
                                        "before "
                                        "or "
                                        "within "
                                        "five "
                                        "years "
                                        "after "
                                        "first "
                                        "publication "
                                        "of "
                                        "the "
                                        "work "
                                        "shall "
                                        "constitute "
                                        "prima "
                                        "facie "
                                        "evidence "
                                        "of "
                                        "the "
                                        "validity "
                                        "of "
                                        "the "
                                        "copyright "
                                        "and "
                                        "of "
                                        "the "
                                        "facts "
                                        "stated "
                                        "in "
                                        "the "
                                        "certificate. "
                                        "The "
                                        "evidentiary "
                                        "weight "
                                        "to "
                                        "be "
                                        "accorded "
                                        "the "
                                        "certificate "
                                        "of "
                                        "a "
                                        "registration "
                                        "made "
                                        "thereafter "
                                        "shall "
                                        "be "
                                        "within "
                                        "the "
                                        "discretion "
                                        "of "
                                        "the "
                                        "court.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1031576/",
                                        "id": 1031576,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s410/c",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [{"start": 0, "end": None}],
                                    "quotes": [],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {"passages": []},
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
                                    "content": "${borland_international} "
                                    "copied "
                                    "${the_lotus_menu_command_hierarchy} "
                                    "in "
                                    "creating "
                                    "Quattro's "
                                    "Lotus "
                                    "Emulation "
                                    "Interface",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Borland International",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Lotus menu command hierarchy",
                                        "plural": False,
                                    },
                                ],
                                "name": "Borland International "
                                "copied the Lotus menu "
                                "command hierarchy in "
                                "creating Quattro's Lotus "
                                "Emulation Interface",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "exhibit": {
                                    "generic": False,
                                    "offered_by": {
                                        "generic": True,
                                        "name": "Lotus Development Corporation",
                                        "plural": False,
                                    },
                                    "form": None,
                                    "statement": None,
                                    "statement_attribution": None,
                                    "name": "{'offered_by': "
                                    "'Lotus "
                                    "Development "
                                    "Corporation'}",
                                },
                                "to_effect": {
                                    "generic": False,
                                    "predicate": {
                                        "content": "${borland_international} "
                                        "copied "
                                        "${the_lotus_menu_command_hierarchy} "
                                        "in "
                                        "creating "
                                        "Quattro's "
                                        "Lotus "
                                        "Emulation "
                                        "Interface",
                                        "truth": True,
                                    },
                                    "terms": [
                                        {
                                            "generic": True,
                                            "name": "Borland International",
                                            "plural": False,
                                        },
                                        {
                                            "generic": True,
                                            "name": "the Lotus menu command hierarchy",
                                            "plural": False,
                                        },
                                    ],
                                    "name": "Borland "
                                    "International "
                                    "copied the "
                                    "Lotus menu "
                                    "command "
                                    "hierarchy in "
                                    "creating "
                                    "Quattro's "
                                    "Lotus "
                                    "Emulation "
                                    "Interface",
                                    "standard_of_proof": None,
                                },
                                "name": "evidence of {'offered_by': "
                                "'Lotus Development "
                                "Corporation'} to the effect "
                                "that Borland International "
                                "copied the Lotus menu "
                                "command hierarchy in "
                                "creating Quattro's Lotus "
                                "Emulation Interface",
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
                                            "exact": "",
                                            "prefix": "",
                                            "suffix": "Works of authorship include",
                                        }
                                    ],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {"passages": []},
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
                                    "content": "${borland_international} "
                                    "copied "
                                    "${the_lotus_menu_command_hierarchy} "
                                    "in "
                                    "creating "
                                    "Quattro's "
                                    "Lotus "
                                    "Emulation "
                                    "Interface",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Borland International",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Lotus menu command hierarchy",
                                        "plural": False,
                                    },
                                ],
                                "name": "Borland International "
                                "copied the Lotus menu "
                                "command hierarchy in "
                                "creating Quattro's Lotus "
                                "Emulation Interface",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "exhibit": {
                                    "generic": False,
                                    "offered_by": {
                                        "generic": True,
                                        "name": "Lotus Development Corporation",
                                        "plural": False,
                                    },
                                    "form": None,
                                    "statement": None,
                                    "statement_attribution": None,
                                    "name": "{'offered_by': "
                                    "'Lotus "
                                    "Development "
                                    "Corporation'}",
                                },
                                "to_effect": {
                                    "generic": False,
                                    "predicate": {
                                        "content": "${borland_international} "
                                        "had "
                                        "access "
                                        "to "
                                        "${the_lotus_menu_command_hierarchy}",
                                        "truth": True,
                                    },
                                    "terms": [
                                        {
                                            "generic": True,
                                            "name": "Borland International",
                                            "plural": False,
                                        },
                                        {
                                            "generic": True,
                                            "name": "the Lotus menu command hierarchy",
                                            "plural": False,
                                        },
                                    ],
                                    "name": "Borland "
                                    "International "
                                    "had access to "
                                    "the Lotus "
                                    "menu command "
                                    "hierarchy",
                                    "standard_of_proof": None,
                                },
                                "name": "evidence of {'offered_by': "
                                "'Lotus Development "
                                "Corporation'} to the effect "
                                "that Borland International "
                                "had access to the Lotus "
                                "menu command hierarchy",
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${borland_international} "
                                    "published "
                                    "${quattro_s_lotus_emulation_interface}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Borland International",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Quattro's Lotus Emulation Interface",
                                        "plural": False,
                                    },
                                ],
                                "name": "Borland International "
                                "published Quattro's Lotus "
                                "Emulation Interface",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "exhibit": {
                                    "generic": False,
                                    "offered_by": {
                                        "generic": True,
                                        "name": "Lotus Development Corporation",
                                        "plural": False,
                                    },
                                    "form": None,
                                    "statement": None,
                                    "statement_attribution": None,
                                    "name": "{'offered_by': "
                                    "'Lotus "
                                    "Development "
                                    "Corporation'}",
                                },
                                "to_effect": {
                                    "generic": False,
                                    "predicate": {
                                        "content": "${quattro_s_lotus_emulation_interface} "
                                        "was "
                                        "very "
                                        "similar "
                                        "to "
                                        "${the_lotus_menu_command_hierarchy}",
                                        "truth": True,
                                    },
                                    "terms": [
                                        {
                                            "generic": True,
                                            "name": "Quattro's "
                                            "Lotus "
                                            "Emulation "
                                            "Interface",
                                            "plural": False,
                                        },
                                        {
                                            "generic": True,
                                            "name": "the Lotus menu command hierarchy",
                                            "plural": False,
                                        },
                                    ],
                                    "name": "Quattro's "
                                    "Lotus "
                                    "Emulation "
                                    "Interface was "
                                    "very similar "
                                    "to the Lotus "
                                    "menu command "
                                    "hierarchy",
                                    "standard_of_proof": None,
                                },
                                "name": "evidence of {'offered_by': "
                                "'Lotus Development "
                                "Corporation'} to the effect "
                                "that Quattro's Lotus "
                                "Emulation Interface was "
                                "very similar to the Lotus "
                                "menu command hierarchy",
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
                                            "exact": "",
                                            "prefix": "",
                                            "suffix": "Works of authorship include",
                                        }
                                    ],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {"passages": []},
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
                                    "content": "${borland_international} "
                                    "copied "
                                    "constituent "
                                    "elements "
                                    "of "
                                    "${the_lotus_menu_command_hierarchy} "
                                    "that were "
                                    "original",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Borland International",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Lotus menu command hierarchy",
                                        "plural": False,
                                    },
                                ],
                                "name": "Borland International "
                                "copied constituent "
                                "elements of the Lotus menu "
                                "command hierarchy that "
                                "were original",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${borland_international} "
                                    "copied "
                                    "${the_lotus_menu_command_hierarchy} "
                                    "in "
                                    "creating "
                                    "Quattro's "
                                    "Lotus "
                                    "Emulation "
                                    "Interface",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Borland International",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Lotus menu command hierarchy",
                                        "plural": False,
                                    },
                                ],
                                "name": "Borland International "
                                "copied the Lotus menu "
                                "command hierarchy in "
                                "creating Quattro's Lotus "
                                "Emulation Interface",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "the "
                                    "copying of "
                                    "${quattro_s_lotus_emulation_interface} "
                                    "in "
                                    "${the_lotus_menu_command_hierarchy} "
                                    "was so "
                                    "extensive "
                                    "that it "
                                    "rendered "
                                    "them "
                                    "substantially "
                                    "similar",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Quattro's Lotus Emulation Interface",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Lotus menu command hierarchy",
                                        "plural": False,
                                    },
                                ],
                                "name": "the copying of Quattro's "
                                "Lotus Emulation Interface "
                                "in the Lotus menu command "
                                "hierarchy was so extensive "
                                "that it rendered them "
                                "substantially similar",
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
                                            "exact": "",
                                            "prefix": "",
                                            "suffix": "Works of authorship include",
                                        }
                                    ],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {"passages": []},
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
                                    "content": "${the_lotus_menu_command_hierarchy} "
                                    "was "
                                    "copyrightable",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Lotus menu command hierarchy",
                                        "plural": False,
                                    }
                                ],
                                "name": "false the Lotus menu "
                                "command hierarchy was "
                                "copyrightable",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_lotus_menu_command_hierarchy} "
                                    "was a "
                                    "method of "
                                    "operation",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Lotus menu command hierarchy",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Lotus menu command "
                                "hierarchy was a method of "
                                "operation",
                                "standard_of_proof": None,
                            }
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "a text "
                                    "described "
                                    "${the_lotus_menu_command_hierarchy}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Lotus menu command hierarchy",
                                        "plural": False,
                                    }
                                ],
                                "name": "a text described the Lotus "
                                "menu command hierarchy",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_lotus_menu_command_hierarchy} "
                                    "was an "
                                    "original "
                                    "work",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Lotus menu command hierarchy",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Lotus menu command "
                                "hierarchy was an original "
                                "work",
                                "standard_of_proof": None,
                            },
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
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "",
                                            "prefix": "",
                                            "suffix": "idea, procedure, process",
                                        },
                                        {
                                            "exact": "method of operation",
                                            "prefix": "",
                                            "suffix": "",
                                        },
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
                                    "content": "${the_lotus_menu_command_hierarchy} "
                                    "was a "
                                    "method of "
                                    "operation",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Lotus menu command hierarchy",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Lotus menu command "
                                "hierarchy was a method of "
                                "operation",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${lotus_1_2_3} was a computer program",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Lotus 1-2-3",
                                        "plural": False,
                                    }
                                ],
                                "name": "Lotus 1-2-3 was a computer program",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_lotus_menu_command_hierarchy} "
                                    "provided "
                                    "the means "
                                    "by which "
                                    "users "
                                    "controlled "
                                    "and "
                                    "operated "
                                    "${lotus_1_2_3}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Lotus menu command hierarchy",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Lotus 1-2-3",
                                        "plural": False,
                                    },
                                ],
                                "name": "the Lotus menu command "
                                "hierarchy provided the "
                                "means by which users "
                                "controlled and operated "
                                "Lotus 1-2-3",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "without "
                                    "${the_lotus_menu_command_hierarchy}, "
                                    "users "
                                    "would not "
                                    "have been "
                                    "able to "
                                    "access and "
                                    "control, "
                                    "or indeed "
                                    "make use "
                                    "of, "
                                    "${lotus_1_2_3}’s "
                                    "functional "
                                    "capabilities",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Lotus menu command hierarchy",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Lotus 1-2-3",
                                        "plural": False,
                                    },
                                ],
                                "name": "without the Lotus menu "
                                "command hierarchy, users "
                                "would not have been able to "
                                "access and control, or "
                                "indeed make use of, Lotus "
                                "1-2-3’s functional "
                                "capabilities",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "for "
                                    "another "
                                    "computer "
                                    "program to "
                                    "be "
                                    "operated "
                                    "in "
                                    "substantially "
                                    "the same "
                                    "way as "
                                    "${lotus_1_2_3}, "
                                    "the other "
                                    "program "
                                    "would have "
                                    "to copy "
                                    "${the_lotus_menu_command_hierarchy}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Lotus 1-2-3",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Lotus menu command hierarchy",
                                        "plural": False,
                                    },
                                ],
                                "name": "for another computer "
                                "program to be operated in "
                                "substantially the same way "
                                "as Lotus 1-2-3, the other "
                                "program would have to copy "
                                "the Lotus menu command "
                                "hierarchy",
                                "standard_of_proof": None,
                            },
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "the "
                                    "developers "
                                    "of "
                                    "${lotus_1_2_3} "
                                    "made some "
                                    "expressive "
                                    "choices "
                                    "in "
                                    "choosing "
                                    "and "
                                    "arranging "
                                    "the terms "
                                    "in "
                                    "${the_lotus_menu_command_hierarchy}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Lotus 1-2-3",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the Lotus menu command hierarchy",
                                        "plural": False,
                                    },
                                ],
                                "name": "the developers of Lotus "
                                "1-2-3 made some expressive "
                                "choices in choosing and "
                                "arranging the terms in the "
                                "Lotus menu command "
                                "hierarchy",
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
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "",
                                            "prefix": "",
                                            "suffix": "idea, procedure, process",
                                        },
                                        {
                                            "exact": "method of operation",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                    ],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {"passages": []},
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
                                    "content": "${the_lotus_menu_command_hierarchy} "
                                    "was a "
                                    "method of "
                                    "operation",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Lotus menu command hierarchy",
                                        "plural": False,
                                    }
                                ],
                                "name": "the Lotus menu command "
                                "hierarchy was a method of "
                                "operation",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_lotus_menu_command_hierarchy} "
                                    "was the "
                                    "means by "
                                    "which a "
                                    "person "
                                    "operated "
                                    "${lotus_1_2_3}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Lotus menu command hierarchy",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Lotus 1-2-3",
                                        "plural": False,
                                    },
                                ],
                                "name": "the Lotus menu command "
                                "hierarchy was the means by "
                                "which a person operated "
                                "Lotus 1-2-3",
                                "standard_of_proof": None,
                            }
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_lotus_menu_command_hierarchy} "
                                    "was an "
                                    "abstraction",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the Lotus menu command hierarchy",
                                        "plural": False,
                                    }
                                ],
                                "name": "false the Lotus menu "
                                "command hierarchy was an "
                                "abstraction",
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
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "",
                                            "prefix": "",
                                            "suffix": "idea, procedure, process",
                                        },
                                        {
                                            "exact": "method of operation",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                    ],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {"passages": []},
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
                                    "content": "${lotus_1_2_3} "
                                    "was a "
                                    "method of "
                                    "operation",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Lotus 1-2-3",
                                        "plural": False,
                                    }
                                ],
                                "name": "false Lotus 1-2-3 was a method of operation",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${lotus_1_2_3} was a computer program",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Lotus 1-2-3",
                                        "plural": False,
                                    }
                                ],
                                "name": "Lotus 1-2-3 was a computer program",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "the "
                                    "precise "
                                    "formulation "
                                    "of "
                                    "${lotus_1_2_3}'s "
                                    "code was "
                                    "necessary "
                                    "for "
                                    "${lotus_1_2_3} "
                                    "to work",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Lotus 1-2-3",
                                        "plural": False,
                                    }
                                ],
                                "name": "false the precise "
                                "formulation of Lotus "
                                "1-2-3's code was necessary "
                                "for Lotus 1-2-3 to work",
                                "standard_of_proof": None,
                            },
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "computer "
                                    "code was "
                                    "necessary "
                                    "for "
                                    "${lotus_1_2_3} "
                                    "to work",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Lotus 1-2-3",
                                        "plural": False,
                                    }
                                ],
                                "name": "computer code was "
                                "necessary for Lotus 1-2-3 "
                                "to work",
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
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "",
                                            "prefix": "",
                                            "suffix": "idea, procedure, process",
                                        },
                                        {
                                            "exact": "method of operation",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                    ],
                                },
                            }
                        ]
                    },
                    "enactments_despite": {"passages": []},
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
    "named_anchors": [],
    "enactment_anchors": [],
}


def anchored_holdings() -> AnchoredHoldings:
    """Build AnchoredHoldings for the Lotus case from Python model data."""
    return AnchoredHoldings.model_validate(copy.deepcopy(RAW_ANCHORED_HOLDINGS))
