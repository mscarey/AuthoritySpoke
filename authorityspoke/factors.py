r""":class:`Factor`\s, or inputs and outputs of legal :class:`.Rule`\s."""

from __future__ import annotations

from abc import ABC
from dataclasses import astuple, dataclass
import functools
from itertools import zip_longest
import logging
import operator
from typing import Any, Callable, Dict, Iterable, Iterator, List
from typing import Optional, Sequence, Tuple, Union

logger = logging.getLogger(__name__)


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
        indicates the which generic :class:`.Factor`\s within ``factor`` should
        be replaced and what they should be replaced with.

    :param context_opinion:
        a second object that with generic factors that need to be searched
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
            changes = dict(zip(generic_factors, changes))

        for context_factor in changes:
            name_to_seek = changes[context_factor]
            if isinstance(name_to_seek, str):
                changes[context_factor] = factor.get_factor_by_name(name_to_seek)
            if context_opinion and not changes[context_factor]:
                changes[context_factor] = context_opinion.get_factor_by_name(
                    name_to_seek
                )
            if not changes[context_factor]:
                raise ValueError(
                    f"Unable to find a Factor with the name '{name_to_seek}'"
                )

            if factor.means(context_factor) and factor.name == context_factor.name:
                return changes[context_factor]

        return func(factor, changes)

    return wrapper


