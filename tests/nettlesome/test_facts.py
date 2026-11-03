"""Tests that Statements work the same as AuthoritySpoke Facts."""

import operator

import pytest

from authorityspoke.nettlesome.terms import ContextRegister, DuplicateTermError
from authorityspoke.nettlesome.terms import Explanation, TermSequence, means
from authorityspoke.nettlesome.entities import Entity
from authorityspoke.nettlesome.factors import AbsenceOf
from authorityspoke.nettlesome.predicates import Predicate
from authorityspoke.nettlesome.quantities import Comparison, Q_
from authorityspoke.nettlesome.statements import Statement


class TestFacts:
    def test_default_terms_for_fact(self, make_predicate):
        f1 = Statement(
            predicate=make_predicate["shooting"],
            terms=[Entity(name="Al"), Entity(name="Ed")],
        )
        assert f1.terms[0].short_string == Entity(name="Al").short_string

    def test_brackets_around_generic_terms(self, make_predicate):
        statement = Statement(
            predicate=make_predicate["shooting"],
            terms=[Entity(name="Al"), Entity(name="Ed")],
        )
        assert "<Al> shot <Ed>" in str(statement)
        absent = AbsenceOf(
            absent=Statement(
                predicate=make_predicate["shooting"],
                terms=[Entity(name="Al"), Entity(name="Ed")],
            )
        )
        assert "absence of the statement" in str(absent).lower()

    def test_string_no_truth_value(self):
        factor = Predicate(content="things happened", truth=None)
        assert "whether" in str(factor)

    def test_repeating_entity_string(self):
        three_entities = Predicate(
            content="{planner} told {intermediary} to hire {shooter}"
        )
        statement_3 = Statement(
            predicate=three_entities,
            terms=[Entity(name="Al"), Entity(name="Bob"), Entity(name="Cid")],
        )
        two_entities = Predicate(
            content="{shooter} told {intermediary} to hire {shooter}"
        )
        statement_2 = Statement(
            predicate=two_entities, terms=[Entity(name="Al"), Entity(name="Bob")]
        )
        assert (
            "statement that <Al> told <Bob> to hire <Cid>".lower()
            in str(statement_3).lower()
        )
        assert (
            "statement that <Al> told <Bob> to hire <Al>".lower()
            in str(statement_2).lower()
        )

    def test_string_representation_with_concrete_entities(self):
        """
        "Al" is still a string representation of an Term
        object, but it's not in angle brackets because it can't be
        replaced by another Term object without changing the meaning
        of the Statement.
        """
        three_entities = Predicate(
            content="{planner} told {intermediary} to hire {shooter}"
        )
        statement_3 = Statement(
            predicate=three_entities,
            terms=[
                Entity(name="Al", generic=False),
                Entity(name="Bob"),
                Entity(name="Cid"),
            ],
        )
        assert (
            "statement that Al told <Bob> to hire <Cid>".lower()
            in str(statement_3).lower()
        )

    def test_string_for_fact_with_identical_terms(self):
        devon = Entity(name="Devon", generic=True)
        elaine = Entity(name="Elaine", generic=True)
        opened_account = Statement(
            predicate=Predicate(
                content="{applicant} opened a bank account for {applicant} and {cosigner}"
            ),
            terms=(devon, elaine),
        )
        assert "<Devon> opened a bank account for <Devon> and <Elaine>" in str(
            opened_account
        )

    def test_new_context_replace_fact(self):
        changes = ContextRegister.from_lists(
            [Entity(name="Death Star 3"), Entity(name="Kylo Ren")],
            [Entity(name="Death Star 1"), Entity(name="Darth Vader")],
        )
        statement = Statement.new(
            predicate="{person} blew up a planet with {weapon}",
            terms=[Entity(name="Kylo Ren"), Entity(name="Death Star 3")],
        )
        new = statement.new_context(changes)

        assert "<Darth Vader> blew up" in new.short_string

    def test_make_new_complex_fact(self, make_predicate, make_statement):
        shooting = make_statement["shooting"]
        murder = make_statement["murder"]
        relevant = make_predicate["relevant"]

        fact = Statement(predicate=relevant, terms=(shooting, murder))
        assert fact.terms[0].name == ""

    def test_get_factor_from_recursive_search(self, make_complex_fact):
        complex = make_complex_fact["relevant_murder"]
        factor_list = list(complex.recursive_terms.values())
        assert any(factor.name == "Alice" for factor in factor_list)

    def test_new_context_from_factor(self, make_statement):
        crime = make_statement["crime"]
        greg = Entity(name="Greg", generic=False)
        different = crime.new_context([greg])
        assert "Greg committed a crime" in str(different)

    def test_type_of_terms(self, make_statement):
        assert isinstance(make_statement["crime"].terms, TermSequence)
        assert make_statement["crime"].term_sequence is make_statement["crime"].terms

    def test_concrete_to_abstract(self, make_statement):
        assert (
            "<the Statement that <Alice> committed a crime>".lower()
            in str(make_statement["crime"].make_generic()).lower()
        )

    def test_entity_slots_as_length_of_factor(self, make_statement):
        assert len(make_statement["crime"].predicate) == 1
        assert len(make_statement["crime"]) == 1

    def test_bool_of_statement_is_true(self):
        predicate = Predicate(content="context was included", truth=False)
        no_context = Statement(predicate=predicate, terms=[])
        assert bool(no_context) is True

    def test_predicate_with_entities(self, make_statement):
        content = make_statement["crime"].predicate._content_with_terms(
            [Entity(name="Jim")]
        )
        assert "<Jim> committed" in content

    def test_reciprocal_with_wrong_number_of_entities(self, make_statement):
        with pytest.raises(ValueError):
            make_statement["crime"].predicate._content_with_terms(
                (Entity(name="Al"), Entity(name="Ben"))
            )

    def test_complex_string(self, make_complex_fact):
        statement = make_complex_fact["relevant_murder"]
        assert (
            "\n    the statement that <Alice> shot <Bob>"
            in statement.str_with_concrete_context
        )

    def test_length_with_specific_term(self):
        statement = Statement.new(
            predicate="{person} paid tax to {state}",
            terms=[
                Entity(name="Alice"),
                Entity(name="the State of Texas", generic=False),
            ],
        )
        assert len(statement) == 1

    def test_truth_param(self):
        no_license = Statement.new(
            predicate="{business} was licensed as a money transmitting business",
            truth=False,
            terms=[Entity(name="Helix")],
        )
        assert no_license.predicate.truth is False


