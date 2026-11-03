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

COPYRIGHT_CLAUSE = EnactmentPassage(
    enactment=Enactment(
        node="/us/const/article/I/8/8",
        start_date=date(1788, 9, 13),
        heading="Patents and copyrights.",
        text_version=TextVersion(
            content="To promote the Progress of Science and useful Arts, by securing for limited Times to Authors and Inventors the exclusive Right to their respective Writings and Discoveries;",
            url="https://authorityspoke.com/api/v1/textversions/735650/",
            id=735650,
        ),
        end_date=None,
        first_published=None,
        earliest_in_db=None,
        anchors=[],
        citations=[],
        name="/us/const/article/I/8/8",
        children=[],
    ),
    selection=TextPositionSet(
        quotes=[
            TextQuoteSelector(
                exact="To promote the Progress of Science and useful Arts, by securing for limited Times to Authors",
                prefix="",
                suffix="",
            ),
            TextQuoteSelector(
                exact="the exclusive Right to their respective Writings",
                prefix="",
                suffix="",
            ),
        ],
    ),
)

COMPILATION_COPYRIGHT_RULE = EnactmentPassage(
    enactment=Enactment(
        node="/us/usc/t17/s103/b",
        start_date=date(2013, 7, 18),
        heading="",
        text_version=TextVersion(
            content="The copyright in a compilation or derivative work extends only to the material contributed by the author of such work, as distinguished from the preexisting material employed in the work, and does not imply any exclusive right in the preexisting material. The copyright in such work is independent of, and does not affect or enlarge the scope, duration, ownership, or subsistence of, any copyright protection in the preexisting material.",
            url="https://authorityspoke.com/api/v1/textversions/1030582/",
            id=1030582,
        ),
        end_date=None,
        first_published=None,
        earliest_in_db=None,
        anchors=[],
        citations=[],
        name="/us/usc/t17/s103/b",
        children=[],
    ),
    selection=TextPositionSet(
        quotes=[
            TextQuoteSelector(
                exact="The copyright in a compilation",
                prefix="",
                suffix="",
            ),
            TextQuoteSelector(
                exact="extends only to the material contributed by the author of such work, as distinguished from the preexisting material employed in the work, and does not imply any exclusive right in the preexisting material.",
                prefix="",
                suffix="",
            ),
        ],
    ),
)

COPYRIGHTABILITY_REQUIREMENT = EnactmentPassage(
    enactment=Enactment(
        node="/us/usc/t17/s102/a",
        start_date=date(2013, 7, 18),
        heading="",
        text_version=TextVersion(
            content="Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device. Works of authorship include the following categories:",
            url="https://authorityspoke.com/api/v1/textversions/1030579/",
            id=1030579,
        ),
        end_date=None,
        first_published=None,
        earliest_in_db=None,
        anchors=[],
        citations=[],
        name="/us/usc/t17/s102/a",
        children=[
            Enactment(
                node="/us/usc/t17/s102/a/1",
                start_date=date(2013, 7, 18),
                heading="",
                text_version=TextVersion(
                    content="literary works;",
                    url="https://authorityspoke.com/api/v1/textversions/1030571/",
                    id=1030571,
                ),
                end_date=None,
                first_published=None,
                earliest_in_db=None,
                anchors=[],
                citations=[],
                name="",
                children=[],
            ),
            Enactment(
                node="/us/usc/t17/s102/a/2",
                start_date=date(2013, 7, 18),
                heading="",
                text_version=TextVersion(
                    content="musical works, including any accompanying words;",
                    url="https://authorityspoke.com/api/v1/textversions/1030572/",
                    id=1030572,
                ),
                end_date=None,
                first_published=None,
                earliest_in_db=None,
                anchors=[],
                citations=[],
                name="",
                children=[],
            ),
            Enactment(
                node="/us/usc/t17/s102/a/3",
                start_date=date(2013, 7, 18),
                heading="",
                text_version=TextVersion(
                    content="dramatic works, including any accompanying music;",
                    url="https://authorityspoke.com/api/v1/textversions/1030573/",
                    id=1030573,
                ),
                end_date=None,
                first_published=None,
                earliest_in_db=None,
                anchors=[],
                citations=[],
                name="",
                children=[],
            ),
            Enactment(
                node="/us/usc/t17/s102/a/4",
                start_date=date(2013, 7, 18),
                heading="",
                text_version=TextVersion(
                    content="pantomimes and choreographic works;",
                    url="https://authorityspoke.com/api/v1/textversions/1030574/",
                    id=1030574,
                ),
                end_date=None,
                first_published=None,
                earliest_in_db=None,
                anchors=[],
                citations=[],
                name="",
                children=[],
            ),
            Enactment(
                node="/us/usc/t17/s102/a/5",
                start_date=date(2013, 7, 18),
                heading="",
                text_version=TextVersion(
                    content="pictorial, graphic, and sculptural works;",
                    url="https://authorityspoke.com/api/v1/textversions/1030575/",
                    id=1030575,
                ),
                end_date=None,
                first_published=None,
                earliest_in_db=None,
                anchors=[],
                citations=[],
                name="",
                children=[],
            ),
            Enactment(
                node="/us/usc/t17/s102/a/6",
                start_date=date(2013, 7, 18),
                heading="",
                text_version=TextVersion(
                    content="motion pictures and other audiovisual works;",
                    url="https://authorityspoke.com/api/v1/textversions/1030576/",
                    id=1030576,
                ),
                end_date=None,
                first_published=None,
                earliest_in_db=None,
                anchors=[],
                citations=[],
                name="",
                children=[],
            ),
            Enactment(
                node="/us/usc/t17/s102/a/7",
                start_date=date(2013, 7, 18),
                heading="",
                text_version=TextVersion(
                    content="sound recordings; and",
                    url="https://authorityspoke.com/api/v1/textversions/1030577/",
                    id=1030577,
                ),
                end_date=None,
                first_published=None,
                earliest_in_db=None,
                anchors=[],
                citations=[],
                name="",
                children=[],
            ),
            Enactment(
                node="/us/usc/t17/s102/a/8",
                start_date=date(2013, 7, 18),
                heading="",
                text_version=TextVersion(
                    content="architectural works.",
                    url="https://authorityspoke.com/api/v1/textversions/1030578/",
                    id=1030578,
                ),
                end_date=None,
                first_published=None,
                earliest_in_db=None,
                anchors=[],
                citations=[],
                name="",
                children=[],
            ),
        ],
    ),
    selection=TextPositionSet(
        quotes=[
            TextQuoteSelector(
                exact="",
                prefix="",
                suffix="fixed in any tangible",
            ),
        ],
    ),
)

