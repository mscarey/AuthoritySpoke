r"""Resolving references in imported data to :class:`.Factor`\s and text passages."""

import functools
import re

from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

from authorityspoke.enactments import Code, Enactment
from authorityspoke.entities import Entity
from authorityspoke.factors import Factor
from authorityspoke.jurisdictions import Regime
from authorityspoke.factors import TextLinkDict


def _replace_new_factor_from_mentioned(
    new_factor: Union[Enactment, Factor], mentioned: TextLinkDict
) -> Union[Enactment, Factor]:
    """
    Check if ``new_factor`` can be replaced by an element of ``mentioned``.

    :param new_factor:
        May be identical to an element of ``mentioned``.

    :param mentioned:
        Contains :class:`.Factors` that have already been created.

    :returns:
        An element of mentioned identical to ``new_factor``, or else
        ``new_factor`` itself.
    """

    if not hasattr(new_factor, "generic") or not new_factor.generic:
        for context in mentioned:
            if context == new_factor:
                return context
    return new_factor


def log_mentioned_context(func: Callable):
    """
    Retrieve cached :class:`.Factor` instead of building one with the decorated method.

    Decorator for :func:`.read_factor` and :func:`.read_enactment`.

    If factor_record is a :class:`str` instead of a :class:`dict`, looks up the
    corresponding factor in "mentioned" and returns that instead of
    constructing a new :class:`.Factor`. Also, if the newly-constructed
    :class:`.Factor` has a ``name`` attribute, logs the :class:`.Factor`
    in ``mentioned`` for later use.
    """

    @functools.wraps(func)
    def wrapper(
        factor_record: Dict[str, Any],
        mentioned: Optional[TextLinkDict] = None,
        code: Optional[Code] = None,
        regime: Optional[Regime] = None,
        report_mentioned: bool = False,
    ) -> Union[Factor, None, Tuple[Optional[Factor], TextLinkDict]]:

        if isinstance(factor_record, str):
            factor_record = factor_record.lower()
            if mentioned is None:
                raise TypeError(
                    "No 'mentioned' list exists to search for a Factor "
                    + f"or Enactment by the name '{factor_record}'."
                )
            for context in mentioned:
                if (
                    hasattr(context, "name")
                    and context.name is not None
                    and context.name.lower() == factor_record
                ):
                    return (context, mentioned) if report_mentioned else context
            raise ValueError(
                "The 'factor_record' parameter should be a dict "
                + "representing a Factor or a string "
                + "representing the name of a Factor included in 'mentioned'."
            )

        if factor_record is None:
            return None, mentioned or {}

        if factor_record.get("anchors"):
            anchors = read_selectors(factor_record.get("anchors"))
        else:
            anchors = []

        new_factor, mentioned = func(
            **factor_record,
            mentioned=mentioned or {},
            code=code,
            regime=regime,
            report_mentioned=True,
        )
        mentioned = mentioned or {}
        if not factor_record.get("name"):
            new_factor = _replace_new_factor_from_mentioned(
                new_factor=new_factor, mentioned=mentioned
            )
        mentioned[new_factor] = anchors
        return (new_factor, mentioned) if report_mentioned else new_factor

    return wrapper


def get_references_from_string(content: str) -> Tuple[str, List[Entity]]:
    r"""
    Make :class:`.Entity` context :class:`.Factor`\s from string.
    This function identifies context :class:`.Factor`\s by finding
    brackets around them, while :func:`get_references_from_mentioned`
    depends on knowing the names of the context factors in advance.
    Also, this function works only when all the context_factors
    are type :class:`.Entity`.
    Despite "placeholder" being defined as a variable elsewhere,
    this function isn't compatible with any placeholder string other
    than "{}".
    This function no longer updates the "mentioned" :class:`.TextLinkDict`\.
    That update should instead happen after loading of each item in
    context_factors.
    :param content:
        a string containing a clause making an assertion.
        Curly brackets surround the names of :class:`.Entity`
        context factors to be created.
    :returns:
        a :class:`Predicate` and :class:`.Entity` objects
        from a string that has curly brackets around the
        context factors and the comparison/quantity.
    """
    pattern = r"\{([^\{]+)\}"
    entities_as_text = re.findall(pattern, content)

    context_factors = []
    for entity_name in entities_as_text:
        entity = {"type": "Entity", "name": entity_name}
        content = content.replace(entity_name, "")
        context_factors.append(entity)

    return content, context_factors
