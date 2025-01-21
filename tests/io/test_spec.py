from authorityspoke.holdings import Holding


class TestSpec:
    def test_fact_in_spec(self):
        spec = Holding.model_json_schema()
        assert "Fact" in spec["$defs"]

    def test_factor_one_of(self):
        spec = Holding.model_json_schema()
        factor_schema = spec["$defs"]["Procedure"]["properties"]["outputs"]
        assert "anyOf" in factor_schema["items"]
