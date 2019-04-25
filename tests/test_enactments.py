import datetime
import json
import operator

from pint import UnitRegistry
import pytest

from authorityspoke.entities import Human, Event
from authorityspoke.enactments import Code, Enactment
from authorityspoke.factors import Predicate, Factor, Entity, Fact
from authorityspoke.opinions import Opinion
from authorityspoke.factors import ureg, Q_


class TestCodes:
    def test_making_code(self, make_code):
        const = make_code["const"]
        assert str(const) == "Constitution of the United States"

    def test_make_cfr(self, make_code):
        cfr = make_code["cfr37"]
        assert str(cfr) == "Code of Federal Regulations Title 37"

    def test_get_bill_of_rights_effective_date(self, make_code):
        const = make_code["const"]
        bill_of_rights_date = datetime.date(1791, 12, 15)
        assert const.provision_effective_date("amendment-V") == bill_of_rights_date

    def test_get_14th_A_effective_date(self, make_code):
        const = make_code["const"]
        equal_protection_date = datetime.date(1868, 7, 28)
        assert const.provision_effective_date("amendment-XIV") == equal_protection_date

    def test_uslm_code(self, make_code):
        usc17 = make_code["usc17"]
        assert usc17.title == "USC Title 17"


class TestEnactments:
    def test_make_enactment(self, make_enactment):
        search_clause = make_enactment["search_clause"]
        assert search_clause.text.endswith("shall not be violated")

    def test_passage_from_uslm_code(self, make_code):
        usc17 = make_code["usc17"]
        copyright_exceptions = Enactment(
            usc17, section="102", subsection="b", end="extend to any"
        )
        assert copyright_exceptions.text == (
            "In no case does copyright protection "
            + "for an original work of authorship extend to any"
        )

    def test_passage_from_imported_statute(self, make_code):
        opinion_generator = Opinion.from_file(f'oracle_h.json')
        opinion = next(opinion_generator)
        oracle_majority = opinion.exposit(f'holding_oracle.json')
        despite_text = str(oracle_majority.holdings[5])
        assert 'DESPITE: "In no case does copyright protection ' in despite_text

    def test_short_passage_from_uslm_code(self, make_code):
        usc17 = make_code["usc17"]
        method = Enactment(
            usc17,
            section="102",
            subsection="b",
            start="method of operation",
            end="method of operation",
        )
        assert method.text == "method of operation"

    def test_passage_from_cfr_code(self, make_code):
        cfr = make_code["cfr37"]
        slogans = Enactment(cfr, section=202.1, end="names, titles, and slogans")
        assert "Words and short phrases such as names" in slogans.text

    def test_code_title_in_str(self, make_enactment):
        assert "secure in their persons" in str(make_enactment["search_clause"])

    def test_equal_enactment_text(self, make_enactment):
        assert make_enactment["due_process_5"] == make_enactment["due_process_14"]
        assert not make_enactment["due_process_5"] > make_enactment["due_process_14"]

    def test_unequal_enactment_text(self, make_enactment):
        assert make_enactment["search_clause"] != make_enactment["fourth_a"]

    def test_enactment_subset(self, make_enactment):
        assert make_enactment["search_clause"] < make_enactment["fourth_a"]

    def test_enactment_subset_or_equal(self, make_enactment):
        assert make_enactment["due_process_5"] >= make_enactment["due_process_14"]

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

    def test_bill_of_rights_effective_date(self, make_enactment):
        # December 15, 1791
        assert make_enactment["search_clause"].effective_date == datetime.date(
            1791, 12, 15
        )

    def test_14th_A_effective_date(self, make_enactment):
        # July 28, 1868
        assert make_enactment["due_process_14"].effective_date == datetime.date(
            1868, 7, 28
        )

    def test_compare_effective_dates(self, make_enactment):
        dp5 = make_enactment["due_process_5"]
        dp14 = make_enactment["due_process_14"]
        assert dp14.effective_date > dp5.effective_date
