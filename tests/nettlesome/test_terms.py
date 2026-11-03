import operator

import pytest
from pydantic import ValidationError

from authorityspoke.nettlesome.entities import Entity
from authorityspoke.nettlesome.predicates import Predicate
from authorityspoke.nettlesome.statements import Statement
from authorityspoke.nettlesome.terms import ContextRegister, TermSequence, means


class TestMakeEntities:
    def test_conversion_to_generic(self):
        jon = Entity(name="Jon Doe", generic=False)
        generic = jon.make_generic()
        assert generic.generic is True

    def test_wrapped_string(self):
        entity = Entity(name="the mummy")
        assert entity.wrapped_string == "<the mummy>"

    def test_context_register(self):
        """
        There will be a match because both object are :class:`.Term`.
        """
        left = Entity(name="peanut butter")
        right = Entity(name="jelly")
        update = left._context_registers(right, operator.ge)
        assert any(register is not None for register in update)

        update = left._context_registers(right, operator.le)
        expected = ContextRegister()
        expected.insert_pair(left, right)
        assert any(register == expected for register in update)

    def test_new_context(self):
        changes = ContextRegister.from_lists(
            [Entity(name="Death Star 3"), Entity(name="Kylo Ren")],
            [Entity(name="Death Star 1"), Entity(name="Darth Vader")],
        )
        place = Entity(name="Death Star 3")
        assert place.new_context(changes) == changes.get_factor(place)

    def test_register_for_matching_entities(self):
        known = ContextRegister()
        alice = Entity(name="Alice")
        craig = Entity(name="Craig")
        known.insert_pair(alice, craig)

        gen = alice._context_registers(other=craig, comparison=means, context=known)
        register = next(gen)
        assert register.get("<Alice>") == craig

    def test_term_sequence_from_one_term(self):
        entity = Entity(name="Austin")
        sequence = TermSequence(root=(entity,))
        assert sequence[0].name == entity.name

    def test_cannot_put_string_in_term_sequence(self):
        entity = Entity(name="Austin")
        with pytest.raises(ValidationError):
            TermSequence(root=(entity, "Dallas as a string"))


class TestSameMeaning:
    def test_equality_generic_entities(self):
        left = Entity(name="Bert")
        right = Entity(name="Ernie")
        assert left.means(right)
        assert not left == right

    def test_entity_does_not_mean_statement(self):
        entity = Entity(name="Bob")
        statement = Statement.new(predicate="{person} loves ice cream", terms=[entity])
        assert not entity.means(statement)
        assert not statement.means(entity)


class TestImplication:
    def test_implication_of_generic_entity(self):
        assert Entity(name="Specific Bob", generic=False) > Entity(name="Clara")

    def test_generic_entity_does_not_imply_specific_and_different(self):
        assert not Entity(name="Clara") > Entity(name="Specific Bob", generic=False)

    def test_generic_entity_does_not_imply_specific_and_same(self):
        assert not Entity(name="Clara") > Entity(name="Clara", generic=False)

    def test_same_entity_not_ge(self):
        assert not Entity(name="Clara") > Entity(name="Clara")

    def test_implies_concrete_with_same_name(self):
        concrete = Entity(name="Bob", generic=False)
        other = Entity(name="Bob", generic=False)
        assert concrete.implies(other)
        assert concrete >= other
        assert not concrete > other

    def test_implication_concrete_with_different_name(self):
        concrete = Entity(name="Bob", generic=False)
        generic = Entity(name="Barb")
        assert concrete.implies(generic)
        assert concrete > generic
        assert concrete >= generic

    def test_entity_does_not_imply_statement(self):
        entity = Entity(name="Bob")
        statement = Statement.new(predicate="{person} loves ice cream", terms=[entity])
        assert not entity.implies(statement)
        assert not statement.implies(entity)
        assert not entity >= statement
        assert not statement >= entity
        assert not entity > statement
        assert not statement > entity


class TestContradiction:
    def test_error_contradiction_with_non_factor(self):
        with pytest.raises(TypeError):
            assert Entity(name="Al").contradicts(Predicate(content="any text"))

    def test_no_contradiction_of_other_entity(self):
        assert not Entity(name="Al").contradicts(Entity(name="Ed"))
        assert not Entity(name="Al").contradicts(Statement.new(predicate="any text"))


class TestAdd:
    def test_union_not_valid_alias(self):
        with pytest.raises(TypeError):
            Entity(name="Al") | Entity(name="Ed")

    def test_add_generic(self):
        new = Entity(name="Al") + Entity(name="Ed")
        assert new.name == "Al"

    def test_no_adding_string(self):
        with pytest.raises(TypeError):
            Entity(name="Al") + "Ed"

    def test_add_generic_and_specific(self):
        new = Entity(name="Al") + Entity(name="Mister Ed", generic=False)
        assert new.name == "Mister Ed"

    def test_two_specifics_will_not_add(self):
        new = Entity(name="Inimitable", generic=False) + Entity(
            name="Original", generic=False
        )
        assert new is None

    def test_two_specifics_with_same_name_will_add(self):
        new = Entity(name="Identical", generic=False) + Entity(
            name="Identical", generic=False
        )
        assert new.name == "Identical"
