from collections import defaultdict
from typing import Dict, List, Optional

from authorityspoke.opinions import TextLinkDict


def collect_anchors(obj: Dict) -> List[Dict]:
    return obj.get("anchors") or []


def collect_anchors_recursively(
    obj: Dict, anchors: Optional[TextLinkDict] = None
) -> TextLinkDict:
    r"""
    Move anchors fields to a dict linking object names to lists of anchors.

    To be used during loading of :class:`.Holding`\s.
    Keys are :class:`.Factor`\s, :class:`.Enactment`\s, or :class:`.Holding`\s,
    and values are lists of the :class:`.Opinion` passages that reference them.

    """
    anchors: TextLinkDict = anchors or defaultdict(list)
    if isinstance(obj, List):
        for item in obj:
            incoming = collect_anchors_recursively(item)
            for k, v in incoming.items():
                for selector in v:
                    anchors[k].append(selector)
    if isinstance(obj, Dict):
        if obj.get("name"):
            for selector in collect_anchors(obj):
                anchors[obj["name"]].append(selector)
        for key, value in obj.items():
            if key != "anchors" and isinstance(value, (Dict, List)):
                incoming = collect_anchors_recursively(value)
                for k, v in incoming.items():
                    for selector in v:
                        anchors[k].append(selector)
    return anchors
