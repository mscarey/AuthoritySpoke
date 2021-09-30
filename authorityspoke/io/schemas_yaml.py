"""
Marshmallow schemas for loading AuthoritySpoke objects from YAML.

Intended for use with human-generated files.
Some shortened syntax is allowed.
"""

from copy import deepcopy
from datetime import date
from typing import Any, Dict, List, NamedTuple, Optional, Sequence, Tuple, Type, Union

from marshmallow import Schema, fields, validate, EXCLUDE
from marshmallow import pre_load, post_load
from pydantic import ValidationError

from anchorpoint.textselectors import TextQuoteSelector, TextPositionSet
from legislice.enactments import Enactment, EnactmentPassage, AnchoredEnactmentPassage

from nettlesome.entities import Entity
from nettlesome.factors import Factor
from nettlesome.predicates import Predicate
from nettlesome.quantities import Comparison, QuantityRange, Quantity


from authorityspoke.decisions import CAPCitation, Decision
from authorityspoke.evidence import Exhibit, Evidence

from authorityspoke.facts import Fact
from authorityspoke.holdings import Holding
from authorityspoke.io.enactment_index import EnactmentIndex
from authorityspoke.io.name_index import Mentioned
from authorityspoke.io.name_index import RawFactor, RawPredicate
from authorityspoke.io.nesting import nest_fields
from authorityspoke.io import text_expansion

from authorityspoke.opinions import AnchoredHoldings, HoldingWithAnchors
from authorityspoke.pleadings import Pleading, Allegation

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
            try:
                return deepcopy(mentioned.get_by_name(data))
            except ValueError:
                print(data)
        return data

    def consume_type_field(self, data, **kwargs):
        """Verify that type field is correct and then get rid of it."""
        if data.get("type"):
            data.pop("type")
        return data

    def wrap_single_element_in_list(self, data: Dict, many_element: str):
        """Make a specified field a list if it isn't already a list."""
        if data.get(many_element) is not None and not isinstance(
            data[many_element], list
        ):
            data[many_element] = [data[many_element]]
        return data

    def is_revision_date_known(self, data):
        r"""
        Determine if Enactment's start_date reflects its last revision date.
        If not, then the `start_date` merely reflects the earliest date that versions
        of the :class:`Enactment`\'s code exist in the database.
        """
        if not self.context.get("coverage"):
            data["known_revision_date"] = False
        elif self.context["coverage"]["earliest_in_db"] and (
            self.context["coverage"]["earliest_in_db"]
            < date.fromisoformat(data["start_date"])
        ):
            data["known_revision_date"] = True
        elif (
            self.context["coverage"]["earliest_in_db"]
            and self.context["coverage"]["first_published"]
            and (
                self.context["coverage"]["earliest_in_db"]
                <= self.context["coverage"]["first_published"]
            )
        ):
            data["known_revision_date"] = True
        else:
            data["known_revision_date"] = False
        return data

    def enactments_to_dicts(self, obj: Rule) -> List[Dict[str, Any]]:
        return [item.dict() for item in obj.enactments]

    def enactments_despite_to_dicts(self, obj: Rule) -> List[Dict[str, Any]]:
        return [item.dict() for item in obj.enactments_despite]

    def load_enactment(self, data: Dict[str, Any]) -> EnactmentPassage:
        if isinstance(data, str):
            mentioned = self.context.get("enactment_index") or EnactmentIndex()
            data = deepcopy(mentioned.get_by_name(data))
        data = self.is_revision_date_known(data)
        return EnactmentPassage(**data)

    def load_enactments(self, data: List[Dict[str, Any]]) -> List[EnactmentPassage]:
        """Load EnactmentPassage objects from data."""
        return [self.load_enactment(item) for item in data]

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
RawCAPCitation = Dict[str, str]
RawDecision = Dict[str, Union[str, int, Sequence[RawOpinion], Sequence[RawCAPCitation]]]


class AnchoredEnactmentPassageSchema(ExpandableSchema):
    """
    Schema to load Enactments from JSON created from user-created YAML.

        >>> enactment_data = {
        ...     "name": "original works",
        ...     "enactment": {
        ...     "node": "/us/usc/t17/s102",
        ...     "start_date": "1990-12-01",
        ...     "content": (
        ...         "Copyright protection subsists, in accordance with this title, "
        ...         "in original works of authorship fixed in any tangible medium of expression, "
        ...         "now known or later developed."),
        ...     },
        ...     "selection": [{"suffix": ", in accordance"}, "title,|in original works of authorship|fixed"]}
        >>> schema = EnactmentSchema()
        >>> enactment_index = EnactmentIndex()
        >>> enactment_index.insert_by_name(enactment_data)
        >>> schema.context["enactment_index"] = enactment_index
        >>> enactment = schema.load("original works")
        >>> enactment.selected_text()
        'Copyright protection subsists…in original works of authorship…'
    """

    __model__ = AnchoredEnactmentPassage
    passage = fields.Method(
        serialize="enactment_to_dict", deserialize="load_enactment", required=False
    )
    anchors = fields.Method(
        serialize="anchorset_to_dict", deserialize="load_anchorset", required=False
    )

    def load_anchorset(self, data: Dict[str, Any]) -> TextPositionSet:
        """Load EnactmentPassage objects from data."""
        return TextPositionSet(**data)

    def anchorset_to_dict(self, obj: AnchoredEnactmentPassage) -> Dict[str, Any]:
        return obj.anchors.dict()

    def enactment_to_dict(self, obj: AnchoredEnactmentPassage) -> Dict[str, Any]:
        return obj.passage.dict()

    def load_enactment(self, data: Dict[str, Any]) -> EnactmentPassage:
        if isinstance(data, str):
            mentioned = self.context.get("enactment_index") or EnactmentIndex()
            data = deepcopy(mentioned.get_by_name(data))
        data = self.is_revision_date_known(data)
        return EnactmentPassage(**data)

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)


class NamedAnchors(NamedTuple):
    name: Factor
    anchors: List[TextQuoteSelector]
