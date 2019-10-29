from collections import OrderedDict

from marshmallow import ValidationError
import pint
import pytest

from authorityspoke.enactments import Code, Enactment
from authorityspoke.entities import Entity
from authorityspoke.facts import Fact
from authorityspoke.holdings import Holding
from authorityspoke.opinions import Opinion
from authorityspoke.predicates import Predicate
from authorityspoke.procedures import Procedure
from authorityspoke.io import anchors, loaders, readers, dump, name_index
from authorityspoke.io.loaders import load_holdings
from authorityspoke.io import filepaths, text_expansion
from authorityspoke.rules import Rule
from authorityspoke.selectors import TextQuoteSelector

ureg = pint.UnitRegistry()


class TestHoldingDump:
    def test_dump_holding(self, make_holding):
        holding = make_holding["h2"]
        dumped = dump.to_dict(holding)
        content = dumped["rule"]["procedure"]["inputs"][0]["predicate"]["content"]
        assert content == "{} was on the premises of {}"

    def test_dump_and_read_rule(self, make_holding, make_regime):
        holding = make_holding["h2"]
        dumped = dump.to_dict(holding)
        loaded = readers.read_holding(dumped, regime=make_regime)
        content = loaded.despite[0].predicate.content
        assert "the distance between {} and {} was" in content


