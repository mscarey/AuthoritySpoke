"""Function for generating specification from Marshmallow schemas."""

from apispec import APISpec
from apispec_oneofschema import MarshmallowPlugin

from authorityspoke.io.schemas_json import HoldingSchema


def make_spec() -> APISpec:
    """Generate specification for data used to create AuthoritySpoke objects."""
    holding_spec = APISpec(
        title="AuthoritySpoke Holding API Schema",
        version="0.3.0",
        openapi_version="3.0.2",
        info=dict(description="An interface for annotating judicial holdings"),
        plugins=[MarshmallowPlugin()],
    )

    holding_spec.components.schema("Holding", schema=HoldingSchema)

    return holding_spec


# spec = make_spec()
