"""Function for generating specification from Marshmallow schemas."""

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

from authorityspoke.io.schemas import AllegationSchema, FactSchema
from authorityspoke.io.schemas import EvidenceSchema, HoldingSchema


def make_spec() -> APISpec:
    """Generate specification for data used to create AuthoritySpoke objects."""
    holding_spec = APISpec(
        title="AuthoritySpoke Holding API Schema",
        version="0.1.0",
        openapi_version="3.0.2",
        info=dict(description="An interface for annotating judicial holdings"),
        plugins=[MarshmallowPlugin()],
    )

    holding_spec.components.schema("Holding", schema=HoldingSchema)
    holding_spec.components.schema("Fact", schema=FactSchema)
    holding_spec.components.schema("Evidence", schema=EvidenceSchema)
    holding_spec.components.schema("Allegation", schema=AllegationSchema)

    factor_names = ["Fact", "Exhibit", "Evidence", "Pleading", "Allegation"]
    factor_options = []

    for factor_name in factor_names:
        factor_options.append({"$ref": f"#/components/schemas/{factor_name}"})

    del holding_spec.components._schemas["Factor"]

    holding_spec.components.schema(
        "Factor",
        {
            "oneOf": factor_options,
            "discriminator": {"propertyName": "type"},
        },
    )
    return holding_spec


# spec = make_spec()
