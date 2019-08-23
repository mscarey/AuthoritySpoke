from dataclasses import dataclass
import operator

from typing import ClassVar, Dict, Iterator, List, Optional, Sequence, Union

from authorityspoke.factors import new_context_helper
from authorityspoke.factors import Factor, ContextRegister
from authorityspoke.predicates import Predicate


@dataclass(frozen=True)
class Fact(Factor):
    r"""
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
    predicate: Predicate
    context_factors: Sequence[Factor] = ()
    name: Optional[str] = None
    standard_of_proof: Optional[str] = None
    absent: bool = False
    generic: bool = False
    case_factors: Sequence[Factor] = ()
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
        string = f"{standard}that {predicate}"
        return super().__str__().format(string)

    @property
    def interchangeable_factors(self) -> List[ContextRegister]:
        r"""
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

    @property
    def truth(self) -> Optional[bool]:
        """Access :attr:`~Predicate.truth` attribute."""
        return self.predicate.truth

    def _means_if_concrete(self, other: Factor) -> Iterator[ContextRegister]:
        if (
            isinstance(other, self.__class__)
            and self.predicate.means(other.predicate)
            and self.standard_of_proof == other.standard_of_proof
        ):
            yield from super()._means_if_concrete(other)

    def predicate_in_context(self, entities: Sequence[Factor]) -> str:
        r"""
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

    def _implies_if_concrete(self, other: Factor) -> Iterator[ContextRegister]:
        """
        Test if ``self`` impliess ``other``, assuming they are not ``generic``.

        :returns:
            whether ``self`` implies ``other`` under the given assumption.
        """
        if (
            isinstance(other, self.__class__)
            and bool(self.standard_of_proof) == bool(other.standard_of_proof)
            and not (
                self.standard_of_proof
                and (
                    self.standards_of_proof.index(self.standard_of_proof)
                    < self.standards_of_proof.index(other.standard_of_proof)
                )
            )
            and self.predicate >= other.predicate
        ):
            yield from super()._implies_if_concrete(other)

    def _contradicts_if_present(self, other: Factor) -> Iterator[ContextRegister]:
        """
        Test if ``self`` contradicts :class:`Fact` ``other`` if neither is ``absent``.

        :returns:
            whether ``self`` and ``other`` can't both be true at
            the same time under the given assumption.
        """
        if isinstance(other, Fact) and self.predicate.contradicts(other.predicate):
            yield from self.consistent_with(other, operator.ge)

    def _contradicts_if_factor(self, other: Factor) -> Iterator[ContextRegister]:
        r"""
        Test if ``self`` contradicts ``other``, assuming they are both :class:`Factor`\s.

        :returns:
            whether ``self`` and ``other`` can't both be true at
            the same time under the given assumption.
        """

        if isinstance(other, self.__class__) and not (self.absent and other.absent):
            if self.absent:
                yield from other._implies_if_present(self)
            elif not other.absent:
                yield from self._contradicts_if_present(other)
            else:
                yield from self._implies_if_present(other)

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
