import operator

import pytest

from nettlesome.terms import ContextRegister, TermSequence, means
from nettlesome.entities import Entity
from nettlesome.predicates import Predicate
from nettlesome.quantities import Comparison, Q_
from nettlesome.statements import Statement

from authorityspoke.facts import Fact, AbsenceOfFactor


class TestStatements:
    def test_build_fact(self):
        """
        Check that terms is created as a (hashable) tuple, not list
        """
        shooting = Fact(
            predicate=Predicate(content="$shooter shot $victim"),
            terms=[Entity(name="alice"), Entity(name="bob")],
        )
        assert isinstance(shooting.terms, list)

    def test_string_representation_of_factor(self):
        city = Predicate(content="$place was a city")
        statement = Fact(predicate=city, terms=Entity(name="New York"))
        assert "<New York> was a city" in str(statement)

    def test_string_representation_of_absent_factor(self):
        predicate = Predicate(content="$company was the best brand")
        statement = AbsenceOfFactor(
            absent=Fact(predicate=predicate, terms=Entity(name="Acme"))
        )
        assert "absence of the fact" in str(statement).lower()

    def test_string_no_truth_value(self):
        predicate = Predicate(content="$bird came before $ovum", truth=None)
        statement = Fact(
            predicate=predicate,
            terms=[Entity(name="the chicken"), Entity(name="the egg")],
        )
        assert "whether <the chicken> came before <the egg>" in str(statement)

    def test_terms_param_can_be_dict(self):
        predicate = Predicate(content="$advisor told $employer to hire $applicant")
        three_entities = Fact(
            predicate=predicate,
            terms={
                "advisor": Entity(name="Alice"),
                "employer": Entity(name="Bob"),
                "applicant": Entity(name="Craig"),
            },
        )
        assert (
            "fact that <Alice> told <Bob> to hire <Craig>".lower()
            in str(three_entities).lower()
        )

    def test_string_for_fact_with_identical_terms(self):
        devon = Entity(name="Devon", generic=True)
        elaine = Entity(name="Elaine", generic=True)
        opened_account = Fact(
            predicate=Predicate(
                content="$applicant opened a bank account for $applicant and $cosigner"
            ),
            terms=(devon, elaine),
        )
        assert "<Devon> opened a bank account for <Devon> and <Elaine>" in str(
            opened_account
        )

    def test_complex_fact_no_line_break_in_predicate(self):
        """
        Tests that the string representation of this Holding's only input
        Fact does not contain indented new lines, except in the "SPECIFIC
        CONTEXT" part, if present.

        The representation of the Exhibit mentioned in the Fact should
        not introduce any indented lines inside the Fact's string.
        """
        predicate_shot = Predicate(content="$shooter shot $victim")
        predicate_told = Predicate(content="$speaker told $hearer $statement")
        shot = Fact(
            predicate=predicate_shot, terms=[Entity(name="Alice"), Entity(name="Bob")]
        )
        told = Fact(
            predicate=predicate_told,
            terms=[Entity(name="Henry"), Entity(name="Jenna"), shot],
        )

        fact_text = str(told)
        if "SPECIFIC CONTEXT" in fact_text:
            fact_text = fact_text.split("SPECIFIC CONTEXT")[0].strip()
        assert "\n  " not in fact_text

    def test_new_context_replace_fact(self):
        predicate_shot = Predicate(content="$shooter shot $victim")
        predicate_no_gun = Predicate(content="$suspect had a gun", truth=False)
        predicate_told = Predicate(content="$speaker told $hearer $statement")
        shot = Fact(
            predicate=predicate_shot, terms=[Entity(name="Alice"), Entity(name="Bob")]
        )
        told = Fact(
            predicate=predicate_told,
            terms=[Entity(name="Henry"), Entity(name="Jenna"), shot],
        )
        no_gun = Fact(predicate=predicate_no_gun, terms=Entity(name="Dan"))

        changes = ContextRegister.from_lists(
            [Entity(name="Alice"), Entity(name="Henry"), Entity(name="Jenna"), shot],
            [Entity(name="Dan"), Entity(name="Leslie"), Entity(name="Mike"), no_gun],
        )
        result = told.new_context(changes)
        assert (
            "told <Mike> the fact it was false that <Dan> had a gun".lower()
            in result.short_string.lower()
        )

    def test_too_much_info_to_change_context(self):
        """Test that a list of terms to replace requires "changes" to be consistent."""
        statement = Fact(
            predicate="$person1 loved $person2",
            terms=[Entity(name="Donald"), Entity(name="Daisy")],
        )
        new = statement.new_context(
            changes=[Entity(name="Mickey")],
            terms_to_replace=[Entity(name="Donald"), Entity(name="Daisy")],
        )
        assert "<Mickey> loved <Daisy>" in str(new)

    def test_get_factor_from_recursive_search(self):
        predicate_shot = Predicate(content="$shooter shot $victim")
        predicate_told = Predicate(content="$speaker told $hearer $statement")
        shot = Fact(
            predicate=predicate_shot, terms=[Entity(name="Alice"), Entity(name="Bob")]
        )
        told = Fact(
            predicate=predicate_told,
            terms=[Entity(name="Henry"), Entity(name="Jenna"), shot],
        )
        factors = told.recursive_terms
        assert factors["<Alice>"].compare_keys(Entity(name="Alice"))

    def test_new_concrete_context(self):
        """
        "Dragonfly Inn" is still a string representation of an Entity
        object, but it's not in angle brackets because it can't be
        replaced by another Entity object without changing the meaning
        of the Fact.
        """
        predicate = Predicate(content="$place was a hotel")
        statement = Fact(predicate=predicate, terms=[Entity(name="Independence Inn")])
        different = statement.new_context([Entity(name="Dragonfly Inn", generic=False)])
        assert "Dragonfly Inn was a hotel" in str(different)

    def test_new_statement_from_entities(self):
        predicate = Predicate(content="$person managed $place")
        statement = Fact(
            predicate=predicate, terms=[Entity(name="Steve Jobs"), Entity(name="Apple")]
        )
        different = statement.new_context(
            [Entity(name="Darth Vader"), Entity(name="the Death Star")]
        )
        assert "<Darth Vader> managed" in str(different)
        assert isinstance(different.term_sequence, TermSequence)

    def test_term_cannot_be_string(self):
        city = Predicate(content="$place was a city")
        with pytest.raises(TypeError):
            Statement(city, terms=["New York"])

    def test_concrete_to_abstract(self):
        predicate = Predicate(content="$person had a farm")
        statement = Fact(predicate=predicate, terms=Entity(name="Old MacDonald"))
        assert str(statement).lower() == "the fact that <old macdonald> had a farm"
        generic_str = str(statement.make_generic()).lower()
        assert generic_str == "<the fact that <old macdonald> had a farm>"

    def test_entity_slots_as_length_of_factor(self):
        predicate = Predicate(content="$person had a farm")
        statement = Fact(predicate=predicate, terms=Entity(name="Old MacDonald"))
        assert len(statement.predicate) == 1
        assert len(statement) == 1

    def test_predicate_with_entities(self):
        predicate = Predicate(content="$person1 and $person2 went up the hill")
        terms = [Entity(name="Jack"), Entity(name="Jill")]
        assert (
            predicate._content_with_terms(terms) == "<Jack> and <Jill> went up the hill"
        )

    def test_factor_terms_do_not_match_predicate(self):
        """
        predicate has only one slot for context factors, but
        this tells it to look for three.
        """
        with pytest.raises(ValueError):
            Statement(
                predicate=Predicate(content="$sentence had only one context term"),
                terms=[Entity(name="Al"), Entity(name="Ed"), Entity(name="Xu")],
            )

    def test_repeated_placeholder_in_fact(self):
        predicate = Predicate(
            content="the precise formulation "
            "of ${program}'s code was necessary for $program to work",
            truth=False,
        )
        fact = Fact(predicate=predicate, terms=Entity(name="Lotus 1-2-3"))

        assert fact.short_string.lower() == (
            "the fact it was false that the precise formulation "
            "of <lotus 1-2-3>'s code was necessary for <lotus 1-2-3> to work"
        )
        assert len(fact.terms) == 1


