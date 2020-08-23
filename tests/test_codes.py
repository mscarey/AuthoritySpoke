import datetime
import os

import pytest

from anchorpoint.textselectors import TextPositionSelector, TextSelectionError
from dotenv import load_dotenv

from legislice.download import Client, LegislicePathError

from legislice.mock_clients import JSONRepository

from legislice.schemas import EnactmentSchema

from authorityspoke.io import loaders, schemas

load_dotenv()

TOKEN = os.getenv("LEGISLICE_API_TOKEN")


class TestCodes:
    client = Client(api_token=TOKEN)

    def test_cfr_repr(self):
        oracle_dictionary = loaders.load_holdings("holding_oracle.json")
        regulation = oracle_dictionary[10]["enactments_despite"][1]
        schema = EnactmentSchema()
        enactment = schema.load(regulation)

        assert enactment.level == "regulation"
        assert "/cfr/" in repr(enactment)

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "path, heading, level",
        [
            ("/us/usc", "United States Code", "statute"),
            ("/us/const", "United States Constitution", "constitution"),
            ("/test/acts", "Acts of Australia", "statute"),
        ],
    )
    def test_code_title(self, path, heading, level):
        enactment = self.client.read(path=path)
        assert enactment.heading.startswith(heading)
        assert enactment.level == level

    @pytest.mark.vcr
    def test_code_select_text(self):
        enactment = self.client.read(path="/test/acts/47/1")
        assert enactment.text.startswith("This Act may be cited")

    @pytest.mark.vcr
    def test_code_select_text_chapeau(self):
        enactment = self.client.read(path="/test/acts/47/4")
        enactment.select()
        assert enactment.selected_text().startswith("In this Act, beard means")

    @pytest.mark.vcr
    def test_get_bill_of_rights_effective_date(self):
        enactment = self.client.read(path="/us/const/amendment/V")
        assert enactment.start_date == datetime.date(1791, 12, 15)

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "path, expected",
        (
            ["/us/const/amendment/XIV/3", "No person shall be a Senator"],
            ["/us/const/article/I/5/1", "Each House shall be the Judge"],
        ),
    )
    def test_get_section_from_fed_const(self, path, expected):
        enactment = self.client.read(path=path)
        assert enactment.text.startswith(expected)

    @pytest.mark.vcr
    def test_text_interval_constitution_section(self):
        enactment = self.client.read(path="/us/const/article/I/3/7")

        # The entire 317-character section is selected.
        ranges = enactment.selection.ranges()
        assert ranges[0].start == 0
        assert ranges[0].end == 317

        passage = enactment.get_passage(TextPositionSelector(66, 85))
        assert passage == "…removal from Office…"

    @pytest.mark.vcr
    def test_text_interval_beyond_end_of_section(self):
        """No longer raises an error, just selects to the end of the text."""
        enactment = self.client.read(path="/us/const/article/I/3/7")

        selector = TextPositionSelector(66, 400)
        passage = enactment.get_passage(selector)
        assert passage.startswith("…removal from Office")
        assert passage.endswith(enactment.text[-10:])

    @pytest.mark.vcr
    def test_bad_section(self):
        """
        The path is a section that doesn't exist in USC.
        """
        with pytest.raises(LegislicePathError):
            enactment = self.client.read(path="/us/usc/article/I/3/7")

    def test_text_interval_bad_selector(self, make_selector, make_response):
        client = JSONRepository(responses=make_response)
        enactment = client.read("/us/const/amendment/IV")
        with pytest.raises(TextSelectionError):
            _ = enactment.convert_selection_to_set(make_selector["bad_selector"])
