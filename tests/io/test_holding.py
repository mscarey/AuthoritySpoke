from collections import OrderedDict
from datetime import date
import os
from pydantic import ValidationError
import pytest

from anchorpoint.textselectors import TextQuoteSelector
from dotenv import load_dotenv
from legislice import Enactment
from legislice.download import Client
from nettlesome.terms import ContextRegister
from nettlesome.entities import Entity
from nettlesome.predicates import Predicate

from authorityspoke.decisions import Decision, DecisionReading
from authorityspoke.facts import Fact
from authorityspoke.holdings import Holding, HoldingGroup
from authorityspoke.opinions import (
    HoldingWithAnchors,
    Opinion,
    OpinionReading,
    AnchoredHoldings,
)
from authorityspoke.procedures import Procedure
from authorityspoke.io import loaders, readers, name_index
from authorityspoke.io.fake_enactments import FakeClient
from authorityspoke.io.loaders import load_holdings, read_holdings_from_file
from authorityspoke.io import filepaths, text_expansion
from authorityspoke.rules import Rule

load_dotenv()

TOKEN = os.getenv("LEGISLICE_API_TOKEN")
legislice_client = Client(api_token=TOKEN)


class TestHoldingDump:
    def test_dump_and_read_holding(self, fake_usc_client, make_holding):
        """Dump holding and read it as if it came from YAML."""
        holding = make_holding["h2"]
        dumped = holding.dict()
        content = dumped["rule"]["procedure"]["inputs"][0]["predicate"]["content"]
        assert content == "$thing was on the premises of $place"

        loaded = readers.read_holdings([dumped], client=fake_usc_client)
        loaded_content = loaded[0].despite[0].predicate.content
        assert "the distance between $place1 and $place2 was" in loaded_content

    def test_dump_and_load_holding(self, fake_usc_client, make_holding):
        """Dump holding and load it as if it was a JSON API response."""
        holding = make_holding["h2"]
        dumped = holding.dict()
        content = dumped["rule"]["procedure"]["inputs"][1]["predicate"]["content"]
        assert content == "$thing was a stockpile of Christmas trees"
        loaded = Holding(**dumped)
        loaded_content = loaded.inputs[0].predicate.content
        assert "$thing was on the premises of $place" in loaded_content

    def test_dump_holdings_with_comparison(self, fake_usc_client):

        holdings = read_holdings_from_file("holding_watt.yaml", client=fake_usc_client)
        assert "was no more than 35 foot" in str(holdings[1])
        dumped = holdings[1].dict()
        predicate = dumped["rule"]["procedure"]["inputs"][3]["predicate"]
        assert predicate["quantity_range"]["quantity"] == "35 foot"


