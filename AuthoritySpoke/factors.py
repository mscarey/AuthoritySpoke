import datetime
import functools
import logging
import operator
import re

from typing import Callable, Dict, List, Set, Tuple
from typing import Iterable, Iterator, Mapping
from typing import Optional, Sequence, Type, Union

from pint import UnitRegistry

from authorityspoke.context import log_mentioned_context
from authorityspoke.enactments import Enactment

from dataclasses import astuple, dataclass, field

ureg = UnitRegistry()
Q_ = ureg.Quantity


OPPOSITE_COMPARISONS = {
    ">=": "<",
    "==": "!=",
    "<>": "=",
    "<=": ">",
    "=": "!=",
    ">": "<=",
    "<": ">=",
}


@dataclass(frozen=True)
class Factor:
    """A factor is something used to determine the applicability of a legal
    procedure. Factors can be both inputs and outputs of legal procedures.
    In a chain of legal procedures, the outputs of one may become inputs for
    another. Common types of factors include Facts, Evidence, Allegations,
    Motions, and Arguments."""

    @classmethod
    def all_subclasses(cls):
        """
        The set of subclasses available could change if the user imports
        more classes after calling the method once.
        """
        return set(cls.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in c.all_subclasses()]
        )

    @classmethod
    @functools.lru_cache()
    def class_from_str(cls, name: str):
        """
        Part of the JSON deserialization process. Obtains a classname
        of a Factor subclass from a string, checking first in the lru_cache
        of known subclasses.
        """
        name = name.capitalize()
        class_options = {
            class_obj.__name__: class_obj for class_obj in cls.all_subclasses()
        }
        answer = class_options.get(name)
        if answer is None:
            raise ValueError(
                f'"type" value in input must be one of {class_options}, not {name}'
            )
        return answer

    @classmethod
    def _build_from_dict(
        cls, factor_dict: Dict, mentioned: List[Union["Factor"]]
    ) -> "Factor":
        example = cls()
        new_factor_dict = example.__dict__
        for attr in new_factor_dict:
            if attr in example.context_factor_names:
                value, mentioned = Factor.from_dict(factor_dict.get(attr), mentioned)
            else:
                value = factor_dict.get(attr)
            if value is not None:
                new_factor_dict[attr] = value
        return (cls(**new_factor_dict), mentioned)

    @classmethod
    @log_mentioned_context
    def from_dict(
        cls, factor_record: Dict, mentioned: List["Factor"]
    ) -> Optional["Factor"]:
        """
        Turns a dict recently created from a chunk of JSON into a Factor object.
        """
        cname = factor_record["type"]
        target_class = cls.class_from_str(cname)
        return target_class._build_from_dict(factor_record, mentioned)

    @property
    def generic_factors(self) -> Dict["Factor", None]:
        """Returns an iterable of self's generic Factors,
        which must be matched to other generic Factors to
        perform equality tests between Factors."""

        if self.generic:
            return {self: None}
        return {
            generic: None
            for factor in self.context_factors
            for generic in factor.generic_factors
        }

    def implies_if_present(self, other: "Factor"):
        """
        Determines whether self would imply other, under
        the assumption that neither self nor other is an
        "absent" Factor.
        """

        if isinstance(other, self.__class__):
            if other.generic:
                return True
            if self.generic:
                return False
            return bool(self.implies_if_concrete(other))
        return False

    def any_context_register(self, other: "Factor", comparison: Callable) -> bool:
        """
        Returns a bool indicating whether there's at least one way to
        match the generic context factors of self and other, such that they
        fit the relationship "comparison".
        """

        context_registers = iter(self.context_register(other, operator.ge))
        return any(register is not None for register in context_registers)

    def implies_if_concrete(self, other: "Factor") -> bool:
        """
        Determines whether self would imply other, under the assumptions
        that neither self nor other has the attribute absent, neither
        has the attribute generic, and other is an instance of self's class.
        """

        for i, self_factor in enumerate(self.context_factors):
            if other.context_factors[i]:
                if not (self_factor and self_factor >= other.context_factors[i]):
                    return False
        return self.any_context_register(other, operator.ge)

    def equal_if_concrete(self, other: "Factor") -> bool:
        """
        Determines whether self would imply other, under the assumptions
        that neither self nor other has the attribute absent, neither
        has the attribute generic, and other is an instance of self's class.

        Most subclasses will inject their own tests before calling this.
        """
        for i, self_factor in enumerate(self.context_factors):
            if self_factor != other.context_factors[i]:
                return False

        return self.any_context_register(other, operator.eq)

    def __eq__(self, other) -> bool:
        if self.__class__ != other.__class__:
            return False

        if self.absent != other.absent:
            return False

        if self.generic == other.generic == True:
            return True

        if self.generic != other.generic:
            return False

        return self.equal_if_concrete(other)

    def contradicts_if_factor(self, other: "Factor") -> bool:
        return self >= other.make_absent()

    def contradicts(self, other: Optional["Factor"]) -> bool:
        """Returns True if self and other can't both be true at the same time.
        Otherwise returns False."""

        if other is None:
            return False
        if not isinstance(other, Factor):
            raise TypeError(
                f"{self.__class__} objects may only be compared for "
                + "contradiction with other Factor objects or None."
            )
        return self.contradicts_if_factor(other)

    def __ge__(self, other: "Factor") -> bool:
        if other is None:
            return True

        if not isinstance(other, Factor):
            raise TypeError(
                f"{self.__class__} objects may only be compared for "
                + "implication with other Factor objects or None."
            )
        if self.absent and other.__dict__.get("absent"):
            return bool(other.implies_if_present(self))

        if not self.absent and not other.__dict__.get("absent"):
            return bool(self.implies_if_present(other))

        return False

    def __gt__(self, other: Optional["Factor"]) -> bool:
        return self >= other and self != other

    def make_absent(self) -> "Factor":
        """Returns a new object the same as self except with the
        opposite value for 'absent'"""

        new_attrs = self.__dict__.copy()
        if new_attrs.get("absent") is not None:
            new_attrs["absent"] = not new_attrs["absent"]
        return self.__class__(**new_attrs)

    @property
    def context_factors(self) -> Tuple:

        return tuple(
            self.__dict__.get(factor_name) for factor_name in self.context_factor_names
        )

    @property
    def recursive_factors(self) -> Dict["Factor", None]:
        """
        Using dict instead of set to preserve order
        """
        answers: Dict[Factor, None] = {self: None}
        for context in filter(lambda x: x is not None, self.context_factors):
            if isinstance(context, Iterable):
                for item in context:
                    answers.update(item.recursive_factors)
            else:
                answers.update(context.recursive_factors)
        return answers

    def get_factor_by_name(self, name: str) -> Optional["Factor"]:
        for factor in self.recursive_factors:
            if factor.name == name:
                return factor
        return None

    @property
    def context_factor_names(self) -> Tuple[str, ...]:
        """
        This function and interchangeable_factors should be the only parts
        of the context-matching process that need to be unique for each
        subclass of Factor. It specifies what attributes of self and other
        to look in to find Factor objects to match.

        For Fact, it returns the context_factors, which can't contain None.
        Other classes will return a Tuple[Optional[Factor], ...]
        """

        return ()

    @property
    def interchangeable_factors(self) -> List[Dict["Factor", "Factor"]]:
        """
        Yields the ways the context factors referenced by the Factor object
        can be reordered without changing the truth value of the Factor.

        This is the default version for subclasses that don't have any
        interchangeable context factors.
        """
        return []

    def context_register(
        self, other: "Factor", comparison: Callable
    ) -> Iterator[Dict["Factor", "Factor"]]:
        """Searches through the context factors of self and other, making
        a list of dicts, where each dict is a valid way to make matches between
        corresponding factors. The dict is empty if there are no matches."""

        if other is None:
            yield {}
        elif self.generic or other.generic:
            yield {self: other, other: self}
        else:
            for registry in self.update_mapping(
                {}, self.context_factors, other.context_factors, comparison
            ):
                yield registry

    def registers_for_interchangeable_context(
        self, matches: Dict["Factor", "Factor"]
    ) -> Iterator[Dict["Factor", "Factor"]]:
        """
        Returns context registers with every possible combination of
        self and other's interchangeable context factors.
        """

        def replace_factors_in_dict(
            matches: Dict["Factor", "Factor"],
            replacement_dict: Dict["Factor", "Factor"],
        ):
            values = matches.values()
            keys = [replacement_dict.get(factor) or factor for factor in matches.keys()]
            return dict(zip(keys, values))

        yield matches
        already_returned: List[Dict["Factor", "Factor"]] = [matches]
        for replacement_dict in self.interchangeable_factors:
            changed_registry = replace_factors_in_dict(matches, replacement_dict)
            if not any(
                compare_dict_for_identical_entries(changed_registry, returned_dict)
                for returned_dict in already_returned
            ):
                already_returned.append(changed_registry)
                yield changed_registry

    @staticmethod
    def wrap_with_tuple(item):
        if isinstance(item, Iterable):
            return tuple(item)
        return (item,)

    @staticmethod
    def _import_to_mapping(
        self_mapping: Mapping["Factor", "Factor"],
        incoming_mapping: Dict["Factor", "Factor"],
    ) -> Optional[Mapping["Factor", "Factor"]]:
        """
        If the same factor in one mapping appears to match
        to two different factors in the other, the function
        return False. Otherwise it returns a merged dict of
        matches.

        This is a dict of implication relations.
        So the values need to be lists of Factors that the key implies.
        Need to start by changing the simple context_register function
        for Entity, to take into account the 'comparison' to see which way
        the implication goes.
        """
        logger = logging.getLogger("context_match_logger")
        self_mapping = dict(self_mapping)
        # The key-value relationship isn't symmetrical when the root Factors
        # are being compared for implication.
        for in_key, in_value in incoming_mapping.items():
            # The "if in_value" test prevents a failure when in_value is
            # None, but an "is" test returns False when in_value is
            # equal but not identical to self_mapping[in_key], while
            # equality incorrectly matches generically equal Factors
            # that don't refer to the same thing. Can this be
            # made a nonissue by making it impossible for duplicate
            # Factor objects to exist?

            # Resorting to comparing __repr__ for now. What will be
            # the correct behavior when testing for implication rather
            # than equality?
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

    def update_mapping(
        self,
        self_mapping_proxy: Mapping,
        self_factors: Tuple["Factor"],
        other_factors: Tuple["Factor"],
        comparison: Callable,
    ):
        """
        :param self_mapping_proxy: A view on a dict with keys representing
        factors in self and values representing factors in other. The keys
        and values have been found in corresponding positions in self and
        other.

        :param self_factors: factors from self that will be matched with
        other_factors. This function is expected to be called with various
        permutations of other_factors, but no other permutations of self_factors.

        :param other_factors: an ordering of factors from other.entity_orders

        :returns: a bool indicating whether the factors in other_factors can
        be matched to the tuple of factors in self_factors in
        self_matching_proxy, without making the same factor from other_factors
        match to two different factors in self_matching_proxy.
        """  # TODO: docstring

        new_mapping_choices = [self_mapping_proxy]

        self_factors = self.wrap_with_tuple(self_factors)
        other_factors = self.wrap_with_tuple(other_factors)

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
                        self_factors[index].context_register(
                            other_factors[index], comparison
                        )
                    )
                    for incoming_register in register_iter:
                        for transposed_register in self_factors[
                            index
                        ].registers_for_interchangeable_context(incoming_register):
                            updated_mapping = self._import_to_mapping(
                                mapping, transposed_register
                            )
                            if updated_mapping not in new_mapping_choices:
                                new_mapping_choices.append(updated_mapping)
        for choice in new_mapping_choices:
            yield choice


