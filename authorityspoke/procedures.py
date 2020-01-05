r"""
Descriptions of procedural changes in litigation.

Does not specify whether they are mandatory or universal,
or specify the :class:`.Enactment`\s that might require them.
"""

from __future__ import annotations

import functools
from itertools import chain
import operator

from typing import Any, Callable, ClassVar, Dict, Iterable, Iterator
from typing import List, Optional, Sequence, Tuple, Union

from dataclasses import dataclass

from authorityspoke.factors import Factor, ContextRegister, new_context_helper
from authorityspoke.factors import Analogy, all_analogy_matches, FactorGroup
from authorityspoke.formatting import indented


def find_less_specific_context(
    left: Procedure, right: Procedure, context: Optional[ContextRegister] = None
) -> Optional[ContextRegister]:
    r"""
    Find context assuming :class:`.Factor`\s with same meaning have corresponding generics.

    :param left:
        a :class:`.Procedure` that is being compared to another
        :class:`.Procedure`\, to create a new :class:`.Procedure`
        using the context of the left :class:`.Procedure`\.

    :param right:
        a :class:`.Procedure` that is being compared to another :class:`.Procedure`\,
        but that will have its context overwritten in the newly-created object.

    :param context:
        a :class:`.ContextRegister` identifying any known pairs of corresponding
        context :class:`.Factor`\s between the two :class:`.Procedure`\s being
        compared.

    :returns:
        a :class:`.ContextRegister`\s assuming that :class:`.Factor`\s with the
        same meaning have corresponding generics.
    """
    new_context = context or ContextRegister()
    for left_factor in left.factors_all:
        for right_factor in right.factors_all:
            if left_factor.means(right_factor, context=context):
                incoming = ContextRegister(
                    dict(zip(right_factor.generic_factors, left_factor.generic_factors))
                )
                updated_context = new_context.merged_with(incoming)
                if updated_context is not None:
                    new_context = updated_context
    if new_context and new_context != context:
        return new_context
    return None


def find_more_specific_context(
    left: Procedure, right: Procedure, context: Optional[ContextRegister] = None
) -> Optional[ContextRegister]:
    r"""
    Find context assuming :class:`.Factor`\s that imply each other have corresponding generics.

    :param left:
        a :class:`.Procedure` that is being compared to another
        :class:`.Procedure`\, to create a new :class:`.Procedure`
        using the context of the left :class:`.Procedure`\.

    :param right:
        a :class:`.Procedure` that is being compared to another :class:`.Procedure`\,
        but that will have its context overwritten in the newly-created object.

    :param context:
        a :class:`.ContextRegister` identifying any known pairs of corresponding
        context :class:`.Factor`\s between the two :class:`.Procedure`\s being
        compared.

    :returns:
        a :class:`.ContextRegister`\s assuming that :class:`.Factor`\s with the
        same meaning have corresponding generics.
    """
    new_context = context or ContextRegister()
    for left_factor in left.factors_all:
        for right_factor in right.factors_all:
            if left_factor.implies(
                right_factor, context=context
            ) or right_factor.implies(left_factor, context=context):
                incoming = ContextRegister(
                    dict(zip(right_factor.generic_factors, left_factor.generic_factors))
                )
                updated_context = new_context.merged_with(incoming)
                if updated_context is not None:
                    new_context = updated_context
    if new_context and new_context != context:
        return new_context
    return None


