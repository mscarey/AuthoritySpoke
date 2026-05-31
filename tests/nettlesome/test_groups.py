import pytest

from authorityspoke.nettlesome.terms import (
    ContextRegister,
    consistent_with,
    contradicts,
    means,
)
from authorityspoke.nettlesome.entities import Entity
from authorityspoke.nettlesome.factors import AbsenceOf
from authorityspoke.nettlesome.groups import FactorGroup
from authorityspoke.nettlesome.predicates import Predicate
from authorityspoke.nettlesome.quantities import Comparison
from authorityspoke.nettlesome.statements import Statement


class TestMakeGroup:
    def test_group_from_list(self, make_statement):
        factor_list = [make_statement["crime"], make_statement["shooting"]]
        group = FactorGroup(sequence=factor_list)
        assert isinstance(group, FactorGroup)
        assert group[1] == make_statement["shooting"]
        assert "predicate=Predicate(content='{person1} committed" in repr(group)

    def test_group_from_item(self, make_statement):
        factor = make_statement["shooting"]
        group = FactorGroup(sequence=[factor])
        assert isinstance(group, FactorGroup)
        assert group[0] == make_statement["shooting"]

    def test_make_empty_group(self):
        group = FactorGroup(sequence=[])
        assert isinstance(group, FactorGroup)
        assert len(group) == 0

    def test_factorgroup_from_factorgroup(self, make_statement):
        factor_list = [make_statement["crime"], make_statement["shooting"]]
        group = FactorGroup(sequence=factor_list)
        identical_group = FactorGroup(sequence=group.sequence)
        assert isinstance(identical_group, FactorGroup)
        assert identical_group[0] == make_statement["crime"]

    def test_recursive_terms_from_factorgroup(self, make_statement):
        factor_list = [make_statement["crime"], make_statement["shooting"]]
        group = FactorGroup(sequence=factor_list)
        factors = group.recursive_terms
        assert factors["<Alice>"].name == "Alice"

    def test_one_factor_implies_and_has_same_context_as_other(self, make_statement):
        assert make_statement["more"].implies_same_context(
            make_statement["more_meters"]
        )

    def test_drop_implied_factors(self, make_statement):
        group = FactorGroup(
            sequence=[make_statement["more_meters"], make_statement["more"]]
        )
        shorter = group.drop_implied_factors()
        assert len(shorter) == 1
        assert make_statement["more_meters"] in group

    def test_drop_implied_factors_unmatched_context(self):
        """Test that Statements aren't considered redundant because they relate to different entities."""
        left = Statement(
            predicate=Comparison.new(
                content="the amount that {taller}'s height exceeded {shorter}'s height was",
                sign=">=",
                expression="2 inches",
            ),
            terms=[Entity(name="Ann"), Entity(name="Ben")],
        )
        right = Statement(
            predicate=Comparison.new(
                content="the amount that {taller}'s height exceeded {shorter}'s height was",
                sign=">=",
                expression="2 feet",
            ),
            terms=[Entity(name="Alice"), Entity(name="Bob")],
        )
        group = FactorGroup(sequence=[left, right])
        shorter = group.drop_implied_factors()
        assert len(shorter) == 2

    def test_get_factor_by_index(self, make_statement):
        group = FactorGroup(
            sequence=[make_statement["friends"], make_statement["less"]]
        )
        assert group[1].key.endswith("was less than 35 foot")

    def test_get_factor_by_name(self, make_complex_fact):
        group = FactorGroup(sequence=[make_complex_fact["relevant_murder"]])
        entity = group.get_factor_by_name("Alice")
        assert entity.plural is False

    def test_iterate_through_factors(self, make_complex_fact):
        group = FactorGroup(sequence=[make_complex_fact["relevant_murder"]])
        gen = iter(group)
        factor = next(gen)
        assert factor.short_string.endswith("statement that <Alice> murdered <Bob>")

    def test_cannot_add_entity(self):
        with pytest.raises(TypeError):
            FactorGroup(Entity(name="Morning Star"))


