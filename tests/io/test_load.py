from authorityspoke.io import filepaths, loaders, readers
from authorityspoke.io.downloads import FakeClient
from authorityspoke.io.loaders import read_holdings_from_file


class TestFileLoad:
    def test_get_correct_filepath(self):
        directory = filepaths.get_directory_path("holdings")
        path = filepaths.make_filepath(
            filename="holding_feist.json", directory=directory
        )
        raw_holdings = loaders.load_holdings(filepath=path)
        assert raw_holdings[0]["outputs"]["type"] == "fact"


class TestLoadAndRead:
    def test_read_holdings_from_file(self):
        legis_client = FakeClient.from_file("usc.json")
        oracle_holdings = read_holdings_from_file(
            "holding_oracle.json", client=legis_client
        )
        assert oracle_holdings[0]
