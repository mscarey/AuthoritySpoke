from __future__ import annotations

import json
import operator
import pathlib

from typing import ClassVar, Dict, Iterable, List, Sequence, Tuple
from typing import Iterator, Optional, Union

from dataclasses import dataclass

from authorityspoke.context import get_directory_path
from authorityspoke.rules import Rule


@dataclass(frozen=True)
class Holding:
    """
    An :class:`.Opinion`\'s announcement that it posits or rejects a legal :class:`.Rule`.

    Note that if an opinion merely says the court is not deciding whether
    a :class:`.Rule` is valid, there is no :class:`Holding`, and no
    :class:`.Rule` object should be created. Deciding not to decide
    a :class:`Rule`\'s validity is not the same thing as deciding
    that the :class:`.Rule` is undecided.

    :param rule:
        a statement of a legal doctrine about a :class:`.Procedure` for litigation.

    :param rule_valid:
        ``True`` means the :class:`Rule` is asserted to be valid (or
        useable by a court in litigation). ``False`` means it's asserted
        to be invalid.

    :param decided:
        ``False`` means that it should be deemed undecided
        whether the :class:`Rule` is valid, and thus can have the
        effect of overruling prior holdings finding the :class:`.Rule`
        to be either valid or invalid. Seemingly, ``decided=False``
        should render the ``rule_valid`` flag irrelevant.
    """

    rule: Rule
    rule_valid: bool = True
    decided: bool = True

    directory: ClassVar = get_directory_path("holdings")

    @classmethod
    def from_dict(
        cls, record: Dict, mentioned: List[Factor], regime: Optional[Regime] = None
    ) -> Iterator[Tuple[Holding, List[Factor], Dict[Factor, TextQuoteSelector]]]:
        """
        Will yield multiple items if ``exclusive: True`` is present in ``record``.
        """

        pass
