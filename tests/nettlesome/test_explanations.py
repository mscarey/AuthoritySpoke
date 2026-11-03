import operator

import pytest

from authorityspoke.nettlesome.terms import (
    ContextRegister,
    Explanation,
    consistent_with,
    contradicts,
    means,
)
from authorityspoke.nettlesome.predicates import Predicate
from authorityspoke.nettlesome.quantities import Comparison
from authorityspoke.nettlesome.statements import Statement
from authorityspoke.nettlesome.entities import Entity
from authorityspoke.nettlesome.groups import FactorGroup


class TestContext:
    sale = Predicate(content="{seller} sold {product} to {buyer}")
    fact_al = Statement(
        predicate=sale,
        terms=[Entity(name="Al"), Entity(name="the bull"), Entity(name="Betty")],
    )
    fact_alice = Statement(
        predicate=sale,
        terms=[Entity(name="Alice"), Entity(name="the cow"), Entity(name="Bob")],
    )

    def test_impossible_register(self):
        context = ContextRegister()
        context.insert_pair(Entity(name="Al"), Entity(name="Bob"))
        answers = self.fact_al.update_context_register(self.fact_alice, context, means)
        assert not any(answers)

    def test_possible_register(self):
        register = ContextRegister()
        register.insert_pair(Entity(name="Al"), Entity(name="Alice"))
        answers = self.fact_al.update_context_register(self.fact_alice, register, means)
        assert Entity(name="the bull").short_string in next(answers).keys()

    def test_explain_consistency(self):
        register = ContextRegister()
        register.insert_pair(Entity(name="Al"), Entity(name="Alice"))
        explanation = self.fact_al.explain_consistent_with(self.fact_alice, register)

        assert (
            explanation and "<the bull> is like <the cow>" in explanation.context.reason
        )
        assert "Entity(generic=True, name='Al'" in repr(explanation)


class TestMakeExplanation:
    def test_context_type(self, make_statement):
        explanation = make_statement["large_weight"].explain_implication(
            make_statement["small_weight"]
        )
        with pytest.raises(TypeError):
            Explanation(reasons=[], context=explanation)


class TestContinuedExplanation:
    def test_implication_and_contradiction(self):
        lived_at = Predicate(content="{person} lived at {residence}")
        bob_lived = Statement(
            predicate=lived_at, terms=[Entity(name="Bob"), Entity(name="Bob's house")]
        )
        carl_lived = Statement(
            predicate=lived_at, terms=[Entity(name="Carl"), Entity(name="Carl's house")]
        )
        explanation = bob_lived.explain_implication(carl_lived)

        distance_long = Comparison.new(
            content="the distance from the center of {city} to {residence} was",
            sign=">=",
            expression="50 miles",
        )
        statement_long = Statement(
            predicate=distance_long,
            terms=[Entity(name="Houston"), Entity(name="Bob's house")],
        )

        distance_short = Comparison.new(
            content="the distance from the center of {city} to {residence} was",
            sign="<=",
            expression="10 kilometers",
        )
        statement_short = Statement(
            predicate=distance_short,
            terms=[Entity(name="El Paso"), Entity(name="Carl's house")],
        )

        left = FactorGroup(sequence=[statement_long])
        right = FactorGroup(sequence=[statement_short])
        new_explanation = left.explain_contradiction(right, context=explanation)

        expected = "the statement that <bob> lived at <bob's house>"
        assert new_explanation.reasons[0].left.key.lower() == expected
        assert new_explanation.reasons[0].operation == operator.ge

        part = "from the center of <houston> to <bob's house> was at least 50 mile"
        assert part in new_explanation.reasons[1].left.key.lower()
        assert new_explanation.reasons[1].operation == contradicts

    def test_two_implying_groups(self, make_statement):
        left_weight = FactorGroup(sequence=[make_statement["large_weight"]])
        right_weight = FactorGroup(sequence=[make_statement["small_weight"]])
        explanation = left_weight.explain_implication(right_weight)
        left_more = FactorGroup(sequence=[make_statement["way_more"]])
        right_more = FactorGroup(sequence=[make_statement["more"]])
        new = left_more.explain_implication(right_more, context=explanation)
        assert len(new.reasons) == 2
        assert new.reasons[0].operation == operator.ge
        assert new.reasons[1].operation == operator.ge

    def test_consistent_and_same_meaning(self, make_statement):
        left_weight = FactorGroup(sequence=[make_statement["small_weight_bob"]])
        right_weight = FactorGroup(sequence=[make_statement["large_weight"]])
        explanation = left_weight.explain_consistent_with(right_weight)
        new_explanation = make_statement["crime_bob"].explain_same_meaning(
            make_statement["crime"], context=explanation
        )
        assert "Because <Bob> is like <Alice>" in str(new_explanation)
        assert "FactorGroup(sequence=[" not in str(new_explanation)

    def test_same_meaning_factors_not_grouped(self, make_statement):
        left_weight = FactorGroup(sequence=[make_statement["small_weight_bob"]])
        right_weight = FactorGroup(sequence=[make_statement["large_weight"]])
        explanation = left_weight.explain_consistent_with(right_weight)
        new = FactorGroup(sequence=[make_statement["crime_bob"]]).explain_same_meaning(
            FactorGroup(sequence=[make_statement["crime"]]), context=explanation
        )
        assert "Because <Bob> is like <Alice>" in str(new)
        assert new.reasons[1].operation == means
        assert "was at least 100 kilogram, and the statement" in new.short_string

    def test_means_to_contradicts(self, make_statement):
        explanation = make_statement["crime"].explain_same_meaning(
            make_statement["crime_bob"]
        )
        left = FactorGroup(
            sequence=[make_statement["shooting_craig"], make_statement["less"]]
        )
        right = FactorGroup(
            sequence=[make_statement["murder_craig"], make_statement["more"]]
        )
        new = left.explain_contradiction(right, context=explanation)
        assert len(new.reasons) == 2
        assert new.reasons[1].operation == contradicts

    def test_same_meaning_long_group(self, make_statement):
        explanation = make_statement["crime"].explain_same_meaning(
            make_statement["crime_craig"]
        )
        left = FactorGroup(
            sequence=[
                make_statement["large_weight"],
                make_statement["murder"],
                make_statement["no_context"],
                make_statement["shooting"],
            ]
        )
        right = FactorGroup(
            sequence=[
                make_statement["large_weight_craig"],
                make_statement["murder_craig"],
                make_statement["shooting_craig"],
                make_statement["no_context"],
            ]
        )
        new = left.explain_same_meaning(right, explanation)
        assert len(new.reasons) == 5

    def test_not_same_meaning_no_factor_match(self, make_statement):
        explanation = make_statement["crime_craig"].explain_same_meaning(
            make_statement["crime"]
        )
        left = FactorGroup(
            sequence=[
                make_statement["large_weight"],
                make_statement["murder_entity_order"],
                make_statement["no_context"],
                make_statement["shooting"],
            ]
        )
        right = FactorGroup(
            sequence=[
                make_statement["large_weight_craig"],
                make_statement["murder_craig"],
                make_statement["shooting_craig"],
                make_statement["no_context"],
            ]
        )
        new = right.explain_same_meaning(left, explanation)
        assert new is None


