from authorityspoke.procedures import Procedure

from authorityspoke.io import readers


class TestProcedureDump:
    def test_dump_procedure(self, make_procedure):
        procedure = make_procedure["c2"]
        dumped = procedure.model_dump()
        content = dumped["inputs"][0]["predicate"]["content"]
        assert content == "{thing} was on the premises of {place}"

    def test_dump_and_load_procedure(self, make_procedure):
        procedure = make_procedure["c2"]
        dumped = procedure.model_dump()
        loaded = Procedure(**dumped)
        content = loaded.despite[0].predicate.content
        assert "the distance between {place1} and {place2} was" in content