@dataclass(frozen=True, init=False)
class Factor(ABC):
    """
    Things relevant to a :class:`.Court`\'s application of a :class:`.Rule`.

    The same :class:`Factor` that is in the ``outputs`` for the
    :class:`.Procedure` of one legal :class:`.Rule` might be in the
    ``inputs`` of the :class:`.Procedure` for another.
    """

    def __init__(
        self, *, name: Optional[str] = None, generic: bool = False, absent: bool = False
    ):
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
    def generic_factors(self) -> Tuple[Factor, ...]:
        r"""
        :class:`.Factor`\s that can be replaced without changing ``self``\s meaning.

        :returns:
            a :class:`list` made from a :class:`dict` with ``self``\'s
            generic :class:`.Factor`\s as keys and ``None`` as values,
            so that the keys can be matched to another object's
            ``generic_factors`` to perform an equality test.
        """

        if self.generic:
            return (self,)
        generics: Dict[Factor, None] = {}
        for factor in self.context_factors:
            if factor is not None:
                for generic in factor.generic_factors:
                    generics[generic] = None
        return tuple(generics)

    @property
    def context_factors(self) -> Sequence[Optional[Factor]]:
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
        return tuple(context)

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

    def consistent_with(self, other: Factor, comparison: Callable) -> bool:
        """
        Find whether ``self`` and ``other`` can fit the relationship ``comparison``.

        :returns:
            a bool indicating whether there's at least one way to
            match the :attr:`context_factors` of ``self`` and ``other``,
            such that they fit the relationship ``comparison``.
        """

        context_registers = iter(self._context_registers(other, comparison))
        return any(register is not None for register in context_registers)

    def _contradicts_if_present(self, other: Factor) -> bool:
        """
        Test if ``self`` would contradict ``other`` if neither was ``absent``.

        The default is ``False`` where no class-specific method is available.
        """
        return False

    def _context_registers(
        self, other: Optional[Factor], comparison: Callable
    ) -> Iterator[ContextRegister]:
        r"""
        Search for ways to match :attr:`context_factors` of ``self`` and ``other``.

        :yields:
            all valid ways to make matches between
            corresponding :class:`Factor`\s.
        """

        if other is None:
            yield ContextRegister()
        elif self.generic or other.generic:
            yield ContextRegister({self: other, other: self})
        else:
            relation = Analogy(self.context_factors, other.context_factors, comparison)
            yield from relation.ordered_comparison()

    def contradicts(self, other: Optional[Factor]) -> bool:
        """
        Test whether ``self`` implies the absence of ``other``.

        :returns:
            ``True`` if self and other can't both be true at
            the same time. Otherwise returns ``False``.
        """

        if other is None:
            return False
        if not isinstance(other, Factor):
            raise TypeError(
                f"{self.__class__} objects may only be compared for "
                + "contradiction with other Factor objects or None."
            )
        return self._contradicts_if_factor(other)

    def _contradicts_if_factor(self, other: Factor) -> bool:
        """
        Test whether ``self`` :meth:`implies` the absence of ``other``.

        This should only be called after confirming that ``other``
        is not ``None``.

        :returns:
            ``True`` if self and other can't both be true at
            the same time. Otherwise returns ``False``.
        """
        return self >= other.evolve("absent")

    def evolve(self, changes: Union[str, Tuple[str, ...], Dict[str, Any]]) -> Factor:
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
        if isinstance(changes, str):
            changes = (changes,)
        for key in changes:
            if key not in self.__dict__:
                raise ValueError(
                    f"Invalid: '{key}' is not among the Factor's attributes "
                    f"{list(self.__dict__.keys())}."
                )
        if isinstance(changes, tuple):
            changes = {key: not self.__dict__[key] for key in changes}
        new_dict = self.own_attributes()
        for key in changes:
            new_dict[key] = changes[key]
        return self.__class__(**new_dict)

    def means(self, other) -> bool:
        r"""
        Test whether ``self`` and ``other`` have identical meanings.

        :returns:
            whether ``other`` is another :class:`Factor`
            with the same meaning as ``self``. Not the same as an
            equality comparison with the ``==`` symbol, which simply
            converts ``self``\'s and ``other``\'s fields to tuples
            and compares them.
        """
        if (
            self.__class__ != other.__class__
            or self.absent != other.absent
            or self.generic != other.generic
        ):
            return False
        if self.generic and other.generic:
            return True
        return self._means_if_concrete(other)

    def _means_if_concrete(self, other: Factor) -> bool:
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
        for i, self_factor in enumerate(self.context_factors):
            other_factor = other.context_factors[i]
            if self_factor is None:
                if other_factor is not None:
                    return False
            elif not self_factor.means(other_factor):
                return False

        return self.consistent_with(other, means)

    def get_factor_by_name(self, name: str) -> Optional[Factor]:
        """
        Search of ``self`` and ``self``'s attributes for :class:`Factor` with specified ``name``.

        :returns:
            a :class:`Factor` with the specified ``name`` attribute
            if it exists, otherwise ``None``.
        """
        for factor in self.recursive_factors:
            if factor.name == name:
                return factor
        return None

    def implies(self, other: Optional[Factor]) -> bool:
        """Test whether ``self`` implies ``other``."""
        if other is None:
            return True

        if not isinstance(other, Factor):
            raise TypeError(
                f"{self.__class__} objects may only be compared for "
                + "implication with other Factor objects or None."
            )
        if not self.__dict__.get("absent"):
            if not other.__dict__.get("absent"):
                return bool(self._implies_if_present(other))
            return bool(self._contradicts_if_present(other))

        # if self.__dict__.get("absent")
        if other.__dict__.get("absent"):
            return bool(other._implies_if_present(self))
        return bool(other._contradicts_if_present(self))

    def __gt__(self, other: Optional[Factor]) -> bool:
        """Test whether ``self`` implies ``other`` and ``self`` != ``other``."""
        return self.implies(other) and self != other

    def __ge__(self, other: Optional[Factor]) -> bool:
        """
        Call :meth:`implies` as an alias.

        :returns:
            bool indicating whether ``self`` implies ``other``
        """
        return self.implies(other)

    def _implies_if_concrete(self, other: Factor) -> bool:
        """
        Find if ``self`` would imply ``other`` if they aren't absent or generic.

        Used to test implication based on :attr:`context_factors`,
        usually after a subclass has injected its own tests
        based on other attributes.

        :returns:
            bool indicating whether ``self`` would imply ``other``,
            under the assumptions that neither ``self`` nor ``other``
            has ``absent=True``, neither has ``generic=True``, and
            ``other`` is an instance of ``self``'s class.
        """
        for i, self_factor in enumerate(self.context_factors):
            if other.context_factors[i]:
                if not (self_factor and self_factor >= other.context_factors[i]):
                    return False
        return self.consistent_with(other, operator.ge)


    def _implies_if_present(self, other: Factor) -> bool:
        """
        Find if ``self`` would imply ``other`` if they aren't absent.

        :returns:
            bool indicating whether ``self`` would imply ``other``,
            under the assumption that neither self nor other has
            the attribute ``absent == True``.
        """
        if isinstance(other, self.__class__):
            if other.generic:
                return True
            if self.generic:
                return False
            return bool(self._implies_if_concrete(other))
        return False

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
        string = f"{self.__class__.__name__.lower()}" + " {}"
        if self.generic:
            string = f"<{string}>"
        if self.absent:
            string = "absence of " + string
        return string

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


