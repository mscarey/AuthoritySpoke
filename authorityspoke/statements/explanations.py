"""Objects describing relationships between pairs of Comparables or Opinions."""
from __future__ import annotations

import operator
import textwrap
from typing import Callable, ClassVar, Dict, List, Optional, Tuple

from authorityspoke.statements.comparable import (
    Comparable,
    ContextRegister,
    means,
    contradicts,
)


class Matches(List[Tuple[Comparable, Comparable]]):
    def get_factor_by_str(self, query: str) -> Optional[Comparable]:
        for pair in self:
            for item in pair:
                if str(item) == query:
                    return item
        return None

    def is_factor_plural(self, name: str) -> bool:
        factor = self.get_factor_by_str(name)
        if factor and factor.__dict__.get("plural") is True:
            return True
        return False


class Explanation:

    operation_names: ClassVar[Dict[Callable, str]] = {
        operator.ge: "IMPLIES",
        means: "MEANS",
        contradicts: "CONTRADICTS",
    }

    def __init__(
        self,
        factor_matches: Matches,
        context: Optional[ContextRegister] = None,
        operation: Callable = operator.ge,
    ):
        self.factor_matches = factor_matches
        self.context = context or ContextRegister()
        self.operation = operation

    @property
    def reason(self) -> str:
        """Make statement matching analagous context factors of self and other."""

        similies = [
            f'{key} {"are" if (key.plural) else "is"} like {value}'
            for key, value in self.context.factor_pairs()
        ]
        if len(similies) > 1:
            similies[-2:] = [", and ".join(similies[-2:])]
        return ", ".join(similies)

    def __str__(self):
        indent = "  "
        relation = self.operation_names[self.operation]
        context_text = f" Because {self.reason},\n" if self.context else "\n"
        text = f"EXPLANATION:{context_text}"
        for match in self.factor_matches:
            left = textwrap.indent(str(match[0]), prefix=indent)
            right = textwrap.indent(str(match[1]), prefix=indent)
            match_text = f"{left}\n" f"{relation}\n" f"{right}\n"
            text += match_text
        return text.rstrip("\n")

    def __repr__(self) -> str:
        return f"Explanation(matches={repr(self.factor_matches)}, context={repr(self.context)}), operation={repr(self.operation)})"

    def add_match(self, match=Tuple[Comparable, Comparable]) -> Explanation:
        new_matches = self.factor_matches + [match]
        return Explanation(
            factor_matches=new_matches,
            context=self.context,
            operation=self.operation,
        )
