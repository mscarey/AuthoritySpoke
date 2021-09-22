"""Schema for serializing text selectors."""

from typing import Dict, List, Mapping, Optional, Sequence, TypedDict, Union

from marshmallow import Schema, fields, post_load, pre_load

from anchorpoint.textselectors import (
    TextQuoteSelector,
    TextPositionSelector,
    TextPositionSet,
)


class PositionSelectorDict(TypedDict, total=False):
    """Dict representing TextPositionSelector, to be loaded with SelectorSchema."""

    start: int
    end: Optional[int]


class PositionSchema(Schema):
    r"""Schema for :class:`~anchorpoint.textselectors.TextPositionSelector`."""
    __model__ = TextPositionSelector

    start = fields.Int()
    end = fields.Int(load_default=None)

    class Meta:
        ordered = True

    def convert_bool_to_dict(self, data: bool) -> Dict[str, int]:
        """Interpret True as a TextPositionSelector including the whole section."""

        if data is True:
            return {"start": 0}
        return {"start": 0, "end": 0}

    @pre_load
    def preprocess_data(
        self, data: Union[bool, Mapping[str, int]], **kwargs
    ) -> Mapping[str, int]:
        if isinstance(data, bool):
            return self.convert_bool_to_dict(data)
        return data

    @post_load
    def make_object(
        self, data: PositionSelectorDict, **kwargs
    ) -> Optional[TextPositionSelector]:
        if data["start"] == data.get("end") == 0:
            return None
        return TextPositionSelector(**data)


class QuoteSchema(Schema):
    r"""Schema for :class:`~anchorpoint.textselectors.TextPositionSelector`."""
    __model__ = TextQuoteSelector

    prefix = fields.Str(load_default=None)
    exact = fields.Str(load_default=None)
    suffix = fields.Str(load_default=None)

    class Meta:
        ordered = True

    def expand_anchor_shorthand(self, text: str) -> Mapping[str, str]:
        """
        Convert input from shorthand format to normal selector format.
            >>> schema = SelectorSchema()
            >>> schema.expand_anchor_shorthand("eats,|shoots,|and leaves")
            {'prefix': 'eats,', 'exact': 'shoots,', 'suffix': 'and leaves'}
        """
        result = {}
        (
            result["prefix"],
            result["exact"],
            result["suffix"],
        ) = TextQuoteSelector.split_anchor_text(text)
        return result

    @pre_load
    def preprocess_data(
        self, data: Union[str, Mapping[str, str]], **kwargs
    ) -> Mapping[str, str]:
        if isinstance(data, str):
            return self.expand_anchor_shorthand(data)
        return data

    @post_load
    def make_object(self, data: Dict[str, str], **kwargs) -> TextQuoteSelector:

        return TextQuoteSelector(**data)


class TextPositionSetSchema(Schema):
    """Schema for a set of positions in a text."""

    __model__ = TextPositionSet
    quotes = fields.Nested(QuoteSchema, many=True)
    positions = fields.Nested(PositionSchema, many=True)

    @pre_load
    def preprocess_data(
        self,
        data: Union[
            str, Mapping[str, Union[Mapping[str, str], List[Mapping[str, str]]]]
        ],
        **kwargs
    ) -> Mapping[str, List[Mapping[str, str]]]:
        if isinstance(data.get("quotes"), dict):
            data["quotes"] = [data["quotes"]]
        if isinstance(data.get("positions"), dict):
            data["positions"] = [data["positions"]]
        return data

    @post_load
    def make_object(self, data: Dict[str, str], **kwargs) -> TextPositionSet:

        return TextPositionSet(**data)
