import pytest

from authorityspoke.enactments import Code, Enactment
from authorityspoke.io import loaders, readers, references
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
        selector = references.read_selector(data)
        assert selector.exact.startswith("method")

    def test_passage_from_uslm_code(self, make_enactment):
        copyright_exceptions = make_enactment["copyright"]
        assert copyright_exceptions.selector.exact.strip() == (
            "In no case does copyright protection "
            + "for an original work of authorship extend to any"
        )

    def test_convert_selector_to_json(self, make_enactment):
        copyright_exceptions = make_enactment["copyright"]
        str_version = to_json(copyright_exceptions.selector)
        assert '"exact": "In no case does copyright' in str_version

    def test_failed_prefix(self, make_code):
        """
        The phrase "sound recordings" is in the cited Code, but not in
        the cited subsection, so creating the Enactment should fail.
        """
        usc17 = make_code["usc17"]
        up_to_sound = TextQuoteSelector(prefix="sound recordings")
        with pytest.raises(ValueError):
            _ = Enactment(source="/us/usc/t17/s102/b", selector=up_to_sound, code=usc17)

    def test_failed_suffix(self, make_code):
        usc17 = make_code["usc17"]
        up_to_sound = TextQuoteSelector(suffix="sound recordings")
        with pytest.raises(ValueError):
            _ = Enactment(source="/us/usc/t17/s102/b", selector=up_to_sound, code=usc17)

    def test_fail_no_exact_or_source(self, make_code):
        """
        "method of operation," is in the cited section, but there's no
        Code provided for the __init__ method to look up the text of
        the passage the user is trying to select.
        """
        selector = TextQuoteSelector(prefix="method of operation,")
        with pytest.raises(AttributeError):
            _ = Enactment(source="/us/usc/t17/s102/b", selector=selector)

    def test_section_text_from_path_and_regime(self, make_regime):
        copyright_exceptions = Enactment(
            source="/us/usc/t17/s102/b", regime=make_regime
        )
        assert copyright_exceptions.text.startswith(
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
        data = {"text": "process, system,|method of operation|, concept, principle"}
        selector = references.read_selector(data)
        schema = get_schema_for_item(selector)
        assert isinstance(schema, SelectorSchema)

    def test_dump_selector(self):
        """
        Uses text from "path": "/us/usc/t17/s102/b", but
        no longer includes a reference to the path.
        """

        data = {"text": "process, system,|method of operation|, concept, principle"}
        selector = references.read_selector(data)
        selector_dict = to_dict(selector)
        assert isinstance(selector_dict, dict)
        assert selector_dict["prefix"].startswith("process, system")

    def test_string_dump_selector(self):
        data = {"text": "process, system,|method of operation|, concept, principle"}
        selector = references.read_selector(data)
        selector_str = to_json(selector)
        assert isinstance(selector_str, str)
        assert '"prefix": "process, system' in selector_str
