from datetime import date
import os

from dotenv import load_dotenv

import pytest

from legislice.yaml_schemas import EnactmentSchema
from authorityspoke.io.enactment_index import EnactmentIndex, collect_enactments

load_dotenv()

TOKEN = os.getenv("LEGISLICE_API_TOKEN")


class TestIndexEnactments:
    def test_index_section_with_name(self, section6d):
        mentioned = EnactmentIndex()
        section6d["name"] = "section6d"
        mentioned.index_enactment(section6d)
        assert mentioned["section6d"]["start_date"] == "1935-04-01"
        assert "EnactmentIndex({'section6d" in str(mentioned)

    def test_index_key_error(self, section6d):
        mentioned = EnactmentIndex()
        section6d["name"] = "section6d"
        mentioned.index_enactment(section6d)
        with pytest.raises(KeyError):
            mentioned.get_by_name("not in index")


class TestCollectEnactments:
    """Tests for finding and collecting Enactment records from a nested dict."""

    example_rules = [
        {
            "inputs": [
                {"type": "fact", "content": "{the suspected beard} was facial hair"},
                {
                    "type": "fact",
                    "content": "the length of the suspected beard was >= 5 millimetres",
                },
                {
                    "type": "fact",
                    "content": "the suspected beard occurred on or below the chin",
                },
            ],
            "outputs": [
                {
                    "type": "fact",
                    "content": "the suspected beard was a beard",
                    "name": "the fact that the facial hair was a beard",
                }
            ],
            "enactments": [
                {
                    "name": "beard means",
                    "enactment": {
                        "node": "/test/acts/47/4",
                        "exact": "In this Act, beard means any facial hair no shorter than 5 millimetres in length that:",
                    },
                },
                {"enactment": {"node": "/test/acts/47/4/a", "suffix": ", or"}},
                {
                    "name": "ear rule",
                    "enactment": {
                        "node": "/test/acts/47/4/b",
                        "anchors": [{"start": 10, "end": 20}, {"start": 40, "end": 50}],
                    },
                },
            ],
            "universal": True,
        },
        {
            "inputs": [
                {"type": "fact", "content": "{the suspected beard} was facial hair"},
                {
                    "type": "fact",
                    "content": "the length of the suspected beard was >= 5 millimetres",
                },
                {
                    "type": "fact",
                    "content": "the suspected beard existed in an uninterrupted line from the front of one ear to the front of the other ear below the nose",
                },
            ],
            "outputs": [
                {
                    "type": "fact",
                    "content": "the suspected beard was a beard",
                    "name": "the fact that the facial hair was a beard",
                }
            ],
            "enactments": [
                "beard means",
                {"passage": "ear rule", "anchors": [{"start": 100, "end": 150}]},
            ],
            "universal": True,
        },
    ]

    def test_collect_enactments_from_list(
        self, section6d, section_11_subdivided, fifth_a
    ):
        data = {
            "enactments": [
                {"name": "s11", "enactment": section_11_subdivided},
                {"name": "6d", "enactment": section6d},
                {"name": "5a", "enactment": fifth_a},
            ]
        }
        obj, mentioned = collect_enactments(data)
        assert mentioned["s11"]["enactment"]["node"] == "/test/acts/47/11"

    def test_collect_enactments_from_dict(self):
        obj, mentioned = collect_enactments(self.example_rules)
        assert mentioned["beard means"]["enactment"]["node"] == "/test/acts/47/4"

    def test_add_two_enactment_indexes(self):
        """
        Test that adding another EnactmentIndex puts its anchors in the first EnactmentIndex.
        The anchors won't be merged yet because the Enactment hasn't been loaded by the serializer.
        """
        obj, enactment_index = collect_enactments(self.example_rules)

        more_enactments = EnactmentIndex(
            {
                "ear rule": {
                    "node": "/test/acts/47/4/b",
                    "anchors": [{"start": 15, "end": 45}],
                }
            }
        )
        new_index = enactment_index + more_enactments
        assert {"start": 15, "end": 45} in new_index["ear rule"]["anchors"]

    def test_replace_enactment_in_source_with_name(self):
        example_rules, mentioned = collect_enactments(self.example_rules)
        assert example_rules[0]["enactments"][0] == "beard means"
        assert example_rules[0]["enactments"][1] == '/test/acts/47/4/a:suffix=", or"'

    @pytest.mark.xfail(
        reason="Text anchors for one passage no longer consolidated in one place."
    )
    def test_collect_enactment_anchors_from_dict(self):
        """Anchors for this Enactment are collected in two different places."""
        example_rules, mentioned = collect_enactments(self.example_rules)
        assert mentioned["ear rule"]["enactment"]["anchors"][0]["start"] == 10
        assert mentioned["ear rule"]["enactment"]["anchors"][2]["start"] == 100

    @pytest.mark.vcr
    def test_update_unloaded_enactment_from_api(self, test_client):
        example_rules, mentioned = collect_enactments(self.example_rules)
        updated = test_client.update_enactment_from_api(
            mentioned["ear rule"]["enactment"]
        )
        assert updated["node"] == "/test/acts/47/4/b"
        assert updated["anchors"][0]["start"] == 10
        assert updated["text_version"]["content"].startswith(
            "exists in an uninterrupted"
        )
        assert updated["start_date"] == "1935-04-01"

    @pytest.mark.vcr
    def test_load_updated_enactment_data(self, test_client):
        example_rules, mentioned = collect_enactments(self.example_rules)
        updated = test_client.update_enactment_from_api(mentioned["ear rule"])
        schema = EnactmentSchema()
        enactment = schema.load(updated)
        assert enactment.start_date == date(1935, 4, 1)
        assert enactment.content.startswith("exists in an uninterrupted")
        assert enactment.anchors[2].start == 100

    def test_retrieve_enactment_by_name(self, section6d, section_11_subdivided):
        obj, indexed = collect_enactments([section6d, section_11_subdivided])
        schema = EnactmentSchema(many=True)
        schema.context["enactment_index"] = indexed
        enactments = schema.load(obj)
        assert enactments[0].start_date.isoformat() == "1935-04-01"