class TestSameMeaning:
    def test_equality_factor_from_same_predicate(self, make_statement):
        assert make_statement["crime"].means(make_statement["crime"])

    def test_equality_because_factors_are_generic_entities(self, make_statement):
        assert make_statement["murder"].means(make_statement["murder_entity_order"])

    def test_unequal_because_a_factor_is_not_generic(self, make_statement):
        assert not make_statement["crime"].means(
            make_statement["crime_specific_person"]
        )

    def test_generic_terms_equal(self):
        generic = Statement.new(predicate="something happened", generic=True)
        generic_false = Statement.new(
            predicate=Predicate(content="something happened", truth=False), generic=True
        )
        assert generic.means(generic_false)
        assert generic_false.means(generic)

    def test_generic_and_specific_factors_unequal(self):
        generic = Statement.new(predicate="something happened", generic=True)
        specific = Statement.new(predicate="something happened", generic=False)
        assert not generic.means(specific)

    def test_cannot_repeat_term_in_termsequence(self, make_predicate):
        with pytest.raises(DuplicateTermError):
            Statement.new(
                predicate="{person1} shot {person2}",
                terms=[Entity(name="Al"), Entity(name="Al")],
            )

    def test_factor_different_predicate_truth_unequal(self, make_statement):
        assert not make_statement["shooting"].means(make_statement["murder"])

    def test_unequal_because_one_factor_is_absent(self, make_predicate):
        left = Statement.new(
            predicate=make_predicate["shooting"],
            terms=[Entity(name="Al"), Entity(name="Bo")],
        )
        right = AbsenceOf(
            absent=Statement.new(
                predicate=make_predicate["shooting"],
                terms=[Entity(name="Al"), Entity(name="Bob")],
            )
        )
        assert not left.means(right)

    def test_copies_of_identical_factor(self, make_statement):
        """
        Even if the two factors have different entity markers in self.terms,
        I expect them to evaluate equal because the choice of entity markers is
        arbitrary.
        """
        f = make_statement
        assert f["irrelevant_3"].means(f["irrelevant_3"])
        assert f["irrelevant_3"].means(f["irrelevant_3_new_context"])

    def test_equal_with_different_generic_subfactors(self, make_complex_fact):
        assert make_complex_fact["relevant_murder"].means(
            make_complex_fact["relevant_murder_craig"]
        )

    def test_interchangeable_concrete_terms(self):
        """Detect that placeholders differing only by a final digit are interchangeable."""
        ann = Entity(name="Ann", generic=False)
        bob = Entity(name="Bob", generic=False)

        ann_and_bob_were_family = Statement.new(
            predicate=Predicate(
                content="{relative1} and {relative2} both were members of the same family"
            ),
            terms=(ann, bob),
        )
        bob_and_ann_were_family = Statement(
            predicate=Predicate(
                content="{relative1} and {relative2} both were members of the same family"
            ),
            terms=(bob, ann),
        )

        assert ann_and_bob_were_family.means(bob_and_ann_were_family)

    def test_means_despite_plural(self):
        directory = Entity(name="Rural's telephone directory", plural=False)
        listings = Entity(name="Rural's telephone listings", plural=True)
        directory_original = Statement(
            predicate=Predicate(content="{thing} was original"), terms=[directory]
        )
        listings_original = Statement(
            predicate=Predicate(content="{thing} were original"), terms=[listings]
        )
        assert directory_original.means(listings_original)

    def test_same_meaning_no_terms(self, make_statement):
        assert make_statement["no_context"].means(make_statement["no_context"])