class TestSameFactors:
    def test_empty_groups_same_meaning(self):
        left = FactorGroup(sequence=[])
        right = FactorGroup(sequence=[])
        assert left.means(right)

    def test_group_has_same_factors_as_identical_group(self, make_statement):
        first_group = FactorGroup(
            sequence=[make_statement["crime"], make_statement["shooting"]]
        )
        second_group = FactorGroup(
            sequence=[make_statement["crime"], make_statement["shooting"]]
        )
        assert first_group.has_all_factors_of(second_group)

    def test_likely_contexts_with_identical_factor(self, make_statement):
        first_group = FactorGroup(
            sequence=[make_statement["shooting"], make_statement["crime"]]
        )
        second_group = FactorGroup(sequence=[make_statement["crime"]])
        gen = first_group.likely_contexts(second_group)
        context = next(gen)
        assert context.get("<Alice>").name == "Alice"

    def test_likely_contexts_to_identical_factor(self, make_statement):
        first_group = FactorGroup(sequence=[make_statement["shooting"]])
        second_group = FactorGroup(
            sequence=[make_statement["crime"], make_statement["shooting"]]
        )
        gen = first_group.likely_contexts(second_group)
        context = next(gen)
        assert context.get("<Alice>").name == "Alice"

    def test_group_has_same_factors_as_included_group(self, make_statement):
        first_group = FactorGroup(
            sequence=[
                make_statement["crime"],
                make_statement["shooting"],
                make_statement["murder"],
            ]
        )
        second_group = FactorGroup(
            sequence=[make_statement["crime"], make_statement["murder"]]
        )
        assert first_group.has_all_factors_of(second_group)
        assert not second_group.has_all_factors_of(first_group)

    def test_group_shares_all_factors_with_bigger_group(self, make_statement):
        first_group = FactorGroup(
            sequence=[
                make_statement["crime"],
                make_statement["shooting"],
                make_statement["murder"],
            ]
        )
        second_group = FactorGroup(
            sequence=[make_statement["crime"], make_statement["murder"]]
        )
        assert second_group.shares_all_factors_with(first_group)
        assert not first_group.shares_all_factors_with(second_group)

    def test_group_means_identical_group(self, make_statement):
        first_group = FactorGroup(
            sequence=[make_statement["crime"], make_statement["murder"]]
        )
        second_group = FactorGroup(
            sequence=[make_statement["crime"], make_statement["murder"]]
        )
        assert first_group.means(second_group)
        assert means(first_group, second_group)

    def test_group_does_not_mean_different_group(self, make_statement):
        first_group = FactorGroup(
            sequence=[
                make_statement["crime"],
                make_statement["shooting"],
                make_statement["murder"],
            ]
        )
        second_group = FactorGroup(
            sequence=[make_statement["crime"], make_statement["murder"]]
        )
        assert not first_group.means(second_group)
        assert not second_group.means(first_group)

    def test_term_outside_of_group(self):
        speed = "{person}'s speed was"
        comparison = Comparison.new(
            content=speed, sign=">", expression="36 kilometers per hour"
        )
        other = Comparison.new(
            content=speed, sign=">", expression="10 meters per second"
        )
        left = FactorGroup(
            sequence=[Statement(predicate=comparison, terms=[Entity(name="Ann")])]
        )
        right = Statement(predicate=other, terms=[Entity(name="Bob")])
        assert left.means(right)

    def test_list_instead_of_group(self):
        comparison = Comparison.new(
            content="{person}'s speed was",
            sign=">",
            expression="36 kilometers per hour",
        )
        other_comparison = Comparison.new(
            content="{person}'s speed was", sign=">", expression="10 meters per second"
        )
        left = FactorGroup(
            sequence=[Statement(predicate=comparison, terms=[Entity(name="Ann")])]
        )
        right = [Statement(predicate=other_comparison, terms=[Entity(name="Bob")])]
        assert left.means(right)
        assert "Because <Ann> is like <Bob>" in str(left.explain_same_meaning(right))

    def test_no_comparison_with_comparison(self):
        comparison = Comparison.new(
            content="{person}'s speed was",
            sign=">",
            expression="36 kilometers per hour",
        )
        other_comparison = Comparison.new(
            content="{person}'s speed was", sign=">", expression="10 meters per second"
        )
        left = FactorGroup(
            sequence=[Statement(predicate=comparison, terms=[Entity(name="Ann")])]
        )
        assert not left.means(other_comparison)

    def test_empty_factorgroup_is_falsy(self):
        group = FactorGroup(sequence=[])
        assert bool(group) is False

    def test_does_not_share_all_factors(self, make_statement):
        left = FactorGroup(
            sequence=[
                Statement(
                    predicate=Predicate(content="{suburb} was a suburb of {city}"),
                    terms=(
                        Entity(name="Oakland"),
                        Entity(name="San Francisco"),
                    ),
                ),
                make_statement["more"],
                Statement.new(
                    predicate="{city} was sunny", terms=[Entity(name="Oakland")]
                ),
            ]
        )
        right = FactorGroup(
            sequence=[
                Statement.new(
                    predicate=Predicate(content="{suburb} was a suburb of {city}"),
                    terms=(
                        Entity(name="San Francisco"),
                        Entity(name="Oakland"),
                    ),
                ),
                make_statement["more"],
                Statement.new(
                    predicate="{city} was sunny", terms=[Entity(name="Oakland")]
                ),
            ]
        )
        assert not left.shares_all_factors_with(right)

    def test_not_same_nonmatching_terms(self, make_statement):
        left = FactorGroup(
            sequence=[
                Statement.new(
                    predicate=Predicate(content="{suburb} was a suburb of {city}"),
                    terms=(
                        Entity(name="Oakland"),
                        Entity(name="San Francisco"),
                    ),
                ),
                make_statement["more"],
                Statement.new(
                    predicate="{city} was sunny", terms=[Entity(name="Oakland")]
                ),
            ]
        )
        right = FactorGroup(
            sequence=[
                Statement(
                    predicate=Predicate(content="{suburb} was a suburb of {city}"),
                    terms=(
                        Entity(name="San Francisco"),
                        Entity(name="Oakland"),
                    ),
                ),
                make_statement["more"],
                Statement.new(
                    predicate="{city} was sunny", terms=[Entity(name="Oakland")]
                ),
            ]
        )
        assert not left.means(right)

    def test_interchangeable_same_meaning_no_repeated_explanations(self):
        nafta = FactorGroup(
            sequence=[
                Statement.new(
                    predicate="{country1} signed a treaty with {country2}",
                    terms=[Entity(name="Mexico"), Entity(name="USA")],
                ),
                Statement.new(
                    predicate="{country2} signed a treaty with {country3}",
                    terms=[Entity(name="USA"), Entity(name="Canada")],
                ),
                Statement.new(
                    predicate="{country3} signed a treaty with {country1}",
                    terms=[Entity(name="Canada"), Entity(name="Mexico")],
                ),
            ]
        )
        nato = FactorGroup(
            sequence=[
                Statement.new(
                    predicate="{country1} signed a treaty with {country2}",
                    terms=[Entity(name="USA"), Entity(name="UK")],
                ),
                Statement.new(
                    predicate="{country2} signed a treaty with {country3}",
                    terms=[Entity(name="UK"), Entity(name="Germany")],
                ),
                Statement.new(
                    predicate="{country3} signed a treaty with {country1}",
                    terms=[Entity(name="Germany"), Entity(name="USA")],
                ),
            ]
        )
        assert nafta.means(nato)
        answers = list(
            nafta.explanations_same_meaning(
                nato, context=([Entity(name="USA")], [Entity(name="UK")])
            )
        )
        assert len(answers) == 2


