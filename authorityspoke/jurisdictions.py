from __future__ import annotations

from pathlib import PurePosixPath
from typing import Dict, List, Optional, Union

from dataclasses import dataclass, field

from authorityspoke.enactments import Code
from authorityspoke.courts import Court
from authorityspoke.selectors import TextQuoteSelector

@dataclass
class Jurisdiction:
    """
    A geopolitical entity with the power to enact legislation
    and with courts to interpret the legislation.

    :param id: the jurisdiction's identifier in USLM or, failing that,
    in Citation Style Language.

    :param codes: a list of :class:`.Code`\s enacted by the Jurisdiction.

    :param courts: a list of :class:`.Court`\s operated by the Jurisdiction.
    """
    codes: Dict[str, Code] = field(default_factory=dict)
    courts: Dict[str, Court] = field(default_factory=dict)

    def get_code(self, uri: str) -> Code:
        """
        Finds and returns a :class:`.Code` saved under a key
        corresponding to as much as possible of the `uri`.

        If the initial form of `uri` isn't found, truncates
        parts from the right side of the `uri` until a match
        is found or nothing is left.

        :param uri:
            identifier for legislative text in the USLM format
            (or possibly pseudo-USLM for non-USC sources)
        """
        query = uri[:]
        while query:
            if self.codes.get(str(query)):
                return self.codes.get(query)
            query = query[:query.rfind('/')]
        return None

@dataclass
class Regime:
    """
    A legal system consisting of multiple jurisdictions.
    """
    jurisdictions: Dict[str, Jurisdiction] = field(default_factory=dict)

    def get_code(self, selector: Union[TextQuoteSelector, str]):
        if isinstance(selector, TextQuoteSelector):
            if selector.path is not None:
                return self.get_code(selector.path)
            else:
                raise ValueError(
                    '"selector" must have a "path" attribute containing ',
                    'a path to the code, or must be a string containing the path'
                )

        jurisdiction_id = selector.split("/")[1]

        if jurisdiction_id not in self.jurisdictions:
            raise ValueError(
                f"Regime has no jurisdiction {jurisdiction_id}."
            )
        return self.jurisdictions[jurisdiction_id].get_code(selector)

    def set_code(self, code: Code):
        jurisdiction_id = code.uri.split("/")[1]
        if jurisdiction_id not in self.jurisdictions:
            self.jurisdictions[jurisdiction_id] = Jurisdiction()

        self.jurisdictions[jurisdiction_id].codes[code.uri] = code
        return code
