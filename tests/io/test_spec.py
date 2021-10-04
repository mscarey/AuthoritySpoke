import apispec

from authorityspoke.holdings import Holding


class TestSpec:
    def test_fact_in_spec(self):
        spec = Holding.schema()
        assert "Fact" in spec["definitions"]

    def test_factor_one_of(self):
        spec = Holding.schema()
        factor_schema = spec["definitions"]["Procedure"]["properties"]["outputs"]
        assert "anyOf" in factor_schema["items"]
