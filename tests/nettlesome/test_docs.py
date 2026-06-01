from authorityspoke.nettlesome import Comparison, Entity, FactorGroup, Predicate, Statement


def test_context_guide_statements_can_have_same_meaning():
    hades_curse = Statement(
        predicate=Predicate(content="{deity} cursed {target}"),
        terms=[Entity(name="Hades"), Entity(name="Persephone")],
    )
    aphrodite_curse = Statement(
        predicate=Predicate(content="{deity} cursed {target}"),
        terms=[Entity(name="Aphrodite"), Entity(name="Narcissus")],
    )

    assert str(aphrodite_curse) == "the statement that <Aphrodite> cursed <Narcissus>"
    assert hades_curse.means(aphrodite_curse)


def test_intro_guide_false_predicate_string_representation():
    no_account_for_company = Predicate(
        content="{applicant} opened a bank account for {company}",
        truth=False,
    )

    assert (
        str(no_account_for_company)
        == "it was false that {applicant} opened a bank account for {company}"
    )


def test_terms_explain_same_meaning_doc_example():
    hades_curse = Statement.new(
        predicate="{deity} cursed {target}",
        terms=[Entity(name="Hades"), Entity(name="Persephone")],
    )
    aphrodite_curse = Statement.new(
        predicate="{deity} cursed {target}",
        terms=[Entity(name="Aphrodite"), Entity(name="Narcissus")],
    )

    assert str(hades_curse.explain_same_meaning(aphrodite_curse)) == (
        "Because <Hades> is like <Aphrodite>, and <Persephone> is like <Narcissus>,\n"
        "  the statement that <Hades> cursed <Persephone>\n"
        "MEANS\n"
        "  the statement that <Aphrodite> cursed <Narcissus>"
    )


def test_terms_implies_doc_example():
    over_100y = Comparison.new(
        content="the distance between {site1} and {site2} was",
        sign=">",
        expression="100 yards",
    )
    under_1mi = Comparison.new(
        content="the distance between {site1} and {site2} was",
        sign="<",
        expression="1 mile",
    )
    protest_facts = FactorGroup(
        sequence=[
            Statement(
                predicate=over_100y,
                terms=[
                    Entity(name="the political convention"),
                    Entity(name="the police cordon"),
                ],
            ),
            Statement(
                predicate=under_1mi,
                terms=[
                    Entity(name="the police cordon"),
                    Entity(name="the political convention"),
                ],
            ),
        ]
    )

    over_50m = Comparison.new(
        content="the distance between {site1} and {site2} was",
        sign=">",
        expression="50 meters",
    )
    under_2km = Comparison.new(
        content="the distance between {site1} and {site2} was",
        sign="<=",
        expression="2 km",
    )
    speech_zone_facts = FactorGroup(
        sequence=[
            Statement(
                predicate=over_50m,
                terms=[
                    Entity(name="the free speech zone"),
                    Entity(name="the courthouse"),
                ],
            ),
            Statement(
                predicate=under_2km,
                terms=[
                    Entity(name="the free speech zone"),
                    Entity(name="the courthouse"),
                ],
            ),
        ]
    )

    assert protest_facts.implies(speech_zone_facts)


def test_terms_means_doc_example():
    hades_curse = Statement(
        predicate=Predicate(content="{deity} cursed {target}"),
        terms=[Entity(name="Hades"), Entity(name="Persephone")],
    )
    aphrodite_curse = Statement(
        predicate=Predicate(content="{deity} cursed {target}"),
        terms=[Entity(name="Aphrodite"), Entity(name="Narcissus")],
    )

    assert hades_curse.means(aphrodite_curse)
