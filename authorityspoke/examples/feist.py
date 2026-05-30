import copy

from authorityspoke.examples.legislation import (
    COMPILATION_COPYRIGHT_RULE,
    COPYRIGHTABILITY_REQUIREMENT,
    COPYRIGHT_CLAUSE,
    IDEA_EXPRESSION_RULE,
)
from authorityspoke.opinions import (
    AnchoredHoldings,
    HoldingWithAnchors,
    TextPositionSet,
)


from legislice.groups import EnactmentGroup
from authorityspoke import Entity, Fact, Holding, Predicate, Rule
from authorityspoke.holdings import HoldingGroup
from authorityspoke.procedures import Procedure

HOLDINGS = HoldingGroup(holdings=[])
ENTITIES: dict[str, Entity] = {
    "rural_s_telephone_directory": Entity(
        name="Rural's telephone directory", generic=True, plural=False
    ),
    "rural_telephone_service_company": Entity(
        name="Rural Telephone Service Company", generic=True, plural=False
    ),
    "feist_publications": Entity(name="Feist Publications", generic=True, plural=False),
    "feist_s_telephone_directory": Entity(
        name="Feist's telephone directory", generic=True, plural=False
    ),
    "rural_s_telephone_listings": Entity(
        name="Rural's telephone listings", generic=True, plural=True
    ),
    "rural_s_arragement_of_its_telephone_listings": Entity(
        name="Rural's arragement of its telephone listings", generic=True, plural=False
    ),
}


