import datetime
import os

import pytest

from anchorpoint.textselectors import TextPositionSelector, TextSelectionError
from dotenv import load_dotenv

from legislice.download import Client

load_dotenv()

TOKEN = os.getenv("LEGISLICE_API_TOKEN")


class TestCodes:
    client = Client(api_token=TOKEN)

    @pytest.mark.parametrize(
        "codename, name, level",
        [
            ("usc17", "USC Title 17", "statute"),
            ("const", "Constitution of the United States", "constitution"),
            ("cfr37", "Code of Federal Regulations Title 37", "regulation"),
            ("ca_evid", "California Evidence Code", "statute"),
            ("ca_pen", "California Penal Code", "statute"),
        ],
    )
    def test_making_code(self, codename, name, level):
        code = make_code[codename]
        assert str(code) == name
        assert code.level == level

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

    @pytest.mark.parametrize(
        "code, path",
        [
            ("usc17", "/us/usc/t17"),
            ("const", "/us/const"),
            ("cfr37", "/us/cfr/t37"),
            ("ca_evid", "/us-ca/code/evid"),
            ("ca_pen", "/us-ca/code/pen"),
            ("beard_act", "/au/act/1934/47"),
        ],
    )
    def test_code_urls(self, code, path):
        assert make_code[code].uri == path

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "path, expected",
        [("/us/usc/t17", "COPYRIGHTS"), ("/us/const", "United States Constitution"),],
    )
    def test_code_title(self, path, expected):
        enactment = self.client.read(path=path)
        assert enactment.heading == expected

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
        passage = enactment.select_text_from_interval(TextPositionSelector(66, 85))
        assert passage == "removal from Office"

    def test_text_interval_entire_section(self):
        """
        Returns an interval covering the entire 317-character section.
        """
        interval = make_code["const"].text_interval(path="/us/const/article/I/3/7")
        assert interval == (0, 317)

    def test_text_interval_beyond_end_of_section(self):
        with pytest.raises(IndexError):
            _ = make_code["const"].select_text_from_interval(
                path="/us/const/article/I/3/7", interval=TextPositionSelector(66, 400)
            )

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

    def test_text_interval_bad_selector(self, make_selector):
        with pytest.raises(TextSelectionError):
            _ = make_code["const"].text_interval(
                selector=make_selector["bad_selector"], path="/us/const/amendment/IV",
            )
