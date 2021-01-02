"""
Downloading data that can be converted to authorityspoke objects.
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests
from legislice.download import Client, normalize_path, LegislicePathError, RawEnactment


def download_enactment_from_client(
    path: str,
    client: Union[Client, FakeClient],
    date: Union[datetime.date, str] = "",
):
    """
    Download Enactment object from an API.

    Allows either a real client or a fake testing client.
    """
    enactment = client.read(query=path, date=date)
    return enactment


def download_enactment(
    path: str,
    date: Union[datetime.date, str] = "",
    api_token: str = "",
    api_root: str = "https://authorityspoke.com/api/v1",
):
    """
    Download Enactment object from an API using the Legislice JSON schema.

    :param path:
        a path to the desired legislation section using the United States
        Legislation Markup tree-like citation format.

    :param date:
        The date of the desired version of the provision to be downloaded.
        This is not needed if a CrossReference passed to the query param
        specifies a date. If no date is provided, the API will use the most
        recent date.

    :param api_token:
        An authentication key for the API that will serve the enactment data.

    :param api_root:
        The URL where the API can be found.
    """
    client = Client(api_token=api_token, api_root=api_root)
    return download_enactment_from_client(path=path, client=client, date=date)


def download_case(
    cap_id: Optional[int] = None,
    cite: Optional[str] = None,
    full_case: bool = False,
    api_key: Optional[str] = None,
    many: bool = False,
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Download cases from Caselaw Access Project API.

    Queries the Opinion endpoint of the
    `Caselaw Access Project API <https://api.case.law/v1/cases/>`_,
    saves the JSON object(s) from the response to the
    ``example_data/cases/`` directory in the repo,
    and returns one or more dict objects from the JSON.

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

    :param full_case:
        whether to request the full text of the opinion from the
        `Caselaw Access Project API <https://api.case.law/v1/cases/>`_.
        If this is ``True``, the `api_key` parameter must be
        provided.

    :param api_key:
        a Caselaw Access Project API key. Visit
        https://case.law/user/register/ to obtain one. Not needed if you
        only want to download metadata about the opinion without the
        full text.

    :param always_list:
        If True and as_generator is False, a single case from the API will
        be returned as a one-item list. If False and as_generator is False,
        a single case will be a list.

    :returns:
        a case record or list of case records from the API.

    """
    endpoint = "https://api.case.law/v1/cases/"
    params = {}
    if cap_id:
        endpoint += f"{cap_id}/"
    elif cite is not None:
        params["cite"] = cite
    else:
        raise ValueError(
            "To identify the desired opinion, either 'cap_id' or 'cite' "
            "must be provided."
        )

    api_dict = {}
    if full_case:
        if not api_key:
            raise ValueError("A CAP API key must be provided when full_case is True.")
        else:
            api_dict["Authorization"] = f"Token {api_key}"

    if full_case:
        params["full_case"] = "true"
    response = requests.get(endpoint, params=params, headers=api_dict).json()

    if cap_id and response.get("detail") == "Not found.":
        raise ValueError(f"API returned no cases with id {cap_id}")
    if cite and not response.get("results") and response.get("results") is not None:
        raise ValueError(f"API returned no cases with cite {cite}")

    # Because the API wraps the results in a list only if there's
    # more than one result.

    if response.get("results"):
        if many:
            return response["results"]
        return response["results"][0]
    return response


# A dict indexing responses by iso-format date strings.
ResponsesByDate = Dict[str, Dict]
ResponsesByDateByPath = Dict[str, Dict[str, Dict]]


class FakeClient(Client):
    """Repository for mocking API responses locally."""

    def __init__(self, responses: ResponsesByDateByPath):
        self.responses = responses
        self.coverage: Dict[str, Dict[str, Union[datetime.date, str]]] = {
            "/us/const": {
                "latest_heading": "United States Constitution",
                "first_published": datetime.date(1788, 6, 21),
                "earliest_in_db": datetime.date(1788, 6, 21),
            },
            "/us/usc": {
                "latest_heading": "United States Code (USC)",
                "first_published": datetime.date(1926, 6, 30),
                "earliest_in_db": datetime.date(2013, 7, 18),
                "latest_in_db": datetime.date(2020, 8, 8),
            },
            "/test/acts": {
                "latest_heading": "Test Acts",
                "first_published": datetime.date(1935, 4, 1),
                "earliest_in_db": datetime.date(1935, 4, 1),
                "latest_in_db": datetime.date(2013, 7, 18),
            },
        }
        self.update_coverage_from_api = False

    @classmethod
    def from_file(cls, filename: str) -> FakeClient:
        parent_directory = Path(__file__).resolve().parents[2]
        responses_filepath = parent_directory / "example_data" / "responses" / filename
        with open(responses_filepath, "r") as f:
            responses = json.load(f)
        return cls(responses)

    def get_entry_closest_to_cited_path(self, path: str) -> Optional[ResponsesByDate]:
        path = normalize_path(path)
        if self.responses.get(path):
            return self.responses[path]
        branches_that_start_path = [
            entry for entry in self.responses.keys() if path.startswith(entry)
        ]
        if not branches_that_start_path:
            return None
        name_of_best_entry = max(branches_that_start_path, key=len)
        return self.responses[name_of_best_entry]

    def search_tree_for_path(
        self, path: str, branch: Dict
    ) -> Optional[ResponsesByDate]:
        path = normalize_path(path)
        if branch["node"] == path:
            return branch
        branches_that_start_path = [
            nested_node
            for nested_node in branch["children"]
            if path.startswith(nested_node["node"])
        ]
        if branches_that_start_path:
            return self.search_tree_for_path(
                path=path, branch=branches_that_start_path[0]
            )
        return None

    def fetch(self, query: str, date: Union[datetime.date, str] = "") -> RawEnactment:
        """
        Fetches data about legislation at specified path and date from Client's assigned API root.

        :param path:
            A path to the desired legislation section using the United States Legislation Markup
            tree-like citation format. Examples: /us/const/amendment/IV, /us/usc/t17/s103

        :param date:
            A date when the desired version of the legislation was in effect. This does not need to
            be the "effective date" or the first date when the version was in effect. However, if
            you select a date when two versions of the provision were in effect at the same time,
            you will be given the version that became effective later.

        :returns:
            A fake JSON response in the format of the Legislice API.
        """
        responses = self.get_entry_closest_to_cited_path(query)
        if not responses:
            raise LegislicePathError(f"No enacted text found for query {query}")

        if isinstance(date, datetime.date):
            date = date.isoformat()

        if not date:
            selected_date = max(responses.keys())
        else:
            versions_not_later_than_query = [
                version_date
                for version_date in responses.keys()
                if version_date <= date
            ]
            if not versions_not_later_than_query:
                raise ValueError(
                    f"No enacted text found for query {query} after date {date}"
                )
            selected_date = max(versions_not_later_than_query)

        selected_version = responses[selected_date]

        result = self.search_tree_for_path(path=query, branch=selected_version)
        if not result:
            raise LegislicePathError(
                f"No enacted text found for query {query} after date {date}"
            )
        return result

    def _fetch_from_url(self, url: str) -> None:
        raise RuntimeError("Network access not allowed from FakeClient")
