from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from legislice.enactments import RawEnactment

RawPredicate = Dict[str, Union[str, bool]]
RawFactor = Dict[str, Union[RawPredicate, Sequence[Any], str, bool]]


class EnactmentIndex(OrderedDict):
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
        value = {"name": name}
        value.update(self[name])
        return value

    def __repr__(self):
        return f"EnactmentIndex({repr(dict(self))})"

    def enactment_has_anchor(
        self, enactment_name: str, anchor: Dict[str, Union[str, int]]
    ) -> bool:
        anchors_for_selected_element = self[enactment_name].get("anchors") or []
        return any(
            existing_anchor == anchor
            for existing_anchor in anchors_for_selected_element
        )

    def add_anchor_for_enactment(
        self, enactment_name: str, anchor: Dict[str, Union[str, int]]
    ) -> None:
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
    name: str = obj["node"]
    if obj.get("start_date"):
        name += f'@{obj["start_date"]}'

    for field_name in ["start", "end", "prefix", "exact", "suffix"]:
        if obj.get(field_name):
            name += f':{field_name}="{obj[field_name]}"'
    return name


def ensure_enactment_has_name(obj: RawEnactment) -> RawEnactment:

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

        if new_dict.get("node") or (new_dict.get("name") in mentioned.keys()):
            new_dict = ensure_enactment_has_name(new_dict)
            new_dict = mentioned.index_enactment(new_dict)
        obj = new_dict
    return obj, mentioned