class TestSameMeaning:
    def test_equality_factor_from_same_predicate(self):
        predicate = Predicate(content="$speaker greeted $listener")
        fact = Fact(predicate=predicate, terms=[Entity(name="Al"), Entity(name="Meg")])
        fact_b = Fact(
            predicate=predicate, terms=[Entity(name="Al"), Entity(name="Meg")]
        )
        assert fact.means(fact_b)

    def test_equality_factor_from_equal_predicate(self):
        predicate = Predicate(content="$speaker greeted $listener")
        equal_predicate = Predicate(content="$speaker greeted $listener")
        fact = Fact(predicate=predicate, terms=[Entity(name="Al"), Entity(name="Meg")])
        fact_b = Fact(
            predicate=equal_predicate, terms=[Entity(name="Al"), Entity(name="Meg")]
        )
        assert fact.means(fact_b)

    def test_equality_because_factors_are_generic_entities(self):
        predicate = Predicate(content="$speaker greeted $listener")
        fact = Fact(predicate=predicate, terms=[Entity(name="Al"), Entity(name="Meg")])
        fact_b = Fact(
            predicate=predicate, terms=[Entity(name="Ed"), Entity(name="Imogene")]
        )
        assert fact.means(fact_b)

    def test_unequal_because_a_factor_is_not_generic(self):
        predicate = Predicate(content="$speaker greeted $listener")
        fact = Fact(predicate=predicate, terms=[Entity(name="Al"), Entity(name="Meg")])
        fact_b = Fact(
            predicate=predicate,
            terms=[Entity(name="Ed"), Entity(name="Imogene", generic=False)],
        )
        assert not fact.means(fact_b)

    def test_true_and_false_generic_terms_equal(self):
        predicate = Predicate(content="$speaker greeted $listener")
        false_predicate = Predicate(content="$speaker greeted $listener", truth=False)
        fact = Fact(
            predicate=predicate,
            terms=[Entity(name="Al"), Entity(name="Meg")],
            generic=True,
        )
        false_fact = Fact(
            predicate=false_predicate,
            terms=[Entity(name="Ed"), Entity(name="Imogene")],
            generic=True,
        )
        assert fact.means(false_fact)

    def test_generic_terms_with_different_text_equal(self):
        predicate = Predicate(content="$speaker greeted $listener")
        different_predicate = Predicate(content="$speaker attacked $listener")
        fact = Fact(
            predicate=predicate,
            terms=[Entity(name="Al"), Entity(name="Meg")],
            generic=True,
        )
        different_fact = Fact(
            predicate=different_predicate,
            terms=[Entity(name="Al"), Entity(name="Meg")],
            generic=True,
        )
        assert fact.means(different_fact)

    def test_equal_referencing_diffent_generic_terms(self):
        predicate = Predicate(content="$speaker greeted $listener")
        fact = Fact(predicate=predicate, terms=[Entity(name="Al"), Entity(name="Meg")])
        fact_b = Fact(
            predicate=predicate, terms=[Entity(name="Jim"), Entity(name="Ned")]
        )
        assert fact.means(fact_b)

    def test_factor_reciprocal_unequal(self):
        predicate = Predicate(content="$advisor told $employer to hire $applicant")
        three_entities = Fact(
            predicate=predicate,
            terms={
                "advisor": Entity(name="Alice"),
                "employer": Entity(name="Bob"),
                "applicant": Entity(name="Craig"),
            },
        )
        repeating_predicate = Predicate(
            content="$applicant told $employer to hire $applicant"
        )
        two_entities = Fact(
            predicate=repeating_predicate,
            terms={
                "applicant": Entity(name="Alice"),
                "employer": Entity(name="Bob"),
            },
        )
        assert not three_entities.means(two_entities)

    def test_factor_different_predicate_truth_unequal(self):
        predicate = Predicate(content="$shooter shot $victim")
        false_predicate = Predicate(content="$shooter shot $victim", truth=False)
        fact = Fact(predicate=predicate, terms=[Entity(name="Al"), Entity(name="Meg")])
        fact_b = Fact(
            predicate=false_predicate, terms=[Entity(name="Al"), Entity(name="Meg")]
        )
        assert not fact.means(fact_b)

    def test_unequal_because_one_factor_is_absent(self):
        predicate = Predicate(content="$shooter shot $victim")
        fact = Fact(predicate=predicate, terms=[Entity(name="Al"), Entity(name="Meg")])
        fact_b = Fact(
            predicate=predicate,
            terms=[Entity(name="Al"), Entity(name="Meg")],
            absent=True,
        )
        assert not fact.means(fact_b)

    def test_equal_with_different_generic_subfactors(self):
        shot_predicate = Predicate(content="$shooter shot $victim")
        shot_fact = Fact(
            predicate=shot_predicate, terms=[Entity(name="Alice"), Entity(name="Bob")]
        )
        murder_predicate = Predicate(content="$shooter murdered $victim")
        murder_fact = Fact(
            predicate=murder_predicate, terms=[Entity(name="Alice"), Entity(name="Bob")]
        )
        relevant_predicate = Predicate(content="$clue was relevant to $conclusion")
        relevant_fact = Fact(
            predicate=relevant_predicate, terms=[shot_fact, murder_fact]
        )

        changes = ContextRegister.from_lists(
            [Entity(name="Alice"), Entity(name="Bob")],
            [Entity(name="Deb"), Entity(name="Eve")],
        )
        new_fact = relevant_fact.new_context(changes)

        assert relevant_fact.means(new_fact)

    def test_interchangeable_concrete_terms(self):
        """Detect that placeholders differing only by a final digit are interchangeable."""
        ann = Entity(name="Ann", generic=False)
        bob = Entity(name="Bob", generic=False)

        ann_and_bob_were_family = Fact(
            predicate=Predicate(
                content="$relative1 and $relative2 both were members of the same family"
            ),
            terms=(ann, bob),
        )
        bob_and_ann_were_family = Fact(
            predicate=Predicate(
                content="$relative1 and $relative2 both were members of the same family"
            ),
            terms=(bob, ann),
        )

        assert ann_and_bob_were_family.means(bob_and_ann_were_family)

    def test_means_despite_plural(self):
        directory = Entity(name="the telephone directory", plural=False)
        listings = Entity(name="the telephone listings", plural=True)
        directory_original = Fact(
            predicate=Predicate(content="$thing was original"), terms=directory
        )
        listings_original = Fact(
            predicate=Predicate(content="$thing were original"), terms=listings
        )
        assert directory_original.means(listings_original)

    def test_same_meaning_no_terms(self):
        assert Statement(predicate=Predicate(content="good morning")).means(
            Statement(predicate=Predicate(content="good morning"))
        )


