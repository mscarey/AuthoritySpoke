from __future__ import annotations

from abc import ABC
from copy import deepcopy
from itertools import permutations, zip_longest
import logging
from typing import Callable, Dict, Iterator, List, Optional, Type, Union

logger = logging.getLogger(__name__)


def consistent_with(left: Comparable, right: Comparable) -> bool:
    """
    Call :meth:`.Factor.consistent_with` as function alias.

    This exists because :func:`Factor._context_registers` needs
    a function rather than a method for the `comparison` variable.

    :returns:
        whether ``other`` is consistent with ``self``.
    """
    return left.consistent_with(right)


def means(left: Comparable, right: Comparable) -> bool:
    """
    Call :meth:`.Factor.means` as function alias.

    This exists because :class:`.Explanation` objects expect
    a function rather than a method

    :returns:
        whether ``other`` is another :class:`Factor` with the same
        meaning as ``self``.
    """
    return left.means(right)


def contradicts(left: Comparable, right: Comparable) -> bool:
    """
    Call :meth:`.Factor.contradicts` as function alias.

    This exists because :class:`.Explanation` objects expect
    a function rather than a method

    :returns:
        whether ``other`` is another :class:`Factor` that can
        contradict ``self``, assuming relevant context factors
    """
    return left.contradicts(right)


