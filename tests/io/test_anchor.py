from authorityspoke.io import anchors, name_index
from authorityspoke.io.name_index import index_names
from authorityspoke.io.text_expansion import expand_shorthand


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
            "source": "/us/usc/t17/s102/a",
            "exact": "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.",
            "name": "copyright protection provision",
            "anchors": "qualify for copyright protection. |17 U.S.C. § 102(a)|.",
        },
    }

    def test_anchor_not_wrapped_in_list(self):
        obj = expand_shorthand(self.fact_string_anchor)
        assert obj["anchors"][0].startswith("In preparing")

    def test_anchors_from_fact_with_inferred_name(self):
        record = expand_shorthand(self.fact)
        factor_anchors = anchors.get_named_anchors(record)
        fact_anchors = factor_anchors[
            "false Rural's telephone directory was copyrightable"
        ]
        assert fact_anchors[1].exact == "no one may copyright"

    def test_make_enactment_anchor(self):
        record, mentioned = index_names(self.enactment_anchor)
        named_anchors = anchors.get_named_anchors(mentioned)
        enactment_anchors = named_anchors["copyright protection provision"]
        assert enactment_anchors[0].exact == "17 U.S.C. § 102(a)"