def new_context_helper(func: Callable):
    """
    Decorator for make_dict() methods of Factor subclasses, including Rule.
    """

    @functools.wraps(func)
    def wrapper(
        factor: Factor, context: Optional[Union[Sequence[Factor], Dict[Factor, Factor]]]
    ) -> Factor:

        if isinstance(context, Factor) or isinstance(context, str):
            context = context.wrap_with_tuple(context)
        if context is not None:
            if not isinstance(context, Iterable):
                raise TypeError('"context" must be a dict or Sequence')
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
            # BUG: needs an equality test, not an "in" test?
            for context_factor in context:
                if factor.name == context_factor or (
                    factor == context_factor and factor.name == context_factor.name
                ):
                    return context[context_factor]

        return func(factor, context)

    return wrapper


@dataclass(frozen=True)
class Predicate:
    """
    A statement about real events or about a legal conclusion.
    Predicates may be "alleged" by a pleading, "supported" by evidence, or
    "found" to be factual by a jury verdict or a judge's finding of fact.

    A predicate's self.content string shows where references to specific
    entities from the case can be used as subjects or objects of the predicate.

    If self.reciprocal is True, then the order of the first two entities will
    be considered interchangeable. There's no way to make any entities
    interchangeable other than the first two.

    A predicate can also end with a comparison to some quantity, as described
    by a ureg.Quantity object from the pint library. See pint.readthedocs.io.

    If a quantity is defined, a "comparison" should also be defined. That's
    a string indicating whether the thing described by the predicate is
    greater than, less than, or equal to the quantity. Even though "="
    is the default, it's the least useful, because courts almost always state
    rules that are intended to apply to quantities above or below some threshold.

    The quantity comparison can only be mentioned last. No entities may be
    mentioned after the quantity comparison is mentioned.
    """

    content: str
    truth: Optional[bool] = True
    reciprocal: bool = False
    comparison: Optional[str] = None
    quantity: Optional[Union[int, float, ureg.Quantity]] = None

    def __post_init__(self):

        normalize_comparison = {"==": "=", "!=": "<>"}
        if self.comparison in normalize_comparison:
            object.__setattr__(
                self, "comparison", normalize_comparison[self.comparison]
            )

        if self.comparison and self.comparison not in OPPOSITE_COMPARISONS.keys():
            raise ValueError(
                f'"comparison" string parameter must be one of {OPPOSITE_COMPARISONS.keys()}.'
            )

        if self.context_slots < 2 and self.reciprocal:
            raise ValueError(
                f'"reciprocal" flag not allowed because "{self.content}" has '
                f"{self.context_slots} spaces for context entities. At least 2 spaces needed."
            )

        if self.comparison and self.truth is False:
            object.__setattr__(self, "truth", True)
            object.__setattr__(
                self, "comparison", OPPOSITE_COMPARISONS[self.comparison]
            )

    @property
    def context_slots(self):
        slots = self.content.count("{}")
        if self.quantity:
            slots -= 1
        return slots

    @staticmethod
    def str_to_quantity(quantity: str) -> Union[float, int, ureg.Quantity]:
        quantity = quantity.strip()
        if quantity.isdigit():
            return int(quantity)
        float_parts = quantity.split(".")
        if len(float_parts) == 2 and all(
            substring.isnumeric() for substring in float_parts
        ):
            return float(quantity)
        return Q_(quantity)

    @classmethod
    def from_string(
        cls, content: str, truth: Optional[bool] = True, reciprocal: bool = False
    ) -> Tuple["Predicate", Tuple[Factor, ...]]:

        """Generates a Predicate object and Entities from a string that
        has curly brackets around the Entities and the comparison/quantity.
        Assumes the comparison/quantity can only come last.

        This may never be used because it's an alternative to
        Fact.from_dict(). This function identifies Entities
        by finding brackets around them, while Fact.from_dict()
        depends on knowing the names of the Entities in advance.
        """

        comparison = None
        quantity = None
        pattern = r"\{([^\{]+)\}"

        entities = re.findall(pattern, content)
        for c in OPPOSITE_COMPARISONS:
            if entities[-1].startswith(c):
                comparison = c
                quantity = entities.pop(-1)
                quantity = quantity[2:].strip()
                quantity = cls.str_to_quantity(quantity)

        return (
            Predicate(
                content=re.sub(pattern, "{}", content),
                truth=truth,
                reciprocal=reciprocal,
                comparison=comparison,
                quantity=quantity,
            ),
            tuple(entities),
        )

    def __len__(self):
        """
        Returns the number of entities that can fit in the pairs of brackets
        in the predicate. self.quantity doesn't count as one of these entities,
        even though the place where self.quantity goes in represented by brackets
        in the "content" string.

        Also called the linguistic valency, arity, or adicity.
        """

        return self.context_slots

    def __str__(self):
        if self.truth is None:
            truth_prefix = "whether "
        elif self.truth is False:
            truth_prefix = "it is false that "
        else:
            truth_prefix = ""
        if self.quantity:
            slots = ("{}" for slot in range(len(self)))
            content = self.content.format(*slots, self.quantity_comparison())
        else:
            content = self.content
        return f"{truth_prefix}{content}"

    def __eq__(self, other: "Predicate") -> bool:
        if not isinstance(other, self.__class__):
            return False

        if (
            self.content.lower() == other.content.lower()
            and self.reciprocal == other.reciprocal
            and self.quantity == other.quantity
        ):
            return self.truth == other.truth and self.comparison == other.comparison

    def __gt__(self, other: Optional["Predicate"]) -> bool:
        """Indicates whether self implies the other predicate,
        which is True if their statements about quantity imply it.
        Returns False if self and other are equal."""

        if other is None:
            return True
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"{self.__class__} objects may only be compared for "
                + f"implication with other {self.__class__} objects or None."
            )

        # Assumes no predicate implies another based on meaning of their content text
        if not (
            self.content.lower() == other.content.lower()
            and self.reciprocal == other.reciprocal
        ):
            return False

        if other.truth is None:
            return True

        if self.truth is None:
            return False

        if not (
            self.quantity and other.quantity and self.comparison and other.comparison
        ):
            return False

        if isinstance(self.quantity, ureg.Quantity) != (
            isinstance(other.quantity, ureg.Quantity)
        ):
            return False

        if (
            isinstance(self.quantity, ureg.Quantity)
            and self.quantity.dimensionality != other.quantity.dimensionality
        ):
            return False

        if "<" in self.comparison and (
            "<" in other.comparison or "=" in other.comparison
        ):
            if self.quantity < other.quantity:
                return True
        if ">" in self.comparison and (
            ">" in other.comparison or "=" in other.comparison
        ):
            if self.quantity > other.quantity:
                return True
        if "=" in self.comparison and "<" in other.comparison:
            if self.quantity < other.quantity:
                return True
        if "=" in self.comparison and ">" in other.comparison:
            if self.quantity > other.quantity:
                return True
        if "=" in self.comparison and "=" in other.comparison:
            if self.quantity == other.quantity:
                return True
        if "=" not in self.comparison and "=" not in other.comparison:
            if self.quantity == other.quantity:
                return True
        return False

    def __ge__(self, other: "Predicate") -> bool:
        if self == other:
            return True
        return self > other

    def contradicts(self, other: Optional["Predicate"]) -> bool:
        """This first tries to find a contradiction based on the relationship
        between the quantities in the predicates. If there are no quantities, it
        returns false only if the content is exactly the same and self.truth is
        different.
        """
        if other is None:
            return False

        if not isinstance(other, self.__class__):
            raise TypeError(
                f"{self.__class__} objects may only be compared for "
                + "contradiction with other {self.__class__} objects or None."
            )

        if (type(self.quantity) == ureg.Quantity) != (
            type(other.quantity) == ureg.Quantity
        ):
            return False

        if self.truth is None or other.truth is None:
            return False

        if (
            isinstance(self.quantity, ureg.Quantity)
            and self.quantity.dimensionality != other.quantity.dimensionality
        ):
            return False

        if not (
            self.content.lower() == other.content.lower()
            and self.reciprocal == other.reciprocal
        ):
            return False

        if self.quantity and other.quantity:
            if (
                ">" in self.comparison or "=" in self.comparison
            ) and "<" in other.comparison:
                if self.quantity > other.quantity:
                    return True
            if (
                "<" in self.comparison or "=" in self.comparison
            ) and ">" in other.comparison:
                if self.quantity < other.quantity:
                    return True
            if ">" in self.comparison and "=" in other.comparison:
                if self.quantity > other.quantity:
                    return True
            if "<" in self.comparison and "=" in other.comparison:
                if self.quantity < other.quantity:
                    return True
            if ("=" in self.comparison) != ("=" in other.comparison):
                if self.quantity == other.quantity:
                    return True
            return False
        return self.content == other.content and self.truth != other.truth

    def quantity_comparison(self) -> str:
        """String representation of a comparison with a quantity,
        which can include units due to the pint library."""

        if not self.quantity:
            return None
        comparison = self.comparison or "="
        expand = {
            "=": "exactly equal to",
            "!=": "not equal to",
            ">": "greater than",
            "<": "less than",
            ">=": "at least",
            "<=": "no more than",
        }
        return f"{expand[comparison]} {self.quantity}"

    def content_with_entities(self, entities: Union[Factor, Sequence[Factor]]) -> str:
        """Creates a sentence by substituting the names of entities
        from a particular case into the predicate_with_truth."""

        if isinstance(entities, Factor):
            entities = (entities,)
        if len(entities) != len(self):
            raise ValueError(
                f"Exactly {len(self)} entities needed to complete "
                + f'"{self.content}", but {len(entities)} were given.'
            )
        return str(self).format(*(str(e) for e in entities))

    def negated(self) -> "Predicate":
        """
        Returns a copy of the same Predicate, but with the opposite
        truth value.
        """

        return Predicate(
            content=self.content,
            truth=not self.truth,
            reciprocal=self.reciprocal,
            comparison=self.comparison,
            quantity=self.quantity,
        )


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
        case_factors = self.__class__.wrap_with_tuple(case_factors)
        context_factors = self.__class__.wrap_with_tuple(context_factors)

        if len(context_factors) != len(self.predicate):
            raise ValueError(
                "The number of items in 'context_factors' must be "
                + f"{len(self.predicate)}, to match predicate.context_slots"
            )
        if any(
            not isinstance(s, (Factor, int))
            for s in context_factors
        ):
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
        string = (
            f"{'the absence of the fact ' if self.absent else ''}"
            + f"{standard}{predicate}"
        )
        if self.generic:
            return f"<{string}>"
        return string

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

    def equal_if_concrete(self, other: Factor) -> bool:
        if (
            self.predicate != other.predicate
            or self.standard_of_proof != other.standard_of_proof
        ):
            return False
        return super().equal_if_concrete(other)

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

    def implies_if_concrete(self, other: Factor) -> bool:
        if bool(self.standard_of_proof) != bool(other.standard_of_proof):
            return False

        if self.standard_of_proof and self.standards_of_proof().index(
            self.standard_of_proof
        ) < self.standards_of_proof().index(other.standard_of_proof):
            return False

        if not self.predicate >= other.predicate:
            return False
        return super().implies_if_concrete(other)

    def contradicts_if_present(self, other: "Fact") -> bool:
        """
        Indicates whether self contradicts the Fact other under the assumption that
        self.absent == False.
        """
        if (self.predicate.contradicts(other.predicate) and not other.absent) or (
            self.predicate >= other.predicate and other.absent
        ):
            return self.any_context_register(other, operator.ge)
        return False

    def contradicts_if_factor(self, other: Factor) -> bool:
        """
        Returns True if self and other can't both be true at the same time.
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
        """Constructs and returns a Fact object from a dict imported from
        a JSON file in the format used in the "input" folder."""

        placeholder = "{}"  # to be replaced in the Fact's string method

        def add_content_references(
            content: str, mentioned: List[Factor], placeholder: str
        ) -> Tuple[str, List[Factor]]:
            """
            :param content: the content for the Fact's Predicate

            :param mentioned: list of Factors with names that could be
            referenced in content

            :param placeholder: a string to replace the names of
            referenced Factors in content

            :returns: the content string with any referenced Factors
            replaced by placeholder, and a list of referenced Factors
            in the order they appeared in content.
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
        for item in OPPOSITE_COMPARISONS:
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

    def context_register(
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
        return (self.filer,)

    def equal_if_concrete(self, other: "Pleading") -> bool:
        if self.date != other.date:
            return False
        return super().equal_if_concrete(other)

    def __eq__(self, other: Factor) -> bool:
        return super.__eq__(other)

    def implies_if_concrete(self, other: "Pleading"):

        if self.date != other.date:
            return False

        return super().implies_if_concrete(other)

    @new_context_helper
    def new_context(self, changes: Dict[Factor, Factor]) -> "Pleading":
        """
        Creates new Factor object, replacing keys of "changes" with their values.
        """
        filer = self.filer.new_context(changes) if self.filer else None
        return self.__class__(
            filer=filer,
            date=self.date,
            name=self.name,
            absent=self.absent,
            generic=self.generic,
        )

    def __str__(self):
        string = (
            f'{"absent " if self.absent else ""}{self.__class__.__name__}'
            + f'{(" filed by " + str(self.filer) if self.filer else "")}'
            + f'{(" on " + str(self.date)) if self.date else ""}'
        )
        if self.generic:
            string = f"<{string}>"
        return string


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

    @new_context_helper
    def new_context(self, changes: Dict[Factor, Factor]) -> "Allegation":
        """
        Creates new Allegation object, replacing keys of "changes" with their values.
        """
        to_effect = self.to_effect.new_context(changes) if self.to_effect else None
        pleading = self.pleading.new_context(changes) if self.pleading else None
        return Allegation(
            to_effect=to_effect,
            pleading=pleading,
            name=self.name,
            absent=self.absent,
            generic=self.generic,
        )

    def __str__(self):
        string = (
            f'{"absent " if self.absent else ""}an allegation '
            + f'{(" in " + str(self.pleading) + "," if self.pleading else "")}'
            + f'{("claiming " + str(self.to_effect)) + "," if self.to_effect else ""}'
        )
        string = string.strip(",")
        if self.generic:
            string = f"<{string}>"
        return string


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

    def equal_if_concrete(self, other: "Pleading") -> bool:
        if self.form != other.form:
            return False
        return super().equal_if_concrete(other)

    def __eq__(self, other: Factor) -> bool:
        return super().__eq__(other)

    def implies_if_concrete(self, other: "Exhibit"):

        if not (self.form == other.form or other.form is None):
            return False

        return super().implies_if_concrete(other)

    @new_context_helper
    def new_context(self, changes: Dict[Factor, Factor]) -> "Exhibit":
        """
        Creates new Exhibit object, replacing keys of "changes" with their values.
        """
        statement = self.statement.new_context(changes) if self.statement else None
        stated_by = self.stated_by.new_context(changes) if self.stated_by else None
        return Exhibit(
            form=self.form,
            statement=statement,
            stated_by=stated_by,
            name=self.name,
            absent=self.absent,
            generic=self.generic,
        )

    def __str__(self):
        string = (
            f'{"absent " if self.absent else ""}{self.form if self.form else "exhibit"}'
            + f'{(" by " + str(self.stated_by)) if self.stated_by else ""}'
            + f'{(", asserting " + str(self.statement)) if self.statement else ""}'
        )
        if self.generic:
            if self.name:
                string = self.name
            string = f"<{string}>"
        return string


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
        if self.exhibit:
            string = str(self.exhibit)
        else:
            string = self.__class__.__name__.lower()
        if self.absent:
            string = "the absence of " + string
        if self.to_effect:
            string += f", which supports {self.to_effect}"
        if self.generic:
            return f"<{string}>"
        return string

    def __eq__(self, other: Factor) -> bool:
        return super().__eq__(other)

    @property
    def context_factor_names(self) -> Tuple[str, ...]:
        return ("exhibit", "to_effect")

    @new_context_helper
    def new_context(self, changes: Dict[Factor, Factor]) -> "Evidence":
        """
        Creates new Evidence object, replacing keys of "changes" with their values.
        """
        exhibit = self.exhibit.new_context(changes) if self.exhibit else None
        to_effect = self.to_effect.new_context(changes) if self.to_effect else None
        return Evidence(
            exhibit=exhibit,
            to_effect=to_effect,
            name=self.name,
            absent=self.absent,
            generic=self.generic,
        )


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
