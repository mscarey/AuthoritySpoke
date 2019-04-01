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
        if context is not None and isinstance(holding, ProceduralRule):
            holding = holding.new_context(context)
        self.holdings.append(holding)

    @property
    def generic_factors(self) -> List[Factor]:
        return list(
            {
                generic: None
                for holding in self.holdings
                for generic in holding.generic_factors
            }
        )