class TestImplication:
    def test_fact_implies_none(self, make_statement):
        assert make_statement["crime"].implies(None)

    def test_specific_factor_implies_generic(self, make_statement):
        assert make_statement["crime"] > make_statement["crime_generic"]
        assert not make_statement["crime_generic"] > make_statement["crime"]

    def test_specific_factor_implies_generic_explain(self, make_statement):
        answer = make_statement["crime"].explain_implication(
            make_statement["crime_generic"]
        )
        assert (
            answer.context[str(make_statement["crime"])]
            == make_statement["crime_generic"]
        )

    def test_specific_implies_generic_form_of_another_fact(self, make_statement):
        assert make_statement["murder"] > make_statement["crime_generic"]

    def test_specific_fact_does_not_imply_generic_entity(self, make_statement):
        assert not make_statement["crime"] > Entity(name="Bob")

    def test_factor_does_not_imply_predicate(self, make_statement, make_predicate):
        with pytest.raises(TypeError):
            assert not make_statement["crime"] > make_predicate["crime"]

    def test_factor_implies_because_of_quantity(self, make_statement):
        meters = Comparison.new(
            content="the distance between {place1} and {place2} was",
            sign=">=",
            expression=Q_("10 meters"),
        )
        left = Statement(
            predicate=meters, terms=[Entity(name="Al"), Entity(name="Bob")]
        )
        more = Comparison.new(
            content="the distance between {place1} and {place2} was",
            truth=True,
            sign=">",
            expression=Q_("30 feet"),
        )
        right = Statement(predicate=more, terms=[Entity(name="Al"), Entity(name="Bob")])
        assert left > right

    def test_int_factor_implies_float_factor(self, make_statement):
        assert make_statement["float_distance"] > make_statement["higher_int"]
        assert make_statement["int_distance"] > make_statement["higher_int"]

    def test_factor_implies_no_truth_value(self, make_statement):
        assert make_statement["shooting"] > make_statement["shooting_whether"]
        assert not make_statement["shooting_whether"] > make_statement["shooting"]

    def test_comparison_implies_no_truth_value(self, make_statement):
        assert make_statement["less"] > make_statement["less_whether"]
        assert not make_statement["less_whether"] > make_statement["less"]

    def test_factor_implies_because_of_exact_quantity(self, make_statement):
        assert make_statement["exact"] > make_statement["less"]
        assert make_statement["exact"] >= make_statement["not_more"]

    def test_no_implication_pint_quantity_and_int(self, make_statement):
        assert not make_statement["less"] > make_statement["int_distance"]
        assert not make_statement["less"] < make_statement["int_distance"]

    def test_absent_implies_more_specific_absent(self, make_statement):
        assert make_statement["absent_more"] > make_statement["absent_way_more"]

    def test_equal_factors_not_gt(self, make_statement):
        assert make_statement["less"] >= make_statement["less"]
        assert make_statement["less"] <= make_statement["less"]
        assert not make_statement["less"] > make_statement["less"]

    def test_implication_complex_whether(self, make_complex_fact):
        assert (
            make_complex_fact["relevant_murder"]
            > make_complex_fact["relevant_murder_whether"]
        )

    def test_context_register_text(self, make_context_register):
        assert str(make_context_register) == (
            "ContextRegister(<Alice> is like <Craig>, and <Bob> is like <Dan>)"
        )

    def test_implication_complex_explain(
        self, make_complex_fact, make_context_register
    ):
        complex_true = make_complex_fact["relevant_murder"]
        complex_whether = make_complex_fact["relevant_murder_whether"].new_context(
            make_context_register
        )
        explanation = complex_true.explain_implication(complex_whether)
        assert str(Entity(name="Alice")), Entity(name="Craig") in explanation.items()

    def test_implication_explain_keys_only_from_left(
        self, make_complex_fact, make_context_register
    ):
        """
        Check that when implies provides a ContextRegister as an "explanation",
        it uses elements only from the left as keys and from the right as values.
        """
        complex_true = make_complex_fact["relevant_murder"]
        complex_whether = make_complex_fact["relevant_murder_whether"]
        new = complex_whether.new_context(make_context_register)
        explanations = list(complex_true.explanations_implication(new))
        explanation = explanations.pop()
        assert "<Craig>" not in explanation.context.keys()
        assert explanation.context["<Alice>"].name == "Craig"

    def test_context_registers_for_complex_comparison(self, make_complex_fact):
        gen = make_complex_fact["relevant_murder_nested_swap"]._context_registers(
            make_complex_fact["relevant_murder"], operator.ge
        )
        register = next(gen)
        assert register.matches.get("<Alice>").name == "Bob"

    def test_no_implication_complex(self, make_complex_fact):
        left = make_complex_fact["relevant_murder"]
        right = make_complex_fact["relevant_murder_alice_craig"]
        assert not left >= right
        assert left.explain_implication(right) is None

    def test_implied_by(self, make_complex_fact):
        assert make_complex_fact["relevant_murder_whether"].implied_by(
            make_complex_fact["relevant_murder"]
        )

    def test_explanation_implied_by(self, make_complex_fact):
        explanation = make_complex_fact["relevant_murder_whether"].explain_implied_by(
            make_complex_fact["relevant_murder"]
        )
        assert explanation

    def test_explain_not_implied_by(self, make_complex_fact):
        left = make_complex_fact["relevant_murder"]
        right = make_complex_fact["relevant_murder_whether"]
        assert left.explain_implied_by(right) is None

    def test_not_implied_by_none(self, make_complex_fact):
        left = make_complex_fact["relevant_murder"]
        assert not left.implied_by(None)


