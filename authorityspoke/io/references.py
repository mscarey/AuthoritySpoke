import functools

from typing import Callable, Dict, Iterable, List, Optional, Tuple, Union

from authorityspoke.enactments import Code, Enactment
from authorityspoke.factors import Factor
from authorityspoke.jurisdictions import Regime
from authorityspoke.selectors import TextQuoteSelector


def _find_or_build_factor(
    factor_record: Dict[str, Union[str, bool]],
    mentioned: Dict[Factor, List[TextQuoteSelector]],
    func: Callable,
    code: Optional[Code] = None,
    regime: Optional[Regime] = None,
) -> Tuple[Optional[Factor], Dict[Factor, List[TextQuoteSelector]]]:
    """
    Retrieve cached :class:`.Factor` if possible, or else build one.

    Should be called by log_mentioned_context, which should
    have already normalized the parameter types,
    so this function can have simpler type annotations.
    """

    new_factor, mentioned = func(
        factor_record,
        mentioned=mentioned,
        code=code,
        regime=regime,
        report_mentioned=True,
    )

    mentioned = mentioned or {}

    if not factor_record.get("name") and (
        not hasattr(new_factor, "generic") or not new_factor.generic
    ):
        for context in mentioned:
            if context == new_factor:
                return context, mentioned

    if hasattr(new_factor, "recursive_factors"):
        factors_to_add = new_factor.recursive_factors
    else:
        factors_to_add = [new_factor]
    for recursive_factor in factors_to_add:
        if recursive_factor not in mentioned:
            mentioned[recursive_factor] = []

    text = factor_record.pop("text", None)
    if text:
        mentioned[new_factor] = read_selectors(text)
    return new_factor, mentioned


def log_mentioned_context(func: Callable):
    """
    Retrieve cached :class:`.Factor` instead of building one with the decorated method.

    Decorator for :meth:`.Factor.from_dict()` and :meth:`.Enactment.from_dict()`.

    If factor_record is a :class:`str` instead of a :class:`dict`, looks up the
    corresponding factor in "mentioned" and returns that instead of
    constructing a new :class:`.Factor`. Also, if the newly-constructed
    :class:`.Factor` has a ``name`` attribute, logs the :class:`.Factor`
    in ``mentioned`` for later use.
    """

    @functools.wraps(func)
    def wrapper(
        factor_record: Union[str, Optional[Dict[str, Union[str, bool]]]],
        mentioned: Optional[Dict[Factor, List[TextQuoteSelector]]] = None,
        code: Optional[Code] = None,
        regime: Optional[Regime] = None,
        report_mentioned: bool = False,
    ) -> Union[
        Factor, None, Tuple[Optional[Factor], Dict[Factor, List[TextQuoteSelector]]]
    ]:

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

        if mentioned is None:
            mentioned = {}

        if factor_record is None:
            return None, mentioned

        new_factor, mentioned = _find_or_build_factor(
            factor_record=factor_record,
            mentioned=mentioned,
            func=func,
            code=code,
            regime=regime,
        )

        return (new_factor, mentioned) if report_mentioned else new_factor

    return wrapper


def read_selector(text: Union[dict, str]) -> TextQuoteSelector:
    """
    Create new instance from JSON user input.

    If the input is a :class:`str`, tries to break up the string
    into :attr:`~TextQuoteSelector.prefix`, :attr:`~TextQuoteSelector.exact`,
    and :attr:`~TextQuoteSelector.suffix`, by splitting on the pipe characters.

    :param text:
        a string or dict representing a text passage

    :returns: a new :class:`TextQuoteSelector`
    """
    if isinstance(text, dict):
        return TextQuoteSelector(**text)
    if text.count("|") == 0:
        return TextQuoteSelector(exact=text)
    elif text.count("|") == 2:
        prefix, exact, suffix = text.split("|")
        return TextQuoteSelector(exact=exact, prefix=prefix, suffix=suffix)
    raise ValueError(
        "'text' must be either a dict, a string containing no | pipe "
        + "separator, or a string containing two pipe separators to divide "
        + "the string into 'prefix', 'exact', and 'suffix'."
    )


def read_selectors(
    records: Optional[Union[str, Dict[str, str], Iterable[Union[str, Dict[str, str]]]]]
) -> List[TextQuoteSelector]:
    r"""
    Create list of :class:`.TextQuoteSelector`\s from JSON user input.

    If the input is a :class:`str`, tries to break up the string
    into :attr:`~TextQuoteSelector.prefix`, :attr:`~TextQuoteSelector.exact`,
    and :attr:`~TextQuoteSelector.suffix`, by splitting on the pipe characters.

    :param record:
        a string or dict representing a text passage, or list of
        strings and dicts.

    :returns: a list of :class:`TextQuoteSelector`\s
    """
    if records is None:
        return []
    if isinstance(records, (str, dict)):
        return [read_selector(records)]
    return [read_selector(record) for record in records]
