"""Functions for indexing named objects in JSON to be imported."""

from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
from re import findall
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from authorityspoke.predicates import StatementTemplate
from authorityspoke.io import text_expansion


RawPredicate = Dict[str, Union[str, bool]]
RawFactor = Dict[str, Union[RawPredicate, Sequence[Any], str, bool]]


class Mentioned(OrderedDict):
    """Index of cross-referenced objects, keyed to phrases that reference them."""

    def insert_by_name(self, obj: Dict) -> None:
        """Add record to dict, using value of record's "name" field as the dict key."""
        self[obj["name"]] = obj.copy()
        self[obj["name"]].pop("name")
        return None

    def get_by_name(self, name: str) -> Dict:
        """
        Convert retrieved record so name is a field rather than the key for the whole record.

        :param name:
            the name of the key where the record can be found in the Mentioned dict.

        :returns:
            the value stored at the key "name", plus a name field.
        """
        if not self.get(name):
            raise ValueError(
                f'Name "{name}" not found in the index of mentioned Factors'
            )
        value = {"name": name}
        value.update(self[name])
        return value

    def sorted_by_length(self) -> Mentioned:
        """
        Sort dict items from longest to shortest.

        Used to ensure that keys nearer the start can't be substrings of later keys.
        """
        return Mentioned(sorted(self.items(), key=lambda t: len(t[0]), reverse=True))

    def __str__(self):
        return f"Mentioned({str(dict(self))})"

    def __repr__(self):
        return f"Mentioned({repr(dict(self))})"


def assign_name_from_content(obj: Dict) -> str:
    r"""
    Use the content to assign a name to any Fact that lacks one.

    This can fail if the parser replaces placeholder text with another placeholder

    :param obj:
        object loaded from JSON to make a :class:`.Factor` or :class:`.Holding`

    :returns:
        a new name
    """

    if obj.get("terms"):
        template = StatementTemplate(obj["predicate"]["content"])
        placeholders = template.get_placeholders()
        if any(placeholders):
            substitutions = dict(zip(placeholders, obj["terms"]))
            content_for_name = template.substitute(substitutions)
        else:
            content_for_name = obj["predicate"]["content"]
            for context_factor in obj["terms"]:
                content_for_name = content_for_name.replace("{}", context_factor, 1)
    else:
        content_for_name = obj["predicate"]["content"]
    false_modifier = "false " if obj["predicate"].get("truth") is False else ""
    return f"{false_modifier}{content_for_name}".replace("{", "").replace("}", "")


def assign_name_for_evidence(obj: Dict) -> str:
    r"""
    Return an appropriate name for Evidence.

    :param obj: an unloaded :class:`.Evidence` object

    :returns: a name for the Evidence
    """
    name = "evidence"
    if obj.get("exhibit"):
        name += f' of {obj["exhibit"]}'
    if obj.get("to_effect"):
        name += f' to the effect that {obj["to_effect"]}'
    return name


def assign_name_for_pleading(obj: Dict) -> str:
    r"""
    Return an appropriate name for a Pleading.

    :param obj: an unloaded :class:`.Pleading`

    :returns: a name for the Pleading
    """
    name = "pleading"
    if obj.get("filer"):
        name += f' filed by {obj["filer"]}'
    return name


def create_name_for_factor(obj: Dict) -> str:
    """
    Determine what kind of RawFactor the input is and return an appropriate name.

    :param obj: an unloaded :class:`.Factor`

    :returns: a name for the Factor
    """

    if (
        obj.get("content")  # Predicates don't need name
        or obj.get("rule")
        or obj.get("procedure")
        or obj.get("outputs")  # Procedures, Rules, and Holdings don't need names
        or obj.get("exact")
        or obj.get("prefix")
        or obj.get("suffix")  # Text Selectors don't need names
    ):
        return ""
    elif obj.get("predicate", {}).get("content"):
        name = assign_name_from_content(obj)
    elif obj.get("exhibit") or (obj.get("type") and obj["type"].lower()) == "evidence":
        name = assign_name_for_evidence(obj)
    elif obj.get("type") and obj["type"].lower() == "pleading":
        name = assign_name_for_pleading(obj)
    else:
        raise NotImplementedError
    if obj.get("absent") is True:
        name = f"absent {name}"
    return name


def ensure_factor_has_name(obj: Dict) -> Dict:
    """
    Add a name to a RawFactor if it doesn't already have one.

    :param obj: an unloaded :class:`.Factor`

    :returns: the same :class:`.Factor` with a name field added
    """
    if not obj.get("name"):
        new_name = create_name_for_factor(obj)
        if new_name:
            obj["name"] = new_name
    return obj


def update_name_index_from_terms(terms: List[RawFactor], mentioned: Mentioned):
    r"""
    Update name index from a list of :class:`.RawFactor`\s or strings referencing them.

    :param terms:
        a list of :class:`.RawFactor`\s or strings referencing them. Both
        :class:`.RawFactor`\s and strings may exist in the list.

    :param mentioned:
        :class:`.RawFactor`\s indexed by name for retrieval when loading objects
        using a Marshmallow schema.

    :returns:
        an updated "mentioned" name index
    """

    for factor in terms:
        if isinstance(factor, str):
            factor_name = factor
            if factor_name not in mentioned:
                raise ValueError(
                    f"Unable to expand referenced Factor '{factor_name}'. "
                    "It doesn't exist in the index of mentioned Factors."
                )
        else:
            factor_name = factor.get("name")
            if factor_name and factor_name not in mentioned:
                mentioned.insert_by_name(factor)
    return mentioned.sorted_by_length()