class TestImplication:
    def test_statement_implies_none(self):
        assert Statement(predicate=Predicate(content="good morning")).implies(None)

    def test_specific_statement_implies_generic(self):
        concrete = Fact(
            predicate=Predicate(content="$person was a person"),
            terms=Entity(name="Alice"),
        )
        generic = Fact(
            predicate=Predicate(content="$person was a person"),
            terms=Entity(name="Alice"),
            generic=True,
        )
        assert concrete > generic
        assert not generic > concrete

    def test_specific_implies_generic_explain(self):
        concrete = Fact(
            predicate=Predicate(content="$person was a person"),
            terms=Entity(name="Alice"),
        )
        generic = Fact(
            predicate=Predicate(content="$person was a person"),
            terms=Entity(name="Alice"),
            generic=True,
        )

        answer = concrete.explain_implication(generic)
        assert (str(concrete), generic) in answer.context.items()

    def test_specific_implies_generic_form_of_another_fact(self):
        concrete = Fact(
            predicate=Predicate(content="$person was a person"),
            terms=Entity(name="Alice"),
        )
        generic_merperson = Fact(
            predicate=Predicate(content="$person was a merperson"),
            terms=Entity(name="Alice"),
            generic=True,
        )

        assert concrete > generic_merperson

    def test_specific_fact_does_not_imply_generic_entity(self):
        concrete = Fact(
            predicate=Predicate(content="$person was a person"),
            terms=Entity(name="Alice"),
        )
        assert not concrete > Entity(name="Tim")

    def test_statement_does_not_imply_comparison(self):
        phrase = Comparison(
            content="the distance north from $south to $north was",
            sign=">",
            expression="180 miles",
        )
        statement = Fact(
            predicate=phrase, terms=[Entity(name="Austin"), Entity(name="Dallas")]
        )

        with pytest.raises(TypeError):
            statement > phrase

    def test_statement_implies_because_of_quantity(self):
        statement = Fact(
            predicate=Comparison(
                content="the distance north from $south to $north was",
                sign=">",
                expression="180 miles",
            ),
            terms=[Entity(name="Austin"), Entity(name="Dallas")],
        )
        statement_meters = Fact(
            predicate=Comparison(
                content="the distance north from $south to $north was",
                sign=">",
                expression="180 meters",
            ),
            terms=[Entity(name="Austin"), Entity(name="Dallas")],
        )

        assert statement > statement_meters

    def test_statement_implies_with_int_and_float(self):
        statement = Fact(
            predicate=Comparison(
                content="the distance north from $south to $north was",
                sign=">",
                expression=180,
            ),
            terms=[Entity(name="Austin"), Entity(name="Dallas")],
        )
        statement_float = Fact(
            predicate=Comparison(
                content="the distance north from $south to $north was",
                sign=">",
                expression=170.22,
            ),
            terms=[Entity(name="Austin"), Entity(name="Dallas")],
        )

        assert statement > statement_float

    def test_statement_implies_with_ints(self):
        statement_higher = Fact(
            predicate=Comparison(
                content="the distance north from $south to $north was",
                sign=">",
                expression=180,
            ),
            terms=[Entity(name="Austin"), Entity(name="Dallas")],
        )
        statement_lower = Fact(
            predicate=Comparison(
                content="the distance north from $south to $north was",
                sign=">",
                expression=170,
            ),
            terms=[Entity(name="Austin"), Entity(name="Dallas")],
        )

        assert statement_lower < statement_higher

    def test_statement_implies_no_truth_value(self):
        fact = Fact(
            predicate=Predicate(content="$person was a person"),
            terms=Entity(name="Alice"),
        )
        whether = Fact(
            predicate=Predicate(content="$person was a person", truth=None),
            terms=Entity(name="Alice"),
        )
        assert fact >= whether
        assert not whether > fact

    def test_comparison_implies_no_truth_value(self):
        fact = Fact(
            predicate=Comparison(
                content="${person}'s weight was", sign=">", expression="150 pounds"
            ),
            terms=Entity(name="Alice"),
        )
        whether = Fact(
            predicate=Comparison(
                content="${person}'s weight was",
                sign=">",
                expression="150 pounds",
                truth=None,
            ),
            terms=Entity(name="Alice"),
        )

        assert fact >= whether
        assert not whether > fact

    def test_factor_implies_because_of_exact_quantity(self):
        fact_exact = Fact(
            predicate=Comparison(
                content="${person}'s height was", sign="=", expression="66 inches"
            ),
            terms=Entity(name="Alice"),
        )
        fact_greater = Fact(
            predicate=Comparison(
                content="${person}'s height was", sign=">", expression="60 inches"
            ),
            terms=Entity(name="Alice"),
        )

        assert fact_exact >= fact_greater
        assert not fact_greater >= fact_exact

    def test_no_implication_pint_quantity_and_int(self):
        fact_exact = Fact(
            predicate=Comparison(
                content="${person}'s height was", sign="=", expression=66
            ),
            terms=Entity(name="Alice"),
        )
        fact_greater = Fact(
            predicate=Comparison(
                content="${person}'s height was", sign=">", expression="60 inches"
            ),
            terms=Entity(name="Alice"),
        )
        assert not fact_exact >= fact_greater
        assert not fact_greater >= fact_exact

    def test_absent_factor_implies_absent_factor_with_lesser_quantity(
        self, watt_factor
    ):
        absent_broader = Fact(
            predicate=Comparison(
                content="the distance north from $south to $north was",
                sign="<",
                expression="200 miles",
            ),
            terms=[Entity(name="Austin"), Entity(name="Dallas")],
            absent=True,
        )
        absent_narrower = Fact(
            predicate=Comparison(
                content="the distance north from $south to $north was",
                sign="<",
                expression="50 miles",
            ),
            terms=[Entity(name="Austin"), Entity(name="Dallas")],
            absent=True,
        )
        assert absent_broader >= absent_narrower
        assert not absent_narrower >= absent_broader

    def test_equal_factors_not_gt(self):
        fact = Fact(
            predicate=Predicate(content="$person was a person"),
            terms=Entity(name="Alice"),
        )
        assert fact >= fact
        assert fact <= fact
        assert not fact > fact

    shot_predicate = Predicate(content="$shooter shot $victim")
    shot_fact = Fact(
        predicate=shot_predicate, terms=[Entity(name="Alice"), Entity(name="Bob")]
    )
    murder_predicate = Predicate(content="$shooter murdered $victim")
    murder_fact = Fact(
        predicate=murder_predicate, terms=[Entity(name="Alice"), Entity(name="Bob")]
    )
    relevant_predicate = Predicate(content="$clue was relevant to $conclusion")
    relevant_fact = Fact(predicate=relevant_predicate, terms=[shot_fact, murder_fact])
    predicate_whether = Predicate(
        content="$clue was relevant to $conclusion", truth=None
    )
    relevant_whether = Fact(predicate=predicate_whether, terms=[shot_fact, murder_fact])

    def test_implication_complex_whether(self):
        assert self.relevant_fact > self.relevant_whether

    def test_implication_complex_explain(self):
        """
        Check that when .implies() provides a ContextRegister as an "explanation",
        it uses elements only from the left as keys and from the right as values.
        """

        context_names = ContextRegister()
        context_names.insert_pair(key=Entity(name="Alice"), value=Entity(name="Craig"))
        context_names.insert_pair(key=Entity(name="Bob"), value=Entity(name="Dan"))

        complex_whether = self.relevant_whether.new_context(context_names)
        explanation = self.relevant_fact.explain_implication(complex_whether)
        assert explanation.context.get("<Alice>").compare_keys(Entity(name="Craig"))
        assert "<Alice> is like <Craig>, and <Bob> is like <Dan>" in str(explanation)
        assert explanation.context.get(Entity(name="Craig").key) is None
        assert explanation.context.get(Entity(name="Alice").key).compare_keys(
            Entity(name="Craig")
        )

    def test_context_registers_for_complex_comparison(self):
        context_names = ContextRegister()
        context_names.insert_pair(key=Entity(name="Alice"), value=Entity(name="Bob"))
        context_names.insert_pair(key=Entity(name="Bob"), value=Entity(name="Alice"))

        swapped_entities = self.relevant_fact.new_context(context_names)
        gen = swapped_entities._context_registers(self.relevant_fact, operator.ge)
        register = next(gen)
        assert register.matches.get("<Alice>").compare_keys(Entity(name="Bob"))

    def test_no_implication_complex(self):
        murder_fact = Fact(
            predicate=self.murder_predicate,
            terms=[Entity(name="Alice"), Entity(name="Craig")],
        )
        relevant_to_craig = Fact(
            predicate=self.relevant_predicate, terms=[self.shot_fact, murder_fact]
        )

        assert not self.relevant_fact >= relevant_to_craig

    def test_implied_by(self):
        assert self.relevant_whether.implied_by(self.relevant_fact)

    def test_explanation_implied_by(self):
        explanation = self.relevant_whether.explain_implied_by(self.relevant_fact)
        assert explanation.context["<Alice>"].name == "Alice"


