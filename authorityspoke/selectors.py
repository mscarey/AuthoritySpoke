"""
Selectors for getting text from legislation and court decisions.

Based on the `Web Annotation Data Model <https://www.w3.org/TR/annotation-model/>`_
"""

from __future__ import annotations

import json
import re
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
        Only needed if ``exact`` is not specified. If this
        parameter is given, then the ``exact`` text will be
        stored even if it's the entire text of a section or
        :class:`.Code`.
    """

    path: Optional[str] = None
    exact: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    source: Optional[Union[Regime, Code]] = None

    def __post_init__(self):

        if self.path and not (
            self.path.startswith("/") or self.path.startswith("http")
        ):
            object.__setattr__(self, "path", "/" + self.path)
        if self.path and self.path.endswith("/"):
            object.__setattr__(self, "path", self.path.rstrip("/"))

        if self.source and not self.path:
            object.__setattr__(self, "path", self.source.uri)

        if self.source and not self.exact:
            object.__setattr__(self, "exact", self.set_exact_from_source(self.source))

        object.__delattr__(self, "source")

    def set_exact_from_source(self, source: Union[Regime, Code]) -> Optional[str]:
        """Use text found in ``source`` as ``exact`` parameter for ``self``."""
        if source.__class__.__name__ == "Regime":
            code = source.get_code(self.path)
        elif source.__class__.__name__ == "Code":
            code = source
        else:
            raise TypeError(f'"source" parameter must be class "Regime" or "Code"')

        section_text = code.section_text(self.path)
        return self.exact_from_ends(section_text)

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
        return text[left_end:right_end].strip()

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

    @property
    def passage_regex(self):
        """Get a regex to identify the selected text."""
        prefix = (re.escape(self.prefix) + r"\s*") if self.prefix else ""
        suffix = (r"\s*" + re.escape(self.suffix)) if self.suffix else ""
        return (prefix + r"(" + re.escape(self.exact) + r")" + suffix).strip()
