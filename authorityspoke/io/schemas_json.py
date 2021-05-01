"""
Marshmallow schemas for loading AuthoritySpoke objects from JSON.

Intended for use with machine-generated API responses.
Should be suitable for generating an OpenAPI specification.
"""

from datetime import date
from typing import Any, Dict, List, NamedTuple, Optional, Sequence, Tuple, Type, Union

from marshmallow import Schema, fields, validate, EXCLUDE
from marshmallow import pre_load, post_load

from anchorpoint.textselectors import TextQuoteSelector, TextPositionSelector
from anchorpoint.schemas import SelectorSchema
from legislice import Enactment
from legislice.schemas import EnactmentSchema
from nettlesome.entities import Entity
from nettlesome.predicates import Predicate
from nettlesome.quantities import Comparison, QuantityRange, Quantity

from authorityspoke.decisions import CaseCitation, Decision
from authorityspoke.evidence import Exhibit, Evidence
from nettlesome.factors import Factor
from authorityspoke.facts import Fact
from authorityspoke.holdings import Holding
from authorityspoke.io.name_index import RawFactor, RawPredicate
from authorityspoke.opinions import Opinion
from authorityspoke.pleadings import Pleading, Allegation

from authorityspoke.procedures import Procedure
from authorityspoke.rules import Rule

from authorityspoke.utils.marshmallow_oneofschema.one_of_schema import OneOfSchema

RawSelector = Union[str, Dict[str, str]]
RawEnactment = Dict[str, Union[str, List[RawSelector]]]
RawProcedure = Dict[str, Sequence[RawFactor]]
RawRule = Dict[str, Union[RawProcedure, Sequence[RawEnactment], str, bool]]
RawHolding = Dict[str, Union[RawRule, str, bool]]


RawOpinion = Dict[str, str]
RawCaseCitation = Dict[str, str]
RawDecision = Dict[
    str, Union[str, int, Sequence[RawOpinion], Sequence[RawCaseCitation]]
]


class CaseCitationSchema(Schema):
    """Schema for Decision citations in CAP API response."""

    __model__ = CaseCitation
    cite = fields.Str()
    reporter = fields.Str(data_key="type")

    @post_load
    def make_object(self, data: RawCaseCitation, **kwargs) -> CaseCitation:
        """Load citation."""
        return self.__model__(**data)


class OpinionSchema(Schema):
    """Schema for Opinions, of which there may be several in one Decision."""

    __model__ = Opinion
    position = fields.Str(data_key="type", missing="majority")
    author = fields.Str(missing="")
    text = fields.Str(missing="")

    @pre_load
    def format_data_to_load(self, data: RawOpinion, **kwargs) -> RawOpinion:
        """Standardize author name before loading object."""
        data["author"] = data.get("author", "").strip(",:")
        return data

    @post_load
    def make_object(self, data: RawOpinion, **kwargs) -> CaseCitation:
        return self.__model__(**data)


class DecisionSchema(Schema):
    """Schema for decisions retrieved from Caselaw Access Project API."""

    __model__ = Decision
    name = fields.Str()
    name_abbreviation = fields.Str(missing=None)
    citations = fields.Nested(CaseCitationSchema, many=True)
    opinions = fields.Nested(OpinionSchema, many=True)
    first_page = fields.Int()
    last_page = fields.Int()
    date = fields.Date(data_key="decision_date")
    court = fields.Str()
    jurisdiction = fields.Str(missing=None)
    # docket_number = fields.Str(missing=None)
    # reporter = fields.Str(missing=None)
    # volume = fields.Str(missing=None)
    id = fields.Int()
    cites_to = fields.Nested(CaseCitationSchema, many=True, missing=list)

    class Meta:
        unknown = EXCLUDE

    @pre_load
    def format_data_to_load(self, data: RawDecision, **kwargs) -> RawDecision:
        """Transform data from CAP API response for loading."""
        if not isinstance(data["court"], str):
            data["court"] = data.get("court", {}).get("slug", "")
        data["jurisdiction"] = data.get("jurisdiction", {}).get("slug", "")
        data["opinions"] = (
            data.get("casebody", {}).get("data", {}).get("opinions", [{}])
        )
        data.pop("docket_number", None)
        data.pop("casebody", None)
        data.pop("preview", None)
        data.pop("reporter", None)
        data.pop("volume", None)
        del data["url"]
        data.pop("frontend_url", None)
        return data

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)


