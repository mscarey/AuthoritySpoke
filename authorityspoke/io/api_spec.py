from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

from authorityspoke.io.schemas import AllegationSchema, FactSchema
from authorityspoke.io.schemas import EvidenceSchema, HoldingSchema

spec = APISpec(
    title="AuthoritySpoke Holding API",
    version="0.1.0",
    openapi_version="3.0.2",
    info=dict(description="An interface for annotating judicial holdings"),
    plugins=[MarshmallowPlugin()],
)

spec.components.schema("Holding", schema=HoldingSchema)
spec.components.schema("Fact", schema=FactSchema)
spec.components.schema("Evidence", schema=EvidenceSchema)
spec.components.schema("Allegation", schema=AllegationSchema)
