r"""Resolving references in imported data to :class:`.Factor`\s and text passages."""

import functools

from typing import Callable, Dict, Iterable, List, Optional, Tuple, Union

from marshmallow import Schema, fields, pre_load, ValidationError

from authorityspoke.enactments import Code, Enactment
from authorityspoke.factors import Factor
from authorityspoke.jurisdictions import Regime
from authorityspoke.factors import TextLinkDict
from authorityspoke.selectors import TextQuoteSelector


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
        factor_record: Union[str, Optional[Dict[str, Union[str, bool]]]],
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
            factor_record,
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


class SelectorSchema(Schema):
    prefix = fields.Str()
    exact = fields.Str()
    suffix = fields.Str()
    path = fields.Url(relative=True)

    def split_text(self, text: str) -> Tuple[str, ...]:
        """
        Break up shorthand text selector format into three fields.

        Tries to break up the string into :attr:`~TextQuoteSelector.prefix`,
        :attr:`~TextQuoteSelector.exact`,
        and :attr:`~TextQuoteSelector.suffix`, by splitting on the pipe characters.

        :param text: a string or dict representing a text passage

        :returns: a tuple of the three values
        """

        if text.count("|") == 0:
            return ("", text, "")
        elif text.count("|") == 2:
            return tuple([*text.split("|")])
        raise ValidationError(
            "If the 'text' field is included, it must be either a dict"
            + "with one or more of 'prefix', 'exact', and 'suffix' "
            + "a string containing no | pipe "
            + "separator, or a string containing two pipe separators to divide "
            + "the string into 'prefix', 'exact', and 'suffix'."
        )

    @pre_load
    def expand_shorthand(
        self, data: Union[str, Dict[str, str]], **kwargs
    ) -> Dict[str, str]:
        """Convert input from shorthand format to normal selector format."""
        if isinstance(data, str):
            data = {"text": data}
        text = data.get("text")
        if text:
            data["prefix"], data["exact"], data["suffix"] = self.split_text(text)
            del data["text"]
        return data


def read_selector(
    record: Union[dict, str], source: Optional[Code] = None
) -> TextQuoteSelector:
    """
    Create new selector from JSON user input.

    :param record:
        a string or dict representing a text passage

    :returns: a new :class:`TextQuoteSelector`
    """

    selector_schema = SelectorSchema()
    return TextQuoteSelector(source=source, **selector_schema.load(record))


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
    schema = SelectorSchema(many=True)
    return [TextQuoteSelector(**record) for record in schema.load(records)]
