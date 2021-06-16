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
from nettlesome.factors import Factor
from nettlesome.schemas import PredicateSchema, EntitySchema, RawFactor

from authorityspoke.decisions import CAPCitation, Decision
from authorityspoke.evidence import Exhibit, Evidence
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
    category = fields.Str(missing=None)
    reporter = fields.Str(missing=None)
    case_ids = fields.List(fields.Int(), allow_none=True)

    class Meta:
        unknown = EXCLUDE

    @post_load
    def make_object(self, data: RawCAPCitation, **kwargs) -> CAPCitation:
        """Load citation."""
        return self.__model__(**data)


class OpinionSchema(Schema):
    """
    Schema for Opinions, of which there may be several in one Decision.

        >>> data = {
        ...     "type": "dissent",
        ...     "author": "Ginsburg",
        ...     "text": "I respectfully dissent."}
        >>> schema = OpinionSchema()
        >>> opinion = schema.load(data)
        >>> opinion.position
        'dissent'
    """

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
    """
    Schema for decisions retrieved from Caselaw Access Project API.

        >>> data = {
        ...     "id": 12083986,
        ...     "url": "https://api.case.law/v1/cases/12083986/",
        ...     "name": "Bellingham executors v. Smith",
        ...     "name_abbreviation": "Bellingham v. Smith",
        ...     "decision_date": "1673-04-29",
        ...     "docket_number": "",
        ...     "first_page": "248",
        ...     "last_page": "248",
        ...     "citations": [
        ...         {
        ...             "type": "official",
        ...             "cite": "1 Rec. Co. Ct. 248"
        ...         }
        ...     ],
        ...     "volume": {
        ...         "url": "https://api.case.law/v1/volumes/32044031754302/",
        ...         "volume_number": "1",
        ...         "barcode": "32044031754302"
        ...     },
        ...     "reporter": {
        ...         "url": "https://api.case.law/v1/reporters/742/",
        ...         "full_name": "Records of the Suffolk county court, 1671-1680",
        ...         "id": 742
        ...     },
        ...     "court": {
        ...         "url": "https://api.case.law/v1/courts/suffolk-cty-ct-2/",
        ...         "name_abbreviation": "Suffolk Cty. Ct.",
        ...         "slug": "suffolk-cty-ct-2",
        ...         "id": 11154,
        ...         "name": "Suffolk County Court"
        ...     },
        ...     "jurisdiction": {
        ...         "id": 4,
        ...         "name_long": "Massachusetts",
        ...         "url": "https://api.case.law/v1/jurisdictions/mass/",
        ...         "slug": "mass",
        ...         "whitelisted": False,
        ...         "name": "Mass."
        ...     },
        ...     "cites_to": [],
        ... }
        >>> schema = DecisionSchema()
        >>> decision = schema.load(data)
        >>> decision.jurisdiction
        'Mass.'
        >>> decision.date.year
        1673
        >>> decision.citations[0].cite
        '1 Rec. Co. Ct. 248'
    """

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
            data["jurisdiction"] = data.get("jurisdiction", {}).get("name", "")
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
    """
    Schema for Facts, which may contain arbitrary levels of nesting.

        >>> lotus_entity = {"type": "Entity", "name": "Lotus Development Corporation"}
        >>> menu_entity = {"type": "Entity", "name": "the Lotus menu command hierarchy"}
        >>> fact_data = {
        ...             "predicate": {
        ...                 "content": "$owner registered a copyright covering $work"},
        ...             "terms": [lotus_entity, menu_entity]
        ...         }
        >>> schema = FactSchema()
        >>> fact = schema.load(fact_data)
        >>> str(fact)
        'the fact that <Lotus Development Corporation> registered a copyright covering <the Lotus menu command hierarchy>'
    """

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
    """
    Schema for an object that may embody a statement.

        >>> lotus_entity = {"type": "Entity", "name": "Lotus Development Corporation"}
        >>> fact_data = {
        ...    "predicate": {
        ...    "content": "$owner registered a copyright covering $work"},
        ...    "terms": [lotus_entity, {"type": "Entity", "name": "the Lotus menu command hierarchy"}]
        ...         }
        >>> exhibit_data = {
        ...     "form": "certificate of copyright registration",
        ...     "statement": fact_data,
        ...     "statement_attribution": {"name": "Lotus Development Corporation"}
        ...     }
        >>> schema = ExhibitSchema()
        >>> exhibit = schema.load(exhibit_data)
        >>> print(exhibit)
        the certificate of copyright registration attributed to <Lotus Development Corporation>, asserting the fact that <Lotus Development Corporation> registered a copyright covering <the Lotus menu command hierarchy>,
    """

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
    """
    Schema for a document to link Allegations to.

    >>> lotus_entity = {"name": "Lotus Development Corporation"}
    >>> pleading_data = {"filer": lotus_entity, "generic": False}
    >>> schema = PleadingSchema()
    >>> pleading = schema.load(pleading_data)
    >>> str(pleading)
    'the pleading filed by <Lotus Development Corporation>'
    """

    __model__: Type = Pleading
    filer = fields.Nested(EntitySchema, missing=None)
    name = fields.Str(missing=None)
    absent = fields.Bool(missing=False)
    generic = fields.Bool(missing=False)

    @post_load
    def make_pleading(self, data: RawFactor, **kwargs) -> Pleading:
        return self.__model__(**data)


