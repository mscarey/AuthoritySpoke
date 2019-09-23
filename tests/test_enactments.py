import datetime
import json
import operator

from pint import UnitRegistry
import pytest


from authorityspoke.enactments import Code, Enactment, consolidate_enactments
from authorityspoke.opinions import Opinion
from authorityspoke.predicates import ureg, Q_
from authorityspoke.io import loaders, readers, dump
from authorityspoke.selectors import TextQuoteSelector


class TestCodes:
    def test_making_code(self, make_code):
        const = make_code["const"]
        assert str(const) == "Constitution of the United States"

    def test_make_cfr(self, make_code):
        cfr = make_code["cfr37"]
        assert str(cfr) == "Code of Federal Regulations Title 37"

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
        interval = make_code["const"].select_text_from_interval(interval=(16, 50))
        assert interval.startswith("Powers herein granted")

    def test_text_interval_constitution_section(self, make_code):
        passage = make_code["const"].select_text_from_interval(
            path="/us/const/article-I/3/7", interval=(66, 85)
        )
        assert passage == "removal from Office"

    def test_text_interval_beyond_end_of_section(self, make_code):
        with pytest.raises(ValueError):
            answer = make_code["const"].select_text_from_interval(
                path="/us/const/article-I/3/7", interval=(66, 400)
            )
            print(answer)


