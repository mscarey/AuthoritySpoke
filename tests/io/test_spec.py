from authorityspoke.io.api_spec import spec

class TestSpec:
    def test_fact_in_spec(self):
        """
        Significant because Fact is a subclass of Factor,
        which is a OneOfSchema. It's difficult to document
        OneOf subschemas with apispec.
        """
        d = spec.to_dict()
        schemas = d['components']['schemas']
        assert "Fact" in schemas