class TestEntityImport:

    smith_holdings = [
        {
            "inputs": [
                {
                    "type": "fact",
                    "content": "{} stole a car",
                    "terms": {
                        "type": "Entity",
                        "name": "Smith",
                        "generic": False,
                    },
                }
            ],
            "outputs": [{"type": "fact", "content": "Smith committed theft"}],
        },
        {
            "inputs": [{"type": "fact", "content": "{Smythe} stole a car"}],
            "outputs": [{"type": "fact", "content": "Smythe committed theft"}],
        },
    ]

    def test_index_names_from_otherwise_identical_factors(self):
        expanded, mentioned = name_index.index_names(self.smith_holdings)
        fact = mentioned[expanded[1]["inputs"][0]]
        assert fact["terms"][0] == "Smythe"

    def test_specific_entity(self):

        different_entity_holdings = readers.read_holdings(self.smith_holdings)
        assert (
            different_entity_holdings[1].generic_terms
            != different_entity_holdings[0].generic_terms
        )
        assert not different_entity_holdings[1] >= different_entity_holdings[0]


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

    def test_import_enactments_and_anchors(
        self, make_opinion_with_holding, make_response
    ):
        """
        Testing issue that caused enactment expansion to fail only when
        text anchors were loaded.
        """
        raw_holdings = [
            {
                "inputs": {
                    "type": "fact",
                    "content": "{Rural's telephone directory} was a fact",
                    "name": "Rural's telephone directory was a fact",
                    "anchors": {
                        "quotes": [
                            {"exact": "facts", "prefix": "The first is that"},
                            {
                                "exact": "as to facts",
                                "prefix": "No one may claim originality",
                            },
                            {"exact": "facts", "prefix": "no one may copyright"},
                        ]
                    },
                },
                "outputs": {
                    "type": "fact",
                    "content": "Rural's telephone directory was copyrightable",
                    "truth": False,
                    "anchors": {
                        "quotes": [
                            {
                                "exact": "copyrightable",
                                "prefix": "first is that facts are not",
                            },
                            "The sine qua non of|copyright|",
                            {"exact": "no one may copyright", "suffix": "facts"},
                        ]
                    },
                },
                "enactments": [
                    {
                        "name": "securing for authors",
                        "enactment": {
                            "node": "/us/const/article/I/8/8",
                            "exact": (
                                "To promote the Progress of Science and useful Arts, "
                                "by securing for limited Times to Authors"
                            ),
                        },
                    },
                    {
                        "name": "right to writings",
                        "enactment": {
                            "node": "/us/const/article/I/8/8",
                            "exact": "the exclusive Right to their respective Writings",
                        },
                    },
                ],
                "mandatory": True,
                "universal": True,
            },
            {
                "outputs": {
                    "type": "fact",
                    "content": "Rural's telephone directory was copyrightable",
                },
                "enactments": ["securing for authors", "right to writings"],
                "mandatory": True,
                "anchors": {"quotes": ["compilations of facts|generally are|"]},
            },
        ]
        mock_client = FakeClient(responses=make_response)
        f_anchored_holdings = readers.read_holdings_with_anchors(
            record=raw_holdings, client=mock_client
        )

        feist = make_opinion_with_holding["feist_majority"]
        feist.clear_holdings()
        feist.posit(
            f_anchored_holdings.holdings,
            named_anchors=f_anchored_holdings.named_anchors,
            enactment_anchors=f_anchored_holdings.enactment_anchors,
        )
        assert feist.holdings[0].enactments[0].node == "/us/const/article/I/8/8"
        assert feist.holdings[1].enactments[0].node == "/us/const/article/I/8/8"

    def test_read_holdings_and_then_get_anchors(self, make_response):
        """
        Test whether read_holdings mutates raw_holding and makes it
        impossible to get text anchors.
        """
        mock_client = FakeClient(responses=make_response)
        raw_holdings = load_holdings("holding_oracle.yaml")
        loaded = readers.read_holdings_with_anchors(raw_holdings, client=mock_client)

        assert isinstance(loaded.holdings[0], HoldingWithAnchors)
        assert isinstance(loaded.named_anchors[1].anchors.quotes[0], TextQuoteSelector)

    def test_load_and_posit_holdings_with_anchors(self, make_response):
        """
        Test that Opinion.posit can take a HoldingsIndexed as the only argument.
        Trying to combine several tasks that normally happen together, into a single command.
        """
        mock_client = FakeClient(responses=make_response)
        oracle_holdings_with_anchors = loaders.read_anchored_holdings_from_file(
            "holding_oracle.yaml", client=mock_client
        )
        reading = OpinionReading()
        reading.posit(oracle_holdings_with_anchors)
        assert len(reading.holdings) == 20

    def test_decision_posits_holdings_with_anchors(self, make_response):
        mock_client = FakeClient(responses=make_response)
        oracle_holdings_with_anchors = loaders.read_anchored_holdings_from_file(
            "holding_oracle.yaml", client=mock_client
        )
        reading = DecisionReading(decision=Decision(decision_date=date(2019, 1, 1)))
        reading.posit(oracle_holdings_with_anchors)
        assert len(reading.holdings) == 20

    def test_pass_holdings_to_decision_reading_constructor(
        self, make_decision, make_response
    ):
        mock_client = FakeClient(responses=make_response)
        oracle = make_decision["oracle"]
        oracle_holdings = read_holdings_from_file(
            "holding_oracle.yaml", client=mock_client
        )
        oracle_reading = DecisionReading(decision=oracle)
        oracle_reading.posit(oracle_holdings)
        assert (
            oracle_reading.opinion_readings[0].holdings[0].enactments[0].node
            == "/us/usc/t17/s102/a"
        )


