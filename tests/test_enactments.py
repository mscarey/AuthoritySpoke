import datetime
import os
from tests.conftest import e_copyright

from anchorpoint.textselectors import TextQuoteSelector, TextSelectionError
from dotenv import load_dotenv
from legislice.download import Client
from legislice.enactments import Enactment, consolidate_enactments
from legislice.schemas import EnactmentSchema
import pytest

from authorityspoke.io import anchors, loaders, readers, dump


load_dotenv()

TOKEN = os.getenv("LEGISLICE_API_TOKEN")


class TestEnactments:
    client = Client(api_token=TOKEN)

    def test_make_enactment(self, e_search_clause):
        search_clause = e_search_clause
        assert search_clause.selected_text().endswith("shall not be violated...")

    @pytest.mark.vcr
    def test_create_enactment_with_init(self, make_code):
        """
        Using the __init__ method of the Enactment class, insteaid of
        readers.read_enactment or the Enactment marshmallow schema.
        """
        beard_definition = self.client.read("/test/acts/47/4/")
        assert beard_definition.text.startswith("In this Act, beard")

    @pytest.mark.vcr
    def test_make_enactment_from_selector_without_code(self):
        selector = TextQuoteSelector(suffix=", shall be vested")
        art_3 = self.client.read("/us/const/article/III/1")
        art_3.select(selector)
        assert art_3.text.startswith("The judicial Power")
        assert art_3.selected_text().endswith("the United States...")

    @pytest.mark.vcr
    def test_make_enactment_from_dict_with_reader(self):
        fourth_a = readers.read_enactment(
            record={"node": "/us/const/amendment/IV"}, client=self.client
        )
        assert fourth_a.text.endswith("and the persons or things to be seized.")

    @pytest.mark.vcr
    def test_make_enactment_from_dict_with_text_split(self):
        fourth_a = readers.read_enactment(
            record={
                "node": "/us/const/amendment/IV",
                "text": "and|the persons or things|to be seized.",
            },
            client=self.client,
        )
        assert fourth_a.selected_text() == "...the persons or things..."

    @pytest.mark.vcr
    def test_passage_from_imported_statute(self, make_regime):
        oracle_majority = loaders.load_and_read_decision(f"oracle_h.json").majority
        raw_holdings = loaders.load_holdings("holding_oracle.json")
        holdings = readers.read_holdings(raw_holdings, regime=make_regime)
        oracle_majority.posit(holdings)
        despite_text = str(list(oracle_majority.holdings)[5])
        assert "In no case does copyright protection " in despite_text

    @pytest.mark.vcr
    def test_short_passage_from_uslm_code(self):
        """Also tests adding the missing initial "/" in ``path``."""
        method = readers.read_enactment(
            {
                "node": "us/usc/t17/s102/b",
                "prefix": "process, system,",
                "suffix": ", concept, principle",
            },
            client=self.client,
        )
        assert method.selected_text() == "...method of operation..."

    @pytest.mark.vcr
    def test_chapeau_and_subsections_from_uslm_code(self):
        definition = readers.read_enactment(
            {"node": "/test/acts/47/4"}, client=self.client,
        )
        assert definition.text.strip().endswith("below the nose.")

    def test_cite_path_in_str(self, e_search_clause):
        assert "/us/const/amendment/IV" in str(e_search_clause)

    def test_equal_enactment_text(self, e_due_process_5, e_due_process_14):
        assert e_due_process_5.means(e_due_process_14)

    def test_not_gt_if_equal(self, e_search_clause):
        assert e_search_clause == e_search_clause
        assert e_search_clause.means(e_search_clause)
        assert not e_search_clause > e_search_clause

    def test_enactment_subset_or_equal(self, e_due_process_5, e_due_process_14):
        assert e_due_process_5 >= e_due_process_14

    def test_unequal_enactment_text(self, e_search_clause, e_fourth_a):
        assert e_search_clause != e_fourth_a

    def test_enactment_subset(self, e_search_clause, e_fourth_a):
        assert e_search_clause < e_fourth_a

    def test_comparison_to_factor_false(self, e_due_process_5, watt_factor):
        f1 = watt_factor["f1"]
        assert not e_due_process_5 == f1

    def test_implication_of_factor_fails(self, e_due_process_5, watt_factor):
        f1 = watt_factor["f1"]
        with pytest.raises(TypeError):
            assert not e_due_process_5 > f1

    def test_implication_by_factor_fails(self, e_due_process_5, watt_factor):
        f1 = watt_factor["f1"]
        with pytest.raises(TypeError):
            assert not e_due_process_5 < f1

    @pytest.mark.vcr
    def test_read_constitution_for_effective_date(self):
        ex_post_facto_provision = readers.read_enactment(
            {"node": "/us/const/article/I/9/3"}, client=self.client
        )
        assert ex_post_facto_provision.start_date == datetime.date(1788, 9, 13)

    def test_bill_of_rights_effective_date(self, e_search_clause):
        # December 15, 1791
        assert e_search_clause.start_date == datetime.date(1791, 12, 15)

    @pytest.mark.vcr
    def test_date_and_text_from_path_and_regime(self):
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
            {"node": "/us/const/amendment/XII"}, client=self.client
        )
        assert amendment_12.start_date == datetime.date(1804, 9, 25)
        assert "Electors shall meet" in amendment_12.text

    def test_14th_A_effective_date(self, e_due_process_14):
        # July 28, 1868
        assert e_due_process_14.start_date == datetime.date(1868, 7, 28)

    def test_compare_effective_dates(self, e_due_process_5, e_due_process_14):
        dp5 = make_enactment["due_process_5"]
        dp14 = make_enactment["due_process_14"]
        assert e_due_process_14.effective_date > e_due_process_5.effective_date

    def test_invalid_selector_text(self, make_selector):
        with pytest.raises(TextSelectionError):
            _ = Enactment(
                node="/us/const/amendment/IV",
                selection=make_selector["bad_selector"],
                heading="",
                content="Not the same text as in the selector",
                start_date="2000-01-01",
            )

    # Addition

    def test_add_overlapping_enactments(self, e_search_clause, e_warrants_clause):
        combined = e_search_clause + e_warrants_clause

        passage = (
            "against unreasonable searches and seizures, "
            + "shall not be violated, "
            + "and no Warrants shall issue,"
        )
        assert passage in combined.text

    def test_add_shorter_plus_longer(self, e_fourth_a, e_search_clause):
        combined = e_search_clause + e_fourth_a

        assert combined.selected_text() == e_fourth_a.selected_text()
        assert combined.means(e_fourth_a)

    def test_add_longer_plus_shorter(self, make_enactment):
        search_clause = e_search_clause
        fourth_a = make_enactment["fourth_a"]

        combined = fourth_a + search_clause

        assert combined.text == fourth_a.text
        assert combined == fourth_a

    def test_consolidate_enactments(self, fourth_a):
        search_clause = fourth_a.copy()
        search_clause["selection"] = [{"suffix": ", and no Warrants"}]

        warrants_clause = fourth_a.copy()
        warrants_clause["selection"] = [{"prefix": "shall not be violated,"}]

        schema = EnactmentSchema()

        fourth = schema.load(fourth_a)
        search = schema.load(search_clause)
        warrants = schema.load(warrants_clause)

        consolidated = consolidate_enactments([fourth, search, warrants])
        assert len(consolidated) == 1
        assert consolidated[0].means(fourth)

    @pytest.mark.vcr()
    def test_consolidate_adjacent_passages(self):
        copyright_clause = self.client.read("/us/const/article/I/8/8")
        copyright_statute = self.client.read("/us/usc/t17/s102/b")

        copyright_clause.select(None)
        securing_for_authors = copyright_clause + (
            "To promote the Progress of Science and "
            "useful Arts, by securing for limited Times to Authors"
        )
        and_inventors = copyright_clause + "and Inventors"
        right_to_writings = (
            copyright_clause + "the exclusive Right to their respective Writings"
        )
        to_combine = [
            copyright_statute,
            securing_for_authors,
            and_inventors,
            right_to_writings,
        ]
        combined = consolidate_enactments(to_combine)
        assert len(combined) == 2
        assert any(
            law.selected_text().startswith("To promote the Progress")
            and law.selected_text().endswith("their respective Writings...")
            for law in combined
        )

    def test_do_not_consolidate_from_different_sections(self, fifth_a, fourteenth_dp):
        schema = EnactmentSchema()

        due_process_5 = schema.load(fifth_a)
        due_process_14 = schema.load(fourteenth_dp)

        due_process_5.select("life, liberty, or property, without due process of law")
        due_process_14.select("life, liberty, or property, without due process of law")

        combined = consolidate_enactments([due_process_5, due_process_14])
        assert len(combined) == 2

    def test_cant_add_fact_to_enactment(self, watt_factor, make_enactment):
        with pytest.raises(TypeError):
            print(e_search_clause + watt_factor["f3"])

    def test_cant_add_enactment_that_is_not_ancestor_or_descendant(
        self, e_search_clause, enactment_copyright
    ):
        with pytest.raises(ValueError):
            e_search_clause + enactment_copyright


