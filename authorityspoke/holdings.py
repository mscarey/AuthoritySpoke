from __future__ import annotations

import json
import operator
import pathlib

from typing import ClassVar, Dict, Iterable, List, Sequence, Tuple
from typing import Iterator, Optional, Union

from dataclasses import dataclass

from authorityspoke.context import get_directory_path
from authorityspoke.factors import Factor
from authorityspoke.rules import Rule
from authorityspoke.selectors import TextQuoteSelector


@dataclass(frozen=True)
class Holding:
    """
    An :class:`.Opinion`\'s announcement that it posits or rejects a legal :class:`.Rule`.

    Note that if an opinion merely says the court is not deciding whether
    a :class:`.Rule` is valid, there is no :class:`Holding`, and no
    :class:`.Rule` object should be created. Deciding not to decide
    a :class:`Rule`\'s validity is not the same thing as deciding
    that the :class:`.Rule` is undecided.

    :param rule:
        a statement of a legal doctrine about a :class:`.Procedure` for litigation.

    :param rule_valid:
        ``True`` means the :class:`.Rule` is asserted to be valid (or
        useable by a court in litigation). ``False`` means it's asserted
        to be invalid.

    :param decided:
        ``False`` means that it should be deemed undecided
        whether the :class:`.Rule` is valid, and thus can have the
        effect of overruling prior holdings finding the :class:`.Rule`
        to be either valid or invalid. Seemingly, ``decided=False``
        should render the ``rule_valid`` flag irrelevant.

    :param selector:
        A text selector for the whole :class:`Holding`, not for any
        individual :class:`.Factor`. Often selects text used to
        indicate whether the :class:`.Rule` is ``mandatory``, ``universal``,
        ``valid``, or ``decided``, or shows the ``exclusive`` way to reach
        the outputs.
    """

    rule: Rule
    rule_valid: bool = True
    decided: bool = True
    selector: Optional[TextQuoteSelector] = None

    directory: ClassVar = get_directory_path("holdings")

    @classmethod
    def from_dict(
        cls, record: Dict, mentioned: List[Factor], regime: Optional[Regime] = None
    ) -> Iterator[Tuple[Holding, List[Factor], Dict[Factor, List[TextQuoteSelector]]]]:
        """
        Will yield multiple items if ``exclusive: True`` is present in ``record``.


        """

        # If lists were omitted around single elements in the JSON,
        # add them back

        for category in ("inputs", "despite", "outputs"):
            if isinstance(record.get(category), dict):
                record[category] = [record[category]]

        factor_text_links: Dict[Factor, List[TextQuoteSelector]] = {}
        factor_groups: Dict[str, List] = {"inputs": [], "outputs": [], "despite": []}
        for factor_type in factor_groups:
            for factor_dict in record[factor_type]:
                created, mentioned = Factor.from_dict(
                    factor_dict, mentioned, regime=regime
                )
                if isinstance(factor_dict, dict):
                    selector_group = factor_dict.pop("text", None)
                    if selector_group:
                        selector_group = [
                            TextQuoteSelector.from_json(selector)
                            for selector in selector_group
                        ]
                        factor_text_links[created] = selector_group
                factor_groups[factor_type].append(created)

        exclusive = record.pop("exclusive", None)
        rule_valid = record.pop("rule_valid", True)
        decided = record.pop("decided", True)
        selector = TextQuoteSelector.from_json(record.pop("text", None))

        basic_rule = Rule.from_dict(
            record=record,
            mentioned=mentioned,
            regime=regime,
            factor_groups=factor_groups,
        )
        yield (
            Holding(
                rule=basic_rule,
                rule_valid=rule_valid,
                decided=decided,
                selector=selector,
            ),
            mentioned,
            factor_text_links,
        )

        if exclusive:
            if not rule_valid:
                raise NotImplementedError(
                    "The ability to state that it is not 'valid' to assert "
                    + "that a Rule is the 'exclusive' way to reach an output is "
                    + "not implemented, so 'rule_valid' cannot be False while "
                    + "'exclusive' is True. Try expressing this in another way "
                    + "without the 'exclusive' keyword."
                )
            if not decided:
                raise NotImplementedError(
                    "The ability to state that it is not 'decided' whether "
                    + "a Rule is the 'exclusive' way to reach an output is "
                    + "not implemented. Try expressing this in another way "
                    + "without the 'exclusive' keyword."
                )
            for modified_rule in basic_rule.get_contrapositives():
                yield (Holding(rule=modified_rule, selector=selector), mentioned, {})

        # Continue by handing off to Rule.from_dict, which will have to be changed
        # to handle the Factors already having been created.
