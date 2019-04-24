import json

from authorityspoke.opinions import Opinion

class TestDownload:
    def test_download_opinion_by_id(self, tmp_path):
        to_file = "oracle_h.json"
        Opinion.cap_download(cap_id=4066790, filename=to_file, directory=tmp_path)
        new_file = tmp_path / to_file
        with open(new_file, "r") as read_file:
            case = json.load(read_file)
        assert case["name_abbreviation"] == "Oracle America, Inc. v. Google Inc."
