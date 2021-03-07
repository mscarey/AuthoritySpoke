"""Functions for loading TextQuoteSelectors."""

from collections import defaultdict
from typing import Any, Dict, Iterable, List, Sequence, Union

from anchorpoint.schemas import SelectorSchema
from anchorpoint.textselectors import TextQuoteSelector

from authorityspoke.opinions import TextLinkDict

from authorityspoke.io.name_index import Mentioned, RawFactor
from authorityspoke.io.schemas import NamedAnchorsSchema

RawSelector = Union[str, Dict[str, str]]
RawEnactment = Dict[str, Union[str, List[RawSelector]]]
RawProcedure = Dict[str, Sequence[RawFactor]]
RawRule = Dict[str, Union[RawProcedure, Sequence[RawEnactment], str, bool]]
RawHolding = Dict[str, Union[RawRule, str, bool]]


def read_selector(record: RawSelector) -> TextQuoteSelector:
    """
    Create new selector from JSON user input.

    :param record:
        a string or dict representing a text passage

    :returns: a new :class:`TextQuoteSelector`
    """
    selector_schema = SelectorSchema(many=False)
    return selector_schema.load(record)


def collect_anchors(obj: Dict) -> List[TextQuoteSelector]:
    r"""Get list containing any available text anchors."""
    anchors = obj.get("anchors") or []
    if not isinstance(anchors, List):
        anchors = [anchors]
    selector_schema = NamedAnchorsSchema(many=True)
    return selector_schema.load(anchors)


def get_holding_anchors(
    record: Union[RawHolding, List[RawHolding]]
) -> List[List[TextQuoteSelector]]:
    """Make indexes of text anchors for a list of Holdings."""

    if isinstance(record, list):
        return [collect_anchors(holding) for holding in record]
    return [collect_anchors(record)]
