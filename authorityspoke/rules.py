"""
Statements of legal doctrines that :class:`.Court`\s may posit as
holdings and that may describe procedural moves available in
litigation.
"""

from __future__ import annotations

import json
import operator
import pathlib

from typing import ClassVar, Dict, Iterable, List, Sequence, Tuple
from typing import Optional, Union

from dataclasses import dataclass

from authorityspoke.context import get_directory_path
from authorityspoke.enactments import Enactment
from authorityspoke.factors import Factor, means, new_context_helper
from authorityspoke.relations import Relation


@dataclass(frozen=True)
class Procedure(Factor):
    """
    A (potential) rule for courts to use in resolving litigation.
    Described in terms of inputs and outputs, and also potentially
    "despite" :class:`.Factor`\s, which occur when a :class:`Rule`
    could be said to apply "even if" some "despite" factor is true.

    Users generally should not need to interact with this class
    directly, under the current design. Instead, they should interact
    with the class :class:`.ProdecuralRule`.

    :param outputs:
        an outcome that a court may accept based on the presence
        of the ``inputs``

    :param inputs:
        supporting :class:`.Factor`\s in favor of the ``output``.
        The ``input`` :class:`.Factor`\s are not treated as
        potential undercutters.

    :param despite:
        :class:`.Factor`\s that do not prevent the court from
        imposing the ``output``. These could be considered
        "failed undercutters" in defeasible logic. If a :class:`.Factor`
        is relevant both as support for the output and as
        a potential undercutter, include it in both ``inputs``
        and ``despite``.

    :param name:
        An identifier that can be used to reference and
        incorporate an existing procedure in a new
        :class:`.Factor`, instead of constructing a new
        copy of the :class:`.Procedure`.

    :param absent:
        Whether the absence, rather than presence, of this
        :class:`.Procedure` is being referenced. The usefulness
        of this is unclear, but I'm not prepared to eliminate it
        before the :class:`.Argument` class has been implemented
        and tested.

    :param generic:
        Whether the this :class:`Procedure` is being referenced
        as a generic example, which could be replaced by any
        other :class:`Procedure`.
    """

    outputs: Iterable[Factor] = ()
    inputs: Iterable[Factor] = ()
    despite: Iterable[Factor] = ()
    name: Optional[str] = None
    absent: bool = False
    generic: bool = False
    context_factor_names: ClassVar = ("outputs", "inputs", "despite")

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

    def __len__(self):
        """
        :returns:
            the number of generic :class:`.Factor`\s that need to be
            specified for this :class:`Procedure`.
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
    def factors_all(self) -> List[Factor]:
        """
        :returns:
            a :class:`list` of all :class:`.Factor`\s."""

        inputs = self.inputs or ()
        despite = self.despite or ()
        return [*self.outputs, *inputs, *despite]

    @property
    def generic_factors(self) -> List[Optional[Factor]]:
        """
        :class:`.Factor`\s that can be replaced without changing ``self``\s meaning.

        :returns:
            ``self``'s generic :class:`.Factor`\s,
            which must be matched to other generic :class:`.Factor`\s to
            perform equality or implication tests between :class:`.Factor`\s
            with :meth:`.Factor.means` or :meth:`.Factor.__ge__`.
        """
        if self.generic:
            return [self]
        return list(
            {
                generic: None
                for factor in self.factors_all
                for generic in factor.generic_factors
            }
        )

    def consistent_factor_groups(
        self,
        self_factors: Tuple[Factor],
        other_factors: Tuple[Factor],
        matches: Dict[Factor, Factor],
    ):
        """
        Find whether two sets of :class:`.Factor`\s can be consistent.

        Works by first determining whether one :class:`.Factor`
        potentially :meth:`~.Factor.contradicts` another,
        and then determining whether it's possible to make
        context assignments match between the contradictory
        :class:`.Factor`\s.

        .. Note::
            Does ``Factor: None`` in matches always mean that
            the :class:`.Factor` can avoid being matched in a
            contradictory way?

        :returns:
            whether unassigned context factors can be assigned in such
            a way that there's no contradiction between any factor in
            ``self_factors`` and ``other_factors``, given that some
            :class:`.Factor`\s have already been assigned as
            described by ``matches``.
        """
        for self_factor in self_factors:
            for other_factor in other_factors:
                if self_factor.contradicts(other_factor):
                    if all(
                        all(
                            matches.get(key) == context_register[key]
                            or matches.get(context_register[key] == key)
                            for key in self_factor.generic_factors
                        )
                        for context_register in self_factor._context_registers(
                            other_factor, means
                        )
                    ):
                        return False
        return True

    def contradiction_between_outputs(
        self, other: Procedure, matches: Dict[Factor, Factor]
    ) -> bool:
        """
        :param other:
            another :class:`Factor`

        :param matches:
            keys representing :class:`.Factor`\s in ``self`` and
            values representing :class:`.Factor`\s in ``other``. The
            keys and values have been found in corresponding positions
            in ``self`` and ``other``.

        :returns:
            whether any :class:`.Factor` assignment can be found that
            makes a :class:`.Factor` in the output of ``other`` contradict
            a :class:`.Factor` in the output of ``self``.
        """
        for other_factor in other.outputs:
            for self_factor in self.outputs:
                if other_factor.contradicts(self_factor):
                    generic_pairs = zip(
                        self_factor.generic_factors, other_factor.generic_factors
                    )
                    if all(matches.get(pair[0]) == pair[1] for pair in generic_pairs):
                        return True
        return False

    def contradicts(self, other) -> bool:
        """
        Find if ``self`` applying in some cases implies ``other`` cannot apply in some.

        Raises an error because, by analogy with :meth:`Procedure.implies`\,
        users might expect this method to return ``True`` only when
        :class:`ProceduralRule` with ``universal=False`` and Procedure ``self``
        would contradict another :class:`ProceduralRule` with ``universal=False``
        and Procedure ``other``. But that would never happen.
        """
        raise NotImplementedError(
            "Procedures do not contradict one another unless one of them ",
            "applies in 'ALL' cases. Consider using ",
            "'Procedure.contradicts_some_to_all' or 'ProceduralRule.contradicts'.",
        )

    def contradicts_some_to_all(self, other: Procedure) -> bool:
        """
        Find if ``self`` applying in some cases implies ``other`` cannot apply in all.

        :returns:
            whether the assertion that ``self`` applies in
            **some** cases contradicts that ``other`` applies in **all**
            cases, where at least one of the :class:`.Rule`\s is ``mandatory``.
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

    def implies_all_to_all(self, other: Procedure) -> bool:
        """
        Find if ``self`` applying in all cases implies ``other`` applies in all.

        ``self`` does not imply ``other`` if any output of ``other``
        is not equal to or implied by some output of ``self``.

        For ``self`` to imply ``other``, every input of ``self``
        must be implied by some input of ``other``.

        ``self`` does not imply ``other`` if any despite of ``other``
        :meth:`~.Factor.contradicts` an input of ``self``.

        :returns:
            whether the assertion that ``self`` applies in **all** cases
            implies that ``other`` applies in **all** cases.
        """
        if not isinstance(other, self.__class__):
            return False

        if self.means(other):
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

    def implies_all_to_some(self, other: Procedure) -> bool:
        """
        Find if ``self`` applying in all cases implies ``other`` applies in some.

        For ``self`` to imply ``other``, every output of ``other``
        must be equal to or implied by some output of ``self``.

        For ``self`` to imply ``other``, every input of ``self`` must not be
        contradicted by any input or despite of ``other``.

        ``self`` does not imply ``other`` if any "despite" :class:`.Factor`\s
        of ``other`` are not implied by inputs of ``self``.

        :returns:
            whether the assertion that ``self`` applies in **all** cases
            implies that ``other`` applies in **some** cases (that is, if
            the list of ``self``'s inputs is not considered an exhaustive list
            of the circumstances needed to invoke the procedure).
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

    def _implies_if_present(self, other: Factor) -> bool:
        """
        When ``self`` and ``other`` are included in
        :class:`Rule`\s that both apply in **some** cases:

        ``self`` does not imply ``other`` if any input of ``other``
        is not equal to or implied by some input of ``self``.

        ``self`` does not imply ``other`` if any output of ``other``
        is not equal to or implied by some output of self.

        ``self`` does not imply ``other`` if any despite of ``other``
        is not equal to or implied by some despite or input of ``self``.

        :returns:
            whether the assertion that ``self`` applies in some cases
            implies that the :class:`.Procedure` ``other`` applies
            in some cases.
        """

        despite_or_input = (*self.despite, *self.inputs)

        relations = (
            Relation(other.outputs, self.outputs, operator.le),
            Relation(other.inputs, self.inputs, operator.le),
            Relation(other.despite, despite_or_input, operator.le),
        )

        return bool(self.all_relation_matches(relations))

    def means(self, other) -> bool:
        """
        Determine whether ``other`` has the same meaning as ``self``.

        :returns:
            whether the two :class:`.Procedure`\s have all the same
            :class:`.Factor`\s with the same context factors in the
            same roles.
        """

        if not isinstance(other, self.__class__):
            return False

            # Verifying that every factor in self is in other.
            # Also verifying that every factor in other is in self.
        groups = ("outputs", "inputs", "despite")
        matchlist = [{}]
        for group in groups:
            updater = Relation(
                need_matches=self.__dict__[group],
                available=other.__dict__[group],
                comparison=means,
            )
            matchlist = updater.update_matchlist(matchlist)
        if not bool(matchlist):
            return False

        # Now doing the same thing in reverse
        matchlist = [{}]
        for group in groups:
            updater = Relation(
                need_matches=other.__dict__[group],
                available=self.__dict__[group],
                comparison=means,
            )
            matchlist = updater.update_matchlist(matchlist)
        return bool(matchlist)

    @new_context_helper
    def new_context(self, changes: Dict[Factor, Factor]) -> Procedure:
        """
        :param changes:
            a :class:`dict` of :class:`.Factor`\s to replace
            matched to the :class:`.Factor`\s that should replace them

        :returns:
            new :class:`.Procedure` object, replacing keys of
            ``changes`` with their values.
        """
        new_dict = self.__dict__.copy()
        for name in self.context_factor_names:
            new_dict[name] = tuple(
                [factor.new_context(changes) for factor in new_dict[name]]
            )
        return self.__class__(**new_dict)

    @staticmethod
    def all_relation_matches(
        relations: Tuple[Relation, ...]
    ) -> List[Dict[Factor, Optional[Factor]]]:
        """
        :param relations:
            a series of :class:`.Relation` comparisons in which
            the ``need_matches`` :class:`.Factor`\s all refer to
            one context (for instance, the same :class:`.Opinion`),
            and the ``available`` :class:`.Factor`\s all refer to
            another context.

        :returns:
            a list of all context registers consistent with all of the
            :class:`.Relation`\s.
        """
        matchlist = [{}]
        for relation in relations:
            matchlist = relation.update_matchlist(matchlist)
        return matchlist

    @staticmethod
    def get_foreign_match_list(
        foreign: List[Dict[Factor, Factor]]
    ) -> List[Dict[Factor, Factor]]:
        """
        Compare this to the regular ``matchlist`` objects, in
        which the indices represent self's entity slots and the
        values represent other's.

        :returns:
            a version of ``matchlist`` in which the indices
            represent ``foreign``'s entity slots and the values
            represent ``self``'s entity slots.
        """

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


@dataclass(frozen=True)
class Rule(Factor):
    """
    A statement of a legal doctrine which a court may posit as authoritative.

    May decide some aspect of current litigation, and also potentially
    may be cided and reused by future courts. When ``Rule``\s appear as
    judicial holdings they are often hypothetical and don't necessarily
    imply that the court accepts the :class:`.Fact` assertions or other
    :class:`.Factor`\s that make up the inputs or outputs of the
    :class:`Procedure` mentioned in the ``Rule``.
    """

    directory = get_directory_path("holdings")

    @classmethod
    def collection_from_dict(
        cls,
        case: Dict,
        mentioned: Optional[List[Factor]] = None,
        regime: Optional["Regime"] = None
    ) -> List[Rule]:
        """
        :param case:
            a :class:`dict` derived from the JSON format that
            lists ``mentioned_entities`` followed by a
            series of :class:`Rule`\s

        :param mentioned:

        :param regime:

        :returns:
            a :class:`list` of :class:`Rule`\s with the items
            from ``mentioned_entities`` as ``context_factors``
        """

        mentioned = cls.get_mentioned_factors(
            factor_dicts=case.get("mentioned_factors"),
            mentioned=mentioned,
            regime=regime
            )
        finished_rules: List[Rule] = []
        for rule in case.get("holdings"):
            # This will need to change for Attribution holdings
            finished_rule, mentioned = ProceduralRule.from_dict(
                rule, mentioned, regime=regime
            )
            finished_rules.append(finished_rule)
        return finished_rules

    @classmethod
    def from_json(
        cls,
        filename: str,
        directory: Optional[pathlib.Path] = None,
        regime: Optional["Regime"] = None,
    ) -> List[Rule]:
        """
        Load a list of ``Rule``\s from JSON.

        Does not cause an :class:`.Opinion` to :meth:`~.Opinion.posit`
        the ``Rule``\s as holdings.

        :param filename:
            the name of the JSON file to look in for :class:`Rule`
            data in the format that lists ``mentioned_entities``
            followed by a list of holdings

        :param directory:
            the path of the directory containing the JSON file

        :parame regime:

        :returns:
            a list of :class:`Rule`\s from a JSON file in the
            ``example_data/holdings`` subdirectory, from a JSON
            file.
        """
        if not directory:
            directory = cls.directory
        with open(directory / filename, "r") as f:
            case = json.load(f)
        return cls.collection_from_dict(case, regime=regime)

    @classmethod
    def get_mentioned_factors(
        cls,
        factor_dicts: Optional[List[Dict[str, str]]],
        mentioned: Optional[List[Factor]] = None,
        regime: Optional["Regime"] = None,
    ) -> List[Factor]:
        """
        :param factor_dicts:
            A list of dicts describing context :class:`.Factor`\s
            in the JSON format used in the ``example_data/holdings``
            folder.

        :param mentioned:
            :class:`.Factors`\s already known, which can be referenced
            by their name parameter.

        :param regime:

        :returns:
            A list of :class:`.Factor`\s mentioned in the
            :class:`.Opinion`\'s holdings. Especially the
            context factors referenced in :class:`.Predicate`\s,
            since there's currently no other way to import
            those using the JSON format.
        """
        if not mentioned:
            mentioned: List[Factor] = []
        if factor_dicts:
            for factor_dict in factor_dicts:
                _, mentioned = Factor.from_dict(factor_dict, mentioned=mentioned, regime=regime)
        return mentioned


@dataclass(frozen=True)
class ProceduralRule(Rule):

    """
    :param procedure:
        a :class:`.Procedure` containing the inputs, and despite
        :class:`.Factor`\s and resulting outputs when this rule
        is triggered.

    :param enactments:
        the :class:`.Enactment`\s cited as authority for
        invoking the ``procedure``.

    :param enactments_despite:
        the :class:`.Enactment`\s specifically cited as failing
        to preclude application of the ``procedure``.

    :param mandatory:
        whether the ``procedure`` is mandatory for the
        court to apply whenever the :class:`.Rule` is properly invoked.
        ``False`` means that the ``procedure`` is "discretionary".

    :param universal:
        ``True`` if the ``procedure`` is applicable whenever
        its inputs are present. ``False`` means that the ``procedure`` is
        applicable in "some" situation where the inputs are present.

    :param rule_valid:
        ``True`` means the :class:`Rule` is asserted to be valid (or
        useable by a court in litigation). ``False`` means it's asserted
        to be invalid.

    :param decided:
        ``False`` means that it should be deemed undecided
        whether the :class:`Rule` is valid, and thus can have the
        effect of overruling prior holdings finding the :class:`.Rule`
        to be either valid or invalid. Seemingly, ``decided=False``
        should render the ``rule_valid`` flag irrelevant. Note that
        if an opinion merely says the court is not deciding whether
        a :class:`.Rule` is valid, there is no holding, and no
        :class:`.Rule` object should be created. Deciding not to decide
        a :class:`Rule`\'s validity is not the same thing as deciding
        that the :class:`.Rule` is undecided.

    :param generic:
        whether the :class:`Rule` is being mentioned in a generic
        context. e.g., if the :class:`Rule` is being mentioned in
        an :class:`.Argument` object merely as an example of the
        kind of :class:`Rule` that might be mentioned in such an
        :class:`.Argument`.

    :param name:
        an identifier used to retrieve this :class:`Rule` when
        needed for the composition of another :class:`.Factor`
        object.
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
    context_factor_names: ClassVar = ("procedure",)

    def __post_init__(self):

        for attr in ("enactments", "enactments_despite"):
            value = self.__dict__[attr]
            if isinstance(value, Enactment):
                object.__setattr__(self, attr, self._wrap_with_tuple(value))

    @classmethod
    def from_dict(
        cls, record: Dict, mentioned: List[Factor], regime: Optional["Regime"] = None
    ) -> Tuple[ProceduralRule, List[Factor]]:

        """
        :param record:
            a :class:`dict` derived from the JSON format that
            lists ``mentioned_entities`` followed by a
            series of :class:`Rule`\s. Only one of the :class:`Rule`\s
            will by covered by this :class:`dict`.

        :param mentioned:
            a series of context factors, including any generic
            :class:`.Factor`\s that need to be mentioned in
            :class:`.Predicate`\s. These will have been constructed
            from the ``mentioned_entities`` section of the input
            JSON.

        :returns:
            a :class:`list` of :class:`Rule`\s with the items
            from ``mentioned_entities`` as ``context_factors``
        """

        def list_from_records(
            record_list: Union[Dict[str, str], List[Dict[str, str]]],
            mentioned: List[Factor],
            class_to_create,
            regime: Optional["Regime"] = None
        ) -> Tuple[Union[Factor, Enactment]]:
            factors_or_enactments: List[Union[Factor, Enactment]] = []
            if not isinstance(record_list, list):
                record_list = [record_list]
            for record in record_list:
                created, mentioned = class_to_create.from_dict(
                    record, mentioned, regime=regime
                )
                factors_or_enactments.append(created)
            return tuple(factors_or_enactments), mentioned

        factor_groups: Dict[str, List] = {"inputs": [], "outputs": [], "despite": []}
        for factor_type in factor_groups:
            factor_groups[factor_type], mentioned = list_from_records(
                record.get(factor_type, []), mentioned, Factor
            )
        enactment_groups: Dict[str, List] = {"enactments": [], "enactments_despite": []}
        for enactment_type in enactment_groups:
            enactment_groups[enactment_type], mentioned = list_from_records(
                record.get(enactment_type, []), mentioned, Enactment, regime=regime
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
            mentioned,
        )

    @property
    def context_factors(self) -> Tuple:
        """
        :returns:
            context_factors from ``self``'s :class:`Procedure`
        """
        return self.procedure.context_factors

    @property
    def despite(self):
        """
        :returns:
            despite :class:`.Factors` from ``self``'s :class:`Procedure`
        """
        return self.procedure.despite

    @property
    def generic_factors(self) -> List[Optional[Factor]]:
        """
        :class:`.Factor`\s that can be replaced without changing ``self``\s meaning.

        :returns:
            generic :class:`.Factors` from ``self``'s :class:`Procedure`
        """
        if self.generic:
            return [self]
        return self.procedure.generic_factors

    @property
    def inputs(self):
        """
        :returns:
            input :class:`.Factors` from ``self``'s :class:`Procedure`
        """
        return self.procedure.inputs

    @property
    def outputs(self):
        """
        :returns:
            output :class:`.Factors` from ``self``'s :class:`Procedure`
        """
        return self.procedure.outputs

    def contradicts(self, other) -> bool:
        """
        A :class:`ProceduralRule` contradicts ``other`` if it
        :meth:`~.Factor.implies` ``other.negated()`` Checked
        by testing whether ``self`` would imply ``other`` if
        ``other`` had an opposite value for ``rule_valid``.

        This method takes three main paths depending on
        whether the holdings ``self`` and ``other`` assert that
        rules are decided or undecided.

        A ``decided`` :class:`ProceduralRule` can never contradict
        a previous statement that any :class:`Rule` was undecided.

        If rule A implies rule B, then a holding that B is undecided
        contradicts a prior :class:`ProceduralRule` deciding that
        rule A is valid or invalid.

        :returns:
            whether ``self`` contradicts ``other``.
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
        return other._implies_if_decided(self) or other._implies_if_decided(
            self.negated()
        )

    def _contradicts_if_valid(self, other) -> bool:
        """
        :returns:
            whether ``self`` contradicts ``other``,
            assuming that ``rule_valid`` and ``decided`` are
            ``True`` for both :class:`Rule`\s.
        """

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

    def __ge__(self, other) -> bool:
        """
        Implication method. See :meth:`.Procedure.implies_all_to_all`
        and :meth:`.Procedure.implies_all_to_some` for
        explanations of how ``inputs``, ``outputs``,
        and ``despite`` :class:`.Factor`\s affect implication.

        If ``self`` relies for support on some :class:`.Enactment` text
        that ``other`` doesn't, then ``self`` doesn't imply ``other``.

        Also, if ``other`` specifies that it applies notwithstanding
        some :class:`.Enactment` not mentioned by ``self``, then
        ``self`` doesn't imply ``other``.

        :returns:
            whether ``self`` implies ``other``, which requires ``other``
            to be another :class:`ProceduralRule`.
        """

        if not isinstance(other, self.__class__):
            raise TypeError(
                f"'Implies' not supported between instances of "
                + f"'{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )

        if self.decided and other.decided:
            return self._implies_if_decided(other)

        # A holding being undecided doesn't seem to imply that
        # any other holding is undecided, except itself and the
        # negation of itself.

        if not self.decided and not other.decided:
            return self.means(other) or self.means(other.negated())

        # It doesn't seem that any holding being undecided implies
        # that any holding is decided, or vice versa.

        return False

    def _implies_if_decided(self, other) -> bool:

        """
        Simplified version of the :meth:`ProceduralRule.__ge__`
        implication function.

        :returns:
            whether ``self`` implies ``other``, assuming that
            ``self.decided == other.decided == True`` and that
            ``self`` and ``other`` are both :class:`ProceduralRule`\s,
            although ``rule_valid`` can be ``False``.
        """

        if self.rule_valid and other.rule_valid:
            return self._implies_if_valid(other)

        if not self.rule_valid and not other.rule_valid:
            return other._implies_if_valid(self)

        # Looking for implication where self.rule_valid != other.rule_valid
        # is equivalent to looking for contradiction.

        # If decided rule A contradicts B, then B also contradicts A

        return self._contradicts_if_valid(other)

    def _implies_if_valid(self, other) -> bool:
        """
        Partial version of the :meth:`ProceduralRule.__ge__`
        implication function.

        :returns: whether ``self`` implies ``other``, assuming that
        both are :class:`ProceduralRule`\s,, and
        ``rule_valid`` and ``decided`` are ``True`` for both of them.
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

    def __len__(self):
        """
        :returns:
            the number of generic :class:`.Factor`\s needed to provide
            context for this :class:`Rule`, which currently is just the
            generic :class:`.Factor`\s needed for the ``procedure``.
        """

        return len(self.procedure)

    def means(self, other: ProceduralRule) -> bool:
        """
        :returns:
            whether ``other`` is a :class:`ProceduralRule` with the
            same meaning as ``self``.
        """

        if not self.__class__ == other.__class__:
            return False

        if not self.procedure.means(other.procedure):
            return False

        return (
            self.mandatory == other.mandatory
            and self.universal == other.universal
            and self.rule_valid == other.rule_valid
            and self.decided == other.decided
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


class Attribution:
    """
    An assertion about the meaning of a prior Opinion. Either a user or an Opinion
    may make an Attribution to an Opinion. An Attribution may attribute either
    a Rule or a further Attribution.
    """

    pass
