import datetime
import os

from anchorpoint.textselectors import TextQuoteSelector, TextSelectionError
from dotenv import load_dotenv
from legislice.download import Client

from legislice.enactments import Enactment, consolidate_enactments
from legislice.schemas import EnactmentSchema
import pytest

from authorityspoke.io import anchors, loaders, readers, dump
from authorityspoke.io.downloads import FakeClient

load_dotenv()

TOKEN = os.getenv("LEGISLICE_API_TOKEN")


class TestEnactments:
    client = Client(api_token=TOKEN)

    def test_make_enactment(self, e_search_clause):
        search_clause = e_search_clause
        assert search_clause.selected_text().endswith("shall not be violated…")

    def test_create_enactment_with_init(self, fake_beard_client):
        """
        Using the __init__ method of the Enactment class, insteaid of
        readers.read_enactment or the Enactment marshmallow schema.
        """
        beard_definition = fake_beard_client.read("/test/acts/47/4/")
        assert beard_definition.text.startswith("In this Act, beard")

    def test_make_enactment_from_selector_without_code(self, fake_usc_client):
        selector = TextQuoteSelector(suffix=" to their respective")
        art_3 = fake_usc_client.read("/us/const/article/I/8/8")
        art_3.select(selector)
        assert art_3.text.startswith("To promote")
        assert art_3.selected_text().endswith("exclusive Right…")

    def test_make_enactment_from_dict_with_reader(self, fake_usc_client):
        fourth_a = fake_usc_client.read_from_json({"node": "/us/const/amendment/IV"})
        assert fourth_a.text.endswith("and the persons or things to be seized.")

    def test_make_enactment_from_dict_with_text_split(self, fake_usc_client):
        fourth_a = fake_usc_client.read_from_json(
            {
                "node": "/us/const/amendment/IV",
                "text": "and|the persons or things|to be seized.",
            }
        )
        assert fourth_a.selected_text() == "…the persons or things…"

    def test_passage_from_imported_statute(self, fake_usc_client):
        oracle_majority = loaders.load_and_read_decision(f"oracle_h.json").majority
        raw_holdings = loaders.load_holdings("holding_oracle.json")
        holdings = readers.read_holdings(raw_holdings, client=fake_usc_client)
        oracle_majority.posit(holdings)
        despite_text = str(list(oracle_majority.holdings)[5])
        assert "In no case does copyright protection " in despite_text

    def test_short_passage_from_uslm_code(self, fake_usc_client):
        """Also tests adding the missing initial "/" in ``path``."""
        method = fake_usc_client.read_from_json(
            {
                "node": "us/usc/t17/s102/b",
                "prefix": "process, system,",
                "suffix": ", concept, principle",
            },
        )
        assert method.selected_text() == "…method of operation…"

    def test_chapeau_and_subsections_from_uslm_code(self, fake_beard_client):
        definition = fake_beard_client.read_from_json({"node": "/test/acts/47/4"})
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
        e_fourth_a.select_all()
        assert e_search_clause != e_fourth_a

    def test_enactment_subset(self, e_search_clause, e_fourth_a):
        e_fourth_a.select_all()
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

    def test_read_constitution_for_effective_date(self, fake_usc_client):
        ex_post_facto_provision = fake_usc_client.read_from_json(
            {"node": "/us/const/article/I/8/8"}
        )
        assert ex_post_facto_provision.start_date == datetime.date(1788, 9, 13)

    def test_bill_of_rights_effective_date(self, e_search_clause):
        # December 15, 1791
        assert e_search_clause.start_date == datetime.date(1791, 12, 15)

    def test_date_and_text_from_path_and_regime(self, fake_usc_client):
        """
        This tests assigning the full text of
        the section as the text of the Enactment, even though no
        ``exact``, ``prefix``, or ``suffix` parameter was
        passed to the TextQuoteSelector constructor.
        """
        amendment_12 = fake_usc_client.read_from_json(
            {"node": "/us/const/amendment/XIV"}
        )
        assert amendment_12.start_date == datetime.date(1868, 7, 28)
        assert "All persons born" in amendment_12.text

    def test_compare_effective_dates(self, e_due_process_5, e_due_process_14):
        assert e_due_process_14.start_date > e_due_process_5.start_date

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
        e_fourth_a.select_all()
        combined = e_search_clause + e_fourth_a

        assert combined.selected_text() == e_fourth_a.selected_text()
        assert combined.means(e_fourth_a)

    def test_add_longer_plus_shorter(self, e_fourth_a, e_search_clause):
        e_fourth_a.select_all()
        combined = e_fourth_a + e_search_clause

        assert combined.selected_text() == e_fourth_a.selected_text()
        assert combined.means(e_fourth_a)

    def test_consolidate_enactments(self, make_response):

        fourth_a = make_response["/us/const/amendment/IV"]["1791-12-15"]
        search_clause = fourth_a.copy()
        search_clause["selection"] = [{"suffix": ", and no Warrants"}]

        warrants_clause = fourth_a.copy()
        warrants_clause["selection"] = [{"prefix": "shall not be violated,"}]

        schema = EnactmentSchema()

        fourth = schema.load(fourth_a)
        fourth.select_all()

        search = schema.load(search_clause)
        warrants = schema.load(warrants_clause)

        consolidated = consolidate_enactments([fourth, search, warrants])
        assert len(consolidated) == 1
        assert consolidated[0].means(fourth)

    def test_consolidate_adjacent_passages(self, make_response):
        client = FakeClient(responses=make_response)
        copyright_clause = client.read("/us/const/article/I/8/8")
        copyright_statute = client.read("/us/usc/t17/s102/b")

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
            and law.selected_text().endswith("their respective Writings…")
            for law in combined
        )

    def test_do_not_consolidate_from_different_sections(self, make_response):
        client = FakeClient(responses=make_response)

        due_process_5 = client.read("/us/const/amendment/V")
        due_process_14 = client.read("/us/const/amendment/XIV")

        due_process_5.select("life, liberty, or property, without due process of law")
        due_process_14.select("life, liberty, or property, without due process of law")

        combined = consolidate_enactments([due_process_5, due_process_14])
        assert len(combined) == 2

    def test_cant_add_fact_to_enactment(self, watt_factor, e_search_clause):
        with pytest.raises(TypeError):
            print(e_search_clause + watt_factor["f3"])

    def test_cant_add_enactment_that_is_not_ancestor_or_descendant(
        self, e_search_clause, e_copyright
    ):
        with pytest.raises(ValueError):
            e_search_clause + e_copyright


