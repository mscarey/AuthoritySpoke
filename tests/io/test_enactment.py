import os

from dotenv import load_dotenv
import pytest

from authorityspoke.io import anchors, name_index, readers, schemas
from authorityspoke.io.loaders import load_holdings


from legislice.download import Client


load_dotenv()

TOKEN = os.getenv("LEGISLICE_API_TOKEN")


class TestEnactmentImport:
    client = Client(api_token=TOKEN)
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

    @pytest.mark.vcr
    def test_enactment_with_anchor(self, fourteenth_dp):
        fourteenth_dp["exact"] = "nor shall any State deprive any person"
        enactment = readers.read_enactment(fourteenth_dp, client=self.client)

        assert enactment.selected_text().startswith("...nor shall any State")

    @pytest.mark.vcr
    def test_enactment_import_from_dict(self):
        holding_brad = load_holdings("holding_brad.json")
        enactments = readers.read_enactments(
            holding_brad[0]["enactments"], client=self.client
        )
        assert enactments[0].selected_text().endswith("shall not be violated...")

    def test_false_as_selection(self):
        input_enactment = self.test_enactment.copy()
        input_enactment["selection"] = False

        enactment = readers.read_enactment(input_enactment)
        assert enactment.selected_text() == ""

    def test_true_as_selection(self):
        input_enactment = self.test_enactment.copy()
        input_enactment["selection"] = True

        enactment = readers.read_enactment(input_enactment)
        assert enactment.selected_text() == enactment.text

    def test_enactment_import_from_holding(self):
        holding_cardenas = load_holdings("holding_cardenas.json")
        holdings = readers.read_holdings(holding_cardenas)
        enactment_list = holdings[0].enactments
        assert "all relevant evidence is admissible" in enactment_list[0].text
