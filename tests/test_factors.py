import logging
import operator

import pytest

from authorityspoke.comparisons import ContextRegister
from authorityspoke.entities import Entity
from authorityspoke.factors import Factor, means, FactorSequence
from authorityspoke.facts import Fact, build_fact
from authorityspoke.rules import Rule
from authorityspoke.opinions import Opinion
from authorityspoke.predicates import Comparison, Q_, Predicate


class TestFacts:
    def test_default_terms_for_fact(self, make_entity, make_predicate, watt_mentioned):
        e = make_entity
        f1 = build_fact(make_predicate["p1"], case_factors=watt_mentioned)
        assert f1.terms == (e["motel"],)

    def test_build_fact(self, make_predicate, watt_mentioned):
        """
        Check that terms is created as a (hashable) tuple, not list
        """
        shooting = build_fact(
            make_predicate["p_shooting"],
            (2, 3),
            case_factors=watt_mentioned,
            standard_of_proof="preponderance of evidence",
        )
        assert isinstance(shooting.terms, tuple)

    def test_terms_from_case_factor_indices(
        self, make_entity, make_predicate, watt_mentioned
    ):
        """
        If you pass in integers instead of Factor objects to fill the blanks
        in the Predicate (which was the only way to do things in the first
        version of the Fact class's __init__ method), then the integers
        you pass in should be used as indices to select Factor objects
        from case_factors.
        """

        e = make_entity

        f2 = build_fact(
            make_predicate["p2"], indices=(1, 0), case_factors=watt_mentioned
        )
        assert f2.terms == (e["watt"], e["motel"])

    def test_correct_factors_from_indices_in_build_fact(
        self, make_entity, make_predicate, watt_mentioned
    ):
        e = make_entity
        f2 = build_fact(
            make_predicate["p2"],
            indices=(1, 2),
            case_factors=watt_mentioned,
        )
        assert f2.terms == (e["watt"], e["trees"])

    def test_wrong_type_in_terms_in_init(
        self, make_entity, make_predicate, watt_mentioned
    ):
        e = make_entity
        with pytest.raises(TypeError):
            f2 = build_fact(
                make_predicate["p1"],
                indices=("nonsense"),
                case_factors=watt_mentioned,
            )

    def test_invalid_index_for_case_factors_in_init(self, make_predicate, make_entity):
        with pytest.raises(IndexError):
            _ = build_fact(
                make_predicate["p1"],
                indices=2,
                case_factors=make_entity["watt"],
            )

    def test_convert_int_terms_to_tuple(self, make_predicate, watt_mentioned):
        f = build_fact(make_predicate["p_irrelevant_1"], 3, case_factors=watt_mentioned)
        assert f.terms == (watt_mentioned[3],)

    def test_string_representation_of_factor(self, watt_factor):
        assert "<Hideaway Lodge> was a motel" in str(watt_factor["f1"])
        assert "absence of the fact" in str(watt_factor["f3_absent"]).lower()

    def test_string_no_truth_value(self, watt_factor):
        factor = watt_factor["f2_no_truth"]
        assert "whether" in str(factor)

    def test_repeating_entity_string(self, make_factor):
        """I'm not convinced that a model of a Fact ever needs to include
        multiple references to the same Entity just because the name of the
        Entity appears more than once in the Predicate."""
        f = make_factor
        assert (
            "Fact that <Alice> told <Bob> to hire <Craig>".lower()
            in str(f["f_three_entities"]).lower()
        )
        assert (
            "Fact that <Alice> told <Bob> to hire <Alice>".lower()
            in str(f["f_repeating_entity"]).lower()
        )

    def test_string_representation_with_concrete_entities(self, watt_factor):
        """
        "Hideaway Lodge" is still a string representation of an Entity
        object, but it's not in angle brackets because it can't be
        replaced by another Entity object without changing the meaning
        of the Fact.
        """
        assert "Hideaway Lodge was a motel" in str(watt_factor["f1_specific"])

    def test_string_for_fact_with_identical_terms(self):
        devon = Entity("Devon", generic=True)
        elaine = Entity("Elaine", generic=True)
        opened_account = Fact(
            Predicate("$applicant opened a bank account for $applicant and $cosigner"),
            terms=(devon, elaine),
        )
        assert "<Devon> opened a bank account for <Devon> and <Elaine>" in str(
            opened_account
        )

    def test_str_with_concrete_context(self, make_opinion_with_holding):
        holding = list(make_opinion_with_holding["cardenas_majority"].holdings)[1]
        longer_str = holding.inputs[0].str_with_concrete_context
        assert "the Exhibit in the FORM testimony" in longer_str
        assert "the Exhibit in the FORM testimony" not in str(holding.inputs[0])

    def test_complex_fact_no_line_break_in_predicate(self, make_opinion_with_holding):
        """
        Tests that the string representation of this Holding's only input
        Fact does not contain indented new lines, except in the "SPECIFIC
        CONTEXT" part, if present.

        The representation of the Exhibit mentioned in the Fact should
        not introduce any indented lines inside the Fact's string.
        """
        holding = list(make_opinion_with_holding["cardenas_majority"].holdings)[1]
        fact_text = str(holding.inputs[0])
        if "SPECIFIC CONTEXT" in fact_text:
            fact_text = fact_text.split("SPECIFIC CONTEXT")[0].strip()
        assert "\n  " not in fact_text

    def test_new_context_replace_fact(self, make_entity, watt_factor):
        changes = ContextRegister.from_lists(
            [make_entity["watt"], watt_factor["f2"]],
            [Entity("Darth Vader"), watt_factor["f10"]],
        )
        assert "was within the curtilage of <Hideaway Lodge>" in (
            watt_factor["f2"].new_context(changes).short_string
        )

    def test_get_factor_from_recursive_search(self, make_opinion_with_holding):
        holding_list = list(make_opinion_with_holding["cardenas_majority"].holdings)
        factor_list = list(holding_list[0].recursive_factors.values())
        assert any(
            factor == Entity("parole officer") and factor.name == "parole officer"
            for factor in factor_list
        )

    def test_new_context_from_factor(self, watt_factor):
        different = watt_factor["f1"].new_context(
            Entity("Great Northern", generic=False)
        )
        assert "Great Northern was a motel" in str(different)

    def test_new_concrete_context(self, make_entity, watt_factor):
        register = ContextRegister.from_lists(
            keys=[make_entity["watt"], make_entity["motel"]],
            values=[Entity("Darth Vader"), Entity("Death Star")],
        )
        different = watt_factor["f2"].new_context(register)
        assert "<Darth Vader> operated" in str(different)

    def test_type_of_terms(self, watt_factor):
        assert isinstance(watt_factor["f1"].terms, FactorSequence)

    def test_concrete_to_abstract(self, make_entity, make_predicate):
        motel = make_entity["motel_specific"]
        d = make_entity["watt"]
        fact = Fact(predicate=make_predicate["p2"], terms=(d, motel))
        assert "<Wattenburg> operated and lived at Hideaway Lodge" in str(fact)
        assert "<Wattenburg> operated and lived at Hideaway Lodge>" in str(
            fact.make_generic()
        )

    def test_entity_slots_as_length_of_factor(self, watt_factor):
        assert len(watt_factor["f1"].predicate) == 1
        assert len(watt_factor["f1"]) == 1

    def test_predicate_with_entities(self, make_entity, watt_factor):
        assert "<Hideaway Lodge> was a motel" in watt_factor[
            "f1"
        ].predicate.content_with_terms((make_entity["motel"]))

    def test_factor_terms_do_not_match_predicate(self, make_predicate, watt_mentioned):
        """
        make_predicate["p1"] has only one slot for context factors, but
        this tells it to look for three.
        """
        with pytest.raises(ValueError):
            _ = build_fact(make_predicate["p1"], (0, 1, 2), case_factors=watt_mentioned)

    def test_reciprocal_with_wrong_number_of_entities(self, make_entity, watt_factor):
        with pytest.raises(ValueError):
            watt_factor["f1"].predicate.content_with_terms(
                (make_entity["motel"], make_entity["watt"])
            )

    def test_entity_and_human_in_predicate(self, make_entity, watt_factor):
        assert "<Wattenburg> operated and lived at <Hideaway Lodge>" in watt_factor[
            "f2"
        ].predicate.content_with_terms((make_entity["watt"], make_entity["motel"]))

    def test_standard_of_proof_must_be_listed(self, make_predicate, watt_mentioned):
        with pytest.raises(ValueError):
            _ = build_fact(
                make_predicate["p2"],
                case_factors=watt_mentioned,
                standard_of_proof="probably so",
            )

    def test_standard_of_proof_in_str(self, watt_factor):
        factor = watt_factor["f2_preponderance_of_evidence"]
        assert factor.standard_of_proof in factor.short_string

    def test_case_factors_deleted_from_fact(self, watt_factor):
        """This attribute should have been deleted during Fact.__post_init__"""
        predicate = Predicate("some things happened")
        factor = build_fact(predicate)
        assert not hasattr(factor, "case_factors")

    def test_repeated_placeholder_in_fact(self, make_opinion_with_holding):
        holding = make_opinion_with_holding["lotus_majority"].holdings[9]
        fact = holding.inputs[1]
        assert fact.short_string == (
            "the fact it was false that the precise formulation "
            "of <Lotus 1-2-3>'s code was necessary for <Lotus 1-2-3> to work"
        )
        assert len(fact.terms) == 1