class TestImplication:
    def test_factorgroup_implies_none(self, make_statement):
        group = FactorGroup(
            sequence=[make_statement["crime"], make_statement["shooting"]]
        )
        assert group.implies(None)

    def test_factorgroup_implication_of_empty_group(self, make_statement):
        factor_list = [make_statement["crime"], make_statement["shooting"]]
        group = FactorGroup(sequence=factor_list)
        empty_group = FactorGroup(sequence=[])
        assert group.implies(empty_group)
        assert group[:1].implies(empty_group)

    def test_explanation_implication_of_factorgroup(self, make_statement):
        """Explanation shows the statements in `left` narrow down the quantity more than `right` does."""
        left = FactorGroup(
            sequence=[make_statement["absent_way_more"], make_statement["less_than_20"]]
        )
        right = FactorGroup(
            sequence=[make_statement["less"], make_statement["absent_more"]]
        )
        explanation = left.explain_implication(right)
        assert "implies" in str(explanation).lower()

    def test_explanations_implication_of_factor(self, make_statement):
        """Explanation shows the statements in `left` narrow down the quantity more than `right` does."""
        left = FactorGroup(
            sequence=[make_statement["absent_way_more"], make_statement["less_than_20"]]
        )
        right = make_statement["less"]
        explanation = left.explain_implication(right)
        assert "implies" in str(explanation).lower()

    def test_ge_not_gt(self, make_statement):
        left = FactorGroup(
            sequence=[make_statement["shooting"], make_statement["murder"]]
        )
        right = FactorGroup(
            sequence=[make_statement["shooting_craig"], make_statement["murder_craig"]]
        )
        assert left >= right
        assert not left > right

    def test_greater_than_none(self, make_statement):
        left = FactorGroup(sequence=[])
        assert left > None

    def test_interchangeable_terms_in_factorgroup(self):
        """Fails whether the method is 'comparison' or '_verbose_comparison'"""
        left = FactorGroup(
            sequence=[
                Statement(
                    predicate=Comparison.new(
                        content="the distance between {place1} and {place2} was",
                        truth=True,
                        sign="<=",
                        expression="35 foot",
                    ),
                    terms=(
                        Entity(name="Scylla", generic=True, plural=False),
                        Entity(name="Charybdis", generic=True, plural=False),
                    ),
                ),
                Statement(
                    predicate=Comparison.new(
                        content="the distance between {monster} and a boat used by {hero} was",
                        truth=True,
                        sign="<=",
                        expression="5 foot",
                    ),
                    terms=(
                        Entity(name="Scylla", generic=True, plural=False),
                        Entity(name="Ulysses", generic=True, plural=False),
                    ),
                ),
            ]
        )

        right = FactorGroup(
            sequence=[
                Statement(
                    predicate=Comparison.new(
                        content="the distance between {place1} and {place2} was",
                        truth=True,
                        sign="<=",
                        expression="35 foot",
                    ),
                    terms=(
                        Entity(name="Charybdis", generic=True, plural=False),
                        Entity(name="Scylla", generic=True, plural=False),
                    ),
                ),
                Statement(
                    predicate=Comparison.new(
                        content="the distance between {thing} and a boat used by {person} was",
                        truth=True,
                        sign="<=",
                        expression="5 foot",
                    ),
                    terms=(
                        Entity(name="Scylla", generic=True, plural=False),
                        Entity(name="Ulysses", generic=True, plural=False),
                    ),
                ),
            ]
        )
        gen = left.explanations_implication(right)
        result = next(gen)
        assert result

    def test_interchangeable_terms_in_different_orders(self):
        more_than_100_yards = Comparison.new(
            content="the distance between {site1} and {site2} was",
            sign=">",
            expression="100 yards",
        )
        less_than_1_mile = Comparison.new(
            content="the distance between {site1} and {site2} was",
            sign="<",
            expression="1 mile",
        )

        protest_facts = FactorGroup(
            sequence=[
                Statement(
                    predicate=more_than_100_yards,
                    terms=[
                        Entity(name="the political convention"),
                        Entity(name="the police cordon"),
                    ],
                ),
                Statement(
                    predicate=less_than_1_mile,
                    terms=[
                        Entity(name="the police cordon"),
                        Entity(name="the political convention"),
                    ],
                ),
            ]
        )
        assert "between <the political convention> and " in str(protest_facts)
        more_than_50_meters = Comparison.new(
            content="the distance between {site1} and {site2} was",
            sign=">",
            expression="50 meters",
        )
        less_than_2_km = Comparison.new(
            content="the distance between {site1} and {site2} was",
            sign="<=",
            expression="2 km",
        )

        speech_zone_facts = FactorGroup(
            sequence=[
                Statement(
                    predicate=more_than_50_meters,
                    terms=[
                        Entity(name="the free speech zone"),
                        Entity(name="the courthouse"),
                    ],
                ),
                Statement(
                    predicate=less_than_2_km,
                    terms=[
                        Entity(name="the free speech zone"),
                        Entity(name="the courthouse"),
                    ],
                ),
            ]
        )
        assert protest_facts.implies(speech_zone_facts)

    def test_context_prevents_implication(self, make_statement):
        left = FactorGroup(
            sequence=[make_statement["shooting"], make_statement["crime"]]
        )
        right = FactorGroup(
            sequence=[make_statement["shooting_craig"], make_statement["crime_craig"]]
        )
        assert left.implies(right)
        assert not left.implies(
            right,
            context=(
                [Entity(name="Alice"), Entity(name="Bob")],
                [Entity(name="Dan"), Entity(name="Craig")],
            ),
        )

    def test_context_preventing_implication_as_dict(self, make_statement):
        left = FactorGroup(
            sequence=[make_statement["shooting"], make_statement["crime"]]
        )
        right = FactorGroup(
            sequence=[make_statement["shooting_craig"], make_statement["crime_craig"]]
        )
        assert left.implies(right)
        assert not left.implies(
            right,
            context={"<Alice>": Entity(name="Dan"), "<Bob>": Entity(name="Craig")},
        )


