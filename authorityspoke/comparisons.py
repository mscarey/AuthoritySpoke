from __future__ import annotations

from abc import ABC
from copy import deepcopy
import functools
from itertools import permutations, zip_longest
import logging
import textwrap
from typing import Any, Callable, ClassVar, Dict, Iterable, Iterator
from typing import List, Optional, Sequence, Tuple, Union

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


def new_context_helper(func: Callable):
    r"""
    Search :class:`.Factor` for generic :class:`.Factor`\s to use in new context.

    Decorators for memoizing generic :class:`.Factor`\s.
    Used when changing an abstract :class:`.Rule` from
    one concrete context to another.

    If a :class:`list` has been passed in rather than a :class:`dict`, uses
    the input as a series of :class:`Factor`\s to replace the
    :attr:`~Factor.generic_factors` from the calling object.

    Also, if ``changes`` contains a replacement for the calling
    object, the decorator returns the replacement and never calls
    the decorated function.

    :param factor:
        a :class:`.Factor` that is having its generic :class:`.Factor`\s
        replaced to change context (for instance, to change to the context
        of a different case involving parties represented by different
        :class:`.Entity` objects).

    :param changes:
        indicates which generic :class:`.Factor`\s within ``factor`` should
        be replaced and what they should be replaced with.

    :returns:
        a new :class:`.Factor` object in the new context.
    """

    @functools.wraps(func)
    def wrapper(
        factor: Comparable,
        changes: Optional[Union[Sequence[Comparable], ContextRegister]],
        terms_to_replace: Optional[Sequence[Comparable]] = None,
        source: Optional[Comparable] = None,
    ) -> Comparable:

        if changes is None:
            return factor
        changes = convert_changes_to_register(
            factor=factor, changes=changes, terms_to_replace=terms_to_replace
        )

        expanded_changes = ContextRegister()
        for old, new in changes.items():
            factor_with_new_name = seek_factor(new, factor, source)
            expanded_changes.insert_pair(old, factor_with_new_name)
        for old, new in expanded_changes.items():
            if str(factor) == old or factor.__dict__.get("name") == old:
                return new

        return func(factor, expanded_changes)

    return wrapper


def seek_factor_by_name(
    name: Union[Factor, str], source_factor: Factor, source_opinion: Comparable
) -> Factor:
    r"""
    Find a Factor matching a name in a Factor or Opinion.

    :param name:
        the name of a Factor to seek and return. Usually the name will correspond to an
        :class:`.Entity` because Entities have shorter names.

    :param source_factor:
        A Factor that might have a context factor matching the "name". Usually the source_factor
        is the Factor that will be assigned a new context, which would include replacing the
        context factor that matches "name"

    :param source_opinion:
        An :class:`.Opinion` to search for a context factor matching "name" if the search of the
        source_factor fails.

    :returns:
        a found Factor matching "name"
    """
    if not isinstance(name, str):
        return name
    result = source_factor.get_factor_by_name(name)
    if source_opinion and not result:
        result = source_opinion.get_factor_by_name(name)
    if not result:
        raise ValueError(f"Unable to find a Factor with the name '{name}'")
    return result


def seek_factor_by_str(
    query: Union[Factor, str], source_factor: Factor, source_opinion: Opinion
) -> Factor:
    r"""
    Find a Factor matching a name in a Factor or Opinion.

    :param query:
        the string representation of a Factor to seek and return.

    :param source_factor:
        A Factor that might have a context factor matching the "name". Usually the source_factor
        is the Factor that will be assigned a new context, which would include replacing the
        context factor that matches "name"

    :param source_opinion:
        An :class:`.Opinion` to search for a context factor matching "name" if the search of the
        source_factor fails.

    :returns:
        a found Factor matching "name"
    """
    if not isinstance(query, str):
        return query
    result = source_factor.get_factor_by_str(query)
    if source_opinion and not result:
        result = source_opinion.get_factor_by_str(query)
    if not result:
        raise ValueError(f"Unable to find a Factor with the string '{query}'")
    return result


def seek_factor(
    query: Union[Comparable, str], source_factor: Comparable, source_opinion: Comparable
) -> Comparable:
    try:
        answer = seek_factor_by_str(
            query=query, source_factor=source_factor, source_opinion=source_opinion
        )
    except ValueError:
        answer = seek_factor_by_name(
            name=query, source_factor=source_factor, source_opinion=source_opinion
        )
    return answer


