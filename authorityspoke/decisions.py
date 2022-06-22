r"""
Interpretations (or "readings") of judicial Decisions.

Each :class:`.justopinion.decisions.Decision` may include
multiple :class:`.justopinion.decisions.Opinion`\s. A
:class:`.authorityspoke.decision.DecisionReading` may link
to multiple :class:`.authorityspoke.opinion.OpinionReading`\s.
"""

from __future__ import annotations

import operator
from typing import Dict, Iterator, List
from typing import Optional, Sequence, Tuple, Union

from anchorpoint.textselectors import TextQuoteSelector, TextPositionSelector
from justopinion.decisions import Decision, CaseBody, CaseData, Opinion, CAPCitation

from nettlesome.terms import Comparable, ContextRegister, Explanation
from nettlesome.factors import Factor
from pydantic import BaseModel

from authorityspoke.holdings import Holding, HoldingGroup
from authorityspoke.opinions import (
    OpinionReading,
    TermWithAnchors,
    AnchoredHoldings,
    HoldingWithAnchors,
    EnactmentWithAnchors,
)
from authorityspoke.rules import Rule


RawCAPCitation = Dict[str, str]
RawOpinion = Dict[str, str]
RawDecision = Dict[str, Union[str, int, Sequence[RawOpinion], Sequence[RawCAPCitation]]]