class TestImpliedBy:
    def test_implied_by(self):
        left = FactorGroup(
            sequence=[
                Statement(
                    predicate=Predicate(
                        content="{rural_s_telephone_directory} was a compilation of facts"
                    ),
                    terms=(Entity(name="Rural's telephone directory"),),
                )
            ]
        )
        right = FactorGroup(
            sequence=[
                Statement(
                    predicate=Predicate(
                        content="{rural_s_telephone_directory} was an idea"
                    ),
                    terms=(Entity(name="Rural's telephone directory"),),
                )
            ]
        )
        assert not left.implied_by(right)

    def test_group_implied_by_factor(self, make_statement):
        left = FactorGroup(sequence=[make_statement["more"]])
        assert left.implied_by(make_statement["way_more"])

    def test_context_prevents_implied_by_factor(self, make_statement):
        left = FactorGroup(sequence=[make_statement["more"]])
        assert not left.implied_by(
            make_statement["way_more"],
            context=(["<San Francisco>"], [Entity(name="Richmond")]),
        )

    def test_context_prevents_implied_by_factor_tuples_not_lists(self, make_statement):
        left = FactorGroup(sequence=[make_statement["more"]])
        assert not left.implied_by(
            make_statement["way_more"],
            context=(("<San Francisco>",), (Entity(name="Richmond"),)),
        )


