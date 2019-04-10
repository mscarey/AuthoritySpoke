from typing import Dict, List, Tuple
from typing import Optional, Sequence, Union

import datetime
import json
import pathlib

from dataclasses import dataclass

from authorityspoke.context import get_directory_path
from authorityspoke.factors import Factor
from authorityspoke.rules import Rule, ProceduralRule


@dataclass
class Opinion:
    """A document that resolves legal issues in a case and posits legal holdings.
    Usually only a majority opinion will create holdings binding on any courts.
    """

    name: str
    name_abbreviation: str
    citations: Tuple[str]
    first_page: int
    last_page: int
    decision_date: datetime.date
    court: str
    position: str
    author: str

    directory = get_directory_path("opinions")

    def __post_init__(self):
        self.holdings = []

    @classmethod
    def from_file(cls, filename: str):
        """This is a generator that gets one opinion from a
        Harvard-format case file every time it's called. Exhaust the
        generator to get the lead opinion and all non-lead opinions."""

        with open(cls.directory / filename, "r") as f:
            opinion_dict = json.load(f)

        citations = tuple(c["cite"] for c in opinion_dict["citations"])

        for opinion in opinion_dict["casebody"]["data"]["opinions"]:
            author = None
            position = opinion["type"]
            author = opinion["author"].strip(",:")

            yield Opinion(
                opinion_dict["name"],
                opinion_dict["name_abbreviation"],
                citations,
                int(opinion_dict["first_page"]),
                int(opinion_dict["last_page"]),
                datetime.date.fromisoformat(opinion_dict["decision_date"]),
                opinion_dict["court"]["slug"],
                position,
                author,
            )

    def posits(self, holding: Rule, context: Optional[Sequence[Factor]] = None) -> None:
        """
        Adds holding to the opinion's holdings list, replacing any other
        Holdings with the same meaning.
        """
        if not isinstance(holding, Rule):
            raise TypeError('"holding" must be an object of type Rule.')

        # These lines repeat lines in new_context_helper
        if isinstance(context, Factor) or isinstance(context, str):
            context = context.wrap_with_tuple(context)

        if context is not None and isinstance(holding, ProceduralRule):
            if isinstance(context, dict):
                for factor in context:
                    if isinstance(context[factor], str):
                        context[factor] = self.get_factor_by_name(context[factor])
            else:
                new_context: List[Factor] = []
                for factor in context:
                    if isinstance(factor, str):
                        new_context.append(self.get_factor_by_name(factor))
                    else:
                        new_context.append(factor)
                context = dict(zip(holding.generic_factors, new_context))
            holding = holding.new_context(context)
        self.holdings.append(holding)

    def get_factor_by_name(self, name: str) -> Optional[Factor]:
        for holding in self.holdings:
            factor = holding.get_factor_by_name(name)
            if factor is not None:
                return factor
        raise ValueError(f'No factor by the name "{name}" was found')

    @property
    def generic_factors(self) -> List[Factor]:
        return list(
            {
                generic: None
                for holding in self.holdings
                for generic in holding.generic_factors
            }
        )
