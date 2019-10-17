from authorityspoke.io import anchors, dump, schemas


class TestLoadSelector:
    def test_get_schema_for_selector(self):
        data = {"text": "process, system,|method of operation|, concept, principle"}
        selector = anchors.read_selector(data)
        schema = schemas.get_schema_for_item(selector)
        assert isinstance(schema, schemas.SelectorSchema)


class TestDumpSelector:
    def test_dump_selector(self):
        """
        Uses text from "path": "/us/usc/t17/s102/b", but
        no longer includes a reference to the path.
        """

        data = {"text": "process, system,|method of operation|, concept, principle"}
        selector = anchors.read_selector(data)
        selector_dict = dump.to_dict(selector)
        assert isinstance(selector_dict, dict)
        assert selector_dict["prefix"].startswith("process, system")

    def test_string_dump_selector(self):
        data = {"text": "process, system,|method of operation|, concept, principle"}
        selector = anchors.read_selector(data)
        selector_str = dump.to_json(selector)
        assert isinstance(selector_str, str)
        assert '"prefix": "process, system' in selector_str

    def test_round_trip_dict(self):
        data = {"exact": "method of operation"}
        selector = anchors.read_selector(data)
        selector_dict = dump.to_dict(selector)
        new = anchors.read_selector(selector_dict)
        assert new.prefix is None
        assert new.exact == "method of operation"
