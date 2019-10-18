from authorityspoke.io import anchors, name_index
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
