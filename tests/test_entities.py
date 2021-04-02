import pytest

from marshmallow.exceptions import ValidationError

from nettlesome.terms import ContextRegister
from nettlesome.entities import Entity
from nettlesome.statements import Statement

from authorityspoke.io import readers


class TestMakeEntities:
    def test_make_entity_from_str_without_mentioned(self):
        """
        This fails because it needs to look up the string factor_records
        in a "mentioned" list, but no "mentioned" parameter is given.
        """
        with pytest.raises(ValidationError):
            print(readers.read_factor(record="Bradley"))

    def test_conversion_to_generic(self, make_entity):
        e = make_entity
        assert e["motel_specific"].generic is False
        new = e["motel_specific"].make_generic()
        assert new.generic is True

    def test_repr_equal_after_make_generic(self, make_entity):
        """
        see the docstring for :meth:`Factor._import_to_mapping`
        for an explanation of what led to __repr__s being
        compared for equality instead of the underlying objects.
        """
        e = make_entity
        motel = e["motel"]
        motel_b = motel.make_generic()
        assert repr(motel) == repr(motel_b)

    def test_new_context(self, make_entity):

        changes = ContextRegister.from_lists(
            [make_entity["motel"], make_entity["watt"]],
            [Entity("Death Star"), Entity("Darth Vader")],
        )
        motel = make_entity["motel"]
        assert motel.new_context(changes) == changes.get_factor(make_entity["motel"])


class TestSameMeaning:
    def test_specific_to_generic_different_object(self, make_entity):
        e = make_entity
        motel = e["motel_specific"]
        motel_b = motel.make_generic()
        assert motel is not motel_b
        assert not motel == motel_b

    def test_equality_generic_entities(self, make_entity):
        e = make_entity
        assert e["motel"].means(e["trees"])
        assert not e["motel"] == e["trees"]

    def test_entity_does_not_mean_statement(self):
        entity = Entity("Bob")
        statement = Statement("$person loves ice cream", terms=entity)
        assert not entity.means(statement)
        assert not statement.means(entity)


class TestImplication:
    def test_implication_of_generic_entity(self, make_entity):
        assert make_entity["motel_specific"] > make_entity["trees"]

    def test_generic_entity_does_not_imply_specific_and_different(self, make_entity):
        assert not make_entity["motel_specific"] < make_entity["trees"]

    def test_implication_same_except_generic(self, make_entity):
        assert make_entity["motel_specific"] > make_entity["motel"]

    def test_generic_entity_does_not_imply_specific_and_same(self, make_entity):
        assert not make_entity["motel_specific"] < make_entity["motel"]

    def test_same_entity_not_ge(self, make_entity):
        assert not make_entity["motel"] > make_entity["motel"]

    def test_implication_subclass(self, make_entity):
        assert make_entity["tree_search_specific"] >= make_entity["motel"]
        assert make_entity["tree_search"] > make_entity["motel"]

    def test_plural_true(self, make_opinion_with_holding):
        """
        holding_feist.json has an entity with the name "Rural's telephone listings"
        and "plural": true
        """
        feist = make_opinion_with_holding["feist_majority"]
        assert any(entity.plural is True for entity in feist.generic_terms())

    def test_implies_concrete_with_same_name(self):
        concrete = Entity("Bob", generic=False)
        other = Entity("Bob", generic=False)
        assert concrete.implies(other)
        assert concrete >= other
        assert not concrete > other

    def test_implication_concrete_with_different_name(self):
        concrete = Entity("Bob", generic=False)
        generic = Entity("Barb")
        assert concrete.implies(generic)
        assert concrete > generic
        assert concrete >= generic

    def test_entity_does_not_imply_statement(self):
        entity = Entity("Bob")
        statement = Statement("$person loves ice cream", terms=entity)
        assert not entity.implies(statement)
        assert not statement.implies(entity)
        assert not entity >= statement
        assert not statement >= entity
        assert not entity > statement
        assert not statement > entity


class TestContradiction:
    def test_error_contradiction_with_non_factor(self, make_entity, make_predicate):
        with pytest.raises(TypeError):
            assert make_entity["trees"].contradicts(make_predicate["p3"])

    def test_no_contradiction_of_other_factor(self, make_entity, watt_factor):
        assert not make_entity["trees"].contradicts(make_entity["watt"])
        assert not make_entity["trees"].contradicts(watt_factor["f1"])
