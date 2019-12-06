import apispec

from authorityspoke.io.api_spec import spec


class TestSpec:
    def test_fact_in_spec(self):
        """
        Significant because Fact is a subclass of Factor,
        which is a OneOfSchema. It's difficult to document
        OneOf subschemas with apispec.
        """
        d = spec.to_dict()
        schemas = d["components"]["schemas"]
        assert "Fact" in schemas

    def test_factor_one_of(self):
        d = spec.to_dict()
        factor_schema = d["components"]["schemas"]["Factor"]
        assert "oneOf" in factor_schema

    def test_factor_schema_list(self):
        d = spec.to_dict()
        factor_schema_list = d["components"]["schemas"]["Factor"]["oneOf"]
        assert factor_schema_list[0]["$ref"].startswith("#/components/schemas/")

    def test_factor_type_discriminator(self):
        """
        Check for the field that determines which schema the
        Factor uses.
        """
        d = spec.to_dict()
        properties = d["components"]["schemas"]["Factor"]
        assert properties["discriminator"]["propertyName"] == "type"

    def test_validate_spec(self):
        """
        This function returns True if the spec validates against
        the OpenAPI standard.
        """
        assert apispec.utils.validate_spec(spec)
