"""
Statements of legal doctrines.

:class:`.Court`/s may posit them as holdings, and they
may describe procedural moves available in litigation.
"""

from __future__ import annotations
from copy import deepcopy

from typing import Any, ClassVar, Dict, Iterable, Iterator, Type
from typing import List, Optional, Sequence, Tuple, Union

from legislice.enactments import Enactment
from legislice.groups import EnactmentGroup

from nettlesome.terms import (
    Comparable,
    ContextRegister,
    Explanation,
    Term,
    TermSequence,
)
from nettlesome.factors import Factor
from nettlesome.formatting import indented
from authorityspoke.procedures import Procedure


class Rule(Comparable):
    r"""
    A statement of a legal doctrine about a :class:`.Procedure` for litigation.

    May decide some aspect of current litigation, and also potentially
    may be cided and reused by future courts. When :class:`Rule`\s appear as
    judicial holdings they are often hypothetical and don't necessarily
    imply that the court accepts the :class:`.Fact` assertions or other
    :class:`.Factor`\s that make up the inputs or outputs of the
    :class:`.Procedure` mentioned in the :class:`Rule`.

    :param procedure:
        a :class:`.Procedure` containing the inputs, and despite
        :class:`.Factor`\s and resulting outputs when this rule
        is triggered.

    :param enactments:
        the :class:`.Enactment`\s cited as authority for
        invoking the ``procedure``.

    :param enactments_despite:
        the :class:`.Enactment`\s specifically cited as failing
        to preclude application of the ``procedure``.

    :param mandatory:
        whether the ``procedure`` is mandatory for the
        court to apply whenever the :class:`.Rule` is properly invoked.
        ``False`` means that the ``procedure`` is "discretionary".

    :param universal:
        ``True`` if the ``procedure`` is applicable whenever
        its inputs are present. ``False`` means that the ``procedure`` is
        applicable in "some" situation where the inputs are present.

    :param generic:
        whether the :class:`Rule` is being mentioned in a generic
        context. e.g., if the :class:`Rule` is being mentioned in
        an :class:`~authorityspoke.Argument` object merely as an example of the
        kind of :class:`Rule` that might be mentioned in such an
        :class:`~authorityspoke..Argument`.

    :param name:
        an identifier used to retrieve this :class:`Rule` when
        needed for the composition of another :class:`.Factor`
        object.
    """

    context_factor_names: ClassVar[Tuple[str, ...]] = ("procedure",)
    enactment_attr_names: ClassVar[Tuple[str, ...]] = (
        "enactments",
        "enactments_despite",
    )

    def __init__(
        self,
        procedure: Procedure,
        enactments: Optional[
            Union[Enactment, EnactmentGroup, Sequence[Enactment]]
        ] = None,
        enactments_despite: Optional[
            Union[Enactment, EnactmentGroup, Sequence[Enactment]]
        ] = None,
        mandatory: bool = False,
        universal: bool = False,
        generic: bool = False,
        absent: bool = False,
        name: Optional[str] = None,
    ):
        self.procedure = procedure
        self.enactments = EnactmentGroup(enactments)
        self.enactments_despite = EnactmentGroup(enactments_despite)
        self.mandatory = mandatory
        self.universal = universal
        self.generic = generic
        self.absent = False
        self.name = name

        for enactment in self.enactments:
            if not enactment.selected_text():
                enactment.select_all()
        for despite in self.enactments_despite:
            if not despite.selected_text():
                despite.select_all()

    @property
    def despite(self):
        return self.procedure.despite

    @property
    def inputs(self):
        return self.procedure.inputs

    @property
    def outputs(self):
        return self.procedure.outputs

    @property
    def recursive_terms(self) -> Dict[str, Term]:
        r"""
        Collect `self`'s :attr:`terms`, and their :attr:`terms`, recursively.

        :returns:
            a :class:`dict` (instead of a :class:`set`,
            to preserve order) of :class:`Term`\s.
        """
        return self.procedure.recursive_terms

    def add(
        self,
        other: Comparable,
        context: Optional[Union[ContextRegister, Explanation]] = None,
    ) -> Optional[Rule]:
        if not isinstance(other, Rule):
            if isinstance(other, Factor):
                return self.with_factor(other)
            if isinstance(other, Enactment):
                return self.with_enactment(other)
            raise TypeError
        if self.universal is False and other.universal is False:
            return None

        if self.universal and other.universal:
            new_procedure = self.procedure._add_if_universal(
                other.procedure, explanation=context
            )
        else:
            new_procedure = self.procedure.add(other.procedure, context=context)

        new_enactments = self.enactments + other.enactments
        new_despite = self.enactments_despite + other.enactments_despite

        if new_procedure is not None:
            result = deepcopy(self)
            result.procedure = new_procedure
            result.universal = min(self.universal, other.universal)
            result.mandatory = min(self.mandatory, other.mandatory)
            result.enactments = new_enactments
            result.enactments_despite = new_despite
            return result
        return None

    def __add__(self, other) -> Optional[Rule]:
        r"""
        Create new :class:`Rule` if ``self`` can satisfy the :attr:`inputs` of ``other``.

        If both ``self`` and ``other`` have False for :attr:`universal`,
        then returns ``None``. Otherwise:

        If the union of the :attr:`inputs` and :attr:`outputs` of ``self``
        would trigger ``other``, then return a new version of ``self``
        with the output :class:`.Factor`\s of ``other`` as well as the
        outputs of ``self``.

        The new ``universal`` and ``mandatory`` values are the
        lesser of the old values for each.

        Does not test whether ``self`` could be triggered by the outputs
        of other. Use ``other + self`` for that.

        :param other:
            another :class:`Rule` to try to add to ``self``

        :returns:
            a combined :class:`Rule` that extends the procedural
            move made in ``self``, if possible. Otherwise ``None``.
        """
        return self.add(other)

    def get_contrapositives(self) -> Iterator[Rule]:
        r"""
        Make contrapositive forms of this :class:`Rule`.

        Used when converting from JSON input containing the entry
        ``"exclusive": True``, which means the specified :class:`~Rule.inputs``
        are the only way to reach the specified output. When that happens,
        it can be inferred that in the absence of any of the inputs, the output
        must also be absent. (Multiple :class:`~Rule.outputs` are not allowed
        when the ``exclusive`` flag is ``True``.) So, this generator will
        yield one new :class:`Rule` for each input.

        :returns:
            iterator yielding :class:`Rule`\s.
        """
        self.procedure.valid_for_exclusive_tag()

        for input_factor in self.inputs:
            result = deepcopy(self)
            next_input = deepcopy(input_factor)
            next_input.absent = not next_input.absent
            next_output = deepcopy(self.outputs[0])
            next_output.absent = True
            result.set_inputs(next_input)
            result.set_outputs(next_output)
            result.mandatory = not self.mandatory
            result.universal = not self.universal
            yield result

    @property
    def terms(self) -> TermSequence:
        """
        Call :class:`Procedure`\'s :meth:`~Procedure.terms` method.

        :returns:
            terms from ``self``'s :class:`Procedure`
        """
        return self.procedure.terms

    def generic_terms_by_str(self) -> Dict[str, Comparable]:
        r"""
        Get :class:`.Factor`\s that can be replaced without changing ``self``\s meaning.

        :returns:
            generic :class:`.Factor`\s from ``self``'s :class:`Procedure`
        """
        if self.generic:
            return {str(self): self}
        return self.procedure.generic_terms_by_str()

    def add_enactment(self, incoming: Enactment) -> None:
        """
        Add Enactment and sort self's Enactments.

        :param incoming:
            the new :class:`.Enactment` to be added to enactments

        :returns:
            None
        """
        if not isinstance(incoming, Enactment):
            raise TypeError

        new_enactments = self.enactments + incoming
        self.set_enactments(new_enactments)

    def add_enactment_despite(self, incoming: Enactment) -> None:
        r"""
        Add "despite" Enactment and sort self's "despite" Enactments.

        :param incoming:
            the new :class:`.Enactment` to be added to enactments_despite

        :returns:
            None
        """
        if not isinstance(incoming, Enactment):
            raise TypeError

        new_enactments = self.enactments_despite + incoming
        self.set_enactments(new_enactments)

    def with_enactment(self, incoming: Enactment) -> Rule:
        r"""
        Create new Rule with added Enactment.

        :param incoming:
            the new :class:`.Enactment` to be added to enactments_despite

        :returns:
            a new version of ``self`` with the specified change
        """
        if not isinstance(incoming, Enactment):
            raise TypeError

        new_enactments = self.enactments + incoming
        result = deepcopy(self)
        result.set_enactments(new_enactments)
        return result

    def with_enactment_despite(self, incoming: Enactment) -> Rule:
        r"""
        Create new Rule with added "despite" Enactment.

        :param incoming:
            the new :class:`.Enactment` to be added to enactments_despite

        :returns:
            a new version of ``self`` with the specified change
        """
        if not isinstance(incoming, Enactment):
            raise TypeError

        new_enactments = self.enactments_despite + incoming
        result = deepcopy(self)
        result.set_enactments_despite(new_enactments)
        return result

    def add_factor(self, incoming: Factor) -> None:
        """
        Add a :class:`.Factor` to self.inputs.

        :param incoming:
            the new :class:`.Factor` to be added to input
        """
        self.procedure.add_factor(incoming)
        return None

    def with_factor(self, incoming: Factor) -> Optional[Rule]:
        """
        Make new version of ``self`` with an added input :class:`.Factor`.

        :param incoming:
            the new :class:`.Factor` to be added to input

        :returns:
            a new version of ``self`` with the specified change
        """
        new_procedure = self.procedure.with_factor(incoming)
        if new_procedure is None:
            return None
        result = deepcopy(self)
        result.procedure = new_procedure
        return result

    def comparable_with(self, other: Any) -> bool:
        """Check if other can be compared to self for implication or contradiction."""
        if other and not isinstance(other, Comparable):
            return False
        if isinstance(other, Procedure):
            return False
        return not isinstance(other, Factor)

    def contradicts(
        self, other: Optional[Comparable], context: Optional[ContextRegister] = None
    ) -> bool:
        """
        Test if ``self`` contradicts ``other``.

        :returns:
            whether ``self`` contradicts ``other``, if each is posited by a
            :class:`.Holding` with :attr:`~Holding.rule_valid``
            and :attr:`~Holding.decided`
        """

        if not self.comparable_with(other):
            raise TypeError(
                f'"contradicts" test not supported between class {self.__class__} and class {other.__class__}.'
            )

        if context is None:
            context = ContextRegister()

        if not isinstance(other, self.__class__):
            if other and hasattr(other, "contradicts"):
                return other.contradicts(self, context=context.reversed())
            return False

        if not self.mandatory and not other.mandatory:
            return False

        if not self.universal and not other.universal:
            return False

        return any(
            register is not None
            for register in self.explanations_contradiction(other, context)
        )

    def _explanations_contradiction(
        self, other, context: Explanation
    ) -> Iterator[Explanation]:
        self_to_other = self.procedure.explain_contradiction_some_to_all(
            other.procedure, context
        )
        other_to_self = (
            register.reversed_context()
            for register in other.procedure.explain_contradiction_some_to_all(
                self.procedure, context.reversed_context()
            )
        )

        if other.universal:
            yield from self_to_other

        if self.universal:
            yield from other_to_self

    def explanations_contradiction(
        self, other, context: Optional[Union[ContextRegister, Explanation]] = None
    ) -> Iterator[ContextRegister]:
        """Find context matches that would result in a contradiction with other."""
        if not isinstance(context, Explanation):
            context = Explanation.from_context(context)

        yield from self._explanations_contradiction(other=other, context=context)

    def needs_subset_of_enactments(self, other) -> bool:
        r"""
        Test whether ``self``\'s :class:`.Enactment` support is a subset of ``other``\'s.

        A :class:`Rule` makes a more powerful statement if it relies on
        fewer :class:`.Enactment`\s (or applies despite more :class:`.Enactment`\s).

        So this method must return ``True`` for ``self`` to imply ``other``.
        """

        if not all(
            any(other_e >= e for other_e in other.enactments) for e in self.enactments
        ):
            return False

        if not all(
            any(e >= other_d for e in self.enactments + self.enactments_despite)
            for other_d in other.enactments_despite
        ):
            return False
        return True

    def explanations_implication(
        self, other, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        if (
            self.needs_subset_of_enactments(other)
            and self.mandatory >= other.mandatory
            and self.universal >= other.universal
        ):

            if self.universal > other.universal:
                yield from self.procedure.explain_implication_all_to_some(
                    other.procedure, context
                )

            elif other.universal:
                yield from self.procedure.explain_implication_all_to_all(
                    other.procedure, context
                )

            else:
                yield from self.procedure.explanations_implication(
                    other.procedure, context
                )

    def implies(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> bool:
        r"""
        Test if ``self`` implies ``other`` if posited in valid and decided :class:`.Holding`\s.

        If ``self`` relies for support on some :class:`.Enactment` text
        that ``other`` doesn't, then ``self`` doesn't imply ``other``.

        Also, if ``other`` specifies that it applies notwithstanding
        some :class:`.Enactment` not mentioned by ``self``, then
        ``self`` doesn't imply ``other``.

        This will be called as part of the
        :meth:`Holding.__ge__` implication function.

        :returns:
            whether ``self`` implies ``other``, assuming that
            both are :class:`Rule`/s, and
            ``rule_valid`` and ``decided`` are ``True`` for both of them.
        """
        if not self.comparable_with(other):
            raise TypeError(
                f'"implies" test not supported between class {self.__class__} and class {other.__class__}.'
            )
        if not isinstance(other, self.__class__):
            if context:
                context = context.reversed()
            return other.implied_by(self, context=context)
        return any(
            explanation is not None
            for explanation in self.explanations_implication(other, context)
        )

    def __ge__(self, other: Optional[Factor]) -> bool:
        return self.implies(other)

    def __len__(self):
        r"""
        Count generic :class:`.Factor`\s needed as context for this :class:`Rule`.

        :returns:
            the number of generic :class:`.Factor`\s needed for
            self's :class:`.Procedure`.
        """

        return len(self.procedure)

    def has_all_same_enactments(self, other: Rule) -> bool:
        r"""
        Test if ``self`` has :class:`.Enactment`\s with same meanings as ``other``\'s.

        :param other:
            another :class:`Rule` to compare to ``self``.

        :returns:
            whether the :meth:`~.Enactment.means` test passes for all :class:`.Enactment`\s
        """
        for enactment_group in self.enactment_attr_names:
            if not all(
                any(other_e.means(self_e) for self_e in self.__dict__[enactment_group])
                for other_e in other.__dict__[enactment_group]
            ):
                return False
        return True

    def explanations_same_meaning(
        self, other: Optional[Factor], context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        """Find context matches that would result in self and other meaning the same."""
        if (
            isinstance(other, Rule)
            and self.has_all_same_enactments(other)
            and other.has_all_same_enactments(self)
            and self.mandatory == other.mandatory
            and self.universal == other.universal
        ):
            yield from self.procedure.explanations_same_meaning(
                other.procedure, context
            )

    def means(
        self, other: Optional[Factor], context: Optional[ContextRegister] = None
    ) -> bool:
        """
        Test whether ``other`` has the same meaning as ``self``.

        :returns:
            whether ``other`` is a :class:`Rule` with the
            same meaning as ``self``.
        """
        return any(
            explanation is not None
            for explanation in self.explanations_same_meaning(other, context)
        )

    def _union_with_rule(self, other: Rule, context: ContextRegister) -> Optional[Rule]:
        new_procedure = self.procedure.union(other.procedure, context=context)
        if new_procedure is None:
            return None

        enactments = self.enactments + other.enactments
        enactments_despite = self.enactments_despite + other.enactments_despite

        if self.procedure.implies_all_to_all(
            other.procedure, context=context
        ) or other.procedure.implies_all_to_all(self.procedure, context=context):
            return Rule(
                procedure=new_procedure,
                enactments=enactments,
                enactments_despite=enactments_despite,
                mandatory=max(self.mandatory, other.mandatory),
                universal=max(self.universal, other.universal),
            )

        if self.universal is other.universal is False:
            return None

        return Rule(
            procedure=new_procedure,
            enactments=enactments,
            enactments_despite=enactments_despite,
            mandatory=min(self.mandatory, other.mandatory),
            universal=min(self.universal, other.universal),
        )

    def union(
        self, other: Optional[Rule], context: Optional[ContextRegister] = None
    ) -> Optional[Rule]:
        if other is None:
            return self
        context = context or ContextRegister()
        if isinstance(other, Rule):
            return self._union_with_rule(other, context=context)
        elif hasattr(other, "union") and hasattr(other, "rule"):
            return other.union(self, context=context.reversed())
        raise TypeError(f"Union operation not possible between Rule and {type(other)}.")

    def __or__(self, other: Rule) -> Optional[Rule]:
        r"""
        Create new :class:`Rule` showing combined effect of all inputs of ``self`` and ``other``.

        This operation is destructive in the sense that the new :class:`Rule` may not
        contain all the information that was available in ``self`` and ``other``.

        This seems to work differently when one Rule
        implies the other. That could mean there is a
        union to return even when both Rules are SOME
        rules. Or it could mean an ALL rule should be
        returned even though ``implied`` is SOME, because
        implied contributes no information that wasn't
        already in ``greater``.

        :param other: a :class:`Rule` to be combined with ``self``.

        :returns:
            a :class:`Rule` indicating the combined effect of the ``input`` and ``despite``
            :class:`.Factor`\s of ``self`` and ``other``
        """
        return self.union(other)

    def set_inputs(self, factors: Sequence[Factor]) -> None:
        self.procedure.set_inputs(factors)

    def set_despite(self, factors: Sequence[Factor]) -> None:
        self.procedure.set_despite(factors)

    def set_outputs(self, factors: Sequence[Factor]) -> None:
        self.procedure.set_outputs(factors)

    def set_enactments(
        self, enactments: Union[Enactment, Sequence[Enactment], EnactmentGroup]
    ) -> None:
        self.enactments = EnactmentGroup(enactments)

    def set_enactments_despite(
        self, enactments: Union[Enactment, Sequence[Enactment], EnactmentGroup]
    ) -> None:
        self.enactments_despite = EnactmentGroup(enactments)

    def __str__(self):
        mandatory = "MUST" if self.mandatory else "MAY"
        universal = "ALWAYS" if self.universal else "SOMETIMES"
        text = (
            f"the Rule that the court {mandatory} {universal} impose the\n"
            + indented(str(self.procedure))
        )
        if self.enactments:
            text += f"\n  GIVEN the ENACTMENT"
            if len(self.enactments) > 1:
                text += "S"
            text += ":"
            for enactment in self.enactments:
                text += "\n" + indented(str(enactment), tabs=2)
        if self.enactments_despite:
            text += f"\n  DESPITE the ENACTMENT"
            if len(self.enactments_despite) > 1:
                text += "S"
            text += ":"
            for despite in self.enactments_despite:
                text += "\n" + indented(str(despite), tabs=2)
        return text


class Attribution:
    """
    An assertion about the meaning of a prior :class:`.Opinion`.

    Either a user or an :class:`.Opinion` may make an Attribution
    to an :class:`.Opinion`. An Attribution may attribute either a
    :class:`.Rule` or a further Attribution.
    """
