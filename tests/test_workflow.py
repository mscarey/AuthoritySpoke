import os
from dotenv import load_dotenv

import pytest

from legislice.download import Client
from authorityspoke import Entity, Fact, Predicate, Holding


load_dotenv()
LEGISLICE_API_TOKEN = os.getenv("LEGISLICE_API_TOKEN")

CLIENT = Client(api_token=LEGISLICE_API_TOKEN)


class TestAddHoldings:
    """
    Test creating Holdings based on United States v. Harmon.

    No. 2019-0395 (D.D.C. 2020) (December 24th, 2020)
    """

    @pytest.mark.vcr
    def test_create_and_add_holdings(self):
        offense_statute = CLIENT.read("/us/usc/t18/s1960/a")
        no_license = Fact(
            "$business was licensed as a money transmitting business",
            truth=False,
            terms=Entity("Helix"),
        )
        operated = Fact(
            "$person operated $business as a business",
            terms=[Entity("Harmon"), Entity("Helix")],
        )
        transmitting = Fact(
            "$business was a money transmitting business", terms=Entity("Helix")
        )
        offense = Fact(
            "$person committed the offense of conducting an unlicensed money transmitting business",
            terms=Entity("Harmon"),
        )
        offense_holding = Holding.from_factors(
            inputs=[operated, transmitting, no_license],
            outputs=offense,
            enactments=offense_statute,
            universal=True,
        )
        definition_statute = CLIENT.read("/us/usc/t18/s1960/b/2")
        bitcoin = Fact(
            "$business transferred bitcoin on behalf of the public",
            terms=Entity("Helix"),
        )
        bitcoin_holding = Holding.from_factors(
            inputs=bitcoin,
            outputs=transmitting,
            enactments=definition_statute,
            universal=True,
        )
        assert "was a money transmitting business" in str(offense_holding.inputs)
        # The combined effect of the two holdings above is that if
        # a person operated a business that transferred bitcoin on behalf of
        # the public without a "money transmitting business" license,
        # the person is guilty of the offense.
        result = bitcoin_holding + offense_holding
        assert "<Helix> was a money transmitting business" not in str(result.inputs)
        assert "<Helix> was a money transmitting business" in str(result.outputs)
        assert "transferred bitcoin on behalf of the public" in str(result.inputs)
