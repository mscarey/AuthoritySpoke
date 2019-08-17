r"""
Descriptions of procedural changes in litigation.

Does not specify whether they are mandatory or universal,
or specify the :class:`.Enactment`\s that might require them.
"""

from __future__ import annotations

import operator

from typing import ClassVar, Dict, Iterable, List, Optional, Tuple

from dataclasses import dataclass

from authorityspoke.factors import Factor, ContextRegister, new_context_helper
from authorityspoke.factors import Analogy, all_analogy_matches, means


@dataclass(frozen=True)
class Procedure(Factor):
    r"""
    A (potential) rule for courts to use in resolving litigation.

    Described in terms of inputs and outputs, and also potentially
    "despite" :class:`.Factor`\s, which occur when a :class:`Rule`
    could be said to apply "even if" some "despite" factor is true.

    Users generally should not need to interact with this class
    directly, under the current design. Instead, they should interact
    with the class :class:`.Rule`.

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

    def __add__(self, other: Procedure) -> Optional[Procedure]:
        if not isinstance(other, self.__class__):
            return self.add_factor(other)
        matchlist = self.triggers_next_procedure(other)
        if matchlist:
            # Arbitrarily choosing the first match to decide what
            # generic Factors appear in the new outputs.
            # Wouldn't it have been better to get just one match with a generator?
            triggered_rule = other.new_context(matchlist[0])
            return self.evolve({"outputs": (*self.outputs, *triggered_rule.outputs)})
        return None

    def __or__(self, other: Procedure) -> Optional[Procedure]:
        r"""
        Combine two :class:`Procedure`\s into one.

        The new :class:`Procedure` will have all of the ``inputs``, ``outputs``,
        and ``despite`` :class:`.Factor`\s of both ``self`` and ``other``.

        All of the context :class:`.Factor`\s of ``self`` will
        remain the same.
        """

        def combine_factor_list(
            self_list, other_list, allow_contradictions: bool = False
        ):
            new_factors = []
            for self_factor in self_list:
                broadest = self_factor
                for other_factor in other_list:
                    if allow_contradictions is False and other_factor.contradicts(
                        self_factor
                    ):
                        return None
                    if other_factor >= self_factor:
                        broadest = other_factor
                new_factors.append(broadest)
            return new_factors + [
                factor for factor in other_list if factor not in new_factors
            ]

        new_inputs = combine_factor_list(self.inputs, other.inputs)
        new_outputs = combine_factor_list(self.outputs, other.outputs)
        new_despite = combine_factor_list(
            self.despite, other.despite, allow_contradictions=True
        )
        if any(group is None for group in (new_outputs, new_inputs, new_despite)):
            return None
        return Procedure(outputs=new_outputs, inputs=new_inputs, despite=new_despite)

    def __len__(self):
        r"""
        Get number of generic :class:`.Factor`\s specified for ``self``.

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
        r"""
        Get :class:`.Factor`\s in ``inputs``, ``outputs``, and ``despite``.

        :returns:
            a :class:`list` of all :class:`.Factor`\s.
        """

        inputs = self.inputs or ()
        despite = self.despite or ()
        return [*self.outputs, *inputs, *despite]

    @property
    def generic_factors(self) -> Tuple[Factor, ...]:
        r"""
        :class:`.Factor`\s that can be replaced without changing ``self``\s meaning.

        If ``self.generic is True`` then the only generic :class:`.Factor` is ``self``.
        This could happen if the :class:`.Procedure` was mentioned generically in an
        :class:`.Argument` about preserving objections for appeal, for instance.

        :returns:
            ``self``'s generic :class:`.Factor`\s,
            which must be matched to other generic :class:`.Factor`\s to
            perform equality or implication tests between :class:`.Factor`\s
            with :meth:`.Factor.means` or :meth:`.Factor.__ge__`.
        """
        if self.generic:
            return (self,)
        return tuple(
            {
                generic: None
                for factor in self.factors_all
                for generic in factor.generic_factors
            }
        )

    def add_factor(self, incoming: Factor, role: str = "inputs") -> Procedure:
        """
        Add an output, input, or despite :class:`.Factor`.

        :param incoming:
            the new :class:`.Factor` to be added to input, output, or despite

        :param role:
            specifies whether the new :class:`.Factor` should be added to
            input, output, or despite

        :returns:
            a new version of ``self`` with the specified change
        """

        if role not in self.context_factor_names:
            raise ValueError(f"'role' must be one of {self.context_factor_names}")
        old_factors = self.__dict__.get(role) or []
        new_factors = list(old_factors) + [incoming]
        return self.evolve({role: new_factors})

    def consistent_factor_groups(
        self,
        self_factors: Tuple[Factor],
        other_factors: Tuple[Factor],
        matches: ContextRegister,
    ):
        r"""
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
        self, other: Procedure, matches: ContextRegister
    ) -> bool:
        r"""
        Test whether outputs of two :class:`Procedure`\s can contradict.

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
        r"""
        Find if ``self`` applying in some cases implies ``other`` cannot apply in some.

        Raises an error because, by analogy with :meth:`.Procedure.implies`\,
        users might expect this method to return ``True`` only when
        :class:`Rule` with ``universal=False`` and Procedure ``self``
        would contradict another :class:`Rule` with ``universal=False``
        and Procedure ``other``. But that would never happen.
        """
        raise NotImplementedError(
            "Procedures do not contradict one another unless one of them ",
            "applies in 'ALL' cases. Consider using ",
            "'Procedure.contradicts_some_to_all' or 'Rule.contradicts'.",
        )

    def contradicts_some_to_all(self, other: Procedure) -> bool:
        r"""
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
        relations = (Analogy(other.inputs, self_despite_or_input, operator.le),)
        matchlist = all_analogy_matches(relations)

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
            Analogy(other.outputs, self.outputs, operator.le),
            Analogy(self.inputs, other.inputs, operator.le),
        )
        matchlist = all_analogy_matches(relations)

        # For every factor in other, find the permutations of entity slots
        # that are consistent with matchlist and that don't cause the factor
        # to contradict any factor of self.

        return any(
            self.consistent_factor_groups(self.inputs, other.despite, matches)
            for matches in matchlist
        )

    def implies_all_to_some(self, other: Procedure) -> bool:
        r"""
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
            Analogy(other.outputs, self.outputs, operator.le),
            Analogy(other.despite, self_despite_or_input, operator.le),
        )

        matchlist = all_analogy_matches(relations)

        return any(
            self.consistent_factor_groups(self.inputs, other_despite_or_input, matches)
            for matches in matchlist
        )

    def _implies_if_present(self, other: Factor) -> bool:
        r"""
        Find if ``self`` would imply ``other`` if they aren't absent.

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
        if not isinstance(other, self.__class__):
            return False
        despite_or_input = (*self.despite, *self.inputs)

        relations = (
            Analogy(other.outputs, self.outputs, operator.le),
            Analogy(other.inputs, self.inputs, operator.le),
            Analogy(other.despite, despite_or_input, operator.le),
        )

        return bool(all_analogy_matches(relations))

    def means(self, other) -> bool:
        r"""
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
        matchlist = [ContextRegister()]
        for group in groups:
            updater = Analogy(
                need_matches=self.__dict__[group],
                available=other.__dict__[group],
                comparison=means,
            )
            matchlist = updater.update_matchlist(matchlist)
        if not bool(matchlist):
            return False

        # Now doing the same thing in reverse
        matchlist = [ContextRegister()]
        for group in groups:
            updater = Analogy(
                need_matches=other.__dict__[group],
                available=self.__dict__[group],
                comparison=means,
            )
            matchlist = updater.update_matchlist(matchlist)
        return bool(matchlist)

    @new_context_helper
    def new_context(self, changes: ContextRegister) -> Procedure:
        r"""
        Create new :class:`Procedure`, replacing keys of ``changes`` with values.

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
                factor.new_context(changes) for factor in new_dict[name]
            )
        return self.__class__(**new_dict)

    def triggers_next_procedure(self, other: Procedure) -> List[ContextRegister]:
        r"""
        Test if :class:`.Factor`\s from firing ``self`` would trigger ``other``.

        .. Note::
            To be confident that ``self`` actually can trigger ``other``,
            we would have to assume that ``other`` has ``universal: True``
            since otherwise we don't know exactly what is required to
            trigger ``other``.

        :param other:
            another :class:`Procedure` to test to see whether it can
            be triggered by triggering ``self``

        :returns:
            whether the set of :class:`Factor`\s that exist after ``self``
            is fired could trigger ``other``
        """
        self_despite_or_input = (*self.despite, *self.inputs)
        self_output_or_input = (*self.outputs, *self.inputs)

        relations = (
            Analogy(other.inputs, self_output_or_input, operator.le),
            Analogy(other.despite, self_despite_or_input, operator.le),
        )
        return all_analogy_matches(relations)