class TestTextAnchors:
    client = Client(api_token=TOKEN)

    def test_read_holding_with_no_anchor(self, make_analysis):
        raw_analysis = make_analysis["no anchors"]
        reading = OpinionReading()
        anchored_holdings = readers.read_holdings_with_anchors(raw_analysis)
        reading.posit(
            holdings=anchored_holdings.holdings,
            named_anchors=anchored_holdings.named_anchors,
            enactment_anchors=anchored_holdings.enactment_anchors,
        )
        assert not reading.holding_anchors[0].positions
        assert not reading.holding_anchors[0].quotes

    def test_holding_without_enactments_or_regime(self, raw_holding):
        expanded = text_expansion.expand_shorthand(raw_holding["bradley_house"])
        built = readers.read_holdings([expanded])
        new_factor = built[0].outputs[0].to_effect.terms[0]
        assert new_factor.name == "Bradley"

    def test_posit_one_holding_with_anchor(self, raw_holding, make_response):
        mock_client = FakeClient(responses=make_response)
        holdings = readers.read_holdings(
            [raw_holding["bradley_house"]], client=mock_client
        )
        reading = OpinionReading()
        reading.posit_holding(
            holdings[0],
            holding_anchors=TextQuoteSelector(
                exact="some text supporting this holding"
            ),
        )
        assert (
            reading.anchored_holdings.holdings[-1].anchors.quotes[0].exact
            == "some text supporting this holding"
        )

    def test_mentioned_context_changing(self):
        """
        The "mentioned" context should not change while data
        is being loaded with the schema. This is to test
        that the "content" field of a value in the "mentioned"
        dict isn't changed to replace the name of a Factor
        with bracketed text.
        """
        holdings = [
            {
                "inputs": {
                    "type": "fact",
                    "content": "{Bradley} lived at Bradley's house",
                },
                "outputs": {
                    "type": "evidence",
                    "exhibit": {"offered_by": {"type": "entity", "name": "the People"}},
                    "to_effect": {
                        "type": "fact",
                        "name": "fact that Bradley committed a crime",
                        "content": "Bradley committed a crime",
                    },
                    "name": "evidence of Bradley's guilt",
                    "absent": True,
                },
            },
            {
                "inputs": "fact that Bradley committed a crime",
                "outputs": {"type": "fact", "content": "Bradley committed a tort"},
            },
        ]
        expanded = text_expansion.expand_shorthand(holdings)
        built = readers.read_holdings(expanded)
        new_factor = built[0].outputs[0].to_effect.terms[0]
        assert new_factor.name == "Bradley"

    def test_holdings_with_allegation_and_exhibit(self):
        """
        Testing the error message:
        The number of items in 'terms' must be 1,
        to match predicate.context_slots for '{} committed
        an attempted robbery' for 'fact that defendant
        committed an attempted robbery'

        This was another bug involving mutation of the "mentioned" context object
        during deserialization.

        Fixed by having FactSchema.get_references_from_mentioned call
        add_found_context with deepcopy(obj) instead of obj for the
        "factor" parameter
        """
        holdings = [
            {
                "inputs": [
                    {
                        "type": "Exhibit",
                        "name": "officer's testimony that defendant was addicted to heroin",
                        "form": "testimony",
                        "offered_by": {
                            "type": "Entity",
                            "name": "The People of California",
                        },
                        "statement": {
                            "type": "Fact",
                            "name": "fact that defendant was addicted to heroin",
                            "content": "the {defendant} was addicted to heroin",
                        },
                        "statement_attribution": {
                            "type": "entity",
                            "name": "parole officer",
                        },
                    },
                    {
                        "type": "Allegation",
                        "name": "the attempted robbery charge",
                        "pleading": {
                            "type": "Pleading",
                            "filer": {
                                "type": "Entity",
                                "name": "The People of California",
                            },
                        },
                        "fact": {
                            "type": "Fact",
                            "name": "fact that defendant committed an attempted robbery",
                            "content": "defendant committed an attempted robbery",
                        },
                    },
                ],
                "despite": [
                    {
                        "type": "Fact",
                        "content": "officer's testimony that defendant was addicted to heroin, was relevant to show the defendant had a motive to commit an attempted robbery",
                    }
                ],
                "outputs": [
                    {
                        "type": "Fact",
                        "content": "the probative value of officer's testimony that defendant was addicted to heroin, in indicating fact that defendant committed an attempted robbery, was outweighed by unfair prejudice to defendant",
                    }
                ],
                "mandatory": True,
            },
            {
                "inputs": [
                    {
                        "type": "Fact",
                        "content": "the probative value of officer's testimony that defendant was addicted to heroin, in indicating fact that defendant committed an attempted robbery, was outweighed by unfair prejudice to defendant",
                    }
                ],
                "despite": [
                    {
                        "type": "Fact",
                        "content": "officer's testimony that defendant was addicted to heroin was relevant to show defendant had a motive to commit an attempted robbery",
                    }
                ],
                "outputs": [
                    {
                        "type": "Evidence",
                        "name": "evidence of officer's testimony that defendant was addicted to heroin",
                        "exhibit": "officer's testimony that defendant was addicted to heroin",
                        "to_effect": "fact that defendant committed an attempted robbery",
                        "absent": True,
                    }
                ],
                "mandatory": True,
            },
        ]
        expanded = text_expansion.expand_shorthand(holdings)
        built = readers.read_holdings(expanded)
        allegation = built[0].inputs[1]
        assert allegation.fact.terms[0].name == "defendant"

    def test_select_enactment_text_by_default(self, make_response):
        mock_client = FakeClient(responses=make_response)
        holding_dict = {
            "outputs": [
                {
                    "type": "fact",
                    "content": "the Lotus menu command hierarchy was copyrightable",
                }
            ],
            "enactments": {"enactment": {"node": "/us/usc/t17/s410/c"}},
        }
        holding = readers.read_holdings([holding_dict], client=mock_client)
        assert holding[0].enactments[0].selected_text().startswith("In any judicial")

    def test_enactment_has_subsection(self, make_response):
        mock_client = FakeClient(responses=make_response)
        to_read = load_holdings("holding_lotus.yaml")
        holdings = readers.read_holdings(to_read, client=mock_client)
        assert holdings[8].enactments[0].node.split("/")[-1] == "b"

    def test_enactment_text_limited_to_subsection(self, make_response):
        mock_client = FakeClient(responses=make_response)
        to_read = load_holdings("holding_lotus.yaml")
        holdings = readers.read_holdings(to_read, client=mock_client)
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
        mock_client = FakeClient(responses=make_response)
        to_read = load_holdings("holding_watt.yaml")
        holdings = readers.read_holdings(to_read, client=mock_client)
        assert holdings[0].enactments[0].means(holdings[1].enactments[0])

    def test_same_enactment_in_two_opinions(self, make_response):
        mock_client = FakeClient(responses=make_response)
        to_read = load_holdings("holding_brad.yaml")
        brad_holdings = readers.read_holdings(to_read, client=mock_client)

        to_read = load_holdings("holding_watt.yaml")
        watt_holdings = readers.read_holdings(to_read, client=mock_client)

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
        mock_client = FakeClient(responses=make_response)
        to_read = load_holdings("holding_brad.yaml")
        holdings = readers.read_holdings(to_read, client=mock_client)
        assert any(holdings[6].inputs[0].means(x) for x in holdings[5].inputs)

    def test_fact_from_loaded_holding(self, make_response):
        to_read = load_holdings("holding_watt.yaml")
        mock_client = FakeClient(responses=make_response)
        holdings = readers.read_holdings(to_read, client=mock_client)
        new_fact = holdings[0].inputs[1]
        assert "lived at <Hideaway Lodge>" in str(new_fact)
        assert isinstance(new_fact.terms[0], Entity)

    def test_fact_with_quantity(self, make_response):
        to_read = load_holdings("holding_watt.yaml")
        mock_client = FakeClient(responses=make_response)
        holdings = readers.read_holdings(to_read, client=mock_client)
        new_fact = holdings[1].inputs[3]
        assert "was no more than 35 foot" in str(new_fact)

    def test_use_int_not_pint_without_dimension(self, make_response):
        mock_client = FakeClient(responses=make_response)
        to_read = load_holdings("holding_brad.yaml")
        loaded_holdings = readers.read_holdings(to_read, client=mock_client)
        anchored_holdings = AnchoredHoldings(
            holdings=[HoldingWithAnchors(holding=item) for item in loaded_holdings]
        )
        reading = OpinionReading(anchored_holdings=anchored_holdings)
        expectation_not_reasonable = list(reading.holdings)[6]
        assert "dimensionless" not in str(expectation_not_reasonable)
        assert expectation_not_reasonable.inputs[0].predicate.quantity == 3

    def test_opinion_posits_holding(self, make_response):
        mock_client = FakeClient(responses=make_response)
        to_read = load_holdings("holding_brad.yaml")
        holdings = readers.read_holdings(to_read, client=mock_client)
        reading = OpinionReading()
        reading.posit(holdings[0])
        assert "warrantless search and seizure" in reading.holdings[0].short_string

    def test_opinion_posits_holding_tuple_context(self, make_entity, make_response):
        """
        Having the Watt case posit a holding from the Brad
        case, but with generic factors from Watt.
        """
        mock_client = FakeClient(responses=make_response)
        to_read = load_holdings("holding_brad.yaml")
        brad_holdings = readers.read_holdings(to_read, client=mock_client)
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
        mock_client = FakeClient(responses=make_response)
        to_read = load_holdings("holding_brad.yaml")
        holdings = readers.read_holdings(to_read, client=mock_client)
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
        mock_client = FakeClient(responses=make_response)
        reading = OpinionReading()
        to_read = load_holdings("holding_brad.yaml")
        holdings = readers.read_holdings(to_read, client=mock_client)
        reading.posit(holdings)
        expectation_not_reasonable = reading.holdings[6]
        generic_patch = expectation_not_reasonable.generic_terms()[1]
        changes = ContextRegister()
        changes.insert_pair(generic_patch, make_entity["trees_specific"])
        context_change = expectation_not_reasonable.new_context(changes)
        string = context_change.short_string
        assert "plants in the stockpile of trees was at least 3" in string

    def test_error_because_string_does_not_match_factor_name(self, make_response):
        rule_holding = {
            "inputs": ["this factor hasn't been mentioned"],
            "outputs": [{"type": "fact", "content": "{the dog} bit {the man}"}],
            "enactments": [{"enactment": {"node": "/us/const/amendment/IV"}}],
            "mandatory": True,
        }
        mock_client = FakeClient(responses=make_response)
        with pytest.raises(ValidationError):
            readers.read_holdings([rule_holding], client=mock_client)

    def test_error_classname_does_not_exist(self):
        rule_dict = {
            "inputs": [
                {
                    "type": "RidiculousFakeClassName",
                    "content": "officers' search of the yard was a warrantless search and seizure",
                }
            ],
            "outputs": [{"type": "fact", "content": "the dog bit the man"}],
        }
        with pytest.raises(ValidationError):
            readers.read_holdings([rule_dict])

    def test_repeating_read_holdings_has_same_result(self, make_analysis):
        raw = make_analysis["minimal"]
        holdings = readers.read_holdings_with_anchors(raw).holdings
        holdings_again = readers.read_holdings_with_anchors(raw).holdings
        assert all(
            left.holding.means(right.holding)
            for left, right in zip(holdings, holdings_again)
        )

    def test_posit_holding_with_selector(self, make_analysis, make_opinion):

        anchored_holdings = readers.read_holdings_with_anchors(make_analysis["minimal"])

        brad = make_opinion["brad_majority"]
        reading = OpinionReading(opinion_type="majority", opinion_author=brad.author)
        reading.posit(anchored_holdings.holdings)
        assert reading.holding_anchors[0].quotes[0].exact == "open fields or grounds"


