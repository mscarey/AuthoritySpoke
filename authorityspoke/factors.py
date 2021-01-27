r""":class:`Factor`\s, or inputs and outputs of legal :class:`.Rule`\s."""

from __future__ import annotations
from copy import deepcopy

from dataclasses import field

from typing import Any, Callable, Dict, Iterable, Iterator, List
from typing import Optional, Sequence, Set, Tuple, TypeVar, Union

from legislice import Enactment

from anchorpoint.textselectors import TextQuoteSelector

from authorityspoke.statements.comparable import (
    ContextRegister,
    Comparable,
    FactorSequence,
)


class Factor(Comparable):
    """
    Things relevant to a :class:`.Court`\'s application of a :class:`.Rule`.

    The same :class:`Factor` that is in the ``outputs`` for the
    :class:`.Procedure` of one legal :class:`.Rule` might be in the
    ``inputs`` of the :class:`.Procedure` for another.
    """

    def __init__(
        self,
        *,
        generic: bool = False,
        absent: bool = False,
        name: Optional[str] = None,
        anchors: List[TextQuoteSelector] = field(default_factory=list),
    ):
        """Designate attributes inherited from Factor as keyword-only."""
        self.name = name
        self.generic = generic
        self.absent = absent
        self.anchors = anchors

    @property
    def terms(self) -> FactorSequence:
        r"""
        Get :class:`Factor`\s used in comparisons with other :class:`Factor`\s.

        :returns:
            a tuple of attributes that are designated as the ``terms``
            for whichever subclass of :class:`Factor` calls this method. These
            can be used for comparing objects using :meth:`consistent_with`
        """
        context: List[Optional[Factor]] = []
        for factor_name in self.context_factor_names:
            next_factor: Optional[Factor] = self.__dict__.get(factor_name)
            context.append(next_factor)
        return FactorSequence(context)

    def __add__(self, other: Comparable) -> Optional[Comparable]:
        if other.__class__.__name__ in ("Procedure", "Rule"):
            return other + self
        return super().__add__(other)

    def explanations_same_meaning(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        """Generate ways to match contexts of self and other so they mean the same."""
        if isinstance(other, self.__class__) and self.absent == other.absent:
            yield from super().explanations_same_meaning(other, context=context)

    def __str__(self):
        text = super().__str__()
        if self.absent:
            text = "absence of " + text

        return text


TextLinkDict = Dict[Union[Factor, Enactment], List[TextQuoteSelector]]


class FactorIndex(Dict[str, Factor]):
    r"""Index of :class:`.Factor`/s that may share common anchors."""

    def insert_by_name(self, value: Factor) -> None:
        """
        Insert Factor using its name as key if possible.

        If the Factor has no name attr, use its str as key instead.
        """
        if value.__dict__.get("name"):
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
            for anchor in value.anchors:
                if anchor not in self[key].anchors:
                    self[key].anchors.append(anchor)
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
