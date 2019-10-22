import pytest

from authorityspoke.io import dump


class TestDump:
    def test_try_to_dump_without_schema(self):
        with pytest.raises(ValueError):
            dump.to_json("not an AuthoritySpoke object")
