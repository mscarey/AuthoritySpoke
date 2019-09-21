import pytest

from authorityspoke.enactments import Code, Enactment
from authorityspoke.io import loaders, references
from authorityspoke.io.schemas import SelectorSchema, get_schema_for_item
from authorityspoke.procedures import Procedure
from authorityspoke.rules import Rule
from authorityspoke.opinions import Opinion
from authorityspoke.selectors import TextQuoteSelector
from authorityspoke import to_dict, to_json


class TestSelectors:
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
        selector = TextQuoteSelector(exact="process, system,")
        statute = Enactment(selector=selector, source="us/usc/t17/s102/b/", code=usc17)
        assert not statute.source.endswith("/")

    def test_add_omitted_initial_slash(self, make_code):
        usc17 = make_code["usc17"]
        selector = TextQuoteSelector(exact="process, system,")
        statute = Enactment(selector=selector, source="us/usc/t17/s102/b/", code=usc17)
        assert statute.source.startswith("/")

    def test_selector_text_split(self):
        data = {
            "path": "/us/usc/t17/s102/b",
            "text": "process, system,|method of operation|, concept, principle",
        }
        selector = references.read_selector(data)
        assert selector.exact.startswith("method")

    def test_passage_from_uslm_code(self, make_enactment):
        copyright_exceptions = make_enactment["copyright"]
        assert copyright_exceptions.selector.exact.strip() == (
            "In no case does copyright protection "
            + "for an original work of authorship extend to any"
        )

    def test_convert_selector_to_json(self, make_code):
        usc17 = make_code["usc17"]
        copyright_exceptions = TextQuoteSelector(
            path="/us/usc/t17/s102/b", suffix="idea, procedure,", source=usc17
        )
        str_version = to_json(copyright_exceptions)
        assert '"exact": "In no case does copyright' in str_version

    def test_failed_prefix(self, make_code):
        usc17 = make_code["usc17"]
        with pytest.raises(ValueError):
            copyright_exceptions = TextQuoteSelector(
                path="/us/usc/t17/s102/b", prefix="sound recordings", source=usc17
            )

    def test_fail_no_exact_or_source(self, make_code):
        with pytest.raises(ValueError):
            copyright_exceptions = TextQuoteSelector(
                path="/us/usc/t17/s102/b", prefix="sound recordings"
            )
            copyright_enactment = Enactment(selector=copyright_exceptions)

    def test_failed_suffix(self, make_code):
        usc17 = make_code["usc17"]
        with pytest.raises(ValueError):
            copyright_exceptions = TextQuoteSelector(
                path="/us/usc/t17/s102/b", suffix="sound recordings", source=usc17
            )

    def test_section_text_from_path_and_regime(self, make_regime):
        copyright_exceptions = TextQuoteSelector(
            path="/us/usc/t17/s102/b", source=make_regime
        )
        assert copyright_exceptions.exact.startswith(
            "In no case does copyright protection "
            + "for an original work of authorship extend to any"
        )

    def test_exact_text_not_in_selection(self, make_regime):
        due_process_wrong_section = TextQuoteSelector(exact="due process")
        enactment = Enactment(
            selector=due_process_wrong_section,
            source="/us/const/amendment-XV/1",
            regime=make_regime,
        )
        with pytest.raises(ValueError):
            print(enactment.text)

    def test_multiple_non_Factor_selectors_for_Holding(self, make_regime):
        """
        The Holding-level TextQuoteSelectors should be built from this:

        "text": [
            "Census data therefore do not|trigger|copyright",
            "|may|possess the requisite originality"
            ]
        """

        holdings = loaders.load_holdings("holding_feist.json", regime=make_regime)
        assert len(holdings[7].selectors) == 2


class TestDump:
    def test_get_schema_for_selector(self):
        data = {
            "path": "/us/usc/t17/s102/b",
            "text": "process, system,|method of operation|, concept, principle",
        }
        selector = references.read_selector(data)
        schema = get_schema_for_item(selector)
        assert isinstance(schema, SelectorSchema)

    def test_dump_selector(self):
        data = {
            "path": "/us/usc/t17/s102/b",
            "text": "process, system,|method of operation|, concept, principle",
        }
        selector = references.read_selector(data)
        selector_dict = to_dict(selector)
        assert isinstance(selector_dict, dict)
        assert selector_dict["prefix"].startswith("process, system")

    def test_string_dump_selector(self):
        data = {
            "path": "/us/usc/t17/s102/b",
            "text": "process, system,|method of operation|, concept, principle",
        }
        selector = references.read_selector(data)
        selector_str = to_json(selector)
        assert isinstance(selector_str, str)
        assert '"prefix": "process, system' in selector_str
