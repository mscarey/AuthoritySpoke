from typing import Dict, List, NamedTuple

from anchorpoint.textselectors import TextQuoteSelector
from anchorpoint.schemas import SelectorSchema
from marshmallow import fields, pre_load, Schema


class NamedAnchors(NamedTuple):
    name: str
    quotes: List[TextQuoteSelector]


class NamedAnchorsSchema(Schema):
    __model__ = NamedAnchors

    name = fields.Str()
    quotes = fields.Nested(SelectorSchema, many=True)

    def wrap_single_element_in_list(self, data: Dict, many_element: str):
        """Make a specified field a list if it isn't already a list."""
        if data.get(many_element) is not None and not isinstance(
            data[many_element], list
        ):
            data[many_element] = [data[many_element]]
        return data

    @pre_load
    def format_data_to_load(self, data, **kwargs):
        data = self.wrap_single_element_in_list(data, "quotes")
        return data
