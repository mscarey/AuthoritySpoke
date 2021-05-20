import json
import os

from dotenv import load_dotenv
import eyecite
import pytest

from authorityspoke.io.downloads import CAPClient, AuthoritySpokeAPIError
from authorityspoke.io.readers import read_decision
from authorityspoke.io.loaders import load_decision
from authorityspoke.io.loaders import load_and_read_decision
from authorityspoke.io import writers
from tests.test_notebooks import CAP_API_KEY

load_dotenv()


class TestDownload:
    client = CAPClient(api_token="Token " + CAP_API_KEY)

    @pytest.mark.vcr
    def test_download_case_by_id(self):
        case = self.client.fetch(4066790)
        assert case["name_abbreviation"] == "Oracle America, Inc. v. Google Inc."

    @pytest.mark.vcr
    def test_download_case_by_string_id(self):
        case = self.client.fetch("4066790")
        assert case["name_abbreviation"] == "Oracle America, Inc. v. Google Inc."

    @pytest.mark.vcr
    def test_download_case_by_cite(self):
        case = self.client.fetch("49 F.3d 807")
        assert case["decision_date"] == "1995-03-09"

    @pytest.mark.vcr
    def test_download_and_make_opinion(self):
        response = self.client.fetch_decision_list_by_cite(cite="49 F.3d 807")
        lotus = response[0]
        lotus_opinion = read_decision(lotus).majority
        assert lotus_opinion.__class__.__name__ == "Opinion"

    @pytest.mark.vcr
    def test_download_save_and_make_opinion(self, tmp_path):
        to_file = "lotus_h.json"
        lotus_from_api = self.client.fetch_cite(cite="49 F.3d 807")
        writers.case_to_file(case=lotus_from_api, filename=to_file, directory=tmp_path)
        filepath = tmp_path / to_file
        lotus_from_file = load_and_read_decision(filepath=filepath)
        assert lotus_from_file.majority.__class__.__name__ == "Opinion"
        assert "Lotus" in lotus_from_file.name_abbreviation

    def test_error_download_without_case_reference(self):
        with pytest.raises(TypeError):
            self.client.fetch_cite()

    @pytest.mark.vcr
    def test_error_bad_cap_id(self):
        with pytest.raises(AuthoritySpokeAPIError):
            self.client.fetch_id(cap_id=99999999)

    @pytest.mark.vcr
    def test_error_bad_cite(self):
        with pytest.raises(ValueError):
            self.client.fetch_cite(cite="999 Cal 9th. 9999")

    @pytest.mark.vcr
    def test_error_full_case_download_without_api_key(self):
        bad_client = CAPClient()
        with pytest.raises(AuthoritySpokeAPIError):
            bad_client.fetch_cite(cite="49 F.3d 807", full_case=True)

    @pytest.mark.skip(reason="uses API key")
    @pytest.mark.vcr
    def test_full_case_download(self):
        """
        This test costs one of your 500 daily full_case API calls every time you run it.

        The author field is only available because of the full_case flag.
        """
        lotus = self.client.fetch_cite(cite="49 F.3d 807", full_case=True)
        assert lotus["casebody"]["data"]["opinions"][0]["author"].startswith("STAHL")

    @pytest.mark.vcr
    def test_read_case_using_client(self):
        licensing_case = self.client.read(query="621 F.3d 205", full_case=False)
        assert licensing_case.name_abbreviation == "United States v. Mazza-Alaluf"

    @pytest.mark.vcr
    def test_read_case_from_id_using_client(self):
        case = self.client.read(query=3675682, full_case=False)
        assert case.name_abbreviation == "Kimbrough v. United States"
        cited_case = self.client.read_cite(cite=case.cites_to[0])
        assert cited_case.name_abbreviation == "United States v. Booker"

    @pytest.mark.vcr
    def test_read_full_case_from_id_using_client(self):
        """Test full case not requiring API key because Arkansas is a free jurisdiction."""
        case = self.client.read_id(cap_id=236682, full_case=True)
        assert "clerical misprision" in case.majority.text
        assert not case.majority.author
        # Add day if missing from date
        assert case.date.isoformat() == "1821-06-01"

    @pytest.mark.vcr
    def test_read_case_list_from_eyecite_case_citation(self):
        case_citation = eyecite.get_citations("9 F. Cas. 50")[0]
        cases_again = self.client.read_decision_list_by_cite(cite=case_citation)
        assert cases_again[0].name_abbreviation == "Fikes v. Bentley"

    @pytest.mark.vcr
    def test_fail_to_read_id_cite(self):
        with pytest.raises(ValueError, match="was type IdCitation, not CaseCitation"):
            self.client.read_decision_list_by_cite(cite="id. at 37")
