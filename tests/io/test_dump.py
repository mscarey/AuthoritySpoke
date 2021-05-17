import pytest

from authorityspoke.io import dump
from authorityspoke.io.loaders import read_holdings_from_file
from authorityspoke.io.schemas_yaml import HoldingSchema


class TestDump:
    def test_try_to_dump_without_schema(self):
        with pytest.raises(ValueError):
            dump.to_json("not an AuthoritySpoke object")


class TestDumpYAMLSchema:
    def test_dump_holdings_with_comparison(self, fake_usc_client):

        holdings = read_holdings_from_file("holding_watt.yaml", client=fake_usc_client)
        assert "was no more than 35 foot" in str(holdings[1])
        schema = HoldingSchema()
        dumped = schema.dump(holdings[1])
        assert (
            dumped["rule"]["procedure"]["inputs"][3]["predicate"]["expression"]
            == "35 foot"
        )