class TestContradiction:
    def test_factor_different_predicate_truth_contradicts(self, make_statement):
        assert make_statement["less"].contradicts(make_statement["more"])
        assert make_statement["more"].contradicts(make_statement["less"])

    def test_same_predicate_true_vs_false(self, make_statement):
        assert make_statement["murder"].contradicts(make_statement["murder_false"])
        assert make_statement["murder"].truth != make_statement["murder_false"].truth

    def test_factor_does_not_contradict_predicate(self, make_statement, make_predicate):
        with pytest.raises(TypeError):
            make_statement["murder"].contradicts(make_predicate["murder_false"])

    def test_factor_contradiction_absent_predicate(self, make_statement):
        assert make_statement["more"].contradicts(make_statement["absent_more"])
        assert make_statement["absent_more"].contradicts(make_statement["more"])

    def test_absences_of_contradictory_facts_consistent(self, make_statement):
        assert not make_statement["absent_more"].contradicts(
            make_statement["absent_less"]
        )

    def test_factor_no_contradiction_no_truth_value(self, make_statement):
        assert not make_statement["murder"].contradicts(
            make_statement["murder_whether"]
        )
        assert not make_statement["murder_whether"].contradicts(
            make_statement["murder_false"]
        )

    def test_absent_factor_contradicts_broader_quantity_statement(self, make_statement):
        assert make_statement["way_more"].contradicts(make_statement["absent_more"])
        assert make_statement["absent_more"].contradicts(make_statement["way_more"])

    def test_no_contradiction_with_more_specific_absent(self, make_statement):
        assert not make_statement["absent_way_more"].contradicts(make_statement["more"])
        assert not make_statement["more"].contradicts(make_statement["absent_way_more"])

    def test_contradiction_complex(self, make_complex_fact):
        assert make_complex_fact["irrelevant_murder"].contradicts(
            make_complex_fact["relevant_murder_craig"]
        )

    def test_no_contradiction_complex(self, make_complex_fact):
        assert not make_complex_fact["irrelevant_murder"].contradicts(
            make_complex_fact["relevant_murder_alice_craig"]
        )

    def test_no_contradiction_of_None(self, make_statement):
        assert not make_statement["exact"].contradicts(None)

    def test_contradicts_if_present_both_present(self, make_statement):
        """
        Test a helper function that checks whether there would
        be a contradiction if neither Factor was "absent".
        """
        assert make_statement["crime"]._contradicts_if_present(
            make_statement["absent_no_crime"], explanation=Explanation.from_context()
        )

    def test_contradicts_if_present_one_absent(self, make_statement):
        assert make_statement["crime"]._contradicts_if_present(
            make_statement["no_crime"], explanation=Explanation.from_context()
        )

    def test_false_does_not_contradict_absent(self):
        absent_fact = AbsenceOf(
            absent=Statement(
                predicate=Predicate(
                    content="{rural_s_telephone_directory} was copyrightable",
                    truth=True,
                ),
                terms=[Entity(name="Rural's telephone directory")],
            )
        )
        false_fact = Statement(
            predicate=Predicate(
                content="{the_java_api} was copyrightable", truth=False
            ),
            terms=[Entity(name="the Java API", generic=True, plural=False)],
        )
        assert not false_fact.contradicts(absent_fact)
        assert not absent_fact.contradicts(false_fact)

    def test_inconsistent_statements_about_different_entities(self):
        """
        Alice and Bob are both generics. So it's possible to reach a
        contradiction if you assume they correspond to one another.
        """
        p_small_weight = Comparison.new(
            content="the amount of gold {person} possessed was",
            sign="<",
            expression=Q_("1 gram"),
        )
        p_large_weight = Comparison.new(
            content="the amount of gold {person} possessed was",
            sign=">=",
            expression=Q_("100 kilograms"),
        )
        alice = Entity(name="Alice")
        bob = Entity(name="Bob")
        alice_rich = Statement(predicate=p_large_weight, terms=[alice])
        bob_poor = Statement(predicate=p_small_weight, terms=[bob])
        assert alice_rich.contradicts(bob_poor)

    def test_inconsistent_statements_about_corresponding_entities(self):
        """
        Even though Alice and Bob are both generics, it's known that
        Alice in the first context corresponds with Alice in the second.
        So there's no contradiction.
        """
        p_small_weight = Comparison.new(
            content="the amount of gold {person} possessed was",
            sign="<",
            expression=Q_("1 gram"),
        )
        p_large_weight = Comparison.new(
            content="the amount of gold {person} possessed was",
            sign=">=",
            expression=Q_("100 kilograms"),
        )
        alice = Entity(name="Alice")
        bob = Entity(name="Bob")
        alice_rich = Statement(predicate=p_large_weight, terms=[alice])
        bob_poor = Statement(predicate=p_small_weight, terms=[bob])
        register = ContextRegister()
        register.insert_pair(alice, alice)
        assert not alice_rich.contradicts(bob_poor, context=register)

    def test_check_entity_consistency_true(self, make_statement):
        left = make_statement["irrelevant_3"]
        right = make_statement["irrelevant_3_new_context"]
        easy_register = ContextRegister.from_lists(
            [Entity(name="Dan")], [Entity(name="Edgar")]
        )
        easy_update = left.update_context_register(
            right, easy_register, comparison=means
        )
        assert any(register is not None for register in easy_update)
        harder_register = ContextRegister.from_lists(
            to_replace=[
                Entity(name="Alice"),
                Entity(name="Bob"),
                Entity(name="Craig"),
            ],
            replacements=[
                Entity(name="Bob"),
                Entity(name="Alice"),
                Entity(name="Craig"),
            ],
        )
        harder_update = left.update_context_register(
            right,
            context=harder_register,
            comparison=means,
        )

        assert any(register is not None for register in harder_update)

    def test_check_entity_consistency_false(self, make_statement):
        context = ContextRegister()
        context.insert_pair(key=Entity(name="circus"), value=Entity(name="Alice"))
        update = make_statement["irrelevant_3"].update_context_register(
            make_statement["irrelevant_3_new_context"],
            comparison=means,
            context=context,
        )
        assert all(register is None for register in update)

    def test_entity_consistency_identity_not_equality(self, make_statement):
        register = ContextRegister()
        register.insert_pair(key=Entity(name="Dan"), value=Entity(name="Dan"))
        update = make_statement["irrelevant_3"].update_context_register(
            make_statement["irrelevant_3_new_context"],
            context=register,
            comparison=means,
        )
        assert all(register is None for register in update)

    def test_check_entity_consistency_type_error(self, make_statement, make_predicate):
        """
        There would be no TypeError if it used "means"
        instead of .gt. The comparison would just return False.
        """
        update = make_statement["irrelevant_3"].update_context_register(
            make_predicate["shooting"],
            {str(Entity(name="Dan")): Entity(name="Dan")},
            operator.gt,
        )
        with pytest.raises(TypeError):
            any(register is not None for register in update)


