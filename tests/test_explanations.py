from nettlesome.terms import ContextRegister, means, Explanation
from nettlesome.entities import Entity

from authorityspoke.io.readers import read_fact
from authorityspoke.io.text_expansion import expand_shorthand


class TestContext:
    al = expand_shorthand({"content": "{Al} sold {the bull} to {Betty}."})
    alice = expand_shorthand({"content": "{Alice} sold {the cow} to {Bob}."})

    def test_impossible_register(self):
        fact_al = read_fact(self.al)
        fact_alice = read_fact(self.alice)
        context = ContextRegister()
        context.insert_pair(Entity("Al"), Entity("Bob"))
        answers = fact_al.update_context_register(fact_alice, context, means)
        assert not any(answers)

    def test_possible_register(self):
        fact_al = read_fact(self.al)
        fact_alice = read_fact(self.alice)
        register = ContextRegister()
        register.insert_pair(Entity("Al"), Entity("Alice"))
        answers = fact_al.update_context_register(fact_alice, register, means)
        assert Entity("the bull").key in next(answers).keys()

    def test_explain_consistency(self):
        fact_al = read_fact(self.al)
        fact_alice = read_fact(self.alice)
        register = ContextRegister()
        register.insert_pair(Entity("Al"), Entity("Alice"))
        explanation = fact_al.explain_consistent_with(fact_alice, register)
        assert "<the bull> is like <the cow>" in str(explanation.context)


class TestExplainHoldings:
    def test_explain_implication(self, make_decision_with_holding):
        oracle = make_decision_with_holding["oracle"]
        left = oracle.holdings[18]
        right = oracle.holdings[19]
        explanation = left.explain_implication(right)

        assert "implies" in str(explanation).lower()