class TestContradiction:
    def test_contradiction_of_group(self):
        lived_at = Predicate(content="{person} lived at {residence}")
        bob_lived = Statement(
            predicate=lived_at, terms=[Entity(name="Bob"), Entity(name="Bob's house")]
        )
        carl_lived = Statement(
            predicate=lived_at, terms=[Entity(name="Carl"), Entity(name="Carl's house")]
        )
        distance_long = Comparison.new(
            content="the distance from the center of {city} to {residence} was",
            sign=">=",
            expression="50 miles",
        )
        statement_long = Statement(
            predicate=distance_long,
            terms=[Entity(name="Houston"), Entity(name="Bob's house")],
        )
        distance_short = Comparison.new(
            content="the distance from the center of {city} to {residence} was",
            sign="<=",
            expression="10 kilometers",
        )
        statement_short = Statement(
            predicate=distance_short,
            terms=[Entity(name="El Paso"), Entity(name="Carl's house")],
        )
        left = FactorGroup(sequence=[bob_lived, statement_long])
        right = FactorGroup(sequence=[carl_lived, statement_short])
        explanation = left.explain_contradiction(right)
        assert explanation.context["<Houston>"].name == "El Paso"
        assert contradicts(left, right)

    def test_interchangeable_contradiction_no_repeated_explanations(self):
        nafta = FactorGroup(
            sequence=[
                Statement.new(
                    predicate="{country1} signed a treaty with {country2}",
                    terms=[Entity(name="Mexico"), Entity(name="USA")],
                ),
                Statement.new(
                    predicate="{country2} signed a treaty with {country3}",
                    terms=[Entity(name="USA"), Entity(name="Canada")],
                ),
                Statement.new(
                    predicate="{country3} signed a treaty with {country1}",
                    terms=[Entity(name="Canada"), Entity(name="Mexico")],
                ),
            ]
        )
        brexit = FactorGroup(
            sequence=[
                Statement.new(
                    predicate="{country1} signed a treaty with {country2}",
                    terms=[Entity(name="UK"), Entity(name="European Union")],
                ),
                Statement.new(
                    predicate="{country2} signed a treaty with {country3}",
                    terms=[Entity(name="European Union"), Entity(name="Germany")],
                ),
                Statement.new(
                    predicate="{country3} signed a treaty with {country1}",
                    terms=[Entity(name="Germany"), Entity(name="UK")],
                    truth=False,
                ),
            ]
        )
        assert nafta.contradicts(brexit)

        explanations_usa_like_uk = nafta.explanations_contradiction(
            brexit, context=([Entity(name="USA")], [Entity(name="UK")])
        )
        assert len(list(explanations_usa_like_uk)) == 2

    def test_register_for_none(self):
        treaty = FactorGroup(
            sequence=[
                Statement.new(
                    predicate="{country1} signed a treaty with {country2}",
                    terms=[Entity(name="UK"), Entity(name="European Union")],
                ),
            ]
        )
        registers = list(
            treaty.update_context_register(
                other=None, context=ContextRegister(), comparison=means
            )
        )
        assert len(registers) == 1
        assert not registers[0]  # empty register

    def test_update_context_register_from_none(self):
        left = FactorGroup(
            sequence=[
                Statement.new(
                    predicate="{shooter} shot {victim}",
                    terms=[Entity(name="Alice"), Entity(name="Bob")],
                )
            ]
        )
        right = FactorGroup(
            sequence=[
                Statement.new(
                    predicate="{shooter} shot {victim}",
                    terms=[Entity(name="Craig"), Entity(name="Dan")],
                )
            ]
        )
        update = left.update_context_register(
            right,
            context=None,
            comparison=means,
        )
        explanation = next(update)
        assert explanation.reason == ""

    def test_implication_no_repeated_explanations(self):
        large_payments = FactorGroup(
            sequence=[
                Statement.new(
                    predicate=Comparison.new(
                        content="the number of dollars that {payer} paid to {payee} was",
                        sign=">",
                        expression=10000,
                    ),
                    terms=[Entity(name="Alice"), Entity(name="Bob")],
                ),
                Statement.new(
                    predicate=Comparison.new(
                        content="the number of dollars that {payer} paid to {payee} was",
                        sign=">",
                        expression=1000,
                    ),
                    terms=[Entity(name="Dan"), Entity(name="Eve")],
                ),
            ]
        )
        small_payments = FactorGroup(
            sequence=[
                Statement.new(
                    predicate=Comparison.new(
                        content="the number of dollars that {payer} paid to {payee} was",
                        sign=">",
                        expression=100,
                    ),
                    terms={"payer": Entity(name="Fred"), "payee": Entity(name="Greg")},
                ),
                Statement.new(
                    predicate=Comparison.new(
                        content="the number of dollars that {payer} paid to {payee} was",
                        sign=">",
                        expression=10,
                    ),
                    terms={"payer": Entity(name="Jim"), "payee": Entity(name="Kim")},
                ),
            ]
        )
        assert large_payments.implies(small_payments)
        all_explanations = list(large_payments.explanations_implication(small_payments))
        assert len(all_explanations) == 2
        limited_explanations = list(
            large_payments.explanations_implication(
                small_payments, context=([Entity(name="Alice")], [Entity(name="Jim")])
            )
        )
        assert len(limited_explanations) == 1

    def test_absence_contradicts_group(self):
        shot_fact = Statement.new(
            predicate=Predicate(content="{shooter} shot {victim}"),
            terms=[Entity(name="Alice"), Entity(name="Bob")],
        )
        shot_absence = AbsenceOf(absent=shot_fact)
        group = FactorGroup(sequence=[shot_fact])
        assert shot_absence.contradicts(group)

    def test_interchangeable_implication_no_repeated_explanations(self):
        nafta = FactorGroup(
            sequence=[
                Statement.new(
                    predicate="{country1} signed a treaty with {country2}",
                    terms=[Entity(name="Mexico"), Entity(name="USA")],
                ),
                Statement.new(
                    predicate="{country2} signed a treaty with {country3}",
                    terms=[Entity(name="USA"), Entity(name="Canada")],
                ),
                Statement.new(
                    predicate="{country3} signed a treaty with {country1}",
                    terms=[Entity(name="Canada"), Entity(name="Mexico")],
                ),
            ]
        )
        nato = FactorGroup(
            sequence=[
                Statement.new(
                    predicate="{country1} signed a treaty with {country2}",
                    terms=[Entity(name="USA"), Entity(name="UK")],
                ),
                Statement.new(
                    predicate="{country2} signed a treaty with {country3}",
                    terms=[Entity(name="UK"), Entity(name="Germany")],
                ),
                Statement.new(
                    predicate="{country3} signed a treaty with {country1}",
                    terms=[Entity(name="Germany"), Entity(name="USA")],
                ),
            ]
        )
        assert nafta.implies(nato)
        all_answers = list(nafta.explanations_implication(nato))
        assert len(all_answers) == 6

        limited_answers = list(
            nafta.explanations_implication(
                nato, context=([Entity(name="USA")], [Entity(name="UK")])
            )
        )
        assert len(limited_answers) == 2


