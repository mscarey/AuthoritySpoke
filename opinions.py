from typing import Dict, List, Tuple
from typing import Optional, Sequence, Union

import datetime
import json
import pathlib

from dataclasses import dataclass

from allegations import Allegation
from evidence import Exhibit, Evidence
from enactments import Enactment
from facts import Fact
from rules import Procedure, Rule, ProceduralRule
from spoke import Factor


@dataclass()
class Holding:
    """
    A ProceduralRule, plus a tuple of generic Factors to substitute
    for the Factors in ProceduralRule.generic_factors().
    """

    def __init__(
        self,
        rule: ProceduralRule,
        context: Optional[Union[Dict[Factor, Factor], Sequence[Factor]]] = None,
    ):
        if context is None:
            context = rule.generic_factors
        if any(not isinstance(item, Factor) for item in context):
            raise TypeError('Each item in "context" must be type Factor')
        if isinstance(context, dict):
            if not all(
                to_replace in rule.generic_factors for to_replace in context.keys()
            ):
                raise ValueError(
                    'If "context" is a dictionary, then each of its keys must '
                    + "be a generic Factor from rule, and each corresponding value "
                    + "must be a Factor that replaces the key in the "
                    + "context of the current Holding."
                )
            # TODO: validate compatible Entity subclasses
            context = [context.get(item, item) for item in rule.generic_factors]
        if len(context) != len(rule.generic_factors):
            raise ValueError(
                f'For this {self.__class__.__name__}, "context" must have exactly '
                + f"{len(rule.generic_factors)} factors, to correspond with the "
                + "number of generic factors in the referenced ProceduralRule."
            )
        if any(not factor.generic for factor in context):
            raise ValueError(
                'Every Factor in "context" must be generic '
                + "(must have the attribute generic=True)"
            )
        self.rule = rule
        self.context = tuple(context)

    def __str__(self):
        string = str(self.rule)
        string = string.replace("the rule that", "the holding that", 1)
        for i in range(len(self.context)):
            string = string.replace(str(self.rule.generic_factors[i]), str(self.context[i]))
        return string


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
        self.holdings = []

    def holdings_from_json(self, filename: str) -> List["Rule"]:
        """
        Creates a list of holdings from a JSON file in the input subdirectory,
        and returns the list.

        Should this also cause the Opinion to posit the Rules as holdings?
        """

        def dict_from_input_json(filename: str) -> Tuple[List[Dict], List[Dict]]:
            """
            Makes entity and holding dicts from a JSON file in the format that lists
            mentioned_entities followed by a list of holdings.
            """

            path = pathlib.Path("input") / filename
            with open(path, "r") as f:
                case = json.load(f)
            return case["mentioned_factors"], case["holdings"]

        context_list, rule_list = dict_from_input_json(filename)
        mentioned = self.__class__.get_mentioned_factors(context_list)
        finished_rules: List["Rule"] = []
        for rule in rule_list:
            # This will need to change for Attribution holdings
            finished_rule, mentioned = ProceduralRule.from_dict(rule, mentioned)
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
        cls, mentioned_list: List[Dict[str, str]]
    ) -> List[Factor]:
        """
        :param mentioned_dict: A dict in the JSON format used in the
        "input" folder.

        :returns: A list of Factors mentioned in the Opinion's holdings.
        Especially the context factors referenced in Predicates, since
        there's currently no other way to import those using the JSON
        format.
        """
        mentioned: List[Factor] = []
        for factor_dict in mentioned_list:
            _, mentioned = Factor.from_dict(factor_dict, mentioned)
        return mentioned

    def posits(self, holding: Holding) -> None:
        """
        Adds holding to the opinion's holdings list, replacing any other
        Holdings with the same meaning.
        """
        if not isinstance(holding, Holding):
            raise TypeError('"holding" must be an object of type Holding.')
        self.holdings.append(holding)

    @property
    def generic_factors(self) -> List[Factor]:
        return list(
            {generic: None for holding in self.holdings for generic in holding.context}
        )
