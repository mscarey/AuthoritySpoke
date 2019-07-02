from __future__ import annotations

import json
import operator
import pathlib

from typing import ClassVar, Dict, Iterable, List, Sequence, Tuple
from typing import Iterator, Optional, Union

from dataclasses import dataclass

from authorityspoke.context import get_directory_path
from authorityspoke.factors import Factor
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

    rule: Rule
    rule_valid: bool = True
    decided: bool = True
    selector: Optional[Union[Iterable[TextQuoteSelector], TextQuoteSelector]] = None
    name: Optional[str] = None

    directory: ClassVar = get_directory_path("holdings")

    def __post_init__(self):
        object.__setattr__(self, "outputs", self.rule.procedure.outputs)
        object.__setattr__(self, "inputs", self.rule.procedure.inputs)
        object.__setattr__(self, "despite", self.rule.procedure.despite)
        if isinstance(self.selector, list):
            object.__setattr__(self, "selector", tuple(self.selector))
        elif isinstance(self.selector, TextQuoteSelector):
            object.__setattr__(self, "selector", tuple([self.selector]))

    @classmethod
    def from_dict(
        cls, record: Dict, mentioned: List[Factor], regime: Optional[Regime] = None
    ) -> Iterator[Tuple[Holding, List[Factor], Dict[Factor, List[TextQuoteSelector]]]]:
        """
        Will yield multiple items if ``exclusive: True`` is present in ``record``.
        """

        # If lists were omitted around single elements in the JSON,
        # add them back

        for category in ("inputs", "despite", "outputs"):
            if isinstance(record.get(category), dict):
                record[category] = [record[category]]

        factor_text_links: Dict[Factor, List[TextQuoteSelector]] = {}
        factor_groups: Dict[str, List] = {"inputs": [], "outputs": [], "despite": []}

        for factor_type in factor_groups:
            for factor_dict in record.get(factor_type) or []:
                created, mentioned = Factor.from_dict(
                    factor_dict, mentioned, regime=regime
                )
                if isinstance(factor_dict, dict):
                    selector_group = factor_dict.pop("text", None)
                    if selector_group:
                        if not isinstance(selector_group, list):
                            selector_group = list(selector_group)
                        selector_group = [
                            TextQuoteSelector.from_record(selector)
                            for selector in selector_group
                        ]
                        factor_text_links[created] = selector_group
                factor_groups[factor_type].append(created)

        exclusive = record.pop("exclusive", None)
        rule_valid = record.pop("rule_valid", True)
        decided = record.pop("decided", True)
        selector = TextQuoteSelector.from_record(record.pop("text", None))

        basic_rule, mentioned = Rule.from_dict(
            record=record,
            mentioned=mentioned,
            regime=regime,
            factor_groups=factor_groups,
        )
        yield (
            Holding(
                rule=basic_rule,
                rule_valid=rule_valid,
                decided=decided,
                selector=selector,
            ),
            mentioned,
            factor_text_links,
        )

        if exclusive:
            if not rule_valid:
                raise NotImplementedError(
                    "The ability to state that it is not 'valid' to assert "
                    + "that a Rule is the 'exclusive' way to reach an output is "
                    + "not implemented, so 'rule_valid' cannot be False while "
                    + "'exclusive' is True. Try expressing this in another way "
                    + "without the 'exclusive' keyword."
                )
            if not decided:
                raise NotImplementedError(
                    "The ability to state that it is not 'decided' whether "
                    + "a Rule is the 'exclusive' way to reach an output is "
                    + "not implemented. Try expressing this in another way "
                    + "without the 'exclusive' keyword."
                )
            for modified_rule in basic_rule.get_contrapositives():
                yield (Holding(rule=modified_rule, selector=selector), mentioned, {})

        # Continue by handing off to Rule.from_dict, which will have to be changed
        # to handle the Factors already having been created.

    @property
    def context_factors(self) -> Tuple:
        """
        Call :class:`Procedure`\'s :meth:`~Procedure.context_factors` method.

        :returns:
            context_factors from ``self``'s :class:`Procedure`
        """
        return self.rule.procedure.context_factors

    @property
    def generic_factors(self) -> List[Optional[Factor]]:
        """
        Get :class:`.Factor`\s that can be replaced without changing ``self``\s meaning.

        :returns:
            generic :class:`.Factor`\s from ``self``'s :class:`Procedure`
        """
        return self.rule.generic_factors

    def contradicts(self, other) -> bool:
        """
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
        """
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
        """
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

    def new_context(self, changes: Dict[Factor, Factor]) -> Factor:
        return Holding(
            rule=self.rule.new_context(changes),
            rule_valid=self.rule_valid,
            decided=self.decided,
            selector=self.selector,
        )

    def __str__(self):
        return (
            f"the holding {'' if self.decided else 'that it is undecided whether '}"
            + f"to {'accept' if self.rule_valid else 'reject'} {str(self.rule)}"
        )