_FACT_FALSE_DIRECTORY_COPYRIGHTABLE = Fact(
    predicate=Predicate(
        content="${rural_s_telephone_directory} was copyrightable", truth=False
    ),
    terms=[ENTITIES["rural_s_telephone_directory"]],
    name="false Rural's telephone directory was copyrightable",
    generic=False,
)
_FACT_DIRECTORY_IS_FACT = Fact(
    predicate=Predicate(content="${rural_s_telephone_directory} was a fact"),
    terms=[ENTITIES["rural_s_telephone_directory"]],
    name="Rural's telephone directory was a fact",
    generic=False,
)
_FACT_DIRECTORY_COPYRIGHTABLE = Fact(
    predicate=Predicate(content="${rural_s_telephone_directory} was copyrightable"),
    terms=[ENTITIES["rural_s_telephone_directory"]],
    name="Rural's telephone directory was copyrightable",
    generic=False,
)
_FACT_DIRECTORY_COMPILATION = Fact(
    predicate=Predicate(
        content="${rural_s_telephone_directory} was a compilation of facts"
    ),
    terms=[ENTITIES["rural_s_telephone_directory"]],
    name="Rural's telephone directory was a compilation of facts",
    generic=False,
)
_FACT_DIRECTORY_IDEA = Fact(
    predicate=Predicate(content="${rural_s_telephone_directory} was an idea"),
    terms=[ENTITIES["rural_s_telephone_directory"]],
    name="Rural's telephone directory was an idea",
    generic=False,
)
_FACT_DIRECTORY_ORIGINAL = Fact(
    predicate=Predicate(content="${rural_s_telephone_directory} was an original work"),
    terms=[ENTITIES["rural_s_telephone_directory"]],
    name="Rural's telephone directory was an original work",
    generic=False,
)
_FACT_DIRECTORY_INDEPENDENTLY_CREATED = Fact(
    predicate=Predicate(
        content="${rural_s_telephone_directory} was independently created by {rural_telephone_service_company}, as opposed to copied from other works"
    ),
    terms=[
        ENTITIES["rural_s_telephone_directory"],
        ENTITIES["rural_telephone_service_company"],
    ],
    name="Rural's telephone directory was independently created by Rural Telephone Service Company, as opposed to copied from other works",
    generic=False,
)
_FACT_DIRECTORY_MINIMAL_CREATIVITY = Fact(
    predicate=Predicate(
        content="${rural_s_telephone_directory} possessed at least some minimal degree of creativity"
    ),
    terms=[ENTITIES["rural_s_telephone_directory"]],
    name="Rural's telephone directory possessed at least some minimal degree of creativity",
    generic=False,
)
_FACT_DIRECTORY_RESEMBLED_OTHERS = Fact(
    predicate=Predicate(
        content="${rural_s_telephone_directory} closely resembled other works"
    ),
    terms=[ENTITIES["rural_s_telephone_directory"]],
    name="Rural's telephone directory closely resembled other works",
    generic=False,
)
_FACT_FALSE_DIRECTORY_ORIGINAL = Fact(
    predicate=Predicate(
        content="${rural_s_telephone_directory} was an original work", truth=False
    ),
    terms=[ENTITIES["rural_s_telephone_directory"]],
    name="false Rural's telephone directory was an original work",
    generic=False,
)
_FACT_COMPANY_COMPILER = Fact(
    predicate=Predicate(
        content="${rural_telephone_service_company} was the compiler of {rural_s_telephone_directory}"
    ),
    terms=[
        ENTITIES["rural_telephone_service_company"],
        ENTITIES["rural_s_telephone_directory"],
    ],
    name="Rural Telephone Service Company was the compiler of Rural's telephone directory",
    generic=False,
)
_FACT_COMPANY_CREATIVE_CHOICE_FACTS = Fact(
    predicate=Predicate(
        content="${rural_telephone_service_company} independently used a degree of creativity to choose which facts to include in {rural_s_telephone_directory}"
    ),
    terms=[
        ENTITIES["rural_telephone_service_company"],
        ENTITIES["rural_s_telephone_directory"],
    ],
    name="Rural Telephone Service Company independently used a degree of creativity to choose which facts to include in Rural's telephone directory",
    generic=False,
)
_FACT_COMPANY_CREATIVE_ARRANGEMENT = Fact(
    predicate=Predicate(
        content="${rural_telephone_service_company} independently used a degree of creativity to choose in what order to place the facts in {rural_s_telephone_directory}, and how to arrange the collected data so that they could be used effectively by readers"
    ),
    terms=[
        ENTITIES["rural_telephone_service_company"],
        ENTITIES["rural_s_telephone_directory"],
    ],
    name="Rural Telephone Service Company independently used a degree of creativity to choose in what order to place the facts in Rural's telephone directory, and how to arrange the collected data so that they could be used effectively by readers",
    generic=False,
)
_FACT_FALSE_DIRECTORY_PROTECTABLE_EXPRESSION = Fact(
    predicate=Predicate(
        content="${rural_s_telephone_directory} contained written expression protectable by copyright",
        truth=False,
    ),
    terms=[ENTITIES["rural_s_telephone_directory"]],
    name="false Rural's telephone directory contained written expression protectable by copyright",
    generic=False,
)
_FACT_FALSE_FEIST_INFRINGED = Fact(
    predicate=Predicate(
        content="${feist_publications} infringed the copyright on {rural_s_telephone_directory}",
        truth=False,
    ),
    terms=[
        ENTITIES["feist_publications"],
        ENTITIES["rural_s_telephone_directory"],
    ],
    name="false Feist Publications infringed the copyright on Rural's telephone directory",
    generic=False,
)
_FACT_FEIST_DIFFERENT_SELECTION = Fact(
    predicate=Predicate(
        content="${feist_s_telephone_directory} did not feature the same selection and arrangement of facts as {rural_s_telephone_directory}"
    ),
    terms=[
        ENTITIES["feist_s_telephone_directory"],
        ENTITIES["rural_s_telephone_directory"],
    ],
    name="Feist's telephone directory did not feature the same selection and arrangement of facts as Rural's telephone directory",
    generic=False,
)
_FACT_FEIST_COPIED_FACTS = Fact(
    predicate=Predicate(
        content="${feist_publications} freely copied the facts contained in {rural_s_telephone_directory}, in preparing {feist_s_telephone_directory}"
    ),
    terms=[
        ENTITIES["feist_publications"],
        ENTITIES["rural_s_telephone_directory"],
        ENTITIES["feist_s_telephone_directory"],
    ],
    name="Feist Publications freely copied the facts contained in Rural's telephone directory, in preparing Feist's telephone directory",
    generic=False,
)
_FACT_FALSE_LISTINGS_ORIGINAL = Fact(
    predicate=Predicate(
        content="${rural_s_telephone_listings} were an original work", truth=False
    ),
    terms=[ENTITIES["rural_s_telephone_listings"]],
    name="false Rural's telephone listings were an original work",
    generic=False,
)
_FACT_LISTINGS_ARE_NAMES_TOWNS_NUMBERS = Fact(
    predicate=Predicate(
        content="${rural_s_telephone_listings} were names, towns, and telephone numbers of telephone subscribers"
    ),
    terms=[ENTITIES["rural_s_telephone_listings"]],
    name="Rural's telephone listings were names, towns, and telephone numbers of telephone subscribers",
    generic=False,
)
_FACT_FALSE_ARRANGEMENT_ORIGINAL = Fact(
    predicate=Predicate(
        content="${rural_s_arragement_of_its_telephone_listings} was an original work",
        truth=False,
    ),
    terms=[ENTITIES["rural_s_arragement_of_its_telephone_listings"]],
    name="false Rural's arragement of its telephone listings was an original work",
    generic=False,
)
_FACT_DIRECTORY_IS_TELEPHONE_DIRECTORY = Fact(
    predicate=Predicate(
        content="${rural_s_telephone_directory} was a telephone directory"
    ),
    terms=[ENTITIES["rural_s_telephone_directory"]],
    name="Rural's telephone directory was a telephone directory",
    generic=False,
)
_FACT_ARRANGEMENT_IS_ALPHABETICAL_METHOD = Fact(
    predicate=Predicate(
        content="${rural_s_arragement_of_its_telephone_listings} was the method of listing subscribers alphabetically by surname in {rural_s_telephone_directory}"
    ),
    terms=[
        ENTITIES["rural_s_arragement_of_its_telephone_listings"],
        ENTITIES["rural_s_telephone_directory"],
    ],
    name="Rural's arragement of its telephone listings was the method of listing subscribers alphabetically by surname in Rural's telephone directory",
    generic=False,
)

