from datetime import date

from legislice.enactments import (
    Enactment,
    EnactmentPassage,
    TextPositionSet,
    TextVersion,
    TextQuoteSelector,
)

SEARCH_CLAUSE = EnactmentPassage(
    enactment=Enactment(
        node="/us/const/amendment/IV",
        start_date=date(1791, 12, 15),
        heading="AMENDMENT IV.",
        text_version=TextVersion(
            content="The right of the people to be secure in their persons, "
            "houses, papers, and effects, against unreasonable searches and "
            "seizures, shall not be violated, and no Warrants shall issue, but "
            "upon probable cause, supported by Oath or affirmation, and "
            "particularly describing the place to be searched, and the persons "
            "or things to be seized.",
            url="https://authorityspoke.com/api/v1/textversions/735706/",
            id=735706,
        ),
        end_date=None,
        first_published=None,
        earliest_in_db=None,
        anchors=[],
        citations=[],
        name="/us/const/amendment/IV",
        children=[],
    ),
    selection=TextPositionSet(
        quotes=[
            TextQuoteSelector(
                exact="",
                prefix="",
                suffix=", and no Warrants shall issue",
            )
        ],
    ),
)

DUE_PROCESS_CLAUSE = EnactmentPassage(
    enactment=Enactment(
        node="/us/const/amendment/XIV/1",
        start_date=date(1868, 7, 28),
        heading="Citizenship: security and equal protection of citizens.",
        text_version=TextVersion(
            content="All persons born or naturalized in the United States, and "
            "subject to the jurisdiction thereof, are citizens of the United States "
            "and of the State wherein they reside. No State shall make or enforce any "
            "law which shall abridge the privileges or immunities of citizens of the "
            "United States; nor shall any State deprive any person of life, liberty, or "
            "property, without due process of law; nor deny to any person within its "
            "jurisdiction the equal protection of the laws.",
            url="https://authorityspoke.com/api/v1/textversions/735717/",
            id=735717,
        ),
        end_date=None,
        first_published=None,
        earliest_in_db=None,
        anchors=[],
        citations=[],
        name="/us/const/amendment/XIV/1",
        children=[],
    ),
    selection=TextPositionSet(
        quotes=[
            TextQuoteSelector(
                exact="",
                prefix="immunities of citizens of the United States; ",
                suffix=" nor deny to any person",
            )
        ],
    ),
)
