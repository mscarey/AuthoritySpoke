from typing import Any, Dict, List, Optional, Tuple, Type, Union

from marshmallow import Schema, fields, validate
from marshmallow import pre_dump, pre_load, post_dump, post_load
from marshmallow import ValidationError

from pint import UnitRegistry

from authorityspoke.enactments import Enactment
from authorityspoke.entities import Entity
from authorityspoke.evidence import Exhibit, Evidence
from authorityspoke.factors import Factor
from authorityspoke.facts import Fact
from authorityspoke.pleadings import Pleading, Allegation
from authorityspoke.predicates import Predicate
from authorityspoke.procedures import Procedure
from authorityspoke.selectors import TextQuoteSelector

from utils.marshmallow_oneofschema.one_of_schema import OneOfSchema

ureg = UnitRegistry()


class ExpandableSchema(Schema):
    def get_from_mentioned(self, data, **kwargs):
        """
        Replaces data to load with any object with same name in "mentioned".
        """

        self.context["mentioned"] = self.context.get("mentioned") or {}
        if isinstance(data, str):
            return self.context["mentioned"].get_by_name(data)
        return data

    def consume_type_field(self, data, **kwargs):
        if data.get("type"):
            ty = data.pop("type").lower()
            if ty != self.__model__.__name__.lower():
                raise ValidationError(
                    f'type field "{ty} does not match model type {self.__model__}'
                )
        return data


class SelectorSchema(ExpandableSchema):
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


class EnactmentSchema(ExpandableSchema):
    __model__ = Enactment
    name = fields.String(missing=None)
    source = fields.Url(relative=True)
    selector = fields.Nested(SelectorSchema, missing=None)

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

    @pre_load
    def format_data_to_load(self, data, **kwargs):
        data = self.get_from_mentioned(data)
        data = self.fix_source_path_errors(data)
        data = self.move_selector_fields(data)
        data = self.consume_type_field(data)
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
    if quantity is None:
        return None
    if isinstance(quantity, (int, float)):
        return quantity
    return f"{quantity.magnitude} {quantity.units}"


class PredicateSchema(ExpandableSchema):
    __model__ = Predicate
    content = fields.Str()
    truth = fields.Bool(missing=True)
    reciprocal = fields.Bool(missing=False)
    comparison = fields.Str(
        missing="",
        validate=validate.OneOf([""] + list(Predicate.opposite_comparisons.keys())),
    )
    quantity = fields.Function(dump_quantity, deserialize=read_quantity, missing=None)

    def split_quantity_from_content(
        self, content: str
    ) -> Tuple[str, Optional[str], Optional[Union[ureg.Quantity, int, float]]]:
        placeholder = "{}"
        for comparison in {
            **Predicate.normalized_comparisons,
            **Predicate.opposite_comparisons,
        }:
            if comparison in content:
                content, quantity_text = content.split(comparison)
                content += placeholder
                return content, comparison, quantity_text
        return content, "", None

    def normalize_comparison(self, data, **kwargs):
        if data.get("quantity") and not data.get("comparison"):
            data["comparison"] = "="

        if data.get("comparison") is None:
            data["comparison"] = ""

        if data.get("comparison") in Predicate.normalized_comparisons:
            data["comparison"] = Predicate.normalized_comparisons[data["comparison"]]
        return data

    @pre_load
    def format_data_to_load(self, data, **kwargs):
        if not data.get("quantity"):
            data["content"], data["comparison"], data[
                "quantity"
            ] = self.split_quantity_from_content(data["content"])
        data = self.normalize_comparison(data)
        return data

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)


class EntitySchema(ExpandableSchema):
    __model__: Type = Entity
    name = fields.Str(missing=None)
    generic = fields.Bool(missing=True)
    plural = fields.Bool()

    @pre_load
    def format_data_to_load(self, data, **kwargs):
        data = self.get_from_mentioned(data)
        data = self.consume_type_field(data)
        return data

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)


