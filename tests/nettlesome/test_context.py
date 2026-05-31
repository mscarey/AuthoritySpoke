import operator

import pytest

from authorityspoke.nettlesome.terms import ContextRegister, Explanation, means
from authorityspoke.nettlesome.entities import Entity
from authorityspoke.nettlesome.groups import FactorGroup
from authorityspoke.nettlesome.predicates import Predicate
from authorityspoke.nettlesome.statements import Statement


class TestContextRegisters:
    bird = Predicate(content="{bird} was a bird")
    paid = Predicate(content="{employer} paid {employee}")

    def test_possible_context_without_empty_spaces(self):
        left = Statement(predicate=self.bird, terms=[Entity(name="Owl")])
        right = Statement(predicate=self.bird, terms=[Entity(name="Owl")])
        contexts = list(left.possible_contexts(right))
        assert len(contexts) == 1
        assert contexts[0].check_match(Entity(name="Owl"), Entity(name="Owl"))

    def test_possible_context_different_terms(self):
        left = Statement(predicate=self.bird, terms=[Entity(name="Foghorn")])
        right = Statement(predicate=self.bird, terms=[Entity(name="Woody")])
        contexts = list(left.possible_contexts(right))
        assert len(contexts) == 1
        assert contexts[0].check_match(Entity(name="Foghorn"), Entity(name="Woody"))

    def test_all_possible_contexts_identical_factor(self):
        left = Statement(
            predicate=self.paid, terms=[Entity(name="Irene"), Entity(name="Bob")]
        )
        contexts = list(left.possible_contexts(left))
        assert len(contexts) == 2
        assert any(
            context.check_match(Entity(name="Irene"), Entity(name="Bob"))
            for context in contexts
        )

    def test_context_not_equal_to_list(self):
        changes = ContextRegister.from_lists(
            [Entity(name="Alice")],
            [Entity(name="Dan")],
        )
        assert changes != [[Entity(name="Alice")], [Entity(name="Dan")]]

    def test_cannot_update_context_register_from_lists(self):
        left = Statement.new(
            predicate="{shooter} shot {victim}",
            terms=[Entity(name="Alice"), Entity(name="Bob")],
        )
        right = Statement.new(
            predicate="{shooter} shot {victim}",
            terms=[Entity(name="Craig"), Entity(name="Dan")],
        )
        update = left.update_context_register(
            right,
            context=[[Entity(name="Alice")], [Entity(name="Craig")]],
            comparison=means,
        )
        with pytest.raises(AttributeError):
            next(update)

    def test_limited_possible_contexts_identical_factor(self):
        statement = Statement(
            predicate=self.paid, terms=[Entity(name="Al"), Entity(name="Xu")]
        )
        context = ContextRegister()
        context.insert_pair(Entity(name="Al"), Entity(name="Xu"))
        contexts = list(statement.possible_contexts(statement, context=context))
        assert len(contexts) == 1
        assert contexts[0].check_match(Entity(name="Al"), Entity(name="Xu"))
        assert "Entity(" in repr(contexts)
        assert "name='Xu'" in repr(contexts)

    def test_context_register_empty(self, make_complex_fact):
        """
        Yields no context_register because the Term in f1 doesn't imply
        the Fact in f_relevant_murder.
        """
        statement = Statement.new(
            predicate="{person} was a defendant", terms=[Entity(name="Alice")]
        )
        complex_statement = make_complex_fact["relevant_murder"]
        gen = statement._context_registers(complex_statement, operator.ge)
        with pytest.raises(StopIteration):
            next(gen)

    def test_insert_pair_with_wrong_type(self):
        context = ContextRegister()
        with pytest.raises(TypeError):
            context.insert_pair(
                Entity(name="Bob"),
                Predicate(
                    content="events transpired"
                ),  # ty: ignore[invalid-argument-type]
            )

    def test_failed_match(self):
        context = ContextRegister()
        context.insert_pair(Entity(name="Bob"), Entity(name="Alice"))
        assert context.check_match(Entity(name="Craig"), Entity(name="Dan")) is False

    def test_context_register_valid(self, make_statement):
        expected = ContextRegister()
        expected.insert_pair(Entity(name="Alice"), Entity(name="Bob"))
        generated = next(
            make_statement["no_crime"]._context_registers(
                make_statement["no_crime_entity_order"], operator.le
            )
        )
        assert len(generated) == len(expected)
        assert generated["<Alice>"].name == expected["<Alice>"].name

    def test_import_to_context_register(self, make_statement):
        left = ContextRegister.from_lists(
            to_replace=[make_statement["shooting"], Entity(name="Alice")],
            replacements=[make_statement["shooting_entity_order"], Entity(name="Bob")],
        )
        right = ContextRegister()
        right.insert_pair(Entity(name="Bob"), Entity(name="Alice"))
        merged = left.merged_with(right)
        assert merged and len(merged) == 3

    def test_import_to_mapping_no_change(self):
        old_mapping = ContextRegister.from_lists(
            [Entity(name="Al")], [Entity(name="Li")]
        )
        new_mapping = ContextRegister.from_lists(
            [Entity(name="Al")], [Entity(name="Li")]
        )
        merged = old_mapping.merged_with(new_mapping)
        assert len(merged) == 1
        assert merged["<Al>"].name == "Li"

    def test_import_to_mapping_conflict(self):
        old_mapping = ContextRegister.from_lists(
            [Entity(name="Al")], [Entity(name="Li")]
        )
        new_mapping = ContextRegister.from_lists(
            [Entity(name="Al")], [Entity(name="Al")]
        )
        merged = old_mapping.merged_with(new_mapping)
        assert merged is None

    def test_import_to_mapping_reciprocal(self, make_statement):
        mapping = ContextRegister.from_lists(
            [make_statement["shooting"]], [make_statement["shooting"]]
        ).merged_with(
            ContextRegister.from_lists(
                [make_statement["shooting_entity_order"]],
                [make_statement["shooting_entity_order"]],
            )
        )
        assert (
            mapping.get_factor(make_statement["shooting"]).short_string
            == make_statement["shooting"].short_string
        )

    def test_registers_for_interchangeable_context(self, make_statement):
        """
        Test that _registers_for_interchangeable_context swaps the first two
        items in the ContextRegister
        """
        factor = Statement.new(
            predicate="{person1} and {person2} met with each other",
            terms=[Entity(name="Al"), Entity(name="Ed")],
        )
        first_pattern, second_pattern = list(factor.term_permutations())
        assert first_pattern[0].name == second_pattern[1].name
        assert first_pattern[1].name == second_pattern[0].name
        assert first_pattern[0].name != first_pattern[1].name

    def test_wrong_type_in_input_list(self, make_statement):
        explanation = Explanation(reasons=[])
        with pytest.raises(TypeError):
            ContextRegister.from_lists(
                to_replace=[Entity(name="Al"), explanation],
                replacements=[Entity(name="Bo"), Entity(name="Cid")],
            )

    def test_cannot_create_register_from_one_list(self):
        with pytest.raises(ValueError):
            ContextRegister.create([Entity(name="Alice"), Entity(name="Bob")])

    def test_no_duplicate_context_interchangeable_terms(self):
        left = Statement.new(
            predicate=Predicate(content="{country1} signed a treaty with {country2}"),
            terms=(Entity(name="Mexico"), Entity(name="USA")),
        )

        right = Statement.new(
            predicate=Predicate(content="{country3} signed a treaty with {country1}"),
            terms=(Entity(name="Germany"), Entity(name="UK")),
        )

        context = ContextRegister.from_lists([Entity(name="USA")], [Entity(name="UK")])

        gen = left._context_registers(right, operator.ge, context)
        results = list(gen)
        assert len(results) == 1

    def test_context_from_lists_wrong_length(self):
        context = ContextRegister.from_lists(
            [Entity(name="Death Star 3"), Entity(name="Kylo Ren")],
            [Entity(name="Death Star 1")],
        )

        assert "Kylo Ren" not in str(context)