class AllegationSchema(Schema):
    """Schema for an Allegation of a Fact."""

    __model__: Type = Allegation
    pleading = fields.Nested(PleadingSchema, missing=None)
    statement = fields.Nested(FactSchema, missing=None)
    name = fields.Str(missing=None)
    absent = fields.Bool(missing=False)
    generic = fields.Bool(missing=False)

    @post_load
    def make_allegation(self, data: RawFactor, **kwargs) -> Allegation:
        return self.__model__(**data)


class EvidenceSchema(Schema):
    """
    Schema for an Exhibit and a reference to the Fact it would support.

        >>> lotus_entity = {"type": "Entity", "name": "Lotus Development Corporation"}
        >>> menu_entity = {"type": "Entity", "name": "the Lotus menu command hierarchy"}
        >>> fact_data = {
        ...     "predicate": {
        ...     "content": "$owner registered a copyright covering $work"},
        ...     "terms": [lotus_entity, menu_entity]
        ...     }
        >>> exhibit_data = {
        ...     "form": "certificate of copyright registration",
        ...     "statement": fact_data,
        ...     "statement_attribution": {"name": "Lotus Development Corporation"}
        ...     }
        >>> evidence_data = {
        ...     "exhibit": exhibit_data,
        ...     "to_effect": {
        ...         "predicate": {"content": "$work was copyrightable"},
        ...         "terms": [menu_entity]}
        ... }
        >>> schema = EvidenceSchema()
        >>> evidence = schema.load(evidence_data)
        >>> print(evidence)
        the evidence of the certificate of copyright registration attributed to <Lotus Development Corporation>, asserting the fact that <Lotus Development Corporation> registered a copyright covering <the Lotus menu command hierarchy>, which supports the fact that <the Lotus menu command hierarchy> was copyrightable
    """

    __model__: Type = Evidence
    exhibit = fields.Nested(ExhibitSchema, missing=None)
    to_effect = fields.Nested(FactSchema, missing=None)
    name = fields.Str(missing=None)
    absent = fields.Bool(missing=False)
    generic = fields.Bool(missing=False)

    @post_load
    def make_evidence(self, data: RawFactor, **kwargs) -> Evidence:
        return self.__model__(**data)


