import pytest

from authorityspoke.nettlesome.terms import ContextRegister
from authorityspoke.nettlesome.entities import Entity
from authorityspoke.nettlesome.factors import AbsenceOf
from authorityspoke.nettlesome.statements import Statement, Assertion


class TestAssertion:
    namespaces = Statement.new(
        predicate="{concept} was one honking great idea",
        terms=[Entity(name="namespaces", plural=True)],
    )
    generic_authority = Assertion(
        statement=namespaces, authority=Entity(name="Twitter user")
    )
    specific_authority = Assertion(
        statement=namespaces, authority=Entity(name="Tim Peters", generic=False)
    )
    no_authority = Assertion(statement=namespaces, authority=None)
    absent_authority = AbsenceOf(
        absent=Assertion(statement=namespaces, authority=Entity(name="a historian"))
    )
    generic_generic_authority = Assertion(
        statement=namespaces, authority=Entity(name="Twitter user"), generic=True
    )

    def test_dictum_string(self):
        assert "<namespaces> were one honking great idea" in str(self.generic_authority)

    def test_generic_string(self):
        assert str(self.generic_generic_authority).startswith("<the assertion")

    def test_include_of_in_string(self):
        fact = Statement.new(
            predicate="{suspect} stole bread", terms=[Entity(name="Valjean")]
        )
        accusation = Assertion(statement=fact, authority=Entity(name="Javert"))
        assert (
            "the assertion, by <Javert>, of the statement that <Valjean> stole bread"
            in str(accusation)
        )

    def test_string_absent(self):
        assert "absence of the assertion" in str(self.absent_authority)

    def test_means_self(self):
        assert self.generic_authority.means(self.generic_authority)

    def test_means_self_with_no_authority(self):
        assert self.no_authority.means(self.no_authority)

    def test_means_self_with_specific_authority(self):
        assert self.specific_authority.means(self.specific_authority)

    def test_not_same_meaning(self):
        assert not self.generic_authority.means(self.no_authority)

    def test_not_same_meaning_None_on_left(self):
        assert not self.no_authority.means(self.generic_authority)

    def test_not_same_meaning_specific_entity(self):
        assert not self.specific_authority.means(self.no_authority)

    def test_not_same_meaning_None_on_left_specific_entity(self):
        assert not self.no_authority.means(self.specific_authority)

    def test_no_authority_implies_none(self):
        assert self.no_authority.implies(self.no_authority)

    def test_generic_authority_implies_none(self):
        assert self.generic_authority.implies(self.no_authority)

    def test_no_implication_of_specific(self):
        assert not self.generic_authority.implies(self.specific_authority)

    def test_implication_by_specific(self):
        assert self.specific_authority.implies(self.generic_authority)

    def test_no_implication_of_specific_by_none(self):
        assert not self.no_authority.implies(self.specific_authority)

    def test_implication_of_none_by_specific(self):
        assert self.specific_authority.implies(self.no_authority)

    def test_implies_self(self):
        assert self.generic_authority.implies(self.generic_authority)

    def test_no_implication_no_authority(self):
        assert not self.no_authority.implies(self.generic_authority)

    def test_new_context(self):
        context = ContextRegister()
        context.insert_pair(
            Entity(name="Twitter user"),
            Entity(name="Python Software Foundation", generic=False),
        )
        new = self.generic_authority.new_context(context)
        assert "by Python" in str(new)


