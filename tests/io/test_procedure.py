from authorityspoke.procedures import Procedure

from authorityspoke.io import text_expansion, readers


class TestProcedureDump:
    def test_dump_procedure(self, make_procedure):
        procedure = make_procedure["c2"]
        dumped = procedure.dict()
        content = dumped["inputs"][0]["predicate"]["content"]
        assert content == "$thing was on the premises of $place"

    def test_dump_and_load_procedure(self, make_procedure):
        procedure = make_procedure["c2"]
        dumped = procedure.dict()
        loaded = Procedure(**dumped)
        content = loaded.despite[0].predicate.content
        assert "the distance between $place1 and $place2 was" in content


class TestProcedureLoad:
    example = {
        "inputs": {
            "type": "fact",
            "content": "{the Java API} was an original work",
            "truth": False,
        },
        "outputs": {
            "type": "fact",
            "content": "the Java API was copyrightable",
            "truth": False,
        },
    }

    def test_load_example(self):
        holdings = readers.read_holdings([self.example])
        factor = holdings[0].outputs[0].terms[0]
        assert factor.name == "the Java API"
