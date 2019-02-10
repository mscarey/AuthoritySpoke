from typing import Dict, Tuple
from typing import Optional

import datetime
import json
import pathlib

from dataclasses import dataclass

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

    def dict_from_input_json(self, filename: str) -> Tuple[Dict, Dict]:
        """
        Makes entity and holding dicts from a JSON file in the format that lists
        mentioned_entities followed by a list of holdings.
        """

        path = pathlib.Path("input") / filename
        with open(path, "r") as f:
            case = json.load(f)
        return case["mentioned_factors"], case["holdings"]

    def holdings_from_json(self, filename: str) -> Dict["Rule", Tuple[Factor, ...]]:
        """Creates a set of holdings from a JSON file in the input subdirectory,
        adds those holdings to self.holdings, and returns self.holdings."""

        entity_list, holding_list = self.dict_from_input_json(filename)
        for record in holding_list:
            factor_groups = {"inputs": set(), "outputs": set(), "despite": set()}
            for factor_type in factor_groups:
                factor_list = record.get(factor_type, [])
                if not isinstance(factor_list, list):
                    factor_list = [factor_list]
                for factor_dict in factor_list:
                    factor = Factor.from_dict(factor_dict)
                    factor_groups[factor_type].add(factor)
            procedure = Procedure(
                inputs=factor_groups["inputs"],
                outputs=factor_groups["outputs"],
                despite=factor_groups["despite"],
            )

            enactment_groups = {"enactments": set(), "enactments_despite": set()}
            for enactment_type in enactment_groups:
                enactment_list = record.get(enactment_type, [])
                if isinstance(enactment_list, dict):
                    enactment_list = [enactment_list]
                for enactment_dict in enactment_list:
                    enactment_groups[enactment_type].add(
                        Enactment.from_dict(enactment_dict)
                    )

            holding = ProceduralRule(
                procedure=procedure,
                enactments=enactment_groups["enactments"],
                enactments_despite=enactment_groups["enactments_despite"],
                mandatory=record.get("mandatory", False),
                universal=record.get("universal", False),
                rule_valid=record.get("rule_valid", True),
                decided=record.get("decided", True),
            )
            # There's currently no way to get the entities from the Predicates.
            self.holdings[holding] = entities
        return self.holdings