def convert_changes_to_register(
    factor: Comparable,
    changes: Union[Comparable, Dict[str, Comparable], List[Comparable]],
    terms_to_replace: Optional[List[Comparable]] = None,
) -> ContextRegister:
    if isinstance(changes, ContextRegister):
        return changes
    if not isinstance(changes, Iterable):
        changes = [changes]
    if terms_to_replace:
        if not isinstance(changes, List):
            raise TypeError(
                "If 'terms_to_replace' is given, 'changes' must be a list of replacements, "
                f"not type {type(changes)}."
            )
        if len(terms_to_replace) != len(changes):
            raise ValueError(
                "Cannot create ContextRegister because 'terms_to_replace' is not the same length "
                f"as 'changes'.\nterms_to_replace: ({terms_to_replace})\nchanges: ({changes})"
            )
        return ContextRegister.from_lists(keys=terms_to_replace, values=changes)
    if isinstance(changes, (list, tuple)):
        generic_factors = list(factor.generic_factors_by_str().values())
        if len(generic_factors) != len(changes):
            raise ValueError(
                f"Needed {len(generic_factors)} replacements for the "
                + f"items of generic_factors, but {len(changes)} were provided."
            )
        return ContextRegister.from_lists(generic_factors, changes)
    return ContextRegister.from_dict(changes)


