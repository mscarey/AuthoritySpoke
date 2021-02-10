from authorityspoke.statements.comparable import ContextRegister, means
from authorityspoke.statements.entities import Entity
from authorityspoke.statements.explanations import Explanation
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
        assert str(Entity("the bull")) in next(answers).keys()

    def test_explain_consistency(self):
        fact_al = read_fact(self.al)
        fact_alice = read_fact(self.alice)
        register = ContextRegister()
        register.insert_pair(Entity("Al"), Entity("Alice"))
        answers = fact_al.explain_consistent_with(fact_alice, register)
        explanation = Explanation(
            factor_matches=[(fact_al, fact_alice)], context=answers
        )
        assert "<the bull> is like <the cow>" in explanation.reason


class TestExplainHoldings:
    def test_explain_implication(self, make_decision_with_holding):
        oracle = make_decision_with_holding["oracle"]
        context = oracle.holdings[18].explain_implication(oracle.holdings[19])
        explanation = Explanation(
            factor_matches=[(oracle.holdings[18], oracle.holdings[19])], context=context
        )
        assert "implies" in str(explanation).lower()
