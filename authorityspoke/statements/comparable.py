from __future__ import annotations

from abc import ABC
from copy import deepcopy
import functools
from itertools import permutations, zip_longest
import logging
import operator
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
        changes: Union[Sequence[Comparable], ContextRegister],
        terms_to_replace: Optional[Sequence[Comparable]] = None,
        source: Optional[Comparable] = None,
    ) -> Comparable:

        changes = convert_changes_to_register(
            factor=factor, changes=changes, terms_to_replace=terms_to_replace
        )

        expanded_changes = ContextRegister()
        for old, new in changes.items():

            if isinstance(new, str):
                factor_with_new_name = factor.get_factor(new)
                if source and factor_with_new_name is None:
                    factor_with_new_name = source.get_factor(new)
            else:
                factor_with_new_name = new
            if factor_with_new_name is None:
                raise ValueError(f'Unable to find replacement factor "{new}"')
            expanded_changes.insert_pair(old, factor_with_new_name)

        for old, new in expanded_changes.items():
            if str(factor) == old or factor.__dict__.get("name") == old:
                return new

        return func(factor, expanded_changes)

    return wrapper


def convert_changes_to_register(
    factor: Comparable,
    changes: Union[Comparable, ContextRegister, Sequence[Comparable]],
    terms_to_replace: Optional[Sequence[Comparable]] = None,
) -> ContextRegister:
    if isinstance(changes, ContextRegister):
        return changes
    if not isinstance(changes, Iterable):
        changes = [changes]
    if terms_to_replace:
        if not isinstance(changes, List):
            raise ValueError(
                "If 'terms_to_replace' is given, 'changes' must be a list of replacements, "
                f"not type {type(changes)}."
            )
        if len(terms_to_replace) != len(changes):
            raise ValueError(
                "Cannot create ContextRegister because 'terms_to_replace' is not the same length "
                f"as 'changes'.\nterms_to_replace: ({terms_to_replace})\nchanges: ({changes})"
            )
        return ContextRegister.from_lists(keys=terms_to_replace, values=changes)
    if isinstance(changes, dict):
        return ContextRegister.from_dict(changes)
    generic_factors = list(factor.generic_factors_by_str().values())
    if len(generic_factors) != len(changes):
        raise ValueError(
            f"Needed {len(generic_factors)} replacements for the "
            + f"items of generic_factors, but {len(changes)} were provided."
        )
    return ContextRegister.from_lists(generic_factors, changes)


