import os

import pytest

from authorityspoke import LegisClient
from authorityspoke.io import filepaths, loaders, readers
from authorityspoke.io.fake_enactments import FakeClient
from authorityspoke.io.loaders import (
    read_holdings_from_file,
    read_anchored_holdings_from_file,
)

LEGISLICE_API_TOKEN = os.getenv("LEGISLICE_API_TOKEN")


class TestHoldingLoad:
    def test_get_json_filepath(self):
        directory = filepaths.get_directory_path("holdings")
        path = filepaths.make_filepath(
            filename="holding_feist.json", directory=directory
        )
        raw_holdings = loaders.load_holdings(filepath=path)
        assert raw_holdings[0]["outputs"]["type"] == "fact"

    def test_get_yaml_filepath(self):
        directory = filepaths.get_directory_path("holdings")
        path = filepaths.make_filepath(
            filename="holding_feist.yaml", directory=directory
        )
        raw_holdings = loaders.load_holdings(filepath=path)
        assert raw_holdings[0]["outputs"]["type"] == "fact"


class TestLoadAndReadFake:
    def test_read_holdings_from_file(self):
        legis_client = FakeClient.from_file("usc.json")
        oracle_holdings = read_holdings_from_file(
            "holding_oracle.json", client=legis_client
        )
        assert oracle_holdings[0]


class TestLoadAndRead:
    client = LegisClient(api_token=LEGISLICE_API_TOKEN)

    @pytest.mark.vcr
    def test_read_holdings_from_yaml(self):
        anchored = read_anchored_holdings_from_file(
            "holding_mazza_alaluf.yaml", client=self.client
        )
        # factor anchor
        assert (
            "Turismo conducted substantial money transmitting business"
            in anchored.named_anchors[
                "the fact that <Turismo Costa Brava> was a money transmitting business"
            ][0].exact
        )

        # holding anchor
        assert "In any event" in anchored.holding_anchors[0][0].suffix

        # enactment anchor
        assert (
            "domestic financial"
            in anchored.enactment_anchors["domestic institution statute"][0].exact
        )