class TestDump:
    client = Client(api_token=TOKEN)

    @pytest.mark.vcr
    def test_dump_dict(self):
        enactment = self.client.read("/us/const/article/I/8/8")
        d = dump.to_dict(enactment)
        start = d["selection"][0]["start"]
        end = d["selection"][0]["end"]
        text_selection = d["text_version"]["content"][start:end]
        assert "Science and useful Arts" in text_selection

    def test_dump_json(self, fake_beard_client):
        provision = fake_beard_client.read_from_json({"node": "/test/acts/47/6A"})
        dumped_provision = dump.to_json(provision)
        assert '"node": "/test/acts/47/6A"' in dumped_provision

    @pytest.mark.vcr
    def test_round_trip_dict(self, fake_beard_client):
        provision = fake_beard_client.read_from_json({"node": "/test/acts/47/6A"})
        dumped_provision = dump.to_dict(provision)
        new = self.client.read_from_json(dumped_provision)
        assert new.node == "/test/acts/47/6A"


class TestTextSelection:
    def test_code_from_selector(self, fake_usc_client):
        enactment = fake_usc_client.read("/us/usc/t17/s103")
        assert enactment.code == "usc"

    def test_usc_selection(self, make_selector, fake_usc_client):
        enactment = fake_usc_client.read("/us/usc/t17/s103")
        selector = make_selector["preexisting material"]
        enactment.select(selector)

        assert enactment.level == "statute"
        assert enactment.jurisdiction == "us"
        assert enactment.code == "usc"

    def test_omit_terminal_slash(self, fake_usc_client):
        statute = fake_usc_client.read_from_json(
            {"exact": "process, system,", "node": "us/usc/t17/s102/b/"}
        )
        assert not statute.source.endswith("/")

    def test_add_omitted_initial_slash(self, fake_usc_client):
        statute = fake_usc_client.read_from_json(
            {"exact": "process, system,", "node": "us/usc/t17/s102/b/"}
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
            + "for an original work of authorship extend to any…"
        )

    def test_section_text_from_path(self, fake_usc_client):
        copyright_exceptions = fake_usc_client.read_from_json(
            {"node": "/us/usc/t17/s102/b"}
        )
        assert copyright_exceptions.text.startswith(
            "In no case does copyright protection "
            + "for an original work of authorship extend to any"
        )

    def test_exact_text_not_in_selection(self, fake_usc_client):
        with pytest.raises(TextSelectionError):
            _ = fake_usc_client.read_from_json(
                {
                    "node": "/us/const/amendment/XV/1",
                    "exact": "due process",
                }
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
