import datetime
import os

from dotenv import load_dotenv
from legislice.download import Client
from legislice.enactments import EnactmentPassage
import pytest

from authorityspoke.io import name_index, readers
from authorityspoke.io.loaders import load_holdings


load_dotenv()

TOKEN = os.getenv("LEGISLICE_API_TOKEN")


class TestEnactmentImport:
    client = Client(api_token=TOKEN)
    test_enactment = {
        "heading": "",
        "text_version": "Except as otherwise provided by statute, all relevant evidence is admissible.",
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
        enactment = fake_usc_client.read_from_json(fourteenth_dp)
        passage = enactment.select("nor shall any State deprive any person")

        assert passage.selected_text().startswith("…nor shall any State")

    @pytest.mark.vcr
    def test_enactment_import_from_yaml(self):
        holding_brad = load_holdings("holding_brad.yaml")
        holdings = readers.read_holdings(holding_brad, client=self.client)
        enactments = holdings[0].enactments
        assert any(
            law.selected_text().endswith("shall not be violated…") for law in enactments
        )

    def test_enactment_import_from_holding(self):
        holding_cardenas = load_holdings("holding_cardenas.yaml")
        holdings = readers.read_holdings(holding_cardenas)
        enactment_list = holdings[0].enactments
        assert any(
            "all relevant evidence is admissible" in enactment.text
            for enactment in enactment_list
        )

    @pytest.mark.vcr
    def test_enactment_does_not_fail_for_excess_selector(self, fake_beard_client):
        """
        Test selector that extends into the text of a subnode.

        Demonstrates that the API has downloaded the entire text of the provision
        and included it in the Enactment object.
        """
        exact = (
            "In this Act, beard means any facial hair no shorter "
            "than 5 millimetres in length that: occurs on or below the chin"
        )
        record = {
            "enactment": {"node": "/test/acts/47/4"},
            "selection": {"quotes": {"exact": exact}},
        }
        client = self.client
        passage = client.read_passage_from_json(record)
        assert passage.selected_text() == exact + "…"
        assert "in an uninterrupted line" in passage.enactment.children[1].content
