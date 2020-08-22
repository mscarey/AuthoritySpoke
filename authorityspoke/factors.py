r""":class:`Factor`\s, or inputs and outputs of legal :class:`.Rule`\s."""

from __future__ import annotations

from dataclasses import dataclass, field
import functools
from itertools import zip_longest
import operator
import textwrap
from typing import Any, Callable, Dict, Iterable, Iterator, List
from typing import Optional, Sequence, Set, Tuple, TypeVar, Union

from legislice import Enactment

from anchorpoint.textselectors import TextQuoteSelector

from authorityspoke.comparisons import (
    ContextRegister,
    Comparable,
    means,
)


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
    query: Union[Factor, str], source_factor: Factor, source_opinion: Opinion
) -> Factor:
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
    factor: Factor, changes: Union[Factor, List, Tuple]
) -> ContextRegister:
    if not isinstance(changes, Iterable):
        changes = (changes,)
    if isinstance(changes, (list, tuple)):
        if (
            len(changes) == 2
            and all(isinstance(item, (tuple, list)) for item in changes)
            and all(isinstance(factor, Comparable) for factor in changes[0])
            and all(isinstance(factor, Comparable) for factor in changes[1])
        ):
            return ContextRegister.from_lists(changes[0], changes[1])
        generic_factors = factor.generic_factors_by_name.keys()
        if len(generic_factors) != len(changes):
            raise ValueError(
                f"Needed {len(generic_factors)} replacements for the "
                + f"items of generic_factors, but {len(changes)} were provided."
            )
        changes = ContextRegister.from_lists(generic_factors, changes)
    return changes


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
        factor: Factor,
        changes: Optional[Union[Sequence[Factor], ContextRegister]],
        source: Optional[Comparable] = None,
    ) -> Factor:

        if changes is None:
            return factor
        if not isinstance(changes, ContextRegister):
            changes = convert_changes_to_register(factor, changes)

        expanded_changes = ContextRegister()
        for old, new in changes.items():
            factor_with_new_name = seek_factor(new, factor, source)
            expanded_changes.insert_pair(old, factor_with_new_name)
        for old, new in expanded_changes.items():
            if str(factor) == old or factor.__dict__.get("name") == old:
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
    def recursive_factors(self) -> Dict[str, Factor]:
        r"""
        Collect `self`'s :attr:`context_factors`, and their :attr:`context_factors`, recursively.

        :returns:
            a :class:`dict` (instead of a :class:`set`,
            to preserve order) of :class:`Factor`\s.
        """
        answers: Dict[str, Factor] = {str(self): self}
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
                yield self.generic_register(other)
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
        factors_to_search = self.recursive_factors
        for value in factors_to_search.values():
            if hasattr(value, "name") and value.name == name:
                return value
        return None

    def get_factor_by_str(self, query: str) -> Optional[Factor]:
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
                if context.get_factor(self) is None or (
                    context.get_factor(self) == other
                ):
                    yield self.generic_register(other)
            if not self.generic:
                yield from self._implies_if_concrete(other, context)

    def _update_context_from_factors(
        self, other: Comparable, context: ContextRegister
    ) -> Optional[ContextRegister]:
        incoming = ContextRegister.from_lists(
            keys=self.generic_factors, values=other.generic_factors
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
        for key, value in changes.matches.items():

            if not isinstance(key, str):
                raise TypeError('Each key in "changes" must be the name of a Factor')
            if value and not isinstance(value, Factor):
                raise TypeError('Each value in "changes" must be a Factor')

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

    @staticmethod
    def _wrap_with_tuple(item):
        if item is None:
            return ()
        if isinstance(item, Iterable):
            return tuple(item)
        return (item,)


TextLinkDict = Dict[Union[Factor, Enactment], List[TextQuoteSelector]]


class FactorSequence(Tuple[Optional[Comparable], ...]):
    def __new__(cls, value: Sequence = ()):
        if isinstance(value, Factor) or value.__class__.__name__ == "FactorGroup":
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

    def insert_factor(self, factor: Factor) -> None:
        name = str(factor)
        self.insert(key=name, value=factor)