class TestConsistent:
    def test_contradictory_facts_about_same_entity(self, make_statement):
        left = make_statement["less_than_20"]
        right = make_statement["more_meters"]
        register = ContextRegister()
        register.insert_pair(left.generic_terms()[0], right.generic_terms()[0])
        assert not left.consistent_with(right, register)
        assert left.explain_consistent_with(right, register) is None

    def test_explanations_consistent_with(self, make_statement):
        left = make_statement["less_than_20"]
        right = make_statement["more_meters"]
        register = ContextRegister()
        register.insert_pair(left.generic_terms()[0], right.generic_terms()[0])
        explanations = list(left.explanations_consistent_with(right, context=register))
        assert not explanations

    def test_inconsistent(self, make_statement):
        context = ContextRegister()
        context.insert_pair(Entity(name="Alice"), Entity(name="Alice"))
        assert not make_statement["crime"].consistent_with(
            make_statement["no_crime"], context=context
        )

    def test_inconsistent_two_terms(self, make_statement):
        context = ContextRegister()
        context.insert_pair(Entity(name="Alice"), Entity(name="Alice"))
        context.insert_pair(Entity(name="Bob"), Entity(name="Bob"))
        assert not make_statement["shooting"].consistent_with(
            make_statement["no_shooting"], context=context
        )


class TestAddition:
    @pytest.mark.parametrize(
        "left, right, expected",
        [
            ("irrelevant_3", "irrelevant_3_new_context", "irrelevant_3"),
            (
                "irrelevant_3_new_context",
                "irrelevant_3",
                "irrelevant_3_new_context",
            ),
        ],
    )
    def test_addition(self, make_statement, left, right, expected):
        answer = make_statement[left] + make_statement[right]
        assert answer.means(make_statement[expected])

    def test_add_unrelated_factors(self, make_statement):
        assert make_statement["murder"] + make_statement["crime"] is None

    def test_same_meaning_after_adding_implied(self):
        dave = Entity(name="Dave")
        speed_template = "{driver}'s driving speed was"
        fast_fact = Statement(
            predicate=Comparison.new(
                content=speed_template, sign=">=", expression="100 miles per hour"
            ),
            terms=[dave],
        )
        slow_fact = Statement(
            predicate=Comparison.new(
                content=speed_template,
                sign=">=",
                expression="20 miles per hour",
            ),
            terms=[dave],
        )
        new = fast_fact + slow_fact
        assert new.means(fast_fact)
