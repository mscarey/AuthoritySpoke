"""For expanding text in input JSON into a format Marshmallow can load."""

from authorityspoke.predicates import StatementTemplate
from re import findall
from string import Template
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from marshmallow import ValidationError
from slugify import slugify

from authorityspoke.io import nesting


def expand_shorthand(obj: Union[List, Dict]) -> Union[List, Dict[str, Any]]:
    """Traverse dict and expand every kind of pre-loading shorthand."""
    return nesting.walk_tree_and_modify(
        obj=obj, func=expand_node_shorthand, ignore=("predicate",)
    )


def expand_node_shorthand(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Expand shorthand at one node while walking tree of input JSON."""
    for list_field in ("terms", "anchors"):
        if obj.get(list_field) is not None:
            obj = wrap_single_element_in_list(obj, list_field)

    to_nest = ["content", "truth", "sign", "expression"]
    obj = nesting.nest_fields(obj, nest="predicate", eggs=to_nest)

    obj = collapse_known_factors(obj)

    return obj


def collapse_known_factors(obj: Dict):
    """Replace all names of known context factors with placeholder strings."""
    if obj.get("terms"):
        for factor in obj["terms"]:
            if isinstance(factor, str):
                name = factor
            else:
                name = factor.get("name")
            if name:
                if name in obj["predicate"]["content"]:
                    obj["predicate"]["content"] = collapse_name_in_content(
                        obj["predicate"]["content"], name
                    )
                else:
                    obj["predicate"]["content"] = replace_brackets_with_placeholder(
                        obj["predicate"]["content"], name
                    )
    return obj


def replace_brackets_with_placeholder(content: str, name: str):
    """Replace brackets with placeholder to show it is referenced in terms."""
    slug = slugify(text=name, separator="_", replacements=[[" ", "_"]])
    placeholder_slug = "${" + slug + "}"
    if placeholder_slug not in content:
        content = content.replace("{}", "${" + slug + "}", 1)
    return content


def collapse_name_in_content(content: str, name: str):
    """Replace name with placeholder to show it is referenced in terms."""
    slug = slugify(text=name, separator="_", replacements=[[" ", "_"]])
    placeholder_slug = "${" + slug + "}"
    if placeholder_slug not in content:
        content = content.replace(name, placeholder_slug)
        content = content.replace("{${", "${", 1).replace("}}", "}", 1)
    return content


def add_found_context_with_brackets(
    content: str, terms: List[Dict], factor: Dict, placeholder="{}"
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Remove bracketed mentions of factor with placeholder and list replacements.

    :returns:
        Content with mentions of factor replaced by placeholder, and
        a terms list with the factor inserted in a position
        corresponding to its position in the context phrase.
    """
    bracketed_name = "{" + factor["name"] + "}"
    if bracketed_name in content:
        index_in_content = content.index(bracketed_name)
        index_in_factor_list = content[:index_in_content].count("${")
        terms.insert(index_in_factor_list, factor)
        content = collapse_name_in_content(content, factor["name"])
    return content, terms


def add_found_context(
    content: str, terms: List[Dict], factor: Dict
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Replace mentions of factor with placeholder and list replacements.

    :returns:
        Content with mentions of factor replaced by placeholder, and
        a terms list with the factor inserted in a position
        corresponding to its position in the context phrase.
    """
    # if factor["name"] is inside an existing placeholder, replace it with a special placeholder
    template = Template(content)
    matches = list(template.pattern.finditer(template.template))
    for match in matches[::-1]:  # backwards to avoid changing index of a later match
        mangled_placeholder = content[match.start() : match.end()].replace(
            factor["name"], "@@@@"
        )
        content = (
            content[: match.start()] + mangled_placeholder + content[match.end() :]
        )

    if factor["name"] in content:
        index_in_content = content.index(factor["name"])
        index_in_factor_list = content[:index_in_content].count("$")
        terms.insert(index_in_factor_list, factor)
        content = collapse_name_in_content(content, factor["name"])

    # replace the special placeholder with factor["name"]
    content = content.replace("@@@@", factor["name"])
    return content, terms


def get_references_from_string(
    content: str, terms: Optional[List[Dict]]
) -> Tuple[str, Sequence[Dict]]:
    r"""
    Make :class:`.Entity` context :class:`.Factor`\s from string.

    This function identifies context :class:`.Factor`\s by finding
    brackets around them, while :func:`get_references_from_mentioned`
    depends on knowing the names of the context factors in advance.
    Also, this function works only when all the terms
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
    pattern = r"(?<!\$)\{([^\{]+)\}"  # matches bracketed text not preceded by $
    entities_as_text = findall(pattern, content)
    entities_as_text.sort(key=len, reverse=True)
    terms = terms or []
    for entity_name in entities_as_text:
        entity = {"type": "Entity", "name": entity_name}
        content, terms = add_found_context_with_brackets(content, terms, entity)

    return content, terms


def wrap_single_element_in_list(data: Dict, many_element: str):
    """Make a specified field a list if it isn't already a list."""
    if not isinstance(data[many_element], list):
        data[many_element] = [data[many_element]]
    return data
