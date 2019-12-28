from authorityspoke.io import filepaths, loaders, readers


class TestFileLoad:
    def test_get_correct_filepath(self):
        directory = filepaths.get_directory_path("holdings")
        path = filepaths.make_filepath(
            filename="holding_feist.json", directory=directory
        )
        raw_holdings = loaders.load_holdings(filepath=path)
        assert raw_holdings[0]["outputs"]["type"] == "fact"


class TestLoadCode:
    def test_check_for_uslm_schema(self):
        code = loaders.load_code("beard_tax_act.xml")
        assert readers.has_uslm_schema(code)
