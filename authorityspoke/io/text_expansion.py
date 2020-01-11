"""For expanding text in input JSON into a format Marshmallow can load."""

from re import findall
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from marshmallow import ValidationError

from authorityspoke.io import nesting


def expand_shorthand(obj: Union[List, Dict]) -> Union[List, Dict[str, Any]]:
    """Traverse dict and expand every kind of pre-loading shorthand."""
    return nesting.walk_tree_and_modify(
        obj=obj, func=expand_node_shorthand, ignore=("predicate",)
    )


def split_anchor_text(text: str) -> Tuple[str, ...]:
    """
    Break up shorthand text selector format into three fields.

    Tries to break up the  string into :attr:`~TextQuoteSelector.prefix`,
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
        "If the 'text' field is included, it must be either a dict "
        + "with one or more of 'prefix', 'exact', and 'suffix' "
        + "a string containing no | pipe "
        + "separator, or a string containing two pipe separators to divide "
        + "the string into 'prefix', 'exact', and 'suffix'."
    )


def expand_anchor_shorthand(
    data: Union[str, Dict[str, str]], **kwargs
) -> Dict[str, str]:
    """Convert input from shorthand format to normal selector format."""
    if isinstance(data, str):
        data = {"text": data}
    text = data.get("text")
    if text:
        data["prefix"], data["exact"], data["suffix"] = split_anchor_text(text)
        del data["text"]
    return data


def expand_node_shorthand(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Expand shorthand at one node while walking tree of input JSON."""
    for list_field in ("context_factors", "anchors"):
        if obj.get(list_field) is not None:
            obj = wrap_single_element_in_list(obj, list_field)

    to_nest = ["content", "truth", "reciprocal", "comparison", "quantity"]
    obj = nesting.nest_fields(obj, nest="predicate", eggs=to_nest)

    obj = collapse_known_factors(obj)

    if obj.get("anchors"):
        obj["anchors"] = [expand_anchor_shorthand(anchor) for anchor in obj["anchors"]]

    return obj


def collapse_known_factors(obj: Dict):
    """Replace all names of known context factors with placeholder strings."""
    if obj.get("context_factors"):
        for factor in obj["context_factors"]:
            if isinstance(factor, str):
                name = factor
            else:
                name = factor.get("name")
            if name:
                obj["predicate"]["content"] = collapse_name_in_content(
                    obj["predicate"]["content"], name
                )
    return obj


def collapse_name_in_content(content: str, name: str, placeholder: str = "{}"):
    """Replace name with placeholder to show it is referenced in context_factors."""
    content = content.replace(name, placeholder, 1)
    double_placeholder = placeholder[0] + placeholder + placeholder[1]
    if double_placeholder in content:
        content = content.replace(double_placeholder, placeholder, 1)
    return content


def add_found_context_with_brackets(
    content: str, context_factors: List[Dict], factor: Dict, placeholder="{}"
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Remove bracketed mentions of factor with placeholder and list replacements.

    :returns:
        Content with mentions of factor replaced by placeholder, and
        a context_factors list with the factor inserted in a position
        corresponding to its position in the context phrase.
    """
    bracketed_name = "{" + factor["name"] + "}"
    while bracketed_name in content:
        index_in_content = content.index(bracketed_name)
        index_in_factor_list = content[:index_in_content].count(placeholder)
        context_factors.insert(index_in_factor_list, factor)
        content = collapse_name_in_content(content, bracketed_name, placeholder)
    return content, context_factors


def add_found_context(
    content: str, context_factors: List[Dict], factor: Dict, placeholder="{}"
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Replace mentions of factor with placeholder and list replacements.

    :returns:
        Content with mentions of factor replaced by placeholder, and
        a context_factors list with the factor inserted in a position
        corresponding to its position in the context phrase.
    """
    while factor["name"] in content:
        index_in_content = content.index(factor["name"])
        index_in_factor_list = content[:index_in_content].count(placeholder)
        context_factors.insert(index_in_factor_list, factor)
        content = collapse_name_in_content(content, factor["name"], placeholder)
    return content, context_factors


def get_references_from_string(
    content: str, context_factors: Optional[List[Dict]]
) -> Tuple[str, Sequence[Dict]]:
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
    entities_as_text = findall(pattern, content)
    entities_as_text.sort(key=len, reverse=True)
    context_factors = context_factors or []
    for entity_name in entities_as_text:
        entity = {"type": "Entity", "name": entity_name}
        content, context_factors = add_found_context_with_brackets(
            content, context_factors, entity
        )

    return content, context_factors


def wrap_single_element_in_list(data: Dict, many_element: str):
    """Make a specified field a list if it isn't already a list."""
    if not isinstance(data[many_element], list):
        data[many_element] = [data[many_element]]
    return data
