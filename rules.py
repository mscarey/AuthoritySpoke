import json
import pathlib
import operator

from types import MappingProxyType

from typing import Dict, List, Set, Tuple
from typing import Iterable, Iterator, Mapping
from typing import Callable, Optional, Union
from typing import NamedTuple

from dataclasses import dataclass

from enactments import Enactment
from file_import import log_mentioned_context
from spoke import Factor


class Relation(NamedTuple):
    need_matches: Tuple[Factor, ...]
    available: Tuple[Factor, ...]
    comparison: Callable


@dataclass(frozen=True)
class Procedure(Factor):
    """A (potential) rule for courts to use in resolving litigation. Described in
    terms of inputs and outputs, and also potentially "even if" factors, which could
    be considered "failed undercutters" in defeasible logic.

    Input factors are not treated as potential undercutters.
    Instead, they're assumed to be additional support in favor of the output.
    If a factor is relevant both as support for the output and as a potential
    undercutter, include it in both 'inputs' and 'despite'."""

    outputs: Iterable[Factor] = ()
    inputs: Iterable[Factor] = ()
    despite: Iterable[Factor] = ()
    absent: bool = False
    generic: bool = True
    name: Optional[str] = None

    def __post_init__(self):

        outputs = self.__class__.sort_in_tuple(self.outputs)
        inputs = self.__class__.sort_in_tuple(self.inputs)
        despite = self.__class__.sort_in_tuple(self.despite)

        groups = {"outputs": outputs, "inputs": inputs, "despite": despite}
        for group in groups:
            for factor_obj in groups[group]:
                if not isinstance(factor_obj, Factor):
                    raise TypeError(
                        "Input, Output, and Despite groups must contain "
                        + "only subclasses of Factor, but "
                        + f"{factor_obj} was type {type(factor_obj)}"
                    )
            object.__setattr__(self, group, groups[group])

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

            # Verifying that every factor in self is in other.
            # Also verifying that every factor in other is in self.
        groups = ("outputs", "inputs", "despite")
        matchlist = [{}]
        for group in groups:
            new_matchlist = []
            for matches in matchlist:
                for answer in self.compare_factors(
                    matches,
                    list(self.__dict__[group]),
                    other.__dict__[group],
                    operator.eq,
                ):
                    new_matchlist.append(answer)
            matchlist = new_matchlist

        if not bool(matchlist):
            return False

        # Now doing the same thing in reverse
        matchlist = [{}]
        for group in groups:
            new_matchlist = []
            for matches in matchlist:
                for answer in self.compare_factors(
                    matches,
                    list(other.__dict__[group]),
                    self.__dict__[group],
                    operator.eq,
                ):
                    new_matchlist.append(answer)
            matchlist = new_matchlist
        return bool(matchlist)

    def compare_factors(
        self,
        matches: Mapping,
        need_matches: List[Factor],
        available_for_matching: Tuple[Factor, ...],
        comparison: Callable,
    ) -> Iterator[Dict[Factor, Optional[Factor]]]:
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
            yield matches
        else:
            self_factor = need_matches.pop()
            for other_factor in available_for_matching:
                if comparison(self_factor, other_factor):
                    updated_mappings = iter(
                        self.update_mapping(
                            matches, (self_factor,), (other_factor,), comparison
                        )
                    )
                    for new_matches in updated_mappings:
                        if new_matches:
                            next_steps = iter(
                                self.compare_factors(
                                    new_matches,
                                    need_matches,
                                    available_for_matching,
                                    comparison,
                                )
                            )
                            for next_step in next_steps:
                                yield next_step

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

        despite_or_input = (*self.despite, *self.inputs)

        relations = (
            Relation(other.outputs, self.outputs, operator.le),
            Relation(other.inputs, self.inputs, operator.le),
            Relation(other.despite, despite_or_input, operator.le),
        )

        return bool(self.all_relation_matches(relations))

    def all_relation_matches(
        self, relations: Tuple[Relation, ...]
    ) -> List[Dict[Factor, Optional[Factor]]]:
        matchlist = [{}]
        for relation in relations:
            new_matchlist = []
            for matches in matchlist:
                for answer in self.compare_factors(
                    MappingProxyType(matches),
                    list(relation.need_matches),
                    relation.available,
                    relation.comparison,
                ):
                    new_matchlist.append(dict(answer))
            matchlist = new_matchlist
        return matchlist

    def __gt__(self, other: "Procedure") -> bool:
        if self == other:
            return False
        return self >= other

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

    def generic_factors(self) -> Dict[Factor, None]:
        """Returns an iterable of self's generic Factors,
        which must be matched to other generic Factors to
        perform equality tests between Factors."""

        return {
            generic: None
            for factor in self.factors_all()
            for generic in factor.generic_factors()
        }

    def contradicts_some_to_all(self, other: "Procedure") -> bool:
        """
        Tests whether the assertion that self applies in SOME cases
        contradicts that the procedure "other" applies in ALL cases,
        where at least one of the holdings is mandatory.

        :param other:
        """

        if not isinstance(other, self.__class__):
            return False

        self_despite_or_input = (*self.despite, *self.inputs)

        # For self to contradict other, every input of other
        # must be implied by some input or despite factor of self.
        relations = (Relation(other.inputs, self_despite_or_input, operator.le),)
        matchlist = self.all_relation_matches(relations)

        # For self to contradict other, some output of other
        # must be contradicted by some output of self.

        return any(self.contradiction_between_outputs(other, m) for m in matchlist)

    def implies_all_to_all(self, other: "Procedure") -> bool:
        """
        Tests whether the assertion that self applies in ALL cases
        implies that the procedure "other" applies in ALL cases.

        Self does not imply other if any output of other
        is not equal to or implied by some output of self.

        For self to imply other, every input of self
        must be implied by some input of other.

        Self does not imply other if any despite of other
        contradicts an input of self.

        :param other:
        """

        if not isinstance(other, self.__class__):
            return False

        if self == other:
            return True

        relations = (
            Relation(other.outputs, self.outputs, operator.le),
            Relation(self.inputs, other.inputs, operator.le),
        )
        matchlist = self.all_relation_matches(relations)

        # For every factor in other, find the permutations of entity slots
        # that are consistent with matchlist and that don't cause the factor
        # to contradict any factor of self.

        return any(
            self.consistent_factor_groups(self.inputs, other.despite, matches)
            for matches in matchlist
        )

    def implies_all_to_some(self, other: "Procedure") -> bool:
        """
        This is a different process for checking whether one procedure implies another,
        used when the list of self's inputs is considered an exhaustive list of the
        circumstances needed to invoke the procedure (i.e. when the rule "always" applies
        when the inputs are present), but the list of other's inputs is not exhaustive.

        For self to imply other, every output of other
        must be equal to or implied by some output of self.

        For self to imply other, every input of self must not be
        contradicted by any input or despite of other.

        Self does not imply other if any despite factors of other
        are not implied by inputs of self.

        :param other:
        """

        if not isinstance(other, self.__class__):
            return False

        if self.implies_all_to_all(other):
            return True

        other_despite_or_input = (*other.despite, *other.inputs)
        self_despite_or_input = (*self.despite, *self.inputs)

        relations = (
            Relation(other.outputs, self.outputs, operator.le),
            Relation(other.despite, self_despite_or_input, operator.le),
        )

        matchlist = self.all_relation_matches(relations)

        return any(
            self.consistent_factor_groups(self.inputs, other_despite_or_input, matches)
            for matches in matchlist
        )

    def consistent_factor_groups(
        self,
        self_factors: Tuple[Factor],
        other_factors: Tuple[Factor],
        matches: Dict[Factor, Factor],
    ):
        """Determines whether unassigned context factors can
        be assigned in such a way that there's no contradiction
        between any factor in self_factors and other_factors,
        given that some factors have already been assigned as
        described by matches.

        Try first determining whether one factor can contradict
        another (imply the absence of the other given matching
        context assignments), and then determine whether it's
        possible to make the contexts not match?

        Does Factor: None in matches always mean that Factor
        can avoid being matched in a contradictory way?"""

        # proxy = MappingProxyType(matches)
        for self_factor in self_factors:
            for other_factor in other_factors:
                if self_factor.contradicts(other_factor):
                    if all(
                        all(
                            matches.get(key) == context_register[key]
                            or matches.get(context_register[key] == key)
                            for key in self_factor.generic_factors()
                        )
                        for context_register in self_factor.context_register(
                            other_factor, operator.eq
                        )
                    ):
                        return False
        return True

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

    def contradicts(self, other):
        raise NotImplementedError(
            "Procedures do not contradict one another unless one of them ",
            "applies in 'ALL' cases. Consider using the ",
            "'contradicts_some_to_all' method.",
        )


