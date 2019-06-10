"""
Selectors for getting text from legislation and court decisions.

Based on the `Web Annotation Data Model <https://www.w3.org/TR/annotation-model/>`_
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from typing import Optional, Union


@dataclass(frozen=True)
class TextQuoteSelector:
    """
    Describes a textual segment by quoting it, or passages before or after it.

    Based on the `Web Annotation Data Model
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

    :param source:
        the :class:`.Code` where the quoted text can be found,
        or the :class:`.Regime` that has enacted it.
        Only needed if ``exact`` is not specified.
    """

    path: Optional[str] = None
    exact: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    source: Optional[Union[Regime, Code]] = None

    def __post_init__(self):

        if self.path and not self.path.startswith("/"):
            object.__setattr__(self, "path", "/" + self.path)
        if self.path and self.path.endswith("/"):
            object.__setattr__(self, "path", self.path.rstrip("/"))

        if not self.exact:
            if self.source:
                self.set_exact_from_source(self.source)

        object.__delattr__(self, "source")

    def set_exact_from_source(self, source: Union[Regime, Code]) -> None:
        """Use text found in ``source`` as ``exact`` parameter for ``self``."""
        if source.__class__.__name__ == "Regime":
            code = source.get_code(self.path)
        elif self.source.__class__.__name__ == "Code":
            code = source
        else:
            return None

        selection = code.select_text(self)
        object.__setattr__(self, "exact", self.exact_from_ends(selection))

    def exact_from_ends(self, text: str) -> str:
        """
        Locate an exact passage from some text.

        :param text:
            the passage where an exact quotation needs to be located.

        :returns:
            the passage between ``self.prefix`` and ``self.suffix`` in ``text``.
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

    @property
    def json(self):
        """
        Serialize the selector.

        Based on the JSON serialization format in the `Web Annotation Data Model
        <https://www.w3.org/TR/annotation-model/#text-quote-selector>`_
        """
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
