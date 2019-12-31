import datetime
import json
import operator

from anchorpoint.textselectors import TextQuoteSelector
from pint import UnitRegistry
import pytest

from authorityspoke.codes import Code
from authorityspoke.enactments import Enactment, consolidate_enactments
from authorityspoke.opinions import Opinion
from authorityspoke.io import anchors, loaders, readers, dump


class TestEnactments:
    def test_make_enactment(self, make_enactment):
        search_clause = make_enactment["search_clause"]
        assert search_clause.text.endswith("shall not be violated")

    def test_create_enactment_with_init(self, make_code):
        """
        Using the __init__ method of the Enactment class, insteaid of
        readers.read_enactment or the Enactment marshmallow schema.
        """
        beard_definition = Enactment(
            source="/au/act/1934/47/1/4/", code=make_code["beard_act"]
        )
        assert beard_definition.text.startswith("In this Act, beard")

    def test_make_enactment_from_selector_without_code(self, make_code):
        select = TextQuoteSelector(suffix=", shall be vested")
        art_3 = Enactment(
            selector=select, source="/us/const/article-III/1", code=make_code["const"]
        )
        assert art_3.text.startswith("The judicial Power")
        assert art_3.text.endswith("the United States")

    def test_make_enactment_from_dict_with_code(self, make_code):
        fourth_a = readers.read_enactment(
            record={"source": "/us/const/amendment-IV"}, code=make_code["const"]
        )
        assert fourth_a.text.endswith("and the persons or things to be seized.")

    def test_make_enactment_from_dict_with_code_and_regime(
        self, make_regime, make_code
    ):
        fourth_a = readers.read_enactment(
            record={"source": "/us/const/amendment-IV"},
            code=make_code["const"],
            regime=make_regime,
        )
        assert fourth_a.text.endswith("and the persons or things to be seized.")

    def test_make_enactment_from_dict_with_text_split(self, make_regime, make_code):
        fourth_a = readers.read_enactment(
            record={
                "source": "/us/const/amendment-IV",
                "text": "and|the persons or things|to be seized.",
            },
            code=make_code["const"],
            regime=make_regime,
        )
        assert fourth_a.selector.exact.endswith("or things")

    def test_passage_from_imported_statute(self, make_regime):
        oracle_majority = loaders.load_and_read_decision(f"oracle_h.json").majority
        raw_holdings = loaders.load_holdings("holding_oracle.json")
        holdings = readers.read_holdings(raw_holdings, regime=make_regime)
        oracle_majority.posit(holdings)
        despite_text = str(list(oracle_majority.holdings)[5])
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

    def test_chapeau_and_subsections_from_uslm_code(self, make_code):
        beard = make_code["beard_act"]
        definition = readers.read_enactment(
            {"source": "/au/act/1934/47/1/4"}, code=beard,
        )
        assert definition.text.strip().endswith("below the nose.")

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
        interval = code.text_interval(provision.selector, path=provision.source)
        this_section = code.section_text_from_path(path=provision.source)
        assert this_section[interval.start : interval.end] == text

    def test_invalid_selector_text(self, make_code, make_selector):
        with pytest.raises(ValueError):
            _ = Enactment(
                source="/us/const/amendment-IV",
                selector=make_selector["bad_selector"],
                code=make_code["const"],
            )

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


class TestTextSelection:
    def test_code_from_selector(self, make_regime, make_selector):
        code = make_regime.get_code("/us/usc/t17/s103")
        assert code.uri == "/us/usc/t17"

    def test_usc_selection(self, make_regime, make_selector):
        selector = make_selector["preexisting material"]
        source = "/us/usc/t17/s103"
        code = make_regime.get_code(source)
        enactment = Enactment(code=code, source=source, selector=selector)
        assert enactment.code.level == "statute"
        assert enactment.code.jurisdiction == "us"

    def test_omit_terminal_slash(self, make_code):
        usc17 = make_code["usc17"]
        statute = readers.read_enactment(
            {"exact": "process, system,", "source": "us/usc/t17/s102/b/"}, code=usc17
        )
        assert not statute.source.endswith("/")

    def test_add_omitted_initial_slash(self, make_code):
        usc17 = make_code["usc17"]
        statute = readers.read_enactment(
            {"exact": "process, system,", "source": "us/usc/t17/s102/b/"}, code=usc17
        )
        assert statute.source.startswith("/")

    def test_selector_text_split(self):
        data = {"text": "process, system,|method of operation|, concept, principle"}
        selector = anchors.read_selector(data)
        assert selector.exact.startswith("method")

    def test_passage_from_uslm_code(self, make_enactment):
        copyright_exceptions = make_enactment["copyright"]
        assert copyright_exceptions.selector.exact.strip() == (
            "In no case does copyright protection "
            + "for an original work of authorship extend to any"
        )

    def test_section_text_from_path_and_regime(self, make_regime):
        copyright_exceptions = readers.read_enactment(
            {"source": "/us/usc/t17/s102/b"}, regime=make_regime
        )
        assert copyright_exceptions.text.startswith(
            "In no case does copyright protection "
            + "for an original work of authorship extend to any"
        )

    def test_exact_text_not_in_selection(self, make_regime):
        due_process_wrong_section = TextQuoteSelector(exact="due process")
        with pytest.raises(ValueError):
            enactment = readers.read_enactment(
                {
                    "selector": due_process_wrong_section,
                    "source": "/us/const/amendment-XV/1",
                },
                regime=make_regime,
            )

    def test_multiple_non_Factor_selectors_for_Holding(self, make_regime):
        """
        The Holding-level TextQuoteSelectors should be built from this:

        "text": [
            "Census data therefore do not|trigger|copyright",
            "|may|possess the requisite originality"
            ]
        """

        raw_holdings = loaders.load_holdings("holding_feist.json")
        holding_links = anchors.get_holding_anchors(raw_holdings)
        assert len(holding_links[6]) == 2
