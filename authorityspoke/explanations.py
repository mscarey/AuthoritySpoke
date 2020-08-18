"""Objects describing relationships between pairs of Factors or Opinions."""
from __future__ import annotations

from dataclasses import dataclass
import operator
import textwrap
from typing import Callable, ClassVar, List, Optional, Tuple

from authorityspoke.comparisons import ContextRegister, means, contradicts
from authorityspoke.factors import Factor


class Matches(List[Tuple[Factor, Factor]]):
    def get_factor_by_str(self, query: str) -> Optional[Factor]:
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


@dataclass
class Explanation:
    matches: Matches
    context: Optional[ContextRegister] = None
    operation: Callable = operator.ge

    operation_names: ClassVar = {
        operator.ge: "IMPLIES",
        means: "MEANS",
        contradicts: "CONTRADICTS",
    }

    def __post_init__(self):
        if not isinstance(self.matches, Matches):
            self.matches = Matches(self.matches)

    @property
    def reason(self) -> str:
        """Make statement matching analagous context factors of self and other."""
        if self.context:
            similies = [
                f'{key} {"are" if self.matches.is_factor_plural(key) else "is"} like {value}'
                for key, value in self.context.items()
            ]
            if len(similies) > 1:
                similies[-2:] = [", and ".join(similies[-2:])]
            return ", ".join(similies)
        return ""

    def __str__(self):
        indent = "  "
        relation = self.operation_names[self.operation]
        context_text = f" Because {self.reason},\n" if self.context else "\n"
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