class TestSameMeaning:
    def test_equality_factor_from_same_predicate(self, watt_factor):
        assert watt_factor["f1"].means(watt_factor["f1b"])

    def test_equality_factor_from_equal_predicate(self, watt_factor):
        assert watt_factor["f1"].means(watt_factor["f1c"])

    def test_equality_because_factors_are_generic_entities(self, watt_factor):
        assert watt_factor["f1"].means(watt_factor["f1_different_entity"])

    def test_unequal_because_a_factor_is_not_generic(self, watt_factor):
        assert not watt_factor["f9_swap_entities_4"].means(watt_factor["f9"])

    def test_generic_factors_equal(self, watt_factor):
        assert watt_factor["f2_generic"].means(watt_factor["f2_false_generic"])
        assert watt_factor["f2_generic"].means(watt_factor["f3_generic"])

    def test_equal_referencing_diffent_generic_factors(self, make_factor):
        assert make_factor["f_murder"].means(make_factor["f_murder_craig"])

    def test_generic_and_specific_factors_unequal(self, watt_factor):
        assert not watt_factor["f2"].means(watt_factor["f2_generic"])

    def test_factor_reciprocal_unequal(self, watt_factor):
        assert not watt_factor["f2"].means(watt_factor["f2_reflexive"])

    def test_factor_different_predicate_truth_unequal(self, watt_factor):
        assert not watt_factor["f7"].means(watt_factor["f7_opposite"])

    def test_unequal_because_one_factor_is_absent(self, watt_factor):
        assert not watt_factor["f8"].means(watt_factor["f8_absent"])

    def test_copies_of_identical_factor(self, make_factor):
        """
        Even if the two factors have different entity markers in self.terms,
        I expect them to evaluate equal because the choice of entity markers is
        arbitrary.
        """
        f = make_factor
        assert f["f_irrelevant_3"].means(f["f_irrelevant_3"])
        assert f["f_irrelevant_3"].means(f["f_irrelevant_3_new_context"])

    def test_equal_with_different_generic_subfactors(self, make_complex_fact):
        assert make_complex_fact["f_relevant_murder"].means(
            make_complex_fact["f_relevant_murder_craig"]
        )

    def test_reciprocal_context_register(self, watt_factor):
        """
        This test describes two objects with the same meaning that have been
        made in two different ways, each with a different id and repr.
        """
        assert watt_factor["f7"].means(watt_factor["f7_swap_entities"])

    def test_interchangeable_concrete_terms(self):
        """Detect that placeholders differing only by a final digit are interchangeable."""
        ann = Entity("Ann", generic=False)
        bob = Entity("Bob", generic=False)

        ann_and_bob_were_family = Fact(
            Predicate("$relative1 and $relative2 both were members of the same family"),
            terms=(ann, bob),
        )
        bob_and_ann_were_family = Fact(
            Predicate("$relative1 and $relative2 both were members of the same family"),
            terms=(bob, ann),
        )

        assert ann_and_bob_were_family.means(bob_and_ann_were_family)

    def test_unequal_due_to_repeating_entity(self, make_factor):
        """I'm not convinced that a model of a Fact ever needs to include
        multiple references to the same Entity just because the name of the
        Entity appears more than once in the Predicate."""
        f = make_factor
        assert not f["f_three_entities"].means(f["f_repeating_entity"])

    def test_unequal_to_enactment(self, watt_factor, e_copyright):
        assert not watt_factor["f1"].means(e_copyright)
        with pytest.raises(TypeError):
            e_copyright.means(watt_factor["f1"])

    def test_standard_of_proof_inequality(self, watt_factor):

        f = watt_factor
        assert not f["f2_clear_and_convincing"].means(f["f2_preponderance_of_evidence"])
        assert not f["f2_clear_and_convincing"].means(f["f2"])

    def test_means_despite_plural(self):
        directory = Entity("Rural's telephone directory", plural=False)
        listings = Entity("Rural's telephone listings", plural=True)
        directory_original = Fact(Predicate("$thing was original"), terms=directory)
        listings_original = Fact(Predicate("$thing were original"), terms=listings)
        assert directory_original.means(listings_original)

    def test_same_meaning_no_terms(self, make_factor):
        assert make_factor["f_no_context"].means(make_factor["f_no_context"])