class TestDump:
    client = Client(api_token=TOKEN)

    def test_dump_dict(self, make_enactment):
        d = dump.to_dict(make_enactment["securing_for_authors"])
        assert "Science and useful Arts" in d["selector"]["exact"]

    @pytest.mark.vcr
    def test_dump_json(self):
        provision = readers.read_enactment(
            {"node": "/test/acts/47/6A"}, client=self.client
        )
        dumped_provision = dump.to_json(provision)
        assert '"node": "/test/acts/47/6A"' in dumped_provision

    @pytest.mark.vcr
    def test_round_trip_dict(self):
        provision = readers.read_enactment(
            {"node": "/test/acts/47/6A"}, client=self.client
        )
        dumped_provision = dump.to_dict(provision)
        new = self.client.read_from_json(dumped_provision)
        assert new.node == "/test/acts/47/6A"


class TestTextSelection:
    client = Client(api_token=TOKEN)

    def test_code_from_selector(self, make_regime):
        code = make_regime.get_code("/us/usc/t17/s103")
        assert code.uri == "/us/usc/t17"

    @pytest.mark.vcr
    def test_usc_selection(self, make_selector):
        enactment = self.client.read("/us/usc/t17/s103")
        selector = make_selector["preexisting material"]
        enactment.select(selector)

        assert enactment.level == "statute"
        assert enactment.jurisdiction == "us"
        assert enactment.code == "usc"

    def test_omit_terminal_slash(self):
        statute = readers.read_enactment(
            {"exact": "process, system,", "node": "us/usc/t17/s102/b/"},
            client=self.client,
        )
        assert not statute.source.endswith("/")

    def test_add_omitted_initial_slash(self):
        statute = readers.read_enactment(
            {"exact": "process, system,", "node": "us/usc/t17/s102/b/"},
            client=self.client,
        )
        assert statute.source.startswith("/")

    def test_selector_text_split(self):
        data = {"text": "process, system,|method of operation|, concept, principle"}
        selector = anchors.read_selector(data)
        assert selector.exact.startswith("method")

    def test_whitespace_when_selecting_with_suffix(self, e_copyright):
        """Overwrite existing selector and test for trailing whitespace."""
        copyright_selector = TextQuoteSelector(suffix="idea, procedure,")
        e_copyright.select(copyright_selector)
        assert e_copyright.selected_text() == (
            "In no case does copyright protection "
            + "for an original work of authorship extend to any..."
        )

    @pytest.mark.vcr
    def test_section_text_from_path(self):
        copyright_exceptions = readers.read_enactment(
            {"node": "/us/usc/t17/s102/b"}, client=self.client
        )
        assert copyright_exceptions.text.startswith(
            "In no case does copyright protection "
            + "for an original work of authorship extend to any"
        )

    @pytest.mark.vcr
    def test_exact_text_not_in_selection(self):
        with pytest.raises(TextSelectionError):
            _ = readers.read_enactment(
                {"node": "/us/const/amendment/XV/1", "exact": "due process",},
                client=self.client,
            )

    def test_multiple_non_Factor_selectors_for_Holding(self):
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
