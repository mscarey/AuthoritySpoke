import os

from dotenv import load_dotenv
import pytest

from legislice.download import Client

from authorityspoke.io import loaders, readers
from authorityspoke.facts import Exhibit
from authorityspoke.rules import Rule

load_dotenv()

TOKEN = os.getenv("LEGISLICE_API_TOKEN")


class TestRuleDump:
    def test_dump_rule(self, make_rule):
        rule = make_rule["h2"]
        dumped = rule.model_dump()
        content = dumped["procedure"]["inputs"][0]["predicate"]["content"]
        assert content == "{thing} was on the premises of {place}"

    def test_dump_and_read_rule(self, make_procedure, e_search_clause):
        rule = Rule(procedure=make_procedure["c2"], enactments=e_search_clause)
        dumped = rule.model_dump()
        loaded = Rule(**dumped)
        content = loaded.despite[0].predicate.content
        assert "the distance between {place1} and {place2} was" in content
