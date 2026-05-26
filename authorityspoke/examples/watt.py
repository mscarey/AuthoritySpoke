import copy
import datetime
from decimal import Decimal

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
                                    "content": "${hideaway_lodge} "
                                    "was "
                                    "${wattenburg}’s "
                                    "abode",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Hideaway Lodge",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Wattenburg",
                                        "plural": False,
                                    },
                                ],
                                "name": "Hideaway Lodge was Wattenburg’s abode",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${hideaway_lodge} was a motel",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Hideaway Lodge",
                                        "plural": False,
                                    }
                                ],
                                "name": "Hideaway Lodge was a motel",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${wattenburg} "
                                    "lived at "
                                    "${hideaway_lodge}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Wattenburg",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Hideaway Lodge",
                                        "plural": False,
                                    },
                                ],
                                "name": "Wattenburg lived at Hideaway Lodge",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${wattenburg} "
                                    "operated "
                                    "${hideaway_lodge} "
                                    "as a "
                                    "business",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Wattenburg",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Hideaway Lodge",
                                        "plural": False,
                                    },
                                ],
                                "name": "Wattenburg operated "
                                "Hideaway Lodge as a "
                                "business",
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
                                            "exact": "The "
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
                                            "violated",
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
                                    "content": "${the_stockpile_of_trees} "
                                    "was "
                                    "within "
                                    "the "
                                    "curtilage "
                                    "of "
                                    "${hideaway_lodge}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Hideaway Lodge",
                                        "plural": False,
                                    },
                                ],
                                "name": "the stockpile of trees was "
                                "within the curtilage of "
                                "Hideaway Lodge",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_stockpile_of_trees} "
                                    "was on the "
                                    "premises "
                                    "of "
                                    "${hideaway_lodge}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Hideaway Lodge",
                                        "plural": False,
                                    },
                                ],
                                "name": "the stockpile of trees was "
                                "on the premises of Hideaway "
                                "Lodge",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_stockpile_of_trees} "
                                    "was a "
                                    "stockpile "
                                    "of "
                                    "Christmas "
                                    "trees",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    }
                                ],
                                "name": "the stockpile of trees was "
                                "a stockpile of Christmas "
                                "trees",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_stockpile_of_trees} "
                                    "was among "
                                    "some "
                                    "standing "
                                    "trees",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    }
                                ],
                                "name": "the stockpile of trees was "
                                "among some standing trees",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "the "
                                    "distance "
                                    "between "
                                    "$place1 "
                                    "and "
                                    "$place2 "
                                    "was",
                                    "truth": True,
                                    "quantity_range": {
                                        "sign": "<=",
                                        "include_negatives": None,
                                        "quantity_magnitude": Decimal("35"),
                                        "quantity_units": "foot",
                                    },
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Hideaway Lodge",
                                        "plural": False,
                                    },
                                ],
                                "name": "long distance",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "the "
                                    "distance "
                                    "between "
                                    "${the_stockpile_of_trees} "
                                    "and a "
                                    "parking "
                                    "area used "
                                    "by "
                                    "personnel "
                                    "and "
                                    "patrons of "
                                    "${hideaway_lodge} "
                                    "was",
                                    "truth": True,
                                    "quantity_range": {
                                        "sign": "<=",
                                        "include_negatives": None,
                                        "quantity_magnitude": Decimal("5"),
                                        "quantity_units": "foot",
                                    },
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Hideaway Lodge",
                                        "plural": False,
                                    },
                                ],
                                "name": "the distance between the "
                                "stockpile of trees and a "
                                "parking area used by "
                                "personnel and patrons of "
                                "Hideaway Lodge was <= 5 "
                                "feet",
                                "standard_of_proof": None,
                            },
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "the "
                                    "distance "
                                    "between "
                                    "$place1 "
                                    "and "
                                    "$place2 "
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
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Hideaway Lodge",
                                        "plural": False,
                                    },
                                ],
                                "name": "the distance between the "
                                "stockpile of trees and "
                                "Hideaway Lodge was >= 20 "
                                "feet",
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
                                            "exact": "The "
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
                                            "violated",
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
                                    "content": "${officers_search_of_the_stockpile} "
                                    "constituted "
                                    "an "
                                    "intrusion "
                                    "upon "
                                    "${the_stockpile_of_trees}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the stockpile",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    },
                                ],
                                "name": "officers' search of the "
                                "stockpile constituted an "
                                "intrusion upon the "
                                "stockpile of trees",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${hideaway_lodge} was a motel",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Hideaway Lodge",
                                        "plural": False,
                                    }
                                ],
                                "name": "Hideaway Lodge was a motel",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_stockpile_of_trees} "
                                    "was on the "
                                    "premises "
                                    "of "
                                    "${hideaway_lodge}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Hideaway Lodge",
                                        "plural": False,
                                    },
                                ],
                                "name": "the stockpile of trees was "
                                "on the premises of Hideaway "
                                "Lodge",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_stockpile_of_trees} "
                                    "was a "
                                    "stockpile "
                                    "of "
                                    "Christmas "
                                    "trees",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    }
                                ],
                                "name": "the stockpile of trees was "
                                "a stockpile of Christmas "
                                "trees",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_stockpile} "
                                    "was a "
                                    "warrantless "
                                    "search and "
                                    "seizure",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the stockpile",
                                        "plural": False,
                                    }
                                ],
                                "name": "officers' search of the "
                                "stockpile was a warrantless "
                                "search and seizure",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_stockpile} "
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
                                        "name": "officers' search of the stockpile",
                                        "plural": False,
                                    }
                                ],
                                "name": "officers' search of the "
                                "stockpile was performed by "
                                "law enforcement officers",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_stockpile} "
                                    "was "
                                    "performed "
                                    "by federal "
                                    "officers",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the stockpile",
                                        "plural": False,
                                    }
                                ],
                                "name": "officers' search of the "
                                "stockpile was performed by "
                                "federal officers",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "in "
                                    "${officers_search_of_the_stockpile}, "
                                    "several "
                                    "law "
                                    "enforcement "
                                    "officials "
                                    "meticulously "
                                    "went "
                                    "through "
                                    "${the_stockpile_of_trees}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the stockpile",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    },
                                ],
                                "name": "in officers' search of the "
                                "stockpile, several law "
                                "enforcement officials "
                                "meticulously went through "
                                "the stockpile of trees",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "the time "
                                    "duration "
                                    "of "
                                    "${officers_search_of_the_stockpile} "
                                    "was",
                                    "truth": True,
                                    "quantity_range": {
                                        "sign": ">=",
                                        "include_negatives": None,
                                        "quantity_magnitude": Decimal("385"),
                                        "quantity_units": "minute",
                                    },
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the stockpile",
                                        "plural": False,
                                    }
                                ],
                                "name": "the time duration of "
                                "officers' search of the "
                                "stockpile was >= 385 "
                                "minutes",
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
                                            "exact": "The "
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
                                            "violated",
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
                                    "content": "${wattenburg} "
                                    "sought to "
                                    "preserve "
                                    "${the_stockpile_of_trees} "
                                    "as "
                                    "private",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Wattenburg",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    },
                                ],
                                "name": "Wattenburg sought to "
                                "preserve the stockpile of "
                                "trees as private",
                                "standard_of_proof": None,
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${hideaway_lodge} "
                                    "was "
                                    "${wattenburg}'s "
                                    "abode",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Hideaway Lodge",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Wattenburg",
                                        "plural": False,
                                    },
                                ],
                                "name": "Hideaway Lodge was Wattenburg's abode",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_stockpile_of_trees} "
                                    "was on the "
                                    "premises "
                                    "of "
                                    "${hideaway_lodge}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Hideaway Lodge",
                                        "plural": False,
                                    },
                                ],
                                "name": "the stockpile of trees was "
                                "on the premises of Hideaway "
                                "Lodge",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_stockpile_of_trees} "
                                    "was a "
                                    "stockpile "
                                    "of "
                                    "Christmas "
                                    "trees",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    }
                                ],
                                "name": "the stockpile of trees was "
                                "a stockpile of Christmas "
                                "trees",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_stockpile_of_trees} "
                                    "was among "
                                    "some "
                                    "standing "
                                    "trees",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    }
                                ],
                                "name": "the stockpile of trees was "
                                "among some standing trees",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "the "
                                    "distance "
                                    "between "
                                    "$place1 "
                                    "and "
                                    "$place2 "
                                    "was",
                                    "truth": True,
                                    "quantity_range": {
                                        "sign": "<=",
                                        "include_negatives": None,
                                        "quantity_magnitude": Decimal("35"),
                                        "quantity_units": "foot",
                                    },
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Hideaway Lodge",
                                        "plural": False,
                                    },
                                ],
                                "name": "long distance",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "the "
                                    "distance "
                                    "between "
                                    "${the_stockpile_of_trees} "
                                    "and a "
                                    "parking "
                                    "area used "
                                    "by "
                                    "personnel "
                                    "and "
                                    "patrons of "
                                    "${hideaway_lodge} "
                                    "was",
                                    "truth": True,
                                    "quantity_range": {
                                        "sign": "<=",
                                        "include_negatives": None,
                                        "quantity_magnitude": Decimal("5"),
                                        "quantity_units": "foot",
                                    },
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Hideaway Lodge",
                                        "plural": False,
                                    },
                                ],
                                "name": "the distance between the "
                                "stockpile of trees and a "
                                "parking area used by "
                                "personnel and patrons of "
                                "Hideaway Lodge was <= 5 "
                                "feet",
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
                                            "exact": "The "
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
                                            "violated",
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
                                        "generic": True,
                                        "offered_by": {
                                            "generic": True,
                                            "name": "prosecutor",
                                            "plural": False,
                                        },
                                        "form": None,
                                        "statement": None,
                                        "statement_attribution": None,
                                        "name": "proof of Wattenburg's guilt",
                                    },
                                    "to_effect": {
                                        "generic": False,
                                        "predicate": {
                                            "content": "${wattenburg} "
                                            "committed "
                                            "a "
                                            "crime",
                                            "truth": True,
                                        },
                                        "terms": [
                                            {
                                                "generic": True,
                                                "name": "Wattenburg",
                                                "plural": False,
                                            }
                                        ],
                                        "name": "Wattenburg committed a crime",
                                        "standard_of_proof": None,
                                    },
                                    "name": "evidence of "
                                    "proof of "
                                    "Wattenburg's "
                                    "guilt to the "
                                    "effect that "
                                    "Wattenburg "
                                    "committed a "
                                    "crime",
                                },
                            }
                        ],
                        "inputs": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${hideaway_lodge} "
                                    "was "
                                    "${wattenburg}’s "
                                    "abode",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Hideaway Lodge",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Wattenburg",
                                        "plural": False,
                                    },
                                ],
                                "name": "Hideaway Lodge was Wattenburg’s abode",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_stockpile} "
                                    "was a "
                                    "warrantless "
                                    "search and "
                                    "seizure",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the stockpile",
                                        "plural": False,
                                    }
                                ],
                                "name": "officers' search of the "
                                "stockpile was a warrantless "
                                "search and seizure",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_stockpile} "
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
                                        "name": "officers' search of the stockpile",
                                        "plural": False,
                                    }
                                ],
                                "name": "officers' search of the "
                                "stockpile was performed by "
                                "law enforcement officers",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_stockpile} "
                                    "was "
                                    "performed "
                                    "by federal "
                                    "officers",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the stockpile",
                                        "plural": False,
                                    }
                                ],
                                "name": "officers' search of the "
                                "stockpile was performed by "
                                "federal officers",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${officers_search_of_the_stockpile} "
                                    "constituted "
                                    "an "
                                    "intrusion "
                                    "upon "
                                    "${the_stockpile_of_trees}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "officers' search of the stockpile",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    },
                                ],
                                "name": "officers' search of the "
                                "stockpile constituted an "
                                "intrusion upon the "
                                "stockpile of trees",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_stockpile_of_trees} "
                                    "was on the "
                                    "premises "
                                    "of "
                                    "${hideaway_lodge}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Hideaway Lodge",
                                        "plural": False,
                                    },
                                ],
                                "name": "the stockpile of trees was "
                                "on the premises of Hideaway "
                                "Lodge",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${wattenburg} "
                                    "sought to "
                                    "preserve "
                                    "${the_stockpile_of_trees} "
                                    "as private",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "Wattenburg",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    },
                                ],
                                "name": "Wattenburg sought to "
                                "preserve the stockpile of "
                                "trees as private",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "the "
                                    "distance "
                                    "between "
                                    "$place1 "
                                    "and "
                                    "$place2 "
                                    "was",
                                    "truth": True,
                                    "quantity_range": {
                                        "sign": "<=",
                                        "include_negatives": None,
                                        "quantity_magnitude": Decimal("35"),
                                        "quantity_units": "foot",
                                    },
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Hideaway Lodge",
                                        "plural": False,
                                    },
                                ],
                                "name": "long distance",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${proof_of_wattenburg_s_guilt} "
                                    "was "
                                    "derived "
                                    "from "
                                    "${officers_search_of_the_stockpile}",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "offered_by": {
                                            "generic": True,
                                            "name": "prosecutor",
                                            "plural": False,
                                        },
                                        "form": None,
                                        "statement": None,
                                        "statement_attribution": None,
                                        "name": "proof of Wattenburg's guilt",
                                    },
                                    {
                                        "generic": True,
                                        "name": "officers' search of the stockpile",
                                        "plural": False,
                                    },
                                ],
                                "name": "proof of Wattenburg's guilt "
                                "was derived from officers' "
                                "search of the stockpile",
                                "standard_of_proof": None,
                            },
                        ],
                        "despite": [
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "${the_stockpile_of_trees} "
                                    "was in an "
                                    "area "
                                    "accessible "
                                    "to the "
                                    "public",
                                    "truth": True,
                                },
                                "terms": [
                                    {
                                        "generic": True,
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    }
                                ],
                                "name": "the stockpile of trees was "
                                "in an area accessible to "
                                "the public",
                                "standard_of_proof": None,
                            },
                            {
                                "generic": False,
                                "predicate": {
                                    "content": "the "
                                    "distance "
                                    "between "
                                    "the "
                                    "$place1 "
                                    "and "
                                    "$place2 "
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
                                        "name": "the stockpile of trees",
                                        "plural": False,
                                    },
                                    {
                                        "generic": True,
                                        "name": "Hideaway Lodge",
                                        "plural": False,
                                    },
                                ],
                                "name": "the distance between the "
                                "the stockpile of trees and "
                                "Hideaway Lodge was >= 20 "
                                "feet",
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
                                            "exact": "The "
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
                                            "violated",
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
            "anchors": {"positions": [], "quotes": []},
        },
    ],
    "named_anchors": [],
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
