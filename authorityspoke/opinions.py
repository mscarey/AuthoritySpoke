r"""
:class:`Court` documents that decide litigation and posit :class:`.Rule`\s.

Unlike most other ``authorityspoke`` classes, :class:`Opinion`\s are not frozen.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple
from typing import Optional, Sequence, Union

import datetime
import logging
import re

from dataclasses import dataclass, field

from authorityspoke.factors import Factor
from authorityspoke.holdings import Holding
from authorityspoke.rules import Rule
from authorityspoke.selectors import TextQuoteSelector

logger = logging.getLogger(__name__)


@dataclass
class Opinion:
    """
    A document that resolves legal issues in a case and posits legal holdings.

    Usually an opinion must have ``position="majority"``
    to create holdings binding on any courts.

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
    :param position:
        the opinion's attitude toward the court's disposition of the case.
        e.g. ``majority``, ``dissenting``, ``concurring``, ``concurring in the result``
    :param author:
        name of the judge who authored the opinion, if identified
    """

    name: str
    name_abbreviation: str
    citations: Iterable[str]
    first_page: Optional[int]
    last_page: Optional[int]
    decision_date: datetime.date
    court: str
    position: Optional[str]
    author: Optional[str]
    text: Optional[str] = field(repr=False)

    def __post_init__(self):
        self.holdings: List[Holding] = []
        self.factors: Dict[
            Factor, Union[TextQuoteSelector, Tuple[TextQuoteSelector, ...]]
        ] = {}

    def contradicts(self, other: Union[Opinion, Holding]) -> bool:
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
                self_holding.contradicts(other) for self_holding in self.holdings
            )
        elif isinstance(other, self.__class__):
            return any(
                any(
                    self_holding.contradicts(other_holding)
                    for self_holding in self.holdings
                )
                for other_holding in other.holdings
            )
        raise TypeError(
            f"'Contradicts' test not implemented for types {self.__class__} and {other.__class__}."
        )

    @property
    def generic_factors(self) -> List[Factor]:
        """
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

    def posit_holding(
        self,
        holding: Union[Holding, Rule],
        text_links: Optional[Dict[Factor, List[TextQuoteSelector]]] = None,
        context: Optional[Sequence[Factor]] = None,
    ) -> None:

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
        self.holdings.append(holding)

        if text_links:
            for factor in holding.recursive_factors:
                for selector in text_links.get(factor, []):
                    if factor not in self.factors:
                        self.factors[factor] = []  # repeated elsewhere?
                    if not any(
                        selector == known_selector
                        for known_selector in self.factors[factor]
                    ):
                        self.factors[factor].append(selector)

    def posit_holdings(
        self,
        holdings: Iterable[Union[Holding, Rule]],
        text_links: Optional[Dict[Factor, List[TextQuoteSelector]]] = None,
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
        for holding in holdings:
            self.posit_holding(holding, text_links=text_links, context=context)

    def posit(
        self,
        holdings: Union[Holding, Iterable[Union[Holding, Rule]]],
        text_links: Optional[Dict[Factor, List[TextQuoteSelector]]] = None,
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
            mapping of :class:`Factor`\s to the :class:`Opinion` passages where
            they can be found. Can be obtained as the "mentioned" return value
            of one of the functions in :mod:`authorityspoke.io.readers`\.

        :param context:
            an ordered sequence (probably :py:class:`dict`) of
            generic :class:`.Factor` objects from ``self`` which
            will provide the context for the new holding in the
            present case.
        """
        if isinstance(holdings, Iterable):
            self.posit_holdings(holdings, text_links=text_links, context=context)
        else:
            self.posit_holding(holdings, text_links=text_links, context=context)

    def get_anchors(self, holding: Holding, include_factors: bool = True) -> List[str]:
        r"""
        Get text passages where a :class:`.Holding` is linked to ``self``.

        :param holding:
            a holding to find anchors for, which must be in :attr:`~Opinion.holdings`\.

        :returns:
            a :class:`list` with the text of each passage that anchors the :class:`.Holding`
        """

        def add_selectors(
            anchor_list: List, selectors: Optional[Iterable[TextQuoteSelector]]
        ) -> List[str]:
            if selectors is None:
                return anchor_list
            for selector in selectors:
                new_text = self.select_text(selector)
                if new_text:
                    anchor_list.append(new_text)
                else:
                    logger.error(
                        f"Failed to find Opinion text with {selector} in "
                        + (f"Opinion {self.name}.")
                    )
            return anchor_list

        anchors: List[str] = []
        if include_factors:
            for factor in holding.rule.procedure.factors_all:
                anchors = add_selectors(anchors, self.factors.get(factor))
        # What about the Rule? Can that have its own selectors?
        anchors = add_selectors(anchors, holding.selectors)

        return anchors

    def __ge__(self, other: Union[Opinion, Rule]) -> bool:
        """
        Find whether ``self``'s holdings imply all the holdings of ``other``.

        :returns:
            a bool indicating whether the :class:`.Rule` ``other``
            (or every holding of ``other``, if other is an :class:`.Opinion`)
            is implied by some :class:`.Rule` in ``self.holdings``.
        """
        if isinstance(other, (Rule, Holding)):
            return any(self_holding >= other for self_holding in self.holdings)
        elif isinstance(other, self.__class__):
            for other_holding in other.holdings:
                if not any(
                    self_holding >= other_holding for self_holding in self.holdings
                ):
                    return False
            return True
        raise TypeError(
            f"'Implies' test not implemented for types {self.__class__} and {other.__class__}."
        )

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
        if isinstance(self.citations, str):
            citation = self.citations
        else:
            citation = self.citations[0]
        name = self.name_abbreviation or self.name
        if self.position == "majority":
            position = ""
        else:
            position = self.position + " "
        return f"<{position}Opinion> {name}, {citation} ({self.decision_date})"
