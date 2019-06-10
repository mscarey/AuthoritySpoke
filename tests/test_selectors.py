import pytest

from authorityspoke.enactments import Code, Enactment
from authorityspoke.factors import Predicate, Entity, Factor, Fact
from authorityspoke.factors import Evidence, Exhibit
from authorityspoke.rules import Procedure, Rule, ProceduralRule
from authorityspoke.opinions import Opinion
from authorityspoke.selectors import TextQuoteSelector


class TestSelectors:
    def test_code_from_selector(self, make_regime, make_selector):
        code = make_regime.get_code(make_selector["/us/usc/t17/s103"])
        assert code.uri == "/us/usc/t17"

    def test_usc_selection(self, make_regime, make_selector):
        selector = make_selector["/us/usc/t17/s103"]
        code = make_regime.get_code(selector.path)
        enactment = Enactment(code=code, selector=selector)
        assert enactment.code.level == "statute"
        assert enactment.code.jurisdiction == "us"

    def test_omit_terminal_slash(self, make_code):
        usc17 = make_code["usc17"]
        selector = TextQuoteSelector(
            path="us/usc/t17/s102/b/",
            prefix="process, system,",
            suffix=", concept, principle",
            source=usc17,
        )
        assert not selector.path.endswith("/")

    def test_add_omitted_initial_slash(self, make_code):
        usc17 = make_code["usc17"]
        selector = TextQuoteSelector(
            path="us/usc/t17/s102/b",
            prefix="process, system,",
            suffix=", concept, principle",
            source=usc17,
        )
        assert selector.path.startswith("/")

    def test_passage_from_uslm_code(self, make_code):
        usc17 = make_code["usc17"]
        copyright_exceptions = TextQuoteSelector(
            path="/us/usc/t17/s102/b", suffix="idea, procedure,", source=usc17
        )
        assert copyright_exceptions.exact.strip() == (
            "In no case does copyright protection "
            + "for an original work of authorship extend to any"
        )

    def test_convert_selector_to_json(self, make_code):
        usc17 = make_code["usc17"]
        copyright_exceptions = TextQuoteSelector(
            path="/us/usc/t17/s102/b", suffix="idea, procedure,", source=usc17
        )
        assert '"exact": "In no case does copyright' in copyright_exceptions.json

    def test_failed_prefix(self, make_code):
        usc17 = make_code["usc17"]
        with pytest.raises(ValueError):
            copyright_exceptions = TextQuoteSelector(
                path="/us/usc/t17/s102/b", prefix="sound recordings", source=usc17
            )

    def test_fail_no_exact_or_source(self, make_code):
        usc17 = make_code["usc17"]
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
        due_process_wrong_section = TextQuoteSelector(
            path="/us/const/amendment-XV/1", exact="due process"
        )
        enactment = Enactment(selector=due_process_wrong_section, regime=make_regime)
        with pytest.raises(ValueError):
            print(enactment.text)
