import pytest

from authorityspoke.enactments import Code, Enactment
from authorityspoke.entities import Entity, Event, Human
from authorityspoke.factors import Predicate, Factor, Fact
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

    def test_failed_prefix(self, make_code):
        usc17 = make_code["usc17"]
        with pytest.raises(ValueError):
            copyright_exceptions = TextQuoteSelector(
                path="/us/usc/t17/s102/b", prefix="sound recordings", source=usc17
            )

    def test_failed_suffix(self, make_code):
        usc17 = make_code["usc17"]
        with pytest.raises(ValueError):
            copyright_exceptions = TextQuoteSelector(
                path="/us/usc/t17/s102/b", suffix="sound recordings", source=usc17
            )