@dataclass(frozen=True)
class Entity(Factor):
    r"""
    Things that exist in the outside world, like people, places, or events.

    Not concepts that derive their meaning from litigation,
    such as a legal Fact, an Allegation, a Pleading, etc.

    Best used to specify things to be mentioned in
    multiple :class:`.Factor`\s in a :class:`.Rule`, often in the
    :class:`.Predicate` of a :class:`.Fact` object.

    An :class:`Entity` is often, but not always, ``generic`` with
    respect to the meaning of the :class:`.Rule` in which it is
    mentioned, which means that the :class:`.Rule` is understood
    to apply generally even if some other :class:`Entity` was
    substituted.

    :param name:
        An identifier. An :class:`Entity` with the same ``name``
        is considered to refer to the same specific object, but
        if they have different names but are ``generic`` and are
        otherwise the same, then they're considered to have the
        same meaning and they evaluate equal to one another.

    :param generic:
        Determines whether a change in the ``name`` of the
        :class:`Entity` would change the meaning of the
        :class:`.Factor` in which the :class:`Entity` is
        embedded.

    :param plural:
        Specifies whether the :class:`Entity` object refers to
        more than one thing. In other words, whether it would
        be represented by a plural noun.
    """

    name: Optional[str] = None
    generic: bool = True
    plural: bool = False

    def means(self, other):
        """
        Test whether ``other`` has the same meaning as ``self``.

        ``Generic`` :class:`Entity` objects are considered equivalent
        in meaning as long as they're the same class. If not ``generic``,
        they're considered equivalent if all their attributes are the same.
        """

        if self.__class__ != other.__class__:
            return False
        if self.generic and other.generic:
            return True
        return astuple(self) == astuple(other)

    def __ge__(self, other: Optional[Factor]):
        if other is None:
            return True
        if not isinstance(other, Entity):
            return False
        if self.generic is False and self.name == other.name:
            return True
        return other.generic

    def __str__(self):
        if self.generic:
            return f"<{self.name}>"
        return self.name

    def _context_register(self, other: Factor, comparison) -> Iterator[ContextRegister]:
        """
        Find how ``self``\'s context of can be mapped onto ``other``\'s.

        :yields:
            the only possible way the context of one ``Entity`` can be
            mapped onto the context of another.
        """
        # If there was a way to compare an Entity to None, should it return {}?
        if comparison(self, other):
            yield {self: other, other: self}

    def contradicts(self, other: Optional[Factor]) -> bool:
        """
        Test whether ``self`` contradicts the ``other`` :class:`Factor`.

        :returns:
            ``False``, because an :class:`Entity` contradicts no other :class:`Factor`.
        """
        if other is None:
            return False

        if not isinstance(other, Factor):
            raise TypeError(
                f"'Contradicts' not supported between class "
                + f"{self.__class__.__name__} and class {other.__class__.__name__}."
            )
        return False

    @new_context_helper
    def new_context(self, changes: ContextRegister) -> Entity:
        """
        Create new :class:`Factor`, replacing keys of ``changes`` with values.

        Assumes no changes are possible because the :func:`new_context_helper`
        decorator would have replaced ``self`` if any replacement was available.
        """
        return self


class ContextRegister(Dict[Factor, Optional[Factor]]):
    r"""
    A mapping of corresponding :class:`Factor`\s from two different contexts.

    When :class:`Factor`\s are matched in a ContextRegister, it indicates
    that their relationship can be described by a comparison function
    like :func:`means`, :meth:`Factor.implies`, or :meth:`Factor.consistent_with`\.
    """

    def __str__(self) -> str:
        return "ContextRegister({})".format(super().__str__())

    def is_full(self) -> bool:
        """Check whether all keys are matched to a :class:`.Factor` value."""
        return all(key for key in self.keys())

    def replace_keys(self, replacements: ContextRegister) -> ContextRegister:
        """Construct new :class:`ContextRegister` by replacing keys."""
        values = self.values()
        keys = [replacements.get(factor) or factor for factor in self.keys()]
        return ContextRegister(zip(keys, values))

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
        self_mapping = ContextRegister(self.items())
        for in_key, in_value in incoming_mapping.items():

            if in_key and in_value:
                if self_mapping.get(in_key) and self_mapping.get(in_key) != in_value:
                    logger.debug(
                        f"{in_key} already in mapping with value "
                        + f"{self_mapping[in_key]}, not {in_value}"
                    )
                    return None
                if self_mapping.get(in_value) and self_mapping.get(in_value) != in_key:
                    logger.debug(
                        f"key {in_value} already in mapping with value "
                        + f"{self_mapping[in_value]}, not {in_key}"
                    )
                    return None
                if in_key.generic or in_value.generic:
                    self_mapping[in_key] = in_value
                    self_mapping[in_value] = in_key
        return self_mapping