class TestContradiction:
    def test_factor_different_predicate_truth_contradicts(self):
        predicate = Comparison(
            content="the distance between $place1 and $place2 was",
            sign=">",
            expression=Q_("30 miles"),
        )
        predicate_opposite = Comparison(
            content="the distance between $place1 and $place2 was",
            sign="<",
            expression=Q_("30 miles"),
        )
        terms = [Entity(name="New York"), Entity(name="Los Angeles")]
        fact = Fact(predicate=predicate, terms=terms)
        fact_opposite = Fact(predicate=predicate_opposite, terms=terms)

        assert fact.contradicts(fact_opposite)
        assert fact_opposite.contradicts(fact)

    def test_same_predicate_true_vs_false(self):
        fact = Fact(
            predicate=Predicate(content="$person was a person"),
            terms=Entity(name="Alice"),
        )
        fiction = Fact(
            predicate=Predicate(content="$person was a person", truth=False),
            terms=Entity(name="Alice"),
        )
        assert fact.contradicts(fiction)
        assert fact.truth != fiction.truth

    def test_factor_does_not_contradict_predicate(self):
        predicate = Predicate(content="$person was a person")
        fact = Fact(predicate=predicate, terms=Entity(name="Alice"))

        with pytest.raises(TypeError):
            fact.contradicts(predicate)

    def test_factor_contradiction_absent_predicate(self):
        predicate = Predicate(content="$person was a person")
        fact = Fact(predicate=predicate, terms=Entity(name="Alice"))
        absent_fact = Fact(predicate=predicate, terms=Entity(name="Alice"), absent=True)

        assert fact.contradicts(absent_fact)
        assert absent_fact.contradicts(fact)

    def test_absences_of_contradictory_facts_consistent(self):
        predicate = Comparison(
            content="the distance between $place1 and $place2 was",
            sign=">",
            expression=Q_("30 miles"),
        )
        predicate_opposite = Comparison(
            content="the distance between $place1 and $place2 was",
            sign="<",
            expression=Q_("30 miles"),
        )
        terms = [Entity(name="New York"), Entity(name="Los Angeles")]
        fact = AbsenceOfFactor(absent=Fact(predicate=predicate, terms=terms))
        fact_opposite = AbsenceOfFactor(
            absent=Fact(predicate=predicate_opposite, terms=terms)
        )

        assert not fact.contradicts(fact_opposite)
        assert not fact_opposite.contradicts(fact)

    def test_factor_no_contradiction_no_truth_value(self):
        fact = Fact(
            predicate=Predicate(content="$person was a person"),
            terms=Entity(name="Alice"),
        )
        fact_no_truth = Fact(
            predicate=Predicate(content="$person was a person"),
            terms=Entity(name="Alice"),
        )
        assert not fact.contradicts(fact_no_truth)
        assert not fact_no_truth.contradicts(fact)

    def test_broader_absent_factor_contradicts_quantity_statement(self):
        predicate_less = Comparison(
            content="${vehicle}'s speed was",
            sign=">",
            expression=Q_("30 miles per hour"),
        )
        predicate_more = Comparison(
            content="${vehicle}'s speed was",
            sign=">",
            expression=Q_("60 miles per hour"),
        )
        terms = [Entity(name="the car")]
        absent_general_fact = AbsenceOfFactor(
            absent=Fact(predicate=predicate_less, terms=terms)
        )
        specific_fact = Fact(predicate=predicate_more, terms=terms)

        assert absent_general_fact.contradicts(specific_fact)
        assert specific_fact.contradicts(absent_general_fact)

    def test_less_specific_absent_contradicts_more_specific(self):
        predicate_less = Comparison(
            content="${vehicle}'s speed was",
            sign="<",
            expression=Q_("30 miles per hour"),
        )
        predicate_more = Comparison(
            content="${vehicle}'s speed was",
            sign="<",
            expression=Q_("60 miles per hour"),
        )
        terms = [Entity(name="the car")]
        absent_general_fact = AbsenceOfFactor(
            absent=Fact(predicate=predicate_more, terms=terms)
        )
        specific_fact = Fact(predicate=predicate_less, terms=terms)

        assert absent_general_fact.contradicts(specific_fact)
        assert specific_fact.contradicts(absent_general_fact)

    def test_no_contradiction_with_more_specific_absent(self):
        predicate_less = Comparison(
            content="${vehicle}'s speed was",
            sign="<",
            expression=Q_("30 miles per hour"),
        )
        predicate_more = Comparison(
            content="${vehicle}'s speed was",
            sign="<",
            expression=Q_("60 miles per hour"),
        )
        terms = [Entity(name="the car")]
        general_fact = Fact(predicate=predicate_more, terms=terms)
        absent_specific_fact = AbsenceOfFactor(
            absent=Fact(predicate=predicate_less, terms=terms)
        )

        assert not general_fact.contradicts(absent_specific_fact)
        assert not absent_specific_fact.contradicts(general_fact)

    def test_contradiction_complex(self):
        shot_predicate = Predicate(content="$shooter shot $victim")
        shot_fact = Fact(
            predicate=shot_predicate, terms=[Entity(name="Alice"), Entity(name="Bob")]
        )
        murder_predicate = Predicate(content="$shooter murdered $victim")
        murder_fact = Fact(
            predicate=murder_predicate, terms=[Entity(name="Alice"), Entity(name="Bob")]
        )
        relevant_predicate = Predicate(content="$clue was relevant to $conclusion")
        relevant_fact = Fact(
            predicate=relevant_predicate, terms=[shot_fact, murder_fact]
        )
        irrelevant_predicate = Predicate(
            content="$clue was relevant to $conclusion", truth=False
        )
        irrelevant_fact = Fact(
            predicate=irrelevant_predicate, terms=[shot_fact, murder_fact]
        )
        assert relevant_fact.contradicts(irrelevant_fact)

    def test_no_contradiction_complex(self):
        shot_predicate = Predicate(content="$shooter shot $victim")
        shot_fact = Fact(
            predicate=shot_predicate, terms=[Entity(name="Alice"), Entity(name="Bob")]
        )
        murder_predicate = Predicate(content="$shooter murdered $victim")
        murder_fact = Fact(
            predicate=murder_predicate, terms=[Entity(name="Alice"), Entity(name="Bob")]
        )
        murder_socrates = Fact(
            predicate=murder_predicate,
            terms=[Entity(name="Alice"), Entity(name="Socrates")],
        )
        relevant_predicate = Predicate(content="$clue was relevant to $conclusion")
        relevant_fact = Fact(
            predicate=relevant_predicate, terms=[shot_fact, murder_fact]
        )
        irrelevant_predicate = Predicate(
            content="$clue was relevant to $conclusion", truth=False
        )
        irrelevant_fact = Fact(
            predicate=irrelevant_predicate, terms=[shot_fact, murder_socrates]
        )
        assert not relevant_fact.contradicts(irrelevant_fact)
        assert not irrelevant_fact.contradicts(relevant_fact)

    def test_no_contradiction_of_None(self):
        shot_predicate = Predicate(content="$shooter shot $victim")
        shot_fact = Fact(
            predicate=shot_predicate, terms=[Entity(name="Alice"), Entity(name="Bob")]
        )
        assert not shot_fact.contradicts(None)

    def test_contradicts_if_present_both_present(self):
        """
        Test a helper function that checks whether there would
        be a contradiction if neither Factor was "absent".
        """
        shot_fact = Fact(
            predicate=Predicate(content="$shooter shot $victim"),
            terms=[Entity(name="Alice"), Entity(name="Bob")],
        )
        shot_false = Fact(
            predicate=Predicate(content="$shooter shot $victim", truth=False),
            terms=[Entity(name="Alice"), Entity(name="Bob")],
        )
        assert shot_fact._contradicts_if_present(shot_false, ContextRegister())
        assert shot_false._contradicts_if_present(shot_fact, ContextRegister())

    def test_contradicts_if_present_one_absent(self):
        shot_fact = Fact(
            predicate=Predicate(content="$shooter shot $victim"),
            terms=[Entity(name="Alice"), Entity(name="Bob")],
        )
        shot_false = AbsenceOfFactor(
            absent=Fact(
                predicate=Predicate(content="$shooter shot $victim", truth=False),
                terms=[Entity(name="Alice"), Entity(name="Bob")],
            )
        )
        assert shot_fact._contradicts_if_present(shot_false, ContextRegister())
        assert shot_false._contradicts_if_present(shot_fact, ContextRegister())

    def test_false_does_not_contradict_absent(self):
        absent_fact = AbsenceOfFactor(
            absent=Fact(
                predicate=Predicate(
                    content="${rural_s_telephone_directory} was copyrightable",
                    truth=True,
                ),
                terms=(Entity(name="Rural's telephone directory")),
            )
        )
        false_fact = Fact(
            predicate=Predicate(
                content="${the_java_api} was copyrightable", truth=False
            ),
            terms=(Entity(name="the Java API", generic=True, plural=False)),
        )
        assert not false_fact.contradicts(absent_fact)
        assert not absent_fact.contradicts(false_fact)

    def test_inconsistent_statements_about_different_entities(self):
        """
        Alice and Bob are both generics. So it's possible to reach a
        contradiction if you assume they correspond to one another.
        """
        p_small_weight = Comparison(
            content="the amount of gold $person possessed was",
            sign="<",
            expression=Q_("1 gram"),
        )
        p_large_weight = Comparison(
            content="the amount of gold $person possessed was",
            sign=">=",
            expression=Q_("100 kilograms"),
        )
        alice = Entity(name="Alice")
        bob = Entity(name="Bob")
        alice_rich = Fact(predicate=p_large_weight, terms=alice)
        bob_poor = Fact(predicate=p_small_weight, terms=bob)
        assert alice_rich.contradicts(bob_poor)

    def test_inconsistent_statements_about_corresponding_entities(self):
        """
        Even though Alice and Bob are both generics, it's known that
        Alice in the first context corresponds with Alice in the second.
        So there's no contradiction.
        """
        p_small_weight = Comparison(
            content="the amount of gold $person possessed was",
            sign="<",
            expression=Q_("1 gram"),
        )
        p_large_weight = Comparison(
            content="the amount of gold $person possessed was",
            sign=">=",
            expression=Q_("100 kilograms"),
        )
        alice = Entity(name="Alice")
        bob = Entity(name="Bob")
        alice_rich = Fact(predicate=p_large_weight, terms=alice)
        bob_poor = Fact(predicate=p_small_weight, terms=bob)
        register = ContextRegister()
        register.insert_pair(alice, alice)
        assert not alice_rich.contradicts(bob_poor, context=register)

    def test_check_entity_consistency_true(self):
        left = Fact(
            predicate=Predicate(content="$shooter shot $victim"),
            terms=[Entity(name="Alice"), Entity(name="Bob")],
        )
        right = Fact(
            predicate=Predicate(content="$shooter shot $victim"),
            terms=[Entity(name="Craig"), Entity(name="Dan")],
        )
        register = ContextRegister.from_lists(
            [Entity(name="Alice")], [Entity(name="Craig")]
        )
        update = left.update_context_register(right, register, comparison=means)
        assert any(register is not None for register in update)

    def test_check_entity_consistency_false(self):
        left = Fact(
            predicate=Predicate(content="$shooter shot $victim"),
            terms=[Entity(name="Alice"), Entity(name="Bob")],
        )
        right = Fact(
            predicate=Predicate(content="$shooter shot $victim"),
            terms=[Entity(name="Craig"), Entity(name="Dan")],
        )
        register = ContextRegister.from_lists(
            [Entity(name="Alice")], [Entity(name="Dan")]
        )
        update = left.update_context_register(right, register, comparison=means)
        assert not any(register is not None for register in update)

    def test_entity_consistency_identity_not_equality(self):
        left = Fact(
            predicate=Predicate(content="$shooter shot $victim"),
            terms=[Entity(name="Alice"), Entity(name="Bob")],
        )
        right = Fact(
            predicate=Predicate(content="$shooter shot $victim"),
            terms=[Entity(name="Craig"), Entity(name="Dan")],
        )
        register = ContextRegister.from_lists(
            [Entity(name="Dan")], [Entity(name="Dan")]
        )
        update = left.update_context_register(right, register, comparison=means)
        assert not any(register is not None for register in update)

    def test_check_entity_consistency_type_error(
        self, make_entity, make_factor, make_predicate
    ):
        """
        There would be no TypeError if it used "means"
        instead of .gt. The comparison would just return False.
        """
        right = Fact(
            predicate=Predicate(content="$shooter shot $victim"),
            terms=[Entity(name="Craig"), Entity(name="Dan")],
        )
        register = ContextRegister.from_lists(
            [Entity(name="Dan")], [Entity(name="Dan")]
        )
        update = right.update_context_register(
            right.predicate,
            register,
            operator.gt,
        )
        with pytest.raises(TypeError):
            any(register is not None for register in update)


