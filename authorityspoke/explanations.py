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
        similies = [f"{key} is like {value}" for key, value in self.context.items()]
        similies_text = ", ".join(similies)
        text = (
            f"an Explanation of why there is a contradiction between\n"
            f"{needs_match_text}\n"
            f"and\n"
            f"{available_text}\n"
            f"is that {similies_text}"
        )
        return text