@dataclass(frozen=True)
class Analogy:
    r"""
    Two groups of :class:`.Factor`\s and a function that must hold between them.

    Can be used to find ways to assign the :class:`.Factor`\s'
    context assignments consistently with the :class:`Analogy`\.

    :param need_matches:
        :class:`.Factor`\s that all need to satisfy the ``comparison``
        with some :class:`.Factor` of ``available``
        for the relation to hold.

    :param available:
        :class:`.Factor`\s available for matching with the
        :attr:`need_matches` :class:`.Factor`\s, but that don't
        all need to be matched themselves for the relation to hold.

    :param comparison:
        a function defining the comparison that must be ``True``
        between each :attr:`need_matches` and some :attr:`available`
        for the relation to hold. Could be :meth:`.Factor.means` or
        :meth:`.Factor.__ge__`.
    """

    need_matches: Sequence[Optional[Factor]]
    available: Sequence[Optional[Factor]]
    comparison: Callable

    def ordered_comparison(
        self, matches: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        r"""
        Find ways for a series of pairs of :class:`.Factor`\s to satisfy a comparison.

        :param matches:
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
                            right, register, self.comparison
                        ):
                            if incoming_register not in new_mapping_choices:
                                new_mapping_choices.append(incoming_register)
                                yield from update_register(
                                    incoming_register, i + 1
                                )

        if matches is None:
            matches = ContextRegister()
        ordered_pairs = list(zip_longest(self.need_matches, self.available))
        yield from update_register(register=matches)

    def unordered_comparison(
        self,
        matches: ContextRegister,
        still_need_matches: Optional[List[Factor]] = None,
    ) -> Iterator[ContextRegister]:
        r"""
        Find ways for two unordered sets of :class:`.Factor`\s to satisfy a comparison.

        :param matches:
            a mapping of :class:`.Factor`\s that have already been matched
            to each other in the recursive search for a complete group of
            matches. Starts empty when the method is first called.

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
        if still_need_matches is None:
            still_need_matches = list(self.need_matches)

        if not still_need_matches:
            # This seems to allow duplicate values in
            # Procedure.output, .input, and .despite, but not in
            # attributes of other kinds of Factors. Likely cause
            # of bugs.
            yield matches
        else:
            self_factor = still_need_matches.pop()
            for other_factor in self.available:
                if self.comparison(self_factor, other_factor):
                    updated_mappings = iter(
                        self_factor.update_context_register(
                            other_factor, matches, self.comparison
                        )
                    )
                    for new_matches in updated_mappings:
                        if new_matches:
                            yield from iter(
                                self.unordered_comparison(
                                    new_matches, still_need_matches
                                )
                            )

    def update_matchlist(
        self, matchlist: List[ContextRegister]
    ) -> List[ContextRegister]:
        r"""
        Filter context assignments with :meth:`~Analogy.unordered_comparison`.

        :param matchlist:
            possible ways to match generic :class:`.Factor`\s of
            ``need_matches`` with ``available``.

        :returns:
            a new version of ``matchlist`` filtered to be consistent with
            ``self``\'s :meth:`~Analogy.unordered_comparison`.
        """
        new_matchlist = []
        for matches in matchlist:
            for answer in self.unordered_comparison(matches=matches):
                new_matchlist.append(answer)
        return new_matchlist


def all_analogy_matches(relations: Tuple[Analogy, ...]) -> List[ContextRegister]:
    r"""
    Find all context registers consistent with multiple :class:`.Analogy` comparisons.

    :param relations:
        a series of :class:`.Analogy` comparisons in which
        the ``need_matches`` :class:`.Factor`\s all refer to
        one context (for instance, the same :class:`.Opinion`),
        and the ``available`` :class:`.Factor`\s all refer to
        another context.

    :returns:
        a list of all context registers consistent with all of the
        :class:`.Analogy`\s.
    """
    matchlist: List[ContextRegister] = [ContextRegister()]
    for relation in relations:
        matchlist = relation.update_matchlist(matchlist)
    return matchlist
