import os

from dotenv import load_dotenv
from legislice.download import Client
from legislice.schemas import EnactmentSchema
import pytest

from authorityspoke.io import anchors, name_index, readers, schemas
from authorityspoke.io.loaders import load_holdings
from authorityspoke.io.readers import read_holding


load_dotenv()

TOKEN = os.getenv("LEGISLICE_API_TOKEN")


class TestEnactmentImport:
    client = Client(api_token=TOKEN)
    test_enactment = {
        "heading": "",
        "content": "Except as otherwise provided by statute, all relevant evidence is admissible.",
        "name": "s351",
        "node": "/us-ca/code/evid/s351",
        "start_date": "1966-01-01",
    }

    def test_enactment_from_dict(self, fake_usc_client):
        enactment = fake_usc_client.read_from_json(self.test_enactment)
        assert "all relevant evidence is admissible" in enactment.text

    def test_enactment_with_anchor(self, fake_usc_client, make_response):
        fourteenth_dp = make_response["/us/const/amendment/XIV"]["1868-07-28"][
            "children"
        ][0]
        fourteenth_dp["exact"] = "nor shall any State deprive any person"
        enactment = fake_usc_client.read_from_json(fourteenth_dp)

        assert enactment.selected_text().startswith("…nor shall any State")

    def test_enactment_import_from_dict(self, fake_usc_client):
        holding_brad = load_holdings("holding_brad.json")
        holdings = readers.read_holdings(holding_brad, client=fake_usc_client)
        enactments = holdings[0].enactments
        assert enactments[0].selected_text().endswith("shall not be violated…")

    def test_false_as_selection(self, fake_usc_client):
        input_enactment = self.test_enactment.copy()
        input_enactment["selection"] = False

        enactment = fake_usc_client.read_from_json(input_enactment)
        assert enactment.selected_text() == ""

    def test_true_as_selection(self, fake_usc_client):
        input_enactment = self.test_enactment.copy()
        input_enactment["selection"] = True

        enactment = fake_usc_client.read_from_json(input_enactment)
        assert enactment.selected_text() == enactment.text

    def test_make_name_for_enactment(self, fake_usc_client):
        data = {
            "inputs": {
                "type": "fact",
                "content": "{the Java API} was an original work",
                "truth": False,
                "anchors": "a work must be “original”",
            },
            "outputs": {
                "type": "fact",
                "content": "the Java API was copyrightable",
                "truth": False,
                "anchors": "must be “original” to qualify for |copyright protection.|",
            },
            "mandatory": True,
            "enactments": {
                "node": "/us/usc/t17/s102/a",
                "exact": "in accordance with this title,",
                "anchors": "qualify for copyright protection. |17 U.S.C. § 102(a)|.",
            },
            "anchors": "By statute, a work |must be “original” to qualify| for",
        }
        holding = read_holding(data, client=fake_usc_client)
        enactment = holding.enactments[0]
        assert enactment.name == ""

    def test_enactment_import_from_holding(self):
        holding_cardenas = load_holdings("holding_cardenas.json")
        holdings = readers.read_holdings(holding_cardenas)
        enactment_list = holdings[0].enactments
        assert "all relevant evidence is admissible" in enactment_list[0].text

    def test_enactment_does_not_fail_for_excess_selector(self, fake_beard_client):
        """Test selector that extends into the text of a subnode."""
        exact = (
            "In this Act, beard means any facial hair no shorter "
            "than 5 millimetres in length that: occurs on or below the chin"
        )
        record = {"node": "/test/acts/47/4", "exact": exact}
        client = fake_beard_client
        enactment = client.read_from_json(record)
        assert enactment.selected_text() == exact + "…"
