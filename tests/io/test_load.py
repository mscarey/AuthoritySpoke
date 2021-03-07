from authorityspoke.io import filepaths, loaders, readers
from authorityspoke.io.downloads import FakeClient
from authorityspoke.io.loaders import load_and_read_holdings


class TestFileLoad:
    def test_get_correct_filepath(self):
        directory = filepaths.get_directory_path("holdings")
        path = filepaths.make_filepath(
            filename="holding_feist.json", directory=directory
        )
        raw_holdings = loaders.load_holdings(filepath=path)
        assert raw_holdings["holdings"][0]["outputs"]["type"] == "fact"


class TestLoadAndRead:
    def test_load_and_read_holdings(self):
        legis_client = FakeClient.from_file("usc.json")
        oracle_holdings = load_and_read_holdings(
            "holding_oracle.json", client=legis_client
        )
        assert oracle_holdings[0]
