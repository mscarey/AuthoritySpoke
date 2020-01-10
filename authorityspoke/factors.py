r""":class:`Factor`\s, or inputs and outputs of legal :class:`.Rule`\s."""

from __future__ import annotations

from dataclasses import dataclass
import functools
from itertools import zip_longest
import operator
import textwrap
from typing import Any, Callable, Dict, Iterable, Iterator, List
from typing import Optional, Sequence, Set, Tuple, TypeVar, Union

from anchorpoint.textselectors import TextQuoteSelector

from authorityspoke.comparisons import ContextRegister, Comparable
from authorityspoke.comparisons import use_likely_context
from authorityspoke.enactments import Enactment


def seek_factor_by_name(
    name: Union[Factor, str], source_factor: Factor, source_opinion: Opinion
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

    :param context_opinion:
        a second object with generic factors that need to be searched
        when trying to resolve what a string in the `changes` parameter
        refers to.

    :returns:
        a new :class:`.Factor` object in the new context.
    """

    @functools.wraps(func)
    def wrapper(
        factor: Factor,
        changes: Optional[Union[Sequence[Factor], ContextRegister]],
        context_opinion: Optional[Opinion] = None,
    ) -> Factor:

        if changes is None:
            return factor
        if not isinstance(changes, Iterable):
            changes = (changes,)
        if not isinstance(changes, dict):
            generic_factors = factor.generic_factors
            if len(generic_factors) < len(changes):
                raise ValueError(
                    f"The iterable {changes} is too long to be interpreted "
                    + f"as a list of replacements for the "
                    + f"{len(generic_factors)} items of generic_factors."
                )
            changes = ContextRegister(dict(zip(generic_factors, changes)))

        expanded_changes = ContextRegister(
            {
                seek_factor_by_name(old, factor, context_opinion): seek_factor_by_name(
                    new, factor, context_opinion
                )
                for old, new in changes.items()
            }
        )
        for old, new in expanded_changes.items():
            if factor.means(old) and factor.name == old.name:
                return new

        return func(factor, expanded_changes)

    return wrapper


@dataclass(frozen=True, init=False)
class Factor(Comparable):
    """
    Things relevant to a :class:`.Court`\'s application of a :class:`.Rule`.

    The same :class:`Factor` that is in the ``outputs`` for the
    :class:`.Procedure` of one legal :class:`.Rule` might be in the
    ``inputs`` of the :class:`.Procedure` for another.
    """

    def __init__(
        self, *, name: Optional[str] = None, generic: bool = False, absent: bool = False
    ):
        """Designate attributes inherited from Factor as keyword-only."""
        self.name = name
        self.generic = generic
        self.absent = absent

    @property
    def context_factor_names(self) -> Tuple[str, ...]:
        """
        Get names of attributes to compare in :meth:`~Factor.means` or :meth:`~Factor.__ge__`.

        This method and :meth:`interchangeable_factors` should be the only parts
        of the context-matching process that need to be unique for each
        subclass of :class:`Factor`.

        :returns:
            attribute names identifying which attributes of ``self`` and
            ``other`` must match, for a :class:`.Analogy` to hold between
            this :class:`Factor` and another.
        """

        return ()

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

    @property
    def generic_factors(self) -> List[Factor]:
        r"""
        :class:`.Factor`\s that can be replaced without changing ``self``\s meaning.

        :returns:
            a :class:`list` made from a :class:`dict` with ``self``\'s
            generic :class:`.Factor`\s as keys and ``None`` as values,
            so that the keys can be matched to another object's
            ``generic_factors`` to perform an equality test.
        """

        if self.generic:
            return [self]
        generics: Dict[Factor, None] = {}
        for factor in self.context_factors:
            if factor is not None:
                for generic in factor.generic_factors:
                    generics[generic] = None
        return list(generics)

    @property
    def context_factors(self) -> FactorSequence:
        r"""
        Get :class:`Factor`\s used in comparisons with other :class:`Factor`\s.

        :returns:
            a tuple of attributes that are designated as the ``context_factors``
            for whichever subclass of :class:`Factor` calls this method. These
            can be used for comparing objects using :meth:`consistent_with`
        """
        context: List[Optional[Factor]] = []
        for factor_name in self.context_factor_names:
            next_factor: Optional[Factor] = self.__dict__.get(factor_name)
            context.append(next_factor)
        return FactorSequence(context)

    @property
    def recursive_factors(self) -> Dict[Factor, None]:
        r"""
        Collect `self`'s :attr:`context_factors`, and their :attr:`context_factors`, recursively.

        :returns:
            a :class:`dict` (instead of a :class:`set`,
            to preserve order) of :class:`Factor`\s.
        """
        answers: Dict[Factor, None] = {self: None}
        for context in self.context_factors:
            if isinstance(context, Iterable):
                for item in context:
                    answers.update(item.recursive_factors)
            elif context is not None:
                answers.update(context.recursive_factors)
        return answers

    def __add__(self, other) -> Optional[Factor]:
        if other.__class__.__name__ in ("Procedure", "Rule"):
            return other + self
        if not isinstance(other, Factor):
            raise TypeError
        if self >= other:
            return self
        if other >= self:
            return other.new_context(self.generic_factors)
        return None

    def _contradicts_if_present(
        self, other: Factor, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        """
        Test if ``self`` would contradict ``other`` if neither was ``absent``.

        The default is to yield nothing where no class-specific method is available.
        """
        yield from iter([])

    def _context_registers(
        self,
        other: Optional[Factor],
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
            if context.get(self) is None or (context.get(self) == other):
                yield ContextRegister({self: other})
        else:
            yield from self.context_factors.ordered_comparison(
                other=other.context_factors, operation=comparison, context=context
            )

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
        if not isinstance(other, Factor):
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

    def _evolve_attribute(
        self, changes: Dict[str, Any], attr_name: str
    ) -> Dict[str, Any]:
        attr_dict = {}
        new_changes = {}
        for key in changes:
            if key in self.__dict__[attr_name].own_attributes():
                attr_dict[key] = changes[key]
            else:
                new_changes[key] = changes[key]
        if attr_dict:
            new_changes[attr_name] = self.__dict__[attr_name].evolve(attr_dict)
        return new_changes

    def _evolve_from_dict(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        for key in changes:
            if key not in self.__dict__:
                raise ValueError(
                    f"Invalid: '{key}' is not among the {self.__class__}'s attributes "
                    f"{list(self.__dict__.keys())}."
                )
        new_dict = self.own_attributes()
        for key in changes:
            new_dict[key] = changes[key]
        return new_dict

    def _make_dict_to_evolve(
        self, changes: Union[str, Sequence[str], Dict[str, Any]]
    ) -> Dict[str, Any]:
        if isinstance(changes, str):
            changes = (changes,)
        if not isinstance(changes, dict):
            changes = {key: not self.__dict__[key] for key in changes}
        return changes

    def evolve(self, changes: Union[str, Sequence[str], Dict[str, Any]]) -> Factor:
        """
        Make new object with attributes from ``self.__dict__``, replacing attributes as specified.

        :param changes:
            a :class:`dict` where the keys are names of attributes
            of self, and the values are new values for those attributes, or
            else an attribute name or :class:`list` of names that need to
            have their values replaced with their boolean opposite.

        :returns:
            a new object initialized with attributes from
            ``self.__dict__``, except that any attributes named as keys in the
            changes parameter are replaced by the corresponding value.
        """
        changes = self._make_dict_to_evolve(changes)
        new_values = self._evolve_from_dict(changes)
        return self.__class__(**new_values)

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
                yield ContextRegister({self: other})
            yield from self._means_if_concrete(other, context)

    def _means_if_concrete(
        self, other: Factor, context: Optional[ContextRegister]
    ) -> Iterator[ContextRegister]:
        """
        Test equality based on :attr:`context_factors`.

        Usually called after a subclasses has injected its own tests
        based on other attributes.

        :returns:
            bool indicating whether ``self`` would equal ``other``,
            under the assumptions that neither ``self`` nor ``other``
            has ``absent=True``, neither has ``generic=True``, and
            ``other`` is an instance of ``self``'s class.
        """
        if self.compare_context_factors(other, means):
            yield from self._context_registers(other, comparison=means, context=context)

    def get_factor_by_name(self, name: str) -> Optional[Factor]:
        """
        Search of ``self`` and ``self``'s attributes for :class:`Factor` with specified ``name``.

        :returns:
            a :class:`Factor` with the specified ``name`` attribute
            if it exists, otherwise ``None``.
        """
        for factor in self.recursive_factors:
            if hasattr(factor, "name") and factor.name == name:
                return factor
        return None

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
        if not isinstance(other, Factor):
            raise TypeError(
                f"{self.__class__} objects may only be compared for "
                + "implication with other Factor objects or None."
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

    def __gt__(self, other: Optional[Factor]) -> bool:
        """Test whether ``self`` implies ``other`` and ``self`` != ``other``."""
        return bool(self.implies(other) and self != other)

    def __ge__(self, other: Optional[Factor]) -> bool:
        """
        Call :meth:`implies` as an alias.

        :returns:
            bool indicating whether ``self`` implies ``other``
        """
        return bool(self.implies(other))

    def compare_context_factors(self, other: Factor, relation: Callable) -> bool:
        r"""
        Test if relation holds for corresponding context factors of self and other.

        This doesn't track a persistent :class:`ContextRegister` as it goes
        down the sequence of :class:`Factor` pairs. Perhaps(?) this simpler
        process can weed out :class:`Factor`\s that clearly don't satisfy
        a comparison before moving on to the more costly :class:`Analogy`
        process. Or maybe it's useful for testing.
        """
        valid = True
        for i, self_factor in enumerate(self.context_factors):
            if not (self_factor is other.context_factors[i] is None):
                if not (
                    self_factor and relation(self_factor, other.context_factors[i])
                ):
                    valid = False
        return valid

    def _implies_if_concrete(
        self, other: Factor, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        """
        Find if ``self`` would imply ``other`` if they aren't absent or generic.

        Used to test implication based on :attr:`context_factors`,
        usually after a subclass has injected its own tests
        based on other attributes.

        :returns:
            context assignments where ``self`` would imply ``other``,
            under the assumptions that neither ``self`` nor ``other``
            has ``absent=True``, neither has ``generic=True``, and
            ``other`` is an instance of ``self``'s class.
        """
        if self.compare_context_factors(other, operator.ge):
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
                if context.get(self) is None or (context.get(self) == other):
                    yield ContextRegister({self: other})
            if not self.generic:
                yield from self._implies_if_concrete(other, context)

    def _update_context_from_factors(
        self, other: Comparable, context: ContextRegister
    ) -> Optional[ContextRegister]:
        incoming = ContextRegister(
            dict(zip(self.generic_factors, other.generic_factors))
        )
        updated_context = context.merged_with(incoming)
        return updated_context

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
        return self.evolve({"generic": True})

    @new_context_helper
    def new_context(self, changes: ContextRegister) -> Factor:
        r"""
        Create new :class:`Factor`, replacing keys of ``changes`` with values.

        :param changes:
            has :class:`.Factor`\s to replace as keys, and has
            their replacements as the corresponding values.

        :returns:
            a new :class:`.Factor` object with the replacements made.
        """
        if any(not isinstance(item, (str, Factor)) for item in changes):
            raise TypeError(
                'Each item in "changes" must be a Factor or the name of a Factor'
            )
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

    def __str__(self):
        text = f"the {self.__class__.__name__}" + " {}"
        if self.generic:
            text = f"<{text}>"
        if self.absent:
            text = "absence of " + text

        return text

    @property
    def short_string(self) -> str:
        """Return string representation without line breaks."""
        return textwrap.shorten(str(self), width=5000, placeholder="...")

    def update_context_register(
        self, other: Optional[Factor], register: ContextRegister, comparison: Callable
    ) -> Iterator[ContextRegister]:
        r"""
        Find ways to update ``self_mapping`` to allow relationship ``comparison``.

        :param other:
            another :class:`Factor` being compared to ``self``

        :param register:
            keys representing :class:`Factor`\s from ``self``'s context and
            values representing :class:`Factor`\s in ``other``'s context.

        :param comparison:
            a function defining the comparison that must be ``True``
            between ``self`` and ``other``. Could be :meth:`Factor.means` or
            :meth:`Factor.__ge__`.

        :yields:
            every way that ``self_mapping`` can be updated to be consistent
            with ``self`` and ``other`` having the relationship
            ``comparison``.
        """
        if other and not isinstance(other, Factor):
            raise TypeError
        if not isinstance(register, ContextRegister):
            register = ContextRegister(register)
        for incoming_register in self._context_registers(other, comparison):
            for new_register_variation in self._registers_for_interchangeable_context(
                incoming_register
            ):
                register_or_none = register.merged_with(new_register_variation)
                if register_or_none is not None:
                    yield register_or_none

    @staticmethod
    def _wrap_with_tuple(item):
        if item is None:
            return ()
        if isinstance(item, Iterable):
            return tuple(item)
        return (item,)


TextLinkDict = Dict[Union[Factor, Enactment], List[TextQuoteSelector]]


def consistent_with(left: Factor, right: Factor) -> bool:
    """
    Call :meth:`.Factor.consistent_with` as function alias.

    This exists because :func:`Factor._context_registers` needs
    a function rather than a method for the `comparison` variable.

    :returns:
        whether ``other`` is consistent with ``self``.
    """
    return left.consistent_with(right)


def means(left: Factor, right: Factor) -> bool:
    """
    Call :meth:`.Factor.means` as function alias.

    This only exists because :class:`.Analogy` objects expect
    a function rather than a method for :attr:`~.Analogy.comparison`.

    :returns:
        whether ``other`` is another :class:`Factor` with the same
        meaning as ``self``.
    """
    return left.means(right)


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
                                self.comparison(
                                    still_need_matches=still_need_matches,
                                    operation=operation,
                                    matches=new_matches,
                                )
                            )

    def explanations_implication(
        self, other: ComparableGroup, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        yield from self.comparison(
            operation=operator.ge, still_need_matches=list(other), matches=context
        )

    def explanations_has_all_factors_of(
        self, other: ComparableGroup, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        yield from self.comparison(
            operation=means, still_need_matches=list(other), matches=context
        )

    @property
    def generic_factors(self) -> List[Comparable]:
        generics: Dict[Comparable, None] = {}
        for factor in self:
            for generic in factor.generic_factors:
                generics[generic] = None
        return list(generics)

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

    def new_context(self, context: ContextRegister) -> ComparableGroup:
        result = [factor.new_context(context) for factor in self]
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
    ) -> Optional[ComparableGroup]:
        result = self + other.new_context(context.reversed())
        result = result.drop_implied_factors()
        return result


FactorGroup = ComparableGroup[Factor]


class FactorSequence(Tuple[Optional[Union[Factor, FactorGroup]], ...]):
    def __new__(cls, value: Sequence = ()):
        if isinstance(value, (Factor, ComparableGroup)):
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

        def update_register(register: ContextRegister, i: int = 0):
            """
            Recursively search through :class:`Factor` pairs trying out context assignments.

            This has the potential to take a long time to fail if the problem is
            unsatisfiable. It will reduce risk to check that every :class:`Factor` pair
            is satisfiable before checking that they're all satisfiable together.
            """
            if i == len(ordered_pairs):
                yield register
            else:
                left, right = ordered_pairs[i]
                if left is not None or right is None:
                    if left is None:
                        yield from update_register(register, i + 1)
                    else:
                        new_mapping_choices: List[ContextRegister] = []
                        for incoming_register in left.update_context_register(
                            right, register, operation
                        ):
                            if incoming_register not in new_mapping_choices:
                                new_mapping_choices.append(incoming_register)
                                yield from update_register(incoming_register, i + 1)

        if context is None:
            context = ContextRegister()
        ordered_pairs = list(zip_longest(self, other))
        yield from update_register(register=context)
