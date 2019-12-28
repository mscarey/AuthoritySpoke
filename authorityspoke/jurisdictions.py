r"""
Representations of legal systems.

These clasess are currently used to organize legislation,
but later they can be linked to :class:`.Court`\s and
thus to :class:`.Opinion`\s.
"""

from __future__ import annotations

from typing import ClassVar, Dict, Optional, Union

from dataclasses import dataclass, field

from anchorpoint.textselectors import TextQuoteSelector

from authorityspoke.enactments import Code
from authorityspoke.courts import Court


@dataclass
class Jurisdiction:
    r"""
    A geopolitical entity with the power to enact legislation.

    Has :class:`.Court`\s to interpret and apply legislation.

    :param id:
        the :class:`Jurisdiction`\'s identifier in USLM or, failing that,
        in Citation Style Language.

    :param codes:
        a list of :class:`.Code`\s enacted by the :class:`Jurisdiction`\.

    :param courts:
        a list of :class:`.Court`\s operated by the :class:`Jurisdiction`\.
    """

    codes: Dict[str, Code] = field(default_factory=dict)
    courts: Dict[str, Court] = field(default_factory=dict)

    def get_code(self, uri: str) -> Optional[Code]:
        """
        Find a :class:`.Code` under a key corresponding to ``uri``.

        If the initial form of ``uri`` isn't found, truncates
        parts from the right side of the ``uri`` until a match
        is found or nothing is left.

        :param uri:
            identifier for legislative text in the USLM format
            (or possibly pseudo-USLM for non-USC sources)

        :returns:
            the :class:`.Code` for the ``uri``
        """
        query = uri[:]
        if self.codes.get(str(query)):
            return self.codes.get(query)
        # try shorter forms of uri
        shortened_query = query[:]
        while shortened_query:
            if self.codes.get(str(shortened_query)):
                return self.codes.get(shortened_query)
            shortened_query = shortened_query[: shortened_query.rfind("/")]

        # try longer form of uri
        for name, code in self.codes.items():
            if name.startswith(uri):
                return code
        return None


@dataclass
class Regime:
    r"""
    A legal system consisting of multiple jurisdictions.

    Currently used for retrieving :class:`.Enactment` text.
    May be modified for retrieving :class:`.Court`\s and
    :class:`.Opinion`\s.

    :param jurisdictions:
    """

    jurisdictions: Dict[str, Jurisdiction] = field(default_factory=dict)
    uri: ClassVar = "/"

    def get_code(self, path: str):
        """
        Find a :class:`.Code` in the :class:`Regime` from a selector.

        :returns:
            the :class:`.Code` described in the selector path.
        """
        jurisdiction_id = path.split("/")[1]

        if jurisdiction_id not in self.jurisdictions:
            raise ValueError(f"Regime has no jurisdiction {jurisdiction_id}.")
        return self.jurisdictions[jurisdiction_id].get_code(path)

    def set_code(self, code: Code) -> None:
        r"""
        Add to the collection of :class:`.Code`\s enacted in this :class:`Regime`.

        Create the appropriate :class:`.Jurisdiction` object for the
        :class:`.Code`, if it's not already linked to the :class:`Regime`.

        :param code:
            a :class:`.Code` valid in this :class:`Regime`
        """
        if code.jurisdiction not in self.jurisdictions:
            self.jurisdictions[code.jurisdiction] = Jurisdiction()

        if not self.jurisdictions[code.jurisdiction].codes.get(code.uri):
            self.jurisdictions[code.jurisdiction].codes[code.uri] = code
        return None
