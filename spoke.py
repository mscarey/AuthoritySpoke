from functools import reduce
import itertools
import logging
import operator
import re

from types import MappingProxyType

from typing import Callable, Dict, List, Set, Tuple
from typing import Iterable, Iterator, Mapping
from typing import Optional, Sequence, Union

from pint import UnitRegistry

from dataclasses import dataclass


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


def compare_dict_for_identical_entries(left, right):
    """Compares two dicts to see whether the
    keys and values of one are the same objects
    as the keys and values of the other, not just
    whether they evaluate equal."""

    return all(
        any((l_key is r_key and left[l_key] is right[r_key]) for r_key in right)
        for l_key in left
    )


class Factor:
    """A factor is something used to determine the applicability of a legal
    procedure. Factors can be both inputs and outputs of legal procedures.
    In a chain of legal procedures, the outputs of one may become inputs for
    another. Common types of factors include Facts, Evidence, Allegations,
    Motions, and Arguments."""

    def __init__(
        self, name: Optional[str] = None, generic: bool = True, absent: bool = False
    ):
        self.name = name
        self.generic = generic
        self.absent = absent

    @classmethod
    def from_dict(cls, factor: dict) -> "Factor":
        """
        Turns a dict recently created from a chunk of JSON into a Factor object.
        """

        # TODO: make subclass search recursive, or make a different factory function
        class_options = cls.__subclasses__()
        for c in class_options:
            cname = factor.get("type", "")
            if cname.capitalize() == c.__name__:
                return c.from_dict(factor)
        raise ValueError(
            f'"type" value in input must be one of {class_options}, not {cname}'
        )

    def __eq__(self, other: "Factor") -> bool:
        if self.__class__ != other.__class__:
            return False
        if self.generic == other.generic == True:
            return True
        return self.__dict__ == other.__dict__

    def __gt__(self, other: "Factor") -> bool:
        if self == other:
            return False
        if isinstance(self, other.__class__):
            if other.generic:
                return True
        return False

    def __hash__(self):
        # TODO: make Factor a dataclass and get rid of this.
        return hash(
            self.__class__.__name__,
            *[v for v in self.__dict__.values() if not isinstance(v, set)],
        )

    def generic_factors(self) -> Iterable["Factor"]:
        """Returns an iterable of self's generic Factors,
        which must be matched to other generic Factors to
        perform equality tests between Factors."""

        if self.generic:
            yield self

    def make_absent(self) -> "Factor":
        """Returns a new object the same as self except with the
        opposite value for 'absent'"""

        new_attrs = self.__dict__.copy()
        new_attrs["absent"] = not new_attrs["absent"]
        return self.__class__(**new_attrs)

    def context_register(
        self, other: "Factor", comparison: Callable
    ) -> Iterator[Optional[Dict["Factor", "Factor"]]]:
        """Searches through the context factors of self and other, making
        a list of dicts, where each dict is a valid way to make matches between
        corresponding factors. The dict is empty if there are no matches."""

        if other is None:
            yield {}
        elif self.generic or other.generic:
            yield {self: other, other: self}
        else:
            for register in self._compare_factor_attributes(other, comparison):
                yield register

    @staticmethod
    def sort_in_tuple(item) -> Tuple["Factor", ...]:
        if isinstance(item, Iterable):
            return tuple(sorted(item, key=repr))
        return (item,)

    @classmethod
    def wrap_with_tuple(cls, item):
        if isinstance(item, Iterable):
            return tuple(item)
        return (item,)

    @staticmethod
    def _import_to_mapping(
        self_mapping: Mapping["Factor", "Factor"],
        incoming_mapping: Dict["Factor", "Factor"],
    ) -> Optional[Mapping["Factor", "Factor"]]:
        """If the same factor in one mapping appears to match
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

    def _update_mapping(
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
        # TODO: Find a way to skip this step and only use the
        # result of the incoming_registers process below
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
                        updated_mapping = self._import_to_mapping(
                            mapping, incoming_register
                        )
                        if updated_mapping not in new_mapping_choices:
                            new_mapping_choices.append(updated_mapping)
        for choice in new_mapping_choices:
            yield choice


@dataclass()
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
    context_slots: int = 0

    @classmethod
    def new(
        cls,
        content: str,
        truth: Optional[bool] = True,
        reciprocal: bool = False,
        comparison: Optional[str] = None,
        quantity: Optional[Union[int, float, ureg.Quantity]] = None,
    ):

        slots = content.count("{}")
        if quantity:
            slots -= 1

        if slots < 2 and reciprocal:
            raise ValueError(
                f'"reciprocal" flag not allowed because {content} has '
                f"{slots} spaces for context entities. At least 2 spaces needed."
            )
        # Assumes that the obverse of a statement about a quantity is
        # necessarily logically equivalent
        if comparison == "==":
            comparison = "="
        if comparison == "!=":
            comparison = "<>"
        if comparison and truth is False:
            truth = True
            comparison = OPPOSITE_COMPARISONS[comparison]
        if comparison and comparison not in OPPOSITE_COMPARISONS.keys():
            raise ValueError(
                f'"comparison" string parameter must be one of {OPPOSITE_COMPARISONS.keys()}.'
            )
        return Predicate(content, truth, reciprocal, comparison, quantity, slots)

    @staticmethod
    def from_string(
        content: str, truth: Optional[bool] = True, reciprocal: bool = False
    ) -> Tuple["Predicate", Tuple[Factor, ...]]:

        """Generates a Predicate object and Entities from a string that
        has curly brackets around the Entities and the comparison/quantity.
        Assumes the comparison/quantity can only come last."""

        comparison = None
        quantity = None
        pattern = r"\{([^\{]+)\}"

        entities = re.findall(pattern, content)
        for c in OPPOSITE_COMPARISONS:
            if entities[-1].startswith(c):
                comparison = c
                quantity = entities.pop(-1)
                quantity = quantity[2:].strip()
                if quantity.isdigit():
                    quantity = int(quantity)
                elif quantity.isdecimal():
                    quantity = float(quantity)
                else:
                    quantity = Q_(quantity)

        entities = (Factor(e) for e in entities)

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
            if self.truth == other.truth and self.comparison == other.comparison:
                return True  # Equal if everything is same
            if (
                self.comparison
                and OPPOSITE_COMPARISONS[self.comparison] == other.comparison
                and (
                    (self.truth == True and other.truth == False)
                    or (self.truth == False and other.truth == True)
                )
            ):
                # Equal if everything is same except obverse quantity statement.
                return True
        return False

    def __gt__(self, other: "Predicate") -> bool:
        """Indicates whether self implies the other predicate,
        which is True if their statements about quantity imply it.
        Returns False if self and other are equal."""

        if not isinstance(other, self.__class__):
            return False

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

    def __hash__(self):
        return hash(
            (
                self.__class__.__name__,
                *[
                    v
                    for v in self.__dict__.values()
                    if not isinstance(v, set) and not isinstance(v, list)
                ],
            )
        )

    def contradicts(self, other: "Predicate") -> bool:
        """This first tries to find a contradiction based on the relationship
        between the quantities in the predicates. If there are no quantities, it
        returns false only if the content is exactly the same and self.truth is
        different.
        """
        if not isinstance(other, self.__class__):
            return False

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
                "<" in self.comparison or "=" in self.comparison
            ) and "<" in other.comparison:
                if self.quantity > other.quantity:
                    return True
            if (
                ">" in self.comparison or "=" in self.comparison
            ) and ">" in other.comparison:
                if self.quantity < other.quantity:
                    return True
            if ">" in self.comparison and "=" in other.comparison:
                if self.quantity > other.quantity:
                    return True
            if "<" in self.comparison and "=" in other.comparison:
                if self.quantity < other.quantity:
                    return True
            if "=" in self.comparison and "=" not in other.comparison:
                if self.quantity == other.quantity:
                    return True
            if "=" not in self.comparison and "=" in other.comparison:
                if self.quantity != other.quantity:
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

    def content_with_entities(
        self, entities: Union[Factor, Sequence[Union[int, Factor]]]
    ) -> str:
        """Creates a sentence by substituting the names of entities
        from a particular case into the predicate_with_truth."""

        if isinstance(entities, Factor):
            entities = (entities,)
        if len(entities) != len(self):
            raise ValueError(
                f"Exactly {len(self)} entities needed to complete "
                + f'"{self.content}", but {len(entities)} were given.'
            )
        if any(isinstance(item, int) for item in entities):
            entities = [f"<{item}>" for item in entities]  # not reachable?
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


def check_entity_consistency(
    left: Factor, right: Factor, matches: Dict[Factor, Factor]
) -> Set[Tuple[Factor, ...]]:
    """
    Given entity assignments for self and other, determines whether
    the factors have consistent entity assignments such that both can
    be true at the same time.

    :param other:

    :param matches: a tuple the same length as len(self). The indices represent
    self's entity slots, and the value at each index represents other's
    corresponding entity slots that have already been assigned, if any.

    :returns: a set containing self's normal entity tuple, self's reciprocal
    entity tuple, both, or neither, depending on which ones match with other.
    """
    # TODO: update docstring

    def all_matches(self_order: Tuple[Factor], other_order: Tuple[Factor]) -> bool:
        """
        Determines whether the entity slots assigned so far are
        consistent for the Factors designated self and other,
        regardless of whether it's possible to make consistent
        assignments for the remaining slots.
        """
        m = dict(matches_proxy)
        for i, slot in enumerate(other_order):
            other_factor = m.get(slot, None)
            if other_factor is self_order[i] or other_factor is None:
                m[slot] = self_order[i]
            else:
                return False
        return m

    if not isinstance(right, Factor):
        raise TypeError(f"other must be type Factor")

    matches_proxy = MappingProxyType(matches)

    answers = []

    for self_order in left.entity_orders:
        for other_order in right.entity_orders:
            if all_matches(self_order, other_order) and all_matches(
                other_order, self_order
            ):
                answers.append(
                    [
                        all_matches(self_order, other_order),
                        all_matches(other_order, self_order),
                    ]
                )

    return answers


def find_matches(
    for_matching: Tuple[Factor],
    need_matches: Iterable[Factor],
    matches: Mapping[Factor, Optional[Factor]],
    comparison: Callable[[Factor, Factor], bool],
) -> Iterator[Mapping[Factor, Optional[Factor]]]:
    """
    Generator that recursively searches for a tuple of entity
    assignments that can cause all of 'need_matches' to satisfy
    the relation described by 'comparison' with a factor
    from for_matching.

    :param for_matching: A frozenset of all of self's factors. These
    factors aren't removed when they're matched to a factor from other,
    because it's possible that one factor in self could imply two
    different factors in other.

    :param need_matches: A set of factors from other that have
    not yet been matched to any factor from self.

    :param matches: A tuple showing which factors from
    for_matching have been matched.

    :param comparison: A function used to filter the for_matching
    factors into the "available" collection. A factor must have
    the "comparison" relation with the factor from the need_matches
    set to be included as "available".

    :returns: iterator that yields tuples of entity assignments that can
    cause all of 'need_matches' to satisfy the relation described by
    'comparison' with a factor from for_matching.
    """

    if not need_matches:
        yield matches
    else:
        need_matches = list(need_matches)
        n = need_matches.pop()
        available = [a for a in for_matching if comparison(a, n)]
        for a in available:
            matches_found = check_entity_consistency(n, a, matches)
            for source_list in matches_found:
                if comparison == operator.le:
                    matches_next = source_list[1]
                else:
                    matches_next = source_list[0]
                for m in find_matches(
                    for_matching,
                    tuple(need_matches),
                    MappingProxyType(matches_next),
                    comparison,
                ):
                    yield m


STANDARDS_OF_PROOF = {
    "scintilla of evidence": 1,
    "preponderance of evidence": 2,
    "clear and convincing": 3,
    "beyond reasonable doubt": 4,
}


@dataclass(frozen=True)
class Fact(Factor):
    """An assertion accepted as factual by a court, often through factfinding by
    a judge or jury."""

    # TODO: rename entity_context

    predicate: Optional[Predicate] = None
    entity_context: Tuple[Factor, ...] = ()
    standard_of_proof: Optional[str] = None
    absent: bool = False
    generic: bool = False

    @classmethod
    def new(
        cls,
        predicate: Optional[Predicate] = None,
        entity_context: Optional[
            Union[Factor, Iterable[Factor], int, Iterable[int]]
        ] = None,
        standard_of_proof: Optional[str] = None,
        absent: bool = False,
        generic: bool = False,
        case_factors: Union[Factor, Iterable[Factor]] = (),
    ):

        if not entity_context:
            entity_context = range(len(predicate))
        case_factors = cls.wrap_with_tuple(case_factors)
        entity_context = cls.wrap_with_tuple(entity_context)

        if len(entity_context) != len(predicate):
            raise ValueError(
                "The number of items in 'entity_context' must be "
                + f"{len(predicate)}, to match predicate.context_slots"
            )

        if any(not isinstance(s, Factor) for s in entity_context):
            if any(not isinstance(s, int) for s in entity_context):
                raise TypeError(
                    "entity_context parameter must contain all integers "
                    + "or all Factor objects."
                )
            if len(case_factors) >= max(entity_context):
                entity_context = tuple(case_factors[i] for i in entity_context)
            else:
                raise ValueError(
                    "Items in the entity_context parameter should "
                    + "be Factor or a subclass of Factor, or should be integer "
                    + "indices of Factor objects in the case_factors parameter."
                )

        if standard_of_proof and standard_of_proof not in STANDARDS_OF_PROOF:
            raise ValueError(
                f"standard of proof must be one of {STANDARDS_OF_PROOF.keys()} or None."
            )
        return cls(predicate, entity_context, standard_of_proof, absent, generic)

    def __str__(self):
        predicate = str(self.predicate.content_with_entities(self.entity_context))
        standard = (
            f" by the standard {self.standard_of_proof},"
            if self.standard_of_proof
            else ""
        )
        return (
            f"{'the absence of ' if self.absent else ''}the fact"
            + f"{standard} {predicate}"
        )

    def entity_orders(self):
        """
        Yields the ways the context factors referenced by the Fact object
        can be reordered without changing the truth value of the Fact.
        Currently the predicate must be phrased either in a way that doesn't
        make any context factors interchangeable, or if the "reciprocal" flag
        is set, in a way that allows only the first two context factors to switch
        places.
        """
        yield self.entity_context
        if self.predicate.reciprocal:
            yield (self.entity_context[1], self.entity_context[0]) + (
                self.entity_context[2:]
            )

    def _compare_factor_attributes(self, other, comparison):
        """
        This function should be the only part of the context-matching
        process that needs to be unique for each subclass of Factor.
        It specifies what attributes of self and other to look in to find
        Factor objects to match.

        For Fact, it creates zero or more updated mappings for each
        other_order in other.entity_orders. Each time, it starts with mapping,
        and updates it with matches from self.entity_context and other_order.
        """  # TODO: docstring

        already_returned = []
        self_orders = iter(self.entity_orders())
        for self_order in self_orders:
            other_orders = iter(other.entity_orders())
            for other_order in other_orders:
                updated_mappings = iter(
                    self._update_mapping({}, self_order, other_order, comparison)
                )
                for next_registry in updated_mappings:
                    if next_registry and next_registry not in already_returned:
                        already_returned.append(next_registry)
                        yield next_registry

    def __eq__(self, other: Factor) -> bool:
        if not isinstance(other, Factor):
            raise TypeError(
                f"{self.__class__} objects may only be compared for "
                + "equality with other Factor objects."
            )
        if self.__class__ != other.__class__:
            return False
        if self.generic == other.generic == True:
            return True
        if (
            self.predicate != other.predicate
            or self.standard_of_proof != other.standard_of_proof
            or self.absent != other.absent
            or self.generic != other.generic
        ):
            return False

        context_registers = iter(self.context_register(other, operator.eq))
        return any(register is not None for register in context_registers)

    def make_generic(self) -> "Fact":
        """
        This changes generic to True and calls make_generic recursively
        on all the Factors in entity_context. But it does preserve the
        predicate attribute. For a Fact with no features specified, use:

        Fact(generic=True)
        """
        new_context = tuple([f.make_generic() for f in self.entity_context])
        return Fact(
            predicate=self.predicate,
            entity_context=new_context,
            standard_of_proof=None,
            absent=self.absent,
            generic=True,
        )

    def generic_factors(self) -> Iterable[Factor]:
        """Returns an iterable of self's generic Factors,
        which must be matched to other generic Factors to
        perform equality tests between Factors."""

        if self.generic:
            yield self
        else:
            collected_factors = [
                generic
                for factor in self.entity_context
                for generic in factor.generic_factors()
            ]
            for output in set(collected_factors):
                yield output

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
        return len(self.entity_context)

    def __gt__(self, other: Optional[Factor]) -> bool:
        """Indicates whether self implies other, taking into account the implication
        test for predicates and whether self and other are labeled 'absent'"""

        if self == other:
            return False
        return self >= other

    def __ge__(self, other: Optional[Factor]) -> bool:
        if other is None:
            return True

        if not isinstance(other, Factor):
            raise TypeError(
                f"'Implies' not supported between instances of "
                + f"'{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )

        if not isinstance(self, other.__class__):
            return False

        if other.generic:
            return True

        if self.generic:
            return False

        if bool(self.standard_of_proof) != bool(other.standard_of_proof):
            return False

        if (
            self.standard_of_proof
            and STANDARDS_OF_PROOF[self.standard_of_proof]
            < STANDARDS_OF_PROOF[other.standard_of_proof]
        ):
            return False

        if not (self.predicate >= other.predicate and self.absent == other.absent):
            return False

        context_registers = iter(self.context_register(other, operator.ge))
        return any(register is not None for register in context_registers)

    def contradicts(self, other: Optional[Factor]) -> bool:
        """Returns True if self and other can't both be true at the same time.
        Otherwise returns False."""

        if other is None:
            return False

        if not isinstance(other, Factor):
            raise TypeError(
                f"'Contradicts' not supported between instances of "
                + f"'{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )

        if not isinstance(other, self.__class__):
            return False

        self_implies_other = iter(self.context_register(other, operator.ge))
        if any(register is not None for register in self_implies_other):
            if self.predicate.contradicts(other.predicate) and not (
                self.absent | other.absent
            ):
                return True
            if self.predicate >= other.predicate and other.absent and not self.absent:
                return True

        other_implies_self = iter(self.context_register(other, operator.le))
        if any(register is not None for register in other_implies_self):
            if self.predicate.contradicts(other.predicate) and not (
                self.absent | other.absent
            ):
                return True
            if other.predicate >= self.predicate and self.absent and not other.absent:
                return True
        return False

    def copy_with_foreign_context(self, context_assignment):
        # TODO: move to Factor class, handle inheritance
        new_context = tuple(
            [context_assignment.get(entity) for entity in self.entity_context]
        )
        return Fact(
            predicate=self.predicate,
            entity_context=new_context,
            standard_of_proof=self.standard_of_proof,
            absent=self.absent,
            generic=self.generic,
        )

    def consistent_entity_combinations(
        self, factors_from_other_procedure, matches
    ) -> List[Dict]:
        """Finds all possible entity marker combinations for self that
        don't result in a contradiction with any of the factors of
        other. The time to call this function
        repeatedly during a recursive search should explode
        as the possibilities increase, so it should only be run
        when matches has been narrowed as much as possible."""
        # TODO: docstring

        answer = []
        for source_list in self.entity_orders:
            available_slots = {
                factor: [
                    key
                    for key in matches
                    if key is not None
                    and (matches.get(key) is None or matches.get(key) == factor)
                ]
                for factor in source_list
            }
            keys, values = zip(*available_slots.items())
            combinations = (
                dict(zip(keys, v))
                for v in itertools.product(*values)
                if len(v) == len(set(v))
            )
            for context in combinations:
                if not any(
                    a.contradicts(self.copy_with_foreign_context(context))
                    for a in factors_from_other_procedure
                ):
                    if all(
                        not compare_dict_for_identical_entries(context, d)
                        for d in answer
                    ):
                        answer.append(context)
        return answer

    @classmethod
    def from_dict(cls, factor: Optional[dict]) -> Optional["Fact"]:
        if factor is None:
            return None
        if factor["type"].capitalize() != "Fact":
            raise ValueError(
                f'"type" value in input must be "fact", not {factor["type"]}'
            )
        predicate, entities = Predicate.from_string(
            content=factor.get("content"),
            truth=factor.get("truth", True),
            reciprocal=factor.get("reciprocal", False),
        )
        yield cls(
            predicate,
            entities,
            factor.get("absent", False),
            factor.get("standard_of_proof", None),
        )

        for entity in entities:
            yield entity

    def make_abstract(self, entity_slots: Iterable[Factor]) -> "Fact":
        """
        Creates a new Fact object, this time with numbered
        entity slots instead of actual entities. The indices of
        the Entities in entity_slots correspond to the numbers
        that will be assigned to the slots in the new object's
        self.entity_context.
        """

        if any(not isinstance(s, Factor) for s in entity_slots):
            raise TypeError(
                "entity_slots must be an interable containing only Factor objects."
            )
        if any(e not in entity_slots for e in self.entity_context):
            raise ValueError(
                f"Every entity in self.entity_context must be present in "
                + f"entity_slots, but {e} is missing."
            )
        slots = [entity_slots.index(e) for e in self.entity_context]
        return Fact(self.predicate, tuple(slots), self.absent, self.standard_of_proof)

    def new_context(
        self,
        entity_context: Union[Iterable[int], Iterable[Factor]],
        case_factors: Iterable[Factor] = (),
    ) -> "Fact":
        """
        Creates a new Fact object, replacing the old entity_context
        attribute with a new one.
        """
        if len(entity_context) != len(self.entity_context):
            raise ValueError(
                f"The number of entities should be equal to the number of slots "
                + f"in self.entity_context, which is {len(self.entity_context)}."
            )
        return Fact(
            self.predicate,
            entity_context,
            self.absent,
            self.standard_of_proof,
            case_factors,
        )