FACTS: list[Fact] = [
    _FACT_FALSE_DIRECTORY_COPYRIGHTABLE,
    _FACT_DIRECTORY_IS_FACT,
    _FACT_DIRECTORY_COPYRIGHTABLE,
    _FACT_DIRECTORY_COMPILATION,
    _FACT_DIRECTORY_IDEA,
    _FACT_DIRECTORY_ORIGINAL,
    _FACT_DIRECTORY_INDEPENDENTLY_CREATED,
    _FACT_DIRECTORY_MINIMAL_CREATIVITY,
    _FACT_DIRECTORY_RESEMBLED_OTHERS,
    _FACT_FALSE_DIRECTORY_ORIGINAL,
    _FACT_COMPANY_COMPILER,
    _FACT_COMPANY_CREATIVE_CHOICE_FACTS,
    _FACT_COMPANY_CREATIVE_ARRANGEMENT,
    _FACT_FALSE_DIRECTORY_PROTECTABLE_EXPRESSION,
    _FACT_FALSE_FEIST_INFRINGED,
    _FACT_FEIST_DIFFERENT_SELECTION,
    _FACT_FEIST_COPIED_FACTS,
    _FACT_FALSE_LISTINGS_ORIGINAL,
    _FACT_LISTINGS_ARE_NAMES_TOWNS_NUMBERS,
    _FACT_FALSE_ARRANGEMENT_ORIGINAL,
    _FACT_DIRECTORY_IS_TELEPHONE_DIRECTORY,
    _FACT_ARRANGEMENT_IS_ALPHABETICAL_METHOD,
]