class TestConsistent:
    p_small_weight = Comparison(
        content="the amount of gold $person possessed was",
        sign="<",
        expression=Q_("1 gram"),
    )
    p_large_weight = Comparison(
        content="the amount of gold $person possessed was",
        sign=">=",
        expression=Q_("100 kilograms"),
    )
    small = Fact(predicate=p_large_weight, terms=Entity(name="Alice"))
    big = Fact(predicate=p_small_weight, terms=Entity(name="Bob"))

    def test_contradictory_facts_about_same_entity(self):
        register = ContextRegister()
        register.insert_pair(Entity(name="Alice"), Entity(name="Bob"))
        assert not self.small.consistent_with(self.big, register)
        explanations = list(
            self.small.explanations_consistent_with(self.big, context=register)
        )
        assert not explanations

    def test_factor_consistent_with_none(self):
        assert self.small.consistent_with(None)


class TestAddition:
    predicate_less = Comparison(
        content="${vehicle}'s speed was",
        sign=">",
        expression=Q_("30 miles per hour"),
    )
    predicate_more = Comparison(
        content="${vehicle}'s speed was",
        sign=">=",
        expression=Q_("60 miles per hour"),
    )
    general_fact = Fact(predicate=predicate_less, terms=Entity(name="the car"))
    specific_fact = Fact(predicate=predicate_more, terms=Entity(name="the motorcycle"))

    def test_addition_returns_broader_operand(self):
        answer = self.specific_fact + self.general_fact
        assert answer.means(self.specific_fact)

    def test_addition_uses_terms_from_left(self):
        answer = self.general_fact + self.specific_fact
        assert "<the car>" in str(answer)

    def test_add_unrelated_factors(self):
        murder = Fact(
            predicate=Predicate(content="$person committed a murder"),
            terms=Entity(name="Al"),
        )
        crime = Fact(
            predicate=Predicate(content="$person committed a crime"),
            terms=Entity(name="Al"),
        )
        assert murder + crime is None

    def test_union_with_string_fails(self):
        murder = Fact(
            predicate=Predicate(content="$person committed a murder"),
            terms=Entity(name="Al"),
        )
        with pytest.raises(TypeError):
            murder | "a string"
