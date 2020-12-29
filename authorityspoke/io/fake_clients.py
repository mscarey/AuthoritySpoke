"""Fake download clients for testing."""

from typing import Dict, Optional, Union

import datetime
import json
import os
from typing import Dict, Optional, Union

from legislice.download import RawEnactment, LegislicePathError, normalize_path

from authorityspoke.io.downloads import LegisClient


# A dict indexing responses by iso-format date strings.
ResponsesByDate = Dict[str, Dict]
ResponsesByDateByPath = Dict[str, Dict[str, Dict]]


class FakeClient(LegisClient):
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
            tree-like citation format. Examples: "/us/const/amendment/IV", "/us/usc/t17/s103"
        :param date:
            A date when the desired version of the legislation was in effect. This does not need to
            be the "effective date" or the first date when the version was in effect. However, if
            you select a date when two versions of the provision were in effect at the same time,
            you will be given the version that became effective later.
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
