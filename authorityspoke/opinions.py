r"""
:class:`Court` documents that decide litigation and posit :class:`.Rule`\s.
"""

from __future__ import annotations

from itertools import zip_longest
from typing import Any, Dict, Iterable, Iterator, List, NamedTuple
from typing import Optional, Sequence, Tuple, Union

import logging
import re

from dataclasses import dataclass, field

from anchorpoint.textselectors import TextQuoteSelector, TextPositionSelector
from justopinion.decisions import Opinion
from nettlesome.terms import Comparable, ContextRegister, Explanation
from nettlesome.factors import Factor
from pydantic import BaseModel, Field, validator

from authorityspoke.holdings import Holding, HoldingGroup
from authorityspoke.procedures import Procedure
from authorityspoke.rules import Rule


logger = logging.getLogger(__name__)


TextLinkDict = Dict[str, List[TextQuoteSelector]]


class AnchoredHoldings(NamedTuple):
    """Holdings with objects storing the Holdings' links to Opinion text."""

    holdings: List[Holding]
    holding_anchors: List[List[TextQuoteSelector]]
    named_anchors: TextLinkDict
    enactment_anchors: TextLinkDict


class OpinionReading(Comparable):
    """
    An interpretation of what Holdings are supported by the text of an Opinion.
    """

    def __init__(
        self,
        opinion_type: str = "",
        opinion_author: str = "",
        holdings: Sequence = HoldingGroup(),
        factor_anchors: TextLinkDict = {},
        enactment_anchors: TextLinkDict = {},
        holding_anchors: Optional[List[List[TextQuoteSelector]]] = None,
    ) -> None:

        super().__init__()
        self.opinion_author = opinion_author
        self.opinion_type = opinion_type
        if not isinstance(holdings, HoldingGroup):
            holdings = HoldingGroup(holdings)
        self.holdings = holdings
        self.factor_anchors = factor_anchors
        self.enactment_anchors = enactment_anchors
        self.holding_anchors = holding_anchors or []

    def __str__(self):
        return super().__str__()

    def factors(self) -> List[Factor]:
        factors_by_name = self.factors_by_name()
        return list(factors_by_name.values())

    def factors_by_name(self) -> FactorIndex:
        factor_index = FactorIndex()
        for holding in self.holdings:
            factors_for_holding = holding.recursive_terms
            for value in factors_for_holding.values():
                if not isinstance(value, Holding):
                    factor_index.insert_by_name(value=value)
        return factor_index

    def clear_holdings(self):
        r"""Remove all :class:`.Holding`\s from the opinion."""
        self.holdings = HoldingGroup()

    def explanations_contradiction(
        self,
        other: Comparable,
    ) -> Iterator[Explanation]:
        """Yield contexts that would result in a contradiction between self and other."""
        if not self.comparable_with(other):
            raise TypeError(
                f"'Implies' test not implemented for types {self.__class__} and {other.__class__}."
            )
        if isinstance(other, Rule):
            other = Holding(rule=other)
        if isinstance(other, Holding):
            yield from self.holdings.explanations_contradiction(other)

        if isinstance(other, HoldingGroup):
            yield from self.holdings.explanations_contradiction(other)

        elif isinstance(other, self.__class__):
            yield from self.holdings.explanations_contradiction(other.holdings)

        elif hasattr(other, "explanations_contradiction"):
            yield from other.explanations_contradiction(self)

    def comparable_with(self, other: Any) -> bool:
        """Check if other can be compared to self for implication or contradiction."""
        if not isinstance(other, Comparable):
            return False
        if isinstance(other, Procedure):
            return False
        return not isinstance(other, Factor)

    def contradicts(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> bool:
        if not self.comparable_with(other):
            raise TypeError(
                "'Contradicts' test not implemented for types "
                + f"{self.__class__} and {other.__class__}."
            )
        return any(
            explanation is not None
            for explanation in self.explanations_contradiction(other)
        )

    def implies(
        self, other: Optional[Comparable], context: Optional[ContextRegister] = None
    ) -> bool:
        if other is None:
            return True
        if isinstance(other, HoldingGroup):
            return self.implies_other_holdings(other)
        return any(self.explanations_implication(other))

    def explain_implication(
        self,
        other: Comparable,
    ) -> Optional[Explanation]:
        explanations = self.explanations_implication(other)
        try:
            explanation = next(explanations)
        except StopIteration:
            return None
        return explanation

    def explain_contradiction(self, other: Comparable) -> Optional[Explanation]:
        explanations = self.explanations_contradiction(other)
        try:
            explanation = next(explanations)
        except StopIteration:
            return None
        return explanation

    def explanations_implication(
        self,
        other: Comparable,
    ) -> Iterator[Union[ContextRegister, Explanation]]:
        """Yield contexts that would result in self implying other."""
        if not self.comparable_with(other):
            raise TypeError(
                f"'Implies' test not implemented for types {self.__class__} and {other.__class__}."
            )
        if isinstance(other, Rule):
            other = Holding(rule=other)
        if isinstance(other, Holding):
            for self_holding in self.holdings:
                yield from self_holding.explanations_implication(other)
        if isinstance(other, HoldingGroup):
            yield from self.holdings.explanations_implication(other)
        elif isinstance(other, self.__class__):
            yield from self.holdings.explanations_implication(other.holdings)
        else:
            yield from other.explanations_implied_by(self)

    def generic_terms_by_str(self) -> Dict[str, Comparable]:
        r"""
        Get all generic :class:`.Factor`\s mentioned in ``self``.

        :returns:
            a list of generic :class:`.Factor` objects mentioned in
            any ``input``, ``output``, or ``despite`` :class:`.Factor`
            of ``self``, with guaranteed order, including each
            generic :class:`.Factor` only once.
        """
        generics: Dict[str, Comparable] = {}
        for holding in self.holdings:
            for generic in holding.generic_terms():
                generics[str(generic)] = generic
        return generics

    def get_factor_by_name(self, name: str) -> Optional[Comparable]:
        """
        Search recursively in holdings of ``self`` for :class:`.Factor` with ``name``.

        :param name:
            string to match with the ``name`` attribute of the
            :class:`.Factor` being searched for.

        :returns:
            a :class:`.Factor` with the specified ``name``, if one
            exists in a :class:`.Rule` in ``self.holdings``.
            Otherwise ``None``.
        """

        for holding in self.holdings:
            factor = holding.get_factor_by_name(name)
            if factor is not None:
                return factor
        return None

    def get_factor_by_str(self, query: str) -> Optional[Factor]:
        r"""
        Search recursively  for :class:`.Factor` in holdings of self.
        """
        return self.holdings.get_factor_by_str(query)

    def get_matching_holding(self, holding: Holding) -> Optional[Holding]:
        for known_holding in self.holdings:
            if holding.means(known_holding):
                return known_holding
        return None

    def posit_holding(
        self,
        holding: Union[Holding, Rule],
        holding_anchors: Optional[
            Union[TextQuoteSelector, List[TextQuoteSelector]]
        ] = None,
        named_anchors: Optional[TextLinkDict] = None,
        enactment_anchors: Optional[TextLinkDict] = None,
        context: Optional[Sequence[Factor]] = None,
    ) -> None:
        r"""Record that this Opinion endorses specified :class:`Holding`\s."""
        if isinstance(holding, Rule):
            logger.warning(
                "posit_holding was called with a Rule "
                "that was automatically converted to a Holding"
            )
            holding = Holding(rule=holding)

        if not isinstance(holding, Holding):
            raise TypeError('"holding" must be an object of type Holding.')

        if holding_anchors and not isinstance(holding_anchors, List):
            holding_anchors = [holding_anchors]

        if holding_anchors:
            holding.anchors = holding.anchors + holding_anchors

        if named_anchors:
            self.factor_anchors = {**self.factor_anchors, **named_anchors}

        if enactment_anchors:
            self.enactment_anchors = {**self.enactment_anchors, **enactment_anchors}

        matching_holding = self.get_matching_holding(holding)
        if matching_holding:
            matching_holding.anchors += holding.anchors
        else:
            if context:
                holding = holding.new_context(context, source=self)
            self.holdings = self.holdings + HoldingGroup(holding)

    def posit_holdings(
        self,
        holdings: Union[AnchoredHoldings, Iterable[Union[Holding, Rule]]],
        holding_anchors: Optional[List[List[TextQuoteSelector]]] = None,
        named_anchors: Optional[TextLinkDict] = None,
        enactment_anchors: Optional[TextLinkDict] = None,
        context: Optional[Sequence[Factor]] = None,
    ):
        r"""
        Add :class:`.Holding`\s to this ``OpinionReading`` from a sequence.

        :param holdings:
            a sequence of :class:`.Holding`\s that this :class:`.OpinionReading`
            posits as valid in its own court or jurisdiction, regardless of
            whether ``self`` accepts that the ``inputs`` correspond to the
            reality of the current case, and regardless of whether the
            court orders that the ``outputs`` be put into effect.

        :param context:
            an ordered sequence (probably :py:class:`dict`) of
            generic :class:`.Factor` objects from ``self`` which
            will provide the context for the new holding in the
            present case.
        """
        if isinstance(holdings, AnchoredHoldings):
            (holdings, holding_anchors, named_anchors, enactment_anchors) = holdings

        holding_anchors = holding_anchors or []
        for (holding, selector_list) in zip_longest(holdings, holding_anchors):
            self.posit_holding(
                holding,
                holding_anchors=selector_list,
                named_anchors=named_anchors,
                enactment_anchors=enactment_anchors,
                context=context,
            )

    def posit(
        self,
        holdings: Union[AnchoredHoldings, Holding, Iterable[Union[Holding, Rule]]],
        holding_anchors: Optional[
            List[Union[TextQuoteSelector, List[TextQuoteSelector]]]
        ] = None,
        named_anchors: Optional[TextLinkDict] = None,
        enactment_anchors: Optional[TextLinkDict] = None,
        context: Optional[Sequence[Factor]] = None,
    ) -> None:
        r"""
        Add one or more :class:`.Holding`\s to this ``OpinionReading``.

        This method passes its values to :meth:`~posit_holding` or
        :meth:`~posit_holdings` depending on whether the `holding` parameter
        is one :class:`.Holding` or a :class:`list`\.

        :param holdings:
            a :class:`.Holding` that the :class:`.OpinionReading` ``self`` posits
            as valid in its own court or jurisdiction, regardless of
            whether ``self`` accepts that the ``inputs`` of the
            :class:`.Holding` correspond to the reality of the current
            case, and regardless of whether the court orders that
            the ``outputs`` of the :class:`.Holding` be put into effect.

        :param context:
            an ordered sequence (probably :py:class:`dict`) of
            generic :class:`.Factor` objects from ``self`` which
            will provide the context for the new holding in the
            present case.
        """
        if isinstance(holdings, Iterable):
            self.posit_holdings(
                holdings,
                holding_anchors=holding_anchors,
                named_anchors=named_anchors,
                enactment_anchors=enactment_anchors,
                context=context,
            )
        else:
            self.posit_holding(
                holdings,
                holding_anchors=holding_anchors,
                named_anchors=named_anchors,
                enactment_anchors=enactment_anchors,
                context=context,
            )

    def _implied_by_holding(self, other: Holding, context: Explanation) -> bool:
        return all(
            other.implies(self_holding, context=context.reversed_context())
            for self_holding in self.holdings
        )

    def _implied_by_rule(self, other: Rule, context: Explanation) -> bool:
        return self._implied_by_holding(other=Holding(other), context=context)

    def implied_by(
        self,
        other: Union[OpinionReading, Holding, Rule],
        context: Optional[Union[ContextRegister, Explanation]] = None,
    ) -> bool:
        """Determine if other implies all the Holdings of self."""
        if not isinstance(context, Explanation):
            context = Explanation.from_context(context)
        if isinstance(other, Holding):
            return self._implied_by_holding(other, context=context)
        elif isinstance(other, Rule):
            return self._implied_by_rule(other, context=context)
        return other.implies(self, context=context.reversed_context())

    def implies_other_holdings(self, other_holdings: Sequence[Holding]):
        for other_holding in other_holdings:
            if not any(
                self_holding.implies(other_holding) for self_holding in self.holdings
            ):
                return False
        return True

    def __ge__(self, other: Union[OpinionReading, Holding, Rule]) -> bool:
        """
        Find whether ``self``'s holdings imply all the holdings of ``other``.

        :returns:
            a bool indicating whether the :class:`.Holding` ``other``
            (or every holding of ``other``, if other is an :class:`.OpinionReading`)
            is implied by some :class:`.Holding` in ``self.holdings``.
        """
        return self.implies(other)

    def __gt__(self, other) -> bool:
        """
        Find whether ``self``\'s holdings imply ``other``\'s but self != other.

        This actually tests for inequality because ``OpinionReading`` does not
        have a ``means`` method.

        :returns:
            self >= other and self != other.
        """
        return (self >= other) and (self != other)


class FactorIndex(Dict[str, Factor]):
    r"""Index of :class:`.Factor`/s that may share common anchors."""

    def insert_by_name(self, value: Factor) -> None:
        """
        Insert Factor using its name as key if possible.

        If the Factor has no name attr, use its str as key instead.
        """
        if value.name:
            self.insert(key=value.name, value=value)
            return None
        key = str(value)
        self.insert(key=key, value=value)

    def insert(self, key: str, value: Factor) -> None:
        """Insert Factor using its str as its key."""
        if key in self.keys():
            if value.name:
                if not self[key].name:
                    self[key].name = value.name
                if value.name != self[key].name:
                    raise NameError(
                        f"{type(value)} objects with identical representation ({str(value)}) "
                        f"have differing names: '{value.name}' and '{self[key].name}'"
                    )
        else:
            self[key] = value
