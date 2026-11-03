from authorityspoke.nettlesome.terms import ContextRegister, means
from authorityspoke.nettlesome.entities import Entity
from authorityspoke.nettlesome import Predicate

from authorityspoke import Fact


class TestContext:
    predicate = Predicate(content="{seller} sold {item} to {buyer}")
    fact_al = Fact(
        predicate=predicate,
        terms=[
            Entity(name="Al"),
            Entity(name="the bull"),
            Entity(name="Betty"),
        ],
    )
    fact_alice = Fact(
        predicate=predicate,
        terms=[
            Entity(name="Alice"),
            Entity(name="the cow"),
            Entity(name="Bob"),
        ],
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
        assert Entity(name="the bull").key in next(answers).keys()

    def test_explain_consistency(self):
        register = ContextRegister()
        register.insert_pair(Entity(name="Al"), Entity(name="Alice"))
        explanation = self.fact_al.explain_consistent_with(self.fact_alice, register)
        assert "<the bull> is like <the cow>" in str(explanation.context)


class TestExplainHoldings:
    def test_explain_implication(self, make_decision_with_holding):
        oracle = make_decision_with_holding["oracle"]
        left = oracle.holdings[18]
        right = oracle.holdings[19]
        explanation = left.explain_implication(right)

        assert "implies" in str(explanation).lower()