IDEA_EXPRESSION_RULE = EnactmentPassage(
    enactment=Enactment(
        node="/us/usc/t17/s102/b",
        start_date=date(2013, 7, 18),
        heading="",
        text_version=TextVersion(
            content="In no case does copyright protection for an original work of authorship extend to any idea, procedure, process, system, method of operation, concept, principle, or discovery, regardless of the form in which it is described, explained, illustrated, or embodied in such work.",
            url="https://authorityspoke.com/api/v1/textversions/1030580/",
            id=1030580,
        ),
        end_date=None,
        first_published=None,
        earliest_in_db=None,
        anchors=[],
        citations=[],
        name="/us/usc/t17/s102/b",
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

SHORT_PHRASES_EXCLUSION_RULE = EnactmentPassage(
    enactment=Enactment(
        node="/us/cfr/t37/s202.1",
        start_date=date(1992, 2, 21),
        heading="",
        text_version=TextVersion(
            content=(
                "The following are examples of works not subject to copyright and "
                "applications for registration of such works cannot be entertained: "
                "Words and short phrases such as names, titles, and slogans; familiar "
                "symbols or designs; mere variations of typographic ornamentation, "
                "lettering, or coloring; mere listing of ingredients or contents."
            ),
            url=None,
            id=None,
        ),
        end_date=None,
        first_published=None,
        earliest_in_db=None,
        anchors=[],
        citations=[],
        name="/us/cfr/t37/s202.1",
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

COPYRIGHT_REGISTRATION_EVIDENCE_RULE = EnactmentPassage(
    enactment=Enactment(
        node="/us/usc/t17/s410/c",
        start_date=date(2013, 7, 18),
        heading="",
        text_version=TextVersion(
            content="In any judicial proceedings the certificate of a registration made before or within five years after first publication of the work shall constitute prima facie evidence of the validity of the copyright and of the facts stated in the certificate. The evidentiary weight to be accorded the certificate of a registration made thereafter shall be within the discretion of the court.",
            url="https://authorityspoke.com/api/v1/textversions/1031576/",
            id=1031576,
        ),
        end_date=None,
        first_published=None,
        earliest_in_db=None,
        anchors=[],
        citations=[],
        name="/us/usc/t17/s410/c",
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


STATE_MONEY_TRANSMITTING_LICENSE_PROVISION = EnactmentPassage(
    enactment=Enactment(
        node="/us/usc/t18/s1960/b/1",
        start_date=date(2013, 7, 18),
        heading="",
        text_version=TextVersion(
            content=(
                'the term "unlicensed money transmitting business" means a money transmitting '
                "business which affects interstate or foreign commerce in any manner or degree "
                "and is operated without an appropriate money transmitting license in a State "
                "where such operation is punishable as a misdemeanor or a felony under State law, "
                "whether or not the defendant knew that the operation was required to be licensed "
                "or that the operation was so punishable; fails to comply with the money "
                "transmitting business registration requirements under section 5330 of title 31, "
                "United States Code, or regulations prescribed under such section; or otherwise "
                "involves the transportation or transmission of funds that are known to the "
                "defendant to have been derived from a criminal offense or are intended to be used "
                "to promote or support unlawful activity;"
            ),
            url=None,
            id=None,
        ),
        end_date=None,
        first_published=None,
        earliest_in_db=None,
        anchors=[],
        citations=[],
        name="/us/usc/t18/s1960/b/1",
        children=[],
    ),
    selection=TextPositionSet(
        quotes=[
            TextQuoteSelector(
                exact=(
                    "is operated without an appropriate money transmitting license in a State "
                    "where such operation is punishable as a misdemeanor or a felony under "
                    "State law, whether or not the defendant knew that the operation was "
                    "required to be licensed or that the operation was so punishable"
                ),
                prefix="",
                suffix="",
            )
        ]
    ),
)

DOMESTIC_FINANCIAL_INSTITUTION_PROVISION = EnactmentPassage(
    enactment=Enactment(
        node="/us/usc/t31/s5312/b/1",
        start_date=date(2013, 7, 18),
        heading="",
        text_version=TextVersion(
            content=(
                '"domestic financial agency" and "domestic financial institution" apply to '
                "an action in the United States of a financial agency or institution."
            ),
            url=None,
            id=None,
        ),
        end_date=None,
        first_published=None,
        earliest_in_db=None,
        anchors=[],
        citations=[],
        name="/us/usc/t31/s5312/b/1",
        children=[],
    ),
    selection=TextPositionSet(
        quotes=[
            TextQuoteSelector(
                exact=(
                    '"domestic financial agency" and "domestic financial institution" apply '
                    "to an action in the United States of a financial agency or institution."
                ),
                prefix="",
                suffix="",
            )
        ]
    ),
)
