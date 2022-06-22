r""":class:`Court` documents that decide litigation and posit :class:`.Rule`\s."""

from __future__ import annotations

from itertools import zip_longest
from typing import Any, Dict, Iterator, List
from typing import Optional, Sequence, Union

import logging

from anchorpoint.textselectors import (
    TextQuoteSelector,
    TextPositionSet,
    TextPositionSelector,
)
from justopinion import Opinion
from legislice.enactments import EnactmentPassage
from nettlesome.terms import Comparable, ContextRegister, Explanation, Term
from nettlesome.factors import Factor
from pydantic import BaseModel, validator

from authorityspoke.facts import Entity, Fact, Allegation, Pleading, Exhibit, Evidence
from authorityspoke.holdings import Holding, HoldingGroup
from authorityspoke.procedures import Procedure
from authorityspoke.rules import Rule


logger = logging.getLogger(__name__)


class EnactmentWithAnchors(BaseModel):
    """A term with a set of anchors."""

    passage: EnactmentPassage
    anchors: TextPositionSet = TextPositionSet()

    @validator("anchors", pre=True)
    def validate_anchors(cls, value: TextPositionSet) -> TextPositionSet:
        """Validate that the anchors are non-empty."""

        if value is None:
            return TextPositionSet()
        return value


class TermWithAnchors(BaseModel):
    """A term with a set of anchors."""

    term: Union[Entity, Fact, Allegation, Pleading, Exhibit, Evidence]
    anchors: TextPositionSet = TextPositionSet()

    @validator("anchors", pre=True)
    def validate_anchors(cls, value: TextPositionSet) -> TextPositionSet:
        """Validate that the anchors are non-empty."""

        if value is None:
            return TextPositionSet()
        return value


class HoldingWithAnchors(BaseModel):
    """A :class:`.Holding` with a :class:`.TextPositionSet` that anchors it."""

    holding: Holding
    anchors: TextPositionSet = TextPositionSet()

    @validator("anchors", pre=True)
    def validate_anchors(cls, value: TextPositionSet) -> TextPositionSet:
        """Validate that the anchors are non-empty."""
        if value is None:
            return TextPositionSet()
        return value


class AnchoredHoldings(BaseModel):
    """Holdings with objects storing the Holdings' links to Opinion text."""

    holdings: List[HoldingWithAnchors] = []
    named_anchors: List[TermWithAnchors] = []
    enactment_anchors: List[EnactmentWithAnchors] = []

    def find_term_index(self, term: Term) -> Optional[int]:
        """Find the index of a term in the holdings."""
        key = term.key
        for index, term_with_anchors in enumerate(self.named_anchors):
            if term_with_anchors.term.key == key:
                return index
        return None

    def add_term(self, term: Term, anchors: TextPositionSet) -> None:
        """Add a term that can be found in self's holdings, with the term's anchors to the text."""
        term_index = self.find_term_index(term)
        if term_index is None:
            self.named_anchors.append(TermWithAnchors(term=term, anchors=anchors))
        else:
            self.named_anchors[term_index].anchors += anchors

    def get_term_anchors(self, key: str) -> TextPositionSet:
        """Get the anchors for a term."""
        for item in self.named_anchors:
            if item.term.key == key:
                return item.anchors
        raise KeyError(f"Term with key '{key}' not found")

    def find_enactment_index(self, enactment: EnactmentPassage) -> Optional[int]:
        """Find the index of a term in the holdings."""
        key = str(enactment)
        for index, enactment_with_anchors in enumerate(self.enactment_anchors):
            if str(enactment_with_anchors.passage) == key:
                return index
        return None

    def add_enactment(
        self, enactment: EnactmentPassage, anchors: TextPositionSet
    ) -> None:
        """Add EnactmentPassage with text anchors, if it isn't a duplicate."""
        term_index = self.find_enactment_index(enactment)
        if term_index is None:
            self.enactment_anchors.append(
                EnactmentWithAnchors(passage=enactment, anchors=anchors)
            )
        else:
            self.enactment_anchors[term_index].anchors += anchors

    def get_enactment_anchors(self, key: str) -> TextPositionSet:
        """Get the anchors for a term."""
        for item in self.enactment_anchors:
            if str(item.passage) == key:
                return item.anchors
        raise KeyError(f"Enactment passage with key '{key}' not found")


