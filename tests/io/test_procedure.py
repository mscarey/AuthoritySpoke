from authorityspoke.io import dump
from authorityspoke.io import readers, schemas


class TestProcedureDump:
    def test_dump_procedure(self, make_procedure):
        procedure = make_procedure["c2"]
        dumped = dump.to_dict(procedure)
        content = dumped["inputs"][0]["predicate"]["content"]
        assert content == "{} was on the premises of {}"

    def test_dump_and_load_procedure(self, make_procedure):
        procedure = make_procedure["c2"]
        dumped = dump.to_dict(procedure)
        schema = schemas.ProcedureSchema()
        loaded = schema.load(dumped)
        content = loaded.despite[0].predicate.content
        assert "the distance between {} and {} was" in content


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
        procedure = readers.read_procedure(self.example)
        factor = procedure.outputs[0].context_factors[0]
        assert factor.name == "the Java API"
