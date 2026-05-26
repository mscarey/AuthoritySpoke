from datetime import date

from legislice.enactments import (
    Enactment,
    EnactmentPassage,
    TextPositionSet,
    TextVersion,
    TextQuoteSelector,
    TextPositionSelector,
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

EVID_351 = EnactmentPassage(
    enactment=Enactment(
        node="/us-ca/code/evid/s351@1966-01-01",
        start_date=date(1966, 1, 1),
        heading="",
        text_version=TextVersion(
            content="Except as otherwise provided by statute, all relevant evidence is admissible.",
            url=None,
            id=None,
        ),
        end_date=None,
        first_published=None,
        earliest_in_db=None,
        anchors=[],
        citations=[],
        name="/us-ca/code/evid/s351@1966-01-01",
        children=[],
    ),
    selection=TextPositionSet(
        positions=[
            TextPositionSelector(
                start=0,
                end=None,
            )
        ],
    ),
)


UNDUE_PREJUDICE_RULE = EnactmentPassage(
    enactment=Enactment(
        node="/us-ca/code/evid/s352@1966-01-01",
        start_date=date(1966, 1, 1),
        heading="",
        text_version=TextVersion(
            content="The court in its discretion may exclude evidence if its probative value is "
            "substantially outweighed by the probability that its admission will necessitate "
            "undue consumption of time or create substantial danger of undue prejudice, of "
            "confusing the issues, or of misleading the jury.",
            url=None,
            id=None,
        ),
        end_date=None,
        first_published=None,
        earliest_in_db=None,
        anchors=[],
        citations=[],
        name="/us-ca/code/evid/s352@1966-01-01",
        children=[
            Enactment(
                node="/us-ca/code/evid/s352/a@1966-01-01",
                start_date=date(1966, 1, 1),
                heading="",
                text_version=TextVersion(
                    content="necessitate undue consumption of time or",
                    url=None,
                    id=None,
                ),
                end_date=None,
                first_published=None,
                earliest_in_db=None,
                anchors=[],
                citations=[],
                name="/us-ca/code/evid/s352/a@1966-01-01",
                children=[],
            ),
            Enactment(
                node="/us-ca/code/evid/s352/b@1966-01-01",
                start_date=date(1966, 1, 1),
                heading="",
                text_version=TextVersion(
                    content="create substantial danger of undue prejudice, of confusing the issues, or of misleading the jury.",
                    url=None,
                    id=None,
                ),
                end_date=None,
                first_published=None,
                earliest_in_db=None,
                anchors=[],
                citations=[],
                name="/us-ca/code/evid/s352/b@1966-01-01",
                children=[],
            ),
        ],
    ),
    selection=TextPositionSet(
        quotes=[
            TextQuoteSelector(
                exact="",
                prefix="",
                suffix="necessitate undue",
            ),
            TextQuoteSelector(
                exact="create substantial danger of undue prejudice",
                prefix="",
                suffix="",
            ),
        ],
    ),
)

ROBBERY_STATUTE = EnactmentPassage(
    enactment=Enactment(
        node="/us-ca/code/penal/s211@1873-01-01",
        start_date=date(1873, 1, 1),
        heading="",
        text_version=TextVersion(
            content="Robbery is the felonious taking of personal property in the possession of another, from his person or immediate presence, and against his will, accomplished by means of force or fear.",
            url=None,
            id=None,
        ),
        end_date=None,
        first_published=None,
        earliest_in_db=None,
        anchors=[],
        citations=[],
        name="/us-ca/code/penal/s211@1872-01-01",
        children=[],
    ),
    selection=TextPositionSet(
        positions=[
            TextPositionSelector(
                start=0,
                end=None,
            )
        ],
    ),
)

ATTEMPT_STATUTE = EnactmentPassage(
    enactment=Enactment(
        node="/us-ca/code/pen/s664@2011-04-04",
        start_date=date(2011, 4, 4),
        heading="",
        text_version=TextVersion(
            content="Every person who attempts to commit any crime, but fails, or is prevented or intercepted in its perpetration, shall be punished where no provision is made by law for the punishment of those attempts, [text omitted]",
            url=None,
            id=None,
        ),
        end_date=None,
        first_published=None,
        earliest_in_db=None,
        anchors=[],
        citations=[],
        name="/us-ca/code/pen/s664@2011-04-04",
        children=[],
    ),
    selection=TextPositionSet(
        quotes=[
            TextQuoteSelector(
                exact="",
                prefix="",
                suffix="where no provision is",
            )
        ],
    ),
)
