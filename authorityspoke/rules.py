"""
Statements of legal doctrines.

:class:`.Court`\s may posit them as holdings, and they
may describe procedural moves available in litigation.
"""

from __future__ import annotations

import json
import operator
import pathlib

from typing import ClassVar, Dict, Iterable, List, Sequence, Tuple
from typing import Iterator, Optional, Union

from dataclasses import dataclass

from authorityspoke.context import get_directory_path
from authorityspoke.enactments import Enactment, consolidate_enactments
from authorityspoke.factors import Factor, means, new_context_helper
from authorityspoke.procedures import Procedure


@dataclass(frozen=True)
class Rule(Factor):
    """
    A statement of a legal doctrine about a :class:`.Procedure` for litigation.

    May decide some aspect of current litigation, and also potentially
    may be cided and reused by future courts. When :class:`Rule`\s appear as
    judicial holdings they are often hypothetical and don't necessarily
    imply that the court accepts the :class:`.Fact` assertions or other
    :class:`.Factor`\s that make up the inputs or outputs of the
    :class:`.Procedure` mentioned in the :class:`Rule`.

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

    procedure: Optional[Procedure] = None
    enactments: Union[Enactment, Iterable[Enactment]] = ()
    enactments_despite: Union[Enactment, Iterable[Enactment]] = ()
    mandatory: bool = False
    universal: bool = False
    rule_valid: bool = True
    decided: bool = True
    generic: bool = False
    name: Optional[str] = None
    outputs: Optional[Union[Factor, Iterable[Factor]]] = None
    inputs: Optional[Union[Factor, Iterable[Factor]]] = None
    despite: Optional[Union[Factor, Iterable[Factor]]] = None

    context_factor_names: ClassVar = ("procedure",)
    enactment_attr_names: ClassVar = ("enactments", "enactments_despite")
    directory: ClassVar = get_directory_path("holdings")

    def __post_init__(self):
        for attr in self.enactment_attr_names:
            value = self.__dict__[attr]
            if isinstance(value, Enactment):
                object.__setattr__(self, attr, self._wrap_with_tuple(value))

        if self.procedure is None:
            if self.outputs is None:
                raise ValueError(
                    "To construct a Rule you must specify either a Procedure "
                    + "or output/input/despite Factors for use in constructing "
                    + "a Procedure (including at least one output)."
                )
            object.__setattr__(
                self,
                "procedure",
                Procedure(
                    outputs=self.outputs, inputs=self.inputs, despite=self.despite
                ),
            )
        object.__setattr__(self, "outputs", self.procedure.outputs)
        object.__setattr__(self, "inputs", self.procedure.inputs)
        object.__setattr__(self, "despite", self.procedure.despite)

    def __add__(self, other) -> Optional[Rule]:
        """
        Create new :class:`Rule` if ``self`` can satisfy the :attr:`inputs` of ``other``.

        If both ``self`` and ``other`` have False for :attr:`universal`,
        or if either has ``False`` for :attr:`rule_valid'\,
        then returns ``None``. Otherwise:

        If the union of the :attr:`inputs` and :attr:`outputs` of ``self``
        would trigger ``other``, then return a new version of ``self``
        with the output :class:`.Factor`\s of ``other`` as well as the
        outputs of ``self``.

        The new ``universal`` and ``mandatory`` values are the
        lesser of the old values for each.

        Don't test whether ``self`` could be triggered by the outputs
        of other. Let user do ``other + self`` for that.

        :param other:
            another :class:`Rule` to try to add to ``self``

        :returns:
            a combined :class:`Rule` that extends the procedural
            move made in ``self``, if possible. Otherwise ``None``.
        """
        if not isinstance(other, Rule):
            if isinstance(other, Factor):
                return self.add_factor(other)
            if isinstance(other, Enactment):
                return self.add_enactment(other)
            raise TypeError
        if self.rule_valid is False or other.rule_valid is False:
            return None
        if self.universal is False and other.universal is False:
            return None

        if not other.needs_subset_of_enactments(self):
            return None

        new_procedure = self.procedure + other.procedure
        if new_procedure is not None:
            return self.evolve(
                {
                    "procedure": new_procedure,
                    "universal": min(self.universal, other.universal),
                    "mandatory": min(self.mandatory, other.mandatory),
                }
            )
        return None

    @classmethod
    def collection_from_dict(
        cls,
        case: Dict,
        mentioned: Optional[List[Factor]] = None,
        regime: Optional[Regime] = None,
    ) -> List[Rule]:
        """
        Create a :py:class:`list` of :class:`Rule`\s from JSON.

        :param case:
            a :class:`dict` derived from the JSON format that
            lists ``mentioned_entities`` followed by a
            series of strings representing :class:`Rule`\s.

        :param mentioned:
            A list of :class:`.Factor`\s mentioned in the
            :class:`.Opinion`\'s holdings. Especially used for
            context factors referenced in :class:`.Predicate`\s,
            since there's currently no other way to import
            those using the JSON format.

        :param regime:
            A :class:`.Regime` to search in for :class:`.Enactment`\s
            referenced in ``case``.

        :returns:
            a :class:`list` of :class:`Rule`\s with the items
            from ``mentioned_entities`` as ``context_factors``.
        """
        if not mentioned:
            mentioned: List[Factor] = []
        factor_dicts = case.get("mentioned_factors")
        if factor_dicts:
            for factor_dict in factor_dicts:
                _, mentioned = Factor.from_dict(
                    factor_dict, mentioned=mentioned, regime=regime
                )

        finished_rules: List[Rule] = []
        for rule in case.get("holdings"):

            # This basic formatting could be moved elsewhere, but
            # it's needed before generating multiple rules based
            # on the "exclusive" flag in the JSON.
            for category in ("inputs", "despite", "outputs"):
                if isinstance(rule.get(category), dict):
                    rule[category] = [rule[category]]

            for finished_rule, new_mentioned in Rule.from_dict(
                rule, mentioned, regime=regime
            ):
                finished_rules.append(finished_rule)
                mentioned = new_mentioned
        return finished_rules

    @classmethod
    def from_json(
        cls,
        filename: str,
        directory: Optional[pathlib.Path] = None,
        regime: Optional[Regime] = None,
    ) -> List[Rule]:
        """
        Load a list of :class:`Rule`\s from JSON.

        Does not cause an :class:`.Opinion` to :meth:`~.Opinion.posit`
        the :class:`Rule`\s as holdings.

        :param filename:
            the name of the JSON file to look in for :class:`Rule`
            data in the format that lists ``mentioned_factors``
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
    def contrapositive_from_dict(
        cls, record: Dict, mentioned: List[Factor], regime: Optional[Regime] = None
    ) -> Iterator[Tuple[Rule, List[Factor]]]:
        """
        Make contrapositive forms of a :class:`Rule` described by JSON input.

        If ``record`` contains the entry ``"exclusive": True``, that means
        the specified :class:`~Rule.inputs`` are the only way to reach the specified
        output. (Multiple :class:`~Rule.outputs` are not allowed when the ``exclusive``
        flag is ``True``.) When that happens, it can be inferred that in the absence
        of any of the inputs, the output must also be absent. So, this method will be
        called once for each input to create more :class:`Rule`\s containing that
        information. None of the completed :class:`Rule` objects will contain an
        ``exclusive`` flag.

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

        :param regime:

        :returns:
            iterator yielding :class:`Rule`\s with the items
            from ``mentioned_entities`` as ``context_factors``
        """

        if len(record["outputs"]) != 1:
            raise ValueError(
                "The 'exclusive' attribute is not allowed for Rules "
                + "with more than one 'output' Factor. If the set of Factors "
                + "in 'inputs' is really the only way to reach any of the "
                + "'outputs', consider making a separate 'exclusive' entry "
                + "for each output."
            )
        if record["outputs"][0].get("absent") is True:
            raise ValueError(
                "The 'exclusive' attribute is not allowed for Rules "
                + "with an 'absent' 'output' Factor. This would indicate "
                + "that the output can or must be present in every litigation "
                + "unless specified inputs are present, which is unlikely."
            )
        if record.get("rule_valid") is False:
            raise NotImplementedError(
                "The ability to state that it is not 'valid' to assert "
                + "that a Rule is the 'exclusive' way to reach an output is "
                + "not implemented, so 'rule_valid' cannot be False while "
                + "'exclusive' is True. Try expressing this in another way "
                + "without the 'exclusive' keyword."
            )
        record["mandatory"] = not record.get("mandatory")
        record["universal"] = not record.get("universal")
        del record["exclusive"]
        record["outputs"][0]["absent"] = True

        for input_factor in record["inputs"]:
            new_record = record.copy()
            new_input = input_factor.copy()
            new_input["absent"] = not new_input.get("absent")
            new_record["inputs"] = [new_input]
            for new_tuple in Rule.from_dict(
                record=new_record, mentioned=mentioned, regime=regime
            ):
                yield new_tuple

    @classmethod
    def from_dict(
        cls, record: Dict, mentioned: List[Factor], regime: Optional[Regime] = None
    ) -> Iterator[Tuple[Rule, List[Factor]]]:
        """
        Make :class:`Rule` from a :class:`dict` of strings and a list of mentioned :class:`.Factor`\s.

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

        :param regime:

        :returns:
            iterator yielding :class:`Rule`\s with the items
            from ``mentioned_entities`` as ``context_factors``
        """

        def list_from_records(
            record_list: Union[Dict[str, str], List[Dict[str, str]]],
            mentioned: List[Factor],
            class_to_create,
            regime: Optional[Regime] = None,
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

        yield (
            Rule(
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

        if record.get("exclusive") is True:
            for response in Rule.contrapositive_from_dict(record, mentioned, regime):
                yield response

    @property
    def context_factors(self) -> Tuple:
        """
        Call :class:`Procedure`\'s :meth:`~Procedure.context_factors` method.

        :returns:
            context_factors from ``self``'s :class:`Procedure`
        """
        return self.procedure.context_factors

    @property
    def generic_factors(self) -> List[Optional[Factor]]:
        """
        Get :class:`.Factor`\s that can be replaced without changing ``self``\s meaning.

        :returns:
            generic :class:`.Factor`\s from ``self``'s :class:`Procedure`
        """
        if self.generic:
            return [self]
        return self.procedure.generic_factors

    def add_enactment(self, incoming: Enactment, role: str = "enactments") -> Rule:
        """
        Make new version of ``self`` with an :class:`.Enactment` added.

        :param incoming:
            the new :class:`.Enactment` to be added to enactments or
            enactments_despite

        :param role:
            specifies whether the new :class:`.Enactment` should be added
            to enactments or enactments_despite

        :returns:
            a new version of ``self`` with the specified change
        """
        if role not in self.enactment_attr_names:
            raise ValueError(f"'role' must be one of {self.enactment_attr_names}")

        if not isinstance(incoming, Enactment):
            raise TypeError

        return self.evolve({role: list(self.__dict__[role]) + [incoming]})

    def add_factor(self, incoming: Factor, role: str = "inputs") -> Rule:
        """
        Make new version of ``self`` with an added input, output, or despite :class:`.Factor`.

        :param incoming:
            the new :class:`.Factor` to be added to input, output, or despite

        :param role:
            specifies whether the new :class:`.Factor` should be added to input, output, or despite

        :returns:
            a new version of ``self`` with the specified change
        """
        return self.evolve({"procedure": self.procedure.add_factor(incoming, role)})

    def contradicts(self, other) -> bool:
        """
        Test if ``self`` :meth:`~.Factor.implies` ``other`` :meth:`~.Factor.negated`\.

        Works by testing whether ``self`` would imply ``other`` if
        ``other`` had an opposite value for ``rule_valid``.

        This method takes three main paths depending on
        whether the holdings ``self`` and ``other`` assert that
        rules are decided or undecided.

        A ``decided`` :class:`Rule` can never contradict
        a previous statement that any :class:`Rule` was undecided.

        If rule A implies rule B, then a holding that B is undecided
        contradicts a prior :class:`Rule` deciding that
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
        Test if ``self`` contradicts ``other``, assuming ``rule_valid`` and ``decided``.

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
        Test for implication.

        See :meth:`.Procedure.implies_all_to_all`
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
            to be another :class:`Rule`.
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
        Test if ``self`` implies ``other`` if they're both decided.

        This is a partial version of the
        :meth:`Rule.__ge__` implication function.

        :returns:
            whether ``self`` implies ``other``, assuming that
            ``self.decided == other.decided == True`` and that
            ``self`` and ``other`` are both :class:`Rule`\s,
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

    def needs_subset_of_enactments(self, other) -> bool:
        """
        Test whether ``self``\'s :class:`.Enactment` support is a subset of ``other``\'s.

        A :class:`Rule` makes a more powerful statement if it relies on
        fewer :class:`.Enactment`\s (or applies despite more :class:`.Enactment`\s).

        So this method must return ``True`` for ``self`` to imply ``other``.
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
        return True

    def _implies_if_valid(self, other) -> bool:
        """
        Test if ``self`` implies ``other`` if they're valid and decided.

        This is a partial version of the
        :meth:`Rule.__ge__` implication function.

        :returns:
            whether ``self`` implies ``other``, assuming that
            both are :class:`Rule`\s, and
            ``rule_valid`` and ``decided`` are ``True`` for both of them.
        """

        if not self.needs_subset_of_enactments(other):
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
        Count generic :class:`.Factor`\s needed as context for this :class:`Rule`.

        :returns:
            the number of generic :class:`.Factor`\s needed for
            self's :class:`.Procedure`.
        """

        return len(self.procedure)

    def has_all_same_enactments(self, other: Rule) -> bool:
        """
        Test if ``self`` has :class:`.Enactment`\s with same meanings as ``other``\'s.

        :param other:
            another :class:`Rule` to compare to ``self``.

        :returns:
            whether the :meth:`~.Enactment.means` test passes for all :class:`.Enactment`\s
        """
        for enactment_group in self.enactment_attr_names:
            if not all(
                any(other_e.means(self_e) for self_e in self.__dict__[enactment_group])
                for other_e in other.__dict__[enactment_group]
            ):
                return False
        return True

    def means(self, other: Rule) -> bool:
        """
        Test whether ``other`` has the same meaning as ``self``.

        :returns:
            whether ``other`` is a :class:`Rule` with the
            same meaning as ``self``.
        """
        if not self.__class__ == other.__class__:
            return False

        if not self.procedure.means(other.procedure):
            return False

        if not self.has_all_same_enactments(other):
            return False
        if not other.has_all_same_enactments(self):
            return False

        return (
            self.mandatory == other.mandatory
            and self.universal == other.universal
            and self.rule_valid == other.rule_valid
            and self.decided == other.decided
        )

    def negated(self):
        """Get new copy of ``self`` with an opposite value for ``rule_valid``."""
        return self.evolve("rule_valid")

    def __or__(self, other: Rule) -> Rule:
        if not isinstance(other, Rule):
            raise TypeError
        if self.universal == other.universal == False:
            return None
        new_procedure = self.procedure | other.procedure
        if new_procedure is None:
            return None
        return Rule(
            procedure=new_procedure,
            enactments=consolidate_enactments(
                list(self.enactments) + list(other.enactments)
            ),
            enactments_despite=consolidate_enactments(
                list(self.enactments_despite) + list(other.enactments_despite)
            ),
            mandatory=min(self.mandatory, other.mandatory),
            universal=min(self.universal, other.universal),
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
    An assertion about the meaning of a prior :class:`.Opinion`.

    Either a user or an :class:`.Opinion` may make an Attribution
    to an :class:`.Opinion`. An Attribution may attribute either a
    :class:`.Rule` or a further Attribution.
    """

    pass
