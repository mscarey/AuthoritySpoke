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
    """

    exact: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    path: Optional[str] = None
