r""":class:`Factor`\s, or inputs and outputs of legal :class:`.Rule`\s."""

from __future__ import annotations
from copy import deepcopy

from dataclasses import field

import operator
from typing import Any, Callable, Dict, Iterable, Iterator, List
from typing import Optional, Sequence, Set, Tuple, TypeVar, Union

from legislice import Enactment

from anchorpoint.textselectors import TextQuoteSelector

from authorityspoke.comparisons import (
    ContextRegister,
    Comparable,
    FactorSequence,
    means,
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
        name: Optional[str] = None,
        generic: bool = False,
        absent: bool = False,
        anchors: List[TextQuoteSelector] = field(default_factory=list),
    ):
        """Designate attributes inherited from Factor as keyword-only."""
        self.name = name
        self.generic = generic
        self.absent = absent
        self.anchors = anchors

    @property
    def context_factor_names(self) -> Tuple[str, ...]:
        """
        Get names of attributes to compare in :meth:`~Factor.means` or :meth:`~Factor.__ge__`.

        This method should be the only part
        of the context-matching process that need to be unique for each
        subclass of :class:`Factor`.

        :returns:
            attribute names identifying which attributes of ``self`` and
            ``other`` must match, for a :class:`.Analogy` to hold between
            this :class:`Factor` and another.
        """

        return ()

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

    def __add__(self, other) -> Optional[Factor]:
        if other.__class__.__name__ in ("Procedure", "Rule"):
            return other + self
        if not isinstance(other, Factor):
            raise TypeError
        if self >= other:
            return self
        if other >= self:
            return other.new_context(self.generic_factors())
        return None

    def _contradicts_if_present(
        self, other: Factor, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        """
        Test if ``self`` would contradict ``other`` if neither was ``absent``.

        The default is to yield nothing where no class-specific method is available.
        """
        yield from iter([])

    def explanations_consistent_with_factor(
        self, other: Factor, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        """
        Test whether ``self`` does not contradict ``other``.

        This should only be called after confirming that ``other``
        is not ``None``.

        :returns:
            ``True`` if self and other can't both be true at
            the same time. Otherwise returns ``False``.
        """
        if context is None:
            context = ContextRegister()
        for possible in self.possible_contexts(other, context):
            if not self.contradicts(other, context=possible):
                yield possible

    def explanations_consistent_with(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        if isinstance(other, tuple):
            raise NotImplementedError
        yield from self.explanations_consistent_with_factor(other, context=context)

    def explanations_same_meaning(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        """Generate ways to match contexts of self and other so they mean the same."""
        if (
            isinstance(other, Factor)
            and self.__class__ == other.__class__
            and self.absent == other.absent
            and self.generic == other.generic
        ):
            if self.generic:
                yield self.generic_register(other)
            yield from self._means_if_concrete(other, context)

    def _means_if_concrete(
        self, other: Factor, context: Optional[ContextRegister]
    ) -> Iterator[ContextRegister]:
        """
        Test equality based on :attr:`terms`.

        Usually called after a subclasses has injected its own tests
        based on other attributes.

        :returns:
            bool indicating whether ``self`` would equal ``other``,
            under the assumptions that neither ``self`` nor ``other``
            has ``absent=True``, neither has ``generic=True``, and
            ``other`` is an instance of ``self``'s class.
        """
        if self.compare_terms(other, means):
            yield from self._context_registers(other, comparison=means, context=context)

    def compare_terms(self, other: Factor, relation: Callable) -> bool:
        r"""
        Test if relation holds for corresponding context factors of self and other.

        This doesn't track a persistent :class:`ContextRegister` as it goes
        down the sequence of :class:`Factor` pairs. Perhaps(?) this simpler
        process can weed out :class:`Factor`\s that clearly don't satisfy
        a comparison before moving on to the more costly :class:`Analogy`
        process. Or maybe it's useful for testing.
        """
        orderings = self.term_permutations()
        for ordering in orderings:
            if self.compare_ordering_of_terms(
                other=other, relation=relation, ordering=ordering
            ):
                return True
        return False

    def compare_ordering_of_terms(
        self, other: Factor, relation: Callable, ordering: FactorSequence
    ) -> bool:
        """
        Determine whether one ordering of self's terms matches other's terms.

        Multiple term orderings exist where the terms can be rearranged without
        changing the Fact's meaning.

        For instance, "<Ann> and <Bob> both were members of the same family" has a
        second ordering "<Bob> and <Ann> both were members of the same family".
        """
        valid = True
        for i, self_factor in enumerate(ordering):
            if not (self_factor is other.terms[i] is None):
                if not (self_factor and relation(self_factor, other.terms[i])):
                    valid = False
        return valid

    def _implies_if_concrete(
        self, other: Factor, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        """
        Find if ``self`` would imply ``other`` if they aren't absent or generic.

        Used to test implication based on :attr:`terms`,
        usually after a subclass has injected its own tests
        based on other attributes.

        :returns:
            context assignments where ``self`` would imply ``other``,
            under the assumptions that neither ``self`` nor ``other``
            has ``absent=True``, neither has ``generic=True``, and
            ``other`` is an instance of ``self``'s class.
        """
        if self.compare_terms(other, operator.ge):
            yield from self._context_registers(other, operator.ge, context)

    def _implies_if_present(
        self, other: Factor, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        """
        Find if ``self`` would imply ``other`` if they aren't absent.

        :returns:
            bool indicating whether ``self`` would imply ``other``,
            under the assumption that neither self nor other has
            the attribute ``absent == True``.
        """
        if context is None:
            context = ContextRegister()
        if isinstance(other, self.__class__):
            if other.generic:
                if context.get_factor(self) is None or (
                    context.get_factor(self) == other
                ):
                    yield self.generic_register(other)
            if not self.generic:
                yield from self._implies_if_concrete(other, context)

    def make_generic(self) -> Factor:
        """
        Get a copy of ``self`` except ensure ``generic`` is ``True``.

        .. note::
            The new object created with this method will have all the
            attributes of ``self`` except ``generic=False``.
            Therefore the method isn't equivalent to creating a new
            instance of the class with only the ``generic`` attribute
            specified. To do that, you would use ``Fact(generic=True)``.

        :returns: a new object changing ``generic`` to ``True``.
        """
        result = deepcopy(self)
        result.generic = True
        return result

    def __str__(self):
        text = f"the {self.__class__.__name__}" + " {}"
        if self.generic:
            text = f"<{text}>"
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
