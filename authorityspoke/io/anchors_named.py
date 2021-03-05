from typing import Dict, List, NamedTuple

from anchorpoint.textselectors import TextQuoteSelector
from anchorpoint.schemas import SelectorSchema
from marshmallow import fields, pre_load, Schema


class NamedAnchors(NamedTuple):
    name: str
    quotes: List[TextQuoteSelector]
