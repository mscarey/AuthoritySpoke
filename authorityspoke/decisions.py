from __future__ import annotations

import datetime
import operator
from typing import Iterable, Iterator, List
from typing import Optional, Sequence, Union

from anchorpoint.textselectors import TextQuoteSelector
from justopinion.decisions import (
    CAPDecision,
    CAPCitation,
    Court,
    Jurisdiction,
    DecisionAnalysis,
)
from nettlesome.terms import Comparable, ContextRegister, Explanation
from nettlesome.factors import Factor
from pydantic import BaseModel, HttpUrl, validator

from authorityspoke.holdings import Holding, HoldingGroup
from authorityspoke.opinions import Opinion, TextLinkDict
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


class Decision(Comparable, CAPDecision):
    r"""
    A court decision to resolve a step in litigation.
    Uses the model of a judicial decision from
    the `Caselaw Access Project API <https://api.case.law/v1/cases/>`_.
    One of these records may contain multiple :class:`.Opinion`\s.
    Typically one record will contain all
    the :class:`~authorityspoke.opinions.Opinion`\s
    from one appeal, but not necessarily from the whole lawsuit. One
    lawsuit may contain multiple appeals or other petitions, and
    if more then one of those generates published Opinions,
    the CAP API will divide those Opinions into a separate
    record for each appeal.
    The outcome of a decision may be determined by one majority
    :class:`~authorityspoke.opinions.Opinion` or by the combined
    effect of multiple Opinions.
    The lead opinion is commonly, but not always, the only
    Opinion that creates binding legal authority.
    Usually every :class:`~authorityspoke.rules.Rule` posited by the lead Opinion is
    binding, but some may not be, often because parts of the
    Opinion fail to command a majority of the panel
    of judges.

    :param name:
        full name of the opinion, e.g. "ORACLE AMERICA, INC.,
        Plaintiff-Appellant, v. GOOGLE INC., Defendant-Cross-Appellant"
    :param name_abbreviation:
        shorter name of the opinion, e.g. "Oracle America, Inc. v. Google Inc."
    :param citations:
        citations to the opinion, usually in the format
        ``[Volume Number] [Reporter Name Abbreviation] [Page Number]``
    :param first_page:
        the page where the opinion begins in its official reporter
    :param last_page:
        the page where the opinion ends in its official reporter
    :param decision_date:
        date when the opinion was first published by the court
        (not the publication date of the reporter volume)
    :param court:
        name of the court that published the opinion
    :param _id:
        unique ID from CAP API
    """

    decision_date: datetime.date
    name: Optional[str] = None
    name_abbreviation: Optional[str] = None
    docket_num: Optional[str] = None
    citations: Optional[Sequence[CAPCitation]] = None
    first_page: Optional[int] = None
    last_page: Optional[int] = None
    court: Optional[Court] = None
    casebody: Optional[CaseBody] = None
    jurisdiction: Optional[Jurisdiction] = None
    cites_to: Optional[Sequence[CAPCitation]] = None
    id: Optional[int] = None
    last_updated: Optional[datetime.datetime] = None
    frontend_url: Optional[HttpUrl] = None
    analysis: Optional[DecisionAnalysis] = None

    class Config:
        json_encoders = {
            datetime.date: lambda v: v.isoformat(),
        }

    def __str__(self):
        citation = self.citations[0].cite if self.citations else ""
        name = self.name_abbreviation or self.name
        return f"{name}, {citation} ({self.decision_date})"

    @property
    def holdings(self) -> HoldingGroup:
        if self.majority is None:
            return HoldingGroup()
        return HoldingGroup(self.majority.holdings)

    @property
    def majority(self) -> Optional[Opinion]:
        for opinion in self.opinions:
            if opinion.type == "majority":
                return opinion
        return None

    def add_opinion(self, opinion: Opinion) -> None:
        if not self.casebody:
            self.casebody = CaseBody(data=CaseData())
        self.casebody.data.opinions.append(opinion)

    def contradicts(self, other):
        if isinstance(other, Decision):
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
        if self.majority is None:
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
        if isinstance(other, (Decision, Opinion)):
            return self.holdings.implies(other.holdings)
        elif isinstance(other, Holding):
            return self.implies_holding(other, context=context)
        elif isinstance(other, Rule):
            return self.implies_rule(other, context=context)
        return False
