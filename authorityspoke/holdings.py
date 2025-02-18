r"""
:class:`Holding`\s describe :class:`.Opinion`\s` attitudes toward :class:`.Rule`\s.

:class:`Holding`\s are text passages within :class:`.Opinion`\s
in which :class:`.Court` posits, or rejects, the validity of a
:class:`.Rule` within the :class:`.Court`\'s :class:`.Jurisdiction`,
or the :class:`.Court` asserts that the validity of the :class:`.Rule`
should be considered undecided.
"""

from __future__ import annotations
from copy import deepcopy

from itertools import chain
import operator
from typing import Any, Callable, Dict, Iterable, Iterator, List
from typing import Optional, Sequence, Union

from legislice.enactments import Enactment

from nettlesome.terms import (
    Comparable,
    ContextRegister,
    Explanation,
    FactorMatch,
    Term,
    TermSequence,
    contradicts,
    new_context_helper,
)
from nettlesome.factors import Factor
from nettlesome.formatting import indented, wrapped
from nettlesome.groups import FactorGroup

from pydantic import field_validator, model_validator, BaseModel, validator

from authorityspoke.procedures import Procedure
from authorityspoke.rules import Rule, RawRule

RawHolding = Dict[str, Union[RawRule, str, bool]]


class Holding(Comparable, BaseModel):
    """
    An :class:`.Opinion`\'s announcement that it posits or rejects a legal :class:`.Rule`.

    Note that if an opinion merely says the court is not deciding whether
    a :class:`.Rule` is valid, there is no :class:`Holding`, and no
    :class:`.Rule` object should be created. Deciding not to decide
    a :class:`Rule`\'s validity is not the same thing as deciding
    that the :class:`.Rule` is undecided.

    :param rule:
        a statement of a legal doctrine about a :class:`.Procedure` for litigation.

    :param rule_valid:
        ``True`` means the :class:`.Rule` is asserted to be valid (or
        useable by a court in litigation). ``False`` means it's asserted
        to be invalid.

    :param decided:
        ``False`` means that it should be deemed undecided
        whether the :class:`.Rule` is valid, and thus can have the
        effect of overruling prior holdings finding the :class:`.Rule`
        to be either valid or invalid. Seemingly, ``decided=False``
        should render the ``rule_valid`` flag irrelevant.

    :param exclusive:
        if True, the stated rule is asserted to be the only way to establish
        the output that is the output of the rule.

    :param generic:
        if True, indicates that the specific attributes of this holding
        are irrelevant in the context of a different holding that is
        referencing this holding.
    """

    rule: Rule
    rule_valid: bool = True
    decided: bool = True
    exclusive: bool = False
    generic: bool = False

    @model_validator(mode="before")
    @classmethod
    def nest_factor_fields(cls, values):
        """Move misplaced fields that belong on Rule or Predicate models."""
        for field_name in ["inputs", "outputs", "despite"]:
            if field_name in values:
                values["procedure"] = values.get("procedure", {})
                values["procedure"][field_name] = values.pop(field_name)
        values["rule"] = values.get("rule", {})

        for field_to_nest in [
            "procedure",
            "enactments",
            "enactments_despite",
            "universal",
            "mandatory",
        ]:
            if field_to_nest in values:
                values["rule"][field_to_nest] = values.pop(field_to_nest)
        return values

    @field_validator("exclusive")
    def not_invalid_and_exclusive(cls, v: bool, values) -> bool:
        """Block "exclusive" flag from being used when "rule_valid" is False."""
        if v and not values.data["rule_valid"]:
            raise NotImplementedError(
                "The ability to state that it is not 'valid' to assert "
                + "that a Rule is the 'exclusive' way to reach an output is "
                + "not implemented, so 'rule_valid' cannot be False while "
                + "'exclusive' is True. Try expressing this in another way "
                + "without the 'exclusive' keyword."
            )
        return v

    @field_validator("exclusive")
    def not_undecided_and_exclusive(cls, v: bool, values) -> bool:
        """Block "exclusive" flag from being used when "decided" is False."""
        if v:
            if not values.data["decided"]:
                raise NotImplementedError(
                    "The ability to state that it is not 'decided' whether "
                    + "a Rule is the 'exclusive' way to reach an output is "
                    + "not implemented. Try expressing this in another way "
                    + "without the 'exclusive' keyword."
                )
            values.data["rule"].procedure.valid_for_exclusive_tag()
        return v

    @classmethod
    def from_factors(
        self,
        outputs: FactorGroup,
        inputs: Optional[FactorGroup] = None,
        despite: Optional[FactorGroup] = None,
        enactments: Sequence[Enactment] = (),
        enactments_despite: Sequence[Enactment] = (),
        mandatory: bool = False,
        universal: bool = False,
        generic: bool = False,
        decided: bool = True,
        exclusive: bool = False,
        absent: bool = False,
    ):
        """Create new Holding without an existing Rule or Procedure."""
        procedure = Procedure(inputs=inputs, outputs=outputs, despite=despite)
        rule = Rule(
            procedure=procedure,
            enactments=enactments,
            enactments_despite=enactments_despite,
            mandatory=mandatory,
            universal=universal,
        )
        return Holding(rule=rule, generic=generic, decided=decided, exclusive=exclusive)

    @property
    def procedure(self):
        """Get Procedure from Rule."""
        return self.rule.procedure

    @property
    def despite(self):
        """Get Factors that specifically don't preclude application of the Holding."""
        return self.rule.procedure.despite_group

    @property
    def inputs(self):
        """Get inputs from Procedure."""
        return self.rule.procedure.inputs_group

    @property
    def outputs(self):
        """Get outputs from Procedure."""
        return self.rule.procedure.outputs_group

    @property
    def enactments(self):
        """Get Enactments required to apply the Holding."""
        return self.rule.enactments

    @property
    def enactments_despite(self):
        """Get Enactments that specifically don't preclude application of the Holding."""
        return self.rule.enactments_despite

    @property
    def recursive_terms(self) -> Dict[str, Term]:
        r"""
        Collect `self`'s :attr:`terms`, and their :attr:`terms`, recursively.

        :returns:
            a :class:`dict` (instead of a :class:`set`,
            to preserve order) of :class:`Term`\s.
        """
        return self.rule.recursive_terms

    @property
    def terms(self) -> TermSequence:
        r"""
        Call :class:`Procedure`\'s :meth:`~Procedure.terms` method.

        :returns:
            terms from ``self``'s :class:`Procedure`
        """
        return self.rule.procedure.terms

    def generic_terms_by_str(self) -> Dict[str, Comparable]:
        r"""
        Get :class:`.Factor`\s that can be replaced without changing ``self``\s meaning.

        :returns:
            generic :class:`.Factor`\s from ``self``'s :class:`Procedure`
        """
        return self.rule.generic_terms_by_str()

    @property
    def mandatory(self) -> bool:
        """Whether court "MUST" apply holding when it is applicable."""
        return self.rule.mandatory

    @property
    def universal(self) -> bool:
        """Whether holding is applicable in "ALL" cases where inputs are present."""
        return self.rule.universal

    def add_if_not_exclusive(self, other: Holding) -> Optional[Holding]:
        """Show how first Holding triggers second, assumed not to be "exclusive" way to reach result."""
        new_rule = self.rule + other.rule
        if new_rule is None:
            return None
        new_holding = deepcopy(self)
        new_holding.rule = new_rule
        return new_holding

    def add_enactment(self, enactment: Enactment) -> None:
        """Add enactment and sort self's Enactments."""
        self.rule.add_enactment(enactment)

    def add_enactment_despite(self, enactment: Enactment) -> None:
        """Add "despite" enactment and sort self's "despite" Enactments."""
        self.rule.add_enactment_despite(enactment)

    def add_holding(self, other: Holding) -> Optional[Holding]:
        """Show how first Holding triggers the second."""
        if not (self.decided and other.decided):
            raise NotImplementedError(
                "Adding is not implemented for Holdings that assert a Rule is not decided."
            )
        if not (self.rule_valid and other.rule_valid):
            raise NotImplementedError(
                "Adding is not implemented for Holdings that assert a Rule is not valid."
            )
        for self_holding in self.nonexclusive_holdings:
            for other_holding in other.nonexclusive_holdings:
                added = self_holding.add_if_not_exclusive(other_holding)
                if added is not None:
                    return added
        return None

    def __add__(self, other: Comparable) -> Optional[Union[Rule, Holding]]:
        """
        Create new Holding combining self and other into a single step, if possible.

        The Holdings can be combined only if the application of Holding ``self``
        necessarily provides all the required inputs for the application of ``other``.
        """
        if isinstance(other, Rule):
            other = Holding(rule=other)
        if isinstance(other, Holding):
            return self.add_holding(other)
        new_rule = self.rule + other
        if new_rule is None:
            return None
        result = deepcopy(self)
        result.rule = new_rule
        return result

    def _explanations_contradiction_of_holding(
        self, other: Holding, context: Explanation
    ) -> Iterator[Explanation]:
        for self_holding in self.nonexclusive_holdings:
            for other_holding in other.nonexclusive_holdings:
                for explanation in self_holding._contradicts_if_not_exclusive(
                    other_holding, context=context
                ):
                    explanation.reasons = [
                        HoldingMatch(
                            left=self_holding,
                            operation=contradicts,
                            right=other_holding,
                        )
                    ]
                    yield explanation

    def explanations_contradiction(
        self, other: Factor, context: ContextRegister = None
    ) -> Iterator[Explanation]:
        r"""
        Find context matches that would result in a contradiction with other.

        Works by testing whether ``self`` would imply ``other`` if
        ``other`` had an opposite value for ``rule_valid``.

        This method takes three main paths depending on
        whether the holdings ``self`` and ``other`` assert that
        rules are decided or undecided.

        A ``decided`` :class:`Rule` can never contradict
        a previous statement that any :class:`Rule` was undecided.

        If rule A implies rule B, then a holding that B is undecided
        contradicts a prior :class:`Rule` deciding that
        rule A is valid or invalid.

        :param other:
            The :class:`.Factor` to be compared to self. Unlike with
            :meth:`~Holding.contradicts`\, this method cannot be called
            with an :class:`.Opinion` for `other`.

        :returns:
            a generator yielding :class:`.ContextRegister`\s that cause a
            contradiction.
        """
        if not self.comparable_with(other):
            raise TypeError(f"Type Holding cannot be compared with type {type(other)}.")
        if not isinstance(context, Explanation):
            context = Explanation.from_context(context)
        if isinstance(other, Procedure):
            other = Rule(procedure=other)
        if isinstance(other, Rule):
            other = Holding(rule=other)
        if isinstance(other, self.__class__):
            yield from self._explanations_contradiction_of_holding(other, context)
        else:
            yield from other.explanations_contradiction(self)

    def _contradicts_if_not_exclusive(
        self, other: Holding, context: Explanation
    ) -> Iterator[Explanation]:
        if isinstance(other, Holding) and other.decided:
            if self.decided:
                yield from self._explanations_implies_if_not_exclusive(
                    other.negated(), context=context
                )
            else:
                yield from chain(
                    other._implies_if_decided(self, context=context),
                    other._implies_if_decided(self.negated(), context=context),
                )

    def _explanations_implies_if_not_exclusive(
        self, other: Factor, context: Explanation
    ) -> Iterator[Explanation]:
        if self.decided and other.decided:
            yield from self._implies_if_decided(other, context)

        # A holding being undecided doesn't seem to imply that
        # any other holding is undecided, except itself and the
        # negation of itself.

        # It doesn't seem that any holding being undecided implies
        # that any holding is decided, or vice versa.

        elif not self.decided and not other.decided:
            yield from chain(
                self.explanations_same_meaning(other, context),
                self.explanations_same_meaning(other.negated(), context),
            )

    def __ge__(self, other: Optional[Factor]) -> bool:
        return self.implies(other)

    def comparable_with(self, other: Any) -> bool:
        """Check if other can be compared to self for implication or contradiction."""
        if other and not isinstance(other, Comparable):
            return False
        return not isinstance(other, Factor)

    def implies(
        self, other: Optional[Comparable], context: ContextRegister = None
    ) -> bool:
        r"""
        Test for implication.

        See :meth:`.Procedure.implies_all_to_all`
        and :meth:`.Procedure.implies_all_to_some` for
        explanations of how ``inputs``, ``outputs``,
        and ``despite`` :class:`.Factor`\s affect implication.

        :param other:
            A :class:`Holding` to compare to self, or a :class:`.Rule` to
            convert into such a :class:`Holding` and then compare

        :returns:
            whether ``self`` implies ``other``
        """
        if other is None:
            return True
        return any(
            explanation is not None
            for explanation in self.explanations_implication(other, context)
        )

    def explanations_implication(
        self,
        other: Comparable,
        context: Optional[Union[ContextRegister, Explanation]] = None,
    ) -> Iterator[Explanation]:
        """Yield contexts that would cause self and other to have same meaning."""
        if not self.comparable_with(other):
            raise TypeError(f"Type Holding cannot be compared with type {type(other)}.")
        if not isinstance(context, Explanation):
            context = Explanation.from_context(context)
        if isinstance(other, Procedure):
            other = Rule(procedure=other)
        if isinstance(other, Rule):
            other = Holding(rule=other)
        if not isinstance(other, self.__class__):
            if context:
                context = context.reversed_context()
            if other.implied_by(self, context=context):
                yield context
        elif self.exclusive is other.exclusive is False:
            yield from self._explanations_implies_if_not_exclusive(
                other, context=context
            )
        else:
            yield from self.nonexclusive_holdings.explanations_implication(
                other.nonexclusive_holdings, context=context
            )

    def implied_by(
        self, other: Factor, context: Optional[ContextRegister] = None
    ) -> bool:
        r"""
        Test if other implies self.

        This function is for handling implication checks for classes
        that don't know the structure of the :class:`Holding` class,
        such as :class:`.Fact` and :class:`.Rule`\.
        """
        if context:
            context = context.reversed()
        if isinstance(other, Rule):
            return Holding(rule=other).implies(self, context=context)
        return other.implies(self, context=context)

    def _implies_if_decided(
        self, other: Holding, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        r"""
        Test if ``self`` implies ``other`` if they're both decided.

        This is a partial version of the
        :meth:`Holding.__ge__` implication function.

        :returns:
            whether ``self`` implies ``other``, assuming that
            ``self.decided == other.decided == True`` and that
            ``self`` and ``other`` are both :class:`Holding`\s,
            although ``rule_valid`` can be ``False``.
        """

        if self.rule_valid and other.rule_valid:
            yield from self.rule.explanations_implication(other.rule, context)

        elif not self.rule_valid and not other.rule_valid:
            yield from other.rule.explanations_implication(self.rule, context)

        # Looking for implication where self.rule_valid != other.rule_valid
        # is equivalent to looking for contradiction.

        # If decided rule A contradicts B, then B also contradicts A

        else:
            yield from self.rule._explanations_contradiction(other.rule, context)

    def __len__(self):
        r"""
        Count generic :class:`.Factor`\s needed as context for this :class:`Holding`.

        :returns:
            the number of generic :class:`.Factor`\s needed for
            self's :class:`.Procedure`.
        """

        return len(self.rule.procedure)

    @property
    def inferred_from_exclusive(self) -> List[Holding]:
        r"""
        Yield :class:`Holding`\s that can be inferred from the "exclusive" flag.

        The generator will be empty if `self.exclusive` is False.
        """
        if self.exclusive:
            return [
                Holding(rule=modified_rule)
                for modified_rule in self.rule.get_contrapositives()
            ]
        return []

    def explanations_same_meaning(
        self, other: Factor, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        """Yield contexts that would cause self and other to have same meaning."""
        if (
            isinstance(other, self.__class__)
            and self.rule_valid == other.rule_valid
            and self.decided == other.decided
        ):
            yield from self.rule.explanations_same_meaning(other.rule, context)

    def negated(self):
        """Get new copy of ``self`` with an opposite value for ``rule_valid``."""
        result = deepcopy(self)
        result.rule_valid = not self.rule_valid
        result.exclusive = False
        return result

    @new_context_helper
    def new_context(self, changes: ContextRegister) -> Factor:
        """
        Create new :class:`Holding`, replacing keys of ``changes`` with values.

        :returns:
            a version of ``self`` with the new context.
        """
        return Holding(
            rule=self.rule.new_context(changes),
            rule_valid=self.rule_valid,
            decided=self.decided,
        )

    @property
    def nonexclusive_holdings(self) -> HoldingGroup:
        r"""Yield all :class:`.Holding`\s with `exclusive is False` implied by self."""
        if not self.exclusive:
            return HoldingGroup([self])
        nonexclusive_holding = deepcopy(self)
        nonexclusive_holding.exclusive = False
        holdings = [nonexclusive_holding] + self.inferred_from_exclusive
        return HoldingGroup(holdings)

    def set_inputs(self, factors: Sequence[Factor]) -> None:
        """Set inputs of this Holding."""
        self.rule.set_inputs(factors)

    def set_despite(self, factors: Sequence[Factor]) -> None:
        """Set Factors that specifically do not preclude applying this Holding."""
        self.rule.set_despite(factors)

    def set_outputs(self, factors: Sequence[Factor]) -> None:
        """Set outputs of this Holding."""
        self.rule.set_outputs(factors)

    def set_enactments(self, enactments: Sequence[Enactment]) -> None:
        """Set Enactments required to apply this Holding."""
        self.rule.set_enactments(enactments)

    def set_enactments_despite(self, enactments: Sequence[Enactment]) -> None:
        """Set Enactments that specifically do not preclude applying this Holding."""
        self.rule.set_enactments_despite(enactments)

    def _union_if_not_exclusive(
        self, other: Holding, context: ContextRegister
    ) -> Optional[Holding]:
        if self.decided is other.decided is False:
            if self.rule.implies(other.rule, context=context):
                return other
            if other.rule.implies(self.rule, context=context.reversed()):
                return self
            return None

        if not self.decided or not other.decided:
            return None
        if self.rule_valid != other.rule_valid:
            return None

        if self.rule_valid is False:
            # If a Rule with input A present is not valid
            # and a Rule with input A absent is also not valid
            # then a version of the Rule with input A
            # omitted is also not valid.
            raise NotImplementedError(
                "The union operation is not yet implemented for Holdings "
                "that assert a Rule is not valid."
            )

        new_rule = self.rule.union(other.rule, context=context)
        if not new_rule:
            return None
        result = deepcopy(self)
        result.rule = new_rule
        result.exclusive = False
        return result

    def _union_with_holding(
        self, other: Holding, context: ContextRegister
    ) -> Optional[Holding]:
        for self_holding in self.nonexclusive_holdings:
            for other_holding in other.nonexclusive_holdings:
                united = self_holding._union_if_not_exclusive(
                    other_holding, context=context
                )
                if united is not None:
                    return united
        return None

    def union(
        self, other: Union[Rule, Holding], context: Optional[ContextRegister] = None
    ) -> Optional[Holding]:
        """
        Infer a Holding from all inputs and outputs of self and other, in context.

        Creates a new Holding with all of the inputs and all of the outputs
        of both of the two original Holdings.

        However, you only get such a new Holding if it can be inferred by
        accepting the truth of the two original Holdings.

        If self contradicts() other, the operation returns None. Likewise, if
        the two original Holdings both have the value False for the parameter
        universal, the operation will return None if it’s possible that the
        “SOME” cases where one of the original Holdings applies don’t
        overlap with the “SOME” cases where the other applies.
        """
        context = context or ContextRegister()
        if isinstance(other, Rule):
            other = Holding(rule=other)
        if not isinstance(other, Holding):
            raise TypeError
        return self._union_with_holding(other, context=context)

    def __or__(self, other: Union[Rule, Holding]) -> Optional[Holding]:
        """Infer a Holding from all inputs and outputs of self and other."""
        return self.union(other)

    def __str__(self):
        action = (
            "consider UNDECIDED"
            if not self.decided
            else ("ACCEPT" if self.rule_valid else "REJECT")
        )
        exclusive = (
            (f" that the EXCLUSIVE way to reach {self.rule.outputs[0].short_string} is")
            if self.exclusive
            else ""
        )
        rule_text = indented(str(self.rule))
        return wrapped(f"the Holding to {action}{exclusive}") + f"\n{rule_text}"


class HoldingMatch(FactorMatch):
    """A logical relation between two holdings, e.g. implies, contradicts."""

    left: Holding
    operation: Callable
    right: Holding


class HoldingGroup(FactorGroup):
    """Group of Holdings that can be compared as a group with other Holdings."""

    term_class = Holding

    def __init__(self, holdings: Union[Sequence[Holding], Holding] = ()):
        """Validate that HoldingGroup is created from a sequence of Holdings."""
        if isinstance(holdings, Iterable):
            holdings = tuple(holdings)
        else:
            holdings = (holdings,)
        if any(not isinstance(holding, Holding) for holding in holdings):
            raise TypeError("All objects in HoldingGroup must be type Holding.")
        self.sequence = holdings

    def _explanations_implication_of_holding(
        self, other: Holding, context: Explanation
    ) -> Iterator[Explanation]:
        for self_holding in self.sequence:
            for result in self_holding.explanations_implication(other, context=context):
                yield result.with_match(
                    FactorMatch(left=self_holding, operation=operator.ge, right=other)
                )

    def explanations_implication(
        self,
        other: Comparable,
        context: Optional[Union[ContextRegister, Explanation]] = None,
    ) -> Iterator[Explanation]:
        """Generate contexts in which all Holdings in other are implied by self."""
        if isinstance(other, Rule):
            other = Holding(rule=other)
        explanation = Explanation.from_context(
            context=context, current=self, incoming=other
        )
        if isinstance(other, Holding):
            yield from self._explanations_implication_of_holding(
                other=other, context=context
            )
        elif isinstance(other, self.__class__):
            yield from self.verbose_comparison(
                operation=operator.ge,
                still_need_matches=list(other),
                explanation=explanation,
            )

    def verbose_comparison(
        self,
        operation: Callable,
        still_need_matches: Sequence[Factor],
        explanation: Explanation,
    ) -> Iterator[Explanation]:
        r"""
        Find one way for two unordered sets of :class:`.Factor`\s to satisfy a comparison.

        All of the elements of `other` need to fit the comparison. The elements of
        `self` don't all need to be used.

        Only returns one answer, to prevent expensive fruitless searching.

        :param context:
            a mapping of :class:`.Factor`\s that have already been matched
            to each other in the recursive search for a complete group of
            matches. Usually starts empty when the method is first called.

        :param still_need_matches:
            :class:`.Factor`\s that need to satisfy the comparison
            :attr:`comparison` with some :class:`.Factor` of :attr:`available`
            for the relation to hold, and have not yet been matched.

        :param explanation:
            an :class:`.Explanation` showing which :class:`.Factor`\s listed in the
            FactorGroups were matched to each other, and also including a
            :class:`.ContextRegister`\.

        :yields:
            context registers showing how each :class:`.Factor` in
            ``need_matches`` can have the relation ``comparison``
            with some :class:`.Factor` in ``available_for_matching``,
            with matching context.
        """
        still_need_matches = list(still_need_matches)

        if not still_need_matches:
            yield explanation
        else:
            other_holding = still_need_matches.pop()
            for self_holding in self:
                if operation(self_holding, other_holding):
                    new_explanation = explanation.with_match(
                        FactorMatch(
                            left=self_holding,
                            operation=explanation.operation,
                            right=other_holding,
                        )
                    )
                    next_step = iter(
                        self.verbose_comparison(
                            still_need_matches=still_need_matches,
                            operation=operation,
                            explanation=new_explanation,
                        )
                    )
                    yield next(next_step)
