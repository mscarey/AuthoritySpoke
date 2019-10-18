"""Functions for indexing named objects in JSON to be imported."""
from __future__ import annotations

from copy import deepcopy
from collections import OrderedDict

from typing import Dict, List, Optional, Tuple

from marshmallow import ValidationError

from authorityspoke.io.nesting import nest_fields


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
        return deepcopy(value)

    def sorted_by_length(self) -> Mentioned:
        return Mentioned(sorted(self.items(), key=lambda t: len(t[0]), reverse=True))

    def __str__(self):
        return f"Mentioned({str(dict(self))})"

    def __repr__(self):
        return f"Mentioned({repr(dict(self))})"


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


def index_names(obj: Dict) -> Mentioned:
    """
    Call all functions to prepare "mentioned" index.

    The names are sorted by length so that if one mentioned Factor's name
    is a substring of another, the longest available name is expanded.

    :returns:
        a modified version of the dict to load, plus a dict of names
        and the objects to expand them with.
    """
    mentioned = collect_mentioned(obj)
    sorted_mentioned = mentioned.sorted_by_length()
    return sorted_mentioned