class TestImplication:
    def test_fact_implies_none(self, watt_factor):
        assert watt_factor["f1"].implies(None)

    def test_no_implication_of_rule(self, watt_factor, make_rule):
        assert not watt_factor["f1"].implies(make_rule["h1"])

    def test_fact_does_not_imply_holding(self, watt_factor, make_holding):
        assert not watt_factor["f1"].implies(make_holding["h1"])

    def test_specific_factor_implies_generic(self, watt_factor):
        assert watt_factor["f2"] > watt_factor["f2_generic"]
        assert not watt_factor["f2_generic"] > watt_factor["f2"]

    def test_specific_factor_implies_generic_explain(self, watt_factor):
        answer = watt_factor["f2"].explain_implication(watt_factor["f2_generic"])
        assert (
            str(watt_factor["f2"]),
            watt_factor["f2_generic"],
        ) in answer.items()

    def test_specific_implies_generic_form_of_another_fact(self, watt_factor):
        assert watt_factor["f2"] > watt_factor["f3_generic"]

    def test_specific_fact_does_not_imply_generic_entity(
        self, make_entity, watt_factor
    ):
        assert not watt_factor["f2"] > make_entity["motel"]

    def test_factor_does_not_imply_predicate(self, make_predicate, watt_factor):
        with pytest.raises(TypeError):
            assert not watt_factor["f8_meters"] > make_predicate["p8"]

    def test_factor_implies_because_of_quantity(self, watt_factor):
        assert watt_factor["f8_meters"] > watt_factor["f8"]
        assert watt_factor["f8_higher_int"] > watt_factor["f8_float"]
        assert watt_factor["f8_int"] < watt_factor["f8_higher_int"]

    def test_factor_implies_no_truth_value(self, watt_factor):
        assert watt_factor["f2"] > watt_factor["f2_no_truth"]
        assert not watt_factor["f2_no_truth"] > watt_factor["f2"]

    def test_comparison_implies_no_truth_value(self, watt_factor):
        assert watt_factor["f8"] > watt_factor["f8_no_truth"]
        assert not watt_factor["f8_no_truth"] > watt_factor["f8"]

    def test_implication_standard_of_proof(self, make_factor):
        assert (
            not make_factor["f_shooting_craig_poe"]
            > make_factor["f_shooting_craig_brd"]
        )
        assert make_factor["f_shooting_craig_brd"] > make_factor["f_shooting_craig_poe"]

    def test_factor_implies_because_of_exact_quantity(self, watt_factor):
        assert watt_factor["f8_exact"] > watt_factor["f7"]
        assert watt_factor["f8_exact"] >= watt_factor["f8"]

    def test_no_implication_pint_quantity_and_int(self, watt_factor):
        assert not watt_factor["f8"] > watt_factor["f8_int"]
        assert not watt_factor["f8"] < watt_factor["f8_int"]

    def test_absent_factor_implies_absent_factor_with_lesser_quantity(
        self, watt_factor
    ):
        assert watt_factor["f9_absent_miles"] > watt_factor["f9_absent"]

    def test_equal_factors_not_gt(self, watt_factor):
        f = watt_factor
        assert f["f7"] >= f["f7"]
        assert f["f7"] <= f["f7"]
        assert not f["f7"] > f["f7"]

    def test_standard_of_proof_comparison(self, watt_factor):
        f = watt_factor
        assert f["f2_clear_and_convincing"].implies(f["f2_preponderance_of_evidence"])
        assert f["f2_beyond_reasonable_doubt"] >= f["f2_clear_and_convincing"]

    def test_no_implication_between_factors_with_and_without_standards(
        self, watt_factor
    ):
        f = watt_factor
        assert not f["f2_clear_and_convincing"] > f["f2"]
        assert not f["f2"] > f["f2_preponderance_of_evidence"]

    def test_implication_complex(self, make_complex_fact):
        assert (
            make_complex_fact["f_relevant_murder"]
            > make_complex_fact["f_relevant_murder_whether"]
        )

    def test_context_register_text(self, make_context_register):
        assert str(make_context_register) == (
            "ContextRegister(<Alice> is like <Craig>, <Bob> is like <Dan>)"
        )

    def test_implication_complex_explain(
        self, make_complex_fact, make_context_register
    ):
        complex_true = make_complex_fact["f_relevant_murder"]
        complex_whether = make_complex_fact["f_relevant_murder_whether"].new_context(
            make_context_register
        )
        explanation = complex_true.explain_implication(complex_whether)
        assert (str(Entity("Alice")), Entity("Craig")) in explanation.items()

    def test_implication_explain_keys_only_from_left(
        self, make_complex_fact, make_context_register
    ):
        """
        Check that when implies provides a ContextRegister as an "explanation",
        it uses elements only from the left as keys and from the right as values.
        """
        complex_true = make_complex_fact["f_relevant_murder"]
        complex_whether = make_complex_fact["f_relevant_murder_whether"]
        new = complex_whether.new_context(make_context_register)
        explanations = list(complex_true.explanations_implication(new))
        explanation = explanations.pop()
        assert (str(Entity("Craig")), Entity("Alice")) not in explanation.items()
        assert (str(Entity("Alice")), Entity("Craig")) in explanation.items()

    def test_context_registers_for_complex_comparison(self, make_complex_fact):
        gen = make_complex_fact["f_relevant_murder_nested_swap"]._context_registers(
            make_complex_fact["f_relevant_murder"], operator.ge
        )
        register = next(gen)
        assert register.matches.get("<Alice>") == Entity("Bob")

    def test_no_implication_complex(self, make_complex_fact):
        assert (
            not make_complex_fact["f_relevant_murder"]
            >= make_complex_fact["f_relevant_murder_alice_craig"]
        )

    def test_implied_by(self, make_complex_fact):
        assert make_complex_fact["f_relevant_murder_whether"].implied_by(
            make_complex_fact["f_relevant_murder"]
        )

    def test_explanation_implied_by(self, make_complex_fact):
        explanation = make_complex_fact["f_relevant_murder_whether"].explain_implied_by(
            make_complex_fact["f_relevant_murder"]
        )
        assert explanation


