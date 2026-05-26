import copy
import datetime


from nettlesome.entities import Entity


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
                                    "content": "${rural_s_telephone_directory} "
                                    "was "
                                    "copyrightable",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "false Rural's telephone "
                                "directory was "
                                "copyrightable",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${rural_s_telephone_directory} "
                                    "was a fact",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "Rural's telephone directory was a fact",
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
                                    "node": "/us/const/article/I/8/8",
                                    "start_date": datetime.date(1788, 9, 13),
                                    "heading": "Patents and copyrights.",
                                    "text_version": {
                                        "content": "To "
                                        "promote "
                                        "the "
                                        "Progress "
                                        "of "
                                        "Science "
                                        "and "
                                        "useful "
                                        "Arts, "
                                        "by "
                                        "securing "
                                        "for "
                                        "limited "
                                        "Times "
                                        "to "
                                        "Authors "
                                        "and "
                                        "Inventors "
                                        "the "
                                        "exclusive "
                                        "Right "
                                        "to "
                                        "their "
                                        "respective "
                                        "Writings "
                                        "and "
                                        "Discoveries;",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735650/",
                                        "id": 735650,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/article/I/8/8",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "To "
                                            "promote "
                                            "the "
                                            "Progress "
                                            "of "
                                            "Science "
                                            "and "
                                            "useful "
                                            "Arts, "
                                            "by "
                                            "securing "
                                            "for "
                                            "limited "
                                            "Times "
                                            "to "
                                            "Authors",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                        {
                                            "exact": "the "
                                            "exclusive "
                                            "Right "
                                            "to "
                                            "their "
                                            "respective "
                                            "Writings",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                    ],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s103/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "The "
                                        "copyright "
                                        "in "
                                        "a "
                                        "compilation "
                                        "or "
                                        "derivative "
                                        "work "
                                        "extends "
                                        "only "
                                        "to "
                                        "the "
                                        "material "
                                        "contributed "
                                        "by "
                                        "the "
                                        "author "
                                        "of "
                                        "such "
                                        "work, "
                                        "as "
                                        "distinguished "
                                        "from "
                                        "the "
                                        "preexisting "
                                        "material "
                                        "employed "
                                        "in "
                                        "the "
                                        "work, "
                                        "and "
                                        "does "
                                        "not "
                                        "imply "
                                        "any "
                                        "exclusive "
                                        "right "
                                        "in "
                                        "the "
                                        "preexisting "
                                        "material. "
                                        "The "
                                        "copyright "
                                        "in "
                                        "such "
                                        "work "
                                        "is "
                                        "independent "
                                        "of, "
                                        "and "
                                        "does "
                                        "not "
                                        "affect "
                                        "or "
                                        "enlarge "
                                        "the "
                                        "scope, "
                                        "duration, "
                                        "ownership, "
                                        "or "
                                        "subsistence "
                                        "of, "
                                        "any "
                                        "copyright "
                                        "protection "
                                        "in "
                                        "the "
                                        "preexisting "
                                        "material.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030582/",
                                        "id": 1030582,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s103/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "The copyright in a compilation",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                        {
                                            "exact": "extends "
                                            "only "
                                            "to "
                                            "the "
                                            "material "
                                            "contributed "
                                            "by "
                                            "the "
                                            "author "
                                            "of "
                                            "such "
                                            "work, "
                                            "as "
                                            "distinguished "
                                            "from "
                                            "the "
                                            "preexisting "
                                            "material "
                                            "employed "
                                            "in "
                                            "the "
                                            "work, "
                                            "and "
                                            "does "
                                            "not "
                                            "imply "
                                            "any "
                                            "exclusive "
                                            "right "
                                            "in "
                                            "the "
                                            "preexisting "
                                            "material.",
                                            "prefix": "",
                                            "suffix": "",
                                        },
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
                                "predicate": {
                                    "content": "${rural_s_telephone_directory} "
                                    "was "
                                    "copyrightable",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "Rural's telephone directory was copyrightable",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${rural_s_telephone_directory} "
                                    "was a "
                                    "compilation "
                                    "of facts",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "Rural's telephone directory "
                                "was a compilation of facts",
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
                                    "node": "/us/const/article/I/8/8",
                                    "start_date": datetime.date(1788, 9, 13),
                                    "heading": "Patents and copyrights.",
                                    "text_version": {
                                        "content": "To "
                                        "promote "
                                        "the "
                                        "Progress "
                                        "of "
                                        "Science "
                                        "and "
                                        "useful "
                                        "Arts, "
                                        "by "
                                        "securing "
                                        "for "
                                        "limited "
                                        "Times "
                                        "to "
                                        "Authors "
                                        "and "
                                        "Inventors "
                                        "the "
                                        "exclusive "
                                        "Right "
                                        "to "
                                        "their "
                                        "respective "
                                        "Writings "
                                        "and "
                                        "Discoveries;",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735650/",
                                        "id": 735650,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/article/I/8/8",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "To "
                                            "promote "
                                            "the "
                                            "Progress "
                                            "of "
                                            "Science "
                                            "and "
                                            "useful "
                                            "Arts, "
                                            "by "
                                            "securing "
                                            "for "
                                            "limited "
                                            "Times "
                                            "to "
                                            "Authors",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                        {
                                            "exact": "the "
                                            "exclusive "
                                            "Right "
                                            "to "
                                            "their "
                                            "respective "
                                            "Writings",
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
                        "exact": "generally are",
                        "prefix": "compilations of facts",
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
                                    "content": "${rural_s_telephone_directory} "
                                    "was "
                                    "copyrightable",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "false Rural's telephone "
                                "directory was "
                                "copyrightable",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${rural_s_telephone_directory} "
                                    "was an "
                                    "idea",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "Rural's telephone directory was an idea",
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
                                    "node": "/us/const/article/I/8/8",
                                    "start_date": datetime.date(1788, 9, 13),
                                    "heading": "Patents and copyrights.",
                                    "text_version": {
                                        "content": "To "
                                        "promote "
                                        "the "
                                        "Progress "
                                        "of "
                                        "Science "
                                        "and "
                                        "useful "
                                        "Arts, "
                                        "by "
                                        "securing "
                                        "for "
                                        "limited "
                                        "Times "
                                        "to "
                                        "Authors "
                                        "and "
                                        "Inventors "
                                        "the "
                                        "exclusive "
                                        "Right "
                                        "to "
                                        "their "
                                        "respective "
                                        "Writings "
                                        "and "
                                        "Discoveries;",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735650/",
                                        "id": 735650,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/article/I/8/8",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "To "
                                            "promote "
                                            "the "
                                            "Progress "
                                            "of "
                                            "Science "
                                            "and "
                                            "useful "
                                            "Arts, "
                                            "by "
                                            "securing "
                                            "for "
                                            "limited "
                                            "Times "
                                            "to "
                                            "Authors",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                        {
                                            "exact": "the "
                                            "exclusive "
                                            "Right "
                                            "to "
                                            "their "
                                            "respective "
                                            "Writings",
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
                                    "content": "${rural_s_telephone_directory} "
                                    "was "
                                    "copyrightable",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "Rural's telephone directory was copyrightable",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${rural_s_telephone_directory} "
                                    "was an "
                                    "original "
                                    "work",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "Rural's telephone directory "
                                "was an original work",
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
                                    "node": "/us/const/article/I/8/8",
                                    "start_date": datetime.date(1788, 9, 13),
                                    "heading": "Patents and copyrights.",
                                    "text_version": {
                                        "content": "To "
                                        "promote "
                                        "the "
                                        "Progress "
                                        "of "
                                        "Science "
                                        "and "
                                        "useful "
                                        "Arts, "
                                        "by "
                                        "securing "
                                        "for "
                                        "limited "
                                        "Times "
                                        "to "
                                        "Authors "
                                        "and "
                                        "Inventors "
                                        "the "
                                        "exclusive "
                                        "Right "
                                        "to "
                                        "their "
                                        "respective "
                                        "Writings "
                                        "and "
                                        "Discoveries;",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735650/",
                                        "id": 735650,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/article/I/8/8",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "To "
                                            "promote "
                                            "the "
                                            "Progress "
                                            "of "
                                            "Science "
                                            "and "
                                            "useful "
                                            "Arts, "
                                            "by "
                                            "securing "
                                            "for "
                                            "limited "
                                            "Times "
                                            "to "
                                            "Authors",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                        {
                                            "exact": "the "
                                            "exclusive "
                                            "Right "
                                            "to "
                                            "their "
                                            "respective "
                                            "Writings",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                    ],
                                },
                            },
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
                                            "suffix": "fixed in any tangible",
                                        }
                                    ],
                                },
                            },
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
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "The sine qua non of",
                        "prefix": "",
                        "suffix": "copyright",
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
                                    "content": "${rural_s_telephone_directory} "
                                    "was an "
                                    "original "
                                    "work",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "Rural's telephone "
                                "directory was an original "
                                "work",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${rural_s_telephone_directory} "
                                    "was "
                                    "independently "
                                    "created by "
                                    "${rural_telephone_service_company}, "
                                    "as opposed "
                                    "to copied "
                                    "from other "
                                    "works",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Rural Telephone Service Company",
                                        "plural": False,
                                    },
                                ],
                                "name": "Rural's telephone directory "
                                "was independently created "
                                "by Rural Telephone Service "
                                "Company, as opposed to "
                                "copied from other works",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${rural_s_telephone_directory} "
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
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "Rural's telephone directory "
                                "possessed at least some "
                                "minimal degree of "
                                "creativity",
                                "standard_of_proof": None,
                            },
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${rural_s_telephone_directory} "
                                    "closely "
                                    "resembled "
                                    "other "
                                    "works",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "Rural's telephone "
                                "directory closely "
                                "resembled other works",
                                "standard_of_proof": None,
                            }
                        ],
                        "name": "",
                    },
                    "enactments": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/const/article/I/8/8",
                                    "start_date": datetime.date(1788, 9, 13),
                                    "heading": "Patents and copyrights.",
                                    "text_version": {
                                        "content": "To "
                                        "promote "
                                        "the "
                                        "Progress "
                                        "of "
                                        "Science "
                                        "and "
                                        "useful "
                                        "Arts, "
                                        "by "
                                        "securing "
                                        "for "
                                        "limited "
                                        "Times "
                                        "to "
                                        "Authors "
                                        "and "
                                        "Inventors "
                                        "the "
                                        "exclusive "
                                        "Right "
                                        "to "
                                        "their "
                                        "respective "
                                        "Writings "
                                        "and "
                                        "Discoveries;",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735650/",
                                        "id": 735650,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/article/I/8/8",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "To "
                                            "promote "
                                            "the "
                                            "Progress "
                                            "of "
                                            "Science "
                                            "and "
                                            "useful "
                                            "Arts, "
                                            "by "
                                            "securing "
                                            "for "
                                            "limited "
                                            "Times "
                                            "to "
                                            "Authors",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                        {
                                            "exact": "the "
                                            "exclusive "
                                            "Right "
                                            "to "
                                            "their "
                                            "respective "
                                            "Writings",
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
                    "universal": True,
                    "name": None,
                },
                "rule_valid": True,
                "decided": True,
                "exclusive": False,
            },
            "anchors": {
                "positions": [],
                "quotes": [{"exact": "means only that", "prefix": "", "suffix": ""}],
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
                                    "content": "${rural_s_telephone_directory} "
                                    "was an "
                                    "original "
                                    "work",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "false Rural's telephone "
                                "directory was an original "
                                "work",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${rural_s_telephone_directory} "
                                    "was a fact",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "Rural's telephone directory was a fact",
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
                                    "node": "/us/const/article/I/8/8",
                                    "start_date": datetime.date(1788, 9, 13),
                                    "heading": "Patents and copyrights.",
                                    "text_version": {
                                        "content": "To "
                                        "promote "
                                        "the "
                                        "Progress "
                                        "of "
                                        "Science "
                                        "and "
                                        "useful "
                                        "Arts, "
                                        "by "
                                        "securing "
                                        "for "
                                        "limited "
                                        "Times "
                                        "to "
                                        "Authors "
                                        "and "
                                        "Inventors "
                                        "the "
                                        "exclusive "
                                        "Right "
                                        "to "
                                        "their "
                                        "respective "
                                        "Writings "
                                        "and "
                                        "Discoveries;",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735650/",
                                        "id": 735650,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/article/I/8/8",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "To "
                                            "promote "
                                            "the "
                                            "Progress "
                                            "of "
                                            "Science "
                                            "and "
                                            "useful "
                                            "Arts, "
                                            "by "
                                            "securing "
                                            "for "
                                            "limited "
                                            "Times "
                                            "to "
                                            "Authors",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                        {
                                            "exact": "the "
                                            "exclusive "
                                            "Right "
                                            "to "
                                            "their "
                                            "respective "
                                            "Writings",
                                            "prefix": "",
                                            "suffix": "",
                                        },
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
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "The end product is a garden-variety white pages "
                        "directory, devoid of even the slightest trace of "
                        "creativity.",
                        "prefix": "",
                        "suffix": "",
                    },
                    {
                        "exact": "Rural’s selection of listings could not be more "
                        "obvious: It publishes the most basic information "
                        "— name, town, and telephone number — about each "
                        "person who applies to it for telephone service. "
                        "This is “selection” of a sort, but it lacks the "
                        "modicum of creativity necessary to transform mere "
                        "selection into copyrightable expression.",
                        "prefix": "",
                        "suffix": "",
                    },
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
                                    "content": "${rural_s_telephone_directory} "
                                    "was an "
                                    "original "
                                    "work",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "Rural's telephone "
                                "directory was an original "
                                "work",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${rural_s_telephone_directory} "
                                    "was a "
                                    "compilation "
                                    "of facts",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "Rural's telephone directory "
                                "was a compilation of facts",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${rural_telephone_service_company} "
                                    "was the "
                                    "compiler "
                                    "of "
                                    "${rural_s_telephone_directory}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural Telephone Service Company",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    },
                                ],
                                "name": "Rural Telephone Service "
                                "Company was the compiler of "
                                "Rural's telephone directory",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${rural_telephone_service_company} "
                                    "independently "
                                    "used a "
                                    "degree of "
                                    "creativity "
                                    "to choose "
                                    "which "
                                    "facts to "
                                    "include in "
                                    "${rural_s_telephone_directory}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural Telephone Service Company",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    },
                                ],
                                "name": "Rural Telephone Service "
                                "Company independently used "
                                "a degree of creativity to "
                                "choose which facts to "
                                "include in Rural's "
                                "telephone directory",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${rural_telephone_service_company} "
                                    "independently "
                                    "used a "
                                    "degree of "
                                    "creativity "
                                    "to choose "
                                    "in what "
                                    "order to "
                                    "place the "
                                    "facts in "
                                    "${rural_s_telephone_directory}, "
                                    "and how to "
                                    "arrange "
                                    "the "
                                    "collected "
                                    "data so "
                                    "that they "
                                    "could be "
                                    "used "
                                    "effectively "
                                    "by readers",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural Telephone Service Company",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    },
                                ],
                                "name": "Rural Telephone Service "
                                "Company independently used "
                                "a degree of creativity to "
                                "choose in what order to "
                                "place the facts in Rural's "
                                "telephone directory, and "
                                "how to arrange the "
                                "collected data so that they "
                                "could be used effectively "
                                "by readers",
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
                                    "node": "/us/const/article/I/8/8",
                                    "start_date": datetime.date(1788, 9, 13),
                                    "heading": "Patents and copyrights.",
                                    "text_version": {
                                        "content": "To "
                                        "promote "
                                        "the "
                                        "Progress "
                                        "of "
                                        "Science "
                                        "and "
                                        "useful "
                                        "Arts, "
                                        "by "
                                        "securing "
                                        "for "
                                        "limited "
                                        "Times "
                                        "to "
                                        "Authors "
                                        "and "
                                        "Inventors "
                                        "the "
                                        "exclusive "
                                        "Right "
                                        "to "
                                        "their "
                                        "respective "
                                        "Writings "
                                        "and "
                                        "Discoveries;",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735650/",
                                        "id": 735650,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/article/I/8/8",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "To "
                                            "promote "
                                            "the "
                                            "Progress "
                                            "of "
                                            "Science "
                                            "and "
                                            "useful "
                                            "Arts, "
                                            "by "
                                            "securing "
                                            "for "
                                            "limited "
                                            "Times "
                                            "to "
                                            "Authors",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                        {
                                            "exact": "the "
                                            "exclusive "
                                            "Right "
                                            "to "
                                            "their "
                                            "respective "
                                            "Writings",
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
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "trigger",
                        "prefix": "Census data therefore do not",
                        "suffix": "copyright",
                    },
                    {
                        "exact": "may",
                        "prefix": "",
                        "suffix": "possess the requisite originality",
                    },
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
                                    "content": "${rural_s_telephone_directory} "
                                    "was "
                                    "copyrightable",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "false Rural's telephone "
                                "directory was "
                                "copyrightable",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${rural_s_telephone_directory} "
                                    "was a "
                                    "compilation "
                                    "of facts",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "Rural's telephone directory "
                                "was a compilation of facts",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${rural_s_telephone_directory} "
                                    "contained "
                                    "written "
                                    "expression "
                                    "protectable "
                                    "by "
                                    "copyright",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "false Rural's telephone "
                                "directory contained written "
                                "expression protectable by "
                                "copyright",
                                "standard_of_proof": None,
                            },
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${rural_telephone_service_company} "
                                    "independently "
                                    "used a "
                                    "degree of "
                                    "creativity "
                                    "to choose "
                                    "which "
                                    "facts to "
                                    "include "
                                    "in "
                                    "${rural_s_telephone_directory}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural Telephone Service Company",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    },
                                ],
                                "name": "Rural Telephone Service "
                                "Company independently used "
                                "a degree of creativity to "
                                "choose which facts to "
                                "include in Rural's "
                                "telephone directory",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${rural_telephone_service_company} "
                                    "independently "
                                    "used a "
                                    "degree of "
                                    "creativity "
                                    "to choose "
                                    "in what "
                                    "order to "
                                    "place the "
                                    "facts in "
                                    "${rural_s_telephone_directory}, "
                                    "and how "
                                    "to "
                                    "arrange "
                                    "the "
                                    "collected "
                                    "data so "
                                    "that they "
                                    "could be "
                                    "used "
                                    "effectively "
                                    "by "
                                    "readers",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural Telephone Service Company",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    },
                                ],
                                "name": "Rural Telephone Service "
                                "Company independently used "
                                "a degree of creativity to "
                                "choose in what order to "
                                "place the facts in Rural's "
                                "telephone directory, and "
                                "how to arrange the "
                                "collected data so that "
                                "they could be used "
                                "effectively by readers",
                                "standard_of_proof": None,
                            },
                        ],
                        "name": "",
                    },
                    "enactments": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/const/article/I/8/8",
                                    "start_date": datetime.date(1788, 9, 13),
                                    "heading": "Patents and copyrights.",
                                    "text_version": {
                                        "content": "To "
                                        "promote "
                                        "the "
                                        "Progress "
                                        "of "
                                        "Science "
                                        "and "
                                        "useful "
                                        "Arts, "
                                        "by "
                                        "securing "
                                        "for "
                                        "limited "
                                        "Times "
                                        "to "
                                        "Authors "
                                        "and "
                                        "Inventors "
                                        "the "
                                        "exclusive "
                                        "Right "
                                        "to "
                                        "their "
                                        "respective "
                                        "Writings "
                                        "and "
                                        "Discoveries;",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735650/",
                                        "id": 735650,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/article/I/8/8",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "To "
                                            "promote "
                                            "the "
                                            "Progress "
                                            "of "
                                            "Science "
                                            "and "
                                            "useful "
                                            "Arts, "
                                            "by "
                                            "securing "
                                            "for "
                                            "limited "
                                            "Times "
                                            "to "
                                            "Authors",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                        {
                                            "exact": "the "
                                            "exclusive "
                                            "Right "
                                            "to "
                                            "their "
                                            "respective "
                                            "Writings",
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
                                    "content": "${feist_publications} "
                                    "infringed "
                                    "the "
                                    "copyright "
                                    "on "
                                    "${rural_s_telephone_directory}",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Feist Publications",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    },
                                ],
                                "name": "false Feist Publications "
                                "infringed the copyright on "
                                "Rural's telephone "
                                "directory",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${rural_s_telephone_directory} "
                                    "was a "
                                    "compilation "
                                    "of facts",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "Rural's telephone directory "
                                "was a compilation of facts",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${feist_s_telephone_directory} "
                                    "did not "
                                    "feature "
                                    "the same "
                                    "selection "
                                    "and "
                                    "arrangement "
                                    "of facts "
                                    "as "
                                    "${rural_s_telephone_directory}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Feist's telephone directory",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    },
                                ],
                                "name": "Feist's telephone directory "
                                "did not feature the same "
                                "selection and arrangement "
                                "of facts as Rural's "
                                "telephone directory",
                                "standard_of_proof": None,
                            },
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${rural_s_telephone_directory} "
                                    "was "
                                    "copyrightable",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "Rural's telephone directory was copyrightable",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${feist_publications} "
                                    "freely "
                                    "copied "
                                    "the facts "
                                    "contained "
                                    "in "
                                    "${rural_s_telephone_directory}, "
                                    "in "
                                    "preparing "
                                    "${feist_s_telephone_directory}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Feist Publications",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Feist's telephone directory",
                                        "plural": False,
                                    },
                                ],
                                "name": "Feist Publications freely "
                                "copied the facts contained "
                                "in Rural's telephone "
                                "directory, in preparing "
                                "Feist's telephone "
                                "directory",
                                "standard_of_proof": None,
                            },
                        ],
                        "name": "",
                    },
                    "enactments": {
                        "passages": [
                            {
                                "enactment": {
                                    "node": "/us/const/article/I/8/8",
                                    "start_date": datetime.date(1788, 9, 13),
                                    "heading": "Patents and copyrights.",
                                    "text_version": {
                                        "content": "To "
                                        "promote "
                                        "the "
                                        "Progress "
                                        "of "
                                        "Science "
                                        "and "
                                        "useful "
                                        "Arts, "
                                        "by "
                                        "securing "
                                        "for "
                                        "limited "
                                        "Times "
                                        "to "
                                        "Authors "
                                        "and "
                                        "Inventors "
                                        "the "
                                        "exclusive "
                                        "Right "
                                        "to "
                                        "their "
                                        "respective "
                                        "Writings "
                                        "and "
                                        "Discoveries;",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735650/",
                                        "id": 735650,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/article/I/8/8",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "To "
                                            "promote "
                                            "the "
                                            "Progress "
                                            "of "
                                            "Science "
                                            "and "
                                            "useful "
                                            "Arts, "
                                            "by "
                                            "securing "
                                            "for "
                                            "limited "
                                            "Times "
                                            "to "
                                            "Authors",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                        {
                                            "exact": "the "
                                            "exclusive "
                                            "Right "
                                            "to "
                                            "their "
                                            "respective "
                                            "Writings",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                    ],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s103/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "The "
                                        "copyright "
                                        "in "
                                        "a "
                                        "compilation "
                                        "or "
                                        "derivative "
                                        "work "
                                        "extends "
                                        "only "
                                        "to "
                                        "the "
                                        "material "
                                        "contributed "
                                        "by "
                                        "the "
                                        "author "
                                        "of "
                                        "such "
                                        "work, "
                                        "as "
                                        "distinguished "
                                        "from "
                                        "the "
                                        "preexisting "
                                        "material "
                                        "employed "
                                        "in "
                                        "the "
                                        "work, "
                                        "and "
                                        "does "
                                        "not "
                                        "imply "
                                        "any "
                                        "exclusive "
                                        "right "
                                        "in "
                                        "the "
                                        "preexisting "
                                        "material. "
                                        "The "
                                        "copyright "
                                        "in "
                                        "such "
                                        "work "
                                        "is "
                                        "independent "
                                        "of, "
                                        "and "
                                        "does "
                                        "not "
                                        "affect "
                                        "or "
                                        "enlarge "
                                        "the "
                                        "scope, "
                                        "duration, "
                                        "ownership, "
                                        "or "
                                        "subsistence "
                                        "of, "
                                        "any "
                                        "copyright "
                                        "protection "
                                        "in "
                                        "the "
                                        "preexisting "
                                        "material.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030582/",
                                        "id": 1030582,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s103/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "The copyright in a compilation",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                        {
                                            "exact": "extends "
                                            "only "
                                            "to "
                                            "the "
                                            "material "
                                            "contributed "
                                            "by "
                                            "the "
                                            "author "
                                            "of "
                                            "such "
                                            "work, "
                                            "as "
                                            "distinguished "
                                            "from "
                                            "the "
                                            "preexisting "
                                            "material "
                                            "employed "
                                            "in "
                                            "the "
                                            "work, "
                                            "and "
                                            "does "
                                            "not "
                                            "imply "
                                            "any "
                                            "exclusive "
                                            "right "
                                            "in "
                                            "the "
                                            "preexisting "
                                            "material.",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                    ],
                                },
                            },
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
                                    "content": "${rural_s_telephone_directory} "
                                    "was "
                                    "copyrightable",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "false Rural's telephone "
                                "directory was "
                                "copyrightable",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${rural_s_telephone_directory} "
                                    "was a "
                                    "compilation "
                                    "of facts",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "Rural's telephone directory "
                                "was a compilation of facts",
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
                                    "node": "/us/const/article/I/8/8",
                                    "start_date": datetime.date(1788, 9, 13),
                                    "heading": "Patents and copyrights.",
                                    "text_version": {
                                        "content": "To "
                                        "promote "
                                        "the "
                                        "Progress "
                                        "of "
                                        "Science "
                                        "and "
                                        "useful "
                                        "Arts, "
                                        "by "
                                        "securing "
                                        "for "
                                        "limited "
                                        "Times "
                                        "to "
                                        "Authors "
                                        "and "
                                        "Inventors "
                                        "the "
                                        "exclusive "
                                        "Right "
                                        "to "
                                        "their "
                                        "respective "
                                        "Writings "
                                        "and "
                                        "Discoveries;",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735650/",
                                        "id": 735650,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/article/I/8/8",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "To "
                                            "promote "
                                            "the "
                                            "Progress "
                                            "of "
                                            "Science "
                                            "and "
                                            "useful "
                                            "Arts, "
                                            "by "
                                            "securing "
                                            "for "
                                            "limited "
                                            "Times "
                                            "to "
                                            "Authors",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                        {
                                            "exact": "the "
                                            "exclusive "
                                            "Right "
                                            "to "
                                            "their "
                                            "respective "
                                            "Writings",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                    ],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s103/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "The "
                                        "copyright "
                                        "in "
                                        "a "
                                        "compilation "
                                        "or "
                                        "derivative "
                                        "work "
                                        "extends "
                                        "only "
                                        "to "
                                        "the "
                                        "material "
                                        "contributed "
                                        "by "
                                        "the "
                                        "author "
                                        "of "
                                        "such "
                                        "work, "
                                        "as "
                                        "distinguished "
                                        "from "
                                        "the "
                                        "preexisting "
                                        "material "
                                        "employed "
                                        "in "
                                        "the "
                                        "work, "
                                        "and "
                                        "does "
                                        "not "
                                        "imply "
                                        "any "
                                        "exclusive "
                                        "right "
                                        "in "
                                        "the "
                                        "preexisting "
                                        "material. "
                                        "The "
                                        "copyright "
                                        "in "
                                        "such "
                                        "work "
                                        "is "
                                        "independent "
                                        "of, "
                                        "and "
                                        "does "
                                        "not "
                                        "affect "
                                        "or "
                                        "enlarge "
                                        "the "
                                        "scope, "
                                        "duration, "
                                        "ownership, "
                                        "or "
                                        "subsistence "
                                        "of, "
                                        "any "
                                        "copyright "
                                        "protection "
                                        "in "
                                        "the "
                                        "preexisting "
                                        "material.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030582/",
                                        "id": 1030582,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s103/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "The copyright in a compilation",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                        {
                                            "exact": "extends "
                                            "only "
                                            "to "
                                            "the "
                                            "material "
                                            "contributed "
                                            "by "
                                            "the "
                                            "author "
                                            "of "
                                            "such "
                                            "work, "
                                            "as "
                                            "distinguished "
                                            "from "
                                            "the "
                                            "preexisting "
                                            "material "
                                            "employed "
                                            "in "
                                            "the "
                                            "work, "
                                            "and "
                                            "does "
                                            "not "
                                            "imply "
                                            "any "
                                            "exclusive "
                                            "right "
                                            "in "
                                            "the "
                                            "preexisting "
                                            "material.",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                    ],
                                },
                            },
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
                                    "content": "${rural_s_telephone_listings} "
                                    "were an "
                                    "original "
                                    "work",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone listings",
                                        "plural": True,
                                    }
                                ],
                                "name": "false Rural's telephone "
                                "listings were an original "
                                "work",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${rural_s_telephone_listings} "
                                    "were "
                                    "names, "
                                    "towns, and "
                                    "telephone "
                                    "numbers of "
                                    "telephone "
                                    "subscribers",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone listings",
                                        "plural": True,
                                    }
                                ],
                                "name": "Rural's telephone listings "
                                "were names, towns, and "
                                "telephone numbers of "
                                "telephone subscribers",
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
                                    "node": "/us/const/article/I/8/8",
                                    "start_date": datetime.date(1788, 9, 13),
                                    "heading": "Patents and copyrights.",
                                    "text_version": {
                                        "content": "To "
                                        "promote "
                                        "the "
                                        "Progress "
                                        "of "
                                        "Science "
                                        "and "
                                        "useful "
                                        "Arts, "
                                        "by "
                                        "securing "
                                        "for "
                                        "limited "
                                        "Times "
                                        "to "
                                        "Authors "
                                        "and "
                                        "Inventors "
                                        "the "
                                        "exclusive "
                                        "Right "
                                        "to "
                                        "their "
                                        "respective "
                                        "Writings "
                                        "and "
                                        "Discoveries;",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735650/",
                                        "id": 735650,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/article/I/8/8",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "To "
                                            "promote "
                                            "the "
                                            "Progress "
                                            "of "
                                            "Science "
                                            "and "
                                            "useful "
                                            "Arts, "
                                            "by "
                                            "securing "
                                            "for "
                                            "limited "
                                            "Times "
                                            "to "
                                            "Authors",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                        {
                                            "exact": "the "
                                            "exclusive "
                                            "Right "
                                            "to "
                                            "their "
                                            "respective "
                                            "Writings",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                    ],
                                },
                            },
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
                                            "suffix": "fixed in any tangible",
                                        }
                                    ],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s103/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "The "
                                        "copyright "
                                        "in "
                                        "a "
                                        "compilation "
                                        "or "
                                        "derivative "
                                        "work "
                                        "extends "
                                        "only "
                                        "to "
                                        "the "
                                        "material "
                                        "contributed "
                                        "by "
                                        "the "
                                        "author "
                                        "of "
                                        "such "
                                        "work, "
                                        "as "
                                        "distinguished "
                                        "from "
                                        "the "
                                        "preexisting "
                                        "material "
                                        "employed "
                                        "in "
                                        "the "
                                        "work, "
                                        "and "
                                        "does "
                                        "not "
                                        "imply "
                                        "any "
                                        "exclusive "
                                        "right "
                                        "in "
                                        "the "
                                        "preexisting "
                                        "material. "
                                        "The "
                                        "copyright "
                                        "in "
                                        "such "
                                        "work "
                                        "is "
                                        "independent "
                                        "of, "
                                        "and "
                                        "does "
                                        "not "
                                        "affect "
                                        "or "
                                        "enlarge "
                                        "the "
                                        "scope, "
                                        "duration, "
                                        "ownership, "
                                        "or "
                                        "subsistence "
                                        "of, "
                                        "any "
                                        "copyright "
                                        "protection "
                                        "in "
                                        "the "
                                        "preexisting "
                                        "material.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030582/",
                                        "id": 1030582,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s103/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "The copyright in a compilation",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                        {
                                            "exact": "extends "
                                            "only "
                                            "to "
                                            "the "
                                            "material "
                                            "contributed "
                                            "by "
                                            "the "
                                            "author "
                                            "of "
                                            "such "
                                            "work, "
                                            "as "
                                            "distinguished "
                                            "from "
                                            "the "
                                            "preexisting "
                                            "material "
                                            "employed "
                                            "in "
                                            "the "
                                            "work, "
                                            "and "
                                            "does "
                                            "not "
                                            "imply "
                                            "any "
                                            "exclusive "
                                            "right "
                                            "in "
                                            "the "
                                            "preexisting "
                                            "material.",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                    ],
                                },
                            },
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
                                    "content": "${rural_s_arragement_of_its_telephone_listings} "
                                    "was an "
                                    "original "
                                    "work",
                                    "truth": False,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's "
                                        "arragement of "
                                        "its telephone "
                                        "listings",
                                        "plural": False,
                                    }
                                ],
                                "name": "false Rural's arragement "
                                "of its telephone listings "
                                "was an original work",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${rural_s_telephone_directory} "
                                    "was a "
                                    "telephone "
                                    "directory",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    }
                                ],
                                "name": "Rural's telephone directory "
                                "was a telephone directory",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${rural_s_arragement_of_its_telephone_listings} "
                                    "was the "
                                    "method of "
                                    "listing "
                                    "subscribers "
                                    "alphabetically "
                                    "by surname "
                                    "in "
                                    "${rural_s_telephone_directory}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Rural's "
                                        "arragement of "
                                        "its telephone "
                                        "listings",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Rural's telephone directory",
                                        "plural": False,
                                    },
                                ],
                                "name": "Rural's arragement of its "
                                "telephone listings was the "
                                "method of listing "
                                "subscribers alphabetically "
                                "by surname in Rural's "
                                "telephone directory",
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
                                    "node": "/us/const/article/I/8/8",
                                    "start_date": datetime.date(1788, 9, 13),
                                    "heading": "Patents and copyrights.",
                                    "text_version": {
                                        "content": "To "
                                        "promote "
                                        "the "
                                        "Progress "
                                        "of "
                                        "Science "
                                        "and "
                                        "useful "
                                        "Arts, "
                                        "by "
                                        "securing "
                                        "for "
                                        "limited "
                                        "Times "
                                        "to "
                                        "Authors "
                                        "and "
                                        "Inventors "
                                        "the "
                                        "exclusive "
                                        "Right "
                                        "to "
                                        "their "
                                        "respective "
                                        "Writings "
                                        "and "
                                        "Discoveries;",
                                        "url": "https://authorityspoke.com/api/v1/textversions/735650/",
                                        "id": 735650,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/const/article/I/8/8",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "To "
                                            "promote "
                                            "the "
                                            "Progress "
                                            "of "
                                            "Science "
                                            "and "
                                            "useful "
                                            "Arts, "
                                            "by "
                                            "securing "
                                            "for "
                                            "limited "
                                            "Times "
                                            "to "
                                            "Authors",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                        {
                                            "exact": "the "
                                            "exclusive "
                                            "Right "
                                            "to "
                                            "their "
                                            "respective "
                                            "Writings",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                    ],
                                },
                            },
                            {
                                "enactment": {
                                    "node": "/us/usc/t17/s103/b",
                                    "start_date": datetime.date(2013, 7, 18),
                                    "heading": "",
                                    "text_version": {
                                        "content": "The "
                                        "copyright "
                                        "in "
                                        "a "
                                        "compilation "
                                        "or "
                                        "derivative "
                                        "work "
                                        "extends "
                                        "only "
                                        "to "
                                        "the "
                                        "material "
                                        "contributed "
                                        "by "
                                        "the "
                                        "author "
                                        "of "
                                        "such "
                                        "work, "
                                        "as "
                                        "distinguished "
                                        "from "
                                        "the "
                                        "preexisting "
                                        "material "
                                        "employed "
                                        "in "
                                        "the "
                                        "work, "
                                        "and "
                                        "does "
                                        "not "
                                        "imply "
                                        "any "
                                        "exclusive "
                                        "right "
                                        "in "
                                        "the "
                                        "preexisting "
                                        "material. "
                                        "The "
                                        "copyright "
                                        "in "
                                        "such "
                                        "work "
                                        "is "
                                        "independent "
                                        "of, "
                                        "and "
                                        "does "
                                        "not "
                                        "affect "
                                        "or "
                                        "enlarge "
                                        "the "
                                        "scope, "
                                        "duration, "
                                        "ownership, "
                                        "or "
                                        "subsistence "
                                        "of, "
                                        "any "
                                        "copyright "
                                        "protection "
                                        "in "
                                        "the "
                                        "preexisting "
                                        "material.",
                                        "url": "https://authorityspoke.com/api/v1/textversions/1030582/",
                                        "id": 1030582,
                                    },
                                    "end_date": None,
                                    "first_published": None,
                                    "earliest_in_db": None,
                                    "anchors": [],
                                    "citations": [],
                                    "name": "/us/usc/t17/s103/b",
                                    "children": [],
                                },
                                "selection": {
                                    "positions": [],
                                    "quotes": [
                                        {
                                            "exact": "The copyright in a compilation",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                        {
                                            "exact": "extends "
                                            "only "
                                            "to "
                                            "the "
                                            "material "
                                            "contributed "
                                            "by "
                                            "the "
                                            "author "
                                            "of "
                                            "such "
                                            "work, "
                                            "as "
                                            "distinguished "
                                            "from "
                                            "the "
                                            "preexisting "
                                            "material "
                                            "employed "
                                            "in "
                                            "the "
                                            "work, "
                                            "and "
                                            "does "
                                            "not "
                                            "imply "
                                            "any "
                                            "exclusive "
                                            "right "
                                            "in "
                                            "the "
                                            "preexisting "
                                            "material.",
                                            "prefix": "",
                                            "suffix": "",
                                        },
                                    ],
                                },
                            },
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
    "named_anchors": [
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${rural_telephone_service_company} "
                    "independently used a degree of creativity "
                    "to choose in what order to place the facts "
                    "in ${rural_s_telephone_directory}, and how "
                    "to arrange the collected data so that they "
                    "could be used effectively by readers",
                    "truth": True,
                },
                "terms": [
                    {
                        "generic": True,
                        "name": "Rural Telephone Service Company",
                        "plural": False,
                    },
                    {
                        "generic": True,
                        "name": "Rural's telephone directory",
                        "plural": False,
                    },
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "The compilation author typically chooses",
                        "prefix": "",
                        "suffix": "",
                    },
                    {
                        "exact": "in what order to place them, and how to "
                        "arrange the collected data so that they may "
                        "be used effectively by readers",
                        "prefix": "",
                        "suffix": "",
                    },
                    {
                        "exact": "so long as they are made independently",
                        "prefix": "",
                        "suffix": "",
                    },
                    {
                        "exact": "and entail a minimal degree of creativity",
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
                    "content": "${rural_s_arragement_of_its_telephone_listings} "
                    "was the method of listing subscribers "
                    "alphabetically by surname in "
                    "${rural_s_telephone_directory}",
                    "truth": True,
                },
                "terms": [
                    {
                        "generic": True,
                        "name": "Rural's arragement of its telephone listings",
                        "plural": False,
                    },
                    {
                        "generic": True,
                        "name": "Rural's telephone directory",
                        "plural": False,
                    },
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "In preparing its white pages, Rural simply "
                        "takes the data provided by its subscribers "
                        "and lists it alphabetically by surname.",
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
                    "content": "${rural_telephone_service_company} "
                    "independently used a degree of creativity "
                    "to choose which facts to include in "
                    "${rural_s_telephone_directory}",
                    "truth": True,
                },
                "terms": [
                    {
                        "generic": True,
                        "name": "Rural Telephone Service Company",
                        "plural": False,
                    },
                    {
                        "generic": True,
                        "name": "Rural's telephone directory",
                        "plural": False,
                    },
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "The compilation author typically chooses "
                        "which facts to include",
                        "prefix": "",
                        "suffix": "",
                    },
                    {
                        "exact": "so long as they are made independently",
                        "prefix": "",
                        "suffix": "",
                    },
                    {
                        "exact": "and entail a minimal degree of creativity",
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
                    "content": "${rural_s_telephone_directory} was "
                    "independently created by "
                    "${rural_telephone_service_company}, as "
                    "opposed to copied from other works",
                    "truth": True,
                },
                "terms": [
                    {
                        "generic": True,
                        "name": "Rural's telephone directory",
                        "plural": False,
                    },
                    {
                        "generic": True,
                        "name": "Rural Telephone Service Company",
                        "plural": False,
                    },
                ],
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
                    "content": "${feist_publications} freely copied the "
                    "facts contained in "
                    "${rural_s_telephone_directory}, in "
                    "preparing ${feist_s_telephone_directory}",
                    "truth": True,
                },
                "terms": [
                    {"generic": True, "name": "Feist Publications", "plural": False},
                    {
                        "generic": True,
                        "name": "Rural's telephone directory",
                        "plural": False,
                    },
                    {
                        "generic": True,
                        "name": "Feist's telephone directory",
                        "plural": False,
                    },
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "the facts contained in existing works may be "
                        "freely copied",
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
                    "content": "${feist_s_telephone_directory} did not "
                    "feature the same selection and arrangement "
                    "of facts as ${rural_s_telephone_directory}",
                    "truth": True,
                },
                "terms": [
                    {
                        "generic": True,
                        "name": "Feist's telephone directory",
                        "plural": False,
                    },
                    {
                        "generic": True,
                        "name": "Rural's telephone directory",
                        "plural": False,
                    },
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "the author make the selection or arrangement "
                        "independently (i. e., without copying that "
                        "selection or arrangement from another work)",
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
                    "content": "${rural_s_telephone_listings} were names, "
                    "towns, and telephone numbers of telephone "
                    "subscribers",
                    "truth": True,
                },
                "terms": [
                    {
                        "generic": True,
                        "name": "Rural's telephone listings",
                        "plural": True,
                    }
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "There is no doubt that Feist took from the "
                        "white pages of Rural’s directory a "
                        "substantial amount of factual information. "
                        "At a minimum, Feist copied the names, towns, "
                        "and telephone numbers of 1,309 of Rural’s "
                        "subscribers.",
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
                    "content": "${rural_s_telephone_directory} contained "
                    "written expression protectable by copyright",
                    "truth": False,
                },
                "terms": [
                    {
                        "generic": True,
                        "name": "Rural's telephone directory",
                        "plural": False,
                    }
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "a directory that contains absolutely no "
                        "protectible written expression",
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
                    "content": "${rural_s_telephone_directory} possessed at "
                    "least some minimal degree of creativity",
                    "truth": True,
                },
                "terms": [
                    {
                        "generic": True,
                        "name": "Rural's telephone directory",
                        "plural": False,
                    }
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "it possesses at least some minimal degree of "
                        "creativity",
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
                    "content": "${rural_telephone_service_company} was the "
                    "compiler of ${rural_s_telephone_directory}",
                    "truth": True,
                },
                "terms": [
                    {
                        "generic": True,
                        "name": "Rural Telephone Service Company",
                        "plural": False,
                    },
                    {
                        "generic": True,
                        "name": "Rural's telephone directory",
                        "plural": False,
                    },
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [{"exact": "by the compiler", "prefix": "", "suffix": ""}],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${feist_publications} infringed the "
                    "copyright on ${rural_s_telephone_directory}",
                    "truth": False,
                },
                "terms": [
                    {"generic": True, "name": "Feist Publications", "plural": False},
                    {
                        "generic": True,
                        "name": "Rural's telephone directory",
                        "plural": False,
                    },
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "may be freely copied because copyright "
                        "protects only the elements that owe their "
                        "origin to the compiler",
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
                    "content": "${rural_s_telephone_directory} closely "
                    "resembled other works",
                    "truth": True,
                },
                "terms": [
                    {
                        "generic": True,
                        "name": "Rural's telephone directory",
                        "plural": False,
                    }
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "it closely resembles other works",
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
                    "content": "${rural_s_telephone_directory} was a "
                    "compilation of facts",
                    "truth": True,
                },
                "terms": [
                    {
                        "generic": True,
                        "name": "Rural's telephone directory",
                        "plural": False,
                    }
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "compilations of facts",
                        "prefix": "",
                        "suffix": "generally are",
                    },
                    {
                        "exact": "Factual compilations",
                        "prefix": "",
                        "suffix": ", on the other hand",
                    },
                    {
                        "exact": "Even if a work qualifies as a copyrightable "
                        "compilation",
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
                    "content": "${rural_s_telephone_listings} were an original work",
                    "truth": False,
                },
                "terms": [
                    {
                        "generic": True,
                        "name": "Rural's telephone listings",
                        "plural": True,
                    }
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "In other words, did Feist, by taking 1,309 "
                        "names, towns, and telephone numbers from "
                        "Rural’s white pages, copy anything that was "
                        "“original” to Rural? Certainly, the raw data "
                        "does not satisfy the originality "
                        "requirement.",
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
                    "content": "${rural_s_telephone_directory} was a "
                    "telephone directory",
                    "truth": True,
                },
                "terms": [
                    {
                        "generic": True,
                        "name": "Rural's telephone directory",
                        "plural": False,
                    }
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "Rural publishes a typical telephone "
                        "directory, consisting of white pages and "
                        "yellow pages.",
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
                    "content": "${rural_s_telephone_directory} was an original work",
                    "truth": True,
                },
                "terms": [
                    {
                        "generic": True,
                        "name": "Rural's telephone directory",
                        "plural": False,
                    }
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "originality",
                        "prefix": "The sine qua non of copyright is",
                        "suffix": "",
                    },
                    {
                        "exact": "Original, as the term is used in copyright",
                        "prefix": "",
                        "suffix": "",
                    },
                    {
                        "exact": "No one may claim originality",
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
                    "content": "${rural_s_telephone_directory} was copyrightable",
                    "truth": True,
                },
                "terms": [
                    {
                        "generic": True,
                        "name": "Rural's telephone directory",
                        "plural": False,
                    }
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "are not copyrightable",
                        "prefix": "The first is that facts",
                        "suffix": "",
                    },
                    {"exact": "no one may copyright", "prefix": "", "suffix": "facts"},
                    {
                        "exact": "copyrightable",
                        "prefix": "first is that facts are not",
                        "suffix": "",
                    },
                    {
                        "exact": "copyright",
                        "prefix": "The sine qua non of",
                        "suffix": "",
                    },
                    {
                        "exact": "Even if a work qualifies as a copyrightable "
                        "compilation",
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
                    "content": "${rural_s_telephone_directory} was an idea",
                    "truth": True,
                },
                "terms": [
                    {
                        "generic": True,
                        "name": "Rural's telephone directory",
                        "plural": False,
                    }
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {
                        "exact": "ideas",
                        "prefix": "no one may copyright facts or",
                        "suffix": "",
                    }
                ],
            },
        },
        {
            "term": {
                "generic": False,
                "predicate": {
                    "content": "${rural_s_telephone_directory} was a fact",
                    "truth": True,
                },
                "terms": [
                    {
                        "generic": True,
                        "name": "Rural's telephone directory",
                        "plural": False,
                    }
                ],
                "name": "",
                "standard_of_proof": None,
            },
            "anchors": {
                "positions": [],
                "quotes": [
                    {"exact": "facts", "prefix": "The first is that", "suffix": ""},
                    {
                        "exact": "as to facts",
                        "prefix": "No one may claim originality",
                        "suffix": "",
                    },
                    {"exact": "facts", "prefix": "no one may copyright", "suffix": ""},
                ],
            },
        },
    ],
    "enactment_anchors": [],
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
