import operator

import pytest

from authorityspoke.factors import Analogy, Factor, ContextRegister, means
from authorityspoke.facts import Fact


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
