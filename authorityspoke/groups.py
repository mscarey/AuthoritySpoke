from __future__ import annotations

import operator
from typing import Callable, Dict, Iterator, Optional, Sequence, Tuple, TypeVar

from authorityspoke.comparisons import (
    Comparable,
    ContextRegister,
    means,
)
from authorityspoke.explanations import Explanation
from authorityspoke.factors import Factor

F = TypeVar("F", bound="Factor")


class ComparableGroup(Tuple[F, ...], Comparable):
    r"""
    Factors to be used together in a comparison.

    The inputs, outputs, and despite :class:`.Factor`\s of
    a :class:`.Procedure` should be FactorGroups.
    """

    def __new__(cls, value: Sequence = ()):
        if isinstance(value, Factor):
            value = (value,)
        return tuple.__new__(ComparableGroup, value)

    def __add__(self, other) -> ComparableGroup:
        added = tuple(self) + ComparableGroup(other)
        return ComparableGroup(added)

    def __getitem__(self, key):
        if isinstance(key, int):
            return super().__getitem__(key)
        return self.__class__(super().__getitem__(key))

    def _must_contradict_one_factor(
        self, other_factor: Comparable, context: ContextRegister
    ) -> bool:
        for self_factor in self:
            if self_factor.contradicts(other_factor, context=context):
                if self_factor.all_generic_factors_match(other_factor, context=context):
                    return True
        return False

    def consistent_with(
        self,
        other: Optional[Comparable],
        context: Optional[ContextRegister] = None,
    ) -> bool:
        r"""
        Find whether two sets of :class:`.Factor`\s can be consistent.

        Works by first determining whether one :class:`.Factor`
        potentially :meth:`~.Factor.contradicts` another,
        and then determining whether it's possible to make
        context assignments match between the contradictory
        :class:`.Factor`\s.

        :param other:

        :param context:
            correspondences between :class:`Factor`\s in self and other
            that can't be changed in seeking a way to interpret the groups
            as consistent

        :returns:
            whether unassigned context factors can be assigned in such
            a way that there's no contradiction between any factor in
            ``self_factors`` and ``other_factors``, given that some
            :class:`.Factor`\s have already been assigned as
            described by ``matches``.
        """
        if other is None:
            return True
        if context is None:
            context = ContextRegister()
        if isinstance(other, ComparableGroup):
            for other_factor in other:
                if self._must_contradict_one_factor(other_factor, context=context):
                    return False
            return True
        return self._must_contradict_one_factor(other, context=context)

    def contradicts(
        self,
        other: ComparableGroup,
        context: Optional[ContextRegister] = None,
    ) -> bool:
        r"""
        Find whether two sets of :class:`.Factor`\s can be contradictory.

        :param other:
            a second set of :class:`Factor`\s with context factors that
            are internally consistent, but may not be consistent with ``self_factors``.

        :param context:
            correspondences between :class:`Factor`\s in self and other
            that can't be changed in seeking a contradiction

        :returns:
            whether any :class:`.Factor` assignment can be found that
            makes a :class:`.Factor` in the output of ``other`` contradict
            a :class:`.Factor` in the output of ``self``.
        """
        if context is None:
            context = ContextRegister()
        for other_factor in other:
            for self_factor in self:
                if self_factor.contradicts(other_factor, context):
                    return True
        return False

    def comparison(
        self,
        operation: Callable,
        still_need_matches: Sequence[Factor],
        matches: ContextRegister = None,
    ) -> Iterator[ContextRegister]:
        r"""
        Find ways for two unordered sets of :class:`.Factor`\s to satisfy a comparison.

        All of the elements of `other` need to fit the comparison. The elements of
        `self` don't all need to be used.

        :param context:
            a mapping of :class:`.Factor`\s that have already been matched
            to each other in the recursive search for a complete group of
            matches. Usually starts empty when the method is first called.

        :param still_need_matches:
            :class:`.Factor`\s that need to satisfy the comparison
            :attr:`comparison` with some :class:`.Factor` of :attr:`available`
            for the relation to hold, and have not yet been matched.

        :param matches:
            a :class:`.ContextRegister` matching generic :class:`.Factor`\s

        :yields:
            context registers showing how each :class:`.Factor` in
            ``need_matches`` can have the relation ``comparison``
            with some :class:`.Factor` in ``available_for_matching``,
            with matching context.
        """
        still_need_matches = list(still_need_matches)

        if matches is None:
            matches = ContextRegister()

        if not still_need_matches:
            yield matches
        else:
            other_factor = still_need_matches.pop()
            for self_factor in self:
                if operation(self_factor, other_factor):
                    updated_mappings = iter(
                        self_factor.update_context_register(
                            other=other_factor, context=matches, comparison=operation
                        )
                    )
                    for new_matches in updated_mappings:
                        if new_matches is not None:
                            yield from iter(
                                self.comparison(
                                    still_need_matches=still_need_matches,
                                    operation=operation,
                                    matches=new_matches,
                                )
                            )

    def get_factor_by_name(self, name: str) -> Factor:
        for comparable in self:
            answer = comparable.get_factor_by_name(name)
            if answer:
                return answer
        return None

    def get_factor_by_str(self, query: str) -> Optional[Factor]:
        """
        Search of ``self`` and ``self``'s attributes for :class:`Factor` with specified string.

        :returns:
            a :class:`Factor` with the specified string
            if it exists, otherwise ``None``.
        """
        for comparable in self:
            for name, factor in comparable.recursive_factors.items():
                if name == query:
                    return factor
        return None

    def verbose_comparison(
        self,
        operation: Callable,
        still_need_matches: Sequence[Factor],
        explanation: Explanation = None,
    ) -> Iterator[Explanation]:
        r"""
        Find ways for two unordered sets of :class:`.Factor`\s to satisfy a comparison.

        All of the elements of `other` need to fit the comparison. The elements of
        `self` don't all need to be used.

        :param context:
            a mapping of :class:`.Factor`\s that have already been matched
            to each other in the recursive search for a complete group of
            matches. Usually starts empty when the method is first called.

        :param still_need_matches:
            :class:`.Factor`\s that need to satisfy the comparison
            :attr:`comparison` with some :class:`.Factor` of :attr:`available`
            for the relation to hold, and have not yet been matched.

        :param explanation:
            an :class:`.Explanation` showing which :class:`.Factor`\s listed in the
            FactorGroups were matched to each other, and also including a
            :class:`.ContextRegister`\.

        :yields:
            context registers showing how each :class:`.Factor` in
            ``need_matches`` can have the relation ``comparison``
            with some :class:`.Factor` in ``available_for_matching``,
            with matching context.
        """
        still_need_matches = list(still_need_matches)

        if explanation is None:
            explanation = Explanation(
                matches=[], context=ContextRegister(), operation=operation
            )

        if not still_need_matches:
            yield explanation
        else:
            other_factor = still_need_matches.pop()
            for self_factor in self:
                if operation(self_factor, other_factor):
                    updated_mappings = iter(
                        self_factor.update_context_register(
                            other=other_factor,
                            context=explanation.context,
                            comparison=operation,
                        )
                    )
                    new_explanation = explanation.add_match((self_factor, other_factor))
                    for new_matches in updated_mappings:
                        if new_matches is not None:
                            yield from iter(
                                self.verbose_comparison(
                                    still_need_matches=still_need_matches,
                                    operation=operation,
                                    explanation=new_explanation,
                                )
                            )

    def explanations_implication(
        self, other: ComparableGroup, context: Optional[ContextRegister] = None
    ) -> Iterator[Explanation]:
        explanation = Explanation(matches=[], context=context or ContextRegister())
        yield from self.verbose_comparison(
            operation=operator.ge,
            still_need_matches=list(other),
            explanation=explanation,
        )

    def explanations_has_all_factors_of(
        self, other: ComparableGroup, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        yield from self.comparison(
            operation=means, still_need_matches=list(other), matches=context
        )

    def generic_factors_by_str(self) -> Dict[str, Comparable]:
        generics: Dict[str, Comparable] = {}
        for factor in self:
            generics.update(factor.generic_factors_by_str())
        return generics

    def has_all_factors_of(
        self, other: ComparableGroup, context: Optional[ContextRegister] = None
    ) -> bool:
        return any(
            register is not None
            for register in self.explanations_has_all_factors_of(other, context=context)
        )

    def explanations_shares_all_factors_with(
        self, other: ComparableGroup, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        context = context or ContextRegister()
        context_for_other = context.reversed()
        yield from (
            context.reversed()
            for context in other.comparison(
                operation=means,
                still_need_matches=list(self),
                matches=context_for_other,
            )
        )

    def shares_all_factors_with(
        self, other: ComparableGroup, context: Optional[ContextRegister] = None
    ) -> bool:
        return any(
            register is not None
            for register in self.explanations_shares_all_factors_with(
                other, context=context
            )
        )

    def explanations_same_meaning(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        if isinstance(other, self.__class__):
            for explanation in self.explanations_shares_all_factors_with(
                other, context
            ):
                yield from self.explanations_has_all_factors_of(other, explanation)

    def _context_registers(
        self,
        other: Optional[ComparableGroup],
        comparison: Callable,
        context: Optional[ContextRegister] = None,
    ) -> Iterator[ContextRegister]:
        r"""
        Search for ways to match :attr:`terms` of ``self`` and ``other``.

        :yields:
            all valid ways to make matches between
            corresponding :class:`Factor`\s.
        """
        if context is None:
            context = ContextRegister()
        if other is None:
            yield context
        else:
            yield from self.comparison(
                operation=comparison, still_need_matches=list(other), matches=context
            )

    def _likely_contexts_for_factor(
        self, other: Factor, context: ContextRegister, i: int = 0
    ) -> Iterator[ContextRegister]:
        if i == len(self):
            yield context
        else:
            next_factor = self[i]
            for new_context in next_factor.likely_contexts(other, context):
                yield from self._likely_contexts_for_factor(other, new_context, i + 1)

    def _likely_contexts_for_factorgroup(
        self, other: FactorGroup, context: ContextRegister, j: int = 0
    ) -> Iterator[ContextRegister]:
        if j == len(other):
            yield context
        else:
            next_factor = other[j]
            for new_context in self._likely_contexts_for_factor(next_factor, context):
                yield from self._likely_contexts_for_factorgroup(
                    other, new_context, j + 1
                )

    def likely_contexts(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        context = context or ContextRegister()
        if isinstance(other, Factor):
            yield from self._likely_contexts_for_factor(other, context)
        else:
            yield from self._likely_contexts_for_factorgroup(other, context)

    def drop_implied_factors(self) -> ComparableGroup:
        """
        Reduce group by removing redundant members implied by other members.

        :returns:
            new group with any redundant items remomved
        """
        result = []
        unchecked = list(self)
        while unchecked:
            current = unchecked.pop()
            for item in unchecked:
                if item.implies_same_context(current):
                    current = item
                    unchecked.remove(item)
                elif current.implies_same_context(item):
                    unchecked.remove(item)
            result.append(current)
        return ComparableGroup(result)

    def internally_consistent(self, context: Optional[ContextRegister] = None) -> bool:
        """
        Check for contradictions among the Factors in self.

        :returns: bool indicating whether self is internally consistent
        """
        context = context or ContextRegister()
        unchecked = list(self)
        while unchecked:
            current = unchecked.pop()
            for item in unchecked:
                if not current.consistent_with(item, context):
                    return False
        return True

    def new_context(self, changes: ContextRegister) -> ComparableGroup:
        result = [factor.new_context(changes) for factor in self]
        return ComparableGroup(result)

    def partial_explanations_union(
        self, other: Comparable, context: ContextRegister
    ) -> Iterator[ContextRegister]:
        for likely in self.likely_contexts(other, context):
            partial = self + other.new_context(likely.reversed())
            if partial.internally_consistent():
                yield likely

    def union_from_explanation(
        self, other: ComparableGroup, context: ContextRegister
    ) -> Optional[ComparableGroup]:
        result = self.union_from_explanation_allow_contradiction(other, context)
        if not result.internally_consistent():
            return None
        return result

    def union_from_explanation_allow_contradiction(
        self, other: ComparableGroup, context: ContextRegister
    ) -> ComparableGroup:
        updated_context = context.reversed() if context else None
        result = self + other.new_context(changes=updated_context)
        result = result.drop_implied_factors()
        return result


FactorGroup = ComparableGroup[Factor]
