import copy

import os
import pytest

from dotenv import load_dotenv
from legislice.download import Client
from authorityspoke.nettlesome.terms import ContextRegister
from authorityspoke.nettlesome.entities import Entity
from authorityspoke.nettlesome.predicates import Predicate

from authorityspoke.examples import brad as brad_example
from authorityspoke.examples import feist as feist_example
from authorityspoke.examples import lotus as lotus_example
from authorityspoke.examples import watt as watt_example
from authorityspoke.facts import Fact, AbsenceOfFactor
from authorityspoke.holdings import Holding
from authorityspoke.opinions import (
    HoldingWithAnchors,
    OpinionReading,
    AnchoredHoldings,
)
from authorityspoke.procedures import Procedure
from authorityspoke.io.loaders import load_holdings
from authorityspoke.rules import Rule

load_dotenv()

TOKEN = os.getenv("LEGISLICE_API_TOKEN")
legislice_client = Client(api_token=TOKEN)


class TestHoldingDump:
    def test_dump_and_read_holding(self, fake_usc_client, make_holding):
        """Dump holding and read it as if it came from YAML."""
        holding = make_holding["h2"]
        dumped = holding.model_dump()
        content = dumped["rule"]["procedure"]["inputs"][0]["predicate"]["content"]
        assert content == "{thing} was on the premises of {place}"

        loaded = Holding(**dumped)
        loaded_content = loaded.despite[0].predicate.content
        assert "the distance between {place1} and {place2} was" in loaded_content

    def test_dump_and_load_holding(self, fake_usc_client, make_holding):
        """Dump holding and load it as if it was a JSON API response."""
        holding = make_holding["h2"]
        dumped = holding.model_dump()
        content = dumped["rule"]["procedure"]["inputs"][1]["predicate"]["content"]
        assert content == "{thing} was a stockpile of Christmas trees"
        loaded = Holding(**dumped)
        loaded_content = loaded.inputs[0].predicate.content
        assert "{thing} was on the premises of {place}" in loaded_content


class TestHoldingImport:
    client = Client(api_token=TOKEN)

    def test_import_some_holdings(self):
        """
        Now generates 10, instead of 12, because the "exclusive" Holding
        is stored with that flag instead of generating Holdings that it
        implies.
        """
        lotus_holdings = load_holdings("holding_lotus.yaml")
        assert len(lotus_holdings) == 10