class FactorSchema(OneOfSchema):
    """
    Schema that directs data to "one of" the other schemas.

    Must include a `type` field to indicate which subclass schema to use.

        >>> lotus_entity = {"type": "Entity", "name": "Lotus Development Corporation"}
        >>> menu_entity = {"type": "Entity", "name": "the Lotus menu command hierarchy"}
        >>> fact_data = {
        ...             "type": "Fact",
        ...             "predicate": {
        ...                 "content": "$owner registered a copyright covering $work"},
        ...             "terms": [lotus_entity, menu_entity]
        ...         }
        >>> schema = FactorSchema()
        >>> fact = schema.load(fact_data)
        >>> str(fact)
        'the fact that <Lotus Development Corporation> registered a copyright covering <the Lotus menu command hierarchy>'
    """

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
    Schema for loading a Procedure from data fitting an OpenAPI schema.

    Does not require separate :class:`~authorityspoke.facts.TermSequence` schema.
    :class:`~FactorSchema` will load the equivalent of
    a :class:`~nettlesome.facts.TermSequence` with the parameter ``many=True``.

        >>> api_data = {"type": "Entity", "name": "the Java API"}
        >>> procedure_data = {
        ... "inputs": [{
        ...     "type": "Fact",
        ...     "predicate": {"content": "$work was an original work",
        ...     "truth": False},
        ...     "terms": [api_data]}],
        ... "outputs": [{
        ...     "type": "Fact",
        ...     "predicate": {"content": "$work was copyrightable",
        ...     "truth": False},
        ...     "terms": [api_data]}]}
        >>> schema = ProcedureSchema()
        >>> procedure = schema.load(procedure_data)
        >>> procedure.short_string
        'RESULT: the fact it was false that <the Java API> was copyrightable GIVEN: the fact it was false that <the Java API> was an original work'
    """

    __model__: Type = Procedure
    inputs = fields.Nested(FactorSchema, many=True)
    despite = fields.Nested(FactorSchema, many=True)
    outputs = fields.Nested(FactorSchema, many=True)

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)


class RuleSchema(Schema):
    """
    Schema for loading Rules from data fitting an OpenAPI schema.

    >>> api_data = {"type": "Entity", "name": "the Java API"}
    >>> procedure_data = {
    ... "inputs": [{
    ...     "type": "Fact",
    ...     "predicate": {"content": "$work was an original work",
    ...     "truth": False},
    ...     "terms": [api_data]}],
    ... "outputs": [{
    ...     "type": "Fact",
    ...     "predicate": {"content": "$work was copyrightable",
    ...     "truth": False},
    ...     "terms": [api_data]}]}
    >>> rule_data = {"procedure": procedure_data,
    ...     "mandatory": True,
    ...     "enactments": [{
    ...         "node": "/us/usc/t17/s102",
    ...         "start_date": "1990-12-01",
    ...         "text_version": {
    ...         "content": "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed."},
    ...         "selection": [{"start": 0, "end": 93}]}]}
    >>> schema = RuleSchema()
    >>> rule = schema.load(rule_data)
    >>> print(rule.short_string)
    the Rule that the court MUST SOMETIMES impose the RESULT: the fact it was false that <the Java API> was copyrightable GIVEN: the fact it was false that <the Java API> was an original work GIVEN the ENACTMENT: "Copyright protection subsists, in accordance with this title, in original works of authorship…" (/us/usc/t17/s102 1990-12-01)
    """

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
    """
    Schema for loading Holdings from data fitting an OpenAPI schema.

    >>> api_data = {"type": "Entity", "name": "the Java API"}
    >>> procedure_data = {
    ... "inputs": [{
    ...     "type": "Fact",
    ...     "predicate": {"content": "$work was an original work",
    ...     "truth": False},
    ...     "terms": [api_data]}],
    ... "outputs": [{
    ...     "type": "Fact",
    ...     "predicate": {"content": "$work was copyrightable",
    ...     "truth": False},
    ...     "terms": [api_data]}]}
    >>> rule_data = {"procedure": procedure_data,
    ...     "mandatory": True,
    ...     "enactments": [{
    ...         "node": "/us/usc/t17/s102",
    ...         "start_date": "1990-12-01",
    ...         "text_version": {
    ...         "content": "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed."},
    ...         "selection": [{"start": 0, "end": 93}]}]}
    >>> holding_data = {
    ...     "rule": rule_data,
    ...     "rule_valid": False}
    >>> schema = HoldingSchema()
    >>> holding = schema.load(holding_data)
    >>> print(holding.short_string)
    the Holding to REJECT the Rule that the court MUST SOMETIMES impose the RESULT: the fact it was false that <the Java API> was copyrightable GIVEN: the fact it was false that <the Java API> was an original work GIVEN the ENACTMENT: "Copyright protection subsists, in accordance with this title, in original works of authorship…" (/us/usc/t17/s102 1990-12-01)
    """

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
    anchors: List[TextQuoteSelector]


class NamedAnchorsSchema(Schema):
    __model__ = NamedAnchors

    name = fields.Nested(FactorSchema)
    anchors = fields.Nested(SelectorSchema, many=True)


class AnchoredEnactments(NamedTuple):
    enactment: Enactment
    anchors: List[TextQuoteSelector]


class AnchoredEnactmentsSchema(Schema):
    __model__ = AnchoredEnactments

    enactment = fields.Nested(EnactmentSchema)
    anchors = fields.Nested(SelectorSchema, many=True)


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
        "Decision": DecisionSchema,
        "Opinion": OpinionSchema,
    }
    result = schemas_for_names.get(classname)
    if result is None:
        raise ValueError(f"No schema found for class '{classname}'")
    return result()
