"""Classes representing legislation."""

from __future__ import annotations

from typing import List, Optional, Union
from dataclasses import dataclass

from anchorpoint.textselectors import TextQuoteSelector, TextPositionSelector

from authorityspoke.codes import Code
from authorityspoke.formatting import wrapped


@dataclass(frozen=True)
class Enactment:
    """
    A passage of legislative text.

    May be used as support for a
    :class:`.Rule`. To retrieve the text, there needs
    to be an available method for identifying the correct XML
    element based on the section and subsection names, and each
    XML format used for any :class:`Code` will require a different method.

    :param selector:
        identifier for the section of a :class:`Code` where
        the text can be found.

    :param selector:
        identifier for the part of the section being cited

    :param code:
        the :class:`Code` where this legislative text appears.

    :param name:
        an identifier for this object, often used if the object needs
        to be referred to multiple times in the process of composing
        other :class:`.Factor` objects.
    """

    source: Optional[str]
    selector: Optional[Union[TextQuoteSelector, TextPositionSelector]] = None
    code: Optional[Code] = None
    name: Optional[str] = None

    def __post_init__(self):
        if not self.source:
            if not self.code:
                raise AttributeError("A Source or Code parameter is required.")
            object.__setattr__(self, "source", self.code.uri)

        if isinstance(self.selector, TextPositionSelector):
            if not self.code:
                raise AttributeError(
                    "Because text alignment may vary between Code versions, "
                    + "a Code parameter is required when the selector is a "
                    + "TextPositionSelector."
                )
            object.__setattr__(self, "_interval", self.selector)
            object.__setattr__(
                self,
                "selector",
                self._interval.as_quote_selector(
                    self.code.section_text_from_path(self.source)
                ),
            )

        if self.selector and self.code:
            text = self.code.section_text_from_path(self.source)
            if not self.selector.exact:
                object.__setattr__(
                    self, "selector", self.selector.rebuild_from_text(text=text)
                )
            interval = self.selector.as_position(text)
            if interval is None:
                raise ValueError(f"Selected text not found in source {self.source}")
            object.__setattr__(self, "_interval", interval)
        else:
            object.__setattr__(self, "_interval", None)

    def __add__(self, other):
        if other.__class__.__name__ == "Rule":
            return other + self
        if not isinstance(other, self.__class__):
            raise TypeError

        if self >= other and self.source.startswith(other.source):
            return self
        if other >= self and other.source.startswith(self.source):
            return other
        combined = self.combine_text(other) or other.combine_text(self)
        return combined

    def _combine_text(self, other: Enactment) -> Optional[Enactment]:
        r"""
        Create new :class:`Enactment` with combined text of the source :class:`Enactment`\s.

        Private method because it only works if other's path includes
        self's path.
        """
        code = self.code or other.code
        if not code:
            raise AttributeError(
                "Code attribute is needed to combine text of Enactments "
                + "with different source URIs."
            )
        section_text = code.section_text_from_path(self.source)
        self_interval = self.selector.as_position(section_text)
        other_interval = other.selector.as_position(section_text)
        new_interval = self_interval + other_interval
        if not new_interval:
            return None
        new_selector = new_interval.as_quote_selector(section_text)
        return Enactment(source=self.source, selector=new_selector, code=self.code,)

    def combine_text(self, other: Enactment) -> Optional[Enactment]:
        r"""
        Create new :class:`Enactment` with combined text of the source :class:`Enactment`\s.

        :param other:
            another :class:`Enactment` with text to combine with the text from ``self``.

        :returns:
            new :class:`Enactment` with combined text of the source :class:`Enactment`\s, or
            ``None`` if the :class:`Enactment`\s can't be combined.
        """
        if other.source == self.source:
            new_interval = self.interval + other.interval
            if new_interval is None:
                return None
            return Enactment(source=self.source, selector=new_interval, code=self.code,)
        if other.source.startswith(self.source):
            return self._combine_text(other)
        elif self.source.startswith(other.source):
            return other._combine_text(self)
        return None

    @property
    def effective_date(self):
        r"""
        Give effective date for the :class:`Enactment`\.

        :returns:
            the effective date of the text in this passage.
            Currently works only for the US Constitution.
        """
        return self.code.provision_effective_date(self.source)

    @property
    def interval(self):
        """Return :class:`TextPositionSelector` for cited part of the Enactment section."""
        return self._interval or TextPositionSelector(0, len(self.text))

    @property
    def text(self):
        r"""
        Get passage from self's Code with self's TextQuoteSelector.

        :returns: the full text of the cited passage from the XML.
        """

        return self.code.select_text(path=self.source, selector=self.selector)

    def means(self, other: Enactment) -> bool:
        r"""
        Find whether meaning of ``self`` is equivalent to that of ``other``.

        ``Self`` must be neither broader nor narrower than ``other``, which
        means it must contain the same legislative text in the same :class:`.Code`
        from the same :class:`.Jurisdiction`

        .. note::
            You could always make the result ``False`` by comparing longer
            passages of text until you found a difference between the two
            sites in the text. Does this undercut the usefulness of the
            ``means`` method?

        :returns:
            whether ``self`` and ``other`` represent the same text
            issued by the same sovereign in the same level of
            :class:`Enactment`\.
        """
        if not isinstance(other, self.__class__):
            return False

        return (
            self.text.strip(",:;. ") == other.text.strip(",:;. ")
            and self.code.jurisdiction == other.code.jurisdiction
            and self.code.level == other.code.level
        )

    def __str__(self):
        return wrapped(f'"{self.text}" ({self.code.title}, {self.source})')

    def __ge__(self, other):
        """
        Tells whether ``self`` implies ``other``.

        .. note::
            Why does this method not require the same ``code.sovereign``
            and ``code.level``, especially considering that
            :meth:`means` does?

        :returns:
            Whether ``self`` "implies" ``other``, which in this context means
            whether ``self`` contains at least all the same text as ``other``.
        """
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"{self.__class__} objects may only be compared for "
                + "implication with other Enactment objects."
            )

        return other.text.strip(",:;. ") in self.text

    def __gt__(self, other) -> bool:
        """Test whether ``self`` implies ``other`` without having same meaning."""
        if self == other:
            return False
        return self >= other


def consolidate_enactments(enactments: List[Enactment]) -> List[Enactment]:
    r"""
    Consolidate any overlapping :class:`Enactment`\s in a :class:`list`.

    :param enactments:
        a list of :class:`Enactment`\s that may include overlapping
        legislative text within the same section

    :returns:
        a list of :class:`Enactment`\s without overlapping text
    """
    consolidated: List[Enactment] = []
    while enactments:
        match_made = False
        left = enactments.pop()
        for right in enactments:
            combined = left + right
            if combined is not None:
                enactments.remove(right)
                enactments.append(combined)
                match_made = True
                break
        if match_made is False:
            consolidated.append(left)
    return consolidated
