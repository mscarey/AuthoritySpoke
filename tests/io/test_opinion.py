import os
from typing import Dict, List

from dotenv import load_dotenv

from authorityspoke import Opinion
from authorityspoke.holdings import HoldingGroup
from authorityspoke.io import loaders, readers
from authorityspoke.io.downloads import CAPClient
from authorityspoke.decisions import DecisionReading
from authorityspoke.opinions import OpinionReading


load_dotenv()

CAP_API_KEY = os.getenv("CAP_API_KEY") or "wrong key"


class TestLoadDecision:
    case_client = CAPClient(api_token="Token " + CAP_API_KEY)

    def test_load_decision(self):
        brad_dict = loaders.load_decision("brad_h.json")
        brad = readers.read_decision(brad_dict)
        dissent = brad.opinions[1]
        assert dissent.type == "concurring-in-part-and-dissenting-in-part"


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
        reading = OpinionReading(opinion_type="majority")
        assert isinstance(reading.holdings, HoldingGroup)

    def test_loading_opinion_with_one_holding_in_list(self, make_anchored_holding):
        holding = make_anchored_holding["watt"].holdings[0]
        reading = OpinionReading(anchored_holdings=[holding])
        assert isinstance(reading.holdings, HoldingGroup)
        assert len(reading.holdings) == 1

    def test_selectors_not_duplicated(self, make_decision, raw_holding):
        """
        Test that the factors attribute for this Opinion contains
        one instance of the Fact "Mark stole a watch", but that both
        of the different text anchors for that Fact are attached to it.
        """
        watch = raw_holding["stolen watch"]
        holdings, _, _ = readers.read_holdings_with_anchors([watch])
        cardenas = OpinionReading(anchored_holdings=holdings)

        assert any(
            selector.exact == "Mark stole the watch"
            for selector in cardenas.anchored_holdings[0].anchors.quotes
        )
        assert any(
            selector.exact == "a watch was stolen by Mark"
            for selector in cardenas.anchored_holdings[0].anchors.quotes
        )
        assert len(cardenas.anchored_holdings[0].anchors.quotes) == 2
