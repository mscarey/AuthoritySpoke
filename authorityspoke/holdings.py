r"""
:class:`Holding`\s describe :class:`.Opinion`\s` attitudes toward :class:`.Rule`\s.

:class:`Holding`\s are text passages within :class:`.Opinion`\s
in which :class:`.Court` posits, or rejects, the validity of a
:class:`.Rule` within the :class:`.Court`\'s :class:`.Jurisdiction`,
or the :class:`.Court` asserts that the validity of the :class:`.Rule`
should be considered undecided.
"""

from __future__ import annotations

from typing import Any, ClassVar, Dict, Iterable, List, Tuple
from typing import Iterator, Optional, Union

from dataclasses import dataclass

from authorityspoke.context import new_context_helper
from authorityspoke.enactments import Enactment
from authorityspoke.factors import Factor
from authorityspoke.procedures import Procedure
from authorityspoke.rules import Rule
from authorityspoke.selectors import TextQuoteSelector


@dataclass(frozen=True)
class Holding(Factor):
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

    :param selector:
        A text selector for the whole :class:`Holding`, not for any
        individual :class:`.Factor`. Often selects text used to
        indicate whether the :class:`.Rule` is ``mandatory``, ``universal``,
        ``valid``, or ``decided``, or shows the ``exclusive`` way to reach
        the outputs.
    """

    rule: Optional[Rule] = None
    rule_valid: bool = True
    decided: bool = True
    selectors: Union[Iterable[TextQuoteSelector], TextQuoteSelector] = ()
    name: Optional[str] = None
    procedure: Optional[Procedure] = None
    outputs: Optional[Union[Factor, Iterable[Factor]]] = None
    inputs: Optional[Union[Factor, Iterable[Factor]]] = None
    despite: Optional[Union[Factor, Iterable[Factor]]] = None
    enactments: Optional[Union[Enactment, Iterable[Enactment]]] = None
    enactments_despite: Optional[Union[Enactment, Iterable[Enactment]]] = None
    mandatory: bool = False
    universal: bool = False

    generic: ClassVar = False

    def __post_init__(self):
        if self.rule is None:
            rule = Rule(
                procedure=self.procedure,
                outputs=self.outputs,
                inputs=self.inputs,
                despite=self.despite,
                enactments=self.enactments,
                enactments_despite=self.enactments_despite,
                mandatory=self.mandatory,
                universal=self.universal,
            )
            object.__setattr__(self, "rule", rule)
        elif not (
            self.procedure
            == self.enactments
            == self.enactments_despite
            == self.universal
            == self.mandatory
            == None
        ):
            new_rule = Rule(
                procedure=self.procedure or self.rule.procedure,
                enactments=self.enactments or self.rule.enactments,
                enactments_despite=self.enactments_despite
                or self.rule.enactments_despite,
                mandatory=self.mandatory or self.rule.mandatory,
                universal=self.universal or self.rule.universal,
            )
            object.__setattr__(self, "rule", new_rule)
        object.__setattr__(self, "procedure", self.rule.procedure)
        object.__setattr__(self, "outputs", self.rule.procedure.outputs)
        object.__setattr__(self, "inputs", self.rule.procedure.inputs)
        object.__setattr__(self, "despite", self.rule.procedure.despite)
        object.__setattr__(self, "enactments", self.rule.enactments)
        object.__setattr__(self, "enactments_despite", self.rule.enactments_despite)
        object.__setattr__(self, "mandatory", self.rule.mandatory)
        object.__setattr__(self, "universal", self.rule.universal)
        if isinstance(self.selectors, Iterable):
            object.__setattr__(self, "selectors", tuple(self.selectors))
        elif isinstance(self.selectors, TextQuoteSelector):
            object.__setattr__(self, "selectors", (self.selectors,))


    @property
    def context_factors(self) -> Tuple:
        r"""
        Call :class:`Procedure`\'s :meth:`~Procedure.context_factors` method.

        :returns:
            context_factors from ``self``'s :class:`Procedure`
        """
        return self.rule.procedure.context_factors

    @property
    def generic_factors(self) -> List[Optional[Factor]]:
        r"""
        Get :class:`.Factor`\s that can be replaced without changing ``self``\s meaning.

        :returns:
            generic :class:`.Factor`\s from ``self``'s :class:`Procedure`
        """
        return self.rule.generic_factors

    def __add__(self, other: Factor) -> Holding:
        if isinstance(other, Enactment):
            return self.evolve({"rule": self.rule + other})
        raise NotImplementedError

    def contradicts(self, other) -> bool:
        r"""
        Test if ``self`` :meth:`~.Factor.implies` ``other`` :meth:`~.Factor.negated`\.

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

        :returns:
            whether ``self`` contradicts ``other``.
        """

        if not isinstance(other, self.__class__):
            raise TypeError(
                f"'Contradicts' not supported between instances of "
                + f"'{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )

        if not other.decided:
            return False
        if self.decided:
            return self >= other.negated()
        return other._implies_if_decided(self) or other._implies_if_decided(
            self.negated()
        )

    def __ge__(self, other: Union[Holding, Rule]) -> bool:
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

        if isinstance(other, Rule):
            return self >= Holding(rule=other)

        if not isinstance(other, self.__class__):
            raise TypeError(
                f"'Implies' not supported between instances of "
                + f"'{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )

        if self.decided and other.decided:
            return self._implies_if_decided(other)

        # A holding being undecided doesn't seem to imply that
        # any other holding is undecided, except itself and the
        # negation of itself.

        if not self.decided and not other.decided:
            return self.means(other) or self.means(other.negated())

        # It doesn't seem that any holding being undecided implies
        # that any holding is decided, or vice versa.

        return False

    def _implies_if_decided(self, other) -> bool:
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
            return self.rule >= other.rule

        if not self.rule_valid and not other.rule_valid:
            return other.rule >= self.rule

        # Looking for implication where self.rule_valid != other.rule_valid
        # is equivalent to looking for contradiction.

        # If decided rule A contradicts B, then B also contradicts A

        return self.rule.contradicts(other.rule)

    def __len__(self):
        r"""
        Count generic :class:`.Factor`\s needed as context for this :class:`Holding`.

        :returns:
            the number of generic :class:`.Factor`\s needed for
            self's :class:`.Procedure`.
        """

        return len(self.rule.procedure)

    def means(self, other):
        """
        Test whether ``other`` has the same meaning as ``self``.

        :returns:
            whether ``other`` is a :class:`Holding` with the
            same meaning as ``self``.
        """
        if not isinstance(other, self.__class__):
            return False

        if not self.rule.means(other.rule):
            return False

        return self.rule_valid == other.rule_valid and self.decided == other.decided

    def negated(self):
        """Get new copy of ``self`` with an opposite value for ``rule_valid``."""
        return self.evolve("rule_valid")

    @new_context_helper
    def new_context(self, changes: Dict[Factor, Factor]) -> Factor:
        """
        Create new :class:`Holding`, replacing keys of ``changes`` with values.

        :returns:
            a version of ``self`` with the new context.
        """
        return Holding(
            rule=self.rule.new_context(changes),
            rule_valid=self.rule_valid,
            decided=self.decided,
            selectors=self.selectors,
        )

    def __or__(self, other: Union[Rule, Holding]) -> Optional[Holding]:
        if isinstance(other, Rule):
            return self | Holding(rule=other)
        if not isinstance(other, Holding):
            raise TypeError

        if self.decided == other.decided == False:
            if self.rule >= other.rule:
                return self
            if other.rule >= self.rule:
                return other
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
            raise NotImplementedError

        new_rule = self.rule | other.rule
        if not new_rule:
            return None
        raise NotImplementedError(
            "Need a method to merge two lists of Opinion text selectors."
        )
        return Holding(
            rule=new_rule, decided=True, rule_valid=True, selectors=new_selector_group
        )

    def own_attributes(self) -> Dict[str, Any]:
        """
        Return attributes of ``self`` that aren't inherited from another class.

        Used for getting parameters to pass to :meth:`~Holding.__init__`
        when generating a new object.
        """
        attrs = self.__dict__.copy()
        for group in Procedure.context_factor_names:
            attrs.pop(group, None)
        for group in Rule.enactment_attr_names:
            attrs.pop(group, None)
        attrs.pop("procedure", None)
        return attrs

    def __str__(self):
        return (
            f"the holding {'' if self.decided else 'that it is undecided whether '}"
            + f"to {'accept' if self.rule_valid else 'reject'} {str(self.rule)}"
        )
