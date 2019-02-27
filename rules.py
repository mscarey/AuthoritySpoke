import json
import pathlib
import operator

from types import MappingProxyType

from typing import Dict, List, Set, Tuple
from typing import Iterable, Iterator, Mapping
from typing import Callable, Generator, Optional, Union

from dataclasses import dataclass

from enactments import Enactment
from spoke import Factor


def evolve_match_list(
    available: Iterable[Factor],
    need_matches: Iterable[Factor],
    comparison: Callable[[Factor, Factor], bool],
    prior_matches: List[Dict[Factor, Optional[Factor]]],
) -> List[Dict[Factor, Optional[Factor]]]:

    """
    Takes all the tuples of entity assignments in prior_matches, and
    updates them with every consistent tuple of entity assignments
    that would cause every Factor in need_matches to be related to
    a Factor in "available" by the relation described by "comparison".
    """  # TODO: update docstring

    if isinstance(available, Factor):
        available = (available,)
    if isinstance(need_matches, Factor):
        need_matches = (need_matches,)

    new_matches = []
    for m in prior_matches:
        for y in find_matches(available, need_matches, MappingProxyType(m), comparison):
            y = dict(y)
            if all(existing_dict != y for existing_dict in new_matches):
                new_matches.append(y)
    return new_matches


