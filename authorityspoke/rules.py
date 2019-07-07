"""
Statements of legal doctrines.

:class:`.Court`\s may posit them as holdings, and they
may describe procedural moves available in litigation.
"""

from __future__ import annotations

import json
import operator
import pathlib

from typing import Any, ClassVar, Dict, Iterable, Iterator
from typing import List, Optional, Sequence, Tuple, Union

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
        else:
            if not (self.outputs == self.inputs == self.despite == None):
                new_procedure = Procedure(
                    outputs=self.outputs or self.procedure.outputs,
                    inputs=self.inputs or self.procedure.inputs,
                    despite=self.despite or self.procedure.despite,
                )
                object.__setattr__(self, "procedure", new_procedure)
        object.__setattr__(self, "outputs", self.procedure.outputs)
        object.__setattr__(self, "inputs", self.procedure.inputs)
        object.__setattr__(self, "despite", self.procedure.despite)

    def __add__(self, other) -> Optional[Rule]:
        """
        Create new :class:`Rule` if ``self`` can satisfy the :attr:`inputs` of ``other``.

        If both ``self`` and ``other`` have False for :attr:`universal`,
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

    def get_contrapositives(self) -> Iterator[Rule]:
        """
        Make contrapositive forms of this :class:`Rule`.

        Used when converting from JSON input containing the entry
        ``"exclusive": True``, which means the specified :class:`~Rule.inputs``
        are the only way to reach the specified output. When that happens,
        it can be inferred that in the absence of any of the inputs, the output
        must also be absent. (Multiple :class:`~Rule.outputs` are not allowed
        when the ``exclusive`` flag is ``True``.) So, this generator will
        yield one new :class:`Rule` for each input.

        :returns:
            iterator yielding :class:`Rule`\s.
        """

        if len(self.outputs) != 1:
            raise ValueError(
                "The 'exclusive' attribute is not allowed for Rules "
                + "with more than one 'output' Factor. If the set of Factors "
                + "in 'inputs' is really the only way to reach any of the "
                + "'outputs', consider making a separate 'exclusive' entry "
                + "for each output."
            )
        if self.outputs[0].absent:
            raise ValueError(
                "The 'exclusive' attribute is not allowed for Rules "
                + "with an 'absent' 'output' Factor. This would indicate "
                + "that the output can or must be present in every litigation "
                + "unless specified inputs are present, which is unlikely."
            )
        if not self.inputs:
            raise ValueError(
                "The 'exclusive' attribute is not allowed for Rules "
                + "with no 'input' Factors."
            )

        for input_factor in self.inputs:
            yield self.evolve(
                {
                    "mandatory": not self.mandatory,
                    "universal": not self.universal,
                    "inputs": [input_factor.evolve("absent")],
                    "outputs": [self.outputs[0].evolve({"absent": True})],
                }
            )

    @classmethod
    def from_dict(
        cls,
        record: Dict,
        mentioned: List[Factor],
        regime: Optional[Regime],
        factor_groups: Optional[Dict[str, List[Factor]]] = None,
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

        if factor_groups is None:
            # TODO: make this a separate method also called by Holdings.from_dict
            factor_groups: Dict[str, List] = {
                "inputs": [],
                "outputs": [],
                "despite": [],
            }
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
            Rule(
                procedure=procedure,
                enactments=enactment_groups["enactments"],
                enactments_despite=enactment_groups["enactments_despite"],
                mandatory=record.get("mandatory", False),
                universal=record.get("universal", False),
            ),
            mentioned,
        )

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
        Test if ``self`` contradicts ``other``.

        :returns:
            whether ``self`` contradicts ``other``, if each is posited by a
            :class:`.Holding` with :attr:`~Holding.rule_valid``
            and :attr:`~Holding.decided`
        """
        if not isinstance(other, self.__class__):
            raise TypeError()

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

    def __ge__(self, other) -> bool:
        """
        Test if ``self`` implies ``other`` if posited in valid and decided :class:`.Holding`\s.

        If ``self`` relies for support on some :class:`.Enactment` text
        that ``other`` doesn't, then ``self`` doesn't imply ``other``.

        Also, if ``other`` specifies that it applies notwithstanding
        some :class:`.Enactment` not mentioned by ``self``, then
        ``self`` doesn't imply ``other``.

        This will be called as part of the
        :meth:`Holding.__ge__` implication function.

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

        return self.mandatory == other.mandatory and self.universal == other.universal

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

    def own_attributes(self) -> Dict[str, Any]:
        """
        Return attributes of ``self`` that aren't inherited
        from another class or used for identification.
        """
        attrs = self.__dict__.copy()
        attrs.pop("name", None)
        for group in Procedure.context_factor_names:
            attrs.pop(group, None)
        return attrs

    def __str__(self):
        def factor_catalog(factors: List[Union[Factor, Enactment]], tag: str) -> str:
            lines = [f"{tag}: {factors[i]}\n" for i in range(len(factors))]
            return "".join(lines)

        newline = "\n"
        return (
            f"the rule that the court "
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
