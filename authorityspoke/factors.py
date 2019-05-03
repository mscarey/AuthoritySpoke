from __future__ import annotations

import datetime
import functools
import logging
import operator
import re

from abc import ABC

from typing import Any, Callable, Dict, List, Tuple
from typing import Iterable, Iterator, Mapping
from typing import Optional, Sequence, Set, Type, Union

from pint import UnitRegistry

from authorityspoke.context import log_mentioned_context
from authorityspoke.predicates import Predicate

from dataclasses import astuple, dataclass


def new_context_helper(func: Callable):

    """
    Decorator for :meth:`Factor.new_context`.

    If a :class:`list` has been passed in rather than a :class:`dict`, uses
    the input as a set of :class:`Factor`\s to replace the
    :attr:`Factor.generic_factors` from the calling object.

    Also, if ``context`` contains a replacement for the calling
    object, the decorator returns the replacement and never calls
    the decorated function.
    """

    @functools.wraps(func)
    def wrapper(
        factor: Factor, context: Optional[Union[Sequence[Factor], Dict[Factor, Factor]]]
    ) -> Factor:

        if context is not None:
            if not isinstance(context, Iterable):
                context = (context,)
            if any(not isinstance(item, (Factor, str)) for item in context):
                raise TypeError(
                    'Each item in "context" must be a Factor or the name of a Factor'
                )
            if not isinstance(context, dict):
                generic_factors = factor.generic_factors
                if len(generic_factors) != len(context):
                    raise ValueError(
                        'If the parameter "changes" is not a list of '
                        + "replacements for every element of factor.generic_factors, "
                        + 'then "changes" must be a dict where each key is a Factor '
                        + "to be replaced and each value is the corresponding "
                        + "replacement Factor."
                    )
                context = dict(zip(generic_factors, context))
            for context_factor in context:
                if factor.name == context_factor or (
                    factor == context_factor and factor.name == context_factor.name
                ):
                    return context[context_factor]

        return func(factor, context)

    return wrapper


