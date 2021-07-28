from authorityspoke.holdings import HoldingGroup
from typing import Dict, List

from authorityspoke import Opinion
from authorityspoke.io import loaders, readers, schemas_json as schemas
from authorityspoke.opinions import OpinionReading


class TestLoadOpinion:
    def test_load_opinion_in_CAP_format(self):
        watt_dict = loaders.load_decision("watt_h.json")
        assert watt_dict["name_abbreviation"] == "Wattenburg v. United States"

    def test_load_opinion(self):
        brad_dict = loaders.load_decision("brad_h.json")
        dissent = brad_dict["casebody"]["data"]["opinions"][1]
        opinion = Opinion(**dissent)
        assert opinion.type == "concurring-in-part-and-dissenting-in-part"

    def test_empty_holding_list_when_loading_opinion(self):
        opinion = Opinion(type="majority")
        reading = OpinionReading(opinion=opinion, holdings=[])
        assert isinstance(reading.holdings, HoldingGroup)

    def test_loading_opinion_with_one_holding_in_list(self, make_holding):
        opinion = Opinion(type="majority")
        reading = OpinionReading(opinion=opinion, holdings=[make_holding["h1"]])
        assert isinstance(reading.holdings, HoldingGroup)
        assert len(reading.holdings) == 1

    def test_selectors_not_duplicated(self, make_opinion_with_holding, raw_holding):
        """
        Test that the factors attribute for this Opinion contains
        one instance of the Fact "Mark stole a watch", but that both
        of the different text anchors for that Fact are attached to it.
        """
        watch = raw_holding["stolen watch"]
        holdings = readers.read_holdings([watch])
        cardenas = make_opinion_with_holding["cardenas_majority"]
        cardenas.clear_holdings()
        cardenas.posit_holdings(holdings)

        assert any(
            selector.exact == "Mark stole a watch" for selector in holdings[0].anchors
        )
        assert any(
            selector.exact == "a watch was stolen by Mark"
            for selector in holdings[0].anchors
        )
        assert len(holdings[0].anchors) == 2


class TestLoadDecision:
    def test_load_decision(self):
        brad_dict = loaders.load_decision("brad_h.json")
        brad = readers.read_decision(brad_dict)
        dissent = brad.opinions[1]
        assert dissent.type == "concurring-in-part-and-dissenting-in-part"
