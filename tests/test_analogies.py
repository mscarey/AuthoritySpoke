import operator

import pytest

from authorityspoke.entities import Entity
from authorityspoke.factors import Analogy, Factor
from authorityspoke.factors import ContextRegister, means
from authorityspoke.facts import Fact
from authorityspoke.io.readers import read_fact
from authorityspoke.io.text_expansion import expand_shorthand


class TestAnalogies:
    def test_analogy_has_comparison(self, make_entity):
        """
        Is the VS Code debugger refusing to show callable attributes?
        This problem started with VS Code v. 1.37
        """
        test_analogy = Analogy(
            need_matches=[make_entity["bob"]],
            available=[make_entity["craig"]],
            comparison=operator.ge,
        )
        assert test_analogy.comparison == operator.ge


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
