"""
Downloading data that can be converted to authorityspoke objects.

So far this only covers the Caselaw Access Project API.
"""

from typing import Any, Dict, List, Optional, Union

import requests


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
