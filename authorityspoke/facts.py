"""Create models of assertions accepted as factual by courts."""

from copy import deepcopy
from dataclasses import dataclass, field
import operator

from typing import ClassVar, Dict, Iterator, List, Optional, Sequence, Tuple, Union

from anchorpoint.textselectors import TextQuoteSelector

from authorityspoke.comparisons import FactorSequence, new_context_helper
from authorityspoke.factors import Factor, ContextRegister
from authorityspoke.formatting import indented, wrapped
from authorityspoke.predicates import Predicate


@dataclass()
class Fact(Factor):
    r"""
    An assertion accepted as factual by a court.

    Often based on factfinding by a judge or jury.

    Facts may be "alleged" by a pleading, "supported" by evidence, or
    "found" to be factual by a jury verdict or a judge's finding of fact.

    :param predicate:
        a natural-language clause with zero or more slots
        to insert ``terms`` that are typically the
        subject and objects of the clause.

    :param terms:
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
    terms: FactorSequence = FactorSequence()
    name: Optional[str] = None
    standard_of_proof: Optional[str] = None
    absent: bool = False
    generic: bool = False
    anchors: List[TextQuoteSelector] = field(default_factory=list)
    standards_of_proof: ClassVar[Tuple[str, ...]] = (
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

        if not isinstance(self.terms, FactorSequence):
            terms = FactorSequence(self.terms)
            object.__setattr__(self, "terms", terms)

        if len(self.terms) != len(self.predicate):
            message = (
                "The number of items in 'terms' must be "
                + f"{len(self.predicate)}, not {len(self.terms)}, "
                + f"to match predicate.context_slots for '{self.predicate.content}'"
            )
            if hasattr(self, "name"):
                message += f" for '{self.name}'"
            raise ValueError(message)
        if any(not isinstance(s, Factor) for s in self.terms):
            raise TypeError(
                "Items in the terms parameter should "
                + "be Factor or a subclass of Factor, or should be integer "
                + "indices of Factor objects in the case_factors parameter."
            )

    @property
    def wrapped_string(self):
        content = str(self.predicate.content_with_terms(self.terms))
        unwrapped = self.predicate.add_truth_to_content(content)
        text = wrapped(super().__str__().format(unwrapped))
        if self.standard_of_proof:
            text += "\n" + indented("by the STANDARD {self.standard_of_proof}")
        return text

    @property
    def str_with_concrete_context(self):
        """
        Identify this Fact more verbosely, specifying which text is a concrete context factor.

        :returns:
            the same as the __str__ method, but with an added "SPECIFIC CONTEXT" section
        """
        text = str(self)
        concrete_context = [factor for factor in self.terms if not factor.generic]
        if any(concrete_context) and not self.generic:
            text += "\n" + indented("SPECIFIC CONTEXT:")
            for factor in concrete_context:
                factor_text = indented(factor.wrapped_string, tabs=2)
                text += f"\n{str(factor_text)}"
        return text

    def __str__(self):
        """Create one-line string representation for inclusion in other Facts."""
        content = str(self.predicate.content_with_terms(self.terms))
        unwrapped = self.predicate.add_truth_to_content(content)
        standard = (
            f"by the standard {self.standard_of_proof}, "
            if self.standard_of_proof
            else ""
        )
        string = f"{standard}{unwrapped}"
        return super().__str__().format(string).replace("Fact", "fact")

    @property
    def content(self) -> Optional[str]:
        """Access :attr:`~Predicate.content` attribute."""
        return self.predicate.content

    @property
    def truth(self) -> Optional[bool]:
        """Access :attr:`~Predicate.truth` attribute."""
        return self.predicate.truth

    def _means_if_concrete(
        self, other: Factor, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        if (
            isinstance(other, self.__class__)
            and self.predicate.means(other.predicate)
            and self.standard_of_proof == other.standard_of_proof
        ):
            yield from super()._means_if_concrete(other, context)

    def __len__(self):
        return len(self.terms)

    def _implies_if_concrete(
        self, other: Factor, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
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
            yield from super()._implies_if_concrete(other, context)

    def _contradicts_if_present(
        self, other: Factor, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        """
        Test if ``self`` contradicts :class:`Fact` ``other`` if neither is ``absent``.

        :returns:
            whether ``self`` and ``other`` can't both be true at
            the same time under the given assumption.
        """
        if context is None:
            context = ContextRegister()
        if isinstance(other, Fact) and self.predicate.contradicts(other.predicate):
            yield from self._context_registers(other, operator.ge, context)

    @new_context_helper
    def new_context(self, changes: Dict[Factor, Factor]) -> Factor:
        """
        Create new :class:`Factor`, replacing keys of ``changes`` with values.

        :returns:
            a version of ``self`` with the new context.
        """
        result = deepcopy(self)
        result.terms = FactorSequence(
            [factor.new_context(changes) for factor in self.terms]
        )
        return result

    def term_permutations(self) -> Iterator[FactorSequence]:
        """Generate permutations of context factors that preserve same meaning."""
        for pattern in self.predicate.term_index_permutations():
            sorted_terms = [x for _, x in sorted(zip(pattern, self.terms))]
            yield FactorSequence(sorted_terms)


def build_fact(
    predicate: Predicate,
    indices: Optional[Union[int, Sequence[int]]] = None,
    case_factors: Optional[Union[Factor, Sequence[Factor]]] = None,
    name: Optional[str] = None,
    standard_of_proof: Optional[str] = None,
    absent: bool = False,
    generic: bool = False,
):
    r"""
    Build a :class:`.Fact` with generics selected from a list.

    :param predicate:
        a natural-language clause with zero or more slots
        to insert ``terms`` that are typically the
        subject and objects of the clause.

    :param terms:
        a series of integer indices of generic factors to
        fill in the blanks in the :class:`.Predicate`

    :param name:
        an identifier for this object, often used if the object needs
        to be referred to multiple times in the process of composing
        other :class:`.Factor` objects

    :param standard_of_proof:
        a descriptor for the degree of certainty associated
        with the assertion in the :class:`.Predicate`

    :param absent:
        whether the absence, rather than the presence, of the legal
        fact described above is being asserted.

    :param generic:
        whether this object could be replaced by another generic
        object of the same class without changing the truth of the
        :class:`Rule` in which it is mentioned.

    :param case_factors:
        a series of :class:`.Factor`\s that have already been mentioned
        in the :class:`.Opinion`. They are available for composing the
        new :class:`.Factor` object and don't need to be recreated.
    """
    if not indices:
        indices = range(len(predicate))
    if isinstance(indices, int):
        indices = (indices,)

    if case_factors is None:
        case_factors = []
    if isinstance(case_factors, Factor):
        case_factors = [case_factors]

    terms = FactorSequence([case_factors[i] for i in indices])
    return Fact(
        predicate=predicate,
        terms=terms,
        name=name,
        standard_of_proof=standard_of_proof,
        absent=absent,
        generic=generic,
    )
