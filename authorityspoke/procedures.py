r"""
Descriptions of procedural changes in litigation.

Does not specify whether they are mandatory or universal,
or specify the :class:`.Enactment`\s that might require them.
"""

from __future__ import annotations
from copy import deepcopy

from itertools import chain
import operator

from typing import Any, Dict, Iterable, Iterator
from typing import List, Optional, Sequence, Tuple, Union

from nettlesome.terms import (
    Comparable,
    ContextRegister,
    Explanation,
    new_context_helper,
    Term,
    TermSequence,
)
from nettlesome.factors import Factor
from nettlesome.groups import FactorGroup
from nettlesome.formatting import indented


class Procedure(Comparable):
    r"""
    A (potential) rule for courts to use in resolving litigation.

    Described in terms of inputs and outputs, and also potentially
    "despite" :class:`.Factor`\s, which occur when a :class:`Rule`
    could be said to apply "even if" some "despite" factor is true.

    Users generally should not need to interact with this class
    directly, under the current design. Instead, they should interact
    with the class :class:`.Rule`.

    :param outputs:
        an outcome that a court may accept based on the presence
        of the ``inputs``

    :param inputs:
        supporting :class:`.Factor`\s in favor of the ``output``.
        The ``input`` :class:`.Factor`\s are not treated as
        potential undercutters.

    :param despite:
        :class:`.Factor`\s that do not prevent the court from
        imposing the ``output``. These could be considered
        "failed undercutters" in defeasible logic. If a :class:`.Factor`
        is relevant both as support for the output and as
        a potential undercutter, include it in both ``inputs``
        and ``despite``.

    :param name:
        An identifier that can be used to reference and
        incorporate an existing procedure in a new
        :class:`.Factor`, instead of constructing a new
        copy of the :class:`.Procedure`.

    :param absent:
        Whether the absence, rather than presence, of this
        :class:`.Procedure` is being referenced. The usefulness
        of this is unclear, but I'm not prepared to eliminate it
        before the :class:`.Argument` class has been implemented
        and tested.

    :param generic:
        Whether the this :class:`Procedure` is being referenced
        as a generic example, which could be replaced by any
        other :class:`Procedure`.
    """

    def __init__(
        self,
        outputs: FactorGroup,
        inputs: Optional[FactorGroup] = None,
        despite: Optional[FactorGroup] = None,
        generic: bool = False,
        absent: bool = False,
        name: str = "",
    ):
        self.outputs = FactorGroup(outputs)
        self.inputs = FactorGroup(inputs) if inputs else FactorGroup()
        self.despite = FactorGroup(despite) if despite else FactorGroup()
        self.name = name
        self.absent = False
        self.generic = False
        self.context_factor_names = ("outputs", "inputs", "despite")

    @property
    def groups(self) -> List[FactorGroup]:
        return [self.outputs, self.inputs, self.despite]

    def add(
        self,
        other: Comparable,
        context: Optional[Union[ContextRegister, Explanation]] = None,
    ) -> Optional[Procedure]:
        """Show how first Procedure triggers the second if not both are universal."""
        if not isinstance(other, self.__class__):
            return self.with_factor(other)
        for explanation in self.triggers_next_procedure(other, context=context):
            added = self._trigger_addition(other, explanation)
            if added:
                return added
        return None

    def __add__(self, other: Procedure) -> Optional[Procedure]:
        """Show how first Procedure triggers the second if not both are universal."""
        return self.add(other)

    def _add_if_universal(
        self, other: Procedure, explanation: Explanation
    ) -> Optional[Procedure]:
        """Show how first Procedure triggers the second if both are universal."""
        self_output_or_input = FactorGroup((*self.outputs, *self.inputs))
        other_input = list(other.inputs)
        implied_inputs = []
        not_implied = []

        while other_input:
            current = other_input.pop()
            implying_explanation = self_output_or_input.explain_implication(
                current, context=explanation
            )
            if implying_explanation is not None:
                explanation = implying_explanation
                implied_inputs.append(current)
            else:
                not_implied.append(current)

        if not any(implied_inputs):
            return None
        to_combine = Procedure(
            inputs=not_implied, outputs=other.outputs, despite=other.despite
        )
        return self.union(to_combine, context=explanation)

    def _trigger_addition(
        self, other: Procedure, explanation: Explanation
    ) -> Procedure:
        """Add two Procedures, given that they have already been found to be addable."""
        triggered_procedure = other.new_context(explanation.context.reversed())
        new_outputs = [*self.outputs, *triggered_procedure.outputs]
        unique_new_outputs = {}
        for key in new_outputs:
            unique_new_outputs[str(key)] = key
        result = deepcopy(self)
        result.set_outputs(list(unique_new_outputs.values()))
        return result

    def _explanations_union_partial(
        self, other: Procedure, context: Optional[ContextRegister] = None
    ) -> Iterable[ContextRegister]:
        """Yield as much of the context as seems likely correct based on this Procedure."""
        yield from self.likely_contexts(other, context)

    def explanations_union(
        self,
        other: Procedure,
        context: Optional[Union[ContextRegister, Explanation]] = None,
    ) -> Iterator[ContextRegister]:
        if not isinstance(context, Explanation):
            context = Explanation.from_context(context)
        for partial in self._explanations_union_partial(other, context.context):
            for guess in self.possible_contexts(other, partial):
                answer = self._union_from_explanation(other, guess)
                if answer:
                    yield guess

    def _union_from_explanation(
        self, other: Procedure, context: ContextRegister
    ) -> Optional[Procedure]:
        r"""
        Combine two :class:`Procedure`\s into one.

        The new :class:`Procedure` will have all of the ``inputs``, ``outputs``,
        and ``despite`` :class:`.Factor`\s of both ``self`` and ``other``.

        All of the context :class:`.Factor`\s of ``self`` will
        remain the same.
        """

        new_inputs = self.inputs._union_from_explanation(other.inputs, context)
        new_outputs = self.outputs._union_from_explanation(other.outputs, context)
        new_despite = self.despite._union_from_explanation_allow_contradiction(
            other.despite, context
        )

        if any(group is None for group in (new_outputs, new_inputs, new_despite)):
            return None
        return Procedure(outputs=new_outputs, inputs=new_inputs, despite=new_despite)

    def __len__(self):
        r"""
        Get number of generic :class:`.Factor`\s specified for ``self``.

        :returns:
            the number of generic :class:`.Factor`\s that need to be
            specified for this :class:`Procedure`.
        """

        return len(self.generic_terms())

    def __repr__(self):
        text = (
            f"{self.__class__.__name__}(outputs=("
            + f"{', '.join(repr(factor) for factor in self.outputs)}), "
            + f"inputs=({', '.join(repr(factor) for factor in self.inputs)}), "
            + f"despite=({', '.join(repr(factor) for factor in self.despite)}))"
        )
        return text

    def __str__(self):

        text = "RESULT:"
        for f in self.outputs:
            text += "\n" + indented(f.wrapped_string)
        if self.inputs:
            text += "\nGIVEN:"
            for f in self.inputs:
                text += "\n" + indented(f.wrapped_string)
        if self.despite:
            text += "\nDESPITE:"
            for f in self.despite:
                text += "\n" + indented(f.wrapped_string)

        return text

    @property
    def factors_all(self) -> List[Factor]:
        r"""
        Get :class:`.Factor`\s in ``inputs``, ``outputs``, and ``despite``.

        :returns:
            a :class:`list` of all :class:`.Factor`\s.
        """

        inputs = self.inputs or ()
        despite = self.despite or ()
        return [*self.outputs, *inputs, *despite]

    @property
    def recursive_terms(self) -> Dict[str, Term]:
        r"""
        Collect `self`'s :attr:`terms`, and their :attr:`terms`, recursively.

        :returns:
            a :class:`dict` (instead of a :class:`set`,
            to preserve order) of :class:`Term`\s.
        """
        answers: Dict[str, Term] = {}

        for context in self.groups:
            if context:
                answers.update(context.recursive_terms)
        return answers

    @property
    def terms(self) -> TermSequence:
        r"""
        Get :class:`Factor`\s used in comparisons with other :class:`Factor`\s.

        :returns:
            a tuple of attributes that are designated as the ``terms``
            for whichever subclass of :class:`Factor` calls this method. These
            can be used for comparing objects using :meth:`consistent_with`
        """
        result: List[Term] = []
        result.extend(self.outputs)
        result.extend(self.inputs)
        result.extend(self.despite)
        return TermSequence(result)

    def generic_terms_by_str(self) -> Dict[str, Term]:
        r"""
        :class:`.Factor`\s that can be replaced without changing ``self``\s meaning.

        self.generic can't be True for :class:`.Procedure`.

        :returns:
            ``self``'s generic :class:`.Factor`\s,
            which must be matched to other generic :class:`.Factor`\s to
            perform equality or implication tests between :class:`.Factor`\s
            with :meth:`.Factor.means` or :meth:`.Factor.__ge__`.
        """
        generic_dict = {
            str(generic): generic
            for factor in self.factors_all
            for generic in factor.generic_terms()
        }
        return generic_dict

    def add_factor(self, incoming: Factor) -> None:
        """
        Add an input :class:`.Factor`.

        :param incoming:
            the new :class:`.Factor` to be added to input

        :returns:
            None
        """
        new_factors = self.inputs.add_or_raise_error(incoming)
        self.set_inputs(new_factors)

    def with_factor(self, incoming: Factor) -> Optional[Procedure]:
        """
        Create new Procedure with added input :class:`.Factor`.

        :param incoming:
            the new :class:`.Factor` to be added to input

        :returns:
            a new version of ``self`` with the specified change
        """
        new_factors = self.inputs + incoming
        if new_factors is None:
            return None
        result = deepcopy(self)
        result.set_inputs(new_factors)
        return result

    def contradicts(self, other, context: Optional[ContextRegister] = None) -> bool:
        r"""
        Find if ``self`` applying in some cases implies ``other`` cannot apply in some.

        Raises an error because, by analogy with :meth:`.Procedure.implies`\,
        users might expect this method to return ``True`` only when
        :class:`Rule` with ``universal=False`` and Procedure ``self``
        would contradict another :class:`Rule` with ``universal=False``
        and Procedure ``other``. But that would never happen.
        """
        raise NotImplementedError(
            "Procedures do not contradict one another unless one of them ",
            "applies in 'ALL' cases. Consider using ",
            "'Procedure.contradicts_some_to_all' or 'Rule.contradicts'.",
        )

    def contradicts_some_to_all(
        self, other: Procedure, context: Optional[ContextRegister] = None
    ) -> bool:
        r"""
        Find if ``self`` applying in some cases implies ``other`` cannot apply in all.

        :returns:
            whether the assertion that ``self`` applies in
            **some** cases contradicts that ``other`` applies in **all**
            cases, where at least one of the :class:`.Rule`\s is ``mandatory``.
        """

        if not isinstance(other, self.__class__):
            return False
        return any(
            context is not None
            for context in self.explain_contradiction_some_to_all(other, context)
        )

    def _has_input_or_despite_factors_implied_by_all_inputs_of(
        self,
        other: Procedure,
        context: Explanation,
    ) -> Iterator[Explanation]:
        """Check if every input of other implies some input or despite factor of self."""
        self_despite_or_input = FactorGroup((*self.despite, *self.inputs))
        yield from self_despite_or_input._explanations_implied_by(
            other.inputs, explanation=context
        )

    def _has_input_or_despite_factors_implying_all_inputs_of(
        self,
        other: Procedure,
        context: Explanation,
    ) -> Iterator[Explanation]:
        """Check if every input of other is implied by some input or despite factor of self."""
        self_despite_or_input = FactorGroup((*self.despite, *self.inputs))
        yield from self_despite_or_input._explanations_implication(
            other.inputs, explanation=context
        )

    def explain_contradiction_some_to_all(
        self,
        other: Procedure,
        context: Optional[Union[ContextRegister, Explanation]] = None,
    ) -> Iterator[Explanation]:
        """Explain why ``other`` can't apply in all cases if ``self`` applies in some."""
        if not isinstance(context, Explanation):
            context = Explanation.from_context(context)

        # For self to contradict other, either every input of other
        # must imply some input or despite factor of self...
        implied_contexts = self._has_input_or_despite_factors_implied_by_all_inputs_of(
            other, context
        )

        # or every input of other must be implied by
        # some input or despite factor of self.
        implying_contexts = self._has_input_or_despite_factors_implying_all_inputs_of(
            other, context
        )

        # For self to contradict other, some output of other
        # must be contradicted by some output of self.
        seen_contexts = []
        for m in chain(implying_contexts, implied_contexts):
            if m.context not in seen_contexts:
                seen_contexts.append(m.context)
                yield from self.outputs._explanations_contradiction(other.outputs, m)

    def _explain_implication_all_to_all_of_procedure(
        self, other: Procedure, context: ContextRegister
    ) -> Iterator[ContextRegister]:
        yield from self.explanations_same_meaning(other, context)

        def other_outputs_implied(context: Optional[ContextRegister]):
            for explanation in self.outputs.explanations_implication(
                other.outputs, context=context
            ):
                yield explanation

        def self_inputs_implied(explanations: Iterable[ContextRegister]):
            for explanation in explanations:
                for result in other.inputs.explanations_implication(
                    self.inputs, context=explanation
                ):
                    yield result

        for explanation in self_inputs_implied(other_outputs_implied(context)):
            for result in self.inputs.explanations_consistent_with(
                other=other.despite, context=explanation
            ):
                yield result

    def explain_implication_all_to_all(
        self, other: Factor, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        """Yield contexts establishing that if self is always valid, other is always valid."""
        context = context or ContextRegister()
        if isinstance(other, self.__class__):
            yield from self._explain_implication_all_to_all_of_procedure(other, context)

    def implies_all_to_all(
        self, other: Procedure, context: Optional[ContextRegister] = None
    ) -> bool:
        """
        Find if ``self`` applying in all cases implies ``other`` applies in all.

        ``self`` does not imply ``other`` if any output of ``other``
        is not equal to or implied by some output of ``self``.

        For ``self`` to imply ``other``, every input of ``self``
        must be implied by some input of ``other``.

        ``self`` does not imply ``other`` if any despite of ``other``
        :meth:`~.Factor.contradicts` an input of ``self``.

        :returns:
            whether the assertion that ``self`` applies in **all** cases
            implies that ``other`` applies in **all** cases.
        """
        return any(
            context is not None
            for context in self.explain_implication_all_to_all(other, context)
        )

    def _explain_implication_of_procedure_all_to_some(
        self, other: Procedure, context: ContextRegister
    ) -> Iterator[ContextRegister]:
        yield from self.explain_implication_all_to_all(other, context)

        other_despite_or_input = FactorGroup((*other.despite, *other.inputs))
        self_despite_or_input = FactorGroup((*self.despite, *self.inputs))

        def other_outputs_implied(context: ContextRegister):
            for explanation in self.outputs.explanations_implication(
                other.outputs, context=context
            ):
                yield explanation

        def other_despite_implied(explanations: Iterator[ContextRegister]):
            for explanation in explanations:
                for result in self_despite_or_input.explanations_implication(
                    other.despite, context=explanation
                ):
                    yield result

        for explanation in other_despite_implied(other_outputs_implied(context)):
            if self.inputs.consistent_with(
                other_despite_or_input, context=explanation.context
            ):
                yield explanation

    def explain_implication_all_to_some(
        self,
        other: Factor,
        context: Optional[Union[ContextRegister, Explanation]] = None,
    ) -> Iterator[Explanation]:
        """Yield contexts establishing that if self is always valid, other is sometimes valid."""
        if not isinstance(context, Explanation):
            context = Explanation.from_context(context)
        if isinstance(other, self.__class__):
            yield from self._explain_implication_of_procedure_all_to_some(
                other=other, context=context
            )

    def implies_all_to_some(
        self, other: Procedure, context: Optional[ContextRegister] = None
    ) -> bool:
        r"""
        Find if ``self`` applying in all cases implies ``other`` applies in some.

        For ``self`` to imply ``other``, every output of ``other``
        must be equal to or implied by some output of ``self``.

        For ``self`` to imply ``other``, every input of ``self`` must not be
        contradicted by any input or despite of ``other``.

        ``self`` does not imply ``other`` if any "despite" :class:`.Factor`\s
        of ``other`` are not implied by inputs of ``self``.

        :returns:
            whether the assertion that ``self`` applies in **all** cases
            implies that ``other`` applies in **some** cases (that is, if
            the list of ``self``'s inputs is not considered an exhaustive list
            of the circumstances needed to invoke the procedure).
        """
        return any(
            context is not None
            for context in self.explain_implication_all_to_some(other, context)
        )

    def _implies_procedure_if_present(
        self, other: Procedure, context: Explanation
    ) -> Iterator[Explanation]:
        def other_outputs_implied(context: Explanation):
            yield from self.outputs.explanations_implication(
                other.outputs, context=context
            )

        def other_inputs_implied(context: Explanation):
            yield from self.inputs.explanations_implication(
                other.inputs, context=context
            )

        def other_despite_implied(context: Explanation):
            despite_or_input = FactorGroup((*self.despite, *self.inputs))
            yield from despite_or_input.explanations_implication(
                other.despite,
                context=context,
            )

        for outputs_explanation in other_outputs_implied(context):
            for inputs_explanation in other_inputs_implied(outputs_explanation):
                for despite_explanation in other_despite_implied(inputs_explanation):
                    yield despite_explanation

    def _implies_if_present(
        self, other: Factor, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        r"""
        Find if ``self`` would imply ``other`` if they aren't absent.

        When ``self`` and ``other`` are included in
        :class:`Rule`\s that both apply in **some** cases:

        ``self`` does not imply ``other`` if any output of ``other``
        is not equal to or implied by some output of self.

        ``self`` does not imply ``other`` if any input of ``other``
        is not equal to or implied by some input of ``self``.

        ``self`` does not imply ``other`` if any despite of ``other``
        is not equal to or implied by some despite or input of ``self``.

        :returns:
            whether the assertion that ``self`` applies in some cases
            implies that the :class:`.Procedure` ``other`` applies
            in some cases.
        """

        if isinstance(other, self.__class__):
            yield from self._implies_procedure_if_present(other=other, context=context)

    def _explanations_same_meaning_as_procedure(
        self, other: Procedure, context: Explanation
    ):
        def same_outputs(context: Explanation):
            for explanation in self.outputs.explanations_same_meaning(
                other=other.outputs, context=context
            ):
                yield explanation

        def same_inputs(contexts: Iterable[Explanation]):
            for context in contexts:
                for explanation in self.inputs.explanations_same_meaning(
                    other=other.inputs, context=context
                ):
                    yield explanation

        def same_despite(contexts: Iterable[Explanation]):
            for context in contexts:
                for explanation in self.despite.explanations_same_meaning(
                    other=other.despite, context=context
                ):
                    yield explanation

        yield from same_despite(same_inputs(same_outputs(context)))

    def explanations_same_meaning(
        self,
        other: Comparable,
        context: Optional[Union[ContextRegister, Explanation]] = None,
    ) -> Iterator[Explanation]:
        """Yield contexts that could cause self to have the same meaning as other."""

        if not isinstance(context, Explanation):
            context = Explanation.from_context(context)

        if isinstance(other, self.__class__):
            yield from self._explanations_same_meaning_as_procedure(other, context)

    def means(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> bool:
        r"""
        Determine whether ``other`` has the same meaning as ``self``.

        :returns:
            whether the two :class:`.Procedure`\s have all the same
            :class:`.Factor`\s with the same context factors in the
            same roles.
        """
        return any(
            context is not None
            for context in self.explanations_same_meaning(other, context)
        )

    @new_context_helper
    def new_context(self, changes: ContextRegister) -> Procedure:
        r"""
        Create new :class:`Procedure`, replacing keys of ``changes`` with values.

        :param changes:
            a :class:`dict` of :class:`.Factor`\s to replace
            matched to the :class:`.Factor`\s that should replace them

        :returns:
            new :class:`.Procedure` object, replacing keys of
            ``changes`` with their values.
        """
        new_dict = self.__dict__.copy()
        for name in self.context_factor_names:
            new_dict[name] = tuple(
                factor.new_context(changes) for factor in new_dict[name]
            )
        new_dict.pop("context_factor_names")
        return self.__class__(**new_dict)

    def set_inputs(self, factors: Sequence[Factor]) -> None:
        self.inputs = FactorGroup(factors)

    def set_despite(self, factors: Sequence[Factor]) -> None:
        self.despite = FactorGroup(factors)

    def set_outputs(self, factors: Sequence[Factor]) -> None:
        self.outputs = FactorGroup(factors)

    def triggers_next_procedure(
        self,
        other: Procedure,
        context: Optional[Union[ContextRegister, Explanation]] = None,
    ) -> Iterator[Explanation]:
        r"""
        Test if :class:`.Factor`\s from firing ``self`` would trigger ``other``.

        .. Note::
            To be confident that ``self`` actually can trigger ``other``,
            we would have to assume that self or other has ``universal: True``
            since otherwise there could be a mismatch between what is provided
            and what is needed to trigger ``other``.

        :param other:
            another :class:`Procedure` to test to see whether it can
            be triggered by triggering ``self``

        :returns:
            whether the set of :class:`Factor`\s that exist after ``self``
            is fired could trigger ``other``
        """
        self_despite_or_input = FactorGroup((*self.despite, *self.inputs))
        self_output_or_input = FactorGroup((*self.outputs, *self.inputs))

        if not isinstance(context, Explanation):
            context = Explanation.from_context(context)

        for explanation_1 in self_output_or_input.explanations_implication(
            other.inputs, context=context
        ):
            yield from self_despite_or_input.explanations_implication(
                other.despite, context=explanation_1
            )

    def __or__(self, other: Comparable) -> Optional[Comparable]:
        return self.union(other)

    def union(
        self,
        other: Comparable,
        context: Optional[Union[ContextRegister, Explanation]] = None,
    ) -> Optional[Comparable]:
        if not isinstance(context, Explanation):
            context = Explanation.from_context(context)
        explanations = self.explanations_union(other, context)
        try:
            explanation = next(explanations)
        except StopIteration:
            return None
        return self._union_from_explanation(other, explanation)

    def valid_for_exclusive_tag(self) -> None:
        if len(self.outputs) != 1:
            raise ValueError(
                "The 'exclusive' attribute is not allowed for Holdings "
                + "with more than one 'output' Factor. If the set of Factors "
                + "in 'inputs' is really the only way to reach any of the "
                + "'outputs', consider making a separate 'exclusive' Rule "
                + "for each output."
            )
        if self.outputs[0].absent:
            raise ValueError(
                "The 'exclusive' attribute is not allowed for Holdings "
                + "with an 'absent' 'output' Factor. This would indicate "
                + "that the output can or must be present in every litigation "
                + "unless specified inputs are present, which is unlikely."
            )
        if not self.inputs:
            raise ValueError(
                "The 'exclusive' attribute is not allowed for Holdings "
                + "with no 'input' Factors, since the 'exclusive' attribute "
                + "asserts that the inputs are the only way to reach the output."
            )
        return None
