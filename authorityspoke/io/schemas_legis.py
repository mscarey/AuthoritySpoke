"""
Marshmallow schemas used for loading holding data.

These classes were previously imported from Legislice,
before Legislice switched to Pydantic for serialization.

This module should not be used to implement any new
features if Pydantic can be used instead.
"""
import datetime
from typing import Dict, List, Optional, Union

from legislice.enactments import (
    CrossReference,
    Enactment,
    EnactmentPassage,
    TextVersion,
    AnchoredEnactmentPassage,
)
from marshmallow import Schema, fields, pre_load, post_load, EXCLUDE

from authorityspoke.io.schemas_anchor import TextPositionSetSchema


class CrossReferenceSchema(Schema):
    """Schema for a reference to one Enactment in another Enactment's text."""

    __model__ = CrossReference

    target_uri = fields.Str(required=True)
    target_url = fields.Url(relative=False, required=True)
    reference_text = fields.Str(required=True)
    target_node = fields.Int(required=False)

    class Meta:
        unknown = EXCLUDE

    @post_load
    def make_object(self, data, **kwargs) -> CrossReference:
        r"""Make :class:`~legislice.enactments.CrossReference`\."""
        return self.__model__(**data)


class TextVersionSchema(Schema):
    """Schema for version of statute text."""

    __model__ = TextVersion
    content = fields.Str(required=True)

    class Meta:
        unknown = EXCLUDE

    @pre_load
    def format_data_to_load(
        self, data: Union[str, Dict[str, str]], **kwargs
    ) -> Dict[str, str]:
        """Get content field from nested "text_version" model."""
        if data and isinstance(data, str):
            data = {"content": data}
        return data

    @post_load
    def make_object(self, data, **kwargs):
        r"""Load data as a :class:`~legislice.enactments.TextVersion`\."""
        return self.__model__(**data)


class LinkedEnactmentSchema(Schema):
    """Schema for passages from legislation without the full text of child nodes."""

    __model__ = Enactment
    node = fields.Url(relative=True, required=True)
    heading = fields.Str(required=True)
    text_version = fields.Nested(TextVersionSchema, required=False, missing=None)
    start_date = fields.Date(required=True)
    end_date = fields.Date(missing=None)
    known_revision_date = fields.Boolean()
    citations = fields.Nested(CrossReferenceSchema, many=True, missing=list)
    children = fields.List(fields.Url(relative=False))

    class Meta:
        """Exclude unknown fields from schema."""

        unknown = EXCLUDE
        ordered = True

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
            < datetime.date.fromisoformat(data["start_date"])
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

    @pre_load
    def format_data_to_load(self, data, **kwargs):
        """Prepare Enactment to load."""
        data = self.is_revision_date_known(data)
        return data

    @post_load
    def make_object(self, data, **kwargs):
        """Make Linked Enactment, omitting any text selectors."""

        return self.__model__(**data)


class EnactmentSchema(LinkedEnactmentSchema):
    """Schema for passages from legislation without the full text of child nodes."""

    __model__: Enactment
    node = fields.Url(relative=True, required=True)
    heading = fields.Str(required=True)
    text_version = fields.Nested(TextVersionSchema, required=False, missing=None)
    start_date = fields.Date(required=True)
    end_date = fields.Date(missing=None)
    known_revision_date = fields.Boolean()
    citations = fields.Nested(CrossReferenceSchema, many=True, missing=list)
    children = fields.List(fields.Url(relative=False))

    class Meta:
        """Exclude unknown fields from schema."""

        unknown = EXCLUDE
        ordered = True

    def wrap_single_element_in_list(self, data: Dict, many_element: str):
        """Make a specified field a list if it isn't already a list."""
        if data.get(many_element) is None:
            data[many_element] = []
        elif not isinstance(data[many_element], list):
            data[many_element] = [data[many_element]]
        return data

    def nest_content_in_textversion(self, data):
        """Correct user-generated data omitting a layer of nesting."""
        if data.get("content"):
            if not data.get("text_version"):
                data["text_version"] = {}
            data["text_version"]["content"] = data["content"]
        data.pop("content", None)
        return data

    @pre_load
    def format_data_to_load(self, data, **kwargs):
        """Prepare Enactment to load."""
        data = self.nest_content_in_textversion(data)
        data = self.is_revision_date_known(data)
        return data

    @post_load
    def make_object(self, data, **kwargs):
        """Make Linked Enactment, omitting any text selectors."""
        if data.get("selection"):
            data["selection"] = [item for item in data["selection"] if item is not None]

        return self.__model__(**data)


class EnactmentPassageSchema(Schema):
    """Schema for passages from legislation."""

    __model__ = EnactmentPassage
    enactment = fields.Nested(EnactmentSchema)
    selection = fields.Nested(TextPositionSetSchema)

    class Meta:
        """Exclude unknown fields from schema."""

        unknown = EXCLUDE
        ordered = True

    @post_load
    def make_object(self, data, **kwargs):
        """Make EnactmentPassage, omitting any text selectors."""
        return self.__model__(**data)


class ExpandableLinkedEnactmentSchema(LinkedEnactmentSchema):
    """Schema for passages from legislation without the full text of child nodes."""

    __model__: Enactment
    node = fields.Url(relative=True, required=True)
    heading = fields.Str(required=True)
    text_version = fields.Nested(TextVersionSchema, required=False, missing=None)
    start_date = fields.Date(required=True)
    end_date = fields.Date(missing=None)
    known_revision_date = fields.Boolean()
    citations = fields.Nested(CrossReferenceSchema, many=True, missing=list)
    children = fields.List(fields.Url(relative=False))

    class Meta:
        """Exclude unknown fields from schema."""

        unknown = EXCLUDE
        ordered = True

    def wrap_single_element_in_list(self, data: Dict, many_element: str):
        """Make a specified field a list if it isn't already a list."""
        if data.get(many_element) is None:
            data[many_element] = []
        elif not isinstance(data[many_element], list):
            data[many_element] = [data[many_element]]
        return data

    def nest_content_in_textversion(self, data):
        """Correct user-generated data omitting a layer of nesting."""
        if data.get("content"):
            if not data.get("text_version"):
                data["text_version"] = {}
            data["text_version"]["content"] = data["content"]
        data.pop("content", None)
        return data

    @pre_load
    def format_data_to_load(self, data, **kwargs):
        """Prepare Enactment to load."""
        data = self.nest_content_in_textversion(data)
        data = self.wrap_single_element_in_list(data, "selection")
        data = self.wrap_single_element_in_list(data, "anchors")
        data = self.is_revision_date_known(data)
        return data

    @post_load
    def make_object(self, data, **kwargs):
        """Make Linked Enactment, omitting any text selectors."""
        if data.get("selection"):
            data["selection"] = [item for item in data["selection"] if item is not None]

        return self.__model__(**data)


class ExpandableEnactmentSchema(ExpandableLinkedEnactmentSchema):
    """Schema for passages from legislation."""

    __model__ = Enactment
    children = fields.List(fields.Nested(lambda: ExpandableEnactmentSchema()))
    heading = fields.Str(missing="")

    class Meta:
        """Exclude unknown fields from schema."""

        unknown = EXCLUDE
        ordered = True