class Comparable(ABC):
    generic: bool = False
    context_factor_names: ClassVar[Tuple] = ()

    @property
    def short_string(self) -> str:
        """Return string representation without line breaks."""
        return textwrap.shorten(str(self), width=5000, placeholder="...")

    @property
    def wrapped_string(self) -> str:
        return str(self)

    def consistent_with(
        self, other: Optional[Comparable], context: Optional[ContextRegister] = None
    ) -> bool:
        """
        Check if self and other can be non-contradictory.

        :returns:
            a bool indicating whether there's at least one way to
            match the :attr:`terms` of ``self`` and ``other``,
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
        Search for ways to match :attr:`terms` of ``self`` and ``other``.

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
            yield from self.terms.ordered_comparison(
                other=other.terms, operation=comparison, context=context
            )

    def all_generic_factors_match(
        self, other: Comparable, context: ContextRegister
    ) -> bool:
        if all(
            all(
                context.get_factor(key) == context_register.get_factor(key)
                or context.get_factor(context_register.get(str(key))) == key
                for key in self.generic_factors()
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
    def terms(self) -> FactorSequence:
        r"""
        Get :class:`Factor`\s used in comparisons with other :class:`Factor`\s.

        :returns:
            a tuple of attributes that are designated as the ``terms``
            for whichever subclass of :class:`Factor` calls this method. These
            can be used for comparing objects using :meth:`consistent_with`
        """
        context: List[Optional[Comparable]] = []
        for factor_name in self.context_factor_names:
            next_factor: Optional[Comparable] = self.__dict__.get(factor_name)
            context.append(next_factor)
        return FactorSequence(context)

    def generic_factors(self) -> List[Comparable]:
        return list(self.generic_factors_by_str().values())

    def generic_factors_by_str(self) -> Dict[str, Comparable]:
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
        for factor in self.terms:
            if factor is not None:
                for generic in factor.generic_factors():
                    generics[str(generic)] = generic
        return generics

    def get_factor_by_name(self, name: str) -> Optional[Comparable]:
        """
        Search of ``self`` and ``self``'s attributes for :class:`Factor` with specified ``name``.

        :returns:
            a :class:`Comparable` with the specified ``name`` attribute
            if it exists, otherwise ``None``.
        """
        factors_to_search = self.recursive_factors
        for value in factors_to_search.values():
            if hasattr(value, "name") and value.name == name:
                return value
        return None

    def get_factor_by_str(self, query: str) -> Optional[Comparable]:
        """
        Search of ``self`` and ``self``'s attributes for :class:`Factor` with specified string.

        :returns:
            a :class:`Factor` with the specified string
            if it exists, otherwise ``None``.
        """
        for name, factor in self.recursive_factors.items():
            if name == query:
                return factor
        return None

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

    def __gt__(self, other: Optional[Comparable]) -> bool:
        """Test whether ``self`` implies ``other`` and ``self`` != ``other``."""
        return bool(self.implies(other) and self != other)

    def implies_same_context(self, other) -> bool:
        same_context = ContextRegister()
        for key in self.generic_factors():
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
        for key in self.generic_factors():
            same_context.insert_pair(key, key)
        return self.means(other, context=same_context)

    @new_context_helper
    def new_context(self, changes: ContextRegister) -> Comparable:
        r"""
        Create new :class:`Comparable`, replacing keys of ``changes`` with values.

        :param changes:
            has :class:`.Comparable`\s to replace as keys, and has
            their replacements as the corresponding values.

        :returns:
            a new :class:`.Comparable` object with the replacements made.
        """
        for key, value in changes.matches.items():

            if not isinstance(key, str):
                raise TypeError(
                    'Each key in "changes" must be the name of a Comparable'
                )
            if value and not isinstance(value, Comparable):
                raise TypeError('Each value in "changes" must be a Comparable')

        new_dict = self.own_attributes()
        for name in self.context_factor_names:
            new_dict[name] = self.__dict__[name].new_context(changes)
        return self.__class__(**new_dict)

    def own_attributes(self) -> Dict[str, Any]:
        """
        Return attributes of ``self`` that aren't inherited from another class.

        Used for getting parameters to pass to :meth:`~Factor.__init__`
        when generating a new object.
        """
        return self.__dict__.copy()

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
            for factor in self.generic_factors()
            if str(factor) not in context.matches.keys()
        ]
        unused_other = [
            factor
            for factor in other.generic_factors()
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

    @property
    def recursive_factors(self) -> Dict[str, Comparable]:
        r"""
        Collect `self`'s :attr:`terms`, and their :attr:`terms`, recursively.

        :returns:
            a :class:`dict` (instead of a :class:`set`,
            to preserve order) of :class:`Factor`\s.
        """
        answers: Dict[str, Comparable] = {str(self): self}
        for context in self.terms:
            if isinstance(context, Iterable):
                for item in context:
                    answers.update(item.recursive_factors)
            elif context is not None:
                answers.update(context.recursive_factors)
        return answers

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

    def term_permutations(self) -> Iterator[FactorSequence]:
        """Generate permutations of context factors that preserve same meaning."""
        yield self.terms

    def _registers_for_interchangeable_context(
        self, matches: ContextRegister
    ) -> Iterator[ContextRegister]:
        r"""
        Find possible combination of interchangeable :attr:`terms`.

        :yields:
            context registers with every possible combination of
            ``self``\'s and ``other``\'s interchangeable
            :attr:`terms`.
        """
        yield matches
        gen = self.term_permutations()
        unchanged_permutation = next(gen)
        already_returned: List[ContextRegister] = [matches]

        for term_permutation in gen:
            changes = ContextRegister.from_lists(self.terms, term_permutation)
            changed_registry = matches.replace_keys(changes)
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

    def __ge__(self, other: Optional[Comparable]) -> bool:
        """
        Call :meth:`implies` as an alias.

        :returns:
            bool indicating whether ``self`` implies ``other``
        """
        return bool(self.implies(other))

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
        """
        Test whether ``self`` :meth:`implies` the absence of ``other``.

        This should only be called after confirming that ``other``
        is not ``None``.

        :returns:
            ``True`` if self and other can't both be true at
            the same time. Otherwise returns ``False``.
        """
        if context is None:
            context = ContextRegister()
        if not isinstance(other, Comparable):
            raise TypeError(
                f"{self.__class__} objects may only be compared for "
                + "contradiction with other Factor objects or None."
            )
        if isinstance(other, self.__class__):
            if not self.__dict__.get("absent"):
                if not other.__dict__.get("absent"):
                    yield from self._contradicts_if_present(other, context)
                else:
                    yield from self._implies_if_present(other, context)
            elif self.__dict__.get("absent"):
                if not other.__dict__.get("absent"):
                    test = other._implies_if_present(self, context.reversed())
                else:
                    test = other._contradicts_if_present(self, context.reversed())
                yield from (register.reversed() for register in test)

    def explanations_implication(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        r"""
        Generate :class:`.ContextRegister`\s that cause `self` to imply `other`.

        If self is `absent`, then generate a ContextRegister from other's point
        of view and then swap the keys and values.
        """
        if context is None:
            context = ContextRegister()
        if not isinstance(other, Comparable):
            raise TypeError(
                f"{self.__class__} objects may only be compared for "
                + "implication with other Comparable objects or None."
            )
        if isinstance(other, self.__class__):
            if not self.__dict__.get("absent"):
                if not other.__dict__.get("absent"):
                    yield from self._implies_if_present(other, context)
                else:
                    yield from self._contradicts_if_present(other, context)

            else:
                if other.__dict__.get("absent"):
                    test = other._implies_if_present(self, context.reversed())
                else:
                    test = other._contradicts_if_present(self, context.reversed())
                yield from (register.reversed() for register in test)

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

    def _likely_context_from_meaning(
        self, other: Comparable, context: ContextRegister
    ) -> Optional[ContextRegister]:
        new_context = None
        if self.means(other, context=context) or other.means(
            self, context=context.reversed()
        ):
            new_context = self._update_context_from_factors(other, context)
        if new_context and new_context != context:
            return new_context
        return None

    def _likely_context_from_implication(
        self, other: Comparable, context: ContextRegister
    ) -> Optional[ContextRegister]:
        new_context = None
        if self.implies(other, context=context) or other.implies(
            self, context=context.reversed()
        ):
            new_context = self._update_context_from_factors(other, context)
        if new_context and new_context != context:
            return new_context
        return None

    def likely_contexts(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        context = context or ContextRegister()
        same_meaning = self._likely_context_from_meaning(other, context)
        if same_meaning:
            implied = self._likely_context_from_implication(other, same_meaning)
        else:
            implied = self._likely_context_from_implication(other, context)
        if implied:
            yield implied
        if same_meaning:
            yield same_meaning
        yield context

    def _update_context_from_factors(
        self, other: Comparable, context: ContextRegister
    ) -> Optional[ContextRegister]:
        incoming = ContextRegister.from_lists(
            keys=self.generic_factors(), values=other.generic_factors()
        )
        updated_context = context.merged_with(incoming)
        return updated_context

    @staticmethod
    def _wrap_with_tuple(item):
        if item is None:
            return ()
        if isinstance(item, Iterable):
            return tuple(item)
        return (item,)


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
        item_names = [f"{str(k)} is like {str(v)}" for k, v in self.matches.items()]
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
        cls, keys: List[Comparable], values: List[Comparable]
    ) -> ContextRegister:
        pairs = zip_longest(keys, values)
        new = cls()
        for pair in pairs:
            new.insert_pair(pair[0], pair[1])
        return new

    @classmethod
    def from_dict(cls, data: Dict) -> ContextRegister:
        result = ContextRegister()
        for k, v in data.items():
            result.insert_pair(key=k, value=v)
        return result

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


class FactorSequence(Tuple[Optional[Comparable], ...]):
    def __new__(cls, value: Sequence = ()):
        if isinstance(value, Comparable) or value.__class__.__name__ == "FactorGroup":
            value = (value,)
        if value is None:
            value = (None,)
        return tuple.__new__(FactorSequence, value)

    def ordered_comparison(
        self,
        other: FactorSequence,
        operation: Callable,
        context: Optional[ContextRegister] = None,
    ) -> Iterator[ContextRegister]:
        r"""
        Find ways for a series of pairs of :class:`.Factor`\s to satisfy a comparison.

        :param context:
            keys representing :class:`.Factor`\s in ``self`` and
            values representing :class:`.Factor`\s in ``other``. The
            keys and values have been found in corresponding positions
            in ``self`` and ``other``.

        :yields:
            every way that ``matches`` can be updated to be consistent
            with each element of ``self.need_matches`` having the relationship
            ``self.comparison`` with the item at the corresponding index of
            ``self.available``.
        """

        def update_register(
            register: ContextRegister,
            factor_pairs: List[Tuple[Optional[Comparable], Optional[Comparable]]],
            i: int = 0,
        ):
            """
            Recursively search through :class:`Factor` pairs trying out context assignments.

            This has the potential to take a long time to fail if the problem is
            unsatisfiable. It will reduce risk to check that every :class:`Factor` pair
            is satisfiable before checking that they're all satisfiable together.
            """
            if i == len(factor_pairs):
                yield register
            else:
                left, right = factor_pairs[i]
                if left is not None or right is None:
                    if left is None:
                        yield from update_register(
                            register, factor_pairs=factor_pairs, i=i + 1
                        )
                    else:
                        new_mapping_choices: List[ContextRegister] = []
                        for incoming_register in left.update_context_register(
                            right, register, operation
                        ):
                            if incoming_register not in new_mapping_choices:
                                new_mapping_choices.append(incoming_register)
                                yield from update_register(
                                    incoming_register,
                                    factor_pairs=factor_pairs,
                                    i=i + 1,
                                )

        if context is None:
            context = ContextRegister()
        ordered_pairs = list(zip_longest(self, other))
        yield from update_register(register=context, factor_pairs=ordered_pairs)