class OpinionReading(Comparable, BaseModel):
    """An interpretation of what Holdings are supported by the text of an Opinion."""

    anchored_holdings: AnchoredHoldings = AnchoredHoldings()
    opinion_type: str = ""
    opinion_author: str = ""

    @property
    def holdings(self) -> HoldingGroup:
        """Get Holdings for the Opinion."""
        return HoldingGroup([item.holding for item in self.anchored_holdings.holdings])

    @property
    def holding_anchors(self) -> List[TextPositionSet]:
        """Get Holdings with corresponding anchors for the Opinion."""
        return [item.anchors for item in self.anchored_holdings.holdings]

    @property
    def anchored_factors(self) -> List[TermWithAnchors]:
        """Get Factors with corresponding anchors for the Opinion."""
        return self.anchored_holdings.named_anchors

    @property
    def anchored_enactments(self) -> List[EnactmentWithAnchors]:
        """Get Enactment passages with corresponding anchors for the Opinion."""
        return self.anchored_holdings.enactment_anchors

    def __str__(self):
        return super().__str__()

    def factors(self) -> List[Factor]:
        """Get all factors from the Holdings of the Opinion, without duplication."""
        factors_by_name = self.factors_by_name()
        return list(factors_by_name.values())

    def factors_by_name(self) -> FactorIndex:
        """Get an index of Factors, indexed by name."""
        factor_index = FactorIndex()
        for holding in self.holdings:
            factors_for_holding = holding.recursive_terms
            for value in factors_for_holding.values():
                if not isinstance(value, Holding):
                    factor_index.insert_by_name(value=value)
        return factor_index

    def clear_holdings(self):
        r"""Remove all :class:`.Holding`\s from the opinion."""
        self.anchored_holdings.holdings = []

    def get_enactment_anchors(self, key: str) -> TextPositionSet:
        """Get the anchors for an enactment passage."""
        return self.anchored_holdings.get_enactment_anchors(key)

    def get_term_anchors(self, key: str) -> TextPositionSet:
        """Get the anchors for an enactment passage."""
        return self.anchored_holdings.get_term_anchors(key)

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
        """Check if other contradicts one of self's Holdings."""
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
        """Check if all of other's Holdings are implied by holdings of self."""
        if other is None:
            return True
        return any(self.explanations_implication(other))

    def explain_implication(
        self,
        other: Comparable,
    ) -> Optional[Explanation]:
        """Get first Explanation of how one of self's Holdings implies other."""
        explanations = self.explanations_implication(other)
        try:
            explanation = next(explanations)
        except StopIteration:
            return None
        return explanation

    def explain_contradiction(self, other: Comparable) -> Optional[Explanation]:
        """Get first Explanation of how other contradicts one of self's Holdings."""
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
        r"""Search recursively for :class:`.Factor` in holdings of self."""
        return self.holdings.get_factor_by_str(query)

    def get_matching_holding(self, holding: Holding) -> Optional[Holding]:
        """Check self's Holdings for a Holding with the same meaning."""
        for known_holding in self.holdings:
            if holding.means(known_holding):
                return known_holding
        return None

    def posit_holding(
        self,
        holding: Union[Holding, Rule, HoldingWithAnchors],
        holding_anchors: Optional[
            Union[TextPositionSelector, TextQuoteSelector, TextPositionSet]
        ] = None,
        named_anchors: Optional[List[TermWithAnchors]] = None,
        enactment_anchors: Optional[List[EnactmentWithAnchors]] = None,
        context: Optional[Sequence[Factor]] = None,
    ) -> None:
        r"""Record that this Opinion endorses specified :class:`Holding`\s."""
        named_anchors = named_anchors or []
        enactment_anchors = enactment_anchors or []

        if isinstance(holding, HoldingWithAnchors):
            holding, holding_anchors = holding.holding, holding.anchors
        if isinstance(holding_anchors, (TextQuoteSelector, str)):
            holding_anchors = [holding_anchors]
        if isinstance(holding_anchors, List) and isinstance(
            holding_anchors[0], (str, TextQuoteSelector)
        ):
            holding_anchors = TextPositionSet.from_quotes(holding_anchors)
        if isinstance(holding, Rule):
            logger.warning(
                "posit_holding was called with a Rule "
                "that was automatically converted to a Holding"
            )
            holding = Holding(rule=holding)

        if not isinstance(holding, Holding):
            raise TypeError('"holding" must be an object of type Holding.')

        for named_anchor in named_anchors:
            self.anchored_holdings.add_term(
                term=named_anchor.term, anchors=named_anchor.anchors
            )

        for enactment_anchor in enactment_anchors:
            self.anchored_holdings.add_enactment(
                enactment=enactment_anchor.passage, anchors=named_anchor.anchors
            )

        matching_holding = self.get_matching_holding(holding)
        if matching_holding:
            matching_holding.anchors += holding.anchors
        else:
            if context:
                holding = holding.new_context(context, source=self)
            self.anchored_holdings.holdings.append(
                HoldingWithAnchors(holding=holding, anchors=holding_anchors)
            )

    def posit_holdings(
        self,
        holdings: Union[
            AnchoredHoldings, List[Union[HoldingWithAnchors, Holding, Rule]]
        ],
        holding_anchors: Optional[List[HoldingWithAnchors]] = None,
        named_anchors: Optional[List[TermWithAnchors]] = None,
        enactment_anchors: Optional[List[EnactmentWithAnchors]] = None,
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
            for holding_with_anchor in holdings.holdings:
                self.posit_holding(
                    holding=holding_with_anchor,
                    named_anchors=named_anchors,
                    enactment_anchors=enactment_anchors,
                    context=context,
                )
        else:
            holding_anchors = holding_anchors or []
            for (holding, selector_list) in zip_longest(holdings, holding_anchors):
                self.posit_holding(
                    holding=holding,
                    holding_anchors=selector_list,
                    named_anchors=named_anchors,
                    enactment_anchors=enactment_anchors,
                    context=context,
                )

    def posit(
        self,
        holdings: Union[
            AnchoredHoldings,
            Holding,
            Rule,
            HoldingWithAnchors,
            List[Union[HoldingWithAnchors, Holding, Rule]],
        ],
        holding_anchors: Optional[List[HoldingWithAnchors]] = None,
        named_anchors: Optional[List[TermWithAnchors]] = None,
        enactment_anchors: Optional[List[EnactmentWithAnchors]] = None,
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
        if isinstance(holdings, (Holding, Rule, HoldingWithAnchors)):
            self.posit_holding(
                holdings,
                holding_anchors=holding_anchors,
                named_anchors=named_anchors,
                enactment_anchors=enactment_anchors,
                context=context,
            )
        else:
            self.posit_holdings(
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
        return self._implied_by_holding(other=Holding(rule=other), context=context)

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