class TestEntityImport:
    smith_holdings = [
        {
            "inputs": [
                {
                    "type": "fact",
                    "content": "{} stole a car",
                    "context_factors": {
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

    def test_expand_shorthand(self):
        expanded = text_expansion.expand_shorthand(self.smith_holdings)
        fact = expanded[1]["inputs"][0]
        assert fact["context_factors"][0]["name"] == "Smythe"

    def test_specific_entity(self):

        different_entity_holdings = readers.read_holdings(self.smith_holdings)
        assert (
            different_entity_holdings[1].generic_factors
            != different_entity_holdings[0].generic_factors
        )
        assert not different_entity_holdings[1] >= different_entity_holdings[0]


class TestHoldingImport:
    def test_import_some_holdings(self, make_regime):
        """
        Now generates 10, instead of 12, because the "exclusive" Holding
        is stored with that flag instead of generating Holdings that it
        implies.
        """
        lotus_holdings = load_holdings("holding_lotus.json")
        assert len(lotus_holdings) == 10

    def test_import_enactments_and_anchors(self, make_regime, make_opinion):
        """
        Testing issue that caused enactment expansion to fail only when
        text anchors were loaded.
        """
        raw_holdings = [
            {
                "inputs": {
                    "type": "fact",
                    "content": "{Rural's telephone directory} was a fact",
                    "anchors": [
                        {"exact": "facts", "prefix": "The first is that"},
                        {
                            "exact": "as to facts",
                            "prefix": "No one may claim originality",
                        },
                        {"exact": "facts", "prefix": "no one may copyright"},
                    ],
                },
                "outputs": {
                    "type": "fact",
                    "content": "Rural's telephone directory was copyrightable",
                    "truth": False,
                    "anchors": [
                        {
                            "exact": "are not copyrightable",
                            "prefix": "The first is that facts",
                        },
                        {"exact": "no one may copyright", "suffix": "facts"},
                    ],
                },
                "enactments": [
                    {
                        "source": "/us/const/article-I/8/8",
                        "exact": ("To promote the Progress of Science and useful Arts, "
                        "by securing for limited Times to Authors"),
                        "name": "securing for authors",
                    },
                    {
                        "source": "/us/const/article-I/8/8",
                        "exact": "the exclusive Right to their respective Writings",
                        "name": "right to writings",
                    },
                ],
                "mandatory": True,
                "universal": True,
            },
            {
                "outputs": {
                    "type": "fact",
                    "content": "Rural's telephone directory was copyrightable",
                    "anchors": [
                        {
                            "exact": "copyrightable",
                            "prefix": "first is that facts are not",
                        },
                        "The sine qua non of|copyright|",
                    ],
                },
                "enactments": ["securing for authors", "right to writings"],
                "mandatory": True,
                "anchors": "compilations of facts|generally are|",
            },
        ]
        holding_anchors = anchors.get_holding_anchors(raw_holdings)
        named_anchors = anchors.get_named_anchors(raw_holdings)
        feist_holdings = readers.read_holdings(
            raw_holdings, regime=make_regime
        )
        feist = make_opinion["feist_majority"]
        feist.posit(feist_holdings, holding_anchors=holding_anchors, named_anchors=named_anchors)
        assert feist.holdings[0].enactments[0].name == "securing for authors"
        assert feist.holdings[1].enactments[0].name == "securing for authors"


    def test_read_holdings_and_then_get_anchors(self, make_regime):
        """
        Test whether read_holdings mutates raw_holding and makes it
        impossible to get text anchors.
        """
        raw_holdings = load_holdings(f"holding_oracle.json")
        oracle_holdings = readers.read_holdings(
            raw_holdings, regime=make_regime
        )
        named_anchors = anchors.get_named_anchors(raw_holdings)

        assert isinstance(oracle_holdings[0], Holding)
        assert isinstance(named_anchors.popitem()[1].pop(), TextQuoteSelector)

class TestTextAnchors:
    one_holding = {
            "inputs": {"type": "fact", "content": "{Bradley} lived at Bradley's house"},
            "outputs": {
                "type": "evidence",
                "to_effect": {
                    "type": "fact",
                    "name": "fact that Bradley committed a crime",
                    "content": "Bradley committed a crime",
                },
                "name": "evidence of Bradley's guilt",
                "absent": True,
            },
        }

    def test_read_holding_with_no_anchor(self, make_opinion, make_analysis):
        oracle = make_opinion["oracle_majority"]
        raw_analysis = make_analysis["no anchors"]
        oracle_holdings = readers.read_holdings(raw_analysis)
        holding_anchors = anchors.get_holding_anchors(raw_analysis)
        named_anchors = anchors.get_named_anchors(raw_analysis)
        oracle.posit(oracle_holdings, holding_anchors=holding_anchors, named_anchors=named_anchors)
        has_no_anchors = oracle.holdings[0]
        assert oracle.holding_anchors[has_no_anchors] == []


    def test_holding_without_enactments_or_regime(self):

        expanded = text_expansion.expand_shorthand(self.one_holding)
        built = readers.read_holding(expanded)
        new_factor = built.outputs[0].to_effect.context_factors[0]
        assert new_factor.name == "Bradley"

    def test_posit_one_holding_with_anchor(self, make_opinion):
        expanded = text_expansion.expand_shorthand(self.one_holding)
        cardenas = make_opinion["cardenas_majority"]
        anchor_list = anchors.get_holding_anchors(expanded)
        holding = readers.read_holding(expanded)
        cardenas.posit(holding, holding_anchors=anchor_list)

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
        new_factor = built[0].outputs[0].to_effect.context_factors[0]
        assert new_factor.name == "Bradley"

    def test_holdings_with_allegation_and_exhibit(self):
        """
        Testing the error message:
        The number of items in 'context_factors' must be 1,
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
                        "statement": {
                            "type": "Fact",
                            "name": "fact that defendant was addicted to heroin",
                            "content": "the {defendant} was addicted to heroin",
                        },
                        "stated_by": {"type": "entity", "name": "parole officer"},
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
                        "statement": {
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
                        "content": "the probative value of officer's testimony that defendant was addicted to heroin, in showing fact that defendant committed an attempted robbery, was outweighed by unfair prejudice to defendant",
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
        assert allegation.statement.context_factors[0].name == "defendant"

    def test_enactment_has_subsection(self, make_regime):
        to_read = load_holdings("holding_lotus.json")
        holdings = readers.read_holdings(to_read, regime=make_regime)
        assert holdings[8].enactments[0].source.split("/")[-1] == "b"

    def test_enactment_text_limited_to_subsection(self, make_regime):
        to_read = load_holdings("holding_lotus.json")
        holdings = readers.read_holdings(to_read, regime=make_regime)
        assert "architectural works" not in str(holdings[8].enactments[0])

    @pytest.mark.xfail
    def test_imported_holding_same_as_test_object(self, real_holding, make_opinion):
        """
        These objects were once the same, but now the JSON treats
        "lived at" at "operated" as separate Factors.
        """

        watt = make_opinion["watt_majority"]
        watt.posit(load_holdings("holding_watt.json"))
        assert watt.holdings[0] == real_holding["h1"]

    def test_same_enactment_objects_equal(self, make_regime):
        """
        Don't expect the holdings imported from the JSON to
        exactly match the holdings created for testing in conftest.
        """
        to_read = load_holdings("holding_watt.json")
        holdings = readers.read_holdings(to_read, regime=make_regime)
        assert holdings[0].enactments[0] == holdings[1].enactments[0]

    def test_different_enactments_same_code(self, make_regime):
        """
        Don't expect the holdings imported from the JSON to
        exactly match the holdings created for testing in conftest.
        """
        to_read = load_holdings("holding_lotus.json")
        holdings = readers.read_holdings(to_read, regime=make_regime)
        assert holdings[0].enactments[0].code == holdings[1].enactments[0].code
        assert holdings[0].enactments[0].code is holdings[1].enactments[0].code

    def test_same_enactment_in_two_opinions(self, make_regime):
        to_read = load_holdings("holding_watt.json")
        watt_holdings = readers.read_holdings(to_read, regime=make_regime)

        to_read = load_holdings("holding_brad.json")
        brad_holdings = readers.read_holdings(to_read, regime=make_regime)

        assert any(
            watt_holdings[0].enactments[0].means(brad_enactment)
            for brad_enactment in brad_holdings[0].enactments
        )

    def test_same_object_for_enactment_in_import(self, make_regime):
        """
        The JSON for Bradley repeats identical fields to create the same Factor
        for multiple Rules, instead of using the "name" field as a shortcut.
        This tests whether the loaded objects turn out equal.
        """
        to_read = load_holdings("holding_brad.json")
        holdings = readers.read_holdings(to_read, regime=make_regime)
        assert any(holdings[6].inputs[0] == x for x in holdings[5].inputs)

    def test_fact_from_loaded_holding(self, make_regime):
        to_read = load_holdings("holding_watt.json")
        holdings = readers.read_holdings(to_read, regime=make_regime)
        new_fact = holdings[0].inputs[1]
        assert "lived at <Hideaway Lodge>" in str(new_fact)
        assert isinstance(new_fact.context_factors[0], Entity)

    def test_fact_with_quantity(self, make_regime):
        to_read = load_holdings("holding_watt.json")
        holdings = readers.read_holdings(to_read, regime=make_regime)
        new_fact = holdings[1].inputs[3]
        assert "was no more than 35 foot" in str(new_fact)

    def test_use_int_not_pint_without_dimension(self, make_regime, make_opinion):

        brad = make_opinion["brad_majority"]
        to_read = load_holdings("holding_brad.json")
        holdings = readers.read_holdings(to_read, regime=make_regime)
        brad.posit(holdings)
        expectation_not_reasonable = list(brad.holdings)[6]
        assert "dimensionless" not in str(expectation_not_reasonable)
        assert isinstance(expectation_not_reasonable.inputs[0].predicate.quantity, int)

    def test_opinion_posits_holding(self, make_opinion, make_regime):
        brad = make_opinion["brad_majority"]
        to_read = load_holdings("holding_brad.json")
        holdings = readers.read_holdings(to_read, regime=make_regime)
        brad.posit(holdings)
        assert "warrantless search and seizure" in brad.holdings[0].short_string

    def test_opinion_posits_holding_tuple_context(
        self, make_opinion, make_regime, make_entity
    ):
        """
        Having the Watt case posit a holding from the Brad
        case, but with generic factors from Watt.
        """
        to_read = load_holdings("holding_brad.json")
        brad_holdings = readers.read_holdings(to_read, regime=make_regime)
        context_holding = brad_holdings[6].new_context(
            [make_entity["watt"], make_entity["trees"], make_entity["motel"]]
        )
        watt = make_opinion["watt_majority"]
        watt.posit(context_holding)
        holding_string = watt.holdings[-1].short_string
        assert (
            "the number of marijuana plants in <the stockpile of trees> was at least 3"
            in holding_string
        )

    def test_opinion_posits_holding_dict_context(
        self, make_opinion, make_regime, make_entity
    ):
        """
        Having the Watt case posit a holding from the Brad
        case, but replacing one generic factor with a factor
        from Watt.
        """
        watt = make_opinion["watt_majority"]
        brad = make_opinion["brad_majority"]
        to_read = load_holdings("holding_brad.json")
        holdings = readers.read_holdings(to_read, regime=make_regime)
        brad.posit(holdings)
        expectation_not_reasonable = brad.holdings[6]
        context_holding = expectation_not_reasonable.new_context(
            {expectation_not_reasonable.generic_factors[0]: make_entity["watt"]}
        )

        watt.posit(context_holding)
        string = str(context_holding)
        assert "<Wattenburg> lived at <Bradley's house>" in string
        assert "<Wattenburg> lived at <Bradley's house>" in str(watt.holdings[-1])

    def test_holding_with_non_generic_value(
        self, make_opinion, make_regime, make_entity
    ):
        """
        This test originally required a ValueError, but why should it?
        """
        brad = make_opinion["brad_majority"]
        to_read = load_holdings("holding_brad.json")
        holdings = readers.read_holdings(to_read, regime=make_regime)
        brad.posit(holdings)
        expectation_not_reasonable = brad.holdings[6]
        generic_patch = expectation_not_reasonable.generic_factors[1]
        context_change = expectation_not_reasonable.new_context(
            {generic_patch: make_entity["trees_specific"]}
        )
        string = context_change.short_string
        assert "plants in the stockpile of trees was at least 3" in string

    def test_error_because_string_does_not_match_factor_name(self, make_regime):
        rule_holding = {
            "inputs": ["this factor hasn't been mentioned"],
            "outputs": [{"type": "fact", "content": "{the dog} bit {the man}"}],
            "enactments": [{"source": "/us/const/amendment-IV"}],
            "mandatory": True,
        }
        with pytest.raises(ValidationError):
            readers.read_holding(rule_holding, regime=make_regime)

    def test_error_classname_does_not_exist(self):
        rule_dict = {
            "inputs": [
                {
                    "type": "RidiculousFakeClassName",
                    "content": "officers' search of the yard was a warrantless search and seizure",
                }
            ],
            "outputs": [{"type": "fact", "content": "the dog bit the man"}],
            "enactments": [{"source": "/us/const/amendment-IV"}],
        }
        with pytest.raises(ValueError):
            readers.read_holding(rule_dict)

    def test_repeating_read_holdings_has_same_result(self, make_analysis):
        raw = make_analysis["minimal"]
        holdings_and_anchors = [
            readers.read_holdings(raw),
            anchors.get_holding_anchors(raw),
            anchors.get_named_anchors(raw)]
        holdings_and_anchors_again = [
            readers.read_holdings(raw),
            anchors.get_holding_anchors(raw),
            anchors.get_named_anchors(raw)]
        assert all(
            left == right
            for left, right
            in zip(holdings_and_anchors, holdings_and_anchors_again))


    def test_posit_holding_with_selector(self, make_analysis, make_opinion):

        holdings = readers.read_holdings(make_analysis["minimal"])
        holding_anchors = anchors.get_holding_anchors(make_analysis["minimal"])
        brad = make_opinion["brad_majority"]
        brad.posit(holdings, holding_anchors=holding_anchors)
        assert brad.holding_anchors[holdings[0]][0].exact == "we hold"

class TestExclusiveFlag:
    def test_holding_flagged_exclusive(self, make_regime, make_enactment):
        """
        Test that "exclusive" flag doesn't mess up the holding where it's placed.

        Test whether the Feist opinion object includes a holding
        with the output "Rural's telephone directory
        was copyrightable" and the input "Rural's telephone
        directory was original", when that holding was marked
        "exclusive" in the JSON.
        """
        to_read = load_holdings("holding_feist.json")
        feist_holdings = readers.read_holdings(to_read, regime=make_regime)

        directory = Entity("Rural's telephone directory")
        original = Fact(Predicate("{} was an original work"), directory)
        copyrightable = Fact(Predicate("{} was copyrightable"), directory)
        originality_enactments = [
            make_enactment["securing_for_authors"],
            make_enactment["right_to_writings"],
            make_enactment["copyright_requires_originality"],
        ]
        originality_rule = Rule(Procedure(
            outputs=copyrightable,
            inputs=original),
            mandatory=False,
            universal=False,
            enactments=originality_enactments,
        )
        assert any(
            feist_holding.rule.means(originality_rule)
            for feist_holding in feist_holdings
        )

    @pytest.mark.xfail
    def test_holding_inferred_from_exclusive(self, make_enactment, make_regime):
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
        to_read = load_holdings("holding_feist.json")
        feist_holdings = readers.read_holdings(to_read, regime=make_regime)

        directory = Entity("Rural's telephone directory")
        not_original = Fact(
            Predicate("{} was an original work"), directory, absent=True
        )
        not_copyrightable = Fact(
            Predicate("{} was copyrightable"), directory, absent=True
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

    def test_exclusive_does_not_result_in_more_holdings(self, make_regime):
        """
        The intended behavior is now for the Holding to assert that
        its Rule is the "exclusive" way to reach the outputs, and
        to have an additional function that can generate additional
        Rules that can be inferred from the exclusive flag.

        "Implies" and "contradict" methods will be able to look at the Holding's
        generated Rules as well as its original Rule.
        """
        feist_json = load_holdings("holding_feist.json")
        feist_holdings = readers.read_holdings(feist_json, regime=make_regime)

        assert len(feist_holdings) == len(feist_json)


class TestNestedFactorImport:
    def test_import_holding(self, make_regime):
        """
        Based on this text:
        This testimony tended “only remotely” to prove that appellant
        had committed the attempted robbery of money from the 7-Eleven
        store. In addition, the probative value of the evidence was
        substantially outweighed by the inflammatory effect of the
        testimony on the jury. Hence, admission of the testimony
        concerning appellant’s use of narcotics was improper.
        """
        cardenas_json = load_holdings("holding_cardenas.json")
        cardenas_holdings = readers.read_holdings(cardenas_json, regime=make_regime)
        assert len(cardenas_holdings) == 2