def _build_holdings() -> HoldingGroup:
    facts = {fact.name: fact for fact in FACTS}

    def enactments(*passages):
        return EnactmentGroup(passages=[copy.deepcopy(passage) for passage in passages])

    holdings = [
        Holding(
            rule=Rule(
                procedure=Procedure(
                    inputs=[facts["Rural's telephone directory was a fact"]],
                    outputs=[
                        facts["false Rural's telephone directory was copyrightable"]
                    ],
                ),
                enactments=enactments(COPYRIGHT_CLAUSE, COMPILATION_COPYRIGHT_RULE),
                mandatory=True,
                universal=True,
            )
        ),
        Holding(
            rule=Rule(
                procedure=Procedure(
                    inputs=[
                        facts["Rural's telephone directory was a compilation of facts"]
                    ],
                    outputs=[facts["Rural's telephone directory was copyrightable"]],
                ),
                enactments=enactments(COPYRIGHT_CLAUSE),
                mandatory=True,
                universal=False,
            )
        ),
        Holding(
            rule=Rule(
                procedure=Procedure(
                    inputs=[facts["Rural's telephone directory was an idea"]],
                    outputs=[
                        facts["false Rural's telephone directory was copyrightable"]
                    ],
                ),
                enactments=enactments(COPYRIGHT_CLAUSE),
                mandatory=True,
                universal=True,
            )
        ),
        Holding(
            rule=Rule(
                procedure=Procedure(
                    inputs=[facts["Rural's telephone directory was an original work"]],
                    outputs=[facts["Rural's telephone directory was copyrightable"]],
                ),
                enactments=enactments(COPYRIGHT_CLAUSE, COPYRIGHTABILITY_REQUIREMENT),
                mandatory=False,
                universal=False,
            ),
            exclusive=True,
        ),
        Holding(
            rule=Rule(
                procedure=Procedure(
                    inputs=[
                        facts[
                            "Rural's telephone directory was independently created by Rural Telephone Service Company, as opposed to copied from other works"
                        ],
                        facts[
                            "Rural's telephone directory possessed at least some minimal degree of creativity"
                        ],
                    ],
                    despite=[
                        facts[
                            "Rural's telephone directory closely resembled other works"
                        ]
                    ],
                    outputs=[facts["Rural's telephone directory was an original work"]],
                ),
                enactments=enactments(COPYRIGHT_CLAUSE),
                mandatory=False,
                universal=True,
            )
        ),
        Holding(
            rule=Rule(
                procedure=Procedure(
                    inputs=[facts["Rural's telephone directory was a fact"]],
                    outputs=[
                        facts["false Rural's telephone directory was an original work"]
                    ],
                ),
                enactments=enactments(COPYRIGHT_CLAUSE, IDEA_EXPRESSION_RULE),
                mandatory=True,
                universal=True,
            )
        ),
        Holding(
            rule=Rule(
                procedure=Procedure(
                    inputs=[
                        facts["Rural's telephone directory was a compilation of facts"],
                        facts[
                            "Rural Telephone Service Company was the compiler of Rural's telephone directory"
                        ],
                        facts[
                            "Rural Telephone Service Company independently used a degree of creativity to choose which facts to include in Rural's telephone directory"
                        ],
                        facts[
                            "Rural Telephone Service Company independently used a degree of creativity to choose in what order to place the facts in Rural's telephone directory, and how to arrange the collected data so that they could be used effectively by readers"
                        ],
                    ],
                    outputs=[facts["Rural's telephone directory was an original work"]],
                ),
                enactments=enactments(COPYRIGHT_CLAUSE),
                mandatory=False,
                universal=False,
            )
        ),
        Holding(
            rule=Rule(
                procedure=Procedure(
                    inputs=[
                        facts["Rural's telephone directory was a compilation of facts"],
                        facts[
                            "false Rural's telephone directory contained written expression protectable by copyright"
                        ],
                    ],
                    despite=[
                        facts[
                            "Rural Telephone Service Company independently used a degree of creativity to choose which facts to include in Rural's telephone directory"
                        ],
                        facts[
                            "Rural Telephone Service Company independently used a degree of creativity to choose in what order to place the facts in Rural's telephone directory, and how to arrange the collected data so that they could be used effectively by readers"
                        ],
                    ],
                    outputs=[
                        facts["false Rural's telephone directory was copyrightable"]
                    ],
                ),
                enactments=enactments(COPYRIGHT_CLAUSE),
                mandatory=False,
                universal=True,
            ),
            rule_valid=False,
        ),
        Holding(
            rule=Rule(
                procedure=Procedure(
                    inputs=[
                        facts["Rural's telephone directory was a compilation of facts"],
                        facts[
                            "Feist's telephone directory did not feature the same selection and arrangement of facts as Rural's telephone directory"
                        ],
                    ],
                    despite=[
                        facts["Rural's telephone directory was copyrightable"],
                        facts[
                            "Feist Publications freely copied the facts contained in Rural's telephone directory, in preparing Feist's telephone directory"
                        ],
                    ],
                    outputs=[
                        facts[
                            "false Feist Publications infringed the copyright on Rural's telephone directory"
                        ]
                    ],
                ),
                enactments=enactments(COPYRIGHT_CLAUSE, COMPILATION_COPYRIGHT_RULE),
                mandatory=False,
                universal=False,
            )
        ),
        Holding(
            rule=Rule(
                procedure=Procedure(
                    inputs=[
                        facts["Rural's telephone directory was a compilation of facts"]
                    ],
                    outputs=[
                        facts["false Rural's telephone directory was copyrightable"]
                    ],
                ),
                enactments=enactments(COPYRIGHT_CLAUSE, COMPILATION_COPYRIGHT_RULE),
                mandatory=False,
                universal=False,
            )
        ),
        Holding(
            rule=Rule(
                procedure=Procedure(
                    inputs=[
                        facts[
                            "Rural's telephone listings were names, towns, and telephone numbers of telephone subscribers"
                        ]
                    ],
                    outputs=[
                        facts["false Rural's telephone listings were an original work"]
                    ],
                ),
                enactments=enactments(
                    COPYRIGHT_CLAUSE,
                    COPYRIGHTABILITY_REQUIREMENT,
                    COMPILATION_COPYRIGHT_RULE,
                ),
                mandatory=False,
                universal=False,
            )
        ),
        Holding(
            rule=Rule(
                procedure=Procedure(
                    inputs=[
                        facts["Rural's telephone directory was a telephone directory"],
                        facts[
                            "Rural's arragement of its telephone listings was the method of listing subscribers alphabetically by surname in Rural's telephone directory"
                        ],
                    ],
                    outputs=[
                        facts[
                            "false Rural's arragement of its telephone listings was an original work"
                        ]
                    ],
                ),
                enactments=enactments(COPYRIGHT_CLAUSE, COMPILATION_COPYRIGHT_RULE),
                mandatory=False,
                universal=False,
            )
        ),
    ]

    return HoldingGroup(holdings)