class TestEnactments:
    def test_make_enactment(self, make_enactment):
        search_clause = make_enactment["search_clause"]
        assert search_clause.text.endswith("shall not be violated")

    def test_make_enactment_from_selector_without_code(self, make_code):
        select = TextQuoteSelector(suffix=", shall be vested")
        art_3 = Enactment(
            selector=select, source="/us/const/article-III/1", code=make_code["const"]
        )
        assert art_3.text.startswith("The judicial Power")
        assert art_3.text.endswith("the United States")

    def test_make_enactment_from_dict_with_code(self, make_code):
        fourth_a = readers.read_enactment(
            factor_record={"source": "/us/const/amendment-IV"}, code=make_code["const"]
        )
        assert fourth_a.text.endswith("and the persons or things to be seized.")

    def test_make_enactment_from_dict_with_code_and_regime(
        self, make_regime, make_code
    ):
        fourth_a = readers.read_enactment(
            factor_record={"source": "/us/const/amendment-IV"},
            code=make_code["const"],
            regime=make_regime,
        )
        assert fourth_a.text.endswith("and the persons or things to be seized.")

    def test_make_enactment_from_dict_with_text_split(self, make_regime, make_code):
        fourth_a = readers.read_enactment(
            factor_record={
                "source": "/us/const/amendment-IV",
                "text": "and|the persons or things|to be seized.",
            },
            code=make_code["const"],
            regime=make_regime,
        )
        assert fourth_a.selector.exact.endswith("or things")

    def test_passage_from_imported_statute(self, make_regime):
        oracle_majority = loaders.load_opinion(f"oracle_h.json")
        oracle_majority.posit(
            loaders.load_holdings(f"holding_oracle.json", regime=make_regime)
        )
        despite_text = str(oracle_majority.holdings[5])
        assert "In no case does copyright protection " in despite_text

    def test_short_passage_from_uslm_code(self, make_code):
        """Also tests adding the missing initial "/" in ``path``."""
        usc17 = make_code["usc17"]
        method = readers.read_enactment(
            {
                "source": "us/usc/t17/s102/b",
                "prefix": "process, system,",
                "suffix": ", concept, principle",
            },
            code=usc17,
        )
        assert method.text.strip() == "method of operation"

    def test_passage_from_cfr_code(self, make_code):
        cfr = make_code["cfr37"]
        slogans = readers.read_enactment({"source": "/us/cfr/t37/s202.1"}, code=cfr)
        assert "Words and short phrases such as names" in slogans.text

    def test_cite_entire_constitution(self, make_regime):
        entire_const = readers.read_enactment(
            {"source": "/us/const"}, regime=make_regime
        )
        assert "and been seven Years a Citizen" in entire_const.text

    def test_code_title_in_str(self, make_enactment):
        assert "secure in their persons" in str(make_enactment["search_clause"])

    def test_equal_enactment_text(self, make_enactment):
        assert make_enactment["due_process_5"].means(make_enactment["due_process_14"])

    def test_not_gt_if_equal(self, make_enactment):
        assert make_enactment["search_clause"] == make_enactment["search_clause"]
        assert make_enactment["search_clause"].means(make_enactment["search_clause"])
        assert not make_enactment["search_clause"] > make_enactment["search_clause"]

    def test_enactment_subset_or_equal(self, make_enactment):
        dp5 = make_enactment["due_process_5"]
        dp14 = make_enactment["due_process_14"]
        assert dp5 >= dp14

    def test_unequal_enactment_text(self, make_enactment):
        assert make_enactment["search_clause"] != make_enactment["fourth_a"]

    def test_enactment_subset(self, make_enactment):
        assert make_enactment["search_clause"] < make_enactment["fourth_a"]

    def test_comparison_to_factor_false(self, make_enactment, watt_factor):
        dp5 = make_enactment["due_process_5"]
        f1 = watt_factor["f1"]
        assert not dp5 == f1

    def test_implication_of_factor_fails(self, make_enactment, watt_factor):
        dp5 = make_enactment["due_process_5"]
        f1 = watt_factor["f1"]
        with pytest.raises(TypeError):
            assert not dp5 > f1

    def test_implication_by_factor_fails(self, make_enactment, watt_factor):
        dp5 = make_enactment["due_process_5"]
        f1 = watt_factor["f1"]
        with pytest.raises(TypeError):
            assert not dp5 < f1

    def test_constitution_effective_date(self, make_regime):
        ex_post_facto_provision = readers.read_enactment(
            {"source": "/us/const/article-I/9/3"}, regime=make_regime
        )
        assert ex_post_facto_provision.effective_date == datetime.date(1788, 9, 13)

    def test_bill_of_rights_effective_date(self, make_enactment):
        # December 15, 1791
        assert make_enactment["search_clause"].effective_date == datetime.date(
            1791, 12, 15
        )

    def test_date_and_text_from_path_and_regime(self, make_regime):
        """
        This tests different parsing code because the date is
        in the format "dated the 25th of September, 1804"

        This also verifies that providing the ``regime`` to the
        Enactment constructor is sufficient to assign the full text of
        the section as the text of the Enactment, even though no
        ``exact``, ``prefix``, ``suffix``, or ``source`` parameter was
        passed to the TextQuoteSelector constructor.
        """
        amendment_12 = readers.read_enactment(
            {"source": "/us/const/amendment-XII"}, regime=make_regime
        )
        assert amendment_12.effective_date == datetime.date(1804, 9, 25)
        assert "Electors shall meet" in amendment_12.text

    def test_14th_A_effective_date(self, make_enactment):
        # July 28, 1868
        assert make_enactment["due_process_14"].effective_date == datetime.date(
            1868, 7, 28
        )

    def test_compare_effective_dates(self, make_enactment):
        dp5 = make_enactment["due_process_5"]
        dp14 = make_enactment["due_process_14"]
        assert dp14.effective_date > dp5.effective_date

    @pytest.mark.parametrize(
        "enactment_name, code_name, text",
        [
            (
                "due_process_5",
                "const",
                "life, liberty, or property, without due process of law",
            ),
            (
                "copyright",
                "usc17",
                "In no case does copyright protection for an original work of authorship extend to any",
            ),
        ],
    )
    def test_text_interval(
        self, make_code, make_enactment, code_name, enactment_name, text
    ):
        """
        The interval represents the start and end of the phrase
        "life, liberty, or property, without due process of law"
        in the Fifth Amendment.
        """
        provision = make_enactment[enactment_name]
        code = make_code[code_name]
        interval = code.text_interval(provision)
        this_section = code.section_text_from_path(path=provision.source)
        assert this_section[interval[0] : interval[1]] == text

    def test_text_interval_bad_source(self, make_code, make_enactment):
        with pytest.raises(ValueError):
            _ = make_code["usc17"].text_interval(make_enactment["bad_selector"])

    def test_text_interval_bad_selector(self, make_code, make_enactment):
        assert make_code["const"].text_interval(make_enactment["bad_selector"]) is None

    # Addition

    def test_add_overlapping_enactments(self, make_enactment):
        search_clause = make_enactment["search_clause"]
        warrant_clause = make_enactment["warrants_clause"]

        combined = search_clause + warrant_clause

        passage = (
            "against unreasonable searches and seizures, "
            + "shall not be violated, "
            + "and no Warrants shall issue,"
        )
        assert passage in combined.text

    def test_add_shorter_plus_longer(self, make_enactment):
        search_clause = make_enactment["search_clause"]
        fourth_a = make_enactment["fourth_a"]

        combined = search_clause + fourth_a

        assert combined.text == fourth_a.text
        assert combined == fourth_a

    def test_add_longer_plus_shorter(self, make_enactment):
        search_clause = make_enactment["search_clause"]
        fourth_a = make_enactment["fourth_a"]

        combined = fourth_a + search_clause

        assert combined.text == fourth_a.text
        assert combined == fourth_a

    def test_consolidate_enactments(self, make_enactment):
        assert consolidate_enactments(
            [
                make_enactment["search_clause"],
                make_enactment["warrants_clause"],
                make_enactment["fourth_a"],
            ]
        ) == [make_enactment["fourth_a"]]

    def test_consolidate_adjacent_passages(self, make_enactment):
        combined = consolidate_enactments(
            [
                make_enactment["securing_for_authors"],
                make_enactment["right_to_writings"],
                make_enactment["copyright"],
                make_enactment["and_inventors"],
            ]
        )
        assert len(combined) == 2
        assert any(
            law.text.startswith("To promote the Progress")
            and law.text.endswith("their respective Writings")
            for law in combined
        )

    def test_do_not_consolidate_from_different_sections(self, make_enactment):
        combined = consolidate_enactments(
            [make_enactment["due_process_5"], make_enactment["due_process_14"]]
        )
        assert len(combined) == 2

    def test_cant_add_fact_to_enactment(self, watt_factor, make_enactment):
        with pytest.raises(TypeError):
            print(make_enactment["search_clause"] + watt_factor["f3"])

    def test_add_with_invalid_selector_text(self, make_enactment, make_code):
        with pytest.raises(ValueError):
            print(make_enactment["search_clause"] + make_enactment["bad_selector"])

    def test_add_unconnected_provisions(self, make_enactment):
        assert make_enactment["search_clause"] + make_enactment["copyright"] is None

    def test_add_more_specific_path_no_overlap(self, make_enactment):
        assert (
            make_enactment["securing_for_authors"]
            + make_enactment["commerce_vague_path"]
            is None
        )


