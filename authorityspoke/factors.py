""":class:`Factor`\s, or inputs and outputs of legal :class:`.Rule`\s."""

from __future__ import annotations

import datetime
import functools
import logging
import operator
import re

from abc import ABC

from typing import Any, Callable, ClassVar, Dict, Iterable, Iterator, List
from typing import Optional, Sequence, Set, Tuple, Type, Union

from dataclasses import astuple, dataclass

from authorityspoke.context import log_mentioned_context, new_context_helper
from authorityspoke.predicates import Predicate
from authorityspoke.relations import Analogy

@dataclass(frozen=True)
class Factor(ABC):
    """
    Things relevant to a :class:`.Court`\'s application of a :class:`.Rule`.

    The same :class:`Factor` that is in the ``outputs`` for the
    :class:`.Procedure` of one legal :class:`.Rule` might be in the
    ``inputs`` of the :class:`.Procedure` for another.
    """

    @classmethod
    def all_subclasses(cls) -> Set[Type]:
        """
        Get all subclasses of :class:`Factor`.

        :returns:
            the set of all subclasses of :class:`Factor`
        """
        return set(cls.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in c.all_subclasses()]
        )

    @classmethod
    @functools.lru_cache()
    def class_from_str(cls, name: str):
        """
        Find class for use in JSON deserialization process.

        Obtains a classname of a :class:`Factor`
        subclass from a string, checking first
        in the ``lru_cache`` of known subclasses.

        :param name: name of the desired subclass.

        :returns: the Class named ``name``.
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
        return cls(**new_factor_dict)

    @classmethod
    @log_mentioned_context
    def from_dict(
        cls, factor_record: Dict, mentioned: List[Factor], regime: Optional["Regime"] = None, *args, **kwargs
    ) -> Optional[Factor]:
        """
        Turn fields from a chunk of JSON into a :class:`Factor` object.

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
    def interchangeable_factors(self) -> List[Dict[Factor, Factor]]:
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
    def generic_factors(self) -> List[Optional[Factor]]:
        """
        :class:`.Factor`\s that can be replaced without changing ``self``\s meaning.

        :returns:
            a :class:`dict` with self's generic :class:`.Factor`\s
            as keys and ``None`` as values, so that the keys can
            be matched to another object's ``generic_factors``
            to perform an equality test.
        """

        if self.generic:
            return [self]
        return list(
            {
                generic: None
                for factor in self.context_factors
                for generic in factor.generic_factors
            }
        )

    @property
    def context_factors(self) -> Tuple:
        """
        Get :class:`Factor`\s used in comparisons with other :class:`Factor`\s.

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
        Collect ``self``'s :attr:`context_factors`, and each of their :attr:`context_factors`, recursively.

        :returns:
            a :class:`dict` (instead of a :class:`set`,
            to preserve order) of :class:`Factor`\s.
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
        Find whether ``self`` and ``other`` can fit the relationship ``comparison``.

        :returns:
            a bool indicating whether there's at least one way to
            match the :attr:`context_factors` of ``self`` and ``other``,
            such that they fit the relationship ``comparison``.
        """

        context_registers = iter(self._context_registers(other, comparison))
        return any(register is not None for register in context_registers)

    def _context_registers(
        self, other: Factor, comparison: Callable
    ) -> Iterator[Dict[Factor, Factor]]:
        """
        Search for ways to match :attr:`context_factors` of ``self`` and ``other``.

        :yields:
            all valid ways to make matches between
            corresponding :class:`Factor`\s.
        """

        if other is None:
            yield {}
        elif self.generic or other.generic:
            yield {self: other, other: self}
        else:
            relation = Analogy(self.context_factors, other.context_factors, comparison)
            for register in relation.ordered_comparison():
                yield register

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
        new_dict = self.__dict__.copy()
        for key in changes:
            new_dict[key] = changes[key]
        return self.__class__(**new_dict)

    def means(self, other) -> bool:
        """
        Test whether ``self`` and ``other`` have identical meanings.

        :returns:
            whether ``other`` is another :class:`Factor`
            with the same meaning as ``self``. Not the same as an
            equality comparison with the ``==`` symbol, which simply
            converts ``self``'s and ``other``'s fields to tuples
            and compares them.
        """
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
            if not self_factor.means(other.context_factors[i]):
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

    def __ge__(self, other: Factor) -> bool:
        """Test whether ``self`` implies ``other``."""
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
        """Test whether ``self`` implies ``other`` and ``self`` != ``other``."""
        return self >= other and self != other

    def implies(self, other: Factor) -> bool:
        """
        Call :meth:`__ge__` as an alias.

        :returns:
            bool indicating whether ``self`` implies ``other``
        """
        return self >= other

    def _implies_if_concrete(self, other: Factor) -> bool:
        """
        Find if ``self`` would imply ``other`` if they aren't absent or generic.

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
    def new_context(self, changes: Dict[Factor, Factor]) -> Factor:
        """
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
        new_dict = self.__dict__.copy()
        for name in self.context_factor_names:
            new_dict[name] = self.__dict__[name].new_context(changes)
        return self.__class__(**new_dict)

    def _registers_for_interchangeable_context(
        self, matches: Dict[Factor, Factor]
    ) -> Iterator[Dict[Factor, Factor]]:
        """
        Find possible combination of interchangeable :attr:`context_factors`.

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

    @staticmethod
    def _import_to_mapping(
        self_mapping: Dict[Factor, Factor], incoming_mapping: Dict[Factor, Factor]
    ) -> Optional[Dict[Factor, Factor]]:
        """
        Compare :class:`Factor`\s to test if two sets of matches can be merged.

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

    def update_context_register(
        self, other: Factor, register: Dict[Factor, Factor], comparison: Callable
    ):
        """
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
            raise TypeError(f"{other} is type {other.__class__.__name__}, not Factor")
        for incoming_register in self._context_registers(other, comparison):
            for new_register_variation in self._registers_for_interchangeable_context(
                incoming_register
            ):
                yield self._import_to_mapping(register, new_register_variation)

    @staticmethod
    def _wrap_with_tuple(item):
        if isinstance(item, Iterable):
            return tuple(item)
        return (item,)


@dataclass(frozen=True)
class Fact(Factor):
    """
    An assertion accepted as factual by a court.

    Often based on factfinding by a judge or jury.

    :param predicate:
        a natural-language clause with zero or more slots
        to insert ``context_factors`` that are typically the
        subject and objects of the clause.

    :param context_factors:
        a series of :class:`Factor` objects that fill in
        the blank spaces in the ``predicate`` statement.

    :param name:
        an identifier for this object, often used if the object needs
        to be referred to multiple times in the process of composing
        other :class:`Factor` objects.

    :param standard_of_proof:
        a descriptor for the degree of certainty associated
        with the assertion in the ``predicate``.

    :param absent:
        whether the absence, rather than the presence, of the legal
        fact described above is being asserted.

    :param generic:
        whether this object could be replaced by another generic
        object of the same class without changing the truth of the
        :class:`Rule` in which it is mentioned.

    :param case_factors:
        a series of :class:`Factor`\s that have already been mentioned
        in the :class:`.Opinion`. They are available for composing the
        new :class:`Factor` object and don't need to be recreated.

    :attr standards_of_proof:
        a tuple with every allowable name for a standard of
        proof, in order from weakest to strongest.

        .. note:
            If any courts anywhere in a legal regime disagree about the
            relative strength of the various standards of proof, or if
            any court considers the order context-specific, then this
            approach of hard-coding their names and order will have to change.
    """

    predicate: Optional[Predicate] = None
    context_factors: Tuple[Factor, ...] = ()
    name: Optional[str] = None
    standard_of_proof: Optional[str] = None
    absent: bool = False
    generic: bool = False
    case_factors: Tuple[Factor, ...] = ()
    standards_of_proof: ClassVar = (
            "scintilla of evidence",
            "substantial evidence",
            "preponderance of evidence",
            "clear and convincing",
            "beyond reasonable doubt",
        )


    def __post_init__(self):

        if (
            self.standard_of_proof
            and self.standard_of_proof not in self.standards_of_proof
        ):
            raise ValueError(
                f"standard of proof must be one of {self.standards_of_proof} or None."
            )
        case_factors = self.__class__._wrap_with_tuple(self.case_factors)
        if not self.context_factors:
            context_factors = range(len(self.predicate))
        else:
            context_factors = self.__class__._wrap_with_tuple(self.context_factors)
        object.__delattr__(self, "case_factors")

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
    def from_string(
        cls, content: str, truth: Optional[bool] = True, reciprocal: bool = False
    ) -> Fact:
        """
        Make :class:`Fact` with context :class:`.Entity` objects from a :py:class:`str`.

        This method for constructing :class:`Predicate` objects
        from strings may rarely be used because it's an alternative to
        :meth:`.Factor.from_dict`. This function identifies context
        factors by finding brackets around them, while
        :meth:`~.Factor.from_dict` depends on knowing the names of the
        context factors in advance.

        :param content:
            a string containing a clause making an assertion.
            Differs from the ``content`` parameter in
            the :meth:`__init__` method because the curly brackets
            surround the names of :class:`.Entity` context factors,
            and because the ``comparison`` and ``quantity`` are
            represented in the ``content`` string rather than as
            separate parameters.

        :param truth:
            indicates whether the clause in ``content`` is asserted to be
            true or false. ``None`` indicates an assertion as to "whether"
            the clause is true or false, without specifying which.

        :param reciprocal:
            if True, then the order of the first two entities
            is considered interchangeable. There's no way to make
            any entities interchangeable other than the first two.

        :returns:
            a :class:`Predicate` and :class:`.Entity` objects
            from a string that has curly brackets around the
            context factors and the comparison/quantity.
        """

        comparison = None
        quantity = None
        pattern = r"\{([^\{]+)\}"

        entities_as_text = re.findall(pattern, content)
        for c in Predicate.opposite_comparisons:
            if entities_as_text[-1].startswith(c):
                comparison = c
                quantity = entities_as_text.pop(-1)
                quantity = quantity[2:].strip()
                quantity = Predicate.str_to_quantity(quantity)

        entities = [Entity(name=entity) for entity in entities_as_text]

        return Fact(predicate=Predicate(
                content=re.sub(pattern, "{}", content),
                truth=truth,
                reciprocal=reciprocal,
                comparison=comparison,
                quantity=quantity,
            ),
            context_factors=entities,
        )

    @property
    def interchangeable_factors(self) -> List[Dict[Factor, Factor]]:
        """
        Get ways to reorder context :class:`Factor`\s without changing truth value of ``self``.

        Each :class:`dict` returned has :class:`Factor`\s to replace as keys,
        and :class:`Factor`\s to replace them with as values.
        If there's more than one way to rearrange the context factors,
        more than one :class:`dict` should be returned.

        Currently the predicate must be phrased either in a way that
        doesn't make any context factors interchangeable, or if the
        ``reciprocal`` flag is set, in a way that allows only the
        first two context factors to switch places.

        :returns:
            the ways the context factors referenced by the
            :class:`Factor` object can be reordered without changing
            the truth value of the :class:`Factor`.

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
            not self.predicate.means(other.predicate)
            or self.standard_of_proof != other.standard_of_proof
        ):
            return False
        return super()._equal_if_concrete(other)

    def predicate_in_context(self, entities: Sequence[Factor]) -> str:
        """
        Insert :class:`str` representations of ``entities`` into ``self``\s :class:`Predicate`.

        :returns:
            the representation of ``self``\s :class:`Predicate` with
            :class:`str` representations of ``entities`` added into
            the slots, with added text from the :class:`Fact` object
            indicating the class name and whether the :class:`Predicate`
            is ``absent``.
        """

        return (
            f"{'Absent ' if self.absent else ''}{self.__class__.__name__}: "
            + f"{self.predicate.content_with_entities(entities)}"
        )

    def __len__(self):
        return len(self.context_factors)

    def _implies_if_concrete(self, other: Factor) -> bool:
        """
        Test if ``self`` impliess ``other``, assuming they are not ``generic``.

        :returns:
            whether ``self`` implies ``other`` under the given assumption.
        """
        if bool(self.standard_of_proof) != bool(other.standard_of_proof):
            return False

        if self.standard_of_proof and self.standards_of_proof.index(
            self.standard_of_proof
        ) < self.standards_of_proof.index(other.standard_of_proof):
            return False

        if not self.predicate >= other.predicate:
            return False
        return super()._implies_if_concrete(other)

    def _contradicts_if_present(self, other: Fact) -> bool:
        """
        Test if ``self`` contradicts ``other``, assuming they are not ``absent``.

        :returns:
            whether ``self`` and ``other`` can't both be true at
            the same time under the given assumption.
        """
        if (self.predicate.contradicts(other.predicate) and not other.absent) or (
            self.predicate >= other.predicate and other.absent
        ):
            return self.consistent_with(other, operator.ge)
        return False

    def _contradicts_if_factor(self, other: Factor) -> bool:
        """
        Test if ``self`` contradicts ``other``, assuming they are both :class:`Factor`\s.

        :returns:
            whether ``self`` and ``other`` can't both be true at
            the same time under the given assumption.
        """

        if not isinstance(other, self.__class__):
            return False

        if self.absent:
            return other._contradicts_if_present(self)
        return self._contradicts_if_present(other)

    @classmethod
    def _build_from_dict(
        cls, fact_dict: Dict[str, Union[str, bool]], mentioned: List[Factor]
    ) -> Optional[Fact]:
        """
        Construct and return a :class:`Fact` object from a :py:class:`dict`.

        :param fact_dict:
            imported from a JSON file in the format used in the "input" folder.

        :param mentioned:
            a list of :class:`.Factor`\s that may be included by reference to their ``name``\s.

        :returns:
            a :class:`Fact`.
        """

        placeholder = "{}"  # to be replaced in the Fact's string method

        def add_content_references(
            content: str, mentioned: List[Factor], placeholder: str
        ) -> Tuple[str, List[Factor]]:
            """
            Get context :class:`Factor`\s for new :class:`Fact`.

            :param content:
                the content for the :class:`Fact`\'s :class:`Predicate`.

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
            content, context_factors = add_content_references(
                content, mentioned, placeholder
            )
        for item in Predicate.opposite_comparisons:
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

        return cls(
            predicate,
            context_factors,
            name=fact_dict.get("name", None),
            standard_of_proof=fact_dict.get("standard_of_proof", None),
            absent=fact_dict.get("absent", False),
            generic=fact_dict.get("generic", False),
        )

    @new_context_helper
    def new_context(self, changes: Dict[Factor, Factor]) -> Factor:
        """
        Create new :class:`Factor`, replacing keys of ``changes`` with values.

        :returns:
            a version of ``self`` with the new context.
        """
        return self.evolve(
            {
                "context_factors": [
                    factor.new_context(changes) for factor in self.context_factors
                ]
            }
        )


@dataclass(frozen=True)
class Pleading(Factor):
    """A document filed by a party to make :class:`Allegation`\s."""

    filer: Optional["Entity"] = None
    name: Optional[str] = None
    absent: bool = False
    generic: bool = False
    context_factor_names: ClassVar = ("filer",)

    def __str__(self):
        string = f'{("filed by " + str(self.filer) if self.filer else "")}'
        return super().__str__().format(string)


@dataclass(frozen=True)
class Allegation(Factor):
    """
    A formal assertion of a :class:`Fact`.

    May be included by a party in a :class:`Pleading`
    to establish a cause of action.
    """

    to_effect: Optional[Fact] = None
    pleading: Optional[Pleading] = None
    name: Optional[str] = None
    absent: bool = False
    generic: bool = False
    context_factor_names: ClassVar = ("to_effect", "pleading")

    def __str__(self):
        string = (
            f'{("in " + str(self.pleading) + ",") if self.pleading else ""}'
            + f'{("claiming " + str(self.to_effect) + ",") if self.to_effect else ""}'
        )
        string = string.strip(",")
        return super().__str__().format(string)


@dataclass(frozen=True)
class Exhibit(Factor):
    """
    A source of information for use in litigation.

    .. note
        "Derived_from" and "offered_by" parameters were removed
        because the former is probably better represented as a :class:`Fact`,
        and the latter as a :class:`Motion`.

    TODO: Allowed inputs for ``form`` will need to be limited.
    """

    form: Optional[str] = None
    statement: Optional[Fact] = None
    stated_by: Optional[Entity] = None
    name: Optional[str] = None
    absent: bool = False
    generic: bool = False
    context_factor_names: ClassVar = ("statement", "stated_by")

    def _equal_if_concrete(self, other: Exhibit) -> bool:
        if self.form != other.form:
            return False
        return super()._equal_if_concrete(other)

    def _implies_if_concrete(self, other: Exhibit):

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
    """An :class:`Exhibit` admitted by a court to aid a factual determination."""

    exhibit: Optional[Exhibit] = None
    to_effect: Optional[Fact] = None
    name: Optional[str] = None
    absent: bool = False
    generic: bool = False
    context_factor_names: ClassVar = ("exhibit", "to_effect")

    def __str__(self):
        string = (
            f'{("of " + str(self.exhibit)) + ", " if self.exhibit else ""}'
            + f'{("which supports " + str(self.to_effect)) if self.to_effect else ""}'
        )
        return super().__str__().format(string).strip()


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
    """
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
        if not isinstance(self, other.__class__):
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
    ) -> Iterator[Dict[Factor, Factor]]:
        """
        Find how ``self``\'s context of can be mapped onto ``other``\'s.

        :yields:
            the only possible way the context of one ``Entity`` can be
            mapped onto the context of another.
        """
        # If there was a way to compare an Entity to None, should it return {}?
        if comparison(self, other):
            yield {self: other, other: self}

    def contradicts(self, other: Factor) -> bool:
        """
        Test whether ``self`` contradicts the ``other`` :class:`Factor`.

        :returns:
            ``False``, because an :class:`Entity` contradicts no other :class:`Factor`.
        """
        if not isinstance(other, Factor):
            raise TypeError(
                f"'Contradicts' not supported between class "
                + f"{self.__class__.__name__} and class {other.__class__.__name__}."
            )
        return False

    @new_context_helper
    def new_context(self, changes: Dict[Factor, Factor]) -> Entity:
        """
        Create new :class:`Factor`, replacing keys of ``changes`` with values.

        Assumes no changes are possible because the :func:`new_context_helper`
        decorator would have replaced ``self`` if any replacement was available.
        """
        return self