class TestApplyOperation:
    def test_means_to_contradicts_from_explanation(self, make_statement):
        explanation = make_statement["crime"].explain_same_meaning(
            make_statement["crime_bob"]
        )
        left = FactorGroup(
            sequence=[make_statement["shooting_craig"], make_statement["less"]]
        )
        right = FactorGroup(
            sequence=[make_statement["murder_craig"], make_statement["more"]]
        )
        explanation.operation = contradicts
        gen = explanation.operate(left, right)
        new = next(gen)
        assert len(new.reasons) == 2
        assert new.reasons[1].operation == contradicts

    def test_means_to_consistent_from_explanation(self, make_statement):
        explanation = make_statement["crime"].explain_same_meaning(
            make_statement["crime_bob"]
        )
        left = FactorGroup(
            sequence=[make_statement["shooting_craig"], make_statement["less"]]
        )
        right = FactorGroup(
            sequence=[make_statement["murder_craig"], make_statement["more"]]
        )
        explanation.operation = consistent_with
        gen = explanation.operate(left, right)
        new = next(gen)
        assert len(new.reasons) == 2
        assert new.reasons[1].operation == consistent_with
        assert isinstance(new.reasons[1].left, FactorGroup)

    def test_means_to_implied_by(self, make_statement):
        explanation = make_statement["crime_bob"].explain_same_meaning(
            make_statement["crime"]
        )
        left = FactorGroup(sequence=[make_statement["small_weight_bob"]])
        right = FactorGroup(sequence=[make_statement["large_weight"]])
        new = left.explain_implied_by(right, explanation)
        assert len(new.reasons) == 2
        assert new.reasons[1].operation == operator.ge

    def test_cannot_apply_lt(self, make_statement):
        explanation = make_statement["crime"].explain_same_meaning(
            make_statement["crime_bob"]
        )
        left = FactorGroup(
            sequence=[make_statement["shooting_craig"], make_statement["less"]]
        )
        right = FactorGroup(
            sequence=[make_statement["murder_craig"], make_statement["more"]]
        )
        explanation.operation = operator.lt
        gen = explanation.operate(left, right)
        with pytest.raises(ValueError):
            next(gen)


class TestSameMeaning:
    def test_same_meaning(self, make_statement):
        left = make_statement["shooting"].explain_same_meaning(
            make_statement["shooting_craig"]
        )
        right = make_statement["shooting"].explain_same_meaning(
            make_statement["shooting_craig"]
        )
        assert left.means(right)

    def test_not_same_meaning(self, make_statement):
        left = make_statement["shooting"].explain_same_meaning(
            make_statement["shooting_craig"]
        )
        right = make_statement["murder"].explain_same_meaning(
            make_statement["murder_craig"]
        )
        assert not left.means(right)

    def test_not_same_meaning_more_reasons(self, make_statement):
        left = FactorGroup(
            sequence=[make_statement["shooting"], make_statement["crime"]]
        ).explain_same_meaning(
            FactorGroup(
                sequence=[
                    make_statement["shooting_craig"],
                    make_statement["crime_craig"],
                ]
            )
        )
        right = make_statement["murder"].explain_same_meaning(
            make_statement["murder_craig"]
        )
        assert not left.means(right)

    def test_not_same_meaning_as_contextregister(self, make_statement):
        left = make_statement["shooting"].explain_same_meaning(
            make_statement["shooting_craig"]
        )
        right = make_statement["murder"].explain_same_meaning(
            make_statement["murder_craig"]
        )
        assert not left.means(right.context)
        assert not right.context.means(left)