class TestExclusiveFlag:
    client = Client(api_token=TOKEN)

    def test_holding_flagged_exclusive(
        self,
        e_securing_exclusive_right_to_writings,
        e_copyright_requires_originality,
        make_response,
    ):
        """
        Test that "exclusive" flag doesn't mess up the holding where it's placed.

        Test whether the Feist opinion object includes a holding
        with the output "Rural's telephone directory
        was copyrightable" and the input "Rural's telephone
        directory was original", when that holding was marked
        "exclusive" in the JSON.

        `originality_rule` will be a little broader because it's based on
        less Enactment text
        """
        fake_client = FakeClient(responses=make_response)
        holdings = read_holdings_from_file("holding_feist.yaml", client=fake_client)

        directory = Entity(name="Rural's telephone directory")
        original = Fact(
            predicate=Predicate(content="$work was an original work"), terms=directory
        )
        copyrightable = Fact(
            predicate=Predicate(content="$work was copyrightable"), terms=directory
        )
        originality_enactments = [
            e_securing_exclusive_right_to_writings,
            e_copyright_requires_originality,
        ]
        originality_rule = Rule(
            procedure=Procedure(outputs=copyrightable, inputs=original),
            mandatory=False,
            universal=False,
            enactments=originality_enactments,
        )
        assert any(
            originality_rule.implies(feist_holding.rule) for feist_holding in holdings
        )

    def test_fact_containing_wrong_type(self, make_response):
        mock_client = FakeClient(responses=make_response)
        to_read = load_holdings("holding_feist.yaml")
        to_read[0]["outputs"]["type"] = "wrong_type"
        with pytest.raises(ValidationError):
            readers.read_holdings([to_read[0]], client=mock_client)

    def test_type_field_removed_from_factor(self, make_response):
        mock_client = FakeClient(responses=make_response)
        to_read = load_holdings("holding_feist.yaml")
        holdings = readers.read_holdings([to_read[0]], client=mock_client)
        assert holdings[0].inputs[0].__dict__.get("type") is None

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
        mock_client = FakeClient(responses=make_response)
        to_read = load_holdings("holding_feist.yaml")
        feist_holdings = readers.read_holdings(to_read["holdings"], client=mock_client)

        directory = Entity(name="Rural's telephone directory")
        not_original = Fact(
            Predicate(content="{} was an original work"), directory, absent=True
        )
        not_copyrightable = Fact(
            Predicate(content="{} was copyrightable"), directory, absent=True
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

    def test_exclusive_does_not_result_in_more_holdings(self, make_response):
        """
        The intended behavior is now for the Holding to assert that
        its Rule is the "exclusive" way to reach the outputs, and
        to have an additional function that can generate additional
        Rules that can be inferred from the exclusive flag.

        "Implies" and "contradict" methods will be able to look at the Holding's
        generated Rules as well as its original Rule.
        """
        mock_client = FakeClient(responses=make_response)
        feist_json = load_holdings("holding_feist.yaml")
        feist_holdings = readers.read_holdings(feist_json, client=mock_client)

        assert len(feist_holdings) == len(feist_json)


class TestNestedFactorImport:
    def test_import_holding(self, make_response):
        """
        Based on this text:
        This testimony tended “only remotely” to prove that appellant
        had committed the attempted robbery of money from the 7-Eleven
        store. In addition, the probative value of the evidence was
        substantially outweighed by the inflammatory effect of the
        testimony on the jury. Hence, admission of the testimony
        concerning appellant’s use of narcotics was improper.
        """
        mock_client = FakeClient(responses=make_response)
        cardenas_dict = load_holdings("holding_cardenas.yaml")
        cardenas_holdings = readers.read_holdings(cardenas_dict, client=mock_client)
        assert len(cardenas_holdings) == 2