class TestAdd:
    def test_add_does_not_consolidate_factors(self, make_statement):
        left = FactorGroup(sequence=[make_statement["crime"]])
        right = FactorGroup(sequence=[make_statement["crime"]])
        added = left + right
        assert len(added) == 2
        assert isinstance(added, FactorGroup)

    def test_add_factor_to_factorgroup(self, make_statement):
        left = FactorGroup(sequence=[make_statement["crime"]])
        right = make_statement["crime"]
        added = left + right
        assert len(added) == 2
        assert isinstance(added, FactorGroup)

    def test_add_factor_without_contradicting_due_to_context(self, make_statement):
        left = FactorGroup(sequence=[make_statement["less"]])
        combined = left + make_statement["more_atlanta"]
        assert len(combined) == 2

    def test_add_contradictory_factor_to_factorgroup(self, make_statement):
        left = FactorGroup(sequence=[make_statement["less"]])
        combined = left + make_statement["more"]
        assert combined is None


class TestUnion:
    def test_factors_combined_because_of_implication(self, make_statement):
        left = FactorGroup(sequence=[make_statement["more"]])
        right = FactorGroup(sequence=[make_statement["more_meters"]])
        added = left | right
        assert added and len(added) == 1
        assert "35 foot" in str(added[0])

    def test_union_with_factor_outside_group(self, make_statement):
        left = FactorGroup(sequence=[make_statement["more_meters"]])
        right = make_statement["more"]
        added = left | right
        assert len(added) == 1
        assert "35 foot" in str(added[0])

    def test_no_contradiction_because_entities_vary(self, make_statement):
        """
        If these Factors were about the same Term, they would contradict
        and no union would be possible.
        """
        left = FactorGroup(sequence=[make_statement["no_shooting_entity_order"]])
        right = FactorGroup(sequence=[make_statement["shooting"]])
        combined = left | right
        assert combined and len(combined) == 2

    def test_union_causes_contradiction(self, make_statement):
        """Test Factors about the same Term contradict so no union is possible."""
        left = FactorGroup(sequence=[make_statement["no_shooting"]])
        right = FactorGroup(sequence=[make_statement["shooting"]])
        combined = left | right
        assert combined is None

    def test_union_no_factor_redundant(self, make_statement):
        """Test that Factor is not mistaken as redundant."""
        alice_had_bullets = Statement(
            predicate=Comparison.new(
                content="the number of bullets {person} had was", sign=">=", expression=5
            ),
            terms=[Entity(name="Alice")],
        )
        bob_had_bullets = Statement(
            predicate=Comparison.new(
                content="the number of bullets {person} had was", sign=">=", expression=5
            ),
            terms=[Entity(name="Bob")],
        )
        left = FactorGroup(sequence=[make_statement["shooting"], alice_had_bullets])
        right = FactorGroup(sequence=[make_statement["shooting"], bob_had_bullets])
        combined = left | right
        assert len(combined) == 3

    def test_union_same_entity_on_both_sides(self, make_statement):
        two_terms = FactorGroup(sequence=[make_statement["murder_entity_order"]])
        one_term = FactorGroup(sequence=[make_statement["crime"]])
        result = one_term | two_terms
        assert result


