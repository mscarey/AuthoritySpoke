import datetime
import os

import pytest

from anchorpoint.textselectors import TextPositionSelector, TextSelectionError
from dotenv import load_dotenv

from legislice.download import Client, JSONRepository

load_dotenv()

TOKEN = os.getenv("LEGISLICE_API_TOKEN")


class TestCodes:
    client = Client(api_token=TOKEN)

    def test_cfr_repr(self):
        cfr = make_code["cfr37"]
        assert "Title 37" in repr(cfr)

    def test_get_code_from_regime_with_partial_uri(self, make_regime):
        """
        The regime should return the appropriate "code" even though its
        uri is more specific than the query, because it's the only one
        available that starts with that.
        """
        beard_act = make_regime.get_code("/au/act")
        assert "Enlightenment" in str(beard_act)

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

    def test_text_interval_absent_section(self):
        """
        The path is a section that doesn't exist in CFR.
        """
        with pytest.raises(ValueError):
            _ = make_code["cfr37"].select_text_from_interval(
                path="/us/const/article/I/3/7", interval=TextPositionSelector(0, 66)
            )

    def test_text_interval_bad_source(self, make_selector):
        with pytest.raises(ValueError):
            _ = make_code["usc17"].text_interval(
                selector=make_selector["bad_selector"], path="/us/const/amendment/IV",
            )

    def test_text_interval_bad_selector(self, make_selector, make_response):
        client = JSONRepository(responses=make_response)
        enactment = client.read("/us/const/amendment/IV")
        with pytest.raises(TextSelectionError):
            _ = enactment.convert_selection_to_set(make_selector["bad_selector"])
