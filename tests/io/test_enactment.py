from authorityspoke.io import anchors, readers
from authorityspoke.io.loaders import load_holdings


class TestEnactmentImport:
    test_enactments = [
        {"source": "/us-ca/evid/s351"},
        {
            "source": "/us/const/amendment-XIV-1",
            "prefix": "immunities of citizens of the United States; ",
            "suffix": " nor deny to any person",
            "name": "due process clause",
            "anchors": [{"exact": "reference to the Due Process Clause"}],
        },
    ]

    def test_enactment_from_dict(self, make_regime):
        enactment = readers.read_enactment(self.test_enactments[0], regime=make_regime)
        assert "all relevant evidence is admissible" in enactment.text

    def test_enactment_with_anchor(self, make_regime):
        enactment = readers.read_enactment(self.test_enactments[1], regime=make_regime)
        factor_anchors = anchors.get_named_anchors(self.test_enactments[1])
        assert enactment.text.startswith(
            "nor shall any State deprive any person of life, liberty, or property"
        )
        assert (
            factor_anchors[enactment.name][0].exact
            == "reference to the Due Process Clause"
        )

    def test_enactment_import_from_holding(self, make_regime):
        holding_cardenas = load_holdings("holding_cardenas.json")
        holdings = readers.read_holdings(holding_cardenas, regime=make_regime)
        enactment_list = holdings[0].enactments
        assert "all relevant evidence is admissible" in enactment_list[0].text
