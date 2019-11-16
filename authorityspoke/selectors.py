"""
Selectors for citing exact passages in strings.

Based on the `Web Annotation Data Model <https://www.w3.org/TR/annotation-model/>`_
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from typing import Optional, Tuple


@dataclass(frozen=True)
class TextQuoteSelector:
    """
    Describes a textual segment by quoting it, or passages before or after it.

    Based on the `Web Annotation Data Model
    <https://www.w3.org/TR/annotation-model/#text-quote-selector>`_

    :param exact:
        a copy of the text which is being selected

    :param prefix:
        a snippet of text that occurs immediately before the text which
        is being selected.

    :param suffix:
        the snippet of text that occurs immediately after the text which
        is being selected.

    """

    exact: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None

    def exact_from_ends(self, text: str) -> str:
        """
        Get quotation between the prefix and suffix in a text.

        :param text:
            the passage where an exact quotation needs to be located.

        :returns:
            the passage between :attr:`prefix` and :attr:`suffix` in ``text``.
        """

        if self.prefix:
            left_end: int = text.find(self.prefix)
            if left_end == -1:
                raise ValueError(
                    f"'prefix' value '{self.prefix}' not found in '{text}'"
                )
            left_end += len(self.prefix)
        else:
            left_end = 0
        if self.suffix:
            right_end: Optional[int] = text.find(self.suffix)
        else:
            right_end = None
        if right_end == -1:
            raise ValueError(f"'suffix' value '{self.suffix}' not found in '{text}'")
        return text[left_end:right_end]

    def dump(self):
        """
        Serialize the selector.

        Based on the JSON serialization format in the `Web Annotation Data Model
        <https://www.w3.org/TR/annotation-model/#text-quote-selector>`_
        """
        return {
            "type": "TextQuoteSelector",
            "exact": self.exact,
            "prefix": self.prefix,
            "suffix": self.suffix,
        }

    def get_interval(self, text: str) -> Optional[Tuple[int, int]]:
        """
        Get the interval where the selected quote appears in "text".
        """
        regex = self.passage_regex
        match = re.search(regex, text, re.IGNORECASE)
        if match:
            # Getting indices from match group 1 (in the parentheses),
            # not match 0 which includes prefix and suffix
            return (match.start(1), match.end(1))
        return None

    def as_position_selector(self, text: str) -> TextPositionSelector:
        interval = self.get_interval(text)
        if not interval:
            return None
        return TextPositionSelector(start=interval[0], end=interval[1])

    @property
    def passage_regex(self):
        """Get a regex to identify the selected text."""
        prefix = (re.escape(self.prefix) + r"\s*") if self.prefix else ""
        suffix = (r"\s*" + re.escape(self.suffix)) if self.suffix else ""
        return (prefix + r"(" + re.escape(self.exact) + r")" + suffix).strip()


@dataclass(frozen=True)
class TextPositionSelector:
    """
    Describes a textual segment by start and end positions.

    Based on the `Web Annotation Data Model
    <https://www.w3.org/TR/annotation-model/#text-position-selector>`_

    :param start:
        The starting position of the segment of text.
        The first character in the full text is character position 0,
        and the character is included within the segment.

    :param end:
        The end position of the segment of text.
        The character is not included within the segment.

    """

    start: int = 0
    end: Optional[int] = None

    def __add__(self, other: TextPositionSelector) -> TextPositionSelector:
        """
        Make a new selector covering the combined ranges of self and other.
        """
        if not isinstance(other, TextPositionSelector):
            raise TypeError
        if (not other.end or self.start <= other.end) and (
            not self.end or other.start <= self.end
        ):
            return TextPositionSelector(
                start=min(self.start, other.start), end=max(self.end, other.end)
            )
        return self

    def combine(self, other: TextPositionSelector, text: str):
        """
        Make new selector combining ranges of self and other if it will fit in text.
        """
        for selector in (self, other):
            if not selector.validate(text):
                raise ValueError(
                    f'Text "{text}" is too short to include '
                    + f"the interval ({selector.start}, {selector.end})"
                )
        return self + other

    def dump(self):
        return {"type": "TextPositionSelector", "start": self.start, "end": self.end}

    def passage(self, text: str) -> str:
        """
        Get the quotation from text identified by start and end positions.
        """
        if not self.validate(text):
            raise ValueError(
                f'Text "{text}" is too short to include '
                + f"the interval ({self.start}, {self.end})"
            )
        return text[self.start : self.end]

    def validate(self, text: str) -> bool:
        """
        Verify that selector's text positions exist in text.
        """
        if self.end and self.end > len(text):
            return False
        return True
