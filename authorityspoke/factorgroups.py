from __future__ import annotations

import operator
from typing import Optional, Sequence, Tuple, TypeVar

from authorityspoke.factors import Factor, ContextRegister, means

F = TypeVar("F")


class ComparableGroup(Tuple[F, ...]):
    r"""
    Factors to be used together in a comparison.

    The inputs, outputs, and despite :class:`.Factor`\s of
    a :class:`.Procedure` should be FactorGroups.
    """

    def __new__(cls, value: Sequence = ()):
        if isinstance(value, Factor):
            value = (value,)
        return tuple.__new__(ComparableGroup, value)

    def consistent_with(
        self, other: ComparableGroup, context: Optional[ContextRegister] = None,
    ) -> bool:
        r"""
        Find whether two sets of :class:`.Factor`\s can be consistent.

        Works by first determining whether one :class:`.Factor`
        potentially :meth:`~.Factor.contradicts` another,
        and then determining whether it's possible to make
        context assignments match between the contradictory
        :class:`.Factor`\s.

        .. Note::
            Does ``Factor: None`` in matches always mean that
            the :class:`.Factor` can avoid being matched in a
            contradictory way?

        :param context:
            correspondences between :class:`Factor`s in self and other
            that can't be changed in seeking a way to interpret the groups
            as consistent

        :returns:
            whether unassigned context factors can be assigned in such
            a way that there's no contradiction between any factor in
            ``self_factors`` and ``other_factors``, given that some
            :class:`.Factor`\s have already been assigned as
            described by ``matches``.
        """
        if context is None:
            context = ContextRegister()
        for self_factor in self:
            for other_factor in other:
                if self_factor.contradicts(other_factor):
                    if all(
                        all(
                            context.get(key) == context_register[key]
                            or context.get(context_register[key]) == key
                            for key in self_factor.generic_factors
                        )
                        for context_register in self_factor._context_registers(
                            other_factor, means
                        )
                    ):
                        return False
        return True

    def contradicts(
        self, other: ComparableGroup, context: Optional[ContextRegister] = None,
    ) -> bool:
        r"""
        Find whether two sets of :class:`.Factor`\s can be contradictory.

        :param other:
            a second set of :class:`Factor`\s with context factors that
            are internally consistent, but may not be consistent with ``self_factors``.

        :param context:
            correspondences between :class:`Factor`s in self and other
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

    def unordered_comparison(
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
                            other=other_factor, register=matches, comparison=operation
                        )
                    )
                    for new_matches in updated_mappings:
                        if new_matches is not None:
                            yield from iter(
                                self.unordered_comparison(
                                    still_need_matches=still_need_matches,
                                    operation=operation,
                                    matches=new_matches,
                                )
                            )

    def explanations_implication(
        self, other: ComparableGroup, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        yield from self.unordered_comparison(
            operation=operator.ge, still_need_matches=list(other), matches=context
        )

    def implies(
        self, other: ComparableGroup, context: Optional[ContextRegister] = None
    ) -> bool:
        return any(
            register is not None
            for register in self.explanations_implication(other, context=context)
        )

    def explanations_has_all_factors_of(
        self, other: ComparableGroup, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        yield from self.unordered_comparison(
            operation=means, still_need_matches=list(other), matches=context
        )

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
            for context in other.unordered_comparison(
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
        self, other: ComparableGroup, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        for explanation in self.explanations_shares_all_factors_with(other, context):
            yield from self.explanations_has_all_factors_of(other, explanation)

    def means(
        self, other: ComparableGroup, context: Optional[ContextRegister] = None
    ) -> bool:
        return any(
            register is not None
            for register in self.explanations_same_meaning(other, context=context)
        )


FactorGroup = ComparableGroup[Factor]
