from copy import deepcopy
import operator

from typing import ClassVar, Dict, Iterator, List
from typing import Optional, Sequence, Tuple, Union

from anchorpoint.textselectors import TextQuoteSelector

from authorityspoke.statements.comparable import (
    Comparable,
    FactorSequence,
    ContextRegister,
    new_context_helper,
)

from authorityspoke.statements.formatting import indented, wrapped
from authorityspoke.statements.predicates import Predicate


class Statement(Comparable):
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

    def __init__(
        self,
        predicate: Predicate,
        terms: FactorSequence = FactorSequence(),
        absent: bool = False,
        generic: bool = False,
    ):
        self.predicate = predicate
        self.absent = absent
        self.generic = generic
        if not isinstance(self.terms, FactorSequence):
            terms = FactorSequence(self.terms)
            object.__setattr__(self, "terms", terms)

        if len(self.terms) != len(self.predicate):
            message = (
                "The number of items in 'terms' must be "
                + f"{len(self.predicate)}, not {len(self.terms)}, "
                + f"to match predicate.context_slots for '{self.predicate.content}'"
            )
            raise ValueError(message)
        if any(not isinstance(s, Comparable) for s in self.terms):
            raise TypeError(
                "Items in the 'terms' parameter should "
                + "be a subclass of Comparable."
            )

    @property
    def wrapped_string(self):
        content = str(self.predicate.content_with_terms(self.terms))
        unwrapped = self.predicate.add_truth_to_content(content)
        text = wrapped(super().__str__().format(unwrapped))
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
        return super().__str__().format(unwrapped).replace("Fact", "fact")

    @property
    def content(self) -> Optional[str]:
        """Access :attr:`~Predicate.content` attribute."""
        return self.predicate.content

    @property
    def truth(self) -> Optional[bool]:
        """Access :attr:`~Predicate.truth` attribute."""
        return self.predicate.truth

    def _means_if_concrete(
        self, other: Comparable, context: Optional[ContextRegister] = None
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
        self, other: Comparable, context: Optional[ContextRegister] = None
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
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        """
        Test if ``self`` contradicts :class:`Fact` ``other`` if neither is ``absent``.

        :returns:
            whether ``self`` and ``other`` can't both be true at
            the same time under the given assumption.
        """
        if context is None:
            context = ContextRegister()
        if isinstance(other, self.__class__) and self.predicate.contradicts(
            other.predicate
        ):
            yield from self._context_registers(other, operator.ge, context)

    @new_context_helper
    def new_context(self, changes: Dict[Comparable, Comparable]) -> Comparable:
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

    def __or__(self, other: Comparable):
        return self.union(other)

    def union(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Optional[Comparable]:
        if not isinstance(other, Comparable):
            raise TypeError
        if self.implies(other, context=context):
            return self
        if other.implies(self, context=context):
            return other.new_context(self.generic_factors())
        return None