class Comparable(ABC):
    """
    Objects that can be compared for implication, same meaning, contradiction, and consistency.

    :attr generic:
        Whether the object is referred to in a generic sense. If True, substituting
        this object for another generic object of the same class does not change the
        meaning of other Comparable objects that incorporate this one as a term.

    :attr name:
        An identifier for this object. May be used as a shorthand way of referring to
        this object when replacing another Comparable object's generic terms.
    """

    generic: bool = False
    absent: bool = False
    name: Optional[str] = None
    context_factor_names: ClassVar[Tuple[str, ...]] = ()

    @property
    def short_string(self) -> str:
        """Return string representation without line breaks."""
        return textwrap.shorten(str(self), width=5000, placeholder="...")

    @property
    def wrapped_string(self) -> str:
        return str(self)

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

    def __add__(self, other: Comparable) -> Optional[Comparable]:
        if not isinstance(other, Comparable):
            raise TypeError
        if self >= other:
            return self
        if other >= self:
            return other.new_context(self.generic_factors())
        return None

    def __ge__(self, other: Optional[Comparable]) -> bool:
        """
        Call :meth:`implies` as an alias.

        :returns:
            bool indicating whether ``self`` implies ``other``
        """
        return bool(self.implies(other))

    def __gt__(self, other: Optional[Comparable]) -> bool:
        """Test whether ``self`` implies ``other`` and ``self`` != ``other``."""
        return bool(self.implies(other) and self != other)

    def __or__(self, other: Comparable):
        return self.union(other)

    def __str__(self):
        text = f"the {self.__class__.__name__}" + " {}"
        if self.generic:
            text = f"<{text}>"
        if self.absent:
            text = "absence of " + text
        return text

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

    def compare_terms(self, other: Comparable, relation: Callable) -> bool:
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
        self, other: Comparable, relation: Callable, ordering: FactorSequence
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

    def _contradicts_if_present(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        """
        Test if ``self`` would contradict ``other`` if neither was ``absent``.

        The default is to yield nothing where no class-specific method is available.
        """
        yield from iter([])

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
        context = context or ContextRegister()
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
                # No contradiction between absences of any two Comparables
                if not other.__dict__.get("absent"):
                    test = other._implies_if_present(self, context.reversed())
                    yield from (register.reversed() for register in test)
        elif isinstance(other, Sequence):
            yield from other.explanations_contradiction(
                self, context=context.reversed()
            )

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
        """Generate ways to match contexts of self and other so they mean the same."""
        if (
            self.__class__ == other.__class__
            and self.generic == other.generic
            and self.absent == other.absent
        ):
            if self.generic:
                yield self.generic_register(other)
            context = context or ContextRegister()
            yield from self._means_if_concrete(other, context)

    def explanations_union(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        context = context or ContextRegister()
        for partial in self._explanations_union_partial(other, context):
            for guess in self.possible_contexts(other, partial):
                answer = self.union_from_explanation(other, guess)
                if answer:
                    yield guess

    def _explanations_union_partial(
        self, other: Comparable, context: ContextRegister
    ) -> Iterator[ContextRegister]:
        for likely in self.likely_contexts(other, context):
            partial = self + other.new_context(likely.reversed())
            if partial.internally_consistent():
                yield likely

    def generic_register(self, other: Comparable) -> ContextRegister:
        register = ContextRegister()
        register.insert_pair(self, other)
        return register

    def _implies_if_present(
        self, other: Comparable, context: ContextRegister
    ) -> Iterator[ContextRegister]:
        """
        Find if ``self`` would imply ``other`` if they aren't absent.

        :returns:
            bool indicating whether ``self`` would imply ``other``,
            under the assumption that neither self nor other has
            the attribute ``absent == True``.
        """
        if isinstance(other, self.__class__):
            if other.generic:
                if context.get_factor(self) is None or (
                    context.get_factor(self) == other
                ):
                    yield self.generic_register(other)
            if not self.generic:
                yield from self._implies_if_concrete(other, context)

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

    def get_factor(self, query: str) -> Optional[Comparable]:
        """
        Search for Comparable with str or name matching query

        :param query:
            a string that matches the desired Comparable's ``name`` or the
            output of its __str__ method.
        """
        result = self.get_factor_by_str(query)
        if result is None:
            result = self.get_factor_by_name(query)
        return result

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

    def _implies_if_concrete(
        self, other: Comparable, context: Optional[ContextRegister] = None
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

    def implies_same_context(self, other) -> bool:
        same_context = ContextRegister()
        for key in self.generic_factors():
            same_context.insert_pair(key, key)
        return self.implies(other, context=same_context)

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

    def make_generic(self) -> Comparable:
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

    def _means_if_concrete(
        self, other: Comparable, context: Optional[ContextRegister]
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
        _ = next(gen)  # unchanged permutation
        already_returned: List[ContextRegister] = [matches]

        for term_permutation in gen:
            changes = ContextRegister.from_lists(self.terms, term_permutation)
            changed_registry = matches.replace_keys(changes)
            if not any(
                changed_registry == returned_dict for returned_dict in already_returned
            ):
                already_returned.append(changed_registry)
                yield changed_registry

    def term_permutations(self) -> Iterator[FactorSequence]:
        """Generate permutations of context factors that preserve same meaning."""
        yield self.terms

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

    def _update_context_from_factors(
        self, other: Comparable, context: ContextRegister
    ) -> Optional[ContextRegister]:
        incoming = ContextRegister.from_lists(
            keys=self.generic_factors(), values=other.generic_factors()
        )
        updated_context = context.merged_with(incoming)
        return updated_context

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

    @staticmethod
    def wrap_with_tuple(item):
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

    def __getitem__(self, item: str) -> Comparable:
        return self.matches[item]

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
        cls,
        keys: Union[FactorSequence, Sequence[Comparable]],
        values: Union[FactorSequence, Sequence[Comparable]],
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
        """
        Construct new :class:`ContextRegister` by replacing keys.

        Used when making permutations of the key orders because some are interchangeable.

        e.g. in "Amy and Bob were married" the order of "Amy" and "Bob" is interchangeable.
        """

        result = ContextRegister()
        for key, value in self.matches.items():
            replacement = replacements[key]
            result.insert_pair(key=replacement, value=value)

        return result

    def reversed(self):
        """Swap keys for values and vice versa."""
        return ContextRegister.from_lists(
            keys=self.reverse_matches.keys(), values=self.reverse_matches.values()
        )

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
                key_as_factor = incoming_mapping.get_reverse_factor(in_value)
                self_mapping.insert_pair(key_as_factor, in_value)
                if list(self_mapping.values()).count(in_value) > 1:
                    logger.debug("%s assigned to two different keys", in_value)
                    return None
        return self_mapping


class FactorSequence(Tuple[Comparable, ...]):
    def __new__(cls, value: Sequence = ()):
        if isinstance(value, Comparable):
            value = (value,)
        return tuple.__new__(FactorSequence, value)

    def ordered_comparison(
        self,
        other: FactorSequence,
        operation: Callable,
        context: Optional[ContextRegister] = None,
    ) -> Iterator[ContextRegister]:
        r"""
        Find ways for a series of pairs of :class:`.Comparable` terms to satisfy a comparison.

        :param context:
            keys representing terms in ``self`` and
            values representing terms in ``other``. The
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

        context = context or ContextRegister()
        ordered_pairs = list(zip_longest(self, other))
        yield from update_register(register=context, factor_pairs=ordered_pairs)
