import operator

import pytest

from authorityspoke.factors import Analogy, Entity, Factor
from authorityspoke.factors import ContextRegister, means
from authorityspoke.facts import Fact
from authorityspoke.io.readers import read_fact


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
    def test_impossible_register(self):
        fact_al = read_fact("{Al} sold {the bull} to {Betty}.")
        fact_alice = read_fact("{Alice} sold {the cow} to {Bob}.")
        context = ContextRegister({Entity("Al"): Entity("Bob")})
        analogy = Analogy(
            need_matches=[fact_al], available=[fact_alice], comparison=means
        )
        answers = analogy.ordered_comparison(matches=context)
        assert not any(answers)

    def test_possible_register(self):
        fact_al = read_fact("{Al} sold {the bull} to {Betty}.")
        fact_alice = read_fact("{Alice} sold {the cow} to {Bob}.")
        context = ContextRegister({Entity("Al"): Entity("Alice")})
        analogy = Analogy(
            need_matches=[fact_al], available=[fact_alice], comparison=means
        )
        answer = next(analogy.ordered_comparison(matches=context))
        assert Entity("the bull") in answer.keys()
