from re import findall
from typing import Dict, List, Optional, Tuple

from authorityspoke.io.nesting import nest_fields


def expand_shorthand(obj: Dict):
    """
    Traverse dict and expand every kind of pre-loading shorthand.
    """
    if isinstance(obj, List):
        return [expand_shorthand(item) for item in obj]
    if not isinstance(obj, Dict):
        return obj

    obj = expand_node_shorthand(obj)

    for key, value in obj.items():
        if isinstance(value, (Dict, List)) and key != "predicate":
            obj[key] = expand_shorthand(value)
    return obj


def expand_node_shorthand(obj: Dict):
    for list_field in ("context_factors", "anchors"):
        if obj.get(list_field) is not None:
            obj = wrap_single_element_in_list(obj, list_field)

    to_nest = ["content", "truth", "reciprocal", "comparison", "quantity"]
    obj = nest_fields(obj, nest="predicate", eggs=to_nest)

    obj = assign_name_from_content(obj)
    obj = collapse_known_factors(obj)

    obj = expand_shorthand_mentioned(obj)

    return obj


def expand_shorthand_mentioned(obj: Dict) -> Dict:
    """
    Expand any Entity references that use the curly bracket shorthand.

    :param obj:
        object loaded from JSON to make a :class:`.Factor` or :class:`.Holding`

    :returns:
        the input object, but with shorthand references expanded.
    """

    if obj.get("predicate", {}).get("content"):
        obj["predicate"]["content"], obj[
            "context_factors"
        ] = get_references_from_string(
            obj["predicate"]["content"], obj.get("context_factors")
        )

    return obj


def collapse_known_factors(obj: Dict):
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


def collapse_name_in_content(
    content: str, name: Optional[str], placeholder: str = "{}"
):
    """
    Replace name with placeholder to show it is referenced in context_factors.
    """
    content = content.replace(name, placeholder, 1)
    double_placeholder = placeholder[0] + placeholder + placeholder[1]
    if double_placeholder in content:
        content = content.replace(double_placeholder, placeholder, 1)
    return content


def assign_name_from_content(obj: Dict) -> Dict:
    """
    Use the content to assign a name to any :class:`.Fact` that lacks one.

    :param obj:
        object loaded from JSON to make a :class:`.Factor` or :class:`.Holding`

    :returns:
        the input object, but with names assigned.
    """

    if (
        obj.get("predicate", {}).get("content")
        and not obj.get("name")
        and not obj.get("context_factors")
    ):
        obj["name"] = name_from_content(
            obj["predicate"]["content"], obj["predicate"].get("truth")
        )
    return obj


def add_found_context(
    content: str, context_factors: List[Dict], factor: Dict, placeholder="{}"
):
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
) -> Tuple[str, List[Dict]]:
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
        content, context_factors = add_found_context(content, context_factors, entity)

    return content, context_factors


def name_from_content(content: str, truth: Optional[bool] = None):
    false_modifier = "false " if truth is False else ""
    return f"{false_modifier}{content}".replace("{", "").replace("}", "")


def wrap_single_element_in_list(data: Dict, many_element: str):
    """
    Make a specified field a list if it isn't already a list.
    """
    if not isinstance(data[many_element], list):
        data[many_element] = [data[many_element]]
    return data
