from __future__ import annotations

import datetime
import operator
from typing import Iterable, Iterator, List
from typing import Optional, Sequence, Union

from anchorpoint.textselectors import TextQuoteSelector
from justopinion.decisions import CAPDecision as Decision

from justopinion.decisions import (
    CAPCitation,
    Court,
    Jurisdiction,
    DecisionAnalysis,
)
from nettlesome.terms import Comparable, ContextRegister, Explanation
from nettlesome.factors import Factor
from pydantic import BaseModel, HttpUrl, validator

from authorityspoke.holdings import Holding, HoldingGroup
from authorityspoke.opinions import Opinion, OpinionReading, TextLinkDict
from authorityspoke.rules import Rule


class CaseData(BaseModel):
    """
    The content of a Decision, including Opinions.
    """

    head_matter: Optional[str] = None
    corrections: Optional[str] = None
    parties: List[str] = []
    attorneys: List[str] = []
    opinions: List[Opinion] = []
    judges: List[str] = []

    @validator("opinions", each_item=True)
    def check_opinion_type(cls, v):
        """Convert Opinion from CAPOpinion if needed."""
        if not isinstance(v, Opinion):
            values = v.dict()
            return Opinion(**values)
        return v


class CaseBody(BaseModel):
    data: CaseData
    status: str = ""


class DecisionReading(Comparable):
    """
    An interpretation of what Holdings are supported by the Opinions of a Decision.
    """

    def __init__(
        self, decision: Decision, opinion_readings: List[OpinionReading] = None
    ):
        self.decision = decision
        self.opinion_readings = opinion_readings or []

    def __str__(self):
        citation = self.decision.citations[0].cite if self.decision.citations else ""
        name = self.decision.name_abbreviation or self.decision.name
        return f"Reading for {name}, {citation} ({self.decision.decision_date})"

    @property
    def majority(self) -> Optional[Opinion]:
        for reading in self.opinion_readings:
            if reading.opinion.type == "majority":
                return reading
        return None

    def get_majority(self) -> Optional[Opinion]:
        """
        Return the majority OpinionReading, creating it if needed.
        """
        majority = self.majority
        if majority:
            return majority
        for opinion in self.decision.opinions:
            if opinion.type == "majority":
                self.opinion_readings.append(OpinionReading(opinion=opinion))
                return opinion
        return None

    @property
    def holdings(self) -> HoldingGroup:
        if self.decision.majority is None:
            return HoldingGroup()
        return HoldingGroup(self.majority.holdings)

    def add_opinion(self, opinion: Opinion) -> None:
        if not self.decision.casebody:
            self.decision.casebody = CaseBody(data=CaseData())
        self.decision.casebody.data.opinions.append(opinion)

    def contradicts(self, other):
        if isinstance(other, DecisionReading):
            if self.majority and other.majority:
                return self.majority.contradicts(other.majority)
            return False
        return self.majority.contradicts(other)

    def explain_contradiction(
        self, other: Union[Opinion, Holding, Rule]
    ) -> Optional[Explanation]:
        explanations = self.explanations_contradiction(other)
        try:
            explanation = next(explanations)
        except StopIteration:
            return None
        return explanation

    def explanations_contradiction(
        self,
        other: Union[Decision, Opinion, Holding, Rule],
    ) -> Iterator[Explanation]:
        if isinstance(other, Decision):
            if self.majority and other.majority:
                yield from self.majority.explanations_contradiction(other.majority)
        elif isinstance(other, (Rule, Holding, Opinion)):
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
        explanations = self.explanations_implication(other)
        try:
            explanation = next(explanations)
        except StopIteration:
            return None
        return explanation

    def explanations_implication(
        self, other: Union[Decision, Opinion, Holding, Rule]
    ) -> Iterator[Explanation]:
        if isinstance(other, Decision):
            if self.majority and other.majority:
                yield from self.majority.explanations_implication(other.majority)
        elif isinstance(other, (Rule, Holding, Opinion)):
            if self.majority:
                yield from self.majority.explanations_implication(other)
        else:
            raise TypeError(
                f"'Implication' test not implemented for types "
                f"{self.__class__} and {other.__class__}."
            )

    def posit(
        self,
        holdings: Union[Holding, Iterable[Union[Holding, Rule]]],
        holding_anchors: Optional[
            List[Union[TextQuoteSelector, List[TextQuoteSelector]]]
        ] = None,
        named_anchors: Optional[TextLinkDict] = None,
        enactment_anchors: Optional[TextLinkDict] = None,
        context: Optional[Sequence[Factor]] = None,
    ) -> None:
        """
        Add one or more Holdings to the majority Opinion of this Decision.
        """
        if self.get_majority() is None:
            raise AttributeError(
                "Cannot posit Holding because this Decision has no known majority Opinion."
                " Try having an Opinion posit the Holding directly."
            )
        self.majority.posit(
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
        context = context or ContextRegister()
        if isinstance(other, Opinion):
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
        if other is None:
            return False
        return any(self.explanations_implied_by(other, context))

    def implies_holding(
        self, other: Holding, context: Optional[ContextRegister] = None
    ) -> bool:
        return any(
            self_holding.implies(other, context=context)
            for self_holding in self.holdings
        )

    def implies_rule(
        self, other: Rule, context: Optional[ContextRegister] = None
    ) -> bool:
        return self.implies_holding(Holding(other), context=context)

    def implies(self, other, context: Optional[ContextRegister] = None) -> bool:
        if isinstance(other, (DecisionReading, OpinionReading)):
            return self.holdings.implies(other.holdings)
        elif isinstance(other, Holding):
            return self.implies_holding(other, context=context)
        elif isinstance(other, Rule):
            return self.implies_rule(other, context=context)
        return False
