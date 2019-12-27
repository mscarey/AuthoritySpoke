import json
import os

import pytest

from authorityspoke.io.downloads import download_case
from authorityspoke.io.readers import read_decision
from authorityspoke.io.loaders import load_decision
from authorityspoke.io.loaders import load_and_read_decision

# pytestmark = pytest.mark.skip("don't want to call API")


class TestDownload:
    @pytest.mark.vcr
    def test_download_case_by_id(self, tmp_path):
        to_file = "oracle_h.json"
        download_case(cap_id=4066790, filename=to_file, directory=tmp_path)
        new_file = tmp_path / to_file
        with open(new_file, "r") as read_file:
            case = json.load(read_file)
        assert case["name_abbreviation"] == "Oracle America, Inc. v. Google Inc."

    @pytest.mark.vcr
    def test_download_case_by_cite(self, tmp_path):
        to_file = "lotus_h.json"
        download_case(cite="49 F.3d 807", filename=to_file, directory=tmp_path)
        new_file = tmp_path / to_file
        with open(new_file, "r") as read_file:
            case = json.load(read_file)
        assert case["decision_date"] == "1995-03-09"

    @pytest.mark.vcr
    def test_download_and_make_opinion(self):
        response = download_case(
            cite="49 F.3d 807", always_list=True, save_to_file=False
        )
        lotus = response[0]
        lotus_opinion = read_decision(lotus).majority
        assert lotus_opinion.__class__.__name__ == "Opinion"

    @pytest.mark.vcr
    def test_download_save_and_make_opinion(self, tmp_path):
        to_file = "lotus_h.json"
        download_case(
            cite="49 F.3d 807", filename=to_file, directory=tmp_path, save_to_file=True
        )
        filepath = tmp_path / to_file
        lotus_decision = load_and_read_decision(filepath=filepath)
        assert lotus_decision.majority.__class__.__name__ == "Opinion"
        assert "Lotus" in lotus_decision.name_abbreviation

    def test_error_download_without_case_reference(self, tmp_path):
        to_file = "lotus_h.json"
        with pytest.raises(ValueError):
            download_case(filename=to_file, directory=tmp_path)

    def test_error_bad_cap_id(self, tmp_path):
        to_file = "lotus_h.json"
        with pytest.raises(ValueError):
            download_case(cap_id=99999999, filename=to_file, directory=tmp_path)

    def test_error_bad_cite(self, tmp_path):
        to_file = "lotus_h.json"
        with pytest.raises(ValueError):
            download_case(
                cite="999 Cal 9th. 9999", filename=to_file, directory=tmp_path
            )

    def test_error_full_case_download_without_api_key(self, tmp_path):
        to_file = "lotus_h.json"
        with pytest.raises(ValueError):
            download_case(
                cite="49 F.3d 807", filename=to_file, directory=tmp_path, full_case=True
            )

    @pytest.mark.vcr
    def test_full_case_download(self, tmp_path):
        """
        This test costs one of your 500 daily full_case API calls every time you run it.

        The author field is only available because of the full_case flag.
        """
        to_file = "lotus_h.json"
        lotus = download_case(
            cite="49 F.3d 807",
            filename=to_file,
            directory=tmp_path,
            full_case=True,
            api_key=os.environ["CAP_API_KEY"],
        )
        assert lotus["casebody"]["data"]["opinions"][0]["author"].startswith("STAHL")
