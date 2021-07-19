import datetime
import os

import pytest

from anchorpoint.textselectors import TextPositionSelector, TextSelectionError
from dotenv import load_dotenv

from legislice.citations import CodeLevel
from legislice.download import Client, LegislicePathError
from legislice.yaml_schemas import ExpandableEnactmentSchema

from authorityspoke.io import loaders
from authorityspoke.io.fake_enactments import FakeClient

load_dotenv()

TOKEN = os.getenv("LEGISLICE_API_TOKEN")


class TestCodes:
    client = Client(api_token=TOKEN)

    def test_cfr_repr(self):
        oracle_dictionary = loaders.load_holdings("holding_oracle.json")
        regulation = oracle_dictionary[10]["enactments_despite"][1]
        schema = ExpandableEnactmentSchema()
        enactment = schema.load(regulation)

        assert enactment.level == CodeLevel.REGULATION
        assert "/cfr/" in repr(enactment)

    @pytest.mark.vcr
    @pytest.mark.default_cassette("test_us_code_title.yaml")
    def test_us_code_title(self):
        enactment = self.client.read("/us/usc")
        assert enactment.heading.startswith("United States Code")
        assert enactment.level == CodeLevel.STATUTE

    @pytest.mark.vcr
    @pytest.mark.default_cassette("test_const_code_title.yaml")
    def test_const_code_title(self):
        enactment = self.client.read("/us/const")
        assert enactment.heading.startswith("United States Constitution")
        assert enactment.level == CodeLevel.CONSTITUTION

    @pytest.mark.vcr
    @pytest.mark.default_cassette("test_acts_code_title.yaml")
    def test_acts_code_title(self):
        enactment = self.client.read("/test/acts")
        assert enactment.heading.startswith("Acts of Australia")
        assert enactment.level == CodeLevel.STATUTE

    def test_code_select_text(self, fake_beard_client):

        enactment = fake_beard_client.read("/test/acts/47/1")
        assert enactment.text.startswith("This Act may be cited")

    def test_code_select_text_chapeau(self, fake_beard_client):
        enactment = fake_beard_client.read("/test/acts/47/4")
        enactment.select()
        assert enactment.selected_text().startswith("In this Act, beard means")

    def test_get_bill_of_rights_effective_date(self, fake_usc_client):
        enactment = fake_usc_client.read("/us/const/amendment/V")
        assert enactment.start_date == datetime.date(1791, 12, 15)

    def test_text_interval_constitution_section(self, fake_usc_client):
        enactment = fake_usc_client.read("/us/const/article/I/8/8")

        # The entire 317-character section is selected.
        ranges = enactment.selection.ranges()
        assert ranges[0].start == 0
        assert ranges[0].end == 172

        passage = enactment.get_passage(TextPositionSelector(68, 81))
        assert passage == "…limited Times…"

    def test_text_interval_beyond_end_of_section(self, fake_usc_client):
        """No longer raises an error, just selects to the end of the text."""
        enactment = fake_usc_client.read("/us/const/article/I/8/8")

        selector = TextPositionSelector(68, 400)
        passage = enactment.get_passage(selector)
        assert passage.startswith("…limited Times")
        assert passage.endswith(enactment.text[-10:])

    def test_bad_section(self, fake_usc_client):
        """
        The path is a section that doesn't exist in USC.
        """
        with pytest.raises(LegislicePathError):
            enactment = fake_usc_client.read("/us/usc/article/I/3/7")

    def test_text_interval_bad_selector(self, make_selector, make_response):
        client = FakeClient(responses=make_response)
        enactment = client.read("/us/const/amendment/IV")
        with pytest.raises(TextSelectionError):
            _ = enactment.convert_selection_to_set(make_selector["bad_selector"])
