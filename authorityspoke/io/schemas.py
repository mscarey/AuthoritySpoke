from typing import Any, Dict, Tuple, Union

from marshmallow import Schema, fields, pre_load, post_load
from marshmallow import ValidationError

from authorityspoke.enactments import Enactment
from authorityspoke.selectors import TextQuoteSelector


class SelectorSchema(Schema):
    __model__ = TextQuoteSelector
    prefix = fields.Str()
    exact = fields.Str()
    suffix = fields.Str()

    def split_text(self, text: str) -> Tuple[str, ...]:
        """
        Break up shorthand text selector format into three fields.

        Tries to break up the string into :attr:`~TextQuoteSelector.prefix`,
        :attr:`~TextQuoteSelector.exact`,
        and :attr:`~TextQuoteSelector.suffix`, by splitting on the pipe characters.

        :param text: a string or dict representing a text passage

        :returns: a tuple of the three values
        """

        if text.count("|") == 0:
            return ("", text, "")
        elif text.count("|") == 2:
            return tuple([*text.split("|")])
        raise ValidationError(
            "If the 'text' field is included, it must be either a dict"
            + "with one or more of 'prefix', 'exact', and 'suffix' "
            + "a string containing no | pipe "
            + "separator, or a string containing two pipe separators to divide "
            + "the string into 'prefix', 'exact', and 'suffix'."
        )

    @pre_load
    def expand_shorthand(
        self, data: Union[str, Dict[str, str]], **kwargs
    ) -> Dict[str, str]:
        """Convert input from shorthand format to normal selector format."""
        if isinstance(data, str):
            data = {"text": data}
        text = data.get("text")
        if text:
            data["prefix"], data["exact"], data["suffix"] = self.split_text(text)
            del data["text"]
        return data

    @post_load
    def make_selector(self, data, **kwargs):
        return TextQuoteSelector(**data)


class EnactmentSchema(Schema):
    __model__ = Enactment
    source = fields.Url(relative=True)
    selector = fields.Nested(SelectorSchema)


SCHEMAS = [schema() for schema in Schema.__subclasses__()]


def get_schema_for_item(item: Any) -> Schema:
    """
    Find the Marshmallow schema for an AuthoritySpoke object.
    """
    for option in SCHEMAS:
        if item.__class__ == option.__model__:
            return option
    return None