class TestContradiction:
    def test_factor_different_predicate_truth_contradicts(self, watt_factor):
        assert watt_factor["f7"].contradicts(watt_factor["f7_opposite"])
        assert watt_factor["f7_opposite"].contradicts(watt_factor["f7"])

    def test_same_predicate_true_vs_false(self, watt_factor):
        assert watt_factor["f10"].contradicts(watt_factor["f10_false"])
        assert watt_factor["f10"].truth != watt_factor["f10_false"].truth

    def test_factor_does_not_contradict_predicate(self, make_predicate, watt_factor):
        with pytest.raises(TypeError):
            _ = watt_factor["f7"].contradicts(make_predicate["p7_true"])

    def test_factor_contradiction_absent_predicate(self, watt_factor):
        assert watt_factor["f3"].contradicts(watt_factor["f3_absent"])
        assert watt_factor["f3_absent"].contradicts(watt_factor["f3"])

    def test_absences_of_contradictory_facts_consistent(self, watt_factor):
        assert not watt_factor["f8_absent"].contradicts(watt_factor["f8_less_absent"])

    def test_factor_no_contradiction_no_truth_value(self, watt_factor):
        assert not watt_factor["f2"].contradicts(watt_factor["f2_no_truth"])
        assert not watt_factor["f2_no_truth"].contradicts(watt_factor["f2_false"])

    def test_absent_factor_contradicts_broader_quantity_statement(self, watt_factor):
        assert watt_factor["f8_absent"].contradicts(watt_factor["f8_meters"])
        assert watt_factor["f8_meters"].contradicts(watt_factor["f8_absent"])

    def test_less_specific_absent_contradicts_more_specific(self, watt_factor):
        assert watt_factor["f9_absent_miles"].contradicts(watt_factor["f9"])
        assert watt_factor["f9"].contradicts(watt_factor["f9_absent_miles"])

    def test_no_contradiction_with_more_specific_absent(self, watt_factor):
        assert not watt_factor["f9_absent"].contradicts(watt_factor["f9_miles"])
        assert not watt_factor["f9_miles"].contradicts(watt_factor["f9_absent"])

    def test_contradiction_complex(self, make_complex_fact):
        assert make_complex_fact["f_irrelevant_murder"].contradicts(
            make_complex_fact["f_relevant_murder_craig"]
        )

    def test_no_contradiction_complex(self, make_complex_fact):
        assert not make_complex_fact["f_irrelevant_murder"].contradicts(
            make_complex_fact["f_relevant_murder_alice_craig"]
        )

    def test_no_contradiction_of_None(self, watt_factor):
        assert not watt_factor["f1"].contradicts(None)

    def test_contradicts_if_present_both_present(self, watt_factor):
        """
        Test a helper function that checks whether there would
        be a contradiction if neither Factor was "absent".
        """
        assert watt_factor["f2"]._contradicts_if_present(watt_factor["f2_false"])

    def test_contradicts_if_present_one_absent(self, watt_factor):
        assert watt_factor["f2"]._contradicts_if_present(watt_factor["f2_false_absent"])

    def test_false_does_not_contradict_absent(self):
        absent_fact = Fact(
            predicate=Predicate(
                template="${rural_s_telephone_directory} was copyrightable", truth=True
            ),
            terms=(Entity(name="Rural's telephone directory")),
            absent=True,
        )
        false_fact = Fact(
            predicate=Predicate(
                template="${the_java_api} was copyrightable", truth=False
            ),
            terms=(Entity(name="the Java API", generic=True, plural=False)),
            absent=False,
        )
        assert not false_fact.contradicts(absent_fact)
        assert not absent_fact.contradicts(false_fact)

    # Consistency with Entity/Factor assignments

    def test_inconsistent_statements_about_different_entities(self):
        """
        Alice and Bob are both generics. So it's possible to reach a
        contradiction if you assume they correspond to one another.
        """
        p_small_weight = Comparison(
            "the amount of gold $person possessed was",
            sign="<",
            expression=Q_("1 gram"),
        )
        p_large_weight = Comparison(
            "the amount of gold $person possessed was",
            sign=">=",
            expression=Q_("100 kilograms"),
        )
        alice = Entity("Alice")
        bob = Entity("Bob")
        alice_rich = Fact(p_large_weight, terms=alice)
        bob_poor = Fact(p_small_weight, terms=bob)
        assert alice_rich.contradicts(bob_poor)

    def test_inconsistent_statements_about_corresponding_entities(self):
        """
        Even though Alice and Bob are both generics, it's known that
        Alice in the first context corresponds with Alice in the second.
        So there's no contradiction.
        """
        p_small_weight = Comparison(
            "the amount of gold $person possessed was",
            sign="<",
            expression=Q_("1 gram"),
        )
        p_large_weight = Comparison(
            "the amount of gold $person possessed was",
            sign=">=",
            expression=Q_("100 kilograms"),
        )
        alice = Entity("Alice")
        bob = Entity("Bob")
        alice_rich = Fact(p_large_weight, terms=alice)
        bob_poor = Fact(p_small_weight, terms=bob)
        register = ContextRegister()
        register.insert_pair(alice, alice)
        assert not alice_rich.contradicts(bob_poor, context=register)

    def test_copy_with_foreign_context(self, watt_mentioned, watt_factor):
        w = watt_mentioned
        assert (
            watt_factor["f1"]
            .new_context(ContextRegister.from_lists([w[0]], [w[2]]))
            .means(watt_factor["f1_different_entity"])
        )

    def test_check_entity_consistency_true(self, make_entity, make_factor):
        left = make_factor["f_irrelevant_3"]
        right = make_factor["f_irrelevant_3_new_context"]
        e = make_entity
        easy_register = ContextRegister.from_lists([e["dan"]], [e["craig"]])
        easy_update = left.update_context_register(
            right, easy_register, comparison=means
        )
        harder_register = ContextRegister.from_lists(
            keys=[e["alice"], e["bob"], e["craig"], e["dan"], e["circus"]],
            values=[e["bob"], e["alice"], e["dan"], e["craig"], e["circus"]],
        )
        harder_update = left.update_context_register(
            right,
            context=harder_register,
            comparison=means,
        )
        assert any(register is not None for register in easy_update)
        assert any(register is not None for register in harder_update)

    def test_check_entity_consistency_false(self, make_entity, make_factor):
        context = ContextRegister()
        context.insert_pair(make_entity["circus"], make_entity["alice"])
        update = make_factor["f_irrelevant_3"].update_context_register(
            make_factor["f_irrelevant_3_new_context"], comparison=means, context=context
        )
        assert not any(register is not None for register in update)

    def test_entity_consistency_identity_not_equality(self, make_entity, make_factor):

        register = ContextRegister()
        register.insert_pair(make_entity["dan"], make_entity["dan"])
        update = make_factor["f_irrelevant_3"].update_context_register(
            make_factor["f_irrelevant_3_new_context"],
            context=register,
            comparison=means,
        )
        assert not any(register is not None for register in update)

    def test_check_entity_consistency_type_error(
        self, make_entity, make_factor, make_predicate
    ):
        """
        There would be no TypeError if it used "means"
        instead of .gt. The comparison would just return False.
        """
        update = make_factor["f_irrelevant_3"].update_context_register(
            make_predicate["p2"],
            {str(make_entity["dan"]): make_entity["dan"]},
            operator.gt,
        )
        with pytest.raises(TypeError):
            any(register is not None for register in update)