class TestDump:
    def test_dump_dict(self, make_enactment):
        d = dump.to_dict(make_enactment["securing_for_authors"])
        assert "Science and useful Arts" in d["selector"]["exact"]

    def test_dump_json(self, make_code):
        cfr = make_code["cfr37"]
        slogans = readers.read_enactment({"source": "/us/cfr/t37/s202.1"}, code=cfr)
        s = dump.to_json(slogans)
        assert '"source": "/us/cfr/t37/s202.1"' in s

    def test_round_trip_dict(self, make_code):
        cfr = make_code["cfr37"]
        slogans = readers.read_enactment({"source": "/us/cfr/t37/s202.1"}, code=cfr)
        dumped_slogans = dump.to_dict(slogans)
        new = readers.read_enactment(dumped_slogans, code=cfr)
        assert new.source == "/us/cfr/t37/s202.1"

    def test_supply_missing_source_from_code(self, make_code):
        """
        Test that when a "source" path is omitted, the load method
        at least uses the uri of the code as the source.

        It might make sense for the method to find a more accurate
        source path for the specific section, but it doesn't.
        """
        const = make_code["const"]
        due_process = readers.read_enactment(
            {"prefix": "property, without ", "suffix": "nor shall private property"},
            code=const,
        )
        assert "due process" in due_process.text
        assert due_process.source.startswith("/us/const")
