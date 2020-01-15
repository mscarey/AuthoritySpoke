"""Objects describing relationships between pairs of Factors or Opinions."""
from __future__ import annotations

from dataclasses import dataclass
import operator
import textwrap
from typing import Callable, ClassVar, List, Optional, Tuple

from authorityspoke.comparisons import ContextRegister
from authorityspoke.factors import Factor, means, contradicts


@dataclass
class Explanation:
    matches: List[Tuple[Factor, Factor]]
    context: Optional[ContextRegister] = None
    operation: Callable = operator.ge

    operation_names: ClassVar = {
        operator.ge: "IMPLIES",
        means: "MEANS",
        contradicts: "CONTRADICTS",
    }

    def __str__(self):
        indent = "  "
        relation = self.operation_names[self.operation]
        context_text = f" Because {self.context.prose},\n" if self.context else "\n"
        text = f"EXPLANATION:{context_text}"
        for match in self.matches:
            left = textwrap.indent(str(match[0]), prefix=indent)
            right = textwrap.indent(str(match[1]), prefix=indent)
            match_text = f"{left}\n" f"{relation}\n" f"{right}\n"
            text += match_text
        return text.rstrip("\n")

    def add_match(self, match=Tuple[Factor, Factor]) -> Explanation:
        new_matches = self.matches + [match]
        return Explanation(
            matches=new_matches, context=self.context, operation=self.operation,
        )
