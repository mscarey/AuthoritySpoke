from __future__ import annotations

import json
from dataclasses import dataclass

from typing import Optional


@dataclass(frozen=True)
class TextQuoteSelector:
    """
    A selector that describes a textual segment by means of quoting it,
    plus passages before or after it.

    Compare with the `Web Annotation Data Model
    <https://www.w3.org/TR/annotation-model/#text-quote-selector>`_

    :param path:
        a path from the root of the document to the XML element where
        the selected text can be found.

    :param exact:
        a copy of the text which is being selected, after normalization.
        If None, then the entire text of the element identified by the
        `path` parameter is selected. If `path` is also None, then the
        whole :class:`.Code` is selected.

    :param prefix:
        a snippet of text that occurs immediately before the text which
        is being selected.

    :param suffix:
        the snippet of text that occurs immediately after the text which
        is being selected.

    :param start:
        the beginning of the quoted text. Only needed
        if ``exact`` is not specified.

    :param end:
        the end of the quoted text. Only needed
        if ``exact`` is not specified.

    :param code:
        the :class:`.Code` where the quoted text can be found.
        Only needed if ``exact`` is not specified.
    """

    path: Optional[str] = None
    exact: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    code: Optional["Code"] = None

    def __post_init__(self):
        def exact_from_ends(text: str) -> str:
            """
            Locates and returns an exact quotation from a text passage given the
            beginning and end of the passage.

            :param text:
                the passage where an exact quotation needs to be located.

            :returns:
                the exact quotation from the text passage
            """

            if self.start:
                l = text.find(self.start)
            if self.end:
                r = text.find(self.end) + len(self.end)
            if l == -1:
                raise ValueError(f"'start' value {self.start} not found in {text}")
            if r == -1:
                raise ValueError(f"'end' value {self.end} not found in {text}")
            return text[l or None : r or None]

        if not self.exact:
            if self.start or self.end:
                selection = self.code.select_text(TextQuoteSelector(path=self.path))
                object.__setattr__(self, "exact", exact_from_ends(selection))
        object.__delattr__(self, "code")
        object.__delattr__(self, "start")
        object.__delattr__(self, "end")

    @property
    def json(self):
        return json.dumps(
            {
                "source": self.path,
                "selector": {
                    "type": "TextQuoteSelector",
                    "exact": self.exact,
                    "prefix": self.prefix,
                    "suffix": self.suffix,
                },
            }
        )
