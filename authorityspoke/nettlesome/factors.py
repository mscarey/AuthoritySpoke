"""Factors that can be included in FactorGroups."""

from typing import ClassVar, Iterator, Tuple

from pydantic import BaseModel

from authorityspoke.nettlesome.entities import Entity
from authorityspoke.nettlesome.terms import Comparable, Explanation, Term, TermSequence


class Factor(Term, BaseModel):
    r"""
    A thing that can be asserted to be present or absent.

    Factors can be compared as a group by including them
    in :class:`~nettlesome.groups.FactorGroup`\s, unlike
    :class:`~nettlesome.terms.Term`\s that are not Factors.
    """


class AbsenceOf(Comparable, BaseModel):
    """A factor that is not present."""

    generic: bool = False
    absent: Factor
    context_factor_names: ClassVar[Tuple[str, ...]] = ("absent",)

    def __str__(self):
        return f"absence of {str(self.absent)}"

    def _explanations_implication(
        self, other: Comparable, explanation: Explanation
    ) -> Iterator[Explanation]:
        if not isinstance(other, Comparable):
            raise TypeError(
                f"{self.__class__} objects may only be compared for "
                + "implication with other Comparable objects or None."
            )

        reversed_explanation = explanation.with_context(explanation.context.reversed())
        if isinstance(other, self.__class__):
            test = other.absent._implies_if_present(self.absent, reversed_explanation)
        else:
            test = other._contradicts_if_present(self.absent, reversed_explanation)
        yield from (
            register.with_context(register.context.reversed()) for register in test
        )

    def _explanations_contradiction(
        self, other: Comparable, context: Explanation
    ) -> Iterator[Explanation]:
        if not isinstance(other, Comparable):
            raise TypeError(
                f"{self.__class__} objects may only be compared for "
                + "contradiction with other Factor objects or None."
            )
        # No contradiction between absences of any two Comparables
        if not isinstance(other, self.__class__):
            if not isinstance(other, Term):
                explanation_reversed = context.reversed_context()
                yield from other._explanations_contradiction(
                    self, context=explanation_reversed
                )
            elif isinstance(other, self.absent.__class__):
                explanation_reversed = context.with_context(context.context.reversed())
                test = other._implies_if_present(self.absent, explanation_reversed)
                for new_explanation in test:
                    yield new_explanation.with_context(
                        new_explanation.context.reversed()
                    )


TermSequence.model_rebuild()