RawContextFactors = List[Union[RawFactor, str]]


def update_name_index_from_bracketed_phrases(
    content: str, mentioned: Mentioned
) -> Mentioned:
    pattern = r"(?<!\$)\{([^\{]+)\}"  # matches bracketed text not preceded by $
    entities_as_text = findall(pattern, content)
    entities_as_text.sort(key=len, reverse=True)

    for entity_name in entities_as_text:
        if entity_name not in mentioned:
            entity = {"type": "Entity", "name": entity_name}
            mentioned.insert_by_name(entity)
    return mentioned


def update_name_index_from_fact_content(
    obj: RawFactor, mentioned: Mentioned
) -> Tuple[RawFactor, Mentioned]:
    r"""
    Update index of mentioned Factors from Factors mentioned in Fact's content, and vice versa.

    :param obj:
        data from JSON to be loaded as a :class:`.Factor`
    :param mentioned:
        :class:`.RawFactor`\s indexed by name for retrieval when loading objects
        using a Marshmallow schema.

    :returns:
        both 'obj' and 'mentioned', updated with values from each other
    """

    predicate: RawPredicate = obj.get("predicate", {})
    content: str = predicate.get("content", "")
    if content:
        terms: RawContextFactors = obj.get("terms", [])
        mentioned = update_name_index_from_bracketed_phrases(
            content=content, mentioned=mentioned
        )
        mentioned = update_name_index_from_terms(terms, mentioned)

        for name in mentioned.keys():
            if name in content and name != content:
                (content, terms,) = text_expansion.add_found_context(
                    content=content,
                    terms=terms,
                    factor=mentioned.get_by_name(name),
                )
        obj["terms"] = terms
        obj["predicate"]["content"] = content
    return obj, mentioned


def update_name_index_with_factor(
    obj: RawFactor, mentioned: Mentioned
) -> Tuple[Union[str, RawFactor], Mentioned]:
    r"""
    Update index of mentioned Factors with 'obj', if obj is named.

    If there is already an entry in the mentioned index with the same name
    as obj, the old entry won't be replaced. But if any additional text
    anchors are present in the new obj, the anchors will be added.

    If obj has a name, it will be collapsed to a name reference.

    :param obj:
        data from JSON to be loaded as a :class:`.Factor`

    :param mentioned:
        :class:`.RawFactor`\s indexed by name for retrieval when loading objects
        using a Marshmallow schema.

    :returns:
        both 'obj' and 'mentioned', as updated
    """
    if obj.get("name"):
        if obj["name"] in mentioned:
            if obj.get("anchors"):
                for anchor in obj["anchors"]:
                    mentioned[obj["name"]]["anchors"].append(anchor)
        else:
            mentioned.insert_by_name(obj)
        obj = obj["name"]
    return obj, mentioned


def collect_mentioned(
    obj: Union[RawFactor, List[Union[RawFactor, str]]],
    mentioned: Optional[Mentioned] = None,
    keys_to_ignore: Sequence[str] = ("predicate", "anchors"),
) -> Tuple[RawFactor, Mentioned]:
    """
    Make a dict of all nested objects labeled by name, creating names if needed.
    To be used during loading to expand name references to full objects.
    """
    mentioned = mentioned or Mentioned()
    if isinstance(obj, List):
        new_list = []
        for item in obj:
            new_item, new_mentioned = collect_mentioned(item, mentioned)
            mentioned.update(new_mentioned)
            new_list.append(new_item)
        obj = new_list
    if isinstance(obj, Dict):

        obj, mentioned = update_name_index_from_fact_content(obj, mentioned)

        for key, value in obj.items():
            if key not in keys_to_ignore:
                if isinstance(value, (Dict, List)):
                    new_value, new_mentioned = collect_mentioned(value, mentioned)
                    mentioned.update(new_mentioned)
                    obj[key] = new_value
        obj = ensure_factor_has_name(obj)

        # Added because a top-level factor was not having its brackets replaced
        if obj.get("predicate", {}).get("content"):
            for factor in obj.get("terms", []):
                if factor not in obj["predicate"]["content"]:
                    obj["predicate"][
                        "content"
                    ] = text_expansion.replace_brackets_with_placeholder(
                        content=obj["predicate"]["content"], name=factor
                    )

        obj, mentioned = update_name_index_with_factor(obj, mentioned)
    return obj, mentioned


def index_names(record: Union[List, Dict]) -> Mentioned:
    """
    Call all functions to prepare "mentioned" index.

    The names are sorted by length so that if one mentioned Factor's name
    is a substring of another, the longest available name is expanded.

    :returns:
        a modified version of the dict to load, plus a dict of names
        and the objects to expand them with.
    """
    obj = deepcopy(record)
    obj = text_expansion.expand_shorthand(obj)
    obj, mentioned = collect_mentioned(obj)
    sorted_mentioned = mentioned.sorted_by_length()
    return obj, sorted_mentioned
