from authorityspoke.entities import Entity
from authorityspoke.factors import ContextRegister, means
from authorityspoke.io.readers import read_fact
from authorityspoke.io.text_expansion import expand_shorthand


class TestContext:
    al = expand_shorthand({"content": "{Al} sold {the bull} to {Betty}."})
    alice = expand_shorthand({"content": "{Alice} sold {the cow} to {Bob}."})

    def test_impossible_register(self):
        fact_al = read_fact(self.al)
        fact_alice = read_fact(self.alice)
        context = ContextRegister({Entity("Al"): Entity("Bob")})
        answers = fact_al.update_context_register(fact_alice, context, means)
        assert not any(answers)

    def test_possible_register(self):
        fact_al = read_fact(self.al)
        fact_alice = read_fact(self.alice)
        context = ContextRegister({Entity("Al"): Entity("Alice")})
        answers = fact_al.update_context_register(fact_alice, context, means)
        assert Entity("the bull") in next(answers).keys()
