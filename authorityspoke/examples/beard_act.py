import json
from pathlib import Path

from authorityspoke.nettlesome.entities import Entity
from authorityspoke.nettlesome.predicates import Predicate
from authorityspoke.nettlesome.quantities import Comparison, UnitRange

from authorityspoke.facts import (
    AbsenceOfFactor,
    Fact,
    Evidence,
)
from authorityspoke.facts import Exhibit
from authorityspoke.passages import passage_from_quotes
from authorityspoke.rules import Procedure, Rule

from authorityspoke.io.fake_enactments import FakeClient


def beard_response() -> dict[str, dict]:
    """Mock api responses"""
    this_directory = Path(__file__).parent
    parent_directory = this_directory.parent.parent
    responses_filepath = (
        parent_directory / "example_data" / "responses" / "beard_act.json"
    )
    with open(responses_filepath, "r") as f:
        responses = json.load(f)
    return responses


def rules() -> list[Rule]:
    """Rules from the Beard Tax Act built directly from Python model objects."""
    client = FakeClient(responses=beard_response())

    suspected_beard = Entity(name="the suspected beard")
    defendant = Entity(name="the defendant")
    department = Entity(name="the Department of Beards")
    counterparty = Entity(name="the counterparty")
    transaction = Entity(name="the beardcoin transaction")
    barber = Entity(name="the barber")
    customer = Entity(name="the customer")

    fact_facial_hair = Fact(
        predicate=Predicate(content="{the_suspected_beard} was facial hair"),
        terms=[suspected_beard],
    )
    fact_length = Fact(
        predicate=Comparison(
            content="the length of {the_suspected_beard} was",
            quantity_range=UnitRange(
                sign=">=", quantity_magnitude=5, quantity_units="millimetres"
            ),
        ),
        terms=[suspected_beard],
    )
    fact_chin = Fact(
        predicate=Predicate(
            content="{the_suspected_beard} occurred on or below the chin"
        ),
        terms=[suspected_beard],
    )
    fact_ear_line = Fact(
        predicate=Predicate(
            content=(
                "{the_suspected_beard} existed in an uninterrupted line from the front "
                "of one ear to the front of the other ear below the nose"
            )
        ),
        terms=[suspected_beard],
    )
    fact_is_beard = Fact(
        predicate=Predicate(content="{the_suspected_beard} was a beard"),
        terms=[suspected_beard],
        name="the fact that the facial hair was a beard",
    )
    fact_wore_beard = Fact(
        predicate=Predicate(content="{the_defendant} wore {the_suspected_beard}"),
        terms=[defendant, suspected_beard],
        name="the defendant's act of wearing the suspected beard",
    )
    fact_no_exemption = Fact(
        predicate=Predicate(
            content=(
                "the office of {the_department_of_beards} granted an exemption "
                "authorizing the defendant's act of wearing the suspected beard"
            ),
            truth=False,
        ),
        terms=[department],
    )
    offense_wearing_without_exemption = Fact(
        predicate=Predicate(
            content=(
                "{the_defendant} committed the offense of wearing of a beard "
                "without exemption"
            )
        ),
        terms=[defendant],
        name="offense of wearing a beard without exemption",
    )
    fact_defendant_exemption = Fact(
        predicate=Predicate(
            content=(
                "{the_department_of_beards} granted an exemption authorizing the "
                "defendant's act of wearing the suspected beard"
            )
        ),
        terms=[department],
        name="{the_department_of_beards} granted the defendant's beard exemption",
    )
    fact_general_exemption = Fact(
        predicate=Predicate(
            content=(
                "{the_department_of_beards} granted an exemption from the prohibition "
                "of wearing beards"
            )
        ),
        terms=[department],
    )
    defendant_beardcoin = Exhibit(
        offered_by=defendant,
        form="token",
        statement=fact_defendant_exemption,
        statement_attribution=department,
        name="the defendant's beardcoin",
    )
    evidence_beardcoin = Evidence(
        exhibit=defendant_beardcoin,
        to_effect=fact_defendant_exemption,
    )
    beardcoin_transfer = Fact(
        predicate=Predicate(
            content=(
                "{the_beardcoin_transaction} was a transfer of beardcoin between "
                "{the_defendant} and {the_counterparty}"
            )
        ),
        terms=[transaction, defendant, counterparty],
        name="beardcoin transfer",
    )
    purchase_transfer = Fact(
        predicate=Predicate(
            content=(
                "{the_beardcoin_transaction} was {the_defendant}'s purchase of {defendant_beardcoin} "
                "from {the_counterparty}"
            )
        ),
        terms=[transaction, defendant, counterparty, defendant_beardcoin],
    )
    counterparty_purchase = Fact(
        predicate=Predicate(
            content=(
                "{the_beardcoin_transaction} was {the_counterparty}'s purchase of {defendant_beardcoin} "
                "from {the_defendant}"
            )
        ),
        terms=[transaction, counterparty, defendant_beardcoin, defendant],
    )
    defendant_loan = Fact(
        predicate=Predicate(
            content=(
                "{the_beardcoin_transaction} was {the_defendant}'s loan of {defendant_beardcoin} "
                "to {the_counterparty}"
            )
        ),
        terms=[transaction, defendant, counterparty, defendant_beardcoin],
    )
    defendant_lease = Fact(
        predicate=Predicate(
            content=(
                "{the_beardcoin_transaction} was {the_defendant}'s lease of {defendant_beardcoin} "
                "to {the_counterparty}"
            )
        ),
        terms=[transaction, defendant, defendant_beardcoin, counterparty],
    )
    defendant_gift = Fact(
        predicate=Predicate(
            content=(
                "{the_beardcoin_transaction} was {the_defendant}'s gift of {defendant_beardcoin} "
                "to {the_counterparty}"
            )
        ),
        terms=[transaction, defendant, defendant_beardcoin, counterparty],
    )
    defendant_receipt = Fact(
        predicate=Predicate(
            content=(
                "{the_beardcoin_transaction} was {the_defendant}'s receipt of {defendant_beardcoin} "
                "from {the_counterparty}"
            )
        ),
        terms=[transaction, defendant, defendant_beardcoin, counterparty],
    )
    licensed_repurchase = Fact(
        predicate=Predicate(
            content="{the_beardcoin_transaction} was a licensed beardcoin repurchase"
        ),
        terms=[transaction],
    )
    absent_licensed_repurchase = AbsenceOfFactor(absent=licensed_repurchase)
    counterparty_not_department = Fact(
        predicate=Predicate(
            content="{the_counterparty} was {the_department_of_beards}", truth=False
        ),
        terms=[counterparty, department],
    )
    counterfeit_beardcoin = Fact(
        predicate=Predicate(content="any beardcoin was counterfeit")
    )
    improper_transfer_offense = Fact(
        predicate=Predicate(
            content=(
                "{the_defendant} committed the offense of improper transfer of "
                "beardcoin"
            )
        ),
        terms=[defendant],
    )
    counterfeit_offense = Fact(
        predicate=Predicate(
            content="the defendant committed the offense of counterfeiting beardcoin"
        )
    )
    counterfeit_tokens = Fact(
        predicate=Predicate(
            content=(
                "the defendant produced, altered, or manufactured tokens with the "
                "appearance of and purporting to be genuine beardcoin"
            )
        )
    )
    barber_purchase = Fact(
        predicate=Predicate(
            content=(
                "{the_beardcoin_transaction} was {the_barber}'s purchase of {defendant_beardcoin} "
                "from {the_customer}"
            )
        ),
        terms=[transaction, barber, customer, defendant_beardcoin],
    )
    barber_removed_beard = Fact(
        predicate=Predicate(
            content=(
                "the barber removed the customer's beard with barbering, hairdressing, "
                "or other male grooming services"
            )
        )
    )
    barber_licensed = Fact(
        predicate=Predicate(
            content=(
                "{the_department_of_beards} licensed the barber to purchase beardcoins "
                "from customers"
            )
        ),
        terms=[department],
    )

    return [
        Rule(
            procedure=Procedure(
                inputs=[fact_facial_hair, fact_length, fact_chin],
                outputs=[fact_is_beard],
            ),
            enactments=passage_from_quotes(
                client,
                "/test/acts/47/4",
                [
                    "In this Act, beard means any facial hair no shorter than 5 millimetres in length that: occurs on or below the chin"
                ],
            ),
            universal=True,
        ),
        Rule(
            procedure=Procedure(
                inputs=[fact_facial_hair, fact_length, fact_ear_line],
                outputs=[fact_is_beard],
            ),
            enactments=[
                passage_from_quotes(
                    client,
                    "/test/acts/47/4",
                    [
                        "In this Act, beard means any facial hair no shorter than 5 millimetres in length that:",
                        "exists in an uninterrupted line from the front of one ear to the front of the other ear below the nose.",
                    ],
                ),
                passage_from_quotes(client, "/test/acts/47/4/b"),
            ],
            universal=True,
        ),
        Rule(
            procedure=Procedure(
                inputs=[fact_is_beard, fact_wore_beard, fact_no_exemption],
                outputs=[offense_wearing_without_exemption],
            ),
            enactments=[
                passage_from_quotes(client, "/test/acts/47/5"),
                passage_from_quotes(client, "/test/acts/47/7"),
            ],
            enactments_despite=[passage_from_quotes(client, "/test/acts/47/6")],
            universal=True,
        ),
        Rule(
            procedure=Procedure(
                inputs=[fact_defendant_exemption], outputs=[fact_general_exemption]
            ),
            enactments=passage_from_quotes(client, "/test/acts/47/6/1"),
            universal=True,
            mandatory=True,
        ),
        Rule(
            procedure=Procedure(
                inputs=[defendant_beardcoin], outputs=[evidence_beardcoin]
            ),
            enactments=passage_from_quotes(client, "/test/acts/47/6C"),
            universal=True,
        ),
        Rule(
            procedure=Procedure(
                inputs=[purchase_transfer], outputs=[beardcoin_transfer]
            ),
            enactments=passage_from_quotes(client, "/test/acts/47/7A"),
            universal=True,
            mandatory=True,
        ),
        Rule(
            procedure=Procedure(
                inputs=[counterparty_purchase], outputs=[beardcoin_transfer]
            ),
            enactments=passage_from_quotes(client, "/test/acts/47/7A"),
            universal=True,
            mandatory=True,
        ),
        Rule(
            procedure=Procedure(inputs=[defendant_loan], outputs=[beardcoin_transfer]),
            enactments=passage_from_quotes(client, "/test/acts/47/7A"),
            universal=True,
            mandatory=True,
        ),
        Rule(
            procedure=Procedure(inputs=[defendant_lease], outputs=[beardcoin_transfer]),
            enactments=passage_from_quotes(client, "/test/acts/47/7A"),
            universal=True,
            mandatory=True,
        ),
        Rule(
            procedure=Procedure(inputs=[defendant_gift], outputs=[beardcoin_transfer]),
            enactments=passage_from_quotes(client, "/test/acts/47/7A"),
            universal=True,
            mandatory=True,
        ),
        Rule(
            procedure=Procedure(
                inputs=[defendant_receipt], outputs=[beardcoin_transfer]
            ),
            enactments=passage_from_quotes(client, "/test/acts/47/7A"),
            universal=True,
            mandatory=True,
        ),
        Rule(
            procedure=Procedure(
                inputs=[
                    beardcoin_transfer,
                    absent_licensed_repurchase,
                    counterparty_not_department,
                ],
                despite=[counterfeit_beardcoin],
                outputs=[improper_transfer_offense],
            ),
            enactments=[
                passage_from_quotes(client, "/test/acts/47/7A"),
                passage_from_quotes(client, "/test/acts/47/7B/2"),
            ],
            enactments_despite=[passage_from_quotes(client, "/test/acts/47/11")],
            mandatory=True,
            universal=True,
        ),
        Rule(
            procedure=Procedure(
                inputs=[counterfeit_tokens], outputs=[counterfeit_offense]
            ),
            enactments=passage_from_quotes(client, "/test/acts/47/7B/1"),
        ),
        Rule(
            procedure=Procedure(
                inputs=[barber_purchase, barber_removed_beard, barber_licensed],
                outputs=[licensed_repurchase],
            ),
            enactments=passage_from_quotes(client, "/test/acts/47/11"),
        ),
    ]
