"""
Functions for indexing Enactments in unloaded Holding data.

The index is used for expanding name references to full objects.
"""

from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from legislice.enactments import RawEnactment
from authorityspoke.facts import RawPredicate, RawFactor
from authorityspoke.io.name_index import Mentioned


class EnactmentIndex(Mentioned):
    """Index of cross-referenced objects, keyed to phrases that reference them."""


def create_name_for_enactment(obj: RawEnactment) -> str:
    """Create unique name for unloaded Enactment data, for indexing."""
    if "node" not in obj.keys():
        return create_name_for_enactment(obj["enactment"])
    name: str = obj["node"]
    if obj.get("start_date"):
        name += f'@{obj["start_date"]}'

    for field_name in ["start", "end", "prefix", "exact", "suffix"]:
        if obj.get(field_name):
            name += f':{field_name}="{obj[field_name]}"'
    return name


def ensure_enactment_has_name(obj: RawEnactment) -> RawEnactment:
    """Create "name" field for unloaded Enactment data, if needed."""
    if not obj.get("name"):
        new_name = create_name_for_enactment(obj)
        if new_name:
            obj["name"] = new_name
    return obj


def collect_enactments(
    obj: Union[RawFactor, List[Union[RawFactor, str]]],
    mentioned: Optional[EnactmentIndex] = None,
    keys_to_ignore: Sequence[str] = ("predicate", "anchors", "children"),
) -> Tuple[RawFactor, EnactmentIndex]:
    """
    Make a dict of all nested objects labeled by name, creating names if needed.

    To be used during loading to expand name references to full objects.
    """
    mentioned = mentioned or EnactmentIndex()
    if isinstance(obj, List):
        new_list = []
        for item in obj:
            new_item, new_mentioned = collect_enactments(item, mentioned)
            mentioned.update(new_mentioned)
            new_list.append(new_item)
        obj = new_list
    if isinstance(obj, Dict):
        new_dict = {}
        for key, value in obj.items():
            if key not in keys_to_ignore and isinstance(value, (Dict, List)):
                new_value, new_mentioned = collect_enactments(value, mentioned)
                mentioned.update(new_mentioned)
                new_dict[key] = new_value
            else:
                new_dict[key] = value

        if new_dict.get("enactment") or (new_dict.get("name") in mentioned.keys()):
            new_dict = ensure_enactment_has_name(new_dict)
            new_dict = mentioned.update_anchors_or_insert(new_dict)
        obj = new_dict
    return obj, mentioned