def dump_quantity(obj: Predicate) -> Optional[Union[date, float, int, str]]:
    """Convert quantity to string if it's a pint ureg.Quantity object."""
    if not hasattr(obj, "quantity"):
        return None
    if isinstance(obj.quantity, date):
        return obj.quantity.isoformat()
    if isinstance(obj.quantity, (int, float)):
        return obj.quantity
    return f"{obj.quantity.magnitude} {obj.quantity.units}"


class PredicateSchema(Schema):
    """Schema for statements, separate from any claim about their truth or who asserts them."""

    __model__ = Predicate
    template = fields.Str(data_key="content", load_only=True)
    content = fields.Method(serialize="get_content_with_placeholders", dump_only=True)
    truth = fields.Bool(missing=True)
    sign = fields.Str(
        missing=None,
        validate=validate.OneOf([""] + list(QuantityRange.opposite_comparisons.keys())),
    )
    expression = fields.Function(
        dump_quantity, deserialize=Comparison.read_quantity, missing=None
    )

    def get_content_with_placeholders(self, obj) -> str:
        return obj.template.template

    def split_quantity_from_content(
        self, content: str
    ) -> Tuple[str, Optional[str], Optional[Union[Quantity, int, float]]]:
        """Find any reference to a quantity in the content text."""
        for comparison in {
            **QuantityRange.opposite_comparisons,
            **QuantityRange.normalized_comparisons,
        }:
            if comparison in content:
                content, quantity_text = content.split(comparison)
                return content.rstrip(), comparison, quantity_text.lstrip()
        return content, "", None

    def normalize_comparison(self, data: RawPredicate, **kwargs) -> RawPredicate:
        """Reduce the number of possible symbols to represent comparisons."""
        if data.get("expression") and not data.get("sign"):
            data["sign"] = "="

        if data.get("sign") in QuantityRange.normalized_comparisons:
            data["sign"] = QuantityRange.normalized_comparisons[data["sign"]]
        return data

    @pre_load
    def format_data_to_load(self, data: RawPredicate, **kwargs) -> RawPredicate:
        """Expand any reference to a quantity in the content text."""
        if not data.get("expression"):
            (
                data["content"],
                data["sign"],
                data["expression"],
            ) = self.split_quantity_from_content(data["content"])
        data = self.normalize_comparison(data)
        return data

    @post_load
    def make_object(self, data, **kwargs):
        """Make AuthoritySpoke object out of whatever data has been loaded."""
        if data.get("expression") is not None:
            return Comparison(**data)
        data.pop("expression", None)
        data.pop("sign", None)
        return self.__model__(**data)


class EntitySchema(Schema):
    """Schema for Entities, which shouldn't be at the top level of a FactorGroup."""

    __model__: Type = Entity
    name = fields.Str(missing=None)
    generic = fields.Bool(missing=True)
    plural = fields.Bool()

    @post_load
    def make_object(self, data: Dict[str, Union[bool, str]], **kwargs) -> CaseCitation:
        return self.__model__(**data)


class FactSchema(Schema):
    """Schema for Facts, which may contain arbitrary levels of nesting."""

    __model__: Type = Fact
    predicate = fields.Nested(PredicateSchema)
    terms = fields.Nested(lambda: FactorSchema(many=True))
    standard_of_proof = fields.Str(missing=None)
    name = fields.Str(missing=None)
    absent = fields.Bool(missing=False)
    generic = fields.Bool(missing=False)

    @post_load
    def make_object(self, data: RawFactor, **kwargs) -> Fact:
        """Make Fact."""
        return self.__model__(**data)


class ExhibitSchema(Schema):
    """Schema for an object that may embody a statement."""

    __model__: Type = Exhibit
    form = fields.Str(missing=None)
    statement = fields.Nested(FactSchema, missing=None)
    statement_attribution = fields.Nested(EntitySchema, missing=None)
    name = fields.Str(missing=None)
    absent = fields.Bool(missing=False)
    generic = fields.Bool(missing=False)

    @post_load
    def make_object(self, data: RawFactor, **kwargs) -> Exhibit:
        """Make Exhibit."""
        return self.__model__(**data)


class PleadingSchema(Schema):
    """Schema for a document to link Allegations to."""

    __model__: Type = Pleading
    filer = fields.Nested(EntitySchema, missing=None)
    name = fields.Str(missing=None)
    absent = fields.Bool(missing=False)
    generic = fields.Bool(missing=False)


class AllegationSchema(Schema):
    """Schema for an Allegation of a Fact."""

    __model__: Type = Allegation
    pleading = fields.Nested(PleadingSchema, missing=None)
    statement = fields.Nested(FactSchema, missing=None)
    name = fields.Str(missing=None)
    absent = fields.Bool(missing=False)
    generic = fields.Bool(missing=False)


class EvidenceSchema(Schema):
    """Schema for an Exhibit and a reference to the Fact it would support."""

    __model__: Type = Evidence
    exhibit = fields.Nested(ExhibitSchema, missing=None)
    to_effect = fields.Nested(FactSchema, missing=None)
    name = fields.Str(missing=None)
    absent = fields.Bool(missing=False)
    generic = fields.Bool(missing=False)


class FactorSchema(OneOfSchema, Schema):
    """Schema that directs data to "one of" the other schemas."""

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

    def get_obj_type(self, obj) -> str:
        """Return name of object schema."""
        return obj.__class__.__name__


class ProcedureSchema(Schema):
    """
    Schema for Procedure; does not require separate TermSequence schema.

    "FactorSchema, many=True" is an equivalent of a TermSequence.
    """

    __model__: Type = Procedure
    inputs = fields.Nested(FactorSchema, many=True)
    despite = fields.Nested(FactorSchema, many=True)
    outputs = fields.Nested(FactorSchema, many=True)

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)


class RuleSchema(Schema):
    """Schema for Holding; can also hold Procedure fields."""

    __model__: Type = Rule
    procedure = fields.Nested(ProcedureSchema)
    enactments = fields.Nested(EnactmentSchema, many=True)
    enactments_despite = fields.Nested(EnactmentSchema, many=True)
    mandatory = fields.Bool(missing=False)
    universal = fields.Bool(missing=False)
    name = fields.Str(missing=None)
    generic = fields.Bool(missing=False)

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)


class HoldingSchema(Schema):
    """Schema for Holding; can also hold Rule and Procedure fields."""

    __model__: Type = Holding
    rule = fields.Nested(RuleSchema)
    rule_valid = fields.Bool(missing=True)
    decided = fields.Bool(missing=True)
    exclusive = fields.Bool(missing=False)
    generic = fields.Bool(missing=False)
    anchors = fields.Nested(SelectorSchema, many=True)

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)


class NamedAnchors(NamedTuple):
    name: Factor
    quotes: List[TextQuoteSelector]


class NamedAnchorsSchema(Schema):
    __model__ = NamedAnchors

    name = fields.Nested(FactorSchema)
    quotes = fields.Nested(SelectorSchema, many=True)


class AnchoredEnactments(NamedTuple):
    enactment: Enactment
    quotes: List[TextQuoteSelector]


class AnchoredEnactmentsSchema(Schema):
    __model__ = AnchoredEnactments

    enactment = fields.Nested(EnactmentSchema)
    quotes = fields.Nested(SelectorSchema, many=True)


SCHEMAS = list(Schema.__subclasses__()) + [SelectorSchema, EnactmentSchema]


def get_schema_for_item(classname: str) -> Schema:
    """Find the Marshmallow schema for an AuthoritySpoke object."""
    schemas_for_names = {
        "TextPositionSelector": SelectorSchema,
        "TextQuoteSelector": SelectorSchema,
        "Comparison": PredicateSchema,
        "Predicate": PredicateSchema,
        "Fact": FactSchema,
        "Evidence": EvidenceSchema,
        "Exhibit": ExhibitSchema,
        "Allegation": AllegationSchema,
        "Pleading": PleadingSchema,
        "Holding": HoldingSchema,
        "Rule": RuleSchema,
        "Procedure": ProcedureSchema,
        "Enactment": EnactmentSchema,
    }
    result = schemas_for_names.get(classname)
    if result is None:
        raise ValueError(f"No schema found for class '{classname}'")
    return result()
