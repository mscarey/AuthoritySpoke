r"""
:class:`Court` documents that decide litigation and posit :class:`.Rule`\s.

Unlike most other ``authorityspoke`` classes, :class:`Opinion`\s are not frozen.
"""

from __future__ import annotations

from collections import defaultdict, OrderedDict
from itertools import zip_longest
import operator
from typing import Dict, Iterable, Iterator, List, NamedTuple
from typing import Optional, Sequence, Set, Tuple, Union

import logging
import re

from dataclasses import dataclass, field

from anchorpoint.textselectors import TextQuoteSelector

from authorityspoke.factors import Factor, ContextRegister, Analogy
from authorityspoke.explanations import Explanation
from authorityspoke.holdings import Holding
from authorityspoke.rules import Rule


logger = logging.getLogger(__name__)


TextLinkDict = Dict[str, List[TextQuoteSelector]]


class AnchoredHoldings(NamedTuple):
    holdings: List[Holding]
    holding_anchors: List[List[TextQuoteSelector]]
    named_anchors: TextLinkDict


@dataclass
class Opinion:
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

        self.holding_anchors: Dict[Holding, List[TextQuoteSelector]] = defaultdict(list)
        self.factors: Dict[Factor, List[TextQuoteSelector]] = defaultdict(list)

    def clear_holdings(self):
        r"""
        Remove all :class:`.Holding`\s from the opinion.
        """
        self.holding_anchors.clear()

    def explain_contradiction(
        self,
        other: Union[Opinion, Holding, Rule],
        context: Optional[ContextRegister] = None,
    ) -> Optional[Explanation]:
        explanations = self.explanations_contradiction(other, context=context)
        try:
            explanation = next(explanations)
        except StopIteration:
            return None
        return explanation

    def explanations_contradiction(
        self,
        other: Union[Opinion, Holding, Rule],
        context: Optional[ContextRegister] = None,
    ) -> Iterator[Explanation]:
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
            if context:
                context = context.reversed()
            yield from other.explanations_contradiction(self, context=context)
        else:
            raise TypeError(
                f"'Contradicts' test not implemented for types "
                + f"{self.__class__} and {other.__class__}."
            )

    def explain_implication(
        self,
        other: Union[Opinion, Holding, Rule],
        context: Optional[ContextRegister] = None,
    ) -> Optional[Explanation]:
        explanations = self.explanations_implication(other, context=context)
        try:
            explanation = next(explanations)
        except StopIteration:
            return None
        return explanation

    def explanations_implication(
        self,
        other: Union[Opinion, Holding, Rule],
        context: Optional[ContextRegister] = None,
    ) -> Iterator[Explanation]:
        if isinstance(other, Rule):
            other = Holding(rule=other)
        if isinstance(other, Holding):
            for self_holding in self.holdings:
                for explanation in self_holding.explanations_implication(
                    other, context
                ):
                    yield explanation
        elif isinstance(other, self.__class__):
            analogy = Analogy(
                need_matches=other.holdings,
                available=self.holdings,
                comparison=operator.le,
            )
            yield from analogy.unordered_comparison(matches=context)
        elif hasattr(other, "explanations_implication"):
            if context:
                context = context.reversed()
            yield from other.explanations_implication(self, context=context)
        else:
            raise TypeError(
                f"'Implies' test not implemented for types {self.__class__} and {other.__class__}."
            )

    def contradicts(
        self,
        other: Union[Opinion, Holding, Rule],
        context: Optional[ContextRegister] = None,
    ) -> bool:
        """
        Test whether ``other`` is or contains a :class:`.Holding` contradicted by ``self``.

        :param other:
            another :class:`.Opinion` or :class:`.Holding`

        :returns:
            a bool indicating whether any holding of ``self`` is
            inconsistent with the :class:`.Rule` ``other``, or with
            any holding of ``other`` if ``other`` is an :class:`.Opinion`.
        """

        return any(self.explanations_contradiction(other, context=context))

    @property
    def generic_factors(self) -> List[Factor]:
        r"""
        Get all generic :class:`.Factor`\s mentioned in ``self``.

        :returns:
            a list of generic :class:`.Factor` objects mentioned in
            any ``input``, ``output``, or ``despite`` :class:`.Factor`
            of ``self``, with guaranteed order, including each
            generic :class:`.Factor` only once.
        """
        return list(
            {
                generic: None
                for holding in self.holdings
                for generic in holding.generic_factors
            }
        )

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

    @property
    def holdings(self) -> List[Holding]:
        r"""
        Get ordered list of :class:`.Holding`\s posited by this :class:`Opinion`

        :returns:
            keys of the holding_anchors :class:`.OrderedDict`, as a list
        """
        return list(self.holding_anchors)

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
        if holding_anchors and not isinstance(holding_anchors, List):
            holding_anchors = [holding_anchors]
        if isinstance(holding, Rule):
            logger.warning(
                "posit_holding was called with a Rule "
                "that was automatically converted to a Holding"
            )
            holding = Holding(rule=holding)

        if not isinstance(holding, Holding):
            raise TypeError('"holding" must be an object of type Holding.')

        if context:
            holding = holding.new_context(context, context_opinion=self)
        self.holding_anchors[holding].extend(holding_anchors or [])
        if named_anchors:
            for factor in (
                list(holding.recursive_factors)
                + list(holding.enactments)
                + list(holding.enactments_despite)
            ):
                if hasattr(factor, "name") and factor.name in named_anchors:
                    for anchor in named_anchors[factor.name]:
                        if anchor not in self.factors[factor]:
                            self.factors[factor].append(anchor)

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

    def get_anchors(self, holding: Holding, include_factors: bool = True) -> List[str]:
        r"""
        Get text passages where a :class:`.Holding` is linked to ``self``.

        :param holding:
            a holding to find anchors for, which must be in :attr:`~Opinion.holdings`\.

        :returns:
            a :class:`list` with the text of each passage that anchors the :class:`.Holding`
        """

        anchors: List[str] = []
        if include_factors:
            for factor in holding.rule.procedure.factors_all:
                if self.factors.get(factor):
                    anchors.extend(self.factors[factor])
        anchors.extend(self.holding_anchors[holding])

        return anchors

    def implied_by_holding(
        self, other: Holding, context: ContextRegister = None
    ) -> bool:
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

    def implies_other_holdings(
        self, other_holdings: List[Holding], context: ContextRegister = None
    ):
        for other_holding in other_holdings:
            if not any(
                self_holding.implies(other_holding, context=context)
                for self_holding in self.holdings
            ):
                return False
        return True

    def implies(
        self, other: Union[Opinion, Holding, Rule], context: ContextRegister = None
    ) -> bool:
        if isinstance(other, (Rule, Holding)):
            return any(
                self_holding.implies(other, context=context)
                for self_holding in self.holdings
            )
        elif isinstance(other, self.__class__):
            return self.implies_other_holdings(other.holdings)
        if hasattr(other, "implied_by"):
            if context:
                context = context.reversed()
            return other.implied_by(self, context=context)
        return False

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
