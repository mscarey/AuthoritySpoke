import json

import pytest

from authorityspoke.io.downloads import download_case
from authorityspoke.io.readers import opinion_from_case

pytestmark = pytest.mark.skip("don't want to call API")


class TestDownload:
    def test_download_case_by_id(self, tmp_path):
        to_file = "oracle_h.json"
        download_case(cap_id=4066790, filename=to_file, directory=tmp_path)
        new_file = tmp_path / to_file
        with open(new_file, "r") as read_file:
            case = json.load(read_file)
        assert case["name_abbreviation"] == "Oracle America, Inc. v. Google Inc."

    def test_download_case_by_cite(self, tmp_path):
        to_file = "lotus_h.json"
        download_case(cite="49 F.3d 807", filename=to_file, directory=tmp_path)
        new_file = tmp_path / to_file
        with open(new_file, "r") as read_file:
            case = json.load(read_file)
        assert case["decision_date"] == "1995-03-09"

    def test_download_and_make_opinion_object(self):
        lotus: Dict = download_case(cite="49 F.3d 807", save_to_file=False)
        lotus_opinion = opinion_from_case(**lotus)
        assert lotus_opinion.__class__.__name__ == "Opinion"

    def test_error_download_without_case_reference(self, tmp_path):
        to_file = "lotus_h.json"
        with pytest.raises(ValueError):
            download_case(filename=to_file, directory=tmp_path)

    def test_error_full_case_download_without_api_key(self, tmp_path):
        to_file = "lotus_h.json"
        with pytest.raises(ValueError):
            download_case(filename=to_file, directory=tmp_path, full_case=True)
