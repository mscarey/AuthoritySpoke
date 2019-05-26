from __future__ import annotations

from typing import Dict, List, Optional

from dataclasses import dataclass

from authorityspoke.enactments import Code
from authorityspoke.courts import Court

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
    codes: Optional[Dict[str, Code]] = None
    courts: Optional[Dict[str, Court]] = None

    def __post_init__(self):
        if self.codes is None:
            self.codes = {}
        if self.courts is None:
            self.courts = {}


@dataclass
class Regime:
    """
    A legal system consisting of multiple jurisdictions.
    """
    jurisdictions: Optional[Dict[str, Jurisdiction]] = None

    def __post_init__(self):
        if self.jurisdictions is None:
            self.jurisdictions = {}

    def has_code(self, code: Code):
        if code.jurisdiction_id not in self.jurisdictions:
            self.jurisdictions[code.jurisdiction_id] = Jurisdiction()
        self.jurisdictions[code.jurisdiction_id].codes.append(code)
