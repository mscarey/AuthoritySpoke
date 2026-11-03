from authorityspoke.nettlesome.statements import Assertion


class TestSpec:
    def test_make_json_spec(self):
        schema = Assertion.model_json_schema()
        ref = schema["properties"]["statement"]["$ref"]
        ent_ref = schema["properties"]["authority"]["anyOf"][0]["$ref"]
        assert ref == "#/$defs/Statement"
        assert ent_ref == "#/$defs/Entity"
