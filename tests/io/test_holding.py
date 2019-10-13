import json

import pint
import pytest

from authorityspoke.enactments import Code, Enactment
from authorityspoke.entities import Entity
from authorityspoke.facts import Fact
from authorityspoke.holdings import Holding
from authorityspoke.opinions import Opinion
from authorityspoke.predicates import Predicate
from authorityspoke.procedures import Procedure
from authorityspoke.io import readers, dump, name_index
from authorityspoke.io.loaders import load_holdings
from authorityspoke.io import filepaths
from authorityspoke.rules import Rule
from authorityspoke.selectors import TextQuoteSelector

from marshmallow import ValidationError

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
        expanded = name_index.recursively_expand_shorthand(self.smith_holdings)
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
        lotus_holdings = load_holdings("holding_lotus.json", regime=make_regime)
        assert len(lotus_holdings) == 10

    def test_holding_without_enactments_or_regime(self):
        holding = {
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
        built = readers.read_holding(holding)
        new_factor = built.outputs[0].to_effect.context_factors[0]
        assert new_factor.name == "Bradley"

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
        built = readers.read_holdings(holdings)
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
        built = readers.read_holdings(holdings)
        allegation = built[0].inputs[1]
        assert allegation.statement.context_factors[0].name == "defendant"

    def test_enactment_has_subsection(self, make_opinion_with_holding):
        lotus = make_opinion_with_holding["lotus_majority"]
        assert lotus.holdings[8].enactments[0].source.split("/")[-1] == "b"

    def test_enactment_text_limited_to_subsection(self, make_opinion_with_holding):
        lotus = make_opinion_with_holding["lotus_majority"]
        assert "architectural works" not in str(lotus.holdings[8].enactments[0])

    @pytest.mark.xfail
    def test_imported_holding_same_as_test_object(self, real_holding, make_opinion):
        """
        These objects were once the same, but now the JSON treats
        "lived at" at "operated" as separate Factors.
        """

        watt = make_opinion["watt_majority"]
        watt.posit(load_holdings("holding_watt.json"))
        assert watt.holdings[0] == real_holding["h1"]

    def test_same_enactment_objects_equal(self, make_opinion_with_holding):
        """
        Don't expect the holdings imported from the JSON to
        exactly match the holdings created for testing in conftest.
        """
        watt = make_opinion_with_holding["watt_majority"]
        assert watt.holdings[0].enactments[0] == watt.holdings[1].enactments[0]

    def test_different_enactments_same_code(self, make_opinion_with_holding):
        """
        Don't expect the holdings imported from the JSON to
        exactly match the holdings created for testing in conftest.
        """
        lotus = make_opinion_with_holding["lotus_majority"]
        assert (
            lotus.holdings[0].enactments[0].code == lotus.holdings[1].enactments[0].code
        )
        assert (
            lotus.holdings[0].enactments[0].code is lotus.holdings[1].enactments[0].code
        )

    def test_same_enactment_in_two_opinions(self, make_opinion_with_holding):
        watt = make_opinion_with_holding["watt_majority"]
        brad = make_opinion_with_holding["brad_majority"]
        assert any(
            watt.holdings[0].enactments[0].means(brad_enactment)
            for brad_enactment in brad.holdings[0].enactments
        )

    def test_same_object_for_enactment_in_import(self, make_opinion_with_holding):
        """
        The JSON for Bradley repeats identical fields to create the same Factor
        for multiple Rules, instead of using the "name" field as a shortcut.
        This tests whether the loaded objects turn out equal.
        """
        brad = make_opinion_with_holding["brad_majority"]
        assert any(brad.holdings[6].inputs[0] == x for x in brad.holdings[5].inputs)

    def test_fact_from_loaded_holding(self, make_regime):
        to_read = load_holdings("holding_watt.json", regime=make_regime)
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
        assert "dimensionless" not in str(brad.holdings[6])
        assert isinstance(brad.holdings[6].inputs[0].predicate.quantity, int)

    def test_opinion_posits_holding(self, make_opinion, make_regime):
        brad = make_opinion["brad_majority"]
        to_read = load_holdings("holding_brad.json")
        holdings = readers.read_holdings(to_read, regime=make_regime)
        brad.posit(holdings)
        assert "warrantless search and seizure" in str(brad.holdings[0])

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
        holding_string = str(watt.holdings[-1])
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
        to_read = load_holdings("holding_brad.json", regime=make_regime)
        holdings = readers.read_holdings(to_read, regime=make_regime)
        brad.posit(holdings)
        context_holding = brad.holdings[6].new_context(
            {brad.holdings[6].generic_factors[0]: make_entity["watt"]}
        )
        # resetting holdings because of class scope of fixture
        watt.holdings = []
        watt.posit(context_holding)
        string = str(context_holding)
        assert "<Wattenburg> lived at <Bradley's house>" in string
        assert "<Wattenburg> lived at <Bradley's house>" in str(watt.holdings[0])

    def test_holding_with_non_generic_value(
        self, make_opinion, make_regime, make_entity
    ):
        """
        This test originally required a ValueError, but why should it?
        """
        brad = make_opinion["brad_majority"]
        to_read = load_holdings("holding_brad.json", regime=make_regime)
        holdings = readers.read_holdings(to_read, regime=make_regime)
        brad.posit(holdings)
        context_change = brad.holdings[6].new_context(
            {brad.holdings[6].generic_factors[1]: make_entity["trees_specific"]}
        )
        string = str(context_change)
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

    def test_holding_flagged_exclusive(self, make_opinion_with_holding, make_enactment):
        """
        Test that "exclusive" flag doesn't mess up the holding where it's placed.

        Test whether the Feist opinion object includes a holding
        with the output "Rural's telephone directory
        was copyrightable" and the input "Rural's telephone
        directory was original", when that holding was marked
        "exclusive" in the JSON.
        """

        directory = Entity("Rural's telephone directory")
        original = Fact(Predicate("{} was an original work"), directory)
        copyrightable = Fact(Predicate("{} was copyrightable"), directory)
        originality_enactments = [
            make_enactment["securing_for_authors"],
            make_enactment["right_to_writings"],
            make_enactment["copyright_requires_originality"],
        ]
        originality_rule = Rule(
            outputs=copyrightable,
            inputs=original,
            mandatory=False,
            universal=False,
            enactments=originality_enactments,
        )
        assert any(
            feist_holding.rule.means(originality_rule)
            for feist_holding in make_opinion_with_holding["feist_majority"].holdings
        )

    def test_holding_inferred_from_exclusive(
        self, make_enactment, make_opinion_with_holding
    ):
        """
        Test whether the Feist opinion object includes a holding
        that was inferred from an entry in the JSON saying that the
        "exclusive" way to reach the output "Rural's telephone directory
        was copyrightable" is to have the input "Rural's telephone
        directory was original".

        The inferred holding says that in the absence of the input
        "Rural's telephone directory was original", the court MUST
        ALWAYS find the output to be absent as well.
        """

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
        feist = make_opinion_with_holding["feist_majority"]
        assert feist.holdings[4].rule.means(no_originality_rule)

    def test_exclusive_results_in_more_holdings(self, make_opinion_with_holding):
        """
        Test that a holding inferred due to the "exclusive" flag
        is created in addition to all the other holdings, so there
        is one more holding than there are entries in the "holdings"
        section of the JSON.
        """

        with open(
            filepaths.get_directory_path("holdings") / "holding_feist.json", "r"
        ) as f:
            feist_json = json.load(f)
        assert (
            len(make_opinion_with_holding["feist_majority"].holdings)
            == len(feist_json["holdings"]) + 1
        )


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
        cardenas_holdings = load_holdings("holding_cardenas.json", regime=make_regime)
        assert len(cardenas_holdings) == 2