class FactSchema(ExpandableSchema):
    __model__: Type = Fact
    predicate = fields.Nested(PredicateSchema)
    context_factors = fields.Nested("FactorSchema", many=True)
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
                if data.get(predicate_field):
                    data["predicate"][predicate_field] = data[predicate_field]
                    del data[predicate_field]
        return data

    def get_references_from_mentioned(
        self, content: str, placeholder: str = "{}"
    ) -> Tuple[str, List[Dict]]:
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
        mentioned = self.context.get("mentioned") or {}
        context_with_indices: Dict[Union[Enactment, Factor], int] = {}
        for factor in mentioned:
            if factor.name and factor.name in content and factor.name != content:
                factor_index = content.find(factor.name)
                for named_factor in context_with_indices:
                    if context_with_indices[named_factor] > factor_index:
                        context_with_indices[named_factor] -= len(factor.name) - len(
                            placeholder
                        )
                context_with_indices[factor] = factor_index
                content = content.replace(factor.name, placeholder)
        sorted_factors = sorted(context_with_indices, key=context_with_indices.get)
        factor_schema = FactorSchema()
        factor_schema.context["mentioned"] = self.context["mentioned"]
        return content, [factor_schema.dump(factor) for factor in sorted_factors]

    @pre_load
    def format_data_to_load(self, data, **kwargs):
        data = self.get_from_mentioned(data)
        data = self.nest_predicate_fields(data)
        if not data.get("context_factors"):
            data["predicate"]["content"], data[
                "context_factors"
            ] = self.get_references_from_mentioned(data["predicate"]["content"])
        data = self.consume_type_field(data)
        return data

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)


class ExhibitSchema(ExpandableSchema):
    __model__: Type = Exhibit
    form = fields.Str(missing=None)
    statement = fields.Nested(FactSchema, missing=None)
    stated_by = fields.Nested(EntitySchema, missing=None)
    name = fields.Str(missing=None)
    absent = fields.Bool(missing=False)
    generic = fields.Bool(missing=False)

    @pre_load
    def format_data_to_load(self, data, **kwargs):
        data = self.get_from_mentioned(data)
        data = self.consume_type_field(data)
        return data

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)


class PleadingSchema(ExpandableSchema):
    __model__: Type = Pleading
    filer = fields.Nested(EntitySchema, missing=None)
    name = fields.Str(missing=None)
    absent = fields.Bool(missing=False)
    generic = fields.Bool(missing=False)

    @pre_load
    def format_data_to_load(self, data, **kwargs):
        data = self.get_from_mentioned(data)
        data = self.consume_type_field(data)
        return data

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)


class AllegationSchema(ExpandableSchema):
    __model__: Type = Allegation
    pleading = fields.Nested(PleadingSchema, missing=None)
    statement = fields.Nested(FactSchema, missing=None)
    name = fields.Str(missing=None)
    absent = fields.Bool(missing=False)
    generic = fields.Bool(missing=False)

    @pre_load
    def format_data_to_load(self, data, **kwargs):
        data = self.get_from_mentioned(data)
        data = self.consume_type_field(data)
        return data

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)


class EvidenceSchema(ExpandableSchema):
    __model__: Type = Evidence
    exhibit = fields.Nested(ExhibitSchema, missing=None)
    to_effect = fields.Nested(FactSchema, missing=None)
    name = fields.Str(missing=None)
    absent = fields.Bool(missing=False)
    generic = fields.Bool(missing=False)

    @pre_load
    def format_data_to_load(self, data, **kwargs):
        data = self.get_from_mentioned(data)
        data = self.consume_type_field(data)
        return data

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)


class FactorSchema(OneOfSchema, ExpandableSchema):
    __model__: Type = Factor
    type_schemas = {
        "allegation": AllegationSchema,
        "Allegation": AllegationSchema,
        "entity": EntitySchema,
        "Entity": EntitySchema,
        "evidence": EvidenceSchema,
        "Evidence": EvidenceSchema,
        "exhibit": ExhibitSchema,
        "Exhibit": ExhibitSchema,
        "fact": FactSchema,
        "Fact": FactSchema,
        "pleading": PleadingSchema,
        "Pleading": PleadingSchema,
    }

    def pre_load(self, data, **kwargs):
        data = self.get_from_mentioned(data)
        return data

    def get_obj_type(self, obj):
        return obj.__class__.__name__


class ProcedureSchema(ExpandableSchema):
    __model__: Type = Procedure
    inputs = fields.Nested(FactorSchema, many=True)
    despite = fields.Nested(FactorSchema, many=True)
    outputs = fields.Nested(FactorSchema, many=True)

    @pre_load
    def format_data_to_load(self, data, **kwargs):
        standard_keys = {"given": "inputs", "then": "outputs"}
        for key, value in standard_keys.items():
            if key in data:
                data[value] = data[key].pop()
        return data

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)


SCHEMAS = [schema for schema in ExpandableSchema.__subclasses__()]


def get_schema_for_factor_record(record: Dict) -> Schema:
    """
    Find the Marshmallow schema for an AuthoritySpoke object.
    """
    for option in SCHEMAS:
        if record.get("type", "").lower() == option.__model__.__name__.lower():
            return option()
    return None


def get_schema_for_item(item: Any) -> Schema:
    """
    Find the Marshmallow schema for an AuthoritySpoke object.
    """
    for option in SCHEMAS:
        if item.__class__ == option.__model__:
            return option()
    return None
