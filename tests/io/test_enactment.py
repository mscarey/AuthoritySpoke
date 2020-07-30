from authorityspoke.io import anchors, name_index, readers, schemas
from authorityspoke.io.loaders import load_holdings


class TestEnactmentImport:
    test_enactment = {
        "heading": "",
        "content": "Except as otherwise provided by statute, all relevant evidence is admissible.",
        "name": "s351",
        "node": "/us-ca/evid/s351",
        "start_date": "1966-01-01",
    }

    def test_enactment_from_dict(self):
        enactment = readers.read_enactment(self.test_enactment)
        assert "all relevant evidence is admissible" in enactment.text

    def test_enactment_with_anchor(self, fourteenth_dp):
        record, mentioned = name_index.index_names(fourteenth_dp)
        schema = schemas.EnactmentSchema(many=False)
        schema.context["mentioned"] = mentioned
        enactment = schema.load(record)

        factor_anchors = anchors.get_named_anchors(mentioned)
        assert enactment.text.startswith(
            "nor shall any State deprive any person of life, liberty, or property"
        )
        assert (
            factor_anchors[enactment.name][0].exact
            == "reference to the Due Process Clause"
        )

    def test_enactment_import_from_dict(self):
        holding_brad = load_holdings("holding_brad.json")
        enactments = readers.read_enactments(holding_brad[0]["enactments"])
        assert enactments[0].text.endswith("shall not be violated")

    def test_enactment_import_from_holding(self):
        holding_cardenas = load_holdings("holding_cardenas.json")
        holdings = readers.read_holdings(holding_cardenas)
        enactment_list = holdings[0].enactments
        assert "all relevant evidence is admissible" in enactment_list[0].text
