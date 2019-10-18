from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Tuple, Union

from authorityspoke.opinions import TextLinkDict
from authorityspoke.selectors import TextQuoteSelector

from authorityspoke.io import schemas


def read_selector(record: Union[str, Dict[str, str]]) -> TextQuoteSelector:
    """
    Create new selector from JSON user input.

    :param record:
        a string or dict representing a text passage

    :returns: a new :class:`TextQuoteSelector`
    """
    selector_schema = schemas.SelectorSchema(many=False)
    return selector_schema.load(record)


def read_selectors(
    record: Iterable[Union[str, Dict[str, str]]]
) -> List[TextQuoteSelector]:
    r"""
    Create list of :class:`.TextQuoteSelector`\s from JSON user input.

    If the input is a :class:`str`, tries to break up the string
    into :attr:`~TextQuoteSelector.prefix`, :attr:`~TextQuoteSelector.exact`,
    and :attr:`~TextQuoteSelector.suffix`, by splitting on the pipe characters.

    :param record:
        a string or dict representing a text passage, or list of
        strings and dicts.

    :returns: a list of :class:`TextQuoteSelector`\s
    """
    selector_schema = schemas.SelectorSchema(many=True)
    return selector_schema.load(record)


def collect_anchors(obj: Dict) -> List[TextQuoteSelector]:
    anchors = obj.get("anchors") or []
    return read_selectors(anchors)


def collect_anchors_recursively(obj: Union[Dict, List]) -> TextLinkDict:
    r"""
    Move anchors fields to a dict linking object names to lists of anchors.

    To be used during loading of :class:`.Holding`\s.
    Keys are :class:`.Factor`\s, :class:`.Enactment`\s, or :class:`.Holding`\s,
    and values are lists of the :class:`.Opinion` passages that reference them.

    """
    anchors: TextLinkDict = defaultdict(list)
    if isinstance(obj, List):
        for item in obj:
            for k, v in collect_anchors_recursively(item).items():
                anchors[k] += v
    if isinstance(obj, Dict):
        if obj.get("name"):
            for selector in collect_anchors(obj):
                anchors[obj["name"]].append(selector)
        for key, value in obj.items():
            if key != "anchors" and isinstance(value, (Dict, List)):
                for k, v in collect_anchors_recursively(value).items():
                    anchors[k] += v
    return anchors


def index_anchors(
    record: Dict, many: bool = False
) -> Tuple[TextLinkDict, List[List[TextQuoteSelector]]]:
    """
    Make indexes of Holding and Factor text anchors for a list of Holdings.
    """

    factor_anchors = collect_anchors_recursively(record)
    if many:
        holding_anchors = [collect_anchors(holding) for holding in record]
    else:
        holding_anchors = [collect_anchors(record)]
    return factor_anchors, holding_anchors
