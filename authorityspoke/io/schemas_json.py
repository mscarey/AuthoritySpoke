"""
Marshmallow schemas for loading AuthoritySpoke objects from JSON.

Intended for use with machine-generated API responses.
Should be suitable for generating an OpenAPI specification.
"""

from typing import Dict, List, NamedTuple, Optional, Sequence, TypedDict, Type, Union

from marshmallow import Schema, fields, EXCLUDE
from marshmallow import pre_load, post_load
from marshmallow_oneofschema import OneOfSchema

from anchorpoint.textselectors import TextQuoteSelector, TextPositionSelector
from anchorpoint.schemas import SelectorSchema
from legislice import Enactment
from legislice.schemas import EnactmentSchema
from nettlesome.schemas import PredicateSchema, EntitySchema, RawFactor

from authorityspoke.decisions import CAPCitation, Decision
from authorityspoke.evidence import Exhibit, Evidence
from nettlesome.factors import Factor
from authorityspoke.facts import Fact
from authorityspoke.holdings import Holding
from authorityspoke.opinions import Opinion
from authorityspoke.pleadings import Pleading, Allegation
from authorityspoke.procedures import Procedure
from authorityspoke.rules import Rule

RawSelector = Union[str, Dict[str, str]]
RawEnactment = Dict[str, Union[str, List[RawSelector]]]
RawProcedure = Dict[str, Sequence[RawFactor]]
RawRule = Dict[str, Union[RawProcedure, Sequence[RawEnactment], str, bool]]
RawHolding = Dict[str, Union[RawRule, str, bool]]


RawOpinion = Dict[str, str]
RawCAPCitation = Dict[str, str]
RawDecision = Dict[str, Union[str, int, Sequence[RawOpinion], Sequence[RawCAPCitation]]]


class CAPCitationSchema(Schema):
    """Schema for Decision citations in CAP API response."""

    __model__ = CAPCitation
    cite = fields.Str()
    reporter = fields.Str(data_key="type", missing=None)
    case_ids = fields.List(fields.Int(), allow_none=True)

    @post_load
    def make_object(self, data: RawCAPCitation, **kwargs) -> CAPCitation:
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
        author = data.get("author") or ""
        data["author"] = author.strip(",:")
        return data

    @post_load
    def make_object(self, data: RawOpinion, **kwargs) -> CAPCitation:
        return self.__model__(**data)


class DecisionSchema(Schema):
    """Schema for decisions retrieved from Caselaw Access Project API."""

    __model__ = Decision
    name = fields.Str()
    name_abbreviation = fields.Str(missing=None)
    citations = fields.Nested(CAPCitationSchema, many=True)
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
    cites_to = fields.Nested(CAPCitationSchema, many=True, missing=list)

    class Meta:
        unknown = EXCLUDE

    @pre_load
    def format_data_to_load(self, data: RawDecision, **kwargs) -> RawDecision:
        """Transform data from CAP API response for loading."""
        if not isinstance(data["court"], str):
            data["court"] = data.get("court", {}).get("slug", "")
        if not isinstance(data["jurisdiction"], str):
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

        # change month to ISO date
        if data.get("decision_date") and data["decision_date"].count("-") == 1:
            data["decision_date"] += "-01"
        return data

    @post_load
    def make_object(self, data, **kwargs):
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


class FactorSchema(OneOfSchema):
    """Schema that directs data to "one of" the other schemas."""

    __model__: Type = Factor
    type_schemas = {
        "Allegation": AllegationSchema,
        "Entity": EntitySchema,
        "Evidence": EvidenceSchema,
        "Exhibit": ExhibitSchema,
        "Fact": FactSchema,
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