class Comparable(ABC):
    generic: bool = False

    def consistent_with(
        self, other: Optional[Comparable], context: Optional[ContextRegister] = None
    ) -> bool:
        """
        Check if self and other can be non-contradictory.

        :returns:
            a bool indicating whether there's at least one way to
            match the :attr:`context_factors` of ``self`` and ``other``,
            such that they fit the relationship ``comparison``.
        """

        if other is None:
            return True
        return any(
            explanation is not None
            for explanation in self.explanations_consistent_with(other, context)
        )

    def generic_register(self, other: Comparable) -> ContextRegister:
        register = ContextRegister()
        register.insert_pair(self, other)
        return register

    def _context_registers(
        self,
        other: Optional[Comparable],
        comparison: Callable,
        context: Optional[ContextRegister] = None,
    ) -> Iterator[ContextRegister]:
        r"""
        Search for ways to match :attr:`context_factors` of ``self`` and ``other``.

        :yields:
            all valid ways to make matches between
            corresponding :class:`Factor`\s.
        """
        if context is None:
            context = ContextRegister()
        if other is None:
            yield context
        elif self.generic or other.generic:
            if context.get(str(self)) is None or (context.get(str(self)) == other):
                yield self.generic_register(other)
        else:
            yield from self.context_factors.ordered_comparison(
                other=other.context_factors, operation=comparison, context=context
            )

    def all_generic_factors_match(self, other: Comparable, context: ContextRegister):
        if all(
            all(
                context.get_factor(key) == context_register.get_factor(key)
                or context.get_factor(context_register.get(str(key))) == key
                for key in self.generic_factors
            )
            for context_register in self._context_registers(
                other=other, comparison=means, context=context
            )
        ):
            return True
        return False

    def contradicts(
        self, other: Optional[Comparable], context: Optional[ContextRegister] = None
    ) -> bool:
        """
        Test whether ``self`` implies the absence of ``other``.

        :returns:
            ``True`` if self and other can't both be true at
            the same time. Otherwise returns ``False``.
        """

        if other is None:
            return False
        return any(
            explanation is not None
            for explanation in self.explanations_contradiction(other, context)
        )

    @property
    def context_factors(self) -> List[Comparable]:
        r"""
        :class:`.Factor`\s that can be replaced without changing ``self``\s meaning.

        :returns:
            a :class:`list` made from a :class:`dict` with ``self``\'s
            generic :class:`.Factor`\s as keys and ``None`` as values,
            so that the keys can be matched to another object's
            ``generic_factors`` to perform an equality test.
        """
        return []

    @property
    def generic_factors(self) -> List[Comparable]:
        return list(self.generic_factors_by_name.values())

    @property
    def generic_factors_by_name(self) -> Dict[str, Comparable]:
        r"""
        :class:`.Factor`\s that can be replaced without changing ``self``\s meaning.

        :returns:
            a :class:`list` made from a :class:`dict` with ``self``\'s
            generic :class:`.Factor`\s as keys and ``None`` as values,
            so that the keys can be matched to another object's
            ``generic_factors`` to perform an equality test.
        """

        if self.generic:
            return {str(self): self}
        generics: Dict[str, Comparable] = {}
        for factor in self.context_factors:
            if factor is not None:
                for generic in factor.generic_factors:
                    generics[str(generic)] = generic
        return generics

    @property
    def interchangeable_factors(self) -> List[ContextRegister]:
        """
        List ways to reorder :attr:`context_factors` but preserve ``self``\'s meaning.

        The empty list is the default return value for subclasses that don't
        have any interchangeable :attr:`context_factors`.

        :returns:
            the ways :attr:`context_factors` can be reordered without
            changing the meaning of ``self``, or whether it would
            be true in a particular context.
        """
        return []

    def implied_by(
        self, other: Optional[Comparable], context: Optional[ContextRegister] = None
    ):
        """Test whether ``other`` implies ``self``."""
        if other is None:
            return False
        return any(
            register is not None
            for register in self.explanations_implied_by(other, context=context)
        )

    def implies(
        self, other: Optional[Comparable], context: Optional[ContextRegister] = None
    ) -> bool:
        """Test whether ``self`` implies ``other``."""
        if other is None:
            return True
        return any(
            register is not None
            for register in self.explanations_implication(other, context=context)
        )

    def implies_same_context(self, other) -> bool:
        same_context = ContextRegister()
        for key in self.generic_factors:
            same_context.insert_pair(key, key)
        return self.implies(other, context=same_context)

    def means(
        self, other: Optional[Comparable], context: Optional[ContextRegister] = None
    ) -> bool:
        r"""
        Test whether ``self`` and ``other`` have identical meanings.

        :returns:
            whether ``other`` is another :class:`Factor`
            with the same meaning as ``self``. Not the same as an
            equality comparison with the ``==`` symbol, which simply
            converts ``self``\'s and ``other``\'s fields to tuples
            and compares them.
        """
        if other is None:
            return False
        return any(
            explanation is not None
            for explanation in self.explanations_same_meaning(other, context=context)
        )

    def means_same_context(self, other) -> bool:
        same_context = ContextRegister()
        for key in self.generic_factors:
            same_context.insert_pair(key, key)
        return self.means(other, context=same_context)

    def possible_contexts(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        r"""
        Get permutations of generic Factor assignments not ruled out by the known context.

        :param other:
            another :class:`.Comparable` object with generic :class:`.Factor`\s

        :yields: all possible ContextRegisters linking the two :class:`.Comparable`\s
        """
        context = context or ContextRegister()
        unused_self = [
            factor
            for factor in self.generic_factors
            if str(factor) not in context.matches.keys()
        ]
        unused_other = [
            factor
            for factor in other.generic_factors
            if str(factor) not in context.reverse_matches.keys()
        ]
        if not (unused_self and unused_other):
            yield context
        else:
            for permutation in permutations(unused_other):
                incoming = ContextRegister()
                for key, value in zip_longest(unused_self, permutation):
                    incoming.insert_pair(key=key, value=value)
                merged_context = context.merged_with(incoming)
                if merged_context:
                    yield merged_context

    def __or__(self, other: Comparable):
        return self.union(other)

    def explanations_union(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        context = context or ContextRegister()
        for partial in self.partial_explanations_union(other, context):
            for guess in self.possible_contexts(other, partial):
                answer = self.union_from_explanation(other, guess)
                if answer:
                    yield guess

    def _registers_for_interchangeable_context(
        self, matches: ContextRegister
    ) -> Iterator[ContextRegister]:
        r"""
        Find possible combination of interchangeable :attr:`context_factors`.

        :yields:
            context registers with every possible combination of
            ``self``\'s and ``other``\'s interchangeable
            :attr:`context_factors`.
        """
        yield matches
        already_returned: List[ContextRegister] = [matches]
        for replacement_dict in self.interchangeable_factors:
            changed_registry = matches.replace_keys(replacement_dict)
            if not any(
                changed_registry == returned_dict for returned_dict in already_returned
            ):
                already_returned.append(changed_registry)
                yield changed_registry

    def union(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Optional[Comparable]:
        context = context or ContextRegister()
        explanations = self.explanations_union(other, context)
        try:
            explanation = next(explanations)
        except StopIteration:
            return None
        return self.union_from_explanation(other, explanation)

    def update_context_register(
        self,
        other: Optional[Comparable],
        context: ContextRegister,
        comparison: Callable,
    ) -> Iterator[ContextRegister]:
        r"""
        Find ways to update ``self_mapping`` to allow relationship ``comparison``.

        :param other:
            another :class:`Comparable` being compared to ``self``

        :param register:
            keys representing :class:`Comparable`\s from ``self``'s context and
            values representing :class:`Comparable`\s in ``other``'s context.

        :param comparison:
            a function defining the comparison that must be ``True``
            between ``self`` and ``other``. Could be :meth:`Comparable.means` or
            :meth:`Comparable.__ge__`.

        :yields:
            every way that ``self_mapping`` can be updated to be consistent
            with ``self`` and ``other`` having the relationship
            ``comparison``.
        """
        if other and not isinstance(other, Comparable):
            raise TypeError
        if not isinstance(context, ContextRegister):
            raise TypeError
        for incoming_register in self._context_registers(other, comparison):
            for new_register_variation in self._registers_for_interchangeable_context(
                incoming_register
            ):
                register_or_none = context.merged_with(new_register_variation)
                if register_or_none is not None:
                    yield register_or_none

    def explain_same_meaning(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Optional[ContextRegister]:
        """Get one explanation of why self and other have the same meaning."""
        explanations = self.explanations_same_meaning(other, context=context)
        try:
            explanation = next(explanations)
        except StopIteration:
            return None
        return explanation

    def explain_consistent_with(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Optional[ContextRegister]:
        """Get one explanation of why self and other need not contradict."""
        explanations = self.explanations_consistent_with(other, context=context)
        try:
            explanation = next(explanations)
        except StopIteration:
            return None
        return explanation

    def explain_contradiction(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Optional[ContextRegister]:
        """Get one explanation of why self and other contradict."""
        explanations = self.explanations_contradiction(other, context=context)
        try:
            explanation = next(explanations)
        except StopIteration:
            return None
        return explanation

    def explain_implication(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Optional[ContextRegister]:
        """Get one explanation of why self implies other."""
        explanations = self.explanations_implication(other, context=context)
        try:
            explanation = next(explanations)
        except StopIteration:
            return None
        return explanation

    def explain_implied_by(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Optional[ContextRegister]:
        """Get one explanation of why self implies other."""
        explanations = self.explanations_implied_by(other, context=context)
        try:
            explanation = next(explanations)
        except StopIteration:
            return None
        return explanation

    def explanations_consistent_with(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        raise NotImplementedError

    def explanations_contradiction(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        raise NotImplementedError

    def explanations_implication(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        raise NotImplementedError

    def explanations_implied_by(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        context = context or ContextRegister()
        yield from (
            register.reversed()
            for register in other.explanations_implication(
                self, context=context.reversed()
            )
        )

    def explanations_same_meaning(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        raise NotImplementedError


class ContextRegister:
    r"""
    A mapping of corresponding :class:`Factor`\s from two different contexts.

    When :class:`Factor`\s are matched in a ContextRegister, it indicates
    that their relationship can be described by a comparison function
    like :func:`means`, :meth:`Factor.implies`, or :meth:`Factor.consistent_with`\.
    """

    def __init__(self):
        self._matches = {}
        self._reverse_matches = {}

    def __len__(self):
        return len(self.matches)

    def __repr__(self) -> str:
        return "ContextRegister({})".format(self._matches.__repr__())

    def __str__(self) -> str:
        item_names = [f"{str(k)} -> {str(v)}" for k, v in self.matches.items()]
        items = ", ".join(item_names)
        return f"ContextRegister({items})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.matches == other.matches

    @property
    def matches(self):
        return self._matches

    @property
    def reverse_matches(self):
        return self._reverse_matches

    @classmethod
    def from_lists(
        cls, keys=List[Comparable], values=List[Comparable]
    ) -> ContextRegister:
        pairs = zip_longest(keys, values)
        new = cls()
        for pair in pairs:
            new.insert_pair(pair[0], pair[1])
        return new

    def check_match(self, key: Comparable, value: Comparable) -> bool:
        return self.get(str(key)) == value

    def get(self, query: str) -> Optional[Comparable]:
        return self.matches.get(query)

    def get_reverse(self, query: str) -> Optional[Comparable]:
        return self.reverse_matches.get(query)

    def get_factor(self, query: Optional[Comparable]) -> Optional[Comparable]:
        return self.get(str(query))

    def get_reverse_factor(self, query: Optional[Comparable]) -> Optional[Comparable]:
        return self.reverse_matches.get(str(query))

    def items(self):
        return self.matches.items()

    def keys(self):
        return self.matches.keys()

    def values(self):
        return self.matches.values()

    def insert_pair(self, key: Comparable, value: Comparable) -> None:
        self._matches[str(key)] = value
        self._reverse_matches[str(value)] = key

    def replace_keys(self, replacements: ContextRegister) -> ContextRegister:
        """Construct new :class:`ContextRegister` by replacing keys."""

        keys = []
        for factor in self.matches.keys():
            replacement = replacements.get(factor)
            if replacement:
                keys.append(str(replacement))
            else:
                keys.append(factor)
        values = list(self.matches.values())
        return ContextRegister.from_lists(keys, values)

    def reversed(self):
        """Swap keys for values and vice versa."""
        return ContextRegister.from_lists(
            keys=self.reverse_matches.keys(), values=self.reverse_matches.values()
        )

    def reverse_match(self, query: Comparable) -> Optional[str]:
        value_str = str(query)
        return self.reverse_matches.get(value_str)

    def merged_with(
        self, incoming_mapping: ContextRegister
    ) -> Optional[ContextRegister]:
        r"""
        Create a new merged :class:`ContextRegister`\.

        :param incoming_mapping:
            an incoming mapping of :class:`Factor`\s
            from ``self`` to :class:`Factor`\s.

        :returns:
            ``None`` if the same :class:`Factor` in one mapping
            appears to match to two different :class:`Factor`\s in the other.
            Otherwise returns an updated :class:`ContextRegister` of matches.
        """
        self_mapping = deepcopy(self)
        for in_key, in_value in incoming_mapping.matches.items():

            if in_value:
                if self_mapping.get(in_key) and self_mapping.get(in_key) != in_value:
                    logger.debug(
                        f"{in_key} already in mapping with value "
                        + f"{self_mapping.matches[in_key]}, not {in_value}"
                    )
                    return None
                key_as_factor = incoming_mapping.reverse_matches.get(str(in_value))
                self_mapping.insert_pair(key_as_factor, in_value)
                if list(self_mapping.matches.values()).count(in_value) > 1:
                    logger.debug("%s assigned to two different keys", in_value)
                    return None
        return self_mapping
