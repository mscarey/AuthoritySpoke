from authorityspoke.enactments import Code, Enactment
from authorityspoke.entities import Entity, Event, Human
from authorityspoke.factors import Predicate, Factor, Fact
from authorityspoke.factors import Evidence, Exhibit
from authorityspoke.rules import Procedure, Rule, ProceduralRule
from authorityspoke.opinions import Opinion
from authorityspoke.selectors import TextQuoteSelector

class TestSelectors:

    def test_code_from_selector(self, make_code, make_selector):
        code = make_code.get_code(make_selector["/us/usc/t17/s103"])
        assert code.uri == "/us/usc/t17"

    def test_usc_selection(self, make_code, make_selector):
        selector = make_selector["/us/usc/t17/s103"]
        code = make_code.get_code(selector.path)
        enactment = Enactment(code, selector)
        assert enactment.code.level == "statute"
        assert enactment.code.jurisdiction_id == "us"
