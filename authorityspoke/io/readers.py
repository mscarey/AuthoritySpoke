"""
Converting simple structured data from XML or JSON into authorityspoke objects.

These functions will usually be called by functions from the io.loaders module
after they import some data from a file.
"""
from typing import Any, NamedTuple
from typing import Dict, List, Optional, Tuple, Sequence, Union


from anchorpoint.textselectors import TextQuoteSelector
from legislice.download import Client
from legislice.types import RawEnactment
from nettlesome.entities import Entity

from authorityspoke.decisions import Decision, DecisionReading, RawDecision
from authorityspoke.facts import Fact, Exhibit, Evidence, Allegation, Pleading
from authorityspoke.holdings import Holding, RawHolding
from authorityspoke.opinions import (
    AnchoredHoldings,
    EnactmentWithAnchors,
    TermWithAnchors,
    HoldingWithAnchors,
)
from authorityspoke.facts import RawFactor
from authorityspoke.io.name_index import index_names, Mentioned, collect_enactments
from authorityspoke.io.text_expansion import expand_shorthand

RawSelector = Union[str, Dict[str, str]]


FACTOR_SUBCLASSES = {
    class_obj.__name__: class_obj
    for class_obj in (Allegation, Entity, Exhibit, Evidence, Fact, Pleading)
}


class HoldingsIndexed(NamedTuple):
    """Lists :class:`.Holding` objects with corresponding text selectors."""

    holdings: List[Holding]
    mentioned: Mentioned
    holding_anchors: List[List[TextQuoteSelector]]


def collect_anchors_from_index(object_index, field_name: str):
    """Get text anchors out of an index of terms or enactments."""
    result = []
    for key, value in object_index.items():
        if value.get("anchors"):
            anchored_object: Dict[str, Any] = {}
            anchors = value.pop("anchors")
            if isinstance(anchors, List):
                anchors = [anchor for anchor in anchors if anchor != "|"]
            anchored_object["anchors"] = anchors
            anchored_object[field_name] = value
            result.append(anchored_object)
    return result, object_index


def read_holdings_with_anchors(
    record: Dict[str, Union[List[RawHolding], List[RawSelector]]],
    client: Optional[Client] = None,
) -> AnchoredHoldings:
    r"""
    Load a list of Holdings from JSON, with text links.

    :param record:
        a list of dicts representing holdings, in the JSON input format

    :param client:
        Legislice client for downloading missing fields from `record`

    :returns:
        a namedtuple listing :class:`.Holding` objects with
        a list matching :class:`.Holding`\s to selectors and
        an index matching :class:`.Factor`\s to selectors.
    """

    (
        holdings,
        enactment_anchors,
        factor_anchors,
        holding_anchors,
    ) = extract_anchors_from_holding_record(record, client)
    holdings_with_anchors = []
    for i, holding in enumerate(holdings):
        new = HoldingWithAnchors(holding=holding, anchors=holding_anchors[i])
        holdings_with_anchors.append(new)
    return AnchoredHoldings(
        holdings=holdings_with_anchors,
        named_anchors=factor_anchors,
        enactment_anchors=enactment_anchors,
    )


def expand_factor(
    record: Union[str, RawFactor], factor_index: Mentioned
) -> Union[str, RawFactor]:
    """Expand fields of Factor from index of mentioned factors."""
    to_expand = [
        "statement",
        "statement_attribution",
        "fact",
        "offered_by",
        "exhibit",
        "to_effect",
        "filer",
        "pleading",
    ]
    expanded = (
        factor_index.get_if_present(record) if isinstance(record, str) else record
    )
    if not isinstance(expanded, Dict):
        return expanded
    if "terms" in expanded:
        expanded["terms"] = expand_names(expanded["terms"], factor_index)
    for field in to_expand:
        if field in expanded:
            expanded[field] = expand_factor(expanded[field], factor_index)
    return expanded


def expand_names(
    record: List[Union[str, RawFactor]], factor_index: Mentioned
) -> List[RawFactor]:
    r"""Expand a list of names into a list of factors."""
    if isinstance(record, str):
        record = [record]
    if isinstance(record, bool):
        return record

    result = []

    for name in record:

        result.append(expand_factor(name, factor_index=factor_index))

    return result


def expand_enactments(
    record: List[Union[str, RawEnactment]], enactment_index: Mentioned
) -> List[RawEnactment]:
    r"""
    Expand a list of enactments into a list of dicts.

    :param record:
        a list of enactments, either as strings or dicts

    :param enactment_index:
        a dict of names to enactments

    :returns:
        a list of dicts representing enactments
    """
    return [enactment_index.get_if_present(name) for name in record]


