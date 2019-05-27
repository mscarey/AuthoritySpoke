from __future__ import annotations

from typing import List, Optional

from dataclasses import dataclass

from authorityspoke.opinions import Opinion

@dataclass
class Court:
    """
    Issues :class:`.Opinion`\s, has :class:`.Judge`\s,
    may be inferior to other `Courts`.
    """
    id: str
    opinions: Optional[List[Opinion]] = None
    inferior_to: Optional[List[Court]] = None
