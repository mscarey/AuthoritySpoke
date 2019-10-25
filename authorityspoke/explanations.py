from dataclasses import dataclass
import textwrap

from authorityspoke.factors import ContextRegister, Factor


@dataclass(frozen=True)
class Explanation:
    needs_match: Factor
    available: Factor
    context: ContextRegister

    def __str__(self):
        indent = "  "
        needs_match_text = textwrap.indent(str(self.needs_match), prefix=indent)
        available_text = textwrap.indent(str(self.available), prefix=indent)
        inconsistent = self.needs_match.new_context(self.context)
        inconsistent_text = textwrap.indent(str(inconsistent), prefix=indent)
        text = (
            f"the Explanation of why there is a contradiction between\n"
            f"{needs_match_text}\n"
            f"and\n"
            f"{available_text}\n"
            "is that it would be inconsistent to say:\n"
            f"{inconsistent_text}"
        )
        return text