class TestLikelyContext:
    def test_likely_context_one_factor(self, make_statement):
        left = make_statement["murder"]
        right = make_statement["murder"]
        context = next(left.likely_contexts(right))
        assert context.check_match(Entity(name="Bob"), Entity(name="Bob"))

    def test_likely_context_implication_one_factor(self, make_statement):
        left = make_statement["large_weight"]
        right = make_statement["small_weight"]
        context = next(left.likely_contexts(right))
        assert context.check_match(Entity(name="Alice"), Entity(name="Alice"))

    def test_likely_context_two_factors(self, make_statement):
        left = FactorGroup(
            sequence=[make_statement["murder"], make_statement["large_weight"]]
        )
        right = make_statement["small_weight_bob"]
        context = next(left.likely_contexts(right))
        assert context.check_match(Entity(name="Alice"), Entity(name="Bob"))

    def test_likely_context_two_by_two(self, make_statement):
        left = FactorGroup(
            sequence=[make_statement["murder"], make_statement["large_weight"]]
        )
        right = FactorGroup(
            sequence=(
                make_statement["murder_entity_order"],
                make_statement["small_weight_bob"],
            )
        )
        context = next(left.likely_contexts(right))
        assert context.check_match(Entity(name="Alice"), Entity(name="Bob"))

    def test_likely_context_different_terms(self):
        copyright_registered = Statement.new(
            predicate="{entity} registered a copyright covering {work}",
            terms=[
                Entity(name="Lotus Development Corporation"),
                Entity(name="the Lotus menu command hierarchy"),
            ],
        )
        copyrightable = Statement.new(
            predicate="{work} was copyrightable",
            terms=[Entity(name="the Lotus menu command hierarchy")],
        )
        left = FactorGroup(sequence=[copyrightable, copyright_registered])
        right = FactorGroup(
            sequence=[
                Statement.new(
                    predicate="{work} was copyrightable",
                    terms=[Entity(name="the Java API")],
                )
            ]
        )
        context = next(left.likely_contexts(right))
        assert (
            context.get_factor(
                Entity(name="the Lotus menu command hierarchy")
            ).short_string
            == Entity(name="the Java API").short_string
        )

    def test_likely_context_from_factor_meaning(self):
        left = Statement.new(
            predicate="{part} provided the means by which users controlled and operated {whole}",
            terms=[Entity(name="the Java API"), Entity(name="the Java language")],
        )
        right = Statement.new(
            predicate="{part} provided the means by which users controlled and operated {whole}",
            terms=[
                Entity(name="the Lotus menu command hierarchy"),
                Entity(name="Lotus 1-2-3"),
            ],
        )
        likely = left._likely_context_from_meaning(right, context=ContextRegister())

        assert (
            likely.get_factor(Entity(name="the Java API")).short_string
            == Entity(name="the Lotus menu command hierarchy").short_string
        )

    def test_union_one_generic_not_matched(self):
        """
        Here, both FactorGroups have "fact that <> was a computer program".
        But they each have another generic that can't be matched:
        that <the Java API> was a literal element of <the Java language>
        and
        that <the Lotus menu command hierarchy> provided the means by
        which users controlled and operated <Lotus 1-2-3>

        Tests that Factors from "left" should be keys and Factors from "right" values.
        """
        language_program = Statement.new(
            predicate="{program} was a computer program",
            terms=[Entity(name="the Java language")],
        )
        lotus_program = Statement.new(
            predicate="{program} was a computer program",
            terms=[Entity(name="Lotus 1-2-3")],
        )

        controlled = Statement.new(
            predicate="{part} provided the means by which users controlled and operated {whole}",
            terms=[
                Entity(name="the Lotus menu command hierarchy"),
                Entity(name="Lotus 1-2-3"),
            ],
        )
        part = Statement.new(
            predicate="{part} was a literal element of {whole}",
            terms=[Entity(name="the Java API"), Entity(name="the Java language")],
        )

        left = FactorGroup(sequence=[lotus_program, controlled])
        right = FactorGroup(sequence=[language_program, part])

        new = left | right
        text = (
            "that <the Lotus menu command hierarchy> was a "
            "literal element of <Lotus 1-2-3>"
        )
        assert text in new[0].short_string


