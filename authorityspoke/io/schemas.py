from typing import Any, Dict, List, Tuple, Type, Union

from marshmallow import Schema, fields, validate
from marshmallow import pre_dump, pre_load, post_dump, post_load
from marshmallow import ValidationError

from pint import UnitRegistry

from authorityspoke.enactments import Enactment
from authorityspoke.entities import Entity
from authorityspoke.factors import Factor, TextLinkDict
from authorityspoke.facts import Fact
from authorityspoke.predicates import Predicate
from authorityspoke.selectors import TextQuoteSelector

ureg = UnitRegistry()


class SelectorSchema(Schema):
    __model__ = TextQuoteSelector
    prefix = fields.Str(missing=None)
    exact = fields.Str(missing=None)
    suffix = fields.Str(missing=None)

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
    def make_object(self, data, **kwargs):
        return self.__model__(**data)


class EnactmentSchema(Schema):
    __model__ = Enactment
    name = fields.String(missing=None)
    source = fields.Url(relative=True)
    selector = fields.Nested(SelectorSchema, missing=None)

    @pre_load
    def move_selector_fields(self, data, **kwargs):
        """
        Nest fields used for :class:`SelectorSchema` model.

        If the fields are already nested, they need not to be moved.

        The fields can only be moved into a "selector" field with a dict
        value, not a "selectors" field with a list value.
        """
        # Dumping the data because it seems to need to be loaded all at once.
        if isinstance(data.get("selector"), TextQuoteSelector):
            data["selector"] = SelectorSchema().dump(data["selector"])

        selector_field_names = ["text", "exact", "prefix", "suffix"]
        for name in selector_field_names:
            if data.get(name):
                if not data.get("selector"):
                    data["selector"] = {}
                data["selector"][name] = data[name]
                del data[name]
        return data

    @pre_load
    def fix_source_path_errors(self, data, **kwargs):

        if not data.get("source"):
            data["source"] = self.context["code"].uri

        if data.get("source"):
            if not (
                data["source"].startswith("/") or data["source"].startswith("http")
            ):
                data["source"] = "/" + data["source"]
            if data["source"].endswith("/"):
                data["source"] = data["source"].rstrip("/")
        return data

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data, code=self.context["code"])


def read_quantity(value: Union[float, int, str]) -> Union[float, int, ureg.Quantity]:
    """
    Create pint quantity object from text.

    See `pint tutorial <https://pint.readthedocs.io/en/0.9/tutorial.html>`_

    :param quantity:
        when a string is being parsed for conversion to a
        :class:`Predicate`, this is the part of the string
        after the equals or inequality sign.
    :returns:
        a Python number object or a :class:`Quantity`
        object created with `pint.UnitRegistry
        <https://pint.readthedocs.io/en/0.9/tutorial.html>`_.
    """
    if isinstance(value, (int, float)):
        return value
    quantity = value.strip()
    if quantity.isdigit():
        return int(quantity)
    float_parts = quantity.split(".")
    if len(float_parts) == 2 and all(
        substring.isnumeric() for substring in float_parts
    ):
        return float(quantity)
    return ureg.Quantity(quantity)


def dump_quantity(obj: Predicate) -> Union[float, int, str]:
    """
    Convert quantity to string if it's a pint `ureg.Quantity` object.
    """
    quantity = obj.quantity
    if isinstance(quantity, (int, float)):
        return quantity
    return f"{quantity.magnitude} {quantity.units}"


class PredicateSchema(Schema):
    __model__ = Predicate
    content = fields.Str()
    truth = fields.Bool(missing=True)
    reciprocal = fields.Bool(missing=False)
    comparison = fields.Str(
        missing="",
        validate=validate.OneOf([""] + list(Predicate.opposite_comparisons.keys())),
    )
    quantity = fields.Function(dump_quantity, deserialize=read_quantity)

    @pre_load
    def normalize_comparison(self, data, **kwargs):
        if data.get("quantity") and not data.get("comparison"):
            data["comparison"] = "="

        if data.get("comparison") is None:
            data["comparison"] = ""

        normalized = {"==": "=", "!=": "<>"}
        if data.get("comparison") in normalized:
            data["comparison"] = normalized[data["comparison"]]
        return data

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)


class FactorSchema(Schema):
    __model__: Type = Factor
    name = fields.Str(missing=None)
    generic = fields.Bool(missing=False)

    @post_dump
    def add_type_field(self, data, **kwargs):
        data["type"] = self.__model__.__name__
        return data

    @post_load(pass_original=True)
    def make_subclass_factor(self, data, original, **kwargs):
        """
        Return the result of loading with the subclass schema.

        Discards the result of loading with FactorSchema.

        If this function is called from within a subclass,
        it deserializes using the subclass model.
        """
        if self.__model__ == Factor:
            schema = get_schema_for_factor_record(original)
            return schema.load(original)
        return self.__model__(**data)


