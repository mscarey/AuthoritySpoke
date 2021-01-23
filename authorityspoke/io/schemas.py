"""Marshmallow schemas for loading AuthoritySpoke objects from JSON."""

from copy import deepcopy
from datetime import date
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, Union

from marshmallow import Schema, fields, validate, EXCLUDE
from marshmallow import pre_load, post_load
from marshmallow import ValidationError

from anchorpoint.textselectors import TextQuoteSelector, TextPositionSelector
from anchorpoint.schemas import SelectorSchema
from legislice import Enactment
from legislice.schemas import EnactmentSchema

from authorityspoke.decisions import CaseCitation, Decision
from authorityspoke.entities import Entity
from authorityspoke.evidence import Exhibit, Evidence
from authorityspoke.factors import Factor
from authorityspoke.facts import Fact
from authorityspoke.holdings import Holding
from authorityspoke.io.name_index import Mentioned
from authorityspoke.io.name_index import RawFactor, RawPredicate
from authorityspoke.io.nesting import nest_fields
from authorityspoke.io import text_expansion
from authorityspoke.opinions import Opinion
from authorityspoke.pleadings import Pleading, Allegation
from authorityspoke.predicates import Predicate, Comparison, ureg, Q_
from authorityspoke.procedures import Procedure
from authorityspoke.rules import Rule

from authorityspoke.utils.marshmallow_oneofschema.one_of_schema import OneOfSchema

RawSelector = Union[str, Dict[str, str]]
RawEnactment = Dict[str, Union[str, List[RawSelector]]]
RawProcedure = Dict[str, Sequence[RawFactor]]
RawRule = Dict[str, Union[RawProcedure, Sequence[RawEnactment], str, bool]]
RawHolding = Dict[str, Union[RawRule, str, bool]]


class ExpandableSchema(Schema):
    """Base schema for classes that can be cross-referenced by name in input JSON."""

    def get_from_mentioned(self, data, **kwargs):
        """Replace data to load with any object with same name in "mentioned"."""
        if isinstance(data, str):
            mentioned = self.context.get("mentioned") or Mentioned()
            return deepcopy(mentioned.get_by_name(data))
        return data

    def consume_type_field(self, data, **kwargs):
        """Verify that type field is correct and then get rid of it."""
        if data.get("type"):
            ty = data.pop("type").lower()
            if ty != self.__model__.__name__.lower():
                raise ValidationError(
                    f'type field "{ty} does not match model type {self.__model__}'
                )
        return data

    def wrap_single_element_in_list(self, data: Dict, many_element: str):
        """Make a specified field a list if it isn't already a list."""
        if data.get(many_element) is not None and not isinstance(
            data[many_element], list
        ):
            data[many_element] = [data[many_element]]
        return data

    @pre_load
    def format_data_to_load(self, data: RawFactor, **kwargs) -> RawFactor:
        """Expand data if it was just a name reference in the JSON input."""
        data = self.get_from_mentioned(data)
        data = self.consume_type_field(data)
        return data

    @post_load
    def make_object(self, data, **kwargs):
        """Make AuthoritySpoke object out of whatever data has been loaded."""
        if data.get("expression") is not None:
            return Comparison(**data)
        data.pop("expression", None)
        data.pop("sign", None)
        return self.__model__(**data)


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


class OpinionSchema(ExpandableSchema):
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


class DecisionSchema(ExpandableSchema):
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
    _id = fields.Int(data_key="id")
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


def dump_quantity(obj: Comparison) -> Optional[Union[date, float, int, str]]:
    """Convert quantity to string if it's a pint ureg.Quantity object."""
    if obj is None or obj.__dict__.get("expression") is None:
        return None
    if isinstance(obj.expression, date):
        return obj.expression.isoformat()
    if isinstance(obj.expression, (int, float)):
        return obj.expression
    return f"{obj.expression.magnitude} {obj.expression.units}"


class PredicateSchema(ExpandableSchema):
    """Schema for statements, separate from any claim about their truth or who asserts them."""

    __model__ = Predicate
    template = fields.Str(data_key="content", load_only=True)
    content = fields.Method(serialize="get_content_with_placeholders", dump_only=True)
    truth = fields.Bool(missing=True)
    sign = fields.Str(
        missing=None,
        validate=validate.OneOf([""] + list(Comparison.opposite_comparisons.keys())),
    )
    expression = fields.Function(
        dump_quantity, deserialize=Comparison.read_quantity, missing=None
    )

    def get_content_with_placeholders(self, obj) -> str:
        return obj.template.template

    def split_quantity_from_content(
        self, content: str
    ) -> Tuple[str, Optional[str], Optional[Union[ureg.Quantity, int, float]]]:
        """Find any reference to a quantity in the content text."""
        for comparison in {
            **Comparison.normalized_comparisons,
            **Comparison.opposite_comparisons,
        }:
            if comparison in content:
                content, quantity_text = content.split(comparison)
                return content.rstrip(), comparison, quantity_text.lstrip()
        return content, "", None

    def normalize_comparison(self, data: RawPredicate, **kwargs) -> RawPredicate:
        """Reduce the number of possible symbols to represent comparisons."""
        if data.get("expression") and not data.get("sign"):
            data["sign"] = "="

        if data.get("sign") in Comparison.normalized_comparisons:
            data["sign"] = Comparison.normalized_comparisons[data["sign"]]
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