@dataclass()
class Rule(Factor):
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


@dataclass(frozen=True)
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
    enactments: Union[Enactment, Iterable[Enactment]] = ()
    enactments_despite: Union[Enactment, Iterable[Enactment]] = ()
    mandatory: bool = False
    universal: bool = False
    rule_valid: bool = True
    decided: bool = True
    generic: bool = False

    def __post_init__(self):

        for attr in ("enactments", "enactments_despite"):
            value = self.__dict__[attr]
            if isinstance(value, Enactment):
                object.__setattr__(self, attr, self.wrap_with_tuple(value))

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

    @classmethod
    def from_dict(
        cls, record: Dict, context_list: List[Factor]
    ) -> Tuple["ProceduralRule", List[Factor]]:
        def list_from_records(
            record_list: Union[Dict[str, str], List[Dict[str, str]]],
            context_list: List[Factor],
            class_to_create,
        ) -> Tuple[Union[Factor, Enactment]]:
            factors_or_enactments: List[Union[Factor, Enactment]] = []
            if not isinstance(record_list, list):
                record_list = [record_list]
            for record in record_list:
                created, context_list = class_to_create.from_dict(record, context_list)
                factors_or_enactments.append(created)
            return tuple(factors_or_enactments)

        factor_groups: Dict[str, List] = {"inputs": [], "outputs": [], "despite": []}
        for factor_type in factor_groups:
            factor_groups[factor_type] = list_from_records(
                record.get(factor_type, []), context_list, Factor
            )
        enactment_groups: Dict[str, List] = {"enactments": [], "enactments_despite": []}
        for enactment_type in enactment_groups:
            enactment_groups[enactment_type] = list_from_records(
                record.get(enactment_type, []), context_list, Enactment
            )

        procedure = Procedure(
            inputs=factor_groups["inputs"],
            outputs=factor_groups["outputs"],
            despite=factor_groups["despite"],
        )

        return (
            ProceduralRule(
                procedure=procedure,
                enactments=enactment_groups["enactments"],
                enactments_despite=enactment_groups["enactments_despite"],
                mandatory=record.get("mandatory", False),
                universal=record.get("universal", False),
                rule_valid=record.get("rule_valid", True),
                decided=record.get("decided", True),
            ),
            context_list,
        )

    def generic_factors(self):
        return self.procedure.generic_factors()

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
            any(e >= other_d for e in (self.enactments + self.enactments_despite))
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
