import operator

import pytest

from authorityspoke.comparisons import ContextRegister
from authorityspoke.factors import FactorGroup


class TestContextRegisters:
    def test_possible_context_without_empty_spaces(self, watt_factor, make_entity):
        left = watt_factor["f1"]
        right = watt_factor["f1"]
        contexts = list(left.possible_contexts(right))
        assert len(contexts) == 1
        assert contexts[0][make_entity["motel"]] == make_entity["motel"]

    def test_all_possible_contexts_identical_factor(self, watt_factor, make_entity):
        left = watt_factor["f2"]
        right = watt_factor["f2"]
        contexts = list(left.possible_contexts(right))
        assert len(contexts) == 2
        assert any(
            context[make_entity["watt"]] == make_entity["motel"] for context in contexts
        )

    def test_limited_possible_contexts_identical_factor(self, watt_factor, make_entity):
        left = watt_factor["f2"]
        right = watt_factor["f2"]
        context = {make_entity["motel"]: make_entity["motel"]}
        contexts = list(left.possible_contexts(right, context=context))
        assert len(contexts) == 1
        assert contexts[0][make_entity["watt"]] == make_entity["watt"]

    def test_context_register_empty(self, make_complex_fact, watt_factor):
        """
        Yields no context_register because the Entity in f1 doesn't imply
        the Fact in f_relevant_murder.
        """
        with pytest.raises(StopIteration):
            next(
                watt_factor["f1"]._context_registers(
                    make_complex_fact["f_relevant_murder"], operator.ge
                )
            )

    def test_context_register_valid(self, make_entity, watt_factor):
        assert next(
            watt_factor["f1"]._context_registers(
                watt_factor["f1_entity_order"], operator.le
            )
        ) == {make_entity["motel"]: make_entity["watt"],}

    def test_import_to_context_register(self, make_entity, watt_factor):
        f = watt_factor["f7"]
        left = ContextRegister(
            {
                watt_factor["f7"]: watt_factor["f7_swap_entities"],
                make_entity["motel"]: make_entity["trees"],
            }
        )
        right = ContextRegister({make_entity["trees"]: make_entity["motel"]})
        assert len(left.merged_with(right)) == 3

    def test_import_to_mapping_no_change(self, make_entity):
        old_mapping = ContextRegister({make_entity["motel"]: make_entity["trees"]})
        assert dict(
            old_mapping.merged_with({make_entity["motel"]: make_entity["trees"]})
        ) == {make_entity["motel"]: make_entity["trees"],}

    def test_import_to_mapping_conflict(self, make_entity):
        merged = ContextRegister(
            {make_entity["motel"]: make_entity["trees"]}
        ).merged_with(ContextRegister({make_entity["motel"]: make_entity["motel"]}))
        assert merged is None

    def test_import_to_mapping_reciprocal(self, watt_factor):
        mapping = ContextRegister({watt_factor["f7"]: watt_factor["f7"]}).merged_with(
            {watt_factor["f7_swap_entities"]: watt_factor["f7_swap_entities"]}
        )
        assert mapping[watt_factor["f7"]] == watt_factor["f7"]

    def test_registers_for_interchangeable_context(self, make_entity, watt_factor):
        """
        Test that _registers_for_interchangeable_context swaps the first two
        items in the ContextRegister
        """
        matches = ContextRegister(
            {
                make_entity["motel"]: make_entity["trees"],
                make_entity["trees"]: make_entity["motel"],
                make_entity["watt"]: make_entity["watt"],
            }
        )
        new_matches = [
            match
            for match in watt_factor["f7"]._registers_for_interchangeable_context(
                matches
            )
        ]
        assert (
            ContextRegister(
                {
                    make_entity["trees"]: make_entity["trees"],
                    make_entity["motel"]: make_entity["motel"],
                    make_entity["watt"]: make_entity["watt"],
                }
            )
            in new_matches
        )


class TestLikelyContext:
    def test_likely_context_one_factor(self, make_entity, watt_factor):
        left = watt_factor["f2"]
        right = watt_factor["f2"]
        context = next(left.likely_contexts(right))
        assert context[make_entity["motel"]] == make_entity["motel"]

    def test_likely_context_implication_one_factor(self, make_entity, watt_factor):
        left = watt_factor["f8"]
        right = watt_factor["f8_meters"]
        context = next(left.likely_contexts(right))
        assert context[make_entity["motel"]] == make_entity["motel"]

    def test_likely_context_two_factors(self, make_entity, watt_factor):
        left = FactorGroup((watt_factor["f9_swap_entities"], watt_factor["f2"]))
        right = watt_factor["f2"]
        context = next(left.likely_contexts(right))
        assert context[make_entity["motel"]] == make_entity["motel"]

    def test_likely_context_two_by_two(self, make_entity, watt_factor):
        left = FactorGroup((watt_factor["f9"], watt_factor["f2"]))
        right = FactorGroup(
            (watt_factor["f9_swap_entities"], watt_factor["f9_more_different_entity"])
        )
        context = next(left.likely_contexts(right))
        assert context[make_entity["motel"]] == make_entity["trees"]
