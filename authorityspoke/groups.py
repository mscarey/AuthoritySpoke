"""Groups of comparable Terms."""

from __future__ import annotations

from copy import deepcopy
import functools
import operator
import textwrap
from typing import Callable, ClassVar, Dict, Iterator, List
from typing import Optional, Sequence, Tuple, Union

from nettlesome.factors import Factor
from nettlesome.terms import (
    Comparable,
    ContextMemo,
    ContextRegister,
    DuplicateTermError,
)
from nettlesome.terms import Explanation, Term, contradicts, means
from authorityspoke.facts import AbsenceOfFactor


def unique_explanations(func: Callable):
    """Filter out any duplicate Explanations before yielding them from func."""

    @functools.wraps(func)
    def wrapper(
        factor,
        other: Comparable,
        context: Optional[Union[ContextMemo, Explanation]] = None,
    ) -> Iterator[Explanation]:
        seen: List[Explanation] = []
        for explanation in func(factor, other, context):
            if not any(explanation.means(item) for item in seen):
                seen.append(explanation)
                yield explanation

    return wrapper


class FactorGroup(Comparable):
    r"""Terms to be used together in a comparison."""

    term_class = Factor
    absence_class = AbsenceOfFactor
    generic: bool = False
    context_factor_names: ClassVar[Tuple[str, ...]] = ()

    def __init__(
        self,
        factors: FactorGroup
        | Sequence[Factor | AbsenceOfFactor]
        | Factor
        | AbsenceOfFactor = (),
    ):
        """Normalize ``factors`` as sequence attribute."""
        if isinstance(factors, FactorGroup):
            self.sequence: Tuple[Factor, ...] = factors.sequence
        elif isinstance(factors, Sequence):
            self.sequence = tuple(factors)
        else:
            self.sequence = (factors,)
        for factor in self.sequence:
            if not isinstance(factor, (self.term_class, self.absence_class)):
                raise TypeError(
                    f'Object "{factor} could not be included in '
                    f"{self.__class__.__name__} because it is "
                    f"type {factor.__class__.__name__}, not type {self.term_class.__name__}"
                )

    def _at_index(self, key: int) -> Factor:
        return self.sequence[key]

    def __getitem__(self, key: Union[int, slice]) -> Union[Factor, FactorGroup]:
        if isinstance(key, slice):
            start, stop, step = key.indices(len(self))
            return self.__class__([self._at_index(i) for i in range(start, stop, step)])
        return self._at_index(key)

    def __iter__(self):
        yield from self.sequence

    def __len__(self):
        return len(self.sequence)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(list(self.sequence))})"

    def __str__(self):
        result = "the group of Factors:"
        indent = "  "
        for factor in self.sequence:
            result += f"\n{textwrap.indent(str(factor), prefix=indent)}"
        return result

    def _add_group(self, other: FactorGroup) -> FactorGroup:
        combined = self.sequence[:] + other.sequence[:]
        return self.__class__(combined)

    def add(
        self,
        other: Union[FactorGroup, Sequence[Factor], Factor],
    ) -> Optional[FactorGroup]:
        """Combine all Factors into a single FactorGroup."""
        try:
            return self.add_or_raise_error(other)
        except ValueError:
            return None

    def add_or_raise_error(
        self,
        other: Union[FactorGroup, Sequence[Factor], Factor],
    ) -> FactorGroup:
        """Combine all Factors into a single FactorGroup."""
        if isinstance(other, self.__class__):
            return self._add_group(other)
        to_add = self.__class__(other)
        added = self._add_group(to_add)
        added.internally_consistent()
        return added

    def __add__(
        self, other: Union[FactorGroup, Sequence[Factor], Factor]
    ) -> Optional[FactorGroup]:
        return self.add(other)

    @property
    def recursive_terms(self) -> Dict[str, Term]:
        r"""
        Collect `self`'s :attr:`terms`, and their :attr:`terms`, recursively.

        :returns:
            a :class:`dict` (instead of a :class:`set`,
            to preserve order) of :class:`Factor`\s.
        """
        result: Dict[str, Term] = {}
        for context in self:
            result.update(context.recursive_terms)
        return result

    def __gt__(self, other: Optional[Comparable]) -> bool:
        """Test whether ``self`` implies ``other`` and ``self`` != ``other``."""
        if other is None:
            return True
        return bool(self.implies(other) and not self.means(other))

    def _must_contradict_one_factor(
        self, other_factor: Comparable, context: ContextRegister
    ) -> bool:
        for self_factor in self:
            if self_factor.contradicts(
                other_factor, context=context
            ) and self_factor._all_generic_terms_match(other_factor, context=context):
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
        if isinstance(other, self.__class__):
            for other_factor in other:
                if self._must_contradict_one_factor(other_factor, context=context):
                    return False
            return True
        return not self._must_contradict_one_factor(other, context=context)

    def _explain_contradicts_factor(
        self, other: Comparable, explanation: Explanation
    ) -> Iterator[Explanation]:
        for self_factor in self:
            yield from self_factor.explanations_contradiction(other, explanation)

    def _explanations_contradiction(
        self,
        other: Comparable,
        explanation: Explanation,
    ) -> Iterator[Explanation]:
        """Find contexts that would cause ``self`` to contradict ``other``."""

        explanation.operation = contradicts

        if isinstance(other, FactorGroup):
            for other_factor in other:
                yield from self._explain_contradicts_factor(
                    other_factor, explanation=explanation
                )
        else:
            yield from self._explain_contradicts_factor(other, explanation=explanation)

    @unique_explanations
    def explanations_contradiction(
        self,
        other: Comparable,
        context: Optional[Union[ContextMemo, Explanation]] = None,
    ) -> Iterator[Explanation]:
        """
        Find contexts that would cause ``self`` to contradict ``other``.

        In this example, by adding a context parameter to this method's comparison
        of two FactorGroups for contradiction, we can narrow down how nettlesome
        discovers analogies between the Entity objects. The result is that
        nettlesome finds only two Explanations for how a contradiction can exist.

            >>> from nettlesome import Statement, Entity
            >>> nafta = FactorGroup([
            ... Statement(predicate="$country1 signed a treaty with $country2",
            ...     terms=[Entity(name="Mexico"), Entity(name="USA")]),
            ... Statement(predicate="$country2 signed a treaty with $country3",
            ...     terms=[Entity(name="USA"), Entity(name="Canada")]),
            ... Statement(predicate="$country3 signed a treaty with $country1",
            ...    terms=[Entity(name="USA"), Entity(name="Canada")])])
            >>> brexit = FactorGroup([
            ... Statement(predicate="$country1 signed a treaty with $country2",
            ...     terms=[Entity(name="UK"), Entity(name="European Union")]),
            ... Statement(predicate="$country2 signed a treaty with $country3",
            ...     terms=[Entity(name="European Union"), Entity(name="Germany")]),
            ... Statement(predicate="$country3 signed a treaty with $country1",
            ...     terms=[Entity(name="Germany"), Entity(name="UK")], truth=False)])
            >>> explanations_usa_like_uk = nafta.explanations_contradiction(
            ...     brexit,
            ...     context=([Entity(name="USA")], [Entity(name="UK")]))
            >>> len(list(explanations_usa_like_uk))
            2
        """

        context = Explanation.from_context(
            context=context, current=self, incoming=other
        )
        yield from self._explanations_contradiction(other=other, explanation=context)

    def contradicts(
        self,
        other: Optional[Comparable],
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

        >>> from nettlesome import Statement, Entity
        >>> nafta = FactorGroup([
        ... Statement(predicate="$country1 signed a treaty with $country2",
        ...        terms=[Entity(name="Mexico"), Entity(name="USA")]),
        ... Statement(predicate="$country2 signed a treaty with $country3",
        ...        terms=[Entity(name="USA"), Entity(name="Canada")]),
        ... Statement(predicate="$country3 signed a treaty with $country1",
        ...    terms=[Entity(name="USA"), Entity(name="Canada")])])
        >>> brexit = FactorGroup([
        ... Statement(predicate="$country1 signed a treaty with $country2",
        ...         terms=[Entity(name="UK"), Entity(name="European Union")]),
        ... Statement(predicate="$country2 signed a treaty with $country3",
        ...         terms=[Entity(name="European Union"), Entity(name="Germany")]),
        ... Statement(predicate="$country3 signed a treaty with $country1",
        ...     terms=[Entity(name="Germany"), Entity(name="UK")], truth=False)])
        >>> nafta.contradicts(brexit)
        True
        """
        if other is None:
            return False
        return any(self.explanations_contradiction(other, context=context))

    def _explanations_implied_by(
        self,
        other: Comparable,
        explanation: Explanation,
    ) -> Iterator[Explanation]:
        """Generate explanations for how other may imply self."""
        reversed = explanation.reversed_context()
        if isinstance(other, Factor):
            other = FactorGroup(other)
        if isinstance(other, FactorGroup):
            yield from other._explanations_implication(self, explanation=reversed)

    def explanations_implied_by(
        self,
        other: Comparable,
        context: Optional[Union[ContextRegister, Explanation]] = None,
    ) -> Iterator[Explanation]:
        """Generate explanations for how other may imply self."""
        context = context = Explanation.from_context(
            context=context, current=self, incoming=other
        )
        yield from self._explanations_implied_by(other=other, explanation=context)

    def explanations_union(
        self,
        other: Union[Factor, FactorGroup],
        context: Optional[ContextRegister] = None,
    ) -> Iterator[ContextRegister]:
        """Yield contexts that allow ``self`` and ``other`` to be combined with the union operation."""
        to_match = FactorGroup(other) if isinstance(other, Comparable) else other
        context = context or ContextRegister()
        for partial in self._explanations_union_partial(to_match, context):
            for guess in self.possible_contexts(to_match, partial):
                answer = self._union_from_explanation(to_match, guess)
                if answer:
                    yield guess

    def _explanations_union_partial(
        self, other: FactorGroup, context: ContextRegister
    ) -> Iterator[ContextRegister]:
        for likely in self.likely_contexts(other, context):
            partial = self + other.new_context(likely.reversed())
            if partial is not None:
                try:
                    partial.internally_consistent()
                    yield likely
                except ValueError:
                    pass

    def _verbose_comparison(
        self,
        still_need_matches: Sequence[Factor | AbsenceOfFactor],
        explanation: Explanation,
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
        if not still_need_matches:
            yield explanation
        else:
            other_factor = still_need_matches.pop()
            for self_factor in self:
                for new_explanation in explanation.operate(self_factor, other_factor):
                    yield from iter(
                        self._verbose_comparison(
                            still_need_matches=deepcopy(still_need_matches),
                            explanation=new_explanation,
                        )
                    )

    def _explanations_implication(
        self,
        other: Comparable,
        explanation: Explanation,
    ) -> Iterator[Explanation]:
        """Find contexts that would cause ``self`` to imply ``other``."""

        explanation.operation = operator.ge

        if isinstance(other, FactorGroup):
            yield from self._verbose_comparison(
                still_need_matches=list(other.sequence),
                explanation=explanation,
            )
        elif isinstance(other, (self.term_class, self.absence_class)):
            yield from self._verbose_comparison(
                still_need_matches=[other],
                explanation=explanation,
            )

    def explanations_implication(
        self,
        other: Comparable,
        context: Optional[Union[ContextRegister, Explanation]] = None,
    ) -> Iterator[Explanation]:
        """Find contexts that would cause ``self`` to imply ``other``."""
        context = Explanation.from_context(
            context=context, current=self, incoming=other
        )
        yield from self._explanations_implication(other, context)

    def _contexts_has_all_factors_of(
        self,
        other: FactorGroup,
        context: Optional[ContextRegister] = None,
    ) -> Iterator[Explanation]:
        """Find contexts that would cause all of ``other``'s Factors to be in ``self``."""
        explanation = Explanation(
            reasons=[],
            context=context or ContextRegister(),
            operation=means,
        )
        yield from self._verbose_comparison(
            still_need_matches=list(other.sequence),
            explanation=explanation,
        )

    def generic_terms_by_str(self) -> Dict[str, Term]:
        """Index Terms that can be replaced without changing ``self``'s meaning."""
        generics: Dict[str, Term] = {}
        for factor in self:
            generics.update(factor.generic_terms_by_str())
        return generics

    def has_all_factors_of(
        self, other: FactorGroup, context: Optional[ContextRegister] = None
    ) -> bool:
        """Check if ``self`` has all Factors of ``other``."""
        return any(
            explanation is not None
            for explanation in self._contexts_has_all_factors_of(other, context=context)
        )

    def _contexts_shares_all_factors_with(
        self, other: FactorGroup, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        """Find context that would cause all of ``self``'s Factors to be in ``other``."""
        context = context or ContextRegister()
        context_for_other = context.reversed()

        blank = Explanation(
            reasons=[],
            context=context_for_other,
            operation=means,
        )
        yield from (
            explanation.context.reversed()
            for explanation in other._verbose_comparison(
                still_need_matches=list(self),
                explanation=blank,
            )
        )

    def shares_all_factors_with(
        self, other: FactorGroup, context: Optional[ContextRegister] = None
    ) -> bool:
        """Find whether all of ``self``'s Factors are in ``other``."""
        return any(
            register is not None
            for register in self._contexts_shares_all_factors_with(
                other, context=context
            )
        )

    def from_comparable(
        self, value: Union[Comparable, Sequence[Factor]]
    ) -> Optional[FactorGroup]:
        """Create a FactorGroup from a Factor or sequence of Factors."""
        if isinstance(value, FactorGroup):
            return value
        if isinstance(value, Factor):
            return FactorGroup([value])
        elif isinstance(value, Sequence):
            return FactorGroup(value)
        return None

    def explanations_same_meaning(
        self,
        other: Comparable,
        context: Optional[Union[ContextRegister, Explanation]] = None,
    ) -> Iterator[Explanation]:
        """Yield explanations for how ``self`` can have the same meaning as ``other``."""
        context = context = Explanation.from_context(
            context=context, current=self, incoming=other
        )
        context.operation = means
        to_match = self.from_comparable(other)
        if to_match is not None:
            for new_context in self._contexts_shares_all_factors_with(
                to_match, context.context
            ):
                yield from self._verbose_comparison(
                    still_need_matches=list(to_match.sequence),
                    explanation=context.with_context(new_context),
                )

    def _likely_contexts_for_factor(
        self, other: Comparable, context: ContextRegister, i: int = 0
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
        self,
        other: Comparable,
        context: Optional[ContextRegister] = None,
    ) -> Iterator[ContextRegister]:
        """Yield likely contexts based on similar Factor meanings."""
        context = context or ContextRegister()
        if isinstance(other, FactorGroup):
            yield from self._likely_contexts_for_factorgroup(other, context)
        elif isinstance(other, Factor):
            yield from self._likely_contexts_for_factor(other, context)

    def drop_implied_factors(self) -> FactorGroup:
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
        return self.__class__(result)

    def internally_consistent(self) -> None:
        """
        Check for contradictions among the Factors in self.

        :returns: bool indicating whether self is internally consistent
        """
        unchecked = list(self)
        while unchecked:
            current = unchecked.pop()
            for item in unchecked:
                if current.contradicts_same_context(item):
                    raise ValueError(
                        f"{item} can't be included in FactorGroup with contradictory Factor {current}."
                    )

    def new_context(self, changes: ContextRegister) -> FactorGroup:
        """Use ContextRegister to choose changes to ``self``'s context."""
        result = [factor.new_context(changes) for factor in self]
        return self.__class__(result)

    def __or__(self, other: Union[FactorGroup, Factor]) -> Optional[FactorGroup]:
        return self.union(other, context=None)

    def union(
        self,
        other: Union[FactorGroup, Factor],
        context: Optional[ContextRegister] = None,
    ) -> Optional[FactorGroup]:
        """Make new FactorGroup with the set of unique Factors from both ``self`` and ``other``."""
        context = context or ContextRegister()
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        return self._union(other=other, context=context)

    def _union(
        self, other: FactorGroup, context: ContextRegister
    ) -> Optional[FactorGroup]:
        explanations = self.explanations_union(other, context)
        try:
            explanation = next(explanations)
        except StopIteration:
            return None
        return self._union_from_explanation(other, explanation)

    def _union_from_explanation(
        self, other: FactorGroup, context: ContextRegister
    ) -> Optional[FactorGroup]:
        result = self._union_from_explanation_allow_contradiction(other, context)
        if result is None:
            return None
        try:
            result.internally_consistent()
        except ValueError:
            return None
        return result

    def _union_from_explanation_allow_contradiction(
        self, other: FactorGroup, context: ContextRegister
    ) -> Optional[FactorGroup]:
        updated_context = context.reversed() if context else None
        try:
            result = self + other.new_context(changes=updated_context)
        except DuplicateTermError:
            return None
        result = result.drop_implied_factors()
        return result
