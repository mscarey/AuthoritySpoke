from __future__ import annotations

from dataclasses import dataclass, field
import datetime
from typing import Iterable, List, Optional, Sequence, Union

from authorityspoke.factors import Factor, ContextRegister
from authorityspoke.holdings import Holding
from authorityspoke.opinions import Opinion, TextLinkDict
from authorityspoke.rules import Rule
from authorityspoke.selectors import TextQuoteSelector


@dataclass
class CaseCitation:
    cite: str
    reporter: str


@dataclass
class Decision:
    """
    A court decision to resolve a step in litigation.

    Uses the model of a judicial decision from
    the `Caselaw Access Project API <https://api.case.law/v1/cases/>`_.
    One of these records may contain multiple :class:`.Opinion`\s.

    Typically one record will contain all the :class:`.Opinion`\s
    from one appeal, but not necessarily from the whole lawsuit. One
    lawsuit may contain multiple appeals or other petitions, and
    if more then one of those generates published :class:`.Opinion`\s,
    the CAP API will divide those :class:`.Opinion`\s into a separate
    record for each appeal.

    The outcome of a decision may be determined by one majority
    :class:`Opinion` or by the combined effect of multiple Opinions.
    The lead opinion is commonly, but not always, the only
    :class:`.Opinion` that creates binding legal authority.
    Usually every :class:`.Rule` posited by the lead :class:`.Opinion` is
    binding, but some may not be, often because parts of the
    :class:`.Opinion` fail to command a majority of the panel
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

    name: str
    date: datetime.date
    name_abbreviation: Optional[str] = None
    citations: Optional[Sequence[CaseCitation]] = None
    first_page: Optional[int] = None
    last_page: Optional[int] = None
    court: Optional[str] = None
    opinions: Sequence[Opinion] = field(default_factory=list)
    jurisdiction: Optional[str] = None
    _id: Optional[int] = None

    def __str__(self):
        citation = self.citations[0].cite if self.citations else ""
        name = self.name_abbreviation or self.name
        return f"{name}, {citation} ({self.date})"

    @property
    def holdings(self):
        if self.majority is None:
            raise NotImplementedError(
                "Cannot determine Holdings of Decision with no known majority Opinion."
            )
        return self.majority.holdings

    def contradicts(self, other):
        if isinstance(other, Decision):
            if self.majority and other.majority:
                return self.majority.contradicts(other.majority)
            return False
        return self.majority.contradicts(other)

    def posit(
        self,
        holdings: Union[Holding, Iterable[Union[Holding, Rule]]],
        holding_anchors: Optional[
            List[Union[TextQuoteSelector, List[TextQuoteSelector]]]
        ] = None,
        named_anchors: Optional[TextLinkDict] = None,
        context: Optional[Sequence[Factor]] = None,
    ) -> None:
        if self.majority is None:
            raise AttributeError(
                "Cannot posit Holding because this Decision has no known majority Opinion."
                " Try having an Opinion posit the Holding directly."
            )
        self.majority.posit(
            holdings=holdings,
            holding_anchors=holding_anchors,
            named_anchors=named_anchors,
            context=context,
        )

    def __ge__(self, other) -> bool:
        return self.implies(other)

    def __gt__(self, other) -> bool:
        return self.implies(other) and not self == other

    def implied_by_holding(
        self, other: Holding, context: ContextRegister = None
    ) -> bool:
        if context:
            context = context.reversed()
        return all(
            other.implies(self_holding, context=context.reversed())
            for self_holding in self.holdings
        )

    def implied_by_rule(self, other: Rule, context: ContextRegister = None) -> bool:
        return self.implied_by_holding(other=Holding(other), context=context)

    def implied_by(
        self, other: Union[Opinion, Holding, Rule], context: ContextRegister = None
    ) -> bool:
        if isinstance(other, Opinion):
            if context:
                context = context.reversed()
            return other.implies_other_holdings(self.holdings, context=context)
        if isinstance(other, Holding):
            return self.implied_by_holding(other, context=context)
        elif isinstance(other, Rule):
            return self.implied_by_rule(other, context=context)
        if context is not None:
            context = context.reversed()
        return other.implies(self, context=context)

    def implies_decision_or_opinion(
        self, other: Union[Decision, Opinion], context: Optional[ContextRegister] = None
    ) -> bool:
        for other_holding in other.holdings:
            if not any(
                self_holding.implies(other_holding, context=context)
                for self_holding in self.holdings
            ):
                return False
        return True

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
            return self.implies_decision_or_opinion(other, context=context)
        elif isinstance(other, Holding):
            return self.implies_holding(other, context=context)
        elif isinstance(other, Rule):
            return self.implies_rule(other, context=context)
        return False

    @property
    def majority(self) -> Optional[Opinion]:
        for opinion in self.opinions:
            if opinion.position == "majority":
                return opinion
        return None