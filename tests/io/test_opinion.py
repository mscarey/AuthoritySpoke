from typing import Dict, List

from authorityspoke.io import anchors, loaders, readers, schemas


class TestLoadOpinion:
    def test_load_opinion_in_CAP_format(self):
        watt_dict = loaders.load_decision("watt_h.json")
        assert watt_dict["name_abbreviation"] == "Wattenburg v. United States"

    def test_load_opinion(self):
        schema = schemas.OpinionSchema(many=False)
        brad_dict = loaders.load_decision("brad_h.json")
        dissent = brad_dict["casebody"]["data"]["opinions"][1]
        opinion = schema.load(dissent)
        assert opinion.position == "concurring-in-part-and-dissenting-in-part"

    def test_selectors_not_duplicated(self, make_opinion, raw_holding):
        """
        Test that the factors attribute for this Opinion contains
        one instance of the Fact "Mark stole a watch", but that both
        of the different text anchors for that Fact are attached to it.
        """
        watch = raw_holding["stolen watch"]
        holdings, mentioned, holding_anchors = readers.read_holdings_with_index([watch])
        named_anchors = anchors.get_named_anchors(mentioned)
        cardenas = make_opinion["cardenas_majority"]
        cardenas.posit_holdings(holdings, named_anchors=named_anchors)
        output = holdings[0].outputs[0]
        output_factor = cardenas.factors_by_str()[str(output)]

        assert any(
            selector.exact == "Mark stole a watch" for selector in output_factor.anchors
        )
        assert any(
            selector.exact == "a watch was stolen by Mark"
            for selector in output_factor.anchors
        )
        assert len(output_factor.anchors) == 2


class TestLoadDecision:
    def test_load_decision(self):
        brad_dict = loaders.load_decision("brad_h.json")
        brad = readers.read_decision(brad_dict)
        dissent = brad.opinions[1]
        assert dissent.position == "concurring-in-part-and-dissenting-in-part"
