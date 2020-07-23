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

from authorityspoke.codes import Code
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

    def get_code_with_uri_included_in_query(self, query: str) -> Optional[Code]:
        """
        Find a :class:`.Code` under a key corresponding to ``query``.

        If the initial form of ``query`` isn't found, truncates
        parts from the right side of the ``query`` until a match
        is found or nothing is left.

        :param query:
            identifier for legislative text in the USLM format
            (or possibly pseudo-USLM for non-USC sources)

        :returns:
            the :class:`.Code` for the ``query``
        """
        while query:
            if self.codes.get(str(query)):
                return self.codes.get(query)
            query = query[: query.rfind("/")]
        return None

    def get_code_with_uri_that_includes_query(self, query: str) -> Optional[Code]:
        r"""
        Find a :class:`.Code` under a key beginning with ``query``.

        :param query:
            identifier for legislative text in the USLM format
            (or possibly pseudo-USLM for non-USC sources)

        :returns:
            the :class:`.Code` under a key starting with ``query``, or None
        """
        for name, code in self.codes.items():
            if name.startswith(query):
                return code
        return None

    def get_code(self, uri: str) -> Optional[Code]:
        r"""
        Find a :class:`.Code` under a key corresponding to ``uri``.

        If the initial form of ``uri`` isn't found, try shorter
        versions of the uri and then search for uris that contain
        ``uri``.

        :param uri:
            identifier for legislative text in the USLM format
            (or possibly pseudo-USLM for non-USC sources)

        :returns:
            the :class:`.Code` for the ``uri``
        """
        result = self.get_code_with_uri_included_in_query(uri)
        if result:
            return result

        result = self.get_code_with_uri_that_includes_query(uri)
        return result


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