HOLDINGS = _build_holdings()

ANCHORS: list[TextPositionSet] = [
    TextPositionSet(positions=[], quotes=[]),
    TextPositionSet(
        positions=[],
        quotes=[
            {
                "exact": "generally are",
                "prefix": "compilations of facts",
                "suffix": "",
            }
        ],
    ),
    TextPositionSet(positions=[], quotes=[]),
    TextPositionSet(
        positions=[],
        quotes=[
            {
                "exact": "The sine qua non of",
                "prefix": "",
                "suffix": "copyright",
            }
        ],
    ),
    TextPositionSet(
        positions=[],
        quotes=[
            {"exact": "means only that", "prefix": "", "suffix": ""},
        ],
    ),
    TextPositionSet(
        positions=[],
        quotes=[
            {
                "exact": "The end product is a garden-variety white pages directory, devoid of even the slightest trace of creativity.",
                "prefix": "",
                "suffix": "",
            },
            {
                "exact": "Rural’s selection of listings could not be more obvious: It publishes the most basic information — name, town, and telephone number — about each person who applies to it for telephone service. This is “selection” of a sort, but it lacks the modicum of creativity necessary to transform mere selection into copyrightable expression.",
                "prefix": "",
                "suffix": "",
            },
        ],
    ),
    TextPositionSet(
        positions=[],
        quotes=[
            {
                "exact": "trigger",
                "prefix": "Census data therefore do not",
                "suffix": "copyright",
            },
            {
                "exact": "may",
                "prefix": "",
                "suffix": "possess the requisite originality",
            },
        ],
    ),
    TextPositionSet(positions=[], quotes=[]),
    TextPositionSet(positions=[], quotes=[]),
    TextPositionSet(positions=[], quotes=[]),
    TextPositionSet(positions=[], quotes=[]),
    TextPositionSet(positions=[], quotes=[]),
]

NAMED_ANCHORS = [
    {
        "term": next(
            fact
            for fact in FACTS
            if fact.name == "Rural's telephone directory was an idea"
        ),
        "anchors": TextPositionSet(
            positions=[],
            quotes=[
                {
                    "exact": "ideas",
                    "prefix": "no one may copyright facts or",
                    "suffix": "",
                }
            ],
        ),
    }
]


def anchored_holdings() -> AnchoredHoldings:
    """Build AnchoredHoldings from this module's HOLDINGS collection."""
    return AnchoredHoldings(
        holdings=[
            HoldingWithAnchors(
                holding=copy.deepcopy(holding),
                anchors=copy.deepcopy(ANCHORS[index]),
            )
            for index, holding in enumerate(HOLDINGS)
        ],
        named_anchors=copy.deepcopy(NAMED_ANCHORS),
        enactment_anchors=[],
    )
