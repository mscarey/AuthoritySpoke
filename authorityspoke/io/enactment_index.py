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

    def enactment_has_anchor(
        self, enactment_name: str, anchor: Dict[str, Union[str, int]]
    ) -> bool:
        """Check if unloaded Enactment data has fields for a text anchor."""
        anchors_for_selected_element = self[enactment_name].get("anchors") or []
        return any(
            existing_anchor == anchor
            for existing_anchor in anchors_for_selected_element
        )

    def add_anchor_for_enactment(
        self, enactment_name: str, anchor: Dict[str, Union[str, int]]
    ) -> None:
        """Add fields for a text anchor to unloaded Enactment data."""
        anchors_for_selected_element = self[enactment_name].get("anchors") or []
        if not self.enactment_has_anchor(enactment_name, anchor):
            anchors_for_selected_element.append(anchor)
        self[enactment_name]["anchors"] = anchors_for_selected_element

    def __add__(self, other: EnactmentIndex) -> EnactmentIndex:
        new_index = deepcopy(self)
        for key in other.keys():
            other_dict = other.get_by_name(key)
            new_index.index_enactment(other_dict)
        return new_index

    def index_enactment(self, obj: RawEnactment) -> Union[str, RawEnactment]:
        r"""
        Update index of mentioned Factors with 'obj', if obj is named.

        If there is already an entry in the mentioned index with the same name
        as obj, the old entry won't be replaced. But if any additional text
        anchors are present in the new obj, the anchors will be added.
        If obj has a name, it will be collapsed to a name reference.

        :param obj:
            data from JSON to be loaded as a :class:`.Enactment`
        """
        if obj.get("name"):
            if obj["name"] in self:
                if obj.get("anchors"):
                    for anchor in obj["anchors"]:
                        self.add_anchor_for_enactment(
                            enactment_name=obj["name"], anchor=anchor
                        )
            else:
                self.insert_by_name(obj)
            obj = obj["name"]
        return obj


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
            new_dict = mentioned.index_enactment(new_dict)
        obj = new_dict
    return obj, mentioned
