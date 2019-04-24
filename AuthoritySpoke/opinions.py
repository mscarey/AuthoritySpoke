from typing import Dict, List, Tuple
from typing import Optional, Sequence, Union

import datetime
import json
import os
import pathlib

import requests

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
    def cap_download(
        cls,
        cap_id: Optional[int] = None,
        cite: Optional[str] = None,
        save_to_file: bool = True,
        filename: Optional[str] = None,
        directory: Optional[pathlib.Path] = None,
        full_case: bool = False,
        api_key: Optional[str] = None,
    ) -> Union[Dict, List[Dict]]:
        """
        :param cap_id: an integer identifier for an opinion in the CAP
        database, e.g. 4066790 for Oracle America, Inc. v. Google Inc.

        :param cite: a string representing a citation linked to an opinion
        in the CAP database. Usually these will be in the traditional format
        "[Volume Number] [Reporter Name Abbreviation] [Page Number]", e.g.
        "750 F.3d 1339" for Oracle America, Inc. v. Google Inc. If the id
        field is given, the cite field will be ignored. If neither field
        is given, the download will fail.

        :param save_to_file: whether to save the opinion to disk in addition
        to returning it as a dict. Defaults to True.

        :param filename: the filename (not including the directory) for the
        file where the downloaded opinion should be saved.

        :param directory: a Path object specifying the directory where the
        downloaded opinion should be saved. If None is given, the current
        default is example_data/opinions.

        :param full_case: whether to request the full text of the opinion
        from the CAP API. If this is True, the api_key parameter must be
        provided.

        :param api_key: a Case Access Project API key. Visit
        https://case.law/user/register/ to obtain one. Not needed if you
        only want to download metadata about the opinion without the
        full text.
        """

        def save_opinion(
            downloaded: dict,
            directory: pathlib.Path,
            filename: Optional[str] = None,
            save_to_file: bool = save_to_file,
        ):
            if save_to_file:
                if not filename:
                    filename = f'{downloaded["id"]}.json'
                with open(directory / filename, "w") as fp:
                    json.dump(downloaded, fp, ensure_ascii=False)
            return None

        if not (cap_id or cite):
            raise ValueError(
                "To identify the desired opinion, either 'cap_id' or 'cite' "
                "must be provided."
            )
        if full_case and not api_key:
            raise ValueError("A CAP API key must be provided when full_case is True.")
        if not directory:
            directory = cls.directory
        params = {}
        if full_case:
            params["full_case"] = "true"
        endpoint = "https://api.case.law/v1/cases/"
        if cap_id:
            endpoint += f"{cap_id}/"
        else:
            params["cite"] = cite
        downloaded = requests.get(endpoint, params=params, headers=api_key).json()
        if downloaded.get("results") is None:
            save_opinion(downloaded, directory, filename)
            return downloaded
        else:
            if not downloaded["results"]:
                if cap_id:
                    message = f"API returned no cases with id {cap_id}"
                else:
                    message = f"API returned no cases with cite {cite}"
                raise ValueError(message)
            opinions = []
            for n, result in enumerate(downloaded["results"]):
                save_opinion(result, directory, filename.replace(".", f"_{n}."))
                opinions.append(result)
            return opinions

    @classmethod
    def from_file(cls, filename: str, directory: Optional[pathlib.Path] = None):
        """This is a generator that gets one opinion from a
        Harvard-format case file every time it's called. Exhaust the
        generator to get the lead opinion and all non-lead opinions."""

        if not directory:
            directory = cls.directory

        with open(directory / filename, "r") as f:
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
    def make_opinion_with_holdings(cls, party_name: str):
        """
        This generates a majority Opinion with all its holdings, under
        the assumption that the text of the Opinion is in the
        example_data/opinions folder with the name [party_name]_h.json,
        and the holdings are in the example_data/holdings folder with
        the name holding_[party_name].json.
        """
        opinion = next(cls.from_file(f"{party_name}_h.json"))
        holdings = Rule.from_json(f"holding_{party_name}.json")
        for holding in holdings:
            opinion.posits(holding)
        return opinion

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
        """
        Performs a recursive search of each holding in the
        Opinion for a Factor with the specified name attribute.
        Returns such a Factor if it exists, otherwise returns None.
        """

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
