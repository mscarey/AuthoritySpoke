r"""
:class:`Court` documents that decide litigation and posit :class:`.Rule`\s.

Unlike most other ``authorityspoke`` classes, :class:`Opinion`\s are not frozen.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import compress, zip_longest
from typing import Dict, Iterable, Iterator, List, NamedTuple
from typing import Optional, Sequence, Union

import logging
import re

from dataclasses import dataclass, field

from anchorpoint.textselectors import TextQuoteSelector

from authorityspoke.comparisons import Comparable
from authorityspoke.explanations import Explanation
from authorityspoke.factors import Factor, ContextRegister, FactorIndex
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


@dataclass
class Opinion(Comparable):
    """
    A document that resolves legal issues in a case and posits legal holdings.

    Usually an opinion must have ``position="majority"``
    to create holdings binding on any courts.

    :param position:
        the opinion's attitude toward the court's disposition of the case.
        e.g. ``majority``, ``dissenting``, ``concurring``, ``concurring in the result``
    :param author:
        name of the judge who authored the opinion, if identified
    :param text:
    """

    position: Optional[str] = None
    author: Optional[str] = None
    text: Optional[str] = field(default=None, repr=False)

    def __post_init__(self):
        r"""
        Add attributes to store Holdings and Factors keyed to their text selectors.

        The ``holding_anchors`` are text selectors for the whole :class:`Holding`, not for any
        individual :class:`.Factor`. Often select text used to
        indicate whether the :class:`.Rule` is ``mandatory``, ``universal``,
        ``valid``, or ``decided``, or show the ``exclusive`` way to reach
        the outputs.
        """

        self._holdings = HoldingGroup()

    def factors(self) -> List[Factor]:
        factors_by_name = self.factors_by_name()
        return list(factors_by_name.values())

    def factors_by_name(self) -> FactorIndex:
        factor_index = FactorIndex()
        for holding in self.holdings:
            factors_for_holding = holding.recursive_factors
            for value in factors_for_holding.values():
                if not isinstance(value, Holding):
                    factor_index.insert_by_name(value=value)
        return factor_index

    def factors_by_str(self) -> FactorIndex:
        factor_index = FactorIndex()
        for holding in self.holdings:
            for key, value in holding.recursive_factors.items():
                if not isinstance(value, Holding):
                    factor_index.insert(key=key, value=value)
        return factor_index

    @property
    def holdings(self):
        return HoldingGroup(self._holdings)

    def clear_holdings(self):
        r"""Remove all :class:`.Holding`\s from the opinion."""
        self._holdings = HoldingGroup()

    def explanations_contradiction(
        self,
        other: Comparable,
        context: Optional[ContextRegister] = None,
    ) -> Iterator[Explanation]:
        """Yield contexts that would result in a contradiction between self and other."""
        if isinstance(other, Rule):
            other = Holding(rule=other)
        if isinstance(other, Holding):
            for self_holding in self.holdings:
                for explanation in self_holding.explanations_contradiction(
                    other, context
                ):
                    yield explanation
        elif isinstance(other, self.__class__):
            for self_holding in self.holdings:
                for other_holding in other.holdings:
                    for explanation in self_holding.explanations_contradiction(
                        other_holding, context
                    ):
                        yield explanation
        elif hasattr(other, "explanations_contradiction"):
            yield from other.explanations_contradiction(self)

    def contradicts(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> bool:
        if isinstance(other, (Factor, Procedure)):
            return False
        elif isinstance(other, Comparable):
            return any(
                explanation is not None
                for explanation in self.explanations_contradiction(other)
            )
        raise TypeError(
            "'Contradicts' test not implemented for types "
            + f"{self.__class__} and {other.__class__}."
        )

    def implies(
        self, other: Optional[Comparable], context: Optional[ContextRegister] = None
    ) -> bool:
        if other is None:
            return True
        if isinstance(other, HoldingGroup):
            return self.implies_other_holdings(other)
        return any(self.explanations_implication(other))

    def explanations_implication(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Iterator[Union[ContextRegister, Explanation]]:
        """Yield contexts that would result in self implying other."""
        if isinstance(other, Rule):
            other = Holding(rule=other)
        if isinstance(other, Holding):
            for self_holding in self.holdings:
                for explanation in self_holding.explanations_implication(
                    other, context
                ):
                    yield explanation

        elif isinstance(other, self.__class__):
            yield from self.holdings.explanations_implication(
                other.holdings, context=context
            )
        elif hasattr(other, "explanations_implication"):
            if context:
                context = context.reversed()
            yield from other.explanations_implication(self, context=context)
        else:
            raise TypeError(
                f"'Implies' test not implemented for types {self.__class__} and {other.__class__}."
            )

    def generic_factors_by_str(self) -> Dict[str, Comparable]:
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
            for generic in holding.generic_factors():
                generics[str(generic)] = generic
        return generics

    def get_factor_by_name(self, name: str) -> Optional[Factor]:
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

        matching_holding = self.get_matching_holding(holding)
        if matching_holding:
            matching_holding.anchors += holding.anchors
        else:
            if context:
                holding = holding.new_context(context, source=self)
            self._holdings = self._holdings + HoldingGroup(holding)

    def posit_holdings(
        self,
        holdings: Union[AnchoredHoldings, Iterable[Union[Holding, Rule]]],
        holding_anchors: Optional[List[List[TextQuoteSelector]]] = None,
        named_anchors: Optional[TextLinkDict] = None,
        context: Optional[Sequence[Factor]] = None,
    ):
        r"""
        Add :class:`.Holding`\s to this ``Opinion`` from a sequence.

        :param holdings:
            a sequence of :class:`.Holding`\s that this :class:`.Opinion`
            posits as valid in its own court or jurisdiction, regardless of
            whether ``self`` accepts that the ``inputs`` correspond to the
            reality of the current case, and regardless of whether the
            court orders that the ``outputs`` be put into effect.

        :param text_links:
            mapping of :class:`Factor`\s to the :class:`Opinion` passages where
            they can be found. Can be obtained as the `mentioned` return value
            of one of the functions in :mod:`authorityspoke.io.readers`\.

        :param context:
            an ordered sequence (probably :py:class:`dict`) of
            generic :class:`.Factor` objects from ``self`` which
            will provide the context for the new holding in the
            present case.
        """
        if isinstance(holdings, AnchoredHoldings):
            (holdings, holding_anchors, named_anchors) = holdings

        holding_anchors = holding_anchors or []
        for (holding, selector_list) in zip_longest(holdings, holding_anchors):
            self.posit_holding(
                holding,
                holding_anchors=selector_list,
                named_anchors=named_anchors,
                context=context,
            )

    def posit(
        self,
        holdings: Union[AnchoredHoldings, Holding, Iterable[Union[Holding, Rule]]],
        holding_anchors: Optional[
            List[Union[TextQuoteSelector, List[TextQuoteSelector]]]
        ] = None,
        named_anchors: Optional[TextLinkDict] = None,
        context: Optional[Sequence[Factor]] = None,
    ) -> None:
        r"""
        Add one or more :class:`.Holding`\s to this ``Opinion``.

        This method passes its values to :meth:`~posit_holding` or
        :meth:`~posit_holdings` depending on whether the `holding` parameter
        is one :class:`.Holding` or a :class:`list`\.

        :param holdings:
            a :class:`.Holding` that the :class:`.Opinion` ``self`` posits
            as valid in its own court or jurisdiction, regardless of
            whether ``self`` accepts that the ``inputs`` of the
            :class:`.Holding` correspond to the reality of the current
            case, and regardless of whether the court orders that
            the ``outputs`` of the :class:`.Holding` be put into effect.

        :param text_links:
            list of lists of :class:`.Opinion` passages where references to each
            :class:`.Holding` can be found.

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
                context=context,
            )
        else:
            self.posit_holding(
                holdings,
                holding_anchors=holding_anchors,
                named_anchors=named_anchors,
                context=context,
            )

    def implied_by_holding(
        self, other: Holding, context: ContextRegister = None
    ) -> bool:
        context = context or ContextRegister()
        return all(
            other.implies(self_holding, context=context.reversed())
            for self_holding in self.holdings
        )

    def implied_by_rule(self, other: Rule, context: ContextRegister = None) -> bool:
        return self.implied_by_holding(other=Holding(other), context=context)

    def implied_by(
        self, other: Union[Opinion, Holding, Rule], context: ContextRegister = None
    ) -> bool:
        if isinstance(other, Holding):
            return self.implied_by_holding(other, context=context)
        elif isinstance(other, Rule):
            return self.implied_by_rule(other, context=context)
        return other.implies(self, context=context.reversed())

    def implies_other_holdings(self, other_holdings: Sequence[Holding]):
        for other_holding in other_holdings:
            if not any(
                self_holding.implies(other_holding) for self_holding in self.holdings
            ):
                return False
        return True

    def __ge__(self, other: Union[Opinion, Rule]) -> bool:
        """
        Find whether ``self``'s holdings imply all the holdings of ``other``.

        :returns:
            a bool indicating whether the :class:`.Rule` ``other``
            (or every holding of ``other``, if other is an :class:`.Opinion`)
            is implied by some :class:`.Rule` in ``self.holdings``.
        """
        return self.implies(other)

    def __gt__(self, other) -> bool:
        """
        Find whether ``self``\'s holdings imply ``other``\'s but self != other.

        This actually tests for inequality because ``Opinion`` does not
        have a ``means`` method.

        :returns:
            self >= other and self != other.
        """
        return (self >= other) and (self != other)

    def select_text(self, selector: TextQuoteSelector) -> Optional[str]:
        r"""
        Get text using a :class:`.TextQuoteSelector`.

        :param selector:
            a selector referencing a text passage in this :class:`Opinion`.

        :returns:
            the text referenced by the selector, or ``None`` if the text
            can't be found.
        """
        if re.search(selector.passage_regex(), self.text, re.IGNORECASE):
            return selector.exact
        raise ValueError(
            f'Passage "{selector.exact}" from TextQuoteSelector '
            + f'not found in Opinion "{self}".'
        )

    def __str__(self):
        return f"{self.position} Opinion by {self.author}"