def walk_tree_and_expand(
    obj: Union[Dict, List], mentioned: Mentioned, ignore: Sequence[str] = ()
) -> Union[Dict, List]:
    """
    Traverse tree of dicts and lists, and modify each node.

    :param obj: the object to traverse

    :param func:
        the function to call on each dict node, returning a dict

    :param ignore: the names of keys that should not be explored

    :returns: a version of the tree with every node modified by `func`
    """
    if isinstance(obj, str):
        obj = mentioned.get_if_present(obj)
    if isinstance(obj, List):
        obj = [mentioned.get_if_present(item) for item in obj]
        return [walk_tree_and_expand(item, mentioned, ignore) for item in obj]
    if isinstance(obj, Dict):

        obj_dict: Dict = {}
        for key, value in obj.items():
            if key not in ignore:
                obj_dict[key] = mentioned.get_if_present(value)
            else:
                obj_dict[key] = value

        for key, value in obj_dict.items():
            if isinstance(value, (Dict, List)) and key not in ignore:
                obj_dict[key] = walk_tree_and_expand(value, mentioned, ignore)

        return obj_dict

    return obj


def expand_holding(
    record: RawHolding, factor_index: Mentioned, enactment_index: Mentioned
) -> RawHolding:
    """Expand one holding from index of expanded terms and enactments."""
    new_index = Mentioned({**factor_index, **enactment_index})
    return walk_tree_and_expand(
        record,
        mentioned=new_index,
        ignore=["predicate", "enactment", "selection", "name"],
    )


def expand_holdings(
    record: List[Union[str, RawHolding]],
    factor_index: Mentioned,
    enactment_index: Mentioned,
) -> List[RawHolding]:
    """Expand holdings from index of expanded terms and enactments."""
    if isinstance(record, dict):
        record = [record]
    holdings = [factor_index.get_if_present(holding) for holding in record]
    holdings = [
        expand_holding(
            holding, factor_index=factor_index, enactment_index=enactment_index
        )
        for holding in holdings
    ]
    return holdings


def extract_anchors_from_holding_record(
    record: List[RawHolding], client: Optional[Client] = None
) -> Tuple[
    List[Holding],
    List[EnactmentWithAnchors],
    List[TermWithAnchors],
    List[Dict[str, str]],
]:
    r"""
    Load a list of Holdings from JSON, with text links.

    :param record:
        a list of dicts representing holdings, in the JSON input format

    :param client:
        Legislice client for downloading missing fields from `record`

    :returns:
        a tuple of four objects containing holdings, terms, enactments,
        and anchors.
    """
    record_post_enactments, enactment_index = collect_enactments(record)
    if client:
        enactment_index_post_client = client.update_entries_in_enactment_index(
            enactment_index
        )
    else:
        enactment_index_post_client = enactment_index
    enactment_anchors, enactment_index_post_anchors = collect_anchors_from_index(
        enactment_index_post_client, "passage"
    )

    enactment_result = []
    for anchor in enactment_anchors:
        anchor["passage"] = enactment_index_post_anchors.get_if_present(
            anchor["passage"]
        )
        enactment_result.append(EnactmentWithAnchors(**anchor))

    record_post_terms, factor_index = index_names(record_post_enactments)
    factor_anchors, factor_index_post_anchors = collect_anchors_from_index(
        factor_index, "term"
    )

    factor_result = []
    for anchor in factor_anchors:
        anchor["term"] = expand_holding(
            anchor["term"],
            factor_index=factor_index_post_anchors,
            enactment_index=enactment_index_post_anchors,
        )
        factor_result.append(TermWithAnchors(**anchor))

    factor_anchors = [TermWithAnchors(**anchor) for anchor in factor_anchors]

    expanded = expand_holdings(
        record_post_terms,
        factor_index=factor_index_post_anchors,
        enactment_index=enactment_index_post_anchors,
    )
    holding_anchors = [holding.pop("anchors", None) for holding in expanded]

    result = []
    for holding in expanded:
        result.append(Holding(**holding))
    return result, enactment_result, factor_result, holding_anchors


def read_holdings(
    record: List[RawHolding], client: Optional[Client] = None
) -> List[Holding]:
    r"""
    Load a list of :class:`Holdings`\s from JSON.

    :param record:
        a list of dicts representing holdings, in the JSON input format

    :parame regime:
        A collection of :class:`.Jurisdiction`\s and the :class:`.Code`\s
        that have been enacted in each. Used for constructing
        :class:`.Enactment`\s referenced by :class:`.Holding`\s.

    :returns:
        a list of :class:`.Holding` objects
    """
    (
        holdings,
        enactment_anchors,
        factor_anchors,
        holding_anchors,
    ) = extract_anchors_from_holding_record(record, client)

    return holdings


def read_decision(decision: Union[RawDecision, Decision]) -> DecisionReading:
    r"""
    Create and return a :class:`~authorityspoke.decisions.Decision` from a dict API response.

    Relies on the JSON format from the `Caselaw Access Project
    API <https://api.case.law/v1/cases/>`_.

    :param decision_dict:
        A dict created from a Caselaw Access Project API response.
    """
    if not isinstance(decision, Decision):
        decision = Decision(**decision)
    return DecisionReading(decision=decision)
