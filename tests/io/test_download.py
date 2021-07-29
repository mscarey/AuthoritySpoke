from authorityspoke.decisions import Decision
import json
import os

from dotenv import load_dotenv
import eyecite
import pytest

from justopinion.decisions import CAPDecision

from authorityspoke.io.downloads import CAPClient, CaseAccessProjectAPIError
from authorityspoke import LegisClient, DecisionReading
from authorityspoke.io.loaders import load_decision
from authorityspoke.io import writers
from tests.test_notebooks import CAP_API_KEY

load_dotenv()


class TestDownload:
    client = CAPClient(api_token="Token " + CAP_API_KEY)

    @pytest.mark.vcr
    def test_download_case_by_id(self):
        case = self.client.fetch(4066790)
        assert case.json()["name_abbreviation"] == "Oracle America, Inc. v. Google Inc."

    @pytest.mark.default_cassette("TestDownload.test_download_case_by_id.yaml")
    @pytest.mark.vcr
    def test_download_case_by_string_id(self):
        response = self.client.fetch("4066790")
        oracle = self.client.read_decision_from_response(response)
        assert oracle.name_abbreviation == "Oracle America, Inc. v. Google Inc."

    @pytest.mark.vcr
    def test_full_case_download(self):
        """
        This costs one of your 500 daily full_case API calls if there's no VCR cassette.

        The author field is only available because of the full_case flag.
        """
        response = self.client.fetch_cite(cite="49 F.3d 807", full_case=True)
        lotus = self.client.read_decision_from_response(response)
        assert lotus.casebody.data.opinions[0].author.startswith("STAHL")

    @pytest.mark.default_cassette("TestDownload.test_full_case_download.yaml")
    @pytest.mark.vcr
    def test_download_and_make_opinion(self):
        response = self.client.read_decision_list_by_cite(
            cite="49 F.3d 807", full_case=True
        )
        lotus = response[0]
        lotus_opinion = lotus.majority
        assert lotus_opinion.__class__.__name__ == "CAPOpinion"

    @pytest.mark.vcr
    def test_download_case_by_cite(self):
        case = self.client.read_cite("49 F.3d 807")
        assert case.decision_date.isoformat() == "1995-03-09"

    @pytest.mark.default_cassette("TestDownload.test_download_case_by_cite.yaml")
    @pytest.mark.vcr
    def test_decision_without_opinion_posits_holding(self, make_holding):
        """Test that a blank opinion is created when the decision doesn't have an opinion."""
        decision = self.client.read_cite("49 F.3d 807")
        reading = DecisionReading(decision=decision)
        reading.posit(make_holding["h2"])
        assert len(reading.holdings) == 1
        assert reading.casebody.status != "ok"

    @pytest.mark.default_cassette("TestDownload.test_full_case_download.yaml")
    @pytest.mark.vcr
    def test_download_save_and_make_opinion(self, tmp_path):
        to_file = "lotus_h.json"
        lotus_from_api = self.client.read_cite(cite="49 F.3d 807", full_case=True)
        writers.case_to_file(case=lotus_from_api, filename=to_file, directory=tmp_path)
        filepath = tmp_path / to_file
        lotus_from_file = load_decision(filepath=filepath)
        lotus = Decision(**lotus_from_file)
        assert lotus.majority.__class__.__name__ == "CAPOpinion"
        assert "Lotus" in lotus.name_abbreviation

    def test_error_download_without_case_reference(self):
        with pytest.raises(TypeError):
            self.client.fetch_cite()

    @pytest.mark.vcr
    def test_error_bad_cap_id(self):
        with pytest.raises(CaseAccessProjectAPIError):
            self.client.fetch_id(cap_id=99999999)

    @pytest.mark.vcr
    def test_error_bad_cite(self):
        with pytest.raises(ValueError):
            self.client.fetch_cite(cite="999 Cal 9th. 9999")

    @pytest.mark.vcr
    def test_error_full_case_download_without_api_key(self):
        bad_client = CAPClient()
        with pytest.raises(CaseAccessProjectAPIError):
            bad_client.fetch_cite(cite="49 F.3d 807", full_case=True)

    @pytest.mark.vcr
    def test_read_case_using_client(self):
        licensing_case = self.client.read(query="621 F.3d 205", full_case=False)
        assert licensing_case.name_abbreviation == "United States v. Mazza-Alaluf"

    @pytest.mark.vcr
    def test_read_case_from_id_using_client(self):
        case = self.client.read(query=3675682, full_case=False)
        assert case.name_abbreviation == "Kimbrough v. United States"
        cited_case = self.client.read_cite(cite=case.cites_to[0])
        assert cited_case.name_abbreviation == "United States v. Castillo"

    @pytest.mark.vcr
    def test_read_full_case_from_id_using_client(self):
        """Test full case not requiring API key because Arkansas is a free jurisdiction."""
        case = self.client.read_id(cap_id=236682, full_case=True)
        assert "clerical misprision" in case.majority.text
        assert not case.majority.author
        # Add day if missing from date
        assert case.decision_date.isoformat() == "1821-06-01"

    @pytest.mark.vcr
    def test_read_case_list_from_eyecite_case_citation(self):
        case_citation = eyecite.get_citations("9 F. Cas. 50")[0]
        cases_again = self.client.read_decision_list_by_cite(cite=case_citation)
        assert cases_again[0].name_abbreviation == "Fikes v. Bentley"

    @pytest.mark.vcr
    def test_fail_to_read_id_cite(self):
        with pytest.raises(ValueError, match="was type IdCitation, not CaseCitation"):
            self.client.read_decision_list_by_cite(cite="id. at 37")
