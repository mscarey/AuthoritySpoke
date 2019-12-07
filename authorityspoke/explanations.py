"""Objects describing relationships between pairs of Factors or Opinions."""

from dataclasses import dataclass
import textwrap

from authorityspoke.factors import ContextRegister, Factor


@dataclass(frozen=True)
class Explanation:
    needs_match: Factor
    available: Factor
    context: ContextRegister
    relation: str = "IMPLICATION"

    def __str__(self):
        indent = "  "
        needs_match_text = textwrap.indent(str(self.needs_match), prefix=indent)
        available_text = textwrap.indent(str(self.available), prefix=indent)

        text = (
            f"an Explanation of why there is a {self.relation} between\n"
            f"{needs_match_text}\n"
            f"and\n"
            f"{available_text}\n"
            f"is that {self.context.prose}"
        )
        return text