class TestConsistent:
    predicate_less_specific = Comparison.new(
        content="{vehicle}'s speed was",
        sign="<",
        expression="30 miles per hour",
    )
    predicate_less_general = Comparison.new(
        content="{vehicle}'s speed was",
        sign="<",
        expression="60 miles per hour",
    )
    predicate_more = Comparison.new(
        content="{vehicle}'s speed was",
        sign=">",
        expression="55 miles per hour",
    )
    predicate_farm = Predicate(content="{person} had a farm")
    slower_specific_statement = Statement(
        predicate=predicate_less_specific, terms=[Entity(name="the car")]
    )
    slower_general_statement = Statement(
        predicate=predicate_less_general, terms=[Entity(name="the pickup")]
    )
    faster_statement = Statement(
        predicate=predicate_more, terms=[Entity(name="the pickup")]
    )
    farm_statement = Statement(
        predicate=predicate_farm, terms=[Entity(name="Old MacDonald")]
    )

    def test_group_contradicts_single_factor(self):
        group = FactorGroup(
            sequence=[self.slower_specific_statement, self.farm_statement]
        )
        register = ContextRegister()
        register.insert_pair(Entity(name="the car"), Entity(name="the pickup"))
        assert group.contradicts(self.faster_statement, context=register)

    def test_one_statement_does_not_contradict_group(self):
        group = FactorGroup(
            sequence=[self.slower_general_statement, self.farm_statement]
        )
        register = ContextRegister()
        register.insert_pair(Entity(name="the pickup"), Entity(name="the pickup"))
        assert not self.faster_statement.contradicts(group, context=register)

    def test_group_inconsistent_with_single_factor(self):
        group = FactorGroup(
            sequence=[self.slower_specific_statement, self.farm_statement]
        )
        register = ContextRegister()
        register.insert_pair(Entity(name="the car"), Entity(name="the pickup"))
        assert not group.consistent_with(self.faster_statement, context=register)
        assert not consistent_with(group, self.faster_statement, context=register)
        assert repr(group).startswith("FactorGroup([Statement")
        assert "less than 30 mile / hour" in str(group[0])

    def test_no_duplicate_explanations_consistent(self):
        large_payments = FactorGroup(
            sequence=[
                Statement(
                    predicate=Comparison.new(
                        content="the number of dollars that {payer} paid to {payee} was",
                        sign=">",
                        expression=10000,
                    ),
                    terms=[Entity(name="Alice"), Entity(name="Bob")],
                ),
                Statement(
                    predicate=Comparison.new(
                        content="the number of dollars that {payer} paid to {payee} was",
                        sign=">",
                        expression=1000,
                    ),
                    terms=[Entity(name="Dan"), Entity(name="Eve")],
                ),
            ]
        )
        small_payments = FactorGroup(
            sequence=[
                Statement.new(
                    predicate=Comparison.new(
                        content="the number of dollars that {payer} paid to {payee} was",
                        sign=">",
                        expression=100,
                    ),
                    terms={"payer": Entity(name="Fred"), "payee": Entity(name="Greg")},
                ),
                Statement.new(
                    predicate=Comparison.new(
                        content="the number of dollars that {payer} paid to {payee} was",
                        sign=">",
                        expression=10,
                    ),
                    terms={"payer": Entity(name="Jim"), "payee": Entity(name="Kim")},
                ),
            ]
        )
        assert large_payments.consistent_with(small_payments)
        all_explanations = list(
            large_payments.explanations_consistent_with(small_payments)
        )
        assert len(all_explanations) == 24
        limited_explanations = list(
            large_payments.explanations_consistent_with(
                small_payments, context=([Entity(name="Alice")], [Entity(name="Jim")])
            )
        )
        assert len(limited_explanations) == 6

    def test_groups_with_one_statement_consistent(self):
        specific_group = FactorGroup(sequence=[self.slower_specific_statement])
        general_group = FactorGroup(sequence=[self.faster_statement])
        assert specific_group.consistent_with(general_group)
        assert consistent_with(specific_group, general_group)

    def test_group_inconsistent_with_one_statement(self):
        group = FactorGroup(
            sequence=[self.slower_specific_statement, self.farm_statement]
        )
        register = ContextRegister()
        register.insert_pair(Entity(name="the car"), Entity(name="the pickup"))
        assert not group.consistent_with(self.faster_statement, context=register)

    def test_one_statement_inconsistent_with_group(self):
        group = FactorGroup(
            sequence=[self.slower_specific_statement, self.farm_statement]
        )
        register = ContextRegister()
        register.insert_pair(Entity(name="the pickup"), Entity(name="the car"))
        assert not self.faster_statement.consistent_with(group, context=register)

    def test_one_statement_consistent_with_group(self):
        group = FactorGroup(
            sequence=[self.slower_general_statement, self.farm_statement]
        )
        register = ContextRegister()
        register.insert_pair(Entity(name="the pickup"), Entity(name="the pickup"))
        assert self.faster_statement.consistent_with(group, context=register)

    def test_no_contradiction_of_none(self):
        group = FactorGroup(
            sequence=[self.slower_general_statement, self.farm_statement]
        )
        assert not group.contradicts(None)

    def test_consistent_with_none(self):
        group = FactorGroup(
            sequence=[self.slower_general_statement, self.farm_statement]
        )
        assert group.consistent_with(None)

    def test_two_inconsistent_groups(self):
        left = FactorGroup(sequence=[self.slower_specific_statement])
        right = FactorGroup(sequence=[self.faster_statement])
        context = ContextRegister()
        context.insert_pair(Entity(name="the car"), Entity(name="the pickup"))
        assert not left.consistent_with(right, context=context)

    def test_not_internally_consistent_with_context(self, make_statement):
        context = ContextRegister()
        context.insert_pair(Entity(name="Alice"), Entity(name="Alice"))
        context.insert_pair(Entity(name="Bob"), Entity(name="Bob"))
        group = FactorGroup(
            sequence=[make_statement["shooting"], make_statement["no_shooting"]]
        )
        with pytest.raises(ValueError):
            group.internally_consistent()

    def test_not_internally_consistent(self, make_statement):
        group = FactorGroup(
            sequence=[make_statement["shooting"], make_statement["no_shooting"]]
        )
        with pytest.raises(ValueError):
            group.internally_consistent()

    def test_all_generic_terms_match_in_statement(self):
        predicate = Predicate(content="the telescope pointed at {object}")
        morning = Statement(predicate=predicate, terms=[Entity(name="Morning Star")])
        evening = Statement(predicate=predicate, terms=[Entity(name="Evening Star")])
        left = FactorGroup(sequence=[morning])
        right = FactorGroup(sequence=[evening])
        context = ContextRegister()
        context.insert_pair(Entity(name="Morning Star"), Entity(name="Evening Star"))
        assert left._all_generic_terms_match(right, context=context)
