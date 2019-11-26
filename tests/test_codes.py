import datetime

import pytest

from authorityspoke.codes import Code
from authorityspoke.enactments import Enactment, consolidate_enactments
from authorityspoke.io import loaders, readers, dump
from authorityspoke.textselectors.selectors import TextQuoteSelector
from authorityspoke.textselectors.selectors import TextPositionSelector


class TestCodes:
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
    def test_making_code(self, make_code, codename, name, level):
        code = make_code[codename]
        assert str(code) == name
        assert code.level == level

    def test_cfr_repr(self, make_code):
        cfr = make_code["cfr37"]
        assert "Title 37" in repr(cfr)

    @pytest.mark.parametrize(
        "code, path",
        [
            ("usc17", "/us/usc/t17"),
            ("const", "/us/const"),
            ("cfr37", "/us/cfr/t37"),
            ("ca_evid", "/us-ca/evid"),
            ("ca_pen", "/us-ca/pen"),
        ],
    )
    def test_code_urls(self, make_code, code, path):
        assert make_code[code].uri == path

    @pytest.mark.parametrize(
        "code, expected",
        [
            ("usc17", "Title 17"),
            ("const", "Constitution of the United States"),
            ("cfr37", "Code of Federal Regulations Title 37"),
            ("ca_evid", "California Evidence Code"),
            ("ca_pen", "California Penal Code"),
        ],
    )
    def test_code_title(self, make_code, code, expected):
        assert make_code[code].title == expected

    def test_get_bill_of_rights_effective_date(self, make_code):
        const = make_code["const"]
        bill_of_rights_date = datetime.date(1791, 12, 15)
        assert const.provision_effective_date("amendment-V") == bill_of_rights_date

    def test_get_14th_A_effective_date(self, make_code):
        const = make_code["const"]
        equal_protection_date = datetime.date(1868, 7, 28)
        assert const.provision_effective_date("amendment-XIV") == equal_protection_date

    def test_format_uri_for_const(self, make_code):
        """
        This should test the example in the docstring
        for the Code.format_uri_for_const method.
        """

        const = make_code["const"]
        out = const.format_uri_for_const("/us/const/amendment/XIV/1")
        assert out == "amendment-XIV-1"

    @pytest.mark.parametrize(
        "path, expected",
        (
            ["/us/const/amendment-XIV/3", "No person shall be a Senator"],
            ["/article-I/5/1", "Each House shall be the Judge"],
        ),
    )
    def test_get_section_from_fed_const(self, make_code, path, expected):
        const = make_code["const"]
        section = const.get_fed_const_section(path)
        assert section.find("text").text.startswith(expected)

    def test_text_interval_from_entire_code(self, make_code):
        interval = make_code["const"].select_text_from_interval(
            interval=TextPositionSelector(16, 50)
        )
        assert interval.startswith("Powers herein granted")

    def test_text_interval_constitution_section(self, make_code):
        passage = make_code["const"].select_text_from_interval(
            path="/us/const/article-I/3/7", interval=(66, 85)
        )
        assert passage == "removal from Office"

    def test_text_interval_entire_section(self, make_code):
        """
        Returns an interval covering the entire 317-character section.
        """
        interval = make_code["const"].text_interval(path="/us/const/article-I/3/7")
        assert interval == (0, 317)

    def test_text_interval_beyond_end_of_section(self, make_code):
        with pytest.raises(ValueError):
            _ = make_code["const"].select_text_from_interval(
                path="/us/const/article-I/3/7", interval=TextPositionSelector(66, 400)
            )

    def test_text_interval_absent_section(self, make_code):
        """
        The path is a section that doesn't exist in CFR.
        """
        with pytest.raises(ValueError):
            _ = make_code["cfr37"].select_text_from_interval(
                path="/us/const/article-I/3/7", interval=TextPositionSelector(0, 66)
            )

    def test_text_interval_bad_source(self, make_code, make_selector):
        with pytest.raises(ValueError):
            _ = make_code["usc17"].text_interval(
                selector=make_selector["bad_selector"], path="/us/const/amendment-IV",
            )

    def test_text_interval_bad_selector(self, make_code, make_selector):
        assert (
            make_code["const"].text_interval(
                selector=make_selector["bad_selector"], path="/us/const/amendment-IV",
            )
            is None
        )
