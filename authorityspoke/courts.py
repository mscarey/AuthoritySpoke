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

    :param id:
        an identifier

    :param opinions:
        a list of :class:`.Opinion`\s issued

    :param inferior_to:
        a :class:`Court` with the power to overrule
        :class:`.Rule`\s posited by this :class:`Court`
    """

    id: str
    opinions: Optional[List[Opinion]] = None
    inferior_to: Optional[List[Court]] = None
