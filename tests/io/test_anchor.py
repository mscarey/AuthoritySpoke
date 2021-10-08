import pytest


class TestCollectAnchors:
    fact = {
        "type": "fact",
        "content": "Rural's telephone directory was copyrightable",
        "truth": False,
        "anchors": [
            {"exact": "are not copyrightable", "prefix": "The first is that facts"},
            {"exact": "no one may copyright", "suffix": "facts"},
        ],
    }

    fact_string_anchor = {
        "type": "fact",
        "content": (
            "{Rural's arragement of its telephone listings} "
            "was the method of listing subscribers alphabetically "
            "by surname in Rural's telephone directory"
        ),
        "anchors": (
            "In preparing its white pages, Rural simply takes "
            "the data provided by its subscribers "
            "and lists it alphabetically by surname."
        ),
    }
    enactment_anchor = {
        "outputs": {
            "type": "fact",
            "content": "the Java API was copyrightable",
            "truth": False,
            "anchors": "must be “original” to qualify for |copyright protection.|",
        },
        "mandatory": True,
        "enactments": {
            "node": "/us/usc/t17/s102/a",
            "exact": "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.",
            "name": "copyright protection provision",
            "anchors": "qualify for copyright protection. |17 U.S.C. § 102(a)|.",
        },
    }
