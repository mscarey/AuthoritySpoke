from nettlesome.terms import ContextRegister, means, Explanation
from nettlesome.entities import Entity
from nettlesome import Predicate

from authorityspoke import Fact
from authorityspoke.io.text_expansion import expand_shorthand


class TestContext:
    al = expand_shorthand({"content": "{Al} sold {the bull} to {Betty}."})
    alice = expand_shorthand({"content": "{Alice} sold {the cow} to {Bob}."})

    predicate = Predicate(content="$seller sold $item to $buyer")
    fact_al = Fact(
        predicate=predicate,
        terms={
            "seller": Entity(name="Al"),
            "item": Entity(name="the bull"),
            "buyer": Entity(name="Betty"),
        },
    )
    fact_alice = Fact(
        predicate=predicate,
        terms={
            "seller": Entity(name="Alice"),
            "item": Entity(name="the cow"),
            "buyer": Entity(name="Bob"),
        },
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