def use_likely_context(func: Callable):
    r"""
    Find contexts most likely to have been intended for comparing :class:`Procedure`\s.

    When such contexts are found, first tries calling the decorated comparison method
    using those contexts. Only if no answer is found using the likely contexts
    will the decorated method be called with no comparison method specified.

    :param left:
        a :class:`.Procedure` that is being compared to another
        :class:`.Procedure`\, to create a new :class:`.Procedure`
        using the context of the left :class:`.Procedure`\.

    :param right:
        a :class:`.Procedure` that is being compared to another :class:`.Procedure`\,
        but that will have its context overwritten in the newly-created object.

    :param context:
        a :class:`.ContextRegister` identifying any known pairs of corresponding
        context :class:`.Factor`\s between the two :class:`.Procedure`\s being
        compared.

    :returns:
        a generator yielding :class:`.ContextRegister`\s based on the most "likely"
        context that yields any :class:`.ContextRegister`\s at all.
    """

    @functools.wraps(func)
    def wrapper(
        left: Procedure, right: Procedure, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        less_specific = find_less_specific_context(left, right, context)
        more_specific = find_more_specific_context(left, right, less_specific)
        context_to_use = more_specific or less_specific or context or ContextRegister()
        for unused_left, unused_right in zip(
            [
                item
                for item in left.generic_factors
                if item not in context_to_use.keys()
            ],
            [
                item
                for item in right.generic_factors
                if item not in context_to_use.values()
            ],
        ):
            context_to_use[unused_right] = unused_left
        return func(left, right, context_to_use)

    return wrapper


@dataclass(frozen=True)
class Procedure(Factor):
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

    outputs: FactorGroup
    inputs: FactorGroup = FactorGroup()
    despite: FactorGroup = FactorGroup()
    name: Optional[str] = None
    absent: bool = False
    generic: bool = False
    context_factor_names: ClassVar = ("outputs", "inputs", "despite")

    def __post_init__(self):
        outputs = FactorGroup(self.outputs)
        inputs = FactorGroup(self.inputs)
        despite = FactorGroup(self.despite)
        groups = {"outputs": outputs, "inputs": inputs, "despite": despite}
        for group in groups:
            for factor_obj in groups[group]:
                if not isinstance(factor_obj, Factor):
                    raise TypeError(
                        "Input, Output, and Despite groups must contain "
                        + "only subclasses of Factor, but "
                        + f"{factor_obj} was type {type(factor_obj)}"
                    )
            object.__setattr__(self, group, groups[group])

    def _make_dict_to_evolve(
        self, changes: Union[str, Sequence[str], Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Translate shorthand input to the evolve method.

        If "changes" is already a dict, it won't be changed.

        :param changes:
            either a dict of field names and replacements, or one or more strings as shorthand

        :returns:
            a dict of field names and replacements
        """
        if isinstance(changes, str):
            changes = (changes,)
        if not isinstance(changes, dict):
            changes = {
                key: [factor.evolve("absent") for factor in self.__dict__[key]]
                for key in changes
            }
        return changes

    def evolve(self, changes: Union[str, Sequence[str], Dict[str, Any]]) -> Procedure:
        """
        Make new object with attributes from ``self.__dict__``, replacing attributes as specified.

        :param changes:
            a :class:`dict` where the keys are names of attributes
            of self, and the values are new values for those attributes

        :returns:
            a new object initialized with attributes from
            ``self.__dict__``, except that any attributes named as keys in the
            changes parameter are replaced by the corresponding value.
        """
        changes = self._make_dict_to_evolve(changes)
        new_values = self._evolve_from_dict(changes)
        return self.__class__(**new_values)

    def __add__(self, other: Procedure) -> Optional[Procedure]:
        if not isinstance(other, self.__class__):
            return self.add_factor(other)
        matchlist = self.triggers_next_procedure(other)
        if matchlist:
            # Arbitrarily choosing the first match to decide what
            # generic Factors appear in the new outputs.
            # Wouldn't it have been better to get just one match with a generator?
            triggered_rule = other.new_context(matchlist[0])
            new_outputs = [*self.outputs, *triggered_rule.outputs]
            unique_new_outputs = tuple({key: None for key in new_outputs})
            return self.evolve({"outputs": unique_new_outputs})
        return None

    def add_if_universal(self, other: Procedure) -> Optional[Procedure]:
        if not isinstance(other, self.__class__):
            return self.add_factor(other)
        matchlist = self.triggers_next_procedure_if_universal(other)
        if matchlist:
            triggered_rule = other.new_context(matchlist[0])
            new_outputs = [*self.outputs, *triggered_rule.outputs]
            unique_new_outputs = tuple({key: None for key in new_outputs})
            return self.evolve({"outputs": unique_new_outputs})
        return None

    @use_likely_context
    def union(
        self, other: Procedure, context: Optional[ContextRegister] = None
    ) -> Optional[Procedure]:
        r"""
        Combine two :class:`Procedure`\s into one.

        The new :class:`Procedure` will have all of the ``inputs``, ``outputs``,
        and ``despite`` :class:`.Factor`\s of both ``self`` and ``other``.

        All of the context :class:`.Factor`\s of ``self`` will
        remain the same.
        """

        def combine_factor_list(
            self_list, other_list, allow_contradictions: bool = False
        ):
            new_factors = []
            for self_factor in self_list:
                broadest = self_factor
                for other_factor in other_list:
                    if allow_contradictions is False and other_factor.contradicts(
                        self_factor
                    ):
                        return None
                    if other_factor >= self_factor:
                        broadest = other_factor
                new_factors.append(broadest)
            return new_factors + [
                factor for factor in other_list if factor not in new_factors
            ]

        other = other.new_context(context)
        new_inputs = combine_factor_list(self.inputs, other.inputs)
        new_outputs = combine_factor_list(self.outputs, other.outputs)
        new_despite = combine_factor_list(
            self.despite, other.despite, allow_contradictions=True
        )
        if any(group is None for group in (new_outputs, new_inputs, new_despite)):
            return None
        return Procedure(outputs=new_outputs, inputs=new_inputs, despite=new_despite)

    def __or__(self, other):
        return self.union(other)

    def __len__(self):
        r"""
        Get number of generic :class:`.Factor`\s specified for ``self``.

        :returns:
            the number of generic :class:`.Factor`\s that need to be
            specified for this :class:`Procedure`.
        """

        return len(self.generic_factors)

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
            text += "\n" + indented(str(f))
        if self.inputs:
            text += "\nGIVEN:"
            for f in self.inputs:
                text += "\n" + indented(str(f))
        if self.despite:
            text += "\nDESPITE:"
            for f in self.despite:
                text += "\n" + indented(str(f))

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
    def generic_factors(self) -> List[Factor]:
        r"""
        :class:`.Factor`\s that can be replaced without changing ``self``\s meaning.

        If ``self.generic is True`` then the only generic :class:`.Factor` is ``self``.
        This could happen if the :class:`.Procedure` was mentioned generically in an
        :class:`.Argument` about preserving objections for appeal, for instance.

        :returns:
            ``self``'s generic :class:`.Factor`\s,
            which must be matched to other generic :class:`.Factor`\s to
            perform equality or implication tests between :class:`.Factor`\s
            with :meth:`.Factor.means` or :meth:`.Factor.__ge__`.
        """
        if self.generic:
            return [self]
        return list(
            {
                generic: None
                for factor in self.factors_all
                for generic in factor.generic_factors
            }
        )

    def add_factor(self, incoming: Factor, role: str = "inputs") -> Procedure:
        """
        Add an output, input, or despite :class:`.Factor`.

        :param incoming:
            the new :class:`.Factor` to be added to input, output, or despite

        :param role:
            specifies whether the new :class:`.Factor` should be added to
            input, output, or despite

        :returns:
            a new version of ``self`` with the specified change
        """

        if role not in self.context_factor_names:
            raise ValueError(f"'role' must be one of {self.context_factor_names}")
        old_factors = self.__dict__.get(role) or []
        new_factors = list(old_factors) + [incoming]
        return self.evolve({role: new_factors})

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

    def has_input_or_despite_factors_implied_by_all_inputs_of(
        self, other: Procedure, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        self_despite_or_input = FactorGroup((*self.despite, *self.inputs))
        yield from self_despite_or_input.unordered_comparison(
            operation=operator.le, still_need_matches=other.inputs, matches=context
        )

    def has_input_or_despite_factors_implying_all_inputs_of(
        self, other: Procedure, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        self_despite_or_input = FactorGroup((*self.despite, *self.inputs))
        yield from self_despite_or_input.unordered_comparison(
            operation=operator.ge, still_need_matches=other.inputs, matches=context
        )

    def explain_contradiction_some_to_all(
        self, other: Procedure, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        """Explain why ``other`` can't apply in all cases if ``self`` applies in some."""
        if context is None:
            context = ContextRegister()

        # For self to contradict other, either every input of other
        # must imply some input or despite factor of self...
        implied_contexts = self.has_input_or_despite_factors_implied_by_all_inputs_of(
            other, context
        )

        # or every input of other must be implied by
        # some input or despite factor of self.
        implying_contexts = self.has_input_or_despite_factors_implying_all_inputs_of(
            other, context
        )

        # For self to contradict other, some output of other
        # must be contradicted by some output of self.
        for m in chain(implying_contexts, implied_contexts):
            if self.outputs.contradicts(other.outputs, m):
                yield m

    def _explain_implication_all_to_all_of_procedure(
        self, other: Procedure, context: ContextRegister
    ) -> Iterator[ContextRegister]:
        yield from self.explanations_same_meaning(other, context)

        def other_outputs_implied(context: Optional[ContextRegister]):
            yield from self.outputs.explanations_implication(
                other=other.outputs, context=context
            )

        def self_inputs_implied(contexts: Iterable[ContextRegister]):
            for context in contexts:
                yield from other.inputs.explanations_implication(
                    other=self.inputs, context=context
                )

        for explanation in self_inputs_implied(other_outputs_implied(context)):
            if self.inputs.consistent_with(other=other.despite, context=explanation):
                yield explanation

    def explain_implication_all_to_all(
        self, other: Factor, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
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
            yield from self.outputs.explanations_implication(
                other=other.outputs, context=context
            )

        def other_despite_implied(contexts: Iterator[ContextRegister]):
            for context in contexts:
                yield from self_despite_or_input.explanations_implication(
                    other=other.despite, context=context
                )

        for explanation in other_despite_implied(other_outputs_implied(context)):
            if self.inputs.consistent_with(other_despite_or_input, explanation):
                yield explanation

    def explain_implication_all_to_some(
        self, other: Factor, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        context = context or ContextRegister()
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
        self, other: Procedure, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        def other_outputs_implied(context: Optional[ContextRegister]):
            yield from self.outputs.explanations_implication(
                other=other.outputs, context=context
            )

        def other_inputs_implied(contexts: Iterable[ContextRegister]):
            for context in contexts:
                yield from self.inputs.explanations_implication(
                    other=other.inputs, context=context
                )

        def other_despite_implied(contexts: Iterable[ContextRegister]):
            despite_or_input = FactorGroup((*self.despite, *self.inputs))
            for context in contexts:
                yield from despite_or_input.explanations_implication(
                    other=other.despite, context=context
                )

        yield from other_despite_implied(
            other_inputs_implied(other_outputs_implied(context))
        )

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
        self, other: Procedure, context: ContextRegister
    ):
        def same_outputs(context: Optional[ContextRegister]):
            yield from self.outputs.explanations_same_meaning(
                other=other.outputs, context=context
            )

        def same_inputs(contexts: Iterable[ContextRegister]):
            for context in contexts:
                yield from self.inputs.explanations_same_meaning(
                    other=other.inputs, context=context
                )

        def same_despite(contexts: Iterable[ContextRegister]):
            for context in contexts:
                yield from self.despite.explanations_same_meaning(
                    other=other.despite, context=context
                )

        yield from same_despite(same_inputs(same_outputs(context)))

    def explanations_same_meaning(
        self, other: Factor, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        context = context or ContextRegister()
        if isinstance(other, self.__class__):
            yield from self._explanations_same_meaning_as_procedure(other, context)

    def means(self, other, context: Optional[ContextRegister] = None) -> bool:
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
        return self.__class__(**new_dict)

    def triggers_next_procedure(self, other: Procedure) -> List[ContextRegister]:
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
        self_despite_or_input = (*self.despite, *self.inputs)
        self_output_or_input = (*self.outputs, *self.inputs)

        relations = (
            Analogy(other.inputs, self_output_or_input, operator.le),
            Analogy(other.despite, self_despite_or_input, operator.le),
        )
        return all_analogy_matches(relations)

    def triggers_next_procedure_if_universal(
        self, other: Procedure
    ) -> List[ContextRegister]:
        r"""
        Test if Factors from firing `self` trigger `other` if both are universal.

        The difference from :func:`triggers_next_procedure` is that this
        function doesn't require the "despite" :class:`.Factor`\s to
        be addressed. If both calling :class:`.Rules`\s apply in "ALL"
        cases where their inputs are present, then it doesn't matter
        what Factors they apply "despite".

        :param other:
            another :class:`Procedure` to test to see whether it can
            be triggered by triggering ``self``

        :returns:
            whether the set of :class:`Factor`\s that exist after ``self``
            is fired could trigger ``other``
        """
        self_output_or_input = (*self.outputs, *self.inputs)

        relations = (Analogy(other.inputs, self_output_or_input, operator.le),)
        return all_analogy_matches(relations)

