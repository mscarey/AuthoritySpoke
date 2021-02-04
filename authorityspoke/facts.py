"""Create models of assertions accepted as factual by courts."""

from typing import ClassVar, Iterator, List, Optional, Sequence, Tuple, Union

from anchorpoint.textselectors import TextQuoteSelector


from authorityspoke.factors import Factor, ContextRegister
from authorityspoke.statements.formatting import indented, wrapped

from authorityspoke.statements.comparable import (
    Comparable,
    FactorSequence,
)
from authorityspoke.statements.predicates import Predicate
from authorityspoke.statements.statements import Statement


class Fact(Statement, Factor):
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

    standards_of_proof: ClassVar[Tuple[str, ...]] = (
        "scintilla of evidence",
        "substantial evidence",
        "preponderance of evidence",
        "clear and convincing",
        "beyond reasonable doubt",
    )

    def __init__(
        self,
        predicate: Predicate,
        terms: FactorSequence = FactorSequence(),
        name: Optional[str] = None,
        standard_of_proof: Optional[str] = None,
        absent: bool = False,
        generic: bool = False,
        anchors: Optional[List[TextQuoteSelector]] = None,
    ):
        Statement.__init__(
            self, predicate=predicate, terms=terms, absent=absent, generic=generic
        )
        self.standard_of_proof = standard_of_proof
        self.anchors = anchors or []
        self.name = name
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
        if any(not isinstance(s, Comparable) for s in self.terms):
            raise TypeError(
                "Items in the terms parameter should "
                + "be a subclass of Comparable, or should be integer "
                + "indices of Comparable objects in the case_factors parameter."
            )

    @property
    def wrapped_string(self):
        text = super().wrapped_string
        if self.standard_of_proof:
            text += "\n" + indented("by the STANDARD {self.standard_of_proof}")
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
        return Comparable.__str__(self).format(string).replace("Fact", "fact")

    def _means_if_concrete(
        self, other: Factor, context: ContextRegister
    ) -> Iterator[ContextRegister]:
        if self.standard_of_proof == other.standard_of_proof:
            yield from super()._means_if_concrete(other, context)

    def __len__(self):
        return len(self.terms)

    def _implies_if_concrete(
        self, other: Factor, context: ContextRegister
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
        ):
            yield from super()._implies_if_concrete(other, context)


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

    wrapped_factors = Comparable.wrap_with_tuple(case_factors)

    terms = FactorSequence([wrapped_factors[i] for i in indices])
    return Fact(
        predicate=predicate,
        terms=terms,
        name=name,
        standard_of_proof=standard_of_proof,
        absent=absent,
        generic=generic,
    )
