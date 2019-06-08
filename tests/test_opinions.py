import json
import pytest

from authorityspoke.enactments import Code, Enactment
from authorityspoke.factors import Entity, Evidence, Exhibit
from authorityspoke.rules import Procedure, Rule, ProceduralRule
from authorityspoke.opinions import Opinion
from authorityspoke.predicates import ureg, Q_
from authorityspoke.context import log_mentioned_context


class TestOpinions:
    def test_load_opinion_in_Harvard_format(self):
        watt_dict = Opinion.from_file("watt_h.json")
        assert watt_dict.name_abbreviation == "Wattenburg v. United States"

    def test_load_generator_for_opinions(self):
        opinion_generator = Opinion.from_file("brad_h.json", lead_only=False)
        majority = next(opinion_generator)
        dissent = next(opinion_generator)
        assert dissent.position == "concurring-in-part-and-dissenting-in-part"

    def test_opinion_features(self, make_opinion):
        assert make_opinion["watt_majority"].court == "9th-cir"
        assert "388 F.2d 853" in make_opinion["watt_majority"].citations

    def test_opinion_author(self, make_opinion):
        assert make_opinion["watt_majority"].author == "HAMLEY, Circuit Judge"
        assert make_opinion["brad_majority"].author == "BURKE, J."
        assert (
            make_opinion["brad_concurring-in-part-and-dissenting-in-part"].author
            == "TOBRINER, J."
        )

    def test_opinion_holding_list(
        self, make_opinion, real_holding, make_evidence, make_entity
    ):
        watt = make_opinion["watt_majority"]
        h = real_holding
        e = make_entity
        h3_specific = h["h3"]
        watt.posit(h3_specific)
        assert h3_specific in watt.holdings

    def test_opinion_entity_list(
        self, make_opinion, real_holding, make_entity, make_evidence
    ):
        watt = make_opinion["watt_majority"]
        h = real_holding
        e = make_entity

        watt.posit(h["h1"], (e["motel"], e["watt"]))
        watt.posit(h["h2"], (e["trees"], e["motel"]))
        watt.posit(
            h["h3"],
            (
                make_evidence["generic"],
                e["motel"],
                e["watt"],
                e["trees"],
                e["tree_search"],
            ),
        )
        watt.posit(h["h4"], (e["trees"], e["tree_search"], e["motel"], e["watt"]))
        assert make_entity["watt"] in make_opinion["watt_majority"].generic_factors

    def test_opinion_date(self, make_opinion):
        assert (
            make_opinion["watt_majority"].decision_date
            < make_opinion["brad_majority"].decision_date
        )
        assert (
            make_opinion["brad_majority"].decision_date
            == make_opinion[
                "brad_concurring-in-part-and-dissenting-in-part"
            ].decision_date
        )

    def test_positing_non_rule_error(self, make_opinion, make_procedure):
        with pytest.raises(TypeError):
            make_opinion["watt_majority"].posit(make_procedure["c1"])

    def test_new_context_non_iterable_changes(self, make_opinion, make_holding):
        """
        The context here (a Factor outside an iterable) only changes the first
        generic factor of the Rule being posited, which may not be what the user
        expects.
        """
        brad = make_opinion["brad_majority"]
        brad.posit(make_holding["h1"], context=Entity("House on Haunted Hill"))
        assert "Haunted Hill" in str(brad.holdings[0])

    def test_new_context_naming_nonexistent_factor(self, make_opinion, make_holding):
        """
        The context here (a Factor outside an iterable) only changes the first
        generic factor of the Rule being posited, which may not be what the user
        expects.
        """
        brad = make_opinion["brad_majority"]
        with pytest.raises(ValueError):
            brad.posit(
                make_holding["h1"],
                context=(Entity("House on Haunted Hill"), "nonexistent factor"),
            )

    def test_new_context_creates_equal_rule(self, make_opinion, make_regime):
        watt = make_opinion["watt_majority"]
        brad = make_opinion["brad_majority"]
        watt_holdings = Rule.from_json(f"holding_watt.json", regime=make_regime)
        brad_holdings = Rule.from_json(f"holding_brad.json", regime=make_regime)
        for holding in watt_holdings:
            watt.posit(holding)
        for holding in brad_holdings:
            brad.posit(holding)
        context_pairs = {
            "proof of Bradley's guilt": "proof of Wattenburg's guilt",
            "Bradley": "Wattenburg",
            "officers' search of the yard": "officers' search of the stockpile",
            "Bradley's marijuana patch": "the stockpile of trees",
        }
        watt.posit(brad.holdings[0], context_pairs)
        assert watt.holdings[-1].means(brad.holdings[0])

    def test_new_context_inferring_factors_to_change(self, make_opinion, make_regime):
        """
        This changes watt's holdings; may break tests below.
        """

        watt = make_opinion["watt_majority"]
        brad = make_opinion["brad_majority"]
        watt.holdings = []
        brad.holdings = []
        watt_holdings = Rule.from_json(f"holding_watt.json", regime=make_regime)
        brad_holdings = Rule.from_json(f"holding_brad.json", regime=make_regime)
        for holding in watt_holdings:
            watt.posit(holding)
        for holding in brad_holdings:
            brad.posit(holding)

        context_items = [
            "proof of Wattenburg's guilt",
            "Wattenburg",
            "officers' search of the stockpile",
            "Hideaway Lodge",
            "the stockpile of trees",
        ]
        watt.posit(brad.holdings[0], context_items)
        assert watt.holdings[-1].means(brad.holdings[0])

    # Implication

    def test_no_implication(self, make_opinion_with_holding):
        watt = make_opinion_with_holding["watt_majority"]
        brad = make_opinion_with_holding["brad_majority"]
        assert not watt >= brad

    def test_posit_list_of_holdings_and_imply(self, make_opinion, make_regime):
        watt = make_opinion["watt_majority"]
        brad = make_opinion["brad_majority"]
        some_rules = Rule.from_json("holding_watt.json", regime=make_regime)
        for case in (watt, brad):
            case.holdings = []
            case.posit(some_rules[:3])
        watt.posit(some_rules[3])
        assert watt > brad
        assert not brad >= watt

    def test_opinion_implies_rule(self, make_opinion, make_holding):
        watt = make_opinion["watt_majority"]
        watt.holdings = [make_holding["h2_invalid_undecided"]]
        assert watt >= make_holding["h2_undecided"]
        assert watt > make_holding["h2_undecided"]

    def test_opinion_does_not_imply_rule(self, make_opinion, make_holding):
        watt = make_opinion["watt_majority"]
        watt.holdings = [make_holding["h2_irrelevant_inputs_undecided"]]
        assert not watt >= make_holding["h2_undecided"]
        assert not watt > make_holding["h2_undecided"]
