r"""
:class:`Court` documents that decide litigation and posit :class:`.Rule`\s.

Unlike most other ``authorityspoke`` classes, :class:`Opinion`\s are not frozen.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import zip_longest
from typing import Dict, Iterable, List
from typing import Optional, Sequence, Set, Tuple, Union

import datetime
import logging
import re

from dataclasses import dataclass, field

from authorityspoke.factors import Factor, ContextRegister
from authorityspoke.enactments import Enactment
from authorityspoke.holdings import Holding
from authorityspoke.rules import Rule
from authorityspoke.selectors import TextQuoteSelector

logger = logging.getLogger(__name__)


TextLinkDict = Dict[str, List[TextQuoteSelector]]


@dataclass
class CaseCitation:
    cite: str
    reporter: str


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

    def contradicts(
        self, other: Union[Opinion, Holding], context: Optional[ContextRegister] = None
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

        if isinstance(other, Holding):
            return any(
                self_holding.contradicts(other, context)
                for self_holding in self.holdings
            )
        elif isinstance(other, self.__class__):
            return any(
                any(
                    self_holding.contradicts(other_holding, context)
                    for self_holding in self.holdings
                )
                for other_holding in other.holdings
            )
        raise TypeError(
            f"'Contradicts' test not implemented for types {self.__class__} and {other.__class__}."
        )

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
        holding_anchors: Optional[List[TextQuoteSelector]] = None,
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

        if context:
            holding = holding.new_context(context, context_opinion=self)
        self.holding_anchors[holding].extend(holding_anchors or [])
        if named_anchors:
            for factor in holding.recursive_factors:
                if hasattr(factor, "name") and factor.name in named_anchors:
                    self.factors[factor].extend(named_anchors[factor.name])

    def posit_holdings(
        self,
        holdings: Iterable[Union[Holding, Rule]],
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
        holdings: Union[Holding, Iterable[Union[Holding, Rule]]],
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

        :param holding:
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
        if re.search(selector.passage_regex, self.text, re.IGNORECASE):
            return selector.exact
        raise ValueError(
            f'Passage "{selector.exact}" from TextQuoteSelector '
            + f'not found in Opinion "{self}".'
        )

    def __str__(self):
        return f"{self.position} Opinion by {self.author}"


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
