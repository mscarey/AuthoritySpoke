"""
:class:`Court` documents that decide litigation and posit :class:`.Rule`\s.

Unlike most other ``authorityspoke`` classes, :class:`Opinion`\s are not frozen.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple
from typing import Iterable, Iterator
from typing import Optional, Sequence, Union

import datetime
import json
import pathlib

from dataclasses import dataclass

import requests

from authorityspoke.context import get_directory_path
from authorityspoke.factors import Factor
from authorityspoke.rules import Rule, ProceduralRule


@dataclass
class Opinion:
    """
    A document that resolves legal issues in a case and posits legal holdings.

    Usually an opinion must have ``position="majority"``
    to create holdings binding on any courts.

    :param name:
        full name of the opinion, e.g. "ORACLE AMERICA, INC.,
        Plaintiff-Appellant, v. GOOGLE INC., Defendant-Cross-Appellant"
    :param name_abbreviation:
        shorter name of the opinion, e.g. "Oracle America, Inc. v. Google Inc."
    :param citations:
        citations to the opinion, usually in the format
        ``[Volume Number] [Reporter Name Abbreviation] [Page Number]``
    :param first_page:
        the page where the opinion begins in its official reporter
    :param last_page:
        the page where the opinion ends in its official reporter
    :param decision_date:
        date when the opinion was first published by the court
        (not the publication date of the reporter volume)
    :param court:
        name of the court that published the opinion
    :param position:
        the opinion's attitude toward the court's disposition of the case.
        e.g. ``majority``, ``dissenting``, ``concurring``, ``concurring in the result``
    :param author:
        name of the judge who authored the opinion, if identified
    """

    name: str
    name_abbreviation: str
    citations: Tuple[str]
    first_page: int
    last_page: int
    decision_date: datetime.date
    court: str
    position: str
    author: Optional[str]

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
        to_dict: bool = False,
        as_generator: bool = False,
    ) -> Union[
        Opinion,
        List[Opinion],
        Iterator[Opinion],
        Dict[str, Any],
        List[Dict[str, Any]],
        Iterator[Dict[str, Any]],
    ]:
        """
        Download opinions from Caselaw Access Project API.

        Queries the Opinion endpoint of the
        `Caselaw Access Project API <https://api.case.law/v1/cases/>`_,
        saves the JSON object(s) from the response to the
        ``example_data/opinions/`` directory in the repo,
        and returns one or more dict objects from the JSON
        or one or more :class:`.Opinion` objects.

        :param cap_id:
            an identifier for an opinion in the
            `Caselaw Access Project database <https://case.law/api/>`_,
            e.g. 4066790 for
            `Oracle America, Inc. v. Google Inc. <https://api.case.law/v1/cases/4066790/>`_.

        :param cite:
            a citation linked to an opinion in the
            `Caselaw Access Project database <https://case.law/api/>`_.
            Usually these will be in the traditional format
            ``[Volume Number] [Reporter Name Abbreviation] [Page Number]``, e.g.
            `750 F.3d 1339 <https://case.law/search/#/cases?page=1&cite=%22750%20F.3d%201339%22>`_
            for Oracle America, Inc. v. Google Inc.
            If the ``cap_id`` field is given, the cite field will be ignored.
            If neither field is given, the download will fail.

        :param save_to_file:
            whether to save the opinion to disk in addition
            to returning it as a dict. Defaults to ``True``.

        :param filename:
            the filename (not including the directory) for the
            file where the downloaded opinion should be saved.

        :param directory:
            a :py:class:`~pathlib.Path` object specifying the directory where the
            downloaded opinion should be saved. If ``None`` is given, the current
            default is ``example_data/opinions``.

        :param full_case:
            whether to request the full text of the opinion from the
            `Caselaw Access Project API <https://api.case.law/v1/cases/>`_.
            If this is ``True``, the `api_key` parameter must be
            provided.

        :param api_key:
            a Case Access Project API key. Visit
            https://case.law/user/register/ to obtain one. Not needed if you
            only want to download metadata about the opinion without the
            full text.

        :param to_dict:
            if ``True``, opinion records remain dict objects
            rather than being converted to :class:`.Opinion` objects.

        :param as_generator:
            if ``True``, returns a generator that yields all opinions
            meeting the query.
        """

        if not (cap_id or cite):
            raise ValueError(
                "To identify the desired opinion, either 'cap_id' or 'cite' "
                "must be provided."
            )

        api_dict = {}
        if full_case:
            if not api_key:
                raise ValueError(
                    "A CAP API key must be provided when full_case is True."
                )
            else:
                api_dict["Authorization"] = f"Token {api_key}"

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
        downloaded = requests.get(endpoint, params=params, headers=api_dict).json()

        if downloaded.get("results") is not None and not downloaded["results"]:
            if cap_id:
                message = f"API returned no cases with id {cap_id}"
            else:
                message = f"API returned no cases with cite {cite}"
            raise ValueError(message)

        # Because the API wraps the results in a list only if there's
        # more than one result.

        if not downloaded.get("results"):
            results = [downloaded]
        else:
            results = downloaded["results"]

        def opinions_from_response(results, to_dict):

            for number, case in enumerate(results):
                if not filename:
                    mangled_filename = f'{case["id"]}.json'
                else:
                    mangled_filename = filename
                if number > 0:
                    mangled_filename = filename.replace(".", f"_{number}.")
                if save_to_file:
                    with open(directory / filename, "w") as fp:
                        json.dump(case, fp, ensure_ascii=False)
                if to_dict:
                    yield case
                else:
                    for opinion in cls.from_dict(case, lead_only=False):
                        yield opinion

        if as_generator:
            return iter(opinions_from_response(results, to_dict))
        opinions = [case for case in opinions_from_response(results, to_dict)]
        if len(opinions) == 1:
            return opinions[0]
        else:
            return opinions

    def contradicts(self, other: Union[Opinion, Rule]) -> bool:
        """
        Test whether ``other`` is or contains a :class:`.Rule` contradicted by ``self``.

        :param other:
            another :class:`.Opinion` or :class:`.Rule`

        :returns:
            a bool indicating whether any holding of ``self`` is
            inconsistent with the :class:`.Rule` ``other``, or with
            any holding of ``other`` if ``other`` is an :class:`.Opinion`.
        """

        if isinstance(other, Rule):
            return any(
                self_holding.contradicts(other) for self_holding in self.holdings
            )
        elif isinstance(other, self.__class__):
            return any(
                any(
                    self_holding.contradicts(other_holding)
                    for self_holding in self.holdings
                )
                for other_holding in other.holdings
            )
        raise TypeError(
            f"'Contradicts' test not implemented for types {self.__class__} and {other.__class__}."
        )

    @classmethod
    def from_dict(
        cls, decision_dict: Dict[str, Any], lead_only: bool = True
    ) -> Union[Opinion, Iterator[Opinion]]:
        """
        Create and return one or more :class:`.Opinion` objects.

        :param decision_dict:
            A record of an opinion loaded from JSON from the
            `Caselaw Access Project API <https://api.case.law/v1/cases/>`_.

        :param lead_only:
            If ``True``, returns a single :class:`.Opinion` object
            from the first opinion found in the
            ``casebody/data/opinions`` section of the dict, which should
            usually be the lead opinion. The lead opinion is commonly, but
            not always, the only opinion that creates binding legal authority.
            Usually every :class:`.Rule` posited by the lead opinion is
            binding, but some may not be, often because parts of the
            :class:`.Opinion` fail to command a majority of the panel
            of judges. If ``False``, returns an iterator that yields
            :class:`.Opinion` objects from every opinion in the case.
        """

        def make_opinion(decision_dict, opinion_dict, citations) -> Opinion:
            position = opinion_dict["type"]
            author = opinion_dict["author"]
            if author:
                author = author.strip(",:")

            return Opinion(
                decision_dict["name"],
                decision_dict["name_abbreviation"],
                citations,
                int(decision_dict["first_page"]),
                int(decision_dict["last_page"]),
                datetime.date.fromisoformat(decision_dict["decision_date"]),
                decision_dict["court"]["slug"],
                position,
                author,
            )

        citations = tuple(c["cite"] for c in decision_dict["citations"])
        opinions = (
            decision_dict.get("casebody", {})
            .get("data", {})
            .get("opinions", [{"type": "majority", "author": None}])
        )

        if lead_only:
            return make_opinion(decision_dict, opinions[0], citations)
        else:
            return iter(
                make_opinion(decision_dict, opinion_dict, citations)
                for opinion_dict in opinions
            )

    @classmethod
    def from_file(
        cls,
        filename: str,
        directory: Optional[pathlib.Path] = None,
        lead_only: bool = True,
    ) -> Union[Opinion, Iterator[Opinion]]:
        """
        Create and return one or more :class:`.Opinion` objects from JSON.

        Relies on the JSON format from the `Caselaw Access Project
        API <https://api.case.law/v1/cases/>`_.

        :param filename: The name of the input JSON file.

        :param directory: The directory where the input JSON file is located.

        :param lead_only:
            If ``True``, returns a single :class:`.Opinion` object
            from the first opinion found in the
            ``casebody/data/opinions`` section of the dict, which should
            usually be the lead opinion. The lead opinion is commonly, but
            not always, the only opinion that creates binding legal authority.
            Usually every :class:`.Rule` posited by the lead opinion is
            binding, but some may not be, often because parts of the
            :class:`.Opinion` fail to command a majority of the panel
            of judges. If ``False``, returns an iterator that yields
            :class:`.Opinion` objects from every opinion in the case.
        """

        if not directory:
            directory = cls.directory

        with open(directory / filename, "r") as f:
            decision_dict = json.load(f)

        return Opinion.from_dict(decision_dict, lead_only)

    def exposit(
        self,
        rule_file: Optional[str] = None,
        rule_dict: Optional[dict] = None,
        directory: Optional[pathlib.Path] = None,
        regime: Optional["Regime"] = None,
    ):
        """
        Load and :meth:`~Opinion.posit` :class:`.Rule` objects from JSON.

        Here, to :meth:`~Opinion.posit` means to add each :class:`.Rule`
        to ``self.holdings``.

        :param rule_file:
            name of the JSON file with the
            representation of :class:`.Rule` objects. If ``None``
            is passed in, the :class:`.Rule` class will add the
            default value ``holding_[party_name].json``.

        :param rule_dict:
            dict with a representation of :class:`.Rule` objects.

        :param directory:
            directory containing the JSON file with the
            representation of :class:`.Rule` objects. If ``None``
            is passed in, the :class:`.Rule` class will add the
            default value ``example_data/holdings``.
        """

        if rule_dict:
            holdings = Rule.collection_from_dict(rule_dict, regime=regime)
        elif rule_file:
            holdings = Rule.from_json(rule_file, directory=directory, regime=regime)
        else:
            raise ValueError(
                "Must specify either rule_file (filename of a JSON rule input file) "
                "or rule_dict (a dict with the same fields as the JSON input file)."
            )
        for holding in holdings:
            self.posit(holding)
        return self

    @property
    def generic_factors(self) -> List[Factor]:
        """
        Get all generic :class:`.Factor`\s mentioned in ``self``.

        :returns:
            a list of generic :class:`.Factor` objects mentioned in
            any ``input``, ``output``, or ``despite`` :class:`.Factor`
            of ``self``, with guaranteed order, including each
            generic :class:`.Factor` only once.
        """
        return list(
            {
                generic: None
                for holding in self.holdings
                for generic in holding.generic_factors
            }
        )

    def get_factor_by_name(self, name: str) -> Optional[Factor]:
        """
        Search recursively in holdings of ``self`` for :class:`.Factor` with ``name``.

        :param name:
            string to match with the ``name`` attribute of the
            :class:`.Factor` being searched for.

        :returns:
            a :class:`.Factor` with the specified ``name``, if one
            exists in a :class:`.Rule` in ``self.holdings``.
            Otherwise ``None``.
        """

        for holding in self.holdings:
            factor = holding.get_factor_by_name(name)
            if factor is not None:
                return factor
        raise ValueError(f'No factor by the name "{name}" was found')

    def posit(
        self,
        holding: Union[Rule, Iterable[Rule]],
        context: Optional[Sequence[Factor]] = None,
    ) -> None:
        """
        Add a :class:`.Rule` as a holding of this ``Opinion``.

        Adds ``holding`` (or every :class:`.Rule` in ``holding``, if ``holding``
        is iterable) to the :py:class:`list` ``self.holdings``, replacing
        any other :class:`.Rule` in ``self.holdings`` with the same meaning.

        :param holding:
            a :class:`.Rule` that the :class:`.Opinion` ``self`` posits
            as valid in its own court or jurisdiction, regardless of
            whether ``self`` accepts that the ``inputs`` of the
            :class:`.Rule` correspond to the reality of the current
            case, and regardless of whether the court orders that
            the ``outputs`` of the :class:`.Rule` be put into effect.

        :param context:
            an ordered sequence (probably :py:class:`dict`) of
            generic :class:`.Factor` objects from ``self`` which
            will provide the context for the new holding in the
            present case.
        """

        def posits_one_holding(
            holding: Union[Rule, Iterable[Rule]],
            context: Optional[Sequence[Factor]] = None,
        ) -> None:
            if not isinstance(holding, Rule):
                raise TypeError('"holding" must be an object of type Rule.')

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

        # These lines repeat lines in new_context_helper
        if isinstance(context, Factor) or isinstance(context, str):
            context = context._wrap_with_tuple(context)

        if isinstance(holding, Iterable):
            for item in holding:
                posits_one_holding(item, context)
        else:
            posits_one_holding(holding, context)

    def __ge__(self, other: Union[Opinion, Rule]) -> bool:
        """
        Find whether ``self``'s holdings imply all the holdings of ``other``.

        :returns:
            a bool indicating whether the :class:`.Rule` ``other``
            (or every holding of ``other``, if other is an :class:`.Opinion`)
            is implied by some :class:`.Rule` in ``self.holdings``.
        """
        if isinstance(other, Rule):
            return any(self_holding >= other for self_holding in self.holdings)
        elif isinstance(other, self.__class__):
            for other_holding in other.holdings:
                if not any(
                    self_holding >= other_holding for self_holding in self.holdings
                ):
                    return False
            return True
        raise TypeError(
            f"'Implies' test not implemented for types {self.__class__} and {other.__class__}."
        )

    def __gt__(self, other) -> bool:
        """
        Find whether ``self``\'s holdings imply ``other``\'s but self != other.

        This actually tests for inequality because ``Opinion`` does not
        have a ``means`` method.

        :returns:
            self >= other and self != other.
        """
        return (self >= other) and (self != other)
