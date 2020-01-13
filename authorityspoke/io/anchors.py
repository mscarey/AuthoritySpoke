"""Functions for loading TextQuoteSelectors."""

from collections import defaultdict
from typing import Any, Dict, Iterable, List, Union

from anchorpoint.textselectors import TextQuoteSelector

from authorityspoke.opinions import TextLinkDict

from authorityspoke.io import schemas
from authorityspoke.io.schemas import RawSelector, RawHolding
from authorityspoke.io.name_index import Mentioned


def read_selector(record: RawSelector) -> TextQuoteSelector:
    """
    Create new selector from JSON user input.

    :param record:
        a string or dict representing a text passage

    :returns: a new :class:`TextQuoteSelector`
    """
    selector_schema = schemas.SelectorSchema(many=False)
    return selector_schema.load(record)


def read_selectors(record: Iterable[RawSelector]) -> List[TextQuoteSelector]:
    r"""
    Create list of :class:`.TextQuoteSelector`\s from JSON user input.

    If the input is a :class:`str`, tries to break up the string
    into :attr:`~TextQuoteSelector.prefix`, :attr:`~TextQuoteSelector.exact`,
    and :attr:`~TextQuoteSelector.suffix`, by splitting on the pipe characters.

    :param record:
        a string or dict representing a text passage, or list of
        strings and dicts.

    :returns: a list of :class:`TextQuoteSelector`\s
    """
    selector_schema = schemas.SelectorSchema(many=True)
    return selector_schema.load(record)


def collect_anchors(obj: Dict) -> List[TextQuoteSelector]:
    r"""Get list containing any available text anchors."""
    anchors = obj.get("anchors") or []
    if not isinstance(anchors, List):
        anchors = [anchors]
    return read_selectors(anchors)


def get_named_anchors(mentioned: Mentioned) -> TextLinkDict:
    r"""
    Move anchors fields to a dict linking object names to lists of anchors.

    To be used during loading of :class:`.Holding`\s.
    Keys are :class:`.Factor`\s, :class:`.Enactment`\s, or :class:`.Holding`\s,
    and values are lists of the :class:`.Opinion` passages that reference them.

    Assumes that the value of the anchors field is a list (not a dict representing a
    single text anchor, and not a string in the "shorthand" anchor format).

    :param mentioned:
        a dict representing named :class:`.Factor`\s and :class:`.Enactment`\s

    :returns:
        a dict with keys from the mentioned dict, where each key has as its value
        just the "anchors" field from the corresponding dict in "mentioned"
    """
    anchors: TextLinkDict = defaultdict(list)
    for key, value in mentioned.items():
        if "anchors" in value:
            for anchor in value["anchors"]:
                anchors[key].append(anchor)
    for key in anchors:
        anchors[key] = read_selectors(anchors[key])
    return anchors


def get_holding_anchors(
    record: Union[RawHolding, List[RawHolding]]
) -> List[List[TextQuoteSelector]]:
    """Make indexes of text anchors for a list of Holdings."""

    if isinstance(record, list):
        return [collect_anchors(holding) for holding in record]
    return [collect_anchors(record)]