class EntitySchema(ExpandableSchema):
    """Schema for Entities, which shouldn't be at the top level of a FactorGroup."""

    __model__: Type = Entity
    name = fields.Str(missing=None)
    generic = fields.Bool(missing=True)
    plural = fields.Bool()
    anchors = fields.Nested(SelectorSchema, many=True)


class FactSchema(ExpandableSchema):
    """Schema for Facts, which may contain arbitrary levels of nesting."""

    __model__: Type = Fact
    predicate = fields.Nested(PredicateSchema)
    terms = fields.Nested(lambda: FactorSchema(many=True))
    standard_of_proof = fields.Str(missing=None)
    name = fields.Str(missing=None)
    absent = fields.Bool(missing=False)
    generic = fields.Bool(missing=False)
    anchors = fields.Nested(SelectorSchema, many=True)

    def get_references_from_mentioned(
        self,
        content: str,
        terms: Optional[List[Dict]] = None,
        placeholder: str = "{}",
    ) -> Tuple[str, List[Dict]]:
        r"""
        Retrieve known context :class:`.Factor`\s for new :class:`.Fact`\.

        :param content:
            the content for the :class:`.Fact`\'s :class:`.Predicate`
        :param mentioned:
            list of :class:`.Factor`\s with names that could be
            referenced in content
        :param placeholder:
            a string to replace the names of
            referenced :class:`.Factor`\s in content
        :returns:
            the content string with any referenced :class:`.Factor`\s
            replaced by placeholder, and a list of referenced
            :class:`.Factor`\s in the order they appeared in content.
        """
        mentioned = self.context.get("mentioned") or Mentioned({})
        terms = terms or []
        for factor_name in mentioned.keys():
            if factor_name in content and factor_name != content:
                obj = mentioned.get_by_name(factor_name)
                content, terms = text_expansion.add_found_context(
                    content,
                    terms,
                    factor=deepcopy(obj),
                )
        return content, terms

    @pre_load
    def format_data_to_load(self, data: RawFactor, **kwargs) -> RawFactor:
        r"""
        Prepare :class:`.RawFact` to load, replacing name references with full objects.

        Unlike the :func:`.name_index.collect_mentioned` function, this function can't add
        any entries to the "mentioned" name index (due to limitations in the Marshmallow
        serialization library). That means all shorthand references to factors
        need to have been expanded before using the schema to load new objects.

        :param data:
            a dict representing a :class:`.Fact`

        :returns:
            a normalized dict representing a :class:`.Fact`\s with name references
            expanded
        """
        data = self.get_from_mentioned(data)
        to_nest = [
            "content",
            "truth",
            "sign",
            "expression",
        ]
        data = nest_fields(data, nest="predicate", eggs=to_nest)
        data = self.wrap_single_element_in_list(data, "terms")
        (
            data["predicate"]["content"],
            data["terms"],
        ) = self.get_references_from_mentioned(
            data["predicate"]["content"], data.get("terms")
        )
        data = self.consume_type_field(data)
        return data

    @post_load
    def make_object(self, data: RawFactor, **kwargs) -> Fact:
        """Make Fact."""
        return self.__model__(**data)


class ExhibitSchema(ExpandableSchema):
    """Schema for an object that may embody a statement."""

    __model__: Type = Exhibit
    form = fields.Str(missing=None)
    statement = fields.Nested(FactSchema, missing=None)
    statement_attribution = fields.Nested(EntitySchema, missing=None)
    name = fields.Str(missing=None)
    absent = fields.Bool(missing=False)
    generic = fields.Bool(missing=False)
    anchors = fields.Nested(SelectorSchema, many=True)

    @post_load
    def make_object(self, data: RawFactor, **kwargs) -> Exhibit:
        """Make Exhibit."""
        return self.__model__(**data)


class PleadingSchema(ExpandableSchema):
    """Schema for a document to link Allegations to."""

    __model__: Type = Pleading
    filer = fields.Nested(EntitySchema, missing=None)
    name = fields.Str(missing=None)
    absent = fields.Bool(missing=False)
    generic = fields.Bool(missing=False)
    anchors = fields.Nested(SelectorSchema, many=True)


class AllegationSchema(ExpandableSchema):
    """Schema for an Allegation of a Fact."""

    __model__: Type = Allegation
    pleading = fields.Nested(PleadingSchema, missing=None)
    statement = fields.Nested(FactSchema, missing=None)
    name = fields.Str(missing=None)
    absent = fields.Bool(missing=False)
    generic = fields.Bool(missing=False)
    anchors = fields.Nested(SelectorSchema, many=True)


