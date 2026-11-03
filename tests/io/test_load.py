import os


from authorityspoke import LegisClient
from authorityspoke.io import filepaths, loaders


LEGISLICE_API_TOKEN = os.getenv("LEGISLICE_API_TOKEN")


class TestHoldingLoad:
    client = LegisClient(api_token=LEGISLICE_API_TOKEN)

    def test_get_json_filepath(self):
        directory = filepaths.get_directory_path("holdings")
        path = filepaths.make_filepath(
            filename="holding_feist.yaml", directory=directory
        )
        raw_holdings = loaders.load_holdings(filepath=path)
        assert raw_holdings[0]["outputs"]["type"] == "fact"

    def test_get_yaml_filepath(self):
        directory = filepaths.get_directory_path("holdings")
        path = filepaths.make_filepath(
            filename="holding_feist.yaml", directory=directory
        )
        raw_holdings = loaders.load_holdings(filepath=path)
        assert raw_holdings[0]["outputs"]["type"] == "fact"