class TestTextAnchors:
    client = Client(api_token=TOKEN)

    def test_read_holding_with_no_anchor(self, make_analysis):
        reading = OpinionReading()
        reading.posit(
            holdings=make_analysis["no anchors"],
        )
        assert not reading.holding_anchors[0].positions
        assert not reading.holding_anchors[0].quotes

    def test_enactment_text_limited_to_subsection(self, make_response):
        holdings = copy.deepcopy(list(lotus_example.HOLDINGS))
        assert "architectural works" not in str(holdings[8].enactments[0])

    @pytest.mark.xfail
    def test_imported_holding_same_as_test_object(self, real_holding, make_opinion):
        """
        These objects were once the same, but now the JSON treats
        "lived at" at "operated" as separate Factors.
        """

        watt = make_opinion["watt_majority"]
        watt.posit(load_holdings("holding_watt.yaml"))
        assert watt.holdings[0] == real_holding["h1"]

    def test_same_enactment_objects_equal(self, make_response):
        """
        Don't expect the holdings imported from the JSON to
        exactly match the holdings created for testing in conftest.
        """
        holdings = copy.deepcopy(list(watt_example.HOLDINGS))
        assert holdings[0].enactments[0].means(holdings[1].enactments[0])

    def test_same_enactment_in_two_opinions(self, make_response):
        brad_holdings = copy.deepcopy(list(brad_example.HOLDINGS))
        watt_holdings = copy.deepcopy(list(watt_example.HOLDINGS))

        assert any(
            watt_holdings[0].enactments[0].means(brad_enactment)
            for brad_enactment in brad_holdings[0].enactments
        )

    def test_same_object_for_enactment_in_import(self, make_response):
        """
        The JSON for Bradley repeats identical fields to create the same Factor
        for multiple Rules, instead of using the "name" field as a shortcut.
        This tests whether the loaded objects turn out equal.
        """
        holdings = copy.deepcopy(list(brad_example.HOLDINGS))
        assert any(holdings[6].inputs[0].means(x) for x in holdings[5].inputs)

    def test_fact_from_loaded_holding(self, make_response):
        holdings = copy.deepcopy(list(watt_example.HOLDINGS))
        new_fact = holdings[0].inputs[1]
        assert "lived at <Hideaway Lodge>" in str(new_fact)
        assert isinstance(new_fact.terms[0], Entity)

    def test_fact_with_quantity(self, make_response):
        holdings = copy.deepcopy(list(watt_example.HOLDINGS))
        new_fact = holdings[1].inputs[3]
        assert "was no more than 35 foot" in str(new_fact)

    def test_use_int_not_pint_without_dimension(self, make_response):
        loaded_holdings = copy.deepcopy(list(brad_example.HOLDINGS))
        anchored_holdings = AnchoredHoldings(
            holdings=[HoldingWithAnchors(holding=item) for item in loaded_holdings]
        )
        reading = OpinionReading(anchored_holdings=anchored_holdings)
        expectation_not_reasonable = list(reading.holdings)[6]
        assert "dimensionless" not in str(expectation_not_reasonable)
        assert expectation_not_reasonable.inputs[0].predicate.quantity == 3

    def test_opinion_posits_holding(self, make_response):
        holdings = copy.deepcopy(list(brad_example.HOLDINGS))
        reading = OpinionReading()
        reading.posit(holdings[0])
        assert "warrantless search and seizure" in reading.holdings[0].short_string

    def test_opinion_posits_holding_tuple_context(self, make_entity, make_response):
        """
        Having the Watt case posit a holding from the Brad
        case, but with generic factors from Watt.
        """
        brad_holdings = copy.deepcopy(list(brad_example.HOLDINGS))
        context_holding = brad_holdings[6].new_context(
            [make_entity["watt"], make_entity["trees"], make_entity["motel"]]
        )
        reading = OpinionReading()
        reading.posit(context_holding)
        holding_string = reading.holdings[-1].short_string
        assert (
            "the number of marijuana plants in <the stockpile of trees> was at least 3"
            in holding_string
        )

    def test_opinion_posits_holding_dict_context(self, make_entity, make_response):
        """
        Having the Watt case posit a holding from the Brad
        case, but replacing one generic factor with a factor
        from Watt.
        """
        holdings = copy.deepcopy(list(brad_example.HOLDINGS))
        breading = OpinionReading()
        breading.clear_holdings()
        breading.posit(holdings)
        expectation_not_reasonable = breading.holdings[6]
        changes = ContextRegister()
        changes.insert_pair(
            key=expectation_not_reasonable.generic_terms()[0],
            value=make_entity["watt"],
        )
        context_holding = expectation_not_reasonable.new_context(changes)
        wreading = OpinionReading()
        wreading.clear_holdings()
        wreading.posit(context_holding)
        string = str(context_holding)
        assert "<Wattenburg> lived at <Bradley's house>" in string
        assert "<Wattenburg> lived at <Bradley's house>" in str(wreading.holdings[-1])

    def test_holding_with_non_generic_value(self, make_entity, make_response):
        """
        This test originally required a ValueError, but why should it?
        """
        reading = OpinionReading()
        holdings = copy.deepcopy(list(brad_example.HOLDINGS))
        reading.posit(holdings)
        expectation_not_reasonable = reading.holdings[6]
        generic_patch = expectation_not_reasonable.generic_terms()[1]
        changes = ContextRegister()
        changes.insert_pair(generic_patch, make_entity["trees_specific"])
        context_change = expectation_not_reasonable.new_context(changes)
        string = context_change.short_string
        assert "plants in the stockpile of trees was at least 3" in string

    def test_posit_holding_with_selector(self, make_analysis, make_opinion):
        anchored_holding = make_analysis["minimal"][0]

        brad = make_opinion["brad_majority"]
        reading = OpinionReading(opinion_type="majority", opinion_author=brad.author)
        reading.posit(anchored_holding)
        assert reading.holding_anchors[0].quotes[0].exact == "open fields or grounds"


class TestExclusiveFlag:
    client = Client(api_token=TOKEN)

    @pytest.mark.xfail
    def test_holding_inferred_from_exclusive(self, make_enactment, make_response):
        """
        Test whether the Feist opinion object includes a holding
        that was inferred from an entry in the JSON saying that the
        "exclusive" way to reach the output "Rural's telephone directory
        was copyrightable" is to have the input "Rural's telephone
        directory was original".

        The inferred holding says that in the absence of the input
        "Rural's telephone directory was original", the court MUST
        ALWAYS find the output to be absent as well.

        Marked xfail because the "exclusive" flag no longer causes
        inferred Holdings to be expanded. Instead, it now should generate
        inferred Rules that aren't expanded during data loading.
        """
        feist_holdings = copy.deepcopy(list(feist_example.HOLDINGS))

        directory = Entity(name="Rural's telephone directory")
        not_original = AbsenceOfFactor(
            absent=Fact(Predicate(content="{} was an original work"), directory)
        )
        not_copyrightable = AbsenceOfFactor(
            absent=Fact(Predicate(content="{} was copyrightable"), directory)
        )
        no_originality_procedure = Procedure(
            outputs=not_copyrightable, inputs=not_original
        )
        no_originality_rule = Rule(
            no_originality_procedure,
            mandatory=True,
            universal=True,
            enactments=[
                make_enactment["securing_for_authors"],
                make_enactment["right_to_writings"],
                make_enactment["copyright_requires_originality"],
            ],
        )
        assert feist_holdings[4].rule.means(no_originality_rule)