class TestConsistent:
    def test_contradictory_facts_about_same_entity(self, watt_factor):
        left = watt_factor["f8_less"]
        right = watt_factor["f8_meters"]
        register = ContextRegister()
        register.insert_pair(left.generic_factors()[0], right.generic_factors()[0])
        assert not left.consistent_with(right, register)

    def test_explanations_consistent_with(self, watt_factor):
        left = watt_factor["f8_less"]
        right = watt_factor["f8_meters"]
        register = ContextRegister()
        register.insert_pair(left.generic_factors()[0], right.generic_factors()[0])
        explanations = list(left.explanations_consistent_with(right, context=register))
        assert not explanations

    def test_factor_consistent_with_none(self, make_exhibit):
        assert make_exhibit["no_shooting_testimony"].consistent_with(
            make_exhibit["no_shooting_witness_unknown_testimony"]
        )


class TestAddition:
    @pytest.mark.parametrize(
        "left, right, expected",
        [
            ("f_shooting_craig_poe", "f_shooting_craig_brd", "f_shooting_craig_brd"),
            ("f_irrelevant_3", "f_irrelevant_3_new_context", "f_irrelevant_3"),
            (
                "f_irrelevant_3_new_context",
                "f_irrelevant_3",
                "f_irrelevant_3_new_context",
            ),
        ],
    )
    def test_addition(self, make_factor, left, right, expected):
        answer = make_factor[left] + make_factor[right]
        assert answer.means(make_factor[expected])

    def test_add_unrelated_factors(self, make_factor):
        assert make_factor["f_murder"] + make_factor["f_crime"] is None

    def test_cant_add_enactment_to_fact(self, watt_factor, e_search_clause):
        with pytest.raises(TypeError):
            print(watt_factor["f3"] + e_search_clause)