@dataclass(frozen=True)
class Procedure(Factor):
    """A (potential) rule for courts to use in resolving litigation. Described in
    terms of inputs and outputs, and also potentially "even if" factors, which could
    be considered "failed undercutters" in defeasible logic.

    Input factors are not treated as potential undercutters.
    Instead, they're assumed to be additional support in favor of the output.
    If a factor is relevant both as support for the output and as a potential
    undercutter, include it in both 'inputs' and 'despite'."""

    outputs: Tuple[Factor, ...]
    inputs: Tuple[Factor, ...]
    despite: Tuple[Factor, ...]

    @classmethod
    def new(
        cls,
        outputs: Union[Factor, Iterable[Factor]],
        inputs: Union[Factor, Iterable[Factor]] = (),
        despite: Union[Factor, Iterable[Factor]] = (),
    ):
        def wrap_with_tuple(item) -> Tuple[Factor, ...]:
            if isinstance(item, Iterable):
                return tuple(sorted(item, key=repr))
            return (item,)

        outputs = wrap_with_tuple(outputs)
        inputs = wrap_with_tuple(inputs)
        despite = wrap_with_tuple(despite)

        for group in (outputs, inputs, despite):
            for factor_obj in group:
                if not isinstance(factor_obj, Factor):
                    raise TypeError(
                        "Input, Output, and Despite groups must contain "
                        + "only subclasses of Factor, but "
                        + f"{factor_obj} was type {type(factor_obj)}"
                    )
        return cls(outputs, inputs, despite)

    def __eq__(self, other: "Procedure") -> bool:
        """Determines if the two procedures have all the same factors
        with the same entities in the same roles, not whether they're
        actually the same Python object."""

        if not isinstance(other, Factor):
            raise TypeError(
                f"__eq__ not supported between instances of "
                + f"'{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )

        if not isinstance(other, self.__class__):
            return False

        if len(other) != len(self):  # redundant?
            return False

            # Verifying that every factor in self is in other.
            # Also verifying that every factor in other is in self.
        groups = ("outputs", "inputs", "despite")
        matchlist = [{}]
        for group in groups:
            new_matchlist = []
            for matches in matchlist:
                for answer in self.compare_factors(
                    matches, set(self.__dict__[group]), other.__dict__[group], operator.eq
                ):
                    new_matchlist.append(answer)
            matchlist = new_matchlist

        if not bool(matches):
            return False

        # Now doing the same thing in reverse
        matchlist = [{}]
        for group in groups:
            new_matchlist = []
            for matches in matchlist:
                for answer in self.compare_factors(
                    matches, set(other.__dict__[group]), self.__dict__[group], operator.eq
                ):
                    new_matchlist.append(answer)
            matchlist = new_matchlist
        return bool(matchlist)

    def compare_factors(
        self, matches, need_matches, available_for_matching, comparison
    ) -> Dict[Factor, Optional[Factor]]:
        """
        Determines whether all factors in need_matches have the relation
        "comparison" with a factor in available_for_matching, with matching
        entity slots.
        """

        if not need_matches:
            # This seems to allow duplicate values in
            # Procedure.output, .input, and .despite, but not in
            # attributes of other kinds of Factors. Likely cause
            # of bugs.
            if self._update_mapping(
                dict(matches), tuple(matches.keys()), tuple(matches.values())
            ):
                yield matches
        else:
            self_factor = need_matches.pop()
            for other_factor in available_for_matching:
                if comparison(self_factor, other_factor):
                    new_matches = dict(matches)
                    new_matches[self_factor] = other_factor
                    for answer in self.compare_factors(
                        MappingProxyType(new_matches),
                        need_matches,
                        available_for_matching,
                        comparison,
                    ):
                        yield answer

    def __ge__(self, other: "Procedure") -> bool:
        """
        Tests whether the assertion that self applies in some cases
        implies that the procedure "other" applies in some cases.

        When self and other are holdings that both apply in SOME cases:

        Self does not imply other if any input of other
        is not equal to or implied by some input of self.

        Self does not imply other if any output of other
        is not equal to or implied by some output of self.

        Self does not imply other if any despite of other
        is not equal to or implied by some despite or input of self.
        """

        if not isinstance(other, Factor):
            raise TypeError(
                f"'Implies' not supported between instances of "
                + f"'{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )

        if not isinstance(other, self.__class__):
            return False

        despite_or_input = {*self.despite, *self.inputs}

        matchlist = [{context: None for context in self.get_context_factors()}]
        matchlist = evolve_match_list(self.inputs, other.inputs, operator.ge, matchlist)
        matchlist = evolve_match_list(
            self.outputs, other.outputs, operator.ge, matchlist
        )
        matchlist = evolve_match_list(
            despite_or_input, other.despite, operator.ge, matchlist
        )

        return bool(matchlist)

    def __gt__(self, other: "Procedure") -> bool:
        if self == other:
            return False
        return self >= other

    def __hash__(self):
        return hash(
            (
                self.__class__.__name__,
                *[v for v in self.__dict__.values() if not isinstance(v, set)],
            )
        )

    def __len__(self):
        """
        Returns the number of entities that need to be specified for the procedure.
        Works by flattening a series of "markers" fields from the Context objects.
        """

        return len(
            set(
                marker
                for markertuple in (
                    factor.entity_context
                    for factor in self.factors_all()
                    if hasattr(factor, "entity_context")
                )
                for marker in markertuple
            )
        )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(outputs=("
            + f"{', '.join(repr(factor) for factor in self.outputs)}), "
            + f"inputs=({', '.join(repr(factor) for factor in self.inputs)}), "
            + f"despite=({', '.join(repr(factor) for factor in self.despite)}))"
        )

    def __str__(self):
        text = "Procedure:"
        if self.inputs:
            text += "\nSupporting inputs:"
            for f in self.inputs:
                text += "\n" + str(f)
        if self.despite:
            text += "\nDespite:"
            for f in self.despite:
                text += "\n" + str(f)
        if self.outputs:
            text += "\nOutputs:"
            for f in self.outputs:
                text += "\n" + str(f)
        return text

    def contradiction_between_outputs(
        self, other: "Procedure", m: Tuple[int, ...]
    ) -> bool:
        """
        Returns a boolean indicating if any factor assignment can be found that
        makes a factor in the output of other contradict a factor in the
        output of self.
        """
        return any(
            other_factor.contradicts(self_factor)
            and (
                check_entity_consistency(other_factor, self_factor, m)
                for self_factor in self.outputs
            )
            for other_factor in other.outputs
            for self_factor in self.outputs
        )

    def factors_all(self) -> Set[Factor]:
        """Returns a set of all factors."""

        inputs = self.inputs or set()
        despite = self.despite or set()
        return {*self.outputs, *inputs, *despite}

    def factors_sorted(self) -> List[Factor]:
        """Sorts the procedure's factors into an order that will always be
        the same for the same set of factors, but that doesn't correspond to
        whether the factors are inputs, outputs, or "even if" factors."""

        return sorted(self.factors_all(), key=repr)

    def find_consistent_factors(
        self,
        for_matching: Tuple[Factor],
        need_matches: Iterable[Factor],
        matches: Mapping[Factor, Optional[Factor]],
    ) -> Iterator[Mapping[Factor, Optional[Factor]]]:
        """
        Recursively searches for a list of entity assignments that can
        cause all of 'other_factors' to not contradict any of the factors in
        self_matches. Calls a new instance of consistent_entity_combinations
        for each such list that is found. It finally returns
        matchlist when all possibilities have been searched.
        """

        if not need_matches:
            yield dict(matches)
        else:
            need_matches = list(need_matches)
            n = need_matches.pop()
            valid_combinations = n.consistent_entity_combinations(for_matching, matches)
            for c in valid_combinations:
                matches_next = dict(matches)
                for i in c:
                    matches_next[i] = c[i]
                for m in self.find_consistent_factors(
                    for_matching, tuple(need_matches), MappingProxyType(matches_next)
                ):
                    yield m

    def get_context_factors(self) -> Set[Factor]:
        return set(
            context
            for factor in self.factors_all()
            for context in factor.entity_context
        )

    def contradicts_some_to_all(self, other: "Procedure") -> bool:
        """
        Tests whether the assertion that self applies in SOME cases
        contradicts that the procedure "other" applies in ALL cases,
        where at least one of the holdings is mandatory.

        :param other:
        """

        if not isinstance(other, self.__class__):
            return False

        self_despite_or_input = {*self.despite, *self.inputs}

        # For self to contradict other, every input of other
        # must be implied by some input or despite factor of self.
        matchlist = [{context: None for context in self.get_context_factors()}]
        matchlist = evolve_match_list(
            self_despite_or_input, other.inputs, operator.ge, matchlist
        )

        # For self to contradict other, some output of other
        # must be contradicted by some output of self.

        return any(self.contradiction_between_outputs(other, m) for m in matchlist)

    def implies_all_to_all(self, other: "Procedure") -> bool:
        """
        Tests whether the assertion that self applies in ALL cases
        implies that the procedure "other" applies in ALL cases.

        For self to imply other, every input of self
        must be implied by some input of other.

        Self does not imply other if any output of other
        is not equal to or implied by some output of self.

        Self does not imply other if any despite of other
        contradicts an input of self.

        :param other:
        """

        if not isinstance(other, self.__class__):
            return False

        if self == other:
            return True
        matchlist = [{context: None for context in self.get_context_factors()}]
        matchlist_from_other = evolve_match_list(
            other.inputs, self.inputs, operator.ge, matchlist
        )
        matchlist = self.get_foreign_match_list(matchlist_from_other)
        matchlist = evolve_match_list(
            self.outputs, other.outputs, operator.ge, matchlist
        )

        # For every factor in other, find the permutations of entity slots
        # that are consistent with matchlist and that don't cause the factor
        # to contradict any factor of self.

        return any(
            any(
                match
                for match in self.find_consistent_factors(self.inputs, other.despite, m)
            )
            for m in matchlist
        )

    def get_foreign_match_list(
        self, foreign: List[Dict[Factor, Factor]]
    ) -> List[Dict[Factor, Factor]]:
        """Gets a version of matchlist in which the indices represent
        other's entity slots and the values represent self's entity slots.

        Compare this to the regular matchlist objects, in which the
        indices represent self's entity slots and the values represent
        other's."""  # TODO: docstring

        def get_foreign_match(
            match: Dict[Factor, Factor]
        ) -> Optional[Dict[Factor, Factor]]:
            # TODO: write test for multiple keys of match with same value (other than None)
            return {v: k for k, v in match.items() if v is not None}

        return [
            get_foreign_match(match)
            for match in foreign
            if get_foreign_match(match) is not None
        ]

    def implies_all_to_some(self, other: "Procedure") -> bool:
        """
        This is a different process for checking whether one procedure implies another,
        used when the list of self's inputs is considered an exhaustive list of the
        circumstances needed to invoke the procedure (i.e. when the rule "always" applies
        when the inputs are present), but the list of other's inputs is not exhaustive.

        For self to imply other, every input of self must not be
        contradicted by any input of other.

        For self to imply other, every output of other
        must be equal to or implied by some output of self.

        Self does not imply other if any despite factors of other
        are contradicted by inputs of self.

        :param other:
        """

        if not isinstance(other, self.__class__):
            return False

        matchlist = [{context: None for context in self.get_context_factors()}]
        matchlist = evolve_match_list(
            self.outputs, other.outputs, operator.ge, matchlist
        )

        # Not checking whether despite factors of other are
        # contradicted by inputs of self, assuming they can't be
        # because they would be contradicted by inputs of other.

        # For every factor in other, find the permutations of entity slots
        # that are consistent with matchlist and that don't cause the factor
        # to contradict any factor of self.

        other_despite_or_input = {*other.despite, *other.inputs}

        return any(
            any(
                match
                for match in self.find_consistent_factors(
                    other_despite_or_input, self.inputs, MappingProxyType(m)
                )
            )
            for m in matchlist
        )

    def contradicts(self, other):
        raise NotImplementedError(
            "Procedures do not contradict one another unless one of them ",
            "applies in 'ALL' cases. Consider using the ",
            "'contradicts_some_to_all' method.",
        )


@dataclass()
class Rule:
    """
    A statement in which a court posits a legal rule as authoritative,
    deciding some aspect of the current litigation but also potentially
    binding future courts to follow the rule. When holdings appear in
    judicial opinions they are often hypothetical and don't necessarily
    imply that the court accepts the factual assertions or other factors
    that make up the inputs or outputs of the procedure mentioned in the
    holding.
    """

    def __len__(self):
        return 0

    @staticmethod
    def holdings_from_json(self, filename: str) -> Dict["Rule", Tuple[Factor, ...]]:
        """Creates a set of holdings from a JSON file in the input subdirectory,
        adds those holdings to self.holdings, and returns self.holdings."""

        def dict_from_input_json(filename: str) -> Tuple[Dict, Dict]:
            """
            Makes entity and holding dicts from a JSON file in the format that lists
            mentioned_entities followed by a list of holdings.
            """

            path = pathlib.Path("input") / filename
            with open(path, "r") as f:
                case = json.load(f)
            return case["mentioned_factors"], case["holdings"]

        entity_list, holding_list = self.dict_from_input_json(filename)
        for record in holding_list:
            factor_groups = {"inputs": set(), "outputs": set(), "despite": set()}
            for factor_type in factor_groups:
                factor_list = record.get(factor_type, [])
                if not isinstance(factor_list, list):
                    factor_list = [factor_list]
                for factor_dict in factor_list:
                    factor = Factor.from_dict(factor_dict)
                    factor_groups[factor_type].add(factor)
            procedure = Procedure(
                inputs=factor_groups["inputs"],
                outputs=factor_groups["outputs"],
                despite=factor_groups["despite"],
            )

            enactment_groups = {"enactments": set(), "enactments_despite": set()}
            for enactment_type in enactment_groups:
                enactment_list = record.get(enactment_type, [])
                if isinstance(enactment_list, dict):
                    enactment_list = [enactment_list]
                for enactment_dict in enactment_list:
                    enactment_groups[enactment_type].add(
                        Enactment.from_dict(enactment_dict)
                    )

            holding = ProceduralRule(
                procedure=procedure,
                enactments=enactment_groups["enactments"],
                enactments_despite=enactment_groups["enactments_despite"],
                mandatory=record.get("mandatory", False),
                universal=record.get("universal", False),
                rule_valid=record.get("rule_valid", True),
                decided=record.get("decided", True),
            )
            # There's currently no way to get the entities from the Predicates.
            self.holdings[holding] = entities
        return self.holdings


@dataclass()
class ProceduralRule(Rule):

    """
    procedure (Procedure): optional because a holding can contain
    an attribution instead of a holding

    enactments (Union[Enactment, Iterable[Enactment]]): the set of
    enactments cited as authority for the holding

    enactments_despite (Union[Enactment, Iterable[Enactment]]):
    the set of enactments specifically cited as failing to undercut
    the holding

    mandatory (bool): whether the procedure is mandatory for the
    court to apply whenever the holding is properly invoked. False
    may be used for procedures deemed "discretionary".
    Not applicable to attributions.

    universal (bool): True if the procedure is applicable whenever
    its inputs are present. False means that the procedure is
    applicable in "some" situation where the facts are present.
    Not applicable to attributions.

    rule_valid (bool): True means the holding asserts the procedure
    is a valid legal rule. False means it's not a valid legal
    rule.

    decided (bool): False means that it should be deemed undecided
    whether the rule is valid, and thus can have the effect of
    overruling prior holdings finding the rule to be either
    valid or invalid. Seemingly, decided=False should render the
    "rule_valid" flag irrelevant. Note that if an opinion merely
    says the court is not deciding whether a procedure or attribution
    is valid, there is no holding, and no Rule object should be
    created. Deciding not to decide a rule's validity is not the same
    thing as deciding that a rule is undecided.
    """

    procedure: Procedure
    enactments: Union[Enactment, Iterable[Enactment]] = frozenset([])
    enactments_despite: Union[Enactment, Iterable[Enactment]] = frozenset([])
    mandatory: bool = False
    universal: bool = False
    rule_valid: bool = True
    decided: bool = True

    def __post_init__(self):
        if isinstance(self.enactments, Enactment):
            object.__setattr__(self, "enactments", frozenset((self.enactments,)))
        if isinstance(self.enactments_despite, Enactment):
            object.__setattr__(
                self, "enactments_despite", frozenset((self.enactments_despite,))
            )
        object.__setattr__(self, "enactments", frozenset(self.enactments))
        object.__setattr__(
            self, "enactments_despite", frozenset(self.enactments_despite)
        )

    def __str__(self):
        support = despite = None
        if self.enactments:
            support = "Based on this legislation:\n" + "\n".join(
                [str(e) for e in self.enactments]
            )
        if self.enactments_despite:
            despite = "Despite the following legislation:\n" + "\n".join(
                [str(e) for e in self.enactments_despite]
            )
        text = (
            "Rule:\n"
            + f"{support or ''}"
            + f"{despite or ''}"
            + f"\nIt is {'' if self.decided else 'not decided whether it is '}"
            + f"{str(self.rule_valid)} that in {'ALL' if self.universal else 'SOME'} cases "
            + f"where the inputs of the following procedure are present, the court "
            + f"{'MUST' if self.mandatory else 'MAY'} accept the procedure's output(s):\n"
        )
        text += str(self.procedure)
        return text

    def __len__(self):
        """Returns the number of entities needed to provide context
        for the Rule, which currently is just the entities needed
        for the Rule's Procedure."""

        return len(self.procedure)

    def contradicts_if_valid(self, other) -> bool:
        """Determines whether self contradicts other,
        assuming that rule_valid and decided are
        True for both Rules."""

        if not isinstance(other, self.__class__):
            return False

        if not self.mandatory and not other.mandatory:
            return False

        if not self.universal and not other.universal:
            return False

        if other.universal and not self.universal:
            return self.procedure.contradicts_some_to_all(other.procedure)

        if self.universal and not other.universal:
            return other.procedure.contradicts_some_to_all(self.procedure)

        # This last option is for the ALL contradicts ALL case (regardless of MAY or MUST)
        # It could use more tests.

        return other.procedure.contradicts_some_to_all(
            self.procedure
        ) or self.procedure.contradicts_some_to_all(other.procedure)

    def implies_if_decided(self, other) -> bool:

        """Simplified version of the __ge__ implication function
        covering only cases where decided is True for both Rules,
        although rule_valid can be False."""

        if self.rule_valid and other.rule_valid:
            return self.implies_if_valid(other)

        if not self.rule_valid and not other.rule_valid:
            return other.implies_if_valid(self)

        # Looking for implication where self.rule_valid != other.rule_valid
        # is equivalent to looking for contradiction.

        # If decided rule A contradicts B, then B also contradicts A

        if other.rule_valid and not self.rule_valid:
            return self.contradicts_if_valid(other) or other.implies_if_valid(self)

        # if self.rule_valid and not other.rule_valid
        return other.contradicts_if_valid(self) or self.implies_if_valid(other)

    def implies_if_valid(self, other) -> bool:
        """Simplified version of the __ge__ implication function
        covering only cases where rule_valid and decided are
        True for both Rules."""

        if not isinstance(other, self.__class__):
            return False

        # If self relies for support on some enactment text that
        # other doesn't, then self doesn't imply other.

        if not all(
            any(other_e >= e for other_e in other.enactments) for e in self.enactments
        ):
            return False

        # If other specifies that it applies notwithstanding some
        # enactment not mentioned by self, then self doesn't imply other.

        if not all(
            any(e >= other_d for e in (self.enactments | self.enactments_despite))
            for other_d in other.enactments_despite
        ):
            return False

        if other.mandatory > self.mandatory:
            return False

        if other.universal > self.universal:
            return False

        if self.universal > other.universal:
            return self.procedure.implies_all_to_some(other.procedure)

        if other.universal:
            return self.procedure.implies_all_to_all(other.procedure)

        return self.procedure >= other.procedure

    def __gt__(self, other) -> bool:
        if self == other:
            return False
        return self >= other

    def __ge__(self, other) -> bool:
        """Returns a boolean indicating whether self implies other,
        where other is another Rule."""

        if not isinstance(other, self.__class__):
            raise TypeError(
                f"'Implies' not supported between instances of "
                + f"'{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )

        if self.decided and other.decided:
            return self.implies_if_decided(other)

        # A holding being undecided doesn't seem to imply that
        # any other holding is undecided, except itself and the
        # negation of itself.

        if not self.decided and not other.decided:
            return self == other or self == other.negated()

        # It doesn't seem that any holding being undecided implies
        # that any holding is decided, or vice versa.

        return False

    def __hash__(self):
        return hash(
            (
                self.__class__.__name__,
                *[v for v in self.__dict__.values() if not isinstance(v, set)],
            )
        )

    def negated(self):
        return ProceduralRule(
            procedure=self.procedure,
            enactments=self.enactments,
            enactments_despite=self.enactments_despite,
            mandatory=self.mandatory,
            universal=self.universal,
            rule_valid=not self.rule_valid,
            decided=self.decided,
        )

    def contradicts(self, other) -> bool:
        """
        A holding contradicts another holding if it implies
        that the other holding is false. Generally checked
        by testing whether self would imply other if
        other had an opposite value for rule_valid.
        """

        if not isinstance(other, self.__class__):
            raise TypeError(
                f"'Contradicts' not supported between instances of "
                + f"'{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )

        if self.decided and other.decided:
            return self >= other.negated()

        if not self.decided and not other.decided:
            return self == other or self == other.negated()

        # A decided holding doesn't "contradict" a previous
        # statement that any rule was undecided.

        if self.decided and not other.decided:
            return False

        # If holding A implies holding B, then the statement
        # that A is undecided contradicts the prior holding B.

        # if not self.decided and other.decided:
        return other.implies_if_decided(self)


class Attribution:
    """An assertion about the meaning of a prior Opinion. Either a user or an Opinion
    may make an Attribution to an Opinion. An Attribution may attribute either
    a Rule or a further Attribution."""

    pass
