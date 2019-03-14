from typing import Dict, List, Tuple
from typing import Optional

import datetime
import json
import pathlib

from dataclasses import dataclass

from facts import Fact
from evidence import Exhibit, Evidence
from enactments import Enactment
from rules import Procedure, Rule, ProceduralRule
from spoke import Factor


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

    def __post_init__(self):
        self.holdings = {}

    def holdings_from_json(self, filename: str) -> List["Rule"]:
        """
        Creates a list of holdings from a JSON file in the input subdirectory,
        and returns the list.

        Should this also cause the Opinion to posit the Rules as holdings?
        """

        def dict_from_input_json(filename: str) -> Tuple[Dict, Dict]:
            """
            Makes entity and holding dicts from a JSON file in the format that lists
            mentioned_entities followed by a list of holdings.
            """

            path = pathlib.Path("input") / filename
            with open(path, "r") as f:
                case = json.load(f)
            return case["mentioned_factors"], case["holdings"]

        context_list, rule_list = dict_from_input_json(filename)
        context_list = self.__class__.get_mentioned_factors(context_list)
        enactments: List[Enactment] = []
        finished_rules: List["Rule"] = []
        for rule in rule_list:
            # This will need to change for Attribution holdings
            finished_rule, context_list, enactments = ProceduralRule.from_dict(
                rule, context_list, enactments
            )
            finished_rules.append(finished_rule)
        return finished_rules


    @staticmethod
    def from_file(path):
        """This is a generator that gets one opinion from a
        Harvard-format case file every time it's called. Exhaust the
        generator to get the lead opinion and all non-lead opinions."""

        with open(path, "r") as f:
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

    @classmethod
    def get_mentioned_factors(
        cls, mentioned_dict: List[Dict[str, str]]
    ) -> List[Factor]:
        """
        :param mentioned_dict: A dict in the JSON format used in the
        "input" folder.

        :returns: A list of Factors mentioned in the Opinion's holdings.
        Especially the context factors referenced in Predicates, since
        there's currently no other way to import those using the JSON
        format.
        """
        return [Factor.from_dict(factor_dict) for factor_dict in mentioned_dict]

    def get_entities(self):
        return [e for t in self.holdings.values() for e in t]

    def posits(
        self, holding: Rule, entities: Optional[Tuple[Factor, ...]] = None
    ) -> None:
        # TODO: the "entities" parameter is now misnamed because they can be
        # any subclass of Factor.
        if entities is None:
            entities = self.get_entities()[: len(holding)]  # TODO: write test

        if len(holding) > len(entities):
            raise ValueError(
                f"The 'entities' parameter must be a tuple with "
                + f"{len(holding)} entities. This opinion doesn't have "
                + "enough known entities to create context for this holding."
            )

        if holding not in self.holdings:
            self.holdings[holding] = entities

        return None

    def holding_in_context(self, holding: Rule):
        if not isinstance(holding, Rule):
            raise TypeError("holding must be type 'Rule'.")
        if holding not in self.holdings:
            raise ValueError
            (
                f"That holding has not been posited by {self.name}. "
                + "Try using the posits() method to add the holding to self.holdings."
            )
        pass  # TODO: tests
