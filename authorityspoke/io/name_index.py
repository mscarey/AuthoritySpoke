"""Functions for indexing named objects in JSON to be imported."""
from re import findall

from typing import Dict, List, Optional, Tuple, Union


class Mentioned(Dict[str, Dict]):
    def insert_by_name(self, obj: Dict):
        self[obj["name"]] = obj.copy()
        self[obj["name"]].pop("name")

    def get_by_name(self, name: str) -> Dict:
        value = self[name]
        value["name"] = name
        return value


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
        content = content.replace(entity_name, "")
        context_factors.append(entity)

    return content, context_factors


def expand_shorthand_mentioned(obj: Dict) -> Dict:
    """
    Expand any Entity references that use the curly bracket shorthand.

    :param obj:
        object loaded from JSON to make a :class:`.Factor` or :class:`.Holding`

    :returns:
        the input object, but with shorthand references expanded.
    """
    if not isinstance(obj, Dict):
        return obj
    if obj.get("content") and not obj.get("context_factors"):
        obj["content"], obj["context_factors"] = get_references_from_string(
            obj["content"]
        )
    for _, value in obj.items():
        if isinstance(value, Dict):
            value = expand_shorthand_mentioned(value, mentioned)
        elif isinstance(value, List):
            for item in value:
                item = expand_shorthand_mentioned(item, mentioned)
    return obj


def collect_mentioned(
    obj: Dict, mentioned: Optional[Mentioned] = None
) -> Tuple[Dict, Mentioned]:
    """
    Make a dict of all nested objects labeled by name.

    To be used during loading to expand name references to full objects.
    """
    mentioned = mentioned or Mentioned()
    if not isinstance(obj, Dict):
        return obj, mentioned
    if obj.get("name"):
        mentioned.insert_by_name(obj)
    for _, value in obj.items():
        if isinstance(value, Dict):
            value, mentioned = collect_mentioned(value, mentioned)
        elif isinstance(value, List):
            for item in value:
                item, mentioned = collect_mentioned(item, mentioned)
    return obj, mentioned
