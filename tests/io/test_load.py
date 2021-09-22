import os

from marshmallow import ValidationError
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
    client = LegisClient(api_token=LEGISLICE_API_TOKEN)

    def test_get_json_filepath(self):
        directory = filepaths.get_directory_path("holdings")
        path = filepaths.make_filepath(
            filename="holding_feist.yaml", directory=directory
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

    @pytest.mark.vcr
    def test_load_and_read_yaml(self):
        both_holdings_with_anchors = read_anchored_holdings_from_file(
            filename="holding_mazza_alaluf.yaml", client=self.client
        )
        assert len(both_holdings_with_anchors.holdings) == 2

    def test_load_from_fake_client(self):
        fake_client = FakeClient.from_file("usc.json")
        filepath = filepaths.make_filepath(filename="holding_mazza_alaluf.yaml")
        result = read_anchored_holdings_from_file(filepath=filepath, client=fake_client)
        selector = result.named_anchors[
            "the fact it was false that <Turismo Costa Brava> was a domestic financial institution"
        ][0]
        assert (
            selector.exact
            == 'without respect to whether or not Turismo was a "domestic financial institution"'
        )
        assert len(result.holdings) == 2


class TestLoadAndReadFake:
    client = FakeClient.from_file("usc.json")

    @pytest.mark.vcr
    def test_read_holdings_from_file(self):
        oracle_holdings = read_holdings_from_file(
            "holding_oracle.yaml", client=self.client
        )
        assert oracle_holdings[0]

    def test_read_holdings_in_nested_rule(self):
        watt_holdings = read_holdings_from_file("holding_watt.yaml", client=self.client)
        assert watt_holdings[4].inputs[0].terms[0].name == "Hideaway Lodge"

    def test_read_holdings_in_nested_rule(self):
        watt_holdings = read_holdings_from_file("holding_watt.yaml", client=self.client)
        assert watt_holdings[4].inputs[0].terms[0].name == "Hideaway Lodge"


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
        assert "In any event" in anchored.holding_anchors[1][0].suffix

        # enactment anchor
        key = str(anchored.holdings[1].enactments_despite[0])
        assert "domestic financial" in anchored.enactment_anchors[key][0].exact