class TestInterchangeable:
    identical = Statement.new(
        predicate="{god1} was identical with {god2}",
        terms=[Entity(name="Dionysus"), Entity(name="Osiris")],
    )
    generic_authority = Assertion(
        statement=identical, authority=Entity(name="a historian")
    )
    specific_authority = Assertion(
        statement=identical, authority=Entity(name="Herodotus", generic=False)
    )
    no_authority = Assertion(statement=identical, authority=None)

    def test_means_self(self):
        assert self.generic_authority.means(self.generic_authority)

    def test_means_self_with_no_authority(self):
        assert self.no_authority.means(self.no_authority)

    def test_means_self_with_specific_authority(self):
        assert self.specific_authority.means(self.specific_authority)

    def test_not_same_meaning(self):
        assert not self.generic_authority.means(self.no_authority)

    def test_not_same_meaning_None_on_left(self):
        assert not self.no_authority.means(self.generic_authority)

    def test_not_same_meaning_specific_entity(self):
        assert not self.specific_authority.means(self.no_authority)

    def test_not_same_meaning_None_on_left_specific_entity(self):
        assert not self.no_authority.means(self.specific_authority)

    def test_no_authority_implies_none(self):
        assert self.no_authority.implies(self.no_authority)

    def test_generic_authority_implies_none(self):
        assert self.generic_authority.implies(self.no_authority)

    def test_no_implication_of_specific(self):
        assert not self.generic_authority.implies(self.specific_authority)

    def test_implication_by_specific(self):
        assert self.specific_authority.implies(self.generic_authority)

    def test_no_implication_of_specific_by_none(self):
        assert not self.no_authority.implies(self.specific_authority)

    def test_implication_of_none_by_specific(self):
        assert self.specific_authority.implies(self.no_authority)

    def test_implies_self(self):
        assert self.generic_authority.implies(self.generic_authority)

    def test_no_implication_no_authority(self):
        assert not self.no_authority.implies(self.generic_authority)

    def test_same_because_interchangeable(self, make_assertion):
        assert make_assertion["plotted_per_alice"].means(
            make_assertion["plotted_per_craig"]
        )
        assert make_assertion["plotted_per_craig"].means(
            make_assertion["plotted_per_alice"]
        )

    def test_different_because_not_interchangeable(self, make_assertion):
        assert not make_assertion["plotted_per_alice"].means(
            make_assertion["plotted_per_bob"]
        )
        assert not make_assertion["plotted_per_bob"].means(
            make_assertion["plotted_per_alice"]
        )


class TestComplex:
    @pytest.mark.parametrize(
        "left, right, expected",
        [
            ("generic", "generic", True),
            ("no", "no", True),
            ("specific", "specific", True),
            ("generic", "specific", False),
            ("specific", "generic", False),
            ("specific", "no", False),
        ],
    )
    def test_Assertions_same_meaning(self, make_assertion, left, right, expected):
        assert (
            make_assertion[f"{left}_authority"].means(
                make_assertion[f"{right}_authority"]
            )
            is expected
        )
        assert (
            make_assertion[f"{left}_authority_reversed"].means(
                make_assertion[f"{right}_authority"]
            )
            is expected
        )
        assert (
            make_assertion[f"{left}_authority"].means(
                make_assertion[f"{right}_authority_reversed"]
            )
            is expected
        )
        assert (
            make_assertion[f"{left}_authority_reversed"].means(
                make_assertion[f"{right}_authority_reversed"]
            )
            is expected
        )

    @pytest.mark.parametrize(
        "left, right, expected",
        [
            ("no", "no", True),
            ("no", "generic", False),
            ("no", "specific", False),
            ("generic", "generic", True),
            ("generic", "no", True),
            ("generic", "specific", False),
            ("specific", "specific", True),
            ("specific", "generic", True),
            ("specific", "no", True),
        ],
    )
    def test_Assertions_imply(self, make_assertion, left, right, expected):
        assert (
            make_assertion[f"{left}_authority"].implies(
                make_assertion[f"{right}_authority"]
            )
            is expected
        )
        assert (
            make_assertion[f"{left}_authority_reversed"].implies(
                make_assertion[f"{right}_authority"]
            )
            is expected
        )
        assert (
            make_assertion[f"{left}_authority"].implies(
                make_assertion[f"{right}_authority_reversed"]
            )
            is expected
        )
        assert (
            make_assertion[f"{left}_authority_reversed"].implies(
                make_assertion[f"{right}_authority_reversed"]
            )
            is expected
        )
