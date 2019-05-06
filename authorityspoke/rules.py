from __future__ import annotations

import json
import operator
import pathlib

from types import MappingProxyType

from typing import Dict, List, Sequence, Tuple
from typing import Iterable, Iterator, Mapping
from typing import Callable, Optional, Union
from typing import NamedTuple

from dataclasses import dataclass

from authorityspoke.context import get_directory_path
from authorityspoke.enactments import Enactment
from authorityspoke.factors import Factor, new_context_helper


class Relation(NamedTuple):
    """
    Describes two groups of :class:`.Factor`\s and suggests a relation
    between the two groups. The work of determining whether the
    relation holds isn't currently performed by this class.

    :param need_matches:
        :class:`.Factor`\s that all need to satisfy the comparison
        :attr:`comparison` with some factor of :attr:`available`
        for the relation to hold.

    :param available:
        :class:`.Factor`\s available for matching with the
        :attr:`need_matches` :class:`.Factor`\s, but that don't
        all need to be matched themselves for the relation to hold.

    :param comparison:
        a function defining the comparison that must be ``True``
        between each :attr:`need_matches` and some :attr:`available`
        for the relation to hold.
    """
    need_matches: Tuple[Factor, ...]
    available: Tuple[Factor, ...]
    comparison: Callable


@dataclass(frozen=True)
class Procedure(Factor):
    """
    A (potential) rule for courts to use in resolving litigation.
    Described in terms of inputs and outputs, and also potentially
    "despite" :class:`Factor`\s, which occur when a :class:`Rule`
    could be said to apply "even if" some "despite" factor is true.

    Users generally should not need to interact with this class
    directly, under the current design. Instead, they should interact
    with the class :class:`ProdecuralRule`.

    :param outputs:
        an outcome that a court may accept based on the presence
        of the ``inputs``

    :param inputs:
        supporting :class:`Factor`\s in favor of the ``output``.
        The ``input`` :class:`Factor`\s are not treated as
        potential undercutters.

    :param despite:
        :class:`Factor`\s that do not prevent the court from
        imposing the ``output``. These could be considered
        "failed undercutters" in defeasible logic. If a factor
        is relevant both as support for the output and as
        a potential undercutter, include it in both 'inputs'
        and 'despite'.

    :param name:

    :param absent:

    :param generic:
    """

    outputs: Iterable[Factor] = ()
    inputs: Iterable[Factor] = ()
    despite: Iterable[Factor] = ()
    name: Optional[str] = None
    absent: bool = False
    generic: bool = True

    def __post_init__(self):

        outputs = self.__class__._wrap_with_tuple(self.outputs)
        inputs = self.__class__._wrap_with_tuple(self.inputs)
        despite = self.__class__._wrap_with_tuple(self.despite)

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

    def __eq__(self, other: Procedure) -> bool:
        """Determines if the two procedures have all the same factors
        with the same entities in the same roles, not whether they're
        actually the same Python object."""

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
                        self._update_mapping(
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

    def _implies_if_present(self, other: Factor) -> bool:
        """
        Tests whether the assertion that self applies in some cases
        implies that the procedure "other" applies in some cases.
        Despite the "if_present" in the method name, there's no "absent"
        attribute for Procedures.

        When self and other are holdings that both apply in SOME cases:

        Self does not imply other if any input of other
        is not equal to or implied by some input of self.

        Self does not imply other if any output of other
        is not equal to or implied by some output of self.

        Self does not imply other if any despite of other
        is not equal to or implied by some despite or input of self.
        """

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

    def __len__(self):
        """
        Returns the number of context factors that need to be specified for the procedure.
        """

        return len(self.generic_factors)

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

    @property
    def context_factor_names(self):
        return ("outputs", "inputs", "despite")

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

    def factors_all(self) -> List[Factor]:
        """Returns a set of all factors."""

        inputs = self.inputs or ()
        despite = self.despite or ()
        return [*self.outputs, *inputs, *despite]

    def factors_sorted(self) -> List[Factor]:
        """Sorts the procedure's factors into an order that will always be
        the same for the same set of factors, but that doesn't correspond to
        whether the factors are inputs, outputs, or "even if" factors."""

        return sorted(self.factors_all(), key=repr)

    @property
    def generic_factors(self) -> List[Factor]:
        """Returns an iterable of self's generic Factors,
        which must be matched to other generic Factors to
        perform equality tests between Factors."""

        return list(
            {
                generic: None
                for factor in self.factors_all()
                for generic in factor.generic_factors
            }
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
                            matches.get(key) == _context_register[key]
                            or matches.get(_context_register[key] == key)
                            for key in self_factor.generic_factors
                        )
                        for _context_register in self_factor._context_register(
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

    @new_context_helper
    def new_context(
        self, changes: Union[List[Factor], Dict[Factor, Factor]]
    ) -> "Procedure":
        """
        Creates new Procedure object, converting "changes" from a List
        to a Dict if needed, and replacing keys of "changes" with their
        values.
        """
        new_dict = self.__dict__.copy()
        for name in self.context_factor_names:
            new_dict[name] = tuple(
                [factor.new_context(changes) for factor in new_dict[name]]
            )
        return self.__class__(**new_dict)


@dataclass(frozen=True)
class Rule(Factor):
    """
    A statement of a legal rule which a court may posit as authoritative,
    deciding some aspect of the current litigation but also potentially
    binding future courts to follow the rule. When holdings appear in
    judicial opinions they are often hypothetical and don't necessarily
    imply that the court accepts the factual assertions or other factors
    that make up the inputs or outputs of the procedure mentioned in the
    holding.
    """

    directory = get_directory_path("holdings")

    @classmethod
    def collection_from_dict(cls, case: Dict) -> List["Rule"]:
        context_list = case.get("mentioned_factors")
        rule_list = case.get("holdings")

        mentioned = cls.get_mentioned_factors(context_list)
        finished_rules: List["Rule"] = []
        for rule in rule_list:
            # This will need to change for Attribution holdings
            finished_rule, mentioned = ProceduralRule.from_dict(rule, mentioned)
            finished_rules.append(finished_rule)
        return finished_rules

    @classmethod
    def from_json(
        cls, filename: str, directory: Optional[pathlib.Path] = None
    ) -> List["Rule"]:
        """
        Creates a list of holdings from a JSON file in the input
        subdirectory, from a JSON file in the format that lists
        mentioned_entities followed by a list of holdings.
        Then returns the list.

        Does not cause an Opinion to posit the Rules as holdings.
        """
        if not directory:
            directory = cls.directory
        with open(directory / filename, "r") as f:
            case = json.load(f)
        return cls.collection_from_dict(case)

    @classmethod
    def get_mentioned_factors(
        cls, mentioned_list: Optional[List[Dict[str, str]]]
    ) -> List[Factor]:
        """
        :param mentioned_dict: A dict in the JSON format used in the
        "input" folder.

        :returns: A list of Factors mentioned in the Opinion's holdings.
        Especially the context factors referenced in Predicates, since
        there's currently no other way to import those using the JSON
        format.
        """
        mentioned: List[Factor] = []
        if mentioned_list:
            for factor_dict in mentioned_list:
                _, mentioned = Factor.from_dict(factor_dict, mentioned)
        return mentioned


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
    name: Optional[str] = None

    def __post_init__(self):

        for attr in ("enactments", "enactments_despite"):
            value = self.__dict__[attr]
            if isinstance(value, Enactment):
                object.__setattr__(self, attr, self._wrap_with_tuple(value))

    def __str__(self):
        def factor_catalog(factors: List[Union[Factor, Enactment]], tag: str) -> str:
            lines = [f"{tag}: {factors[i]}\n" for i in range(len(factors))]
            return "".join(lines)

        newline = "\n"
        return (
            f"the rule that {'it is not decided whether ' if not self.decided else ''}"
            + f"{'it is not valid that ' if not self.rule_valid else ''}the court "
            + f"{'MUST' if self.mandatory else 'MAY'} {'ALWAYS' if self.universal else 'SOMETIMES'} "
            + f"accept the result{newline}{str(factor_catalog(self.procedure.outputs, 'RESULT'))}"
            + f"{'based on the input' + newline + str(factor_catalog(self.procedure.inputs, 'GIVEN')) if self.procedure.inputs else ''}"
            + f"{str(factor_catalog(self.procedure.despite, 'DESPITE')) if self.procedure.despite else ''}"
            + f"{'according to the legislation' + newline + str(factor_catalog(self.enactments, 'GIVEN')) if self.enactments else ''}"
            + f"{'and despite the legislation' + newline + str(factor_catalog(self.enactments_despite, 'DESPITE')) if self.enactments_despite else ''}"
        )

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
            return tuple(factors_or_enactments), context_list

        factor_groups: Dict[str, List] = {"inputs": [], "outputs": [], "despite": []}
        for factor_type in factor_groups:
            factor_groups[factor_type], context_list = list_from_records(
                record.get(factor_type, []), context_list, Factor
            )
        enactment_groups: Dict[str, List] = {"enactments": [], "enactments_despite": []}
        for enactment_type in enactment_groups:
            enactment_groups[enactment_type], context_list = list_from_records(
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

    @property
    def generic_factors(self):
        return self.procedure.generic_factors

    @property
    def despite(self):
        return self.procedure.despite

    @property
    def inputs(self):
        return self.procedure.inputs

    @property
    def outputs(self):
        return self.procedure.outputs

    @property
    def context_factors(self) -> Tuple:

        return self.procedure.context_factors

    def contradicts_if_valid(self, other) -> bool:
        """Determines whether self contradicts other,
        assuming that rule_valid and decided are
        True for both Rules."""

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

        return self.contradicts_if_valid(other)

    def implies_if_valid(self, other) -> bool:
        """
        Partial version of the __ge__ implication function covering
        only cases where other is an instance of self's class, and
        rule_valid and decided are True for both of them.

        If self relies for support on some enactment text that
        other doesn't, then self doesn't imply other.

        Also, if other specifies that it applies notwithstanding some
        enactment not mentioned by self, then self doesn't imply other.
        """

        if not all(
            any(other_e >= e for other_e in other.enactments) for e in self.enactments
        ):
            return False

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

    @property
    def context_factor_names(self):
        return ("procedure",)

    def contradicts(self, other) -> bool:
        """
        A holding contradicts another holding if it implies
        that the other holding is false. Generally checked
        by testing whether self would imply other if
        other had an opposite value for rule_valid.

        This function takes three main paths depending on
        whether the holdings "self" and "other" assert that
        rules are decided or undecided.

        A decided holding can never contradict a previous
        statement that any rule was undecided.

        If rule A implies rule B, then a holding that B is undecided
        contradicts a prior holding deciding that rule A is valid or invalid.
        """

        if not isinstance(other, self.__class__):
            raise TypeError(
                f"'Contradicts' not supported between instances of "
                + f"'{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )

        if not other.decided:
            return False
        if self.decided:
            return self >= other.negated()
        return other.implies_if_decided(self) or other.implies_if_decided(
            self.negated()
        )


class Attribution:
    """
    An assertion about the meaning of a prior Opinion. Either a user or an Opinion
    may make an Attribution to an Opinion. An Attribution may attribute either
    a Rule or a further Attribution.
    """

    pass
