from authorityspoke.io.readers import collect_anchors


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

    def test_anchors_from_fact(self):
        anchors = collect_anchors(self.fact)
        fact = list(anchors.keys())[0]
        assert any(
            selector.exact == "are not copyrightable" for selector in anchors[fact]
        )