class EvidenceSchema(ExpandableSchema):
    """Schema for an Exhibit and a reference to the Fact it would support."""

    __model__: Type = Evidence
    exhibit = fields.Nested(ExhibitSchema, missing=None)
    to_effect = fields.Nested(FactSchema, missing=None)
    name = fields.Str(missing=None)
    absent = fields.Bool(missing=False)
    generic = fields.Bool(missing=False)
    anchors = fields.Nested(SelectorSchema, many=True)


class FactorSchema(OneOfSchema, ExpandableSchema):
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

    def pre_load(self, data: RawFactor, **kwargs) -> RawFactor:
        data = self.get_from_mentioned(data)
        return data

    def get_obj_type(self, obj) -> str:
        """Return name of object schema."""
        return obj.__class__.__name__


class ProcedureSchema(ExpandableSchema):
    """
    Schema for Procedure; does not require separate FactorSequence schema.

    "FactorSchema, many=True" is an equivalent of a FactorSequence.
    """

    __model__: Type = Procedure
    inputs = fields.Nested(FactorSchema, many=True)
    despite = fields.Nested(FactorSchema, many=True)
    outputs = fields.Nested(FactorSchema, many=True)

    @pre_load
    def format_data_to_load(self, data, **kwargs):
        """Handle omission of brackets around single item."""
        for field_name in ("inputs", "despite", "outputs"):
            data = self.wrap_single_element_in_list(data, field_name)
        return data


class RuleSchema(ExpandableSchema):
    """Schema for Holding; can also hold Procedure fields."""

    __model__: Type = Rule
    procedure = fields.Nested(ProcedureSchema)
    enactments = fields.Nested(EnactmentSchema, many=True)
    enactments_despite = fields.Nested(EnactmentSchema, many=True)
    mandatory = fields.Bool(missing=False)
    universal = fields.Bool(missing=False)
    name = fields.Str(missing=None)
    generic = fields.Bool(missing=False)

    @pre_load
    def format_data_to_load(self, data: Dict, **kwargs) -> RawRule:
        """Prepare to load Rule."""
        data = self.wrap_single_element_in_list(data, "enactments")
        data = self.wrap_single_element_in_list(data, "enactments_despite")
        procedure_fields = ("inputs", "despite", "outputs")
        data["procedure"] = data.get("procedure") or {}
        for field in procedure_fields:
            if field in data:
                data["procedure"][field] = data.pop(field)
        return data

    @post_load
    def make_object(self, data, **kwargs):
        rule = self.__model__(**data)

        for enactment in rule.enactments:
            if not enactment.selected_text():
                enactment.select_all()
        for despite in rule.enactments_despite:
            if not despite.selected_text():
                despite.select_all()
        return rule


class HoldingSchema(ExpandableSchema):
    """Schema for Holding; can also hold Rule and Procedure fields."""

    __model__: Type = Holding
    rule = fields.Nested(RuleSchema)
    rule_valid = fields.Bool(missing=True)
    decided = fields.Bool(missing=True)
    exclusive = fields.Bool(missing=False)
    generic = fields.Bool(missing=False)
    anchors = fields.Nested(SelectorSchema, many=True)

    def nest_fields_inside_rule(self, data: Dict) -> RawHolding:
        """Nest fields inside "rule" and "procedure", if not already nested."""
        data["rule"]["procedure"] = data["rule"].get("procedure") or {}
        procedure_fields = ("inputs", "despite", "outputs")
        for field in procedure_fields:
            if field in data:
                data["rule"]["procedure"][field] = data.pop(field)
            if field in data["rule"]:
                data["rule"]["procedure"][field] = data["rule"].pop(field)

        return data

    @pre_load
    def format_data_to_load(self, data: RawHolding, **kwargs) -> RawHolding:
        """Prepare to load Holding."""
        data = self.get_from_mentioned(data)

        data["rule"] = data.get("rule") or {}
        to_nest = [
            "procedure",
            "enactments",
            "enactments_despite",
            "mandatory",
            "universal",
        ]
        data = nest_fields(data, nest="rule", eggs=to_nest)
        data = self.nest_fields_inside_rule(data)

        return data


SCHEMAS = list(ExpandableSchema.__subclasses__()) + [SelectorSchema, EnactmentSchema]


def get_schema_for_item(item: Any) -> Schema:
    """Find the Marshmallow schema for an AuthoritySpoke object."""
    if isinstance(item, TextPositionSelector):
        return SelectorSchema()
    if isinstance(item, Comparison):
        return PredicateSchema()
    for option in SCHEMAS:
        if item.__class__ == option.__model__:
            return option()
    raise ValueError(f"No schema found for class '{item.__class__}'")