@dataclass(frozen=True)
class Factor(ABC):
    """
    Anything relevant to a court's determination of the applicability
    of a legal :class:`.Rule` can be a :class:`Factor`. The same
    :class:`Factor` that is in the :attr:`.Procedure.outputs`
    for one legal :class:`.Rule` might be in the :attr:`.Procedure.inputs`
    for another.
    """

    @classmethod
    def all_subclasses(cls) -> Set[Type]:
        """
        :return: the set of all subclasses of :class:`Factor`
        """
        return set(cls.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in c.all_subclasses()]
        )

    @classmethod
    @functools.lru_cache()
    def class_from_str(cls, name: str):
        """
        Part of the JSON deserialization process. Obtains a classname
        of a :class:`Factor` subclass from a string, checking first
        in the lru_cache of known subclasses.

        :param: name of the desired subclass
        """
        name = name.capitalize()
        class_options = {
            class_obj.__name__: class_obj for class_obj in cls.all_subclasses()
        }
        answer = class_options.get(name)
        if answer is None:
            raise ValueError(
                f'"type" value in input must be one of '
                + f"{list(class_options.keys())}, not {name}"
            )
        return answer

    @classmethod
    def _build_from_dict(cls, factor_record: Dict, mentioned: List[Factor]) -> Factor:
        example = cls()
        new_factor_dict = example.__dict__
        for attr in new_factor_dict:
            if attr in example.context_factor_names:
                value, mentioned = Factor.from_dict(factor_record.get(attr), mentioned)
            else:
                value = factor_record.get(attr)
            if value is not None:
                new_factor_dict[attr] = value
        return (cls(**new_factor_dict), mentioned)

    @classmethod
    @log_mentioned_context
    def from_dict(
        cls, factor_record: Dict, mentioned: List[Factor]
    ) -> Optional[Factor]:
        """
        Turns a dict recently created from a chunk of JSON
        into a :class:`Factor` object.

        :param factor_record:
            parameter values to pass to :meth:`Factor.__init__`.

        :param mentioned:
            a list of relevant :class:`Factor`\s that have already been
            constructed and can be used in composition of the output
            :class:`Factor`, instead of constructing new ones.
        """
        cname = factor_record["type"]
        target_class = cls.class_from_str(cname)
        return target_class._build_from_dict(factor_record, mentioned)

    @property
    def context_factor_names(self) -> Tuple[str, ...]:
        """
        This method and :meth:`interchangeable_factors` should be the only parts
        of the context-matching process that need to be unique for each
        subclass of :class:`Factor`.

        :returns:
            attribute names identifying which attributes of ``self`` and
            ``other`` must match, for a :class:`.Relation` to hold between
            this :class:`Factor` and another.
        """

        return ()

    @property
    def interchangeable_factors(self) -> List[Dict[Factor, Factor]]:
        """
        :returns:
            the ways :attr:`context_factors` can be reordered without
            changing the meaning of ``self``, or whether it would
            be true in a particular context.

            This is the default version for subclasses that don't have any
            interchangeable :attr:`context_factors`.
        """
        return []

    @property
    def generic_factors(self) -> Dict[Factor, None]:
        """
        :returns:
            a :class:`dict` with self's generic :class:`Factor`\s
            as keys and ``None`` as values, so that the keys can
            be matched to  another object's ``generic_factors``
            to perform an equality test.
        """

        if self.generic:
            return {self: None}
        return {
            generic: None
            for factor in self.context_factors
            for generic in factor.generic_factors
        }

    @property
    def context_factors(self) -> Tuple:
        """
        :returns:
            a tuple of attributes that are designated as the ``context_factors``
            for whichever subclass of :class:`Factor` calls this method. These
            can be used for comparing objects using :meth:`consistent_with`
        """
        return tuple(
            self.__dict__.get(factor_name) for factor_name in self.context_factor_names
        )

    @property
    def recursive_factors(self) -> Dict[Factor, None]:
        """
        :returns:
            a :class:`dict` (instead of a :class:`set`,
            to preserve order) of :class:`Factor`\s including ``self``'s
            :attr:`context_factors`, and each of those :class:`Factor`\s'
            :attr:`context_factors`, recursively.
        """
        answers: Dict[Factor, None] = {self: None}
        for context in filter(lambda x: x is not None, self.context_factors):
            if isinstance(context, Iterable):
                for item in context:
                    answers.update(item.recursive_factors)
            else:
                answers.update(context.recursive_factors)
        return answers

    def consistent_with(self, other: Factor, comparison: Callable) -> bool:
        """
        :returns:
            a bool indicating whether there's at least one way to
            match the :attr:`context_factors` of ``self`` and ``other``,
            such that they fit the relationship ``comparison``.
        """

        context_registers = iter(self._context_register(other, operator.ge))
        return any(register is not None for register in context_registers)

    def _context_register(
        self, other: Factor, comparison: Callable
    ) -> Iterator[Dict[Factor, Factor]]:
        """
        Searches through the :attr:`context_factors` of ``self``
        and ``other``, and yields all valid ways to make matches between
        corresponding :class:`Factor`\s.
        """

        if other is None:
            yield {}
        elif self.generic or other.generic:
            yield {self: other, other: self}
        else:
            for registry in self._update_mapping(
                {}, self.context_factors, other.context_factors, comparison
            ):
                yield registry

    def contradicts(self, other: Optional[Factor]) -> bool:
        """
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
        A :meth:`contradicts` method under the assumption that ``other``
        is not ``None``.

        :returns:
            ``True`` if self and other can't both be true at
            the same time. Otherwise returns ``False``.
        """
        return self >= other.evolve("absent")

    def evolve(self, changes: Union[str, Tuple[str, ...], Dict["str", Any]]) -> Factor:
        """
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
        new_dict = self.__dict__.copy()
        for key in changes:
            new_dict[key] = changes[key]
        return self.__class__(**new_dict)

    def __eq__(self, other) -> bool:
        if self.__class__ != other.__class__:
            return False

        if self.absent != other.absent:
            return False

        if self.generic == other.generic == True:
            return True

        if self.generic != other.generic:
            return False

        return self._equal_if_concrete(other)

    def _equal_if_concrete(self, other: Factor) -> bool:
        """
        Used to test equality based on :attr:`context_factors`,
        usually after a subclasses has injected its own tests
        based on other attributes.

        :returns:
            bool indicating whether ``self`` would equal ``other``,
            under the assumptions that neither ``self`` nor ``other``
            has ``absent=True``, neither has ``generic=True``, and
            ``other`` is an instance of ``self``'s class.
        """
        for i, self_factor in enumerate(self.context_factors):
            if self_factor != other.context_factors[i]:
                return False

        return self.consistent_with(other, operator.eq)

    def get_factor_by_name(self, name: str) -> Optional[Factor]:
        """
        Performs a recursive search of ``self`` and ``self``'s attributes
        for a :class:`Factor` with the specified ``name`` attribute.

        :returns:
            a :class:`Factor` with the specified ``name`` attribute
            if it exists, otherwise returns ``None``.
        """
        for factor in self.recursive_factors:
            if factor.name == name:
                return factor
        return None

    def __ge__(self, other: Factor) -> bool:
        """
        :returns:
            bool indicating whether ``self`` implies ``other``.
        """
        if other is None:
            return True

        if not isinstance(other, Factor):
            raise TypeError(
                f"{self.__class__} objects may only be compared for "
                + "implication with other Factor objects or None."
            )

        if self.__dict__.get("absent") and other.__dict__.get("absent"):
            return bool(other._implies_if_present(self))

        if not self.__dict__.get("absent") and not other.__dict__.get("absent"):
            return bool(self._implies_if_present(other))

        return False

    def __gt__(self, other: Optional[Factor]) -> bool:
        """
        :returns:
            bool indicating whether ``self`` implies ``other``
            and ``self`` != ``other``.
        """
        return self >= other and self != other

    def _implies_if_concrete(self, other: Factor) -> bool:
        """
        Used to test implication based on :attr:`context_factors`,
        usually after a subclasses has injected its own tests
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

    @new_context_helper
    def new_context(self, changes: Dict[Factor, Factor]) -> Factor:
        """
        :param changes:
            has :class:`Factor`\s to replace as keys, and has
            their replacements as the corresponding values.

        :returns:
            a new :class:`Factor` object with the replacements made.
        """
        new_dict = self.__dict__.copy()
        for name in self.context_factor_names:
            new_dict[name] = self.__dict__[name].new_context(changes)
        return self.__class__(**new_dict)

    def _registers_for_interchangeable_context(
        self, matches: Dict[Factor, Factor]
    ) -> Iterator[Dict[Factor, Factor]]:
        """
        :yields:
            context registers with every possible combination of
            ``self``'s and ``other``'s interchangeable
            :attr:`context_factors`.
        """

        def replace_factors_in_dict(
            matches: Dict[Factor, Factor], replacement_dict: Dict[Factor, Factor]
        ):
            values = matches.values()
            keys = [replacement_dict.get(factor) or factor for factor in matches.keys()]
            return dict(zip(keys, values))

        yield matches
        already_returned: List[Dict[Factor, Factor]] = [matches]
        for replacement_dict in self.interchangeable_factors:
            changed_registry = replace_factors_in_dict(matches, replacement_dict)
            if not any(
                compare_dict_for_identical_entries(changed_registry, returned_dict)
                for returned_dict in already_returned
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

    @staticmethod
    def _import_to_mapping(
        self_mapping: Dict[Factor, Factor], incoming_mapping: Dict[Factor, Factor]
    ) -> Optional[Dict[Factor, Factor]]:
        """
        Compares :class:`Factor`\s based on their :meth:`__repr__` to
        determine whether two sets of matches of :class:`Factor`\s
        can be merged.

        :meth:`__repr__` was chosen because an ``is`` test would
        return ``False`` when the :class:`Factor`\s are equal but
        not identical, while :meth:`__eq__` incorrectly matches
        generically equal :class:`Factor`\s that don't refer to the
        same thing.

        This problem is a consequence of overloading the :meth:`__eq__`
        operator.

        :param self_mapping:
            an existing mapping of :class:`Factor`\s
            from ``self`` to :class:`Factor`\s from ``other``

        :param incoming_mapping:
            an incoming mapping of :class:`Factor`\s
            from ``self`` to :class:`Factor`\s from ``other``

        :returns:
            ``None`` if the same :class:`Factor` in one mapping
            appears to match to two different :class:`Factor`\s in the other.
            Otherwise returns an updated :class:`dict` of matches.
        """
        logger = logging.getLogger("context_match_logger")
        self_mapping = dict(self_mapping)
        # The key-value relationship isn't symmetrical when the root Factors
        # are being compared for implication.
        for in_key, in_value in incoming_mapping.items():

            if in_key and in_value:
                if self_mapping.get(in_key) and repr(self_mapping.get(in_key)) != repr(
                    in_value
                ):
                    logger.debug(
                        f"{in_key} already in mapping with value "
                        + f"{self_mapping[in_key]}, not {in_value}"
                    )
                    return None
                if self_mapping.get(in_value) and repr(
                    self_mapping.get(in_value)
                ) != repr(in_key):
                    logger.debug(
                        f"key {in_value} already in mapping with value "
                        + f"{self_mapping[in_value]}, not {in_key}"
                    )
                    return None
                if in_key.generic or in_value.generic:
                    self_mapping[in_key] = in_value
                    self_mapping[in_value] = in_key
        return self_mapping

    def _update_mapping(
        self,
        self_mapping: Dict[Factor, Factor],
        self_factors: Tuple[Factor],
        other_factors: Tuple[Factor],
        comparison: Callable,
    ):
        """
        .. note::
            I understood how this method works, and I wrote the
            docstring for this method, but not at the same time.

        :param self_mapping:
            keysing representing :class:`Factor`\s in ``self`` and
            values representing :class:`Factor`\s in ``other``. The
            keys and values have been found in corresponding positions
            in ``self`` and ``other``.

        :param self_factors:
            :class:`Factor`\s from ``self`` that will be matched with
            ``other_factors``. This function is expected to be called
            with various permutations of ``other_factors``, but no other
            permutations of ``self_factors``.

        :param other_factors:
            other's :attr:`context_factors`

        :returns:
            :class:`bool` indicating whether the :class:`Factor`\s in
            ``other_factors`` can be matched to the :class:`Factor`\s in
            ``self_factors`` in ``self_mapping``, without making the
            same :class:`Factor` from ``other_factors``
            match to two different factors in self_mapping.
        """

        new_mapping_choices = [self_mapping]

        self_factors = self._wrap_with_tuple(self_factors)
        other_factors = self._wrap_with_tuple(other_factors)

        # why am I allowing the __len__s to be different?
        shortest = min(len(self_factors), len(other_factors))

        # The "is" comparison is for None values.
        if not all(
            self_factors[index] is other_factors[index]
            or comparison(self_factors[index], other_factors[index])
            for index in range(shortest)
        ):
            return None
        # TODO: change to depth-first
        for index in range(shortest):
            mapping_choices = new_mapping_choices
            new_mapping_choices = []
            for mapping in mapping_choices:
                if self_factors[index] is None:
                    new_mapping_choices.append(mapping)
                else:
                    register_iter = iter(
                        self_factors[index]._context_register(
                            other_factors[index], comparison
                        )
                    )
                    for incoming_register in register_iter:
                        for transposed_register in self_factors[
                            index
                        ]._registers_for_interchangeable_context(incoming_register):
                            updated_mapping = self._import_to_mapping(
                                mapping, transposed_register
                            )
                            if updated_mapping not in new_mapping_choices:
                                new_mapping_choices.append(updated_mapping)
        for choice in new_mapping_choices:
            yield choice

    @staticmethod
    def _wrap_with_tuple(item):
        if isinstance(item, Iterable):
            return tuple(item)
        return (item,)



@dataclass(frozen=True)
class Fact(Factor):
    """An assertion accepted as factual by a court, often through factfinding by
    a judge or jury."""

    predicate: Optional[Predicate] = None
    context_factors: Tuple[Factor, ...] = ()
    name: Optional[str] = None
    standard_of_proof: Optional[str] = None
    absent: bool = False
    generic: bool = False
    case_factors: Tuple[Factor, ...] = ()

    def __post_init__(self):

        if (
            self.standard_of_proof
            and self.standard_of_proof not in self.standards_of_proof()
        ):
            raise ValueError(
                f"standard of proof must be one of {self.standards_of_proof()} or None."
            )
        context_factors = self.context_factors
        case_factors = self.case_factors
        object.__delattr__(self, "case_factors")

        if not context_factors:
            context_factors = range(len(self.predicate))
        case_factors = self.__class__._wrap_with_tuple(case_factors)
        context_factors = self.__class__._wrap_with_tuple(context_factors)

        if len(context_factors) != len(self.predicate):
            raise ValueError(
                "The number of items in 'context_factors' must be "
                + f"{len(self.predicate)}, to match predicate.context_slots"
            )
        if any(not isinstance(s, (Factor, int)) for s in context_factors):
            raise TypeError(
                "Items in the context_factors parameter should "
                + "be Factor or a subclass of Factor, or should be integer "
                + "indices of Factor objects in the case_factors parameter."
            )

        def get_factor_by_index(
            factor_or_index: Union[Factor, int], case_factors: List[Factor]
        ) -> Factor:
            if isinstance(factor_or_index, int):
                if 0 <= factor_or_index < len(case_factors):
                    factor_or_index = case_factors[factor_or_index]
                else:
                    raise ValueError(
                        f"The integer {factor_or_index} could not be interpreted as "
                        + f"the index of an item from case_factors, which has length "
                        + f"{len(case_factors)}."
                    )
            return factor_or_index

        if any(isinstance(s, int) for s in context_factors):
            context_factors = tuple(
                get_factor_by_index(i, case_factors) for i in context_factors
            )
        object.__setattr__(self, "context_factors", context_factors)

    def __str__(self):
        predicate = str(self.predicate.content_with_entities(self.context_factors))
        standard = (
            f"by the standard {self.standard_of_proof}, "
            if self.standard_of_proof
            else ""
        )
        string = f"{standard}{predicate}"
        return super().__str__().format(string)

    @classmethod
    def standards_of_proof(cls) -> Tuple[str, ...]:
        """
        Returns a tuple with every allowable name for a standard of proof,
        in order from weakest to strongest.

        If any courts anywhere disagree about the relative strength of
        these standards of proof, or if any court considers the order
        context-specific, this representation will have to change.
        """
        return (
            "scintilla of evidence",
            "substantial evidence",
            "preponderance of evidence",
            "clear and convincing",
            "beyond reasonable doubt",
        )

    @property
    def interchangeable_factors(self) -> List[Dict[Factor, Factor]]:
        """
        Yields the ways the context factors referenced by the Fact object
        can be reordered without changing the truth value of the Fact.
        Currently the predicate must be phrased either in a way that doesn't
        make any context factors interchangeable, or if the "reciprocal" flag
        is set, in a way that allows only the first two context factors to switch
        places.

        Each dict returned has factors to replace as keys, and factors to
        replace them with as values. If there's more than one way to
        rearrange the context factors, more than one dict should be returned.
        """
        if self.predicate and self.predicate.reciprocal:
            return [
                {
                    self.context_factors[1]: self.context_factors[0],
                    self.context_factors[0]: self.context_factors[1],
                }
            ]
        return []

    def _equal_if_concrete(self, other: Factor) -> bool:
        if (
            self.predicate != other.predicate
            or self.standard_of_proof != other.standard_of_proof
        ):
            return False
        return super()._equal_if_concrete(other)

    def __eq__(self, other) -> bool:
        return super().__eq__(other)

    def make_generic(self) -> "Fact":
        """
        This returns a new object changing generic to True. But it does
        preserve the predicate attribute.
        For a Fact with no features specified, use: Fact(generic=True)
        """

        return Fact(
            predicate=self.predicate,
            context_factors=self.context_factors,
            standard_of_proof=self.standard_of_proof,
            absent=self.absent,
            generic=True,
        )

    def predicate_in_context(self, entities: Sequence[Factor]) -> str:
        """Prints the representation of the Predicate with Entities
        added into the slots, with added text from the Fact object
        indicating the class name and whether the Predicate is
        "Absent" or not."""

        return (
            f"{'Absent ' if self.absent else ''}{self.__class__.__name__}: "
            + f"{self.predicate.content_with_entities(entities)}"
        )

    def __len__(self):
        return len(self.context_factors)

    def _implies_if_concrete(self, other: Factor) -> bool:
        if bool(self.standard_of_proof) != bool(other.standard_of_proof):
            return False

        if self.standard_of_proof and self.standards_of_proof().index(
            self.standard_of_proof
        ) < self.standards_of_proof().index(other.standard_of_proof):
            return False

        if not self.predicate >= other.predicate:
            return False
        return super()._implies_if_concrete(other)

    def contradicts_if_present(self, other: "Fact") -> bool:
        """
        Indicates whether self contradicts the Fact other under the assumption that
        self.absent == False.
        """
        if (self.predicate.contradicts(other.predicate) and not other.absent) or (
            self.predicate >= other.predicate and other.absent
        ):
            return self.consistent_with(other, operator.ge)
        return False

    def _contradicts_if_factor(self, other: Factor) -> bool:
        """
        :returns:
            True if self and other can't both be true at the same time.
            Otherwise returns False.
        """

        if not isinstance(other, self.__class__):
            return False

        if self.absent:
            return other.contradicts_if_present(self)
        return self.contradicts_if_present(other)

    @classmethod
    def _build_from_dict(
        cls, fact_dict: Dict[str, Union[str, bool]], mentioned: List[Factor]
    ) -> Tuple[Optional["Fact"], List[Factor]]:
        """
        Constructs and returns a :class:`Fact` object from a dict imported from
        a JSON file in the format used in the "input" folder.
        """

        placeholder = "{}"  # to be replaced in the Fact's string method

        def add_content_references(
            content: str, mentioned: List[Factor], placeholder: str
        ) -> Tuple[str, List[Factor]]:
            """
            :param content: the content for the :class:`Fact`\'s Predicate

            :param mentioned:
                list of :class:`Factor`\s with names that could be
                referenced in content

            :param placeholder:
                a string to replace the names of
                referenced :class:`Factor`\s in content

            :returns:
                the content string with any referenced :class:`Factor`\s
                replaced by placeholder, and a list of referenced
                :class:`Factor`\s in the order they appeared in content.
            """
            context_with_indices: List[List[Factor, int]] = []
            for factor in mentioned:
                if factor.name and factor.name in content:
                    factor_index = content.find(factor.name)
                    for pair in context_with_indices:
                        if pair[1] > factor_index:
                            pair[1] -= len(factor.name) - len(placeholder)
                    context_with_indices.append([factor, factor_index])
                    content = content.replace(factor.name, placeholder)
            context_factors = [
                k[0] for k in sorted(context_with_indices, key=lambda k: k[1])
            ]
            return content, context_factors

        # TODO: inherit the later part of this function from Factor
        comparison = None
        quantity = None
        content = fact_dict.get("content")
        if fact_dict.get("content"):
            content = fact_dict.get("content")
            content, context_factors = add_content_references(
                content, mentioned, placeholder
            )
        for item in Predicate.OPPOSITE_COMPARISONS():
            if item in content:
                comparison = item
                content, quantity = content.split(item)
                quantity = Predicate.str_to_quantity(quantity)
                content += placeholder

        # TODO: get default attributes from the classes instead of
        # rewriting them here.
        predicate = Predicate(
            content=content,
            truth=fact_dict.get("truth", True),
            reciprocal=fact_dict.get("reciprocal", False),
            comparison=comparison,
            quantity=quantity,
        )

        factor = cls(
            predicate,
            context_factors,
            name=fact_dict.get("name", None),
            standard_of_proof=fact_dict.get("standard_of_proof", None),
            absent=fact_dict.get("absent", False),
            generic=fact_dict.get("generic", False),
        )
        return factor, mentioned

    @new_context_helper
    def new_context(self, changes: Dict[Factor, Factor]) -> Factor:
        """
        Creates new Fact object, replacing keys of "changes" with their values.
        """
        new_context_factors = [
            factor.new_context(changes) for factor in self.context_factors
        ]
        return Fact(
            self.predicate,
            tuple(new_context_factors),
            self.name,
            self.standard_of_proof,
            self.absent,
            self.generic,
        )


@dataclass(frozen=True)
class Entity(Factor):
    """A person, place, thing, or event that needs to be mentioned in
    multiple predicates/factors in a holding."""

    name: Optional[str] = None
    generic: bool = True
    plural: bool = False

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.generic and other.generic:
            return True
        return astuple(self) == astuple(other)

    def __ge__(self, other: Optional[Factor]):
        return self == other or self > other

    def __gt__(self, other: Optional[Factor]):
        if other is None:
            return True
        if not isinstance(self, other.__class__):
            return False
        if self == other:
            return False
        if self.generic == False and self.name == other.name:
            return True
        return other.generic

    def __str__(self):
        if self.generic:
            return f"<{self.name}>"
        return self.name

    def _context_register(
        self, other: Factor, comparison
    ) -> Optional[Dict[Factor, Factor]]:
        """Returns a list of possible ways the context of self can be
        mapped onto the context of other. Other subclasses of Factor
        will have more complex lists."""

        # If there was a way to compare an Entity to None, should it return {}?
        if comparison(self, other):
            yield {self: other, other: self}

    def contradicts(self, other: Factor) -> bool:
        if not isinstance(other, Factor):
            raise TypeError(
                f"'Contradicts' not supported between class "
                + f"{self.__class__.__name__} and class {other.__class__.__name__}."
            )
        return False

    def make_generic(self):
        if not self.generic:
            return self.__class__(name=self.name, generic=True, plural=self.plural)
        return self

    @new_context_helper
    def new_context(self, context: Dict[Factor, Factor]) -> "Entity":
        return self


@dataclass(frozen=True)
class Pleading(Factor):
    """
    A formal assertion of a Fact, included by a party in a Pleading
    to establish a cause of action.
    """

    filer: Optional[Entity] = None
    date: Optional[datetime.date] = None
    name: Optional[str] = None
    absent: bool = False
    generic: bool = False

    @property
    def context_factor_names(self) -> Tuple[Optional[Entity]]:
        return ("filer",)

    def _equal_if_concrete(self, other: "Pleading") -> bool:
        if self.date != other.date:
            return False
        return super()._equal_if_concrete(other)

    def __eq__(self, other: Factor) -> bool:
        return super.__eq__(other)

    def _implies_if_concrete(self, other: "Pleading"):
        # TODO: allow the same kind of comparisons as Predicate.quantity
        if self.date != other.date:
            return False
        return super()._implies_if_concrete(other)

    def __str__(self):
        string = (
            f'{("filed by " + str(self.filer) if self.filer else "")}'
            + f'{("received on " + str(self.date)) if self.date else ""}'
        )
        return super().__str__().format(string)


@dataclass(frozen=True)
class Allegation(Factor):
    """
    A formal assertion of a Fact, included by a party in a Pleading
    to establish a cause of action.
    """

    to_effect: Optional[Fact] = None
    pleading: Optional[Pleading] = None
    name: Optional[str] = None
    absent: bool = False
    generic: bool = False

    @property
    def context_factor_names(self) -> Tuple[str, ...]:
        return ("to_effect", "pleading")

    def __eq__(self, other: Factor) -> bool:
        """
        dataclass behaves confusingly if this isn't included.
        """
        return super().__eq__(other)

    def __str__(self):
        string = (
            f'{("in " + str(self.pleading) + ",") if self.pleading else ""}'
            + f'{("claiming " + str(self.to_effect) + ",") if self.to_effect else ""}'
        )
        string = string.strip(",")
        return super().__str__().format(string)


@dataclass(frozen=True)
class Exhibit(Factor):
    """A source of information for use in litigation.

    "derived_from" and and "offered_by" parameters were removed
    because the former is probably better represented as a Fact,
    and the latter as a Motion.

    Allowed inputs for "form" will need to be limited.
    """

    form: Optional[str] = None
    statement: Optional[Fact] = None
    stated_by: Optional[Entity] = None
    name: Optional[str] = None
    absent: bool = False
    generic: bool = False

    @property
    def context_factor_names(self) -> Tuple[str, ...]:
        return ("statement", "stated_by")

    def _equal_if_concrete(self, other: "Pleading") -> bool:
        if self.form != other.form:
            return False
        return super()._equal_if_concrete(other)

    def __eq__(self, other: Factor) -> bool:
        return super().__eq__(other)

    def _implies_if_concrete(self, other: "Exhibit"):

        if not (self.form == other.form or other.form is None):
            return False

        return super()._implies_if_concrete(other)

    def __str__(self):
        string = (
            f'{("by " + str(self.stated_by) + ", ") if self.stated_by else ""}'
            + f'{("asserting " + str(self.statement)) if self.statement else ""}'
        )
        string = super().__str__().format(string)
        return string.replace("exhibit", self.form or "exhibit").strip()


@dataclass(frozen=True)
class Evidence(Factor):
    """An Exhibit that has been admitted by the court to aid a
    factual determination."""

    exhibit: Optional[Exhibit] = None
    to_effect: Optional[Fact] = None
    name: Optional[str] = None
    absent: bool = False
    generic: bool = False

    def __str__(self):
        string = (
            f'{("of " + str(self.exhibit)) + ", " if self.exhibit else ""}'
            + f'{("which supports " + str(self.to_effect)) if self.to_effect else ""}'
        )
        return super().__str__().format(string).strip()

    def __eq__(self, other: Factor) -> bool:
        return super().__eq__(other)

    @property
    def context_factor_names(self) -> Tuple[str, ...]:
        return ("exhibit", "to_effect")


def compare_dict_for_identical_entries(
    left: Dict[Factor, Factor], right: Dict[Factor, Factor]
) -> bool:
    """Compares two dicts to see whether the
    keys and values of one are the same objects
    as the keys and values of the other, not just
    whether they evaluate equal."""

    return all(
        any((l_key is r_key and left[l_key] is right[r_key]) for r_key in right)
        for l_key in left
    )