class TestCompareRegisters:
    def test_same_register_one_term(self):
        left = ContextRegister.from_lists(
            [Entity(name="Odysseus")], [Entity(name="Ulysses")]
        )
        right = ContextRegister.from_lists(
            [Entity(name="Odysseus")], [Entity(name="Ulysses")]
        )
        assert right.means(left)

    def test_not_same_register_one_term(self):
        left = ContextRegister.from_lists(
            [Entity(name="Odysseus")], [Entity(name="Ulysses")]
        )
        right = ContextRegister.from_lists(
            [Entity(name="Odysseus")], [Entity(name="Jason")]
        )
        assert not right.means(left)


class TestChangeRegisters:
    def test_reverse_key_and_value_of_register(self):
        left = Entity(name="Siskel")
        right = Entity(name="Ebert")

        register = ContextRegister.from_lists([left], [right])

        assert len(register.keys()) == 1
        assert register.get("<Siskel>").name == "Ebert"

        new = register.reversed()
        assert new.get("<Ebert>").name == "Siskel"

    def test_factor_pairs(self):
        register = ContextRegister.from_lists(
            [Entity(name="apple"), Entity(name="lemon")],
            [Entity(name="pear"), Entity(name="orange")],
        )
        gen = register.factor_pairs()
        assert next(gen)[0].name == "apple"

    def test_no_iterables_in_register(self):
        left = FactorGroup(sequence=[])
        right = FactorGroup(sequence=[])
        context = ContextRegister()
        with pytest.raises(TypeError):
            context.insert_pair(left, right)