def get_references_from_mentioned(
    content: str, mentioned: TextLinkDict, placeholder: str = "{}"
) -> Tuple[str, List[Union[Enactment, Factor]]]:
    r"""
    Retrieve known context :class:`Factor`\s for new :class:`Fact`.

    :param content:
        the content for the :class:`Fact`\'s :class:`Predicate`.

    :param mentioned:
        list of :class:`Factor`\s with names that could be
        referenced in content

    :param placeholder:
        a string to replace the names of
        referenced :class:`Factor`\s in content

    :returns:
        the content string with any referenced :class:`Factor`\s
        replaced by placeholder, and a list of referenced
        :class:`Factor`\s in the order they appeared in content.
    """
    sorted_mentioned = sorted(
        mentioned.keys(), key=lambda x: len(x.name) if x.name else 0, reverse=True
    )
    context_with_indices: Dict[Union[Enactment, Factor], int] = {}
    for factor in sorted_mentioned:
        if factor.name and factor.name in content and factor.name != content:
            factor_index = content.find(factor.name)
            for named_factor in context_with_indices:
                if context_with_indices[named_factor] > factor_index:
                    context_with_indices[named_factor] -= len(factor.name) - len(
                        placeholder
                    )
            context_with_indices[factor] = factor_index
            content = content.replace(factor.name, placeholder)
    context_factors = sorted(context_with_indices, key=context_with_indices.get)
    return content, tuple(context_factors)


def get_references_from_string(
    content: str, mentioned: TextLinkDict
) -> Tuple[str, List[Entity], TextLinkDict]:
    r"""
    Make :class:`.Entity` context :class:`.Factor`\s from string.

    This function identifies context :class:`.Factor`\s by finding
    brackets around them, while :func:`get_references_from_mentioned`
    depends on knowing the names of the context factors in advance.
    Also, this function works only when all the context_factors
    are type :class:`.Entity`.

    Despite "placeholder" being defined as a variable elsewhere,
    this function isn't compatible with any placeholder string other
    than "{}".

    :param content:
        a string containing a clause making an assertion.
        Curly brackets surround the names of :class:`.Entity`
        context factors to be created.

    :param mentioned:
        a :class:`.TextLinkDict` of known :class:`.Factor`\s.
        It will not be searched for :class:`.Factor`\s to add
        to `context_factors`, but newly created :class:`.Entity`
        object will be added to it.

    :returns:
        a :class:`Predicate` and :class:`.Entity` objects
        from a string that has curly brackets around the
        context factors and the comparison/quantity.
    """
    pattern = r"\{([^\{]+)\}"
    entities_as_text = re.findall(pattern, content)

    context_factors = []
    for entity_name in entities_as_text:
        entity = Entity(name=entity_name)
        content = content.replace(entity_name, "")
        context_factors.append(entity)
        mentioned[entity] = []

    return content, tuple(context_factors), mentioned


class FactSchema(FactorSchema):
    __model__: Type = Fact
    predicate = fields.Nested(PredicateSchema)
    context_factors = fields.Nested(FactorSchema, many=True)
    standard_of_proof = fields.Str(missing=None)
    name = fields.Str(missing=None)
    absent = fields.Bool(missing=False)
    generic = fields.Bool(missing=False)

    def nest_predicate_fields(self, data, **kwargs):
        """
        Make sure predicate-related fields are in a dict under "predicate" key.
        """
        if data.get("content") and not data.get("predicate"):
            data["predicate"] = {}
            for predicate_field in [
                "content",
                "truth",
                "reciprocal",
                "comparison",
                "quantity",
            ]:
                if data.get("predicate_field"):
                    data["predicate"][predicate_field] = data["predicate_field"]
                    del data["predicate_field"]
        return data

    @pre_load
    def make_context_factors(self, data, **kwargs):
        data = self.nest_predicate_fields(data)

        placeholder = "{}"  # to be replaced in the Fact's string method
        if not data["name"]:
            truth = data["predicate"].get("truth")
            content = data["predicate"].get("content")
            data["name"] = f'{"false " if not truth else ""}{content}'
        data["name"] = data["name"].replace("{", "").replace("}", "")

        if not data["context_factors"]:
            if placeholder[0] in data["predicate"]["content"]:
                data["predicate"]["content"], data["context_factors"], self.context[
                    "mentioned"
                ] = get_references_from_string(content, mentioned)
            else:
                data["predicate"]["content"], data[
                    "context_factors"
                ] = get_references_from_mentioned(content, mentioned, placeholder)
            return data


class EntitySchema(FactorSchema):
    __model__: Type = Entity
    name = fields.Str(missing=None)
    generic = fields.Bool(missing=True)
    plural = fields.Bool()


SCHEMAS = [schema for schema in Schema.__subclasses__()] + [
    schema for schema in FactorSchema.__subclasses__()
]


def get_schema_for_factor_record(record: Dict) -> Schema:
    """
    Find the Marshmallow schema for an AuthoritySpoke object.
    """
    for option in SCHEMAS:
        if record.get("type", "").lower() == option.__model__.__name__.lower():
            return option(unknown="EXCLUDE")
    return None


def get_schema_for_item(item: Any) -> Schema:
    """
    Find the Marshmallow schema for an AuthoritySpoke object.
    """
    for option in SCHEMAS:
        if item.__class__ == option.__model__:
            return option()
    return None
