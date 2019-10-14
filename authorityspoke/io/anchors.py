from collections import defaultdict
from typing import Dict, List, Optional

from authorityspoke.opinions import TextLinkDict


def collect_anchors(obj: Dict, anchors: Optional[TextLinkDict] = None) -> TextLinkDict:
    anchors: TextLinkDict = anchors or defaultdict(list)
    if obj.get("anchors") and obj.get("name"):
        for selector in obj["anchors"]:
            anchors[obj["name"]].append(selector)

    return anchors


def collect_anchors_recursively(
    obj: Dict, anchors: Optional[TextLinkDict] = None
) -> TextLinkDict:
    r"""
    Move anchors fields to a dict linking object names to lists of anchors.

    To be used during loading of :class:`.Holding`\s.
    Keys are :class:`.Factor`\s, :class:`.Enactment`\s, or :class:`.Holding`\s,
    and values are lists of the :class:`.Opinion` passages that reference them.

    """

    if isinstance(obj, List):
        for item in obj:
            anchors = collect_anchors_recursively(item, anchors=anchors)
    if isinstance(obj, Dict):
        anchors = collect_anchors(obj, anchors)
        for value in obj.values():
            if isinstance(value, (Dict, List)):
                anchors = collect_anchors_recursively(value, anchors=anchors)
    return anchors
