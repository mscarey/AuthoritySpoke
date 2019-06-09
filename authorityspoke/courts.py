"""Classes describing judicial institutions and their effect on legal authority."""

from __future__ import annotations

from typing import List, Optional

from dataclasses import dataclass

from authorityspoke.opinions import Opinion


@dataclass
class Court:
    """
    An institution that issues :class:`.Opinion`\s and decides litigation.

    Has :class:`.Judge`\s and may be inferior to other :class:`Court`\s.
    """

    id: str
    opinions: Optional[List[Opinion]] = None
    inferior_to: Optional[List[Court]] = None
