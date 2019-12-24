"""Functions for indexing named objects in JSON to be imported."""
from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy

from typing import Dict, List, Optional, Sequence, Union

from marshmallow import ValidationError

from authorityspoke.io import text_expansion


class Mentioned(OrderedDict):
    def insert_by_name(self, obj: Dict) -> None:
        self[obj["name"]] = obj.copy()
        self[obj["name"]].pop("name")
        return None

    def get_by_name(self, name: str) -> Dict:
        if not self.get(name):
            raise ValidationError(
                f'Name "{name}" not found in the index of mentioned Factors'
            )
        value = {"name": name}
        value.update(self[name])
        return value

    def sorted_by_length(self) -> Mentioned:
        return Mentioned(sorted(self.items(), key=lambda t: len(t[0]), reverse=True))

    def __str__(self):
        return f"Mentioned({str(dict(self))})"

    def __repr__(self):
        return f"Mentioned({repr(dict(self))})"


def assign_name_from_content(obj: Dict) -> str:
    """
    Use the content to assign a name to any :class:`.Fact` that lacks one.

    :param obj:
        object loaded from JSON to make a :class:`.Factor` or :class:`.Holding`

    :returns:
        a new name
    """

    if obj.get("context_factors"):
        content_for_name = obj["predicate"]["content"]
        for context_factor in obj["context_factors"]:
            content_for_name = content_for_name.replace("{}", context_factor, 1)
    else:
        content_for_name = obj["predicate"]["content"]
    false_modifier = "false " if obj["predicate"].get("truth") is False else ""
    return f"{false_modifier}{content_for_name}".replace("{", "").replace("}", "")


def assign_name_for_enactment(obj: Dict) -> str:
    """
    Return an appropriate name for an :class:`.Enactment`

    :param obj: an unloaded :class:`.Enactment`

    :returns: a name for the Enactment
    """
    name = obj["source"]
    if obj.get("exact"):
        name += obj["exact"]
    elif obj.get("prefix") or obj.get("suffix"):
        name += f' {obj.get("prefix")} {obj.get("suffix")}'.strip()
    return name


def assign_name_for_evidence(obj: Dict) -> str:
    """
    Return an appropriate name for an :class:`.Enactment`

    :param obj: an unloaded :class:`.Enactment`

    :returns: a name for the Enactment
    """
    name = f"evidence"
    if obj.get("exhibit"):
        name += f' of {obj["exhibit"]}'
    if obj.get("to_effect"):
        name += f' to the effect that {obj["to_effect"]}'
    return name


def assign_name_for_pleading(obj: Dict) -> str:
    """
    Return an appropriate name for an :class:`.Enactment`

    :param obj: an unloaded :class:`.Enactment`

    :returns: a name for the Enactment
    """
    name = f"pleading"
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
    elif obj.get("source"):
        name = assign_name_for_enactment(obj)
    elif (
        obj.get("exhibit")
        or (obj.get("type") and obj.get("type").lower()) == "evidence"
    ):
        name = assign_name_for_evidence(obj)
    elif obj.get("type") and obj.get("type").lower() == "pleading":
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

    :returns: the same :class:`.Factor` with at name field added
    """
    if not obj.get("name"):
        new_name = create_name_for_factor(obj)
        if new_name:
            obj["name"] = new_name
    return obj


def collect_mentioned(
    obj: Dict,
    mentioned: Optional[Mentioned] = None,
    keys_to_ignore: Sequence[str] = ("predicate", "anchors"),
) -> Mentioned:
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
        if obj.get("predicate", {}).get("content"):
            mentioned = mentioned.sorted_by_length()
            for name in mentioned.keys():
                if (
                    name in obj["predicate"]["content"]
                    and name != obj["predicate"]["content"]
                ):
                    (
                        obj["predicate"]["content"],
                        obj["context_factors"],
                    ) = text_expansion.add_found_context(
                        content=obj["predicate"]["content"],
                        context_factors=obj["context_factors"],
                        factor=mentioned.get_by_name(name),
                    )
        for key, value in obj.items():
            if key not in keys_to_ignore:
                if isinstance(value, (Dict, List)):
                    new_value, new_mentioned = collect_mentioned(value, mentioned)
                    mentioned.update(new_mentioned)
                    obj[key] = new_value
        obj = ensure_factor_has_name(obj)
        if obj.get("name"):
            if obj["name"] in mentioned:
                if obj.get("anchors"):
                    for anchor in obj["anchors"]:
                        mentioned[obj["name"]]["anchors"].append(anchor)
            else:
                mentioned.insert_by_name(obj)
            obj = obj["name"]
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
