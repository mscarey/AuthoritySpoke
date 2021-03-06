r""":class:`Factor`\s, or inputs and outputs of legal :class:`.Rule`\s."""

from __future__ import annotations
from dataclasses import field

from typing import Dict, List, Optional, Union

from legislice import Enactment

from anchorpoint.textselectors import TextQuoteSelector

from nettlesome.terms import Comparable
from nettlesome.factors import Factor


class FactorIndex(Dict[str, Factor]):
    r"""Index of :class:`.Factor`/s that may share common anchors."""

    def insert_by_name(self, value: Factor) -> None:
        """
        Insert Factor using its name as key if possible.

        If the Factor has no name attr, use its str as key instead.
        """
        if value.name:
            self.insert(key=value.name, value=value)
            return None
        key = str(value)
        for name, saved_factor in self.items():
            if key == str(saved_factor):
                for anchor in value.anchors:
                    if anchor not in self[name].anchors:
                        self[name].anchors.append(anchor)
                return None
        self.insert(key=key, value=value)

    def insert(self, key: str, value: Factor) -> None:
        """Insert Factor using its str as its key."""
        if key in self.keys():
            if value.name:
                if not self[key].name:
                    self[key].name = value.name
                if value.name != self[key].name:
                    raise NameError(
                        f"{type(value)} objects with identical representation ({str(value)}) "
                        f"have differing names: '{value.name}' and '{self[key].name}'"
                    )
        else:
            self[key] = value
