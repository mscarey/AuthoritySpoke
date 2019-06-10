"""Objects that test whether a function holds between two groups of :class:`.Factor`\s."""

from __future__ import annotations

from typing import Callable, Dict, Iterator
from typing import List, Optional, Tuple

from dataclasses import dataclass


@dataclass(frozen=True)
class Analogy:
    """
    Two groups of :class:`.Factor`\s and a function that must hold between them.

    Can be used to find ways to assign the :class:`.Factor`\s'
    context assignments consistently with the ``Analogy``.

    :param need_matches:
        :class:`.Factor`\s that all need to satisfy the ``comparison``
        with some :class:`.Factor` of ``available``
        for the relation to hold.

    :param available:
        :class:`.Factor`\s available for matching with the
        :attr:`need_matches` :class:`.Factor`\s, but that don't
        all need to be matched themselves for the relation to hold.

    :param comparison:
        a function defining the comparison that must be ``True``
        between each :attr:`need_matches` and some :attr:`available`
        for the relation to hold. Could be :meth:`.Factor.means` or
        :meth:`.Factor.__ge__`.
    """

    need_matches: Tuple[Factor, ...]
    available: Tuple[Factor, ...]
    comparison: Callable

    def ordered_comparison(
        self, matches: Optional[Dict[Factor, Factor]] = None
    ) -> Iterator[Dict[Factor, Optional[Factor]]]:
        """
        Find ways for a series of pairs of :class:`.Factor`\s to satisfy a comparison.

        :param matches:
            keys representing :class:`.Factor`\s in ``self`` and
            values representing :class:`.Factor`\s in ``other``. The
            keys and values have been found in corresponding positions
            in ``self`` and ``other``.

        :yields:
            every way that ``matches`` can be updated to be consistent
            with each element of ``self.need_matches`` having the relationship
            ``self.comparison`` with the item at the corresponding index of
            ``self.available``.
        """
        if matches is None:
            matches = {}
        new_mapping_choices = [matches]

        # The "is" comparison is for None values.
        if not all(
            self_factor is self.available[index]
            or self.comparison(self_factor, self.available[index])
            for index, self_factor in enumerate(self.need_matches)
        ):
            return None
        # TODO: change to depth-first
        for index, self_factor in enumerate(self.need_matches):
            mapping_choices = new_mapping_choices
            new_mapping_choices = []
            for mapping in mapping_choices:
                if self_factor is None:
                    new_mapping_choices.append(mapping)
                else:
                    for incoming_register in self_factor.update_context_register(
                        self.available[index], mapping, self.comparison
                    ):
                        if incoming_register not in new_mapping_choices:
                            new_mapping_choices.append(incoming_register)
        for choice in new_mapping_choices:
            yield choice

    def unordered_comparison(
        self,
        matches: Dict[Factor, Factor],
        still_need_matches: Optional[List[Factor]] = None,
    ) -> Iterator[Dict[Factor, Optional[Factor]]]:
        """
        Find ways for two unordered sets of :class:`.Factor`\s to satisfy a comparison.

        :param matches:
            a mapping of :class:`.Factor`\s that have already been matched
            to each other in the recursive search for a complete group of
            matches. Starts empty when the method is first called.

        :param still_need_matches:
            :class:`.Factor`\s that need to satisfy the comparison
            :attr:`comparison` with some :class:`.Factor` of :attr:`available`
            for the relation to hold, and have not yet been matched.

        :yields:
            context registers showing how each :class:`.Factor` in
            ``need_matches`` can have the relation ``comparison``
            with some :class:`.Factor` in ``available_for_matching``,
            with matching context.
        """
        if still_need_matches is None:
            still_need_matches = list(self.need_matches)

        if not still_need_matches:
            # This seems to allow duplicate values in
            # Procedure.output, .input, and .despite, but not in
            # attributes of other kinds of Factors. Likely cause
            # of bugs.
            yield matches
        else:
            self_factor = still_need_matches.pop()
            for other_factor in self.available:
                if self.comparison(self_factor, other_factor):
                    updated_mappings = iter(
                        self_factor.update_context_register(
                            other_factor, matches, self.comparison
                        )
                    )
                    for new_matches in updated_mappings:
                        if new_matches:
                            next_steps = iter(
                                self.unordered_comparison(
                                    new_matches, still_need_matches
                                )
                            )
                            for next_step in next_steps:
                                yield next_step

    def update_matchlist(
        self, matchlist: List[Dict[Factor, Factor]]
    ) -> List[Dict[Factor, Optional[Factor]]]:
        """
        Filter :class:`list` of :class:`.Factor` assignments with :meth:`~Analogy.unordered_comparison`.

        :param matchlist:
            possible ways to match generic :class:`.Factor`\s of
            ``need_matches`` with ``available``.

        :returns:
            a new version of ``matchlist`` filtered to be consistent with
            ``self``\'s :meth:`~Analogy.unordered_comparison`.
        """
        new_matchlist = []
        for matches in matchlist:
            for answer in self.unordered_comparison(matches=matches):
                new_matchlist.append(answer)
        return new_matchlist