class DecisionReading(BaseModel, Comparable):
    """An interpretation of what Holdings are supported by the Opinions of a Decision."""

    decision: Decision
    opinion_readings: List[OpinionReading] = []

    def __str__(self):
        citation = self.decision.citations[0].cite if self.decision.citations else ""
        name = self.decision.name_abbreviation or self.decision.name
        return f"Reading for {name}, {citation} ({self.decision.decision_date})"

    @property
    def majority(self) -> Optional[OpinionReading]:
        """Return the majority OpinionReading, or None if it doesn't exist."""
        for reading in self.opinion_readings:
            if reading.opinion_type == "majority":
                return reading
        return None

    @property
    def opinions(self) -> List[Opinion]:
        """Get the Opinions for this DecisionReading's Decision."""
        return self.decision.opinions

    def find_matching_opinion(
        self,
        opinion_type: str = "",
        opinion_author: str = "",
    ) -> Optional[Opinion]:
        """Find an Opinion described by the given attributes."""
        return self.decision.find_matching_opinion(
            opinion_type=opinion_type, opinion_author=opinion_author
        )

    def find_opinion_matching_reading(
        self,
        opinion_reading: OpinionReading,
    ) -> Optional[Opinion]:
        """Find the Opinion corresponding to an OpinionReading."""
        return self.find_matching_opinion(
            opinion_type=opinion_reading.opinion_type,
            opinion_author=opinion_reading.opinion_author,
        )

    def select_text(
        self,
        selector: Union[
            bool,
            str,
            TextPositionSelector,
            TextQuoteSelector,
            Sequence[
                Union[str, Tuple[int, int], TextQuoteSelector, TextPositionSelector]
            ],
        ],
        opinion_type: str = "",
        opinion_author: str = "",
    ) -> Optional[str]:
        r"""
        Get text using a :class:`.TextQuoteSelector`.

        :param selector:
            a selector referencing a text passage in the :class:`Opinion`.

        :returns:
            the text referenced by the selector, or ``None`` if the text
            can't be found.
        """
        opinion = self.find_matching_opinion(opinion_type, opinion_author)
        return opinion.select_text(selector) if opinion else None

    def add_opinion_reading(self, opinion_reading: OpinionReading) -> None:
        """Add an OpinionReading for an existing Opinion of the Decision."""
        matching_opinion = self.find_opinion_matching_reading(opinion_reading)
        if matching_opinion:
            opinion_reading.opinion_type = (
                matching_opinion.type or opinion_reading.opinion_type
            )
            opinion_reading.opinion_author = (
                matching_opinion.author or opinion_reading.opinion_author
            )
        self.opinion_readings.append(opinion_reading)

    def get_majority(self) -> Optional[OpinionReading]:
        """Return the majority OpinionReading, creating it if needed."""
        majority = self.majority
        if majority:
            return majority
        for opinion in self.decision.opinions:
            if opinion.type == "majority":
                new_reading = OpinionReading(
                    opinion_type=opinion.type, opinion_author=opinion.author
                )
                self.opinion_readings.append(new_reading)
                return new_reading
        return None

    @property
    def holdings(self) -> HoldingGroup:
        """Get the holdings of this Decision's majority Opinion."""
        if self.majority is not None:
            return HoldingGroup(self.majority.holdings)
        elif len(self.opinion_readings) == 1:
            return HoldingGroup(self.opinion_readings[0].holdings)
        return HoldingGroup()

    def add_opinion(self, opinion: Opinion) -> None:
        """Link an Opinion document to this Decision."""
        if not self.decision.casebody:
            self.decision.casebody = CaseBody(data=CaseData())
        self.decision.casebody.data.opinions.append(opinion)

    def contradicts(self, other):
        """Check if a holding attributed to this decision contradicts a holding attributed in "other"."""
        if isinstance(other, DecisionReading):
            if self.majority and other.majority:
                return self.majority.contradicts(other.majority)
            return False
        return self.majority.contradicts(other)

    def explain_contradiction(
        self, other: Union[OpinionReading, Holding, Rule]
    ) -> Optional[Explanation]:
        """Get the first generated explanation of how a Holding of self contradicts a Holding of other."""
        explanations = self.explanations_contradiction(other)
        try:
            explanation = next(explanations)
        except StopIteration:
            return None
        return explanation

    def explanations_contradiction(
        self,
        other: Union[DecisionReading, Opinion, Holding, Rule],
    ) -> Iterator[Explanation]:
        """Generate explanations of how a Holding of self contradicts a Holding of other."""
        if isinstance(other, DecisionReading):
            if self.majority and other.majority:
                yield from self.majority.explanations_contradiction(other.majority)
        elif isinstance(other, (Rule, Holding, OpinionReading)):
            if self.majority:
                yield from self.majority.explanations_contradiction(other)
        else:
            raise TypeError(
                f"'Contradicts' test not implemented for types "
                f"{self.__class__} and {other.__class__}."
            )

    def explain_implication(
        self,
        other: Union[Opinion, Holding, Rule],
    ) -> Optional[Explanation]:
        """Get the first generated explanation of how a Holding of self implies a Holding of other."""
        explanations = self.explanations_implication(other)
        try:
            explanation = next(explanations)
        except StopIteration:
            return None
        return explanation

    def explanations_implication(
        self, other: Union[DecisionReading, Decision, Opinion, Holding, Rule]
    ) -> Iterator[Explanation]:
        """Generate explanation of how self's Holdings can imply other."""
        if isinstance(other, DecisionReading):
            self_majority = self.get_majority()
            if self_majority and other.get_majority():
                yield from self_majority.explanations_implication(other.majority)
        elif isinstance(other, (Rule, Holding, OpinionReading)):
            self_majority = self.get_majority()
            if self_majority:
                yield from self_majority.explanations_implication(other)
        else:
            raise TypeError(
                f"'Implication' test not implemented for types "
                f"{self.__class__} and {other.__class__}."
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
        """Add one or more Holdings to the majority Opinion of this Decision."""
        majority = self.get_majority()
        if majority is not None:
            reading_to_use = majority
        elif len(self.opinion_readings) == 1:
            reading_to_use = self.opinion_readings[0]
        elif not self.opinion_readings:
            self.opinion_readings = [OpinionReading()]
            reading_to_use = self.opinion_readings[0]
        else:
            raise AttributeError(
                "Cannot determine how to posit the Holding because this DecisionReading "
                "has multiple OpinionReadings, none of which is linked to a majority "
                "Opinion. Try using the .posit() method of one of the OpinionReadings "
                "on this object's `opinion_readings` attribute."
            )
        reading_to_use.posit(
            holdings=holdings,
            holding_anchors=holding_anchors,
            named_anchors=named_anchors,
            enactment_anchors=enactment_anchors,
            context=context,
        )

    def __ge__(self, other) -> bool:
        return self.implies(other)

    def __gt__(self, other) -> bool:
        return self.implies(other) and self != other

    def implied_by_holding(
        self, other: Holding, context: Optional[ContextRegister] = None
    ) -> Iterator[Explanation]:
        """Check if a Holding implies all the Holdings of self."""
        if all(
            other.implies(self_holding, context=context)
            for self_holding in self.holdings
        ):
            yield Explanation(
                reasons=[(other, self_holding) for self_holding in self.holdings],
                operation=operator.ge,
            )

    def explanations_implied_by(
        self, other: Comparable, context: Optional[ContextRegister] = None
    ) -> Iterator[Explanation]:
        """Generate explanation of how other can imply all the Holdings of self."""
        context = context or ContextRegister()
        if isinstance(other, OpinionReading):
            other = other.holdings
        if isinstance(other, HoldingGroup):
            yield from other.explanations_implication(
                self.holdings, context=context.reversed()
            )
        if isinstance(other, Rule):
            other = Holding(rule=other)
        if isinstance(other, Holding):
            yield from self.implied_by_holding(other, context)

    def implied_by(
        self, other: Optional[Comparable], context: Optional[ContextRegister] = None
    ) -> bool:
        """Check if other implies all the Holdings of self."""
        if other is None:
            return False
        return any(self.explanations_implied_by(other, context))

    def implies_holding(
        self, other: Holding, context: Optional[ContextRegister] = None
    ) -> bool:
        """Check if a Holding of self implies a Holding made from other."""
        return any(
            self_holding.implies(other, context=context)
            for self_holding in self.holdings
        )

    def implies_rule(
        self, other: Rule, context: Optional[ContextRegister] = None
    ) -> bool:
        """Check if a Holding of self implies a Holding made from other Rule."""
        return self.implies_holding(Holding(rule=other), context=context)

    def implies(self, other, context: Optional[ContextRegister] = None) -> bool:
        """Check if the Holdings of self imply other."""
        if isinstance(other, (DecisionReading, OpinionReading)):
            return self.holdings.implies(other.holdings)
        elif isinstance(other, Holding):
            return self.implies_holding(other, context=context)
        elif isinstance(other, Rule):
            return self.implies_rule(other, context=context)
        return False
