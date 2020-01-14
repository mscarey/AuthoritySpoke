"""Objects describing relationships between pairs of Factors or Opinions."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
import operator
from typing import Callable, ClassVar, List, Optional, Tuple

from authorityspoke.factors import ContextRegister, Factor, means


@dataclass
class Explanation:
    matches: List[Tuple[Factor, Factor]]
    context: ContextRegister
    operation: Callable = operator.ge

    operation_names: ClassVar = {operator.ge: "IMPLIES", means: "MEANS"}

    def __str__(self):
        text = ""
        relation = self.operation_names[self.operation]
        for match in self.matches:
            text += f"{match[0].short_string} {relation} {match[1].short_string}\n"
        if self.context:
            text += self.context.prose
        return text.rstrip("\n")

    def add_match(self, match=Tuple[Factor, Factor]) -> Explanation:
        new_matches = self.matches + [match]
        return Explanation(
            matches=new_matches, context=self.context, operation=self.operation,
        )
