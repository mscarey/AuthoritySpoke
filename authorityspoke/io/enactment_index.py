"""
Functions for indexing Enactments in unloaded Holding data.

The index is used for expanding name references to full objects.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from legislice.enactments import RawEnactment
from authorityspoke.facts import RawPredicate, RawFactor
from authorityspoke.io.name_index import (
    Mentioned,
    update_name_index_with_factor,
    update_name_index_from_fact_content,
    ensure_factor_has_name,
    create_name_for_enactment,
)


def ensure_enactment_has_name(obj: RawEnactment) -> RawEnactment:
    """Create "name" field for unloaded Enactment data, if needed."""
    if not obj.get("name"):
        new_name = create_name_for_enactment(obj)
        if new_name:
            obj["name"] = new_name
    return obj


def collect_enactments(
    obj: Union[RawFactor, List[Union[RawFactor, str]]],
    mentioned: Optional[Mentioned] = None,
    keys_to_ignore: Sequence[str] = (
        "predicate",
        "anchors",
        "children",
        "inputs",
        "despite",
        "outputs",
        "selection",
    ),
) -> Tuple[RawFactor, Mentioned]:
    """
    Make a dict of all nested objects labeled by name, creating names if needed.

    To be used during loading to expand name references to full objects.
    """
    mentioned = mentioned or Mentioned()
    if isinstance(obj, List):
        new_list = []
        for item in obj:
            new_item, new_mentioned = collect_enactments(
                item, mentioned, keys_to_ignore
            )
            mentioned.update(new_mentioned)
            new_list.append(new_item)
        obj = new_list
    if isinstance(obj, Dict):
        obj, mentioned = update_name_index_from_fact_content(obj, mentioned)
        new_dict = {}
        for key, value in obj.items():
            if key not in keys_to_ignore and isinstance(value, (Dict, List)):
                new_value, new_mentioned = collect_enactments(
                    value, mentioned, keys_to_ignore
                )
                mentioned.update(new_mentioned)
                new_dict[key] = new_value
            else:
                new_dict[key] = value

        new_dict = ensure_factor_has_name(new_dict)

        if new_dict.get("enactment") or (new_dict.get("name") in mentioned.keys()):
            new_dict = ensure_enactment_has_name(new_dict)
            new_dict, mentioned = update_name_index_with_factor(new_dict, mentioned)
        obj = new_dict

    return obj, mentioned
