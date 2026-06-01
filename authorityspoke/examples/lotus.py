import copy

from anchorpoint.textselectors import TextQuoteSelector
from authorityspoke.examples.legislation import (
    COPYRIGHTABILITY_REQUIREMENT,
    COPYRIGHT_REGISTRATION_EVIDENCE_RULE,
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
from authorityspoke.facts import (
    AbsenceOfFactor,
    Evidence,
    Exhibit,
)
from authorityspoke.procedures import Procedure

HOLDINGS = HoldingGroup(holdings=[])
ENTITIES: dict[str, Entity] = {
    "borland_international": Entity(
        name="Borland International", generic=True, plural=False
    ),
    "the_lotus_menu_command_hierarchy": Entity(
        name="the Lotus menu command hierarchy", generic=True, plural=False
    ),
    "lotus_development_corporation": Entity(
        name="Lotus Development Corporation", generic=True, plural=False
    ),
    "quattro_s_lotus_emulation_interface": Entity(
        name="Quattro's Lotus Emulation Interface", generic=True, plural=False
    ),
    "lotus_1_2_3": Entity(name="Lotus 1-2-3", generic=True, plural=False),
}

_FACT_HIERARCHY_COPYRIGHTABLE = Fact(
    predicate=Predicate(content="{the_lotus_menu_command_hierarchy} was copyrightable"),
    terms=[ENTITIES["the_lotus_menu_command_hierarchy"]],
    name="the Lotus menu command hierarchy was copyrightable",
    generic=False,
)
_FACT_COPIED_CONSTITUENT_ORIGINAL = Fact(
    predicate=Predicate(
        content="{borland_international} copied constituent elements of {the_lotus_menu_command_hierarchy} that were original"
    ),
    terms=[
        ENTITIES["borland_international"],
        ENTITIES["the_lotus_menu_command_hierarchy"],
    ],
    name="Borland International copied constituent elements of the Lotus menu command hierarchy that were original",
    generic=False,
)
_FACT_INFRINGED_COPYRIGHT = Fact(
    predicate=Predicate(
        content="{borland_international} infringed the copyright in {the_lotus_menu_command_hierarchy}"
    ),
    terms=[
        ENTITIES["borland_international"],
        ENTITIES["the_lotus_menu_command_hierarchy"],
    ],
    name="Borland International infringed the copyright in the Lotus menu command hierarchy",
    generic=False,
)
_FACT_HIERARCHY_ORIGINAL = Fact(
    predicate=Predicate(
        content="{the_lotus_menu_command_hierarchy} was an original work"
    ),
    terms=[ENTITIES["the_lotus_menu_command_hierarchy"]],
    name="the Lotus menu command hierarchy was an original work",
    generic=False,
)
_FACT_FALSE_HIERARCHY_COPYRIGHTABLE = Fact(
    predicate=Predicate(
        content="{the_lotus_menu_command_hierarchy} was copyrightable", truth=False
    ),
    terms=[ENTITIES["the_lotus_menu_command_hierarchy"]],
    name="false the Lotus menu command hierarchy was copyrightable",
    generic=False,
)
_FACT_REGISTERED_COPYRIGHT = Fact(
    predicate=Predicate(
        content="{lotus_development_corporation} registered a copyright covering {the_lotus_menu_command_hierarchy}"
    ),
    terms=[
        ENTITIES["lotus_development_corporation"],
        ENTITIES["the_lotus_menu_command_hierarchy"],
    ],
    name="Lotus Development Corporation registered a copyright covering the Lotus menu command hierarchy",
    generic=False,
)
_FACT_COPIED_IN_CREATING_QUATTRO_INTERFACE = Fact(
    predicate=Predicate(
        content="{borland_international} copied {the_lotus_menu_command_hierarchy} in creating Quattro's Lotus Emulation Interface"
    ),
    terms=[
        ENTITIES["borland_international"],
        ENTITIES["the_lotus_menu_command_hierarchy"],
    ],
    name="Borland International copied the Lotus menu command hierarchy in creating Quattro's Lotus Emulation Interface",
    generic=False,
)
_FACT_HAD_ACCESS_TO_HIERARCHY = Fact(
    predicate=Predicate(
        content="{borland_international} had access to {the_lotus_menu_command_hierarchy}"
    ),
    terms=[
        ENTITIES["borland_international"],
        ENTITIES["the_lotus_menu_command_hierarchy"],
    ],
    name="Borland International had access to the Lotus menu command hierarchy",
    generic=False,
)
_FACT_PUBLISHED_QUATTRO_INTERFACE = Fact(
    predicate=Predicate(
        content="{borland_international} published {quattro_s_lotus_emulation_interface}"
    ),
    terms=[
        ENTITIES["borland_international"],
        ENTITIES["quattro_s_lotus_emulation_interface"],
    ],
    name="Borland International published Quattro's Lotus Emulation Interface",
    generic=False,
)
_FACT_QUATTRO_VERY_SIMILAR_TO_HIERARCHY = Fact(
    predicate=Predicate(
        content="{quattro_s_lotus_emulation_interface} was very similar to {the_lotus_menu_command_hierarchy}"
    ),
    terms=[
        ENTITIES["quattro_s_lotus_emulation_interface"],
        ENTITIES["the_lotus_menu_command_hierarchy"],
    ],
    name="Quattro's Lotus Emulation Interface was very similar to the Lotus menu command hierarchy",
    generic=False,
)
_FACT_COPYING_EXTENSIVE_SIMILAR = Fact(
    predicate=Predicate(
        content="the copying of {quattro_s_lotus_emulation_interface} in {the_lotus_menu_command_hierarchy} was so extensive that it rendered them substantially similar"
    ),
    terms=[
        ENTITIES["quattro_s_lotus_emulation_interface"],
        ENTITIES["the_lotus_menu_command_hierarchy"],
    ],
    name="the copying of Quattro's Lotus Emulation Interface in the Lotus menu command hierarchy was so extensive that it rendered them substantially similar",
    generic=False,
)
_FACT_HIERARCHY_METHOD_OF_OPERATION = Fact(
    predicate=Predicate(
        content="{the_lotus_menu_command_hierarchy} was a method of operation"
    ),
    terms=[ENTITIES["the_lotus_menu_command_hierarchy"]],
    name="the Lotus menu command hierarchy was a method of operation",
    generic=False,
)
_FACT_TEXT_DESCRIBED_HIERARCHY = Fact(
    predicate=Predicate(content="a text described {the_lotus_menu_command_hierarchy}"),
    terms=[ENTITIES["the_lotus_menu_command_hierarchy"]],
    name="a text described the Lotus menu command hierarchy",
    generic=False,
)
_FACT_LOTUS_PROGRAM = Fact(
    predicate=Predicate(content="{lotus_1_2_3} was a computer program"),
    terms=[ENTITIES["lotus_1_2_3"]],
    name="Lotus 1-2-3 was a computer program",
    generic=False,
)
_FACT_HIERARCHY_PROVIDED_MEANS = Fact(
    predicate=Predicate(
        content="{the_lotus_menu_command_hierarchy} provided the means by which users controlled and operated {lotus_1_2_3}"
    ),
    terms=[ENTITIES["the_lotus_menu_command_hierarchy"], ENTITIES["lotus_1_2_3"]],
    name="the Lotus menu command hierarchy provided the means by which users controlled and operated Lotus 1-2-3",
    generic=False,
)
_FACT_WITHOUT_HIERARCHY_NO_ACCESS = Fact(
    predicate=Predicate(
        content="without {the_lotus_menu_command_hierarchy}, users would not have been able to access and control, or indeed make use of, {lotus_1_2_3}’s functional capabilities"
    ),
    terms=[ENTITIES["the_lotus_menu_command_hierarchy"], ENTITIES["lotus_1_2_3"]],
    name="without the Lotus menu command hierarchy, users would not have been able to access and control, or indeed make use of, Lotus 1-2-3’s functional capabilities",
    generic=False,
)
_FACT_OTHER_PROGRAM_WOULD_HAVE_TO_COPY = Fact(
    predicate=Predicate(
        content="for another computer program to be operated in substantially the same way as {lotus_1_2_3}, the other program would have to copy {the_lotus_menu_command_hierarchy}"
    ),
    terms=[ENTITIES["lotus_1_2_3"], ENTITIES["the_lotus_menu_command_hierarchy"]],
    name="for another computer program to be operated in substantially the same way as Lotus 1-2-3, the other program would have to copy the Lotus menu command hierarchy",
    generic=False,
)
_FACT_DEVS_MADE_EXPRESSIVE_CHOICES = Fact(
    predicate=Predicate(
        content="the developers of {lotus_1_2_3} made some expressive choices in choosing and arranging the terms in {the_lotus_menu_command_hierarchy}"
    ),
    terms=[ENTITIES["lotus_1_2_3"], ENTITIES["the_lotus_menu_command_hierarchy"]],
    name="the developers of Lotus 1-2-3 made some expressive choices in choosing and arranging the terms in the Lotus menu command hierarchy",
    generic=False,
)
_FACT_HIERARCHY_MEANS_BY_WHICH_PERSON_OPERATED = Fact(
    predicate=Predicate(
        content="{the_lotus_menu_command_hierarchy} was the means by which a person operated {lotus_1_2_3}"
    ),
    terms=[ENTITIES["the_lotus_menu_command_hierarchy"], ENTITIES["lotus_1_2_3"]],
    name="the Lotus menu command hierarchy was the means by which a person operated Lotus 1-2-3",
    generic=False,
)
_FACT_FALSE_HIERARCHY_ABSTRACTION = Fact(
    predicate=Predicate(
        content="{the_lotus_menu_command_hierarchy} was an abstraction", truth=False
    ),
    terms=[ENTITIES["the_lotus_menu_command_hierarchy"]],
    name="false the Lotus menu command hierarchy was an abstraction",
    generic=False,
)
_FACT_FALSE_PRECISE_FORMULATION_NECESSARY = Fact(
    predicate=Predicate(
        content="the precise formulation of {lotus_1_2_3}'s code was necessary for {lotus_1_2_3} to work",
        truth=False,
    ),
    terms=[ENTITIES["lotus_1_2_3"]],
    name="false the precise formulation of Lotus 1-2-3's code was necessary for Lotus 1-2-3 to work",
    generic=False,
)
_FACT_COMPUTER_CODE_NECESSARY = Fact(
    predicate=Predicate(
        content="computer code was necessary for {lotus_1_2_3} to work"
    ),
    terms=[ENTITIES["lotus_1_2_3"]],
    name="computer code was necessary for Lotus 1-2-3 to work",
    generic=False,
)
_FACT_FALSE_PROGRAM_METHOD_OF_OPERATION = Fact(
    predicate=Predicate(content="{lotus_1_2_3} was a method of operation", truth=False),
    terms=[ENTITIES["lotus_1_2_3"]],
    name="false Lotus 1-2-3 was a method of operation",
    generic=False,
)

FACTS: list[Fact] = [
    _FACT_HIERARCHY_COPYRIGHTABLE,
    _FACT_COPIED_CONSTITUENT_ORIGINAL,
    _FACT_INFRINGED_COPYRIGHT,
    _FACT_HIERARCHY_ORIGINAL,
    _FACT_FALSE_HIERARCHY_COPYRIGHTABLE,
    _FACT_REGISTERED_COPYRIGHT,
    _FACT_COPIED_IN_CREATING_QUATTRO_INTERFACE,
    _FACT_HAD_ACCESS_TO_HIERARCHY,
    _FACT_PUBLISHED_QUATTRO_INTERFACE,
    _FACT_QUATTRO_VERY_SIMILAR_TO_HIERARCHY,
    _FACT_COPYING_EXTENSIVE_SIMILAR,
    _FACT_HIERARCHY_METHOD_OF_OPERATION,
    _FACT_TEXT_DESCRIBED_HIERARCHY,
    _FACT_LOTUS_PROGRAM,
    _FACT_HIERARCHY_PROVIDED_MEANS,
    _FACT_WITHOUT_HIERARCHY_NO_ACCESS,
    _FACT_OTHER_PROGRAM_WOULD_HAVE_TO_COPY,
    _FACT_DEVS_MADE_EXPRESSIVE_CHOICES,
    _FACT_HIERARCHY_MEANS_BY_WHICH_PERSON_OPERATED,
    _FACT_FALSE_HIERARCHY_ABSTRACTION,
    _FACT_FALSE_PRECISE_FORMULATION_NECESSARY,
    _FACT_COMPUTER_CODE_NECESSARY,
    _FACT_FALSE_PROGRAM_METHOD_OF_OPERATION,
]


def _build_holdings() -> HoldingGroup:
    facts = {fact.name: fact for fact in FACTS}

    lotus_copyrightability_requirement = copy.deepcopy(COPYRIGHTABILITY_REQUIREMENT)
    lotus_copyrightability_requirement.selection = TextPositionSet(
        quotes=[
            TextQuoteSelector(
                exact="",
                prefix="",
                suffix="Works of authorship include",
            )
        ]
    )

    lotus_idea_expression_rule = copy.deepcopy(IDEA_EXPRESSION_RULE)
    lotus_idea_expression_rule.selection = TextPositionSet(
        quotes=[
            TextQuoteSelector(
                exact="",
                prefix="",
                suffix="idea, procedure, process",
            ),
            TextQuoteSelector(
                exact="method of operation",
                prefix="",
                suffix="",
            ),
        ]
    )

    exhibit_offered_by_lotus = Exhibit(
        offered_by=ENTITIES["lotus_development_corporation"],
        name="{'offered_by': 'Lotus Development Corporation'}",
        generic=False,
    )
    lotus_registration = Exhibit(
        offered_by=ENTITIES["lotus_development_corporation"],
        form="certificate of copyright registration",
        name="Lotus's copyright registration",
        generic=False,
    )

    absence_hierarchy_original = AbsenceOfFactor(
        absent=facts["the Lotus menu command hierarchy was an original work"],
        generic=False,
    )
    absence_hierarchy_copyrightable = AbsenceOfFactor(
        absent=facts["the Lotus menu command hierarchy was copyrightable"],
        generic=False,
    )
    absence_false_hierarchy_copyrightable = AbsenceOfFactor(
        absent=facts["false the Lotus menu command hierarchy was copyrightable"],
        generic=False,
    )

    evidence_lotus_registration = Evidence(
        exhibit=lotus_registration,
        to_effect=facts[
            "Lotus Development Corporation registered a copyright covering the Lotus menu command hierarchy"
        ],
        name="evidence of Lotus's copyright registration",
        generic=False,
    )
    evidence_copied_in_creating_interface = Evidence(
        exhibit=exhibit_offered_by_lotus,
        to_effect=facts[
            "Borland International copied the Lotus menu command hierarchy in creating Quattro's Lotus Emulation Interface"
        ],
        name="evidence of {'offered_by': 'Lotus Development Corporation'} to the effect that Borland International copied the Lotus menu command hierarchy in creating Quattro's Lotus Emulation Interface",
        generic=False,
    )
    evidence_had_access_to_hierarchy = Evidence(
        exhibit=exhibit_offered_by_lotus,
        to_effect=facts[
            "Borland International had access to the Lotus menu command hierarchy"
        ],
        name="evidence of {'offered_by': 'Lotus Development Corporation'} to the effect that Borland International had access to the Lotus menu command hierarchy",
        generic=False,
    )
    evidence_quattro_very_similar = Evidence(
        exhibit=exhibit_offered_by_lotus,
        to_effect=facts[
            "Quattro's Lotus Emulation Interface was very similar to the Lotus menu command hierarchy"
        ],
        name="evidence of {'offered_by': 'Lotus Development Corporation'} to the effect that Quattro's Lotus Emulation Interface was very similar to the Lotus menu command hierarchy",
        generic=False,
    )

    def enactments(*passages):
        return EnactmentGroup(passages=[copy.deepcopy(passage) for passage in passages])

    holdings = [
        Holding(
            rule=Rule(
                procedure=Procedure(
                    inputs=[
                        facts["the Lotus menu command hierarchy was copyrightable"],
                        facts[
                            "Borland International copied constituent elements of the Lotus menu command hierarchy that were original"
                        ],
                    ],
                    outputs=[
                        facts[
                            "Borland International infringed the copyright in the Lotus menu command hierarchy"
                        ]
                    ],
                ),
                enactments=enactments(lotus_copyrightability_requirement),
                mandatory=False,
                universal=False,
            ),
            exclusive=True,
        ),
        Holding(
            rule=Rule(
                procedure=Procedure(
                    inputs=[absence_hierarchy_original],
                    outputs=[absence_hierarchy_copyrightable],
                ),
                enactments=enactments(lotus_copyrightability_requirement),
                mandatory=False,
                universal=True,
            )
        ),
        Holding(
            rule=Rule(
                procedure=Procedure(
                    inputs=[
                        evidence_lotus_registration,
                        absence_false_hierarchy_copyrightable,
                    ],
                    outputs=[
                        facts["the Lotus menu command hierarchy was copyrightable"]
                    ],
                ),
                enactments=enactments(COPYRIGHT_REGISTRATION_EVIDENCE_RULE),
                mandatory=False,
                universal=False,
            )
        ),
        Holding(
            rule=Rule(
                procedure=Procedure(
                    inputs=[evidence_copied_in_creating_interface],
                    outputs=[
                        facts[
                            "Borland International copied the Lotus menu command hierarchy in creating Quattro's Lotus Emulation Interface"
                        ]
                    ],
                ),
                enactments=enactments(lotus_copyrightability_requirement),
                mandatory=False,
                universal=False,
            )
        ),
        Holding(
            rule=Rule(
                procedure=Procedure(
                    inputs=[
                        evidence_had_access_to_hierarchy,
                        facts[
                            "Borland International published Quattro's Lotus Emulation Interface"
                        ],
                        evidence_quattro_very_similar,
                    ],
                    outputs=[
                        facts[
                            "Borland International copied the Lotus menu command hierarchy in creating Quattro's Lotus Emulation Interface"
                        ]
                    ],
                ),
                enactments=enactments(lotus_copyrightability_requirement),
                mandatory=False,
                universal=False,
            )
        ),
        Holding(
            rule=Rule(
                procedure=Procedure(
                    inputs=[
                        facts[
                            "Borland International copied the Lotus menu command hierarchy in creating Quattro's Lotus Emulation Interface"
                        ],
                        facts[
                            "the copying of Quattro's Lotus Emulation Interface in the Lotus menu command hierarchy was so extensive that it rendered them substantially similar"
                        ],
                    ],
                    outputs=[
                        facts[
                            "Borland International copied constituent elements of the Lotus menu command hierarchy that were original"
                        ]
                    ],
                ),
                enactments=enactments(lotus_copyrightability_requirement),
                mandatory=False,
                universal=False,
            )
        ),
        Holding(
            rule=Rule(
                procedure=Procedure(
                    inputs=[
                        facts[
                            "the Lotus menu command hierarchy was a method of operation"
                        ]
                    ],
                    despite=[
                        facts["a text described the Lotus menu command hierarchy"],
                        facts["the Lotus menu command hierarchy was an original work"],
                    ],
                    outputs=[
                        facts[
                            "false the Lotus menu command hierarchy was copyrightable"
                        ]
                    ],
                ),
                enactments=enactments(lotus_idea_expression_rule),
                mandatory=True,
                universal=True,
            )
        ),
        Holding(
            rule=Rule(
                procedure=Procedure(
                    inputs=[
                        facts["Lotus 1-2-3 was a computer program"],
                        facts[
                            "the Lotus menu command hierarchy provided the means by which users controlled and operated Lotus 1-2-3"
                        ],
                        facts[
                            "without the Lotus menu command hierarchy, users would not have been able to access and control, or indeed make use of, Lotus 1-2-3’s functional capabilities"
                        ],
                        facts[
                            "for another computer program to be operated in substantially the same way as Lotus 1-2-3, the other program would have to copy the Lotus menu command hierarchy"
                        ],
                    ],
                    despite=[
                        facts[
                            "the developers of Lotus 1-2-3 made some expressive choices in choosing and arranging the terms in the Lotus menu command hierarchy"
                        ]
                    ],
                    outputs=[
                        facts[
                            "the Lotus menu command hierarchy was a method of operation"
                        ]
                    ],
                ),
                enactments=enactments(lotus_idea_expression_rule),
                mandatory=False,
                universal=False,
            )
        ),
        Holding(
            rule=Rule(
                procedure=Procedure(
                    inputs=[
                        facts[
                            "the Lotus menu command hierarchy was the means by which a person operated Lotus 1-2-3"
                        ]
                    ],
                    despite=[
                        facts[
                            "false the Lotus menu command hierarchy was an abstraction"
                        ]
                    ],
                    outputs=[
                        facts[
                            "the Lotus menu command hierarchy was a method of operation"
                        ]
                    ],
                ),
                enactments=enactments(lotus_idea_expression_rule),
                mandatory=False,
                universal=False,
            )
        ),
        Holding(
            rule=Rule(
                procedure=Procedure(
                    inputs=[
                        facts["Lotus 1-2-3 was a computer program"],
                        facts[
                            "false the precise formulation of Lotus 1-2-3's code was necessary for Lotus 1-2-3 to work"
                        ],
                    ],
                    despite=[
                        facts["computer code was necessary for Lotus 1-2-3 to work"]
                    ],
                    outputs=[facts["false Lotus 1-2-3 was a method of operation"]],
                ),
                enactments=enactments(lotus_idea_expression_rule),
                mandatory=False,
                universal=False,
            )
        ),
    ]

    return HoldingGroup(holdings)


HOLDINGS = _build_holdings()

ANCHORS: list[TextPositionSet] = [
    TextPositionSet(positions=[], quotes=[]),
    TextPositionSet(positions=[], quotes=[]),
    TextPositionSet(positions=[], quotes=[]),
    TextPositionSet(positions=[], quotes=[]),
    TextPositionSet(positions=[], quotes=[]),
    TextPositionSet(positions=[], quotes=[]),
    TextPositionSet(positions=[], quotes=[]),
    TextPositionSet(positions=[], quotes=[]),
    TextPositionSet(positions=[], quotes=[]),
    TextPositionSet(positions=[], quotes=[]),
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
        named_anchors=[],
        enactment_anchors=[],
    )
