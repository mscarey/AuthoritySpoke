"""Functions for indexing named objects in JSON to be imported."""
from __future__ import annotations

from collections import OrderedDict
from re import findall

from typing import Dict, List, Optional, Tuple, Union


class Mentioned(OrderedDict):
    def insert_by_name(self, obj: Dict):
        self[obj["name"]] = obj.copy()
        self[obj["name"]].pop("name")

    def get_by_name(self, name: str) -> Dict:
        value = self[name]
        value["name"] = name
        return value

    def sorted_by_length(self) -> Mentioned:
        return Mentioned(sorted(self.items(), key=lambda t: len(t[0]), reverse=True))

    def __str__(self):
        return f"Mentioned({str(dict(self))})"

    def __repr__(self):
        return f"Mentioned({repr(dict(self))})"


def get_references_from_string(content: str) -> Tuple[str, List[Dict]]:
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
    context_factors = []
    for entity_name in entities_as_text:
        entity = {"type": "Entity", "name": entity_name}
        context_factors.append(entity)
    sorted_entities = sorted(entities_as_text, key=len, reverse=True)
    for entity_name in sorted_entities:
        content = content.replace(entity_name, "")

    return content, context_factors


def expand_shorthand_mentioned(obj: Dict) -> Dict:
    """
    Expand any Entity references that use the curly bracket shorthand.

    :param obj:
        object loaded from JSON to make a :class:`.Factor` or :class:`.Holding`

    :returns:
        the input object, but with shorthand references expanded.
    """
    if isinstance(obj, List):
        return [expand_shorthand_mentioned(item) for item in obj]
    if not isinstance(obj, Dict):
        return obj
    if obj.get("content") and not obj.get("context_factors"):
        obj["content"], obj["context_factors"] = get_references_from_string(
            obj["content"]
        )
    elif obj.get("predicate", {}).get("content") and not obj.get("context_factors"):
        obj["predicate"]["content"], obj[
            "context_factors"
        ] = get_references_from_string(obj["predicate"]["content"])

    for key, value in obj.items():
        if isinstance(value, (Dict, List)) and key != "predicate":
            obj[key] = expand_shorthand_mentioned(value)
    return obj


def collect_mentioned(obj: Dict, mentioned: Optional[Mentioned] = None) -> Mentioned:
    """
    Make a dict of all nested objects labeled by name.

    To be used during loading to expand name references to full objects.
    """
    mentioned = mentioned or Mentioned()
    if isinstance(obj, List):
        for item in obj:
            mentioned.update(collect_mentioned(item))
    if isinstance(obj, Dict):
        if obj.get("name"):
            mentioned.insert_by_name(obj)
        for _, value in obj.items():
            if isinstance(value, (Dict, List)):
                mentioned.update(collect_mentioned(value))
    return mentioned


def index_names(obj: Dict) -> Tuple[Dict, Mentioned]:
    """
    Call all functions to prepare "mentioned" index.

    The names are sorted by length so that if one mentioned Factor's name
    is a substring of another, the longest available name is expanded.

    :returns:
        a modified version of the dict to load, plus a dict of names
        and the objects to expand them with.
    """
    obj = expand_shorthand_mentioned(obj)
    mentioned = collect_mentioned(obj)
    return obj, mentioned
