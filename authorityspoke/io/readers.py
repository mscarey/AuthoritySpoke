"""
Converting simple structured data from XML or JSON into authorityspoke objects.

These functions will usually be called by functions from the io.loaders module
after they import some data from a file.
"""
from copy import deepcopy
from typing import Any, NamedTuple

from typing import Dict, List, Optional, Tuple, Type, Union

from anchorpoint.textselectors import TextQuoteSelector
from legislice.download import Client
from nettlesome.entities import Entity
from nettlesome.factors import Factor

from authorityspoke.decisions import Decision, DecisionReading
from authorityspoke.evidence import Exhibit, Evidence
from authorityspoke.facts import Fact
from authorityspoke.holdings import Holding
from authorityspoke.io import schemas_yaml
from authorityspoke.opinions import AnchoredHoldings
from authorityspoke.pleadings import Allegation, Pleading
from authorityspoke.procedures import Procedure
from authorityspoke.rules import Rule
from authorityspoke.io import schemas_json
from authorityspoke.io.schemas_yaml import (
    RawEnactment,
    RawHolding,
    RawRule,
    RawPredicate,
    RawFactor,
    RawDecision,
    RawSelector,
)
from authorityspoke.io.name_index import index_names, Mentioned
from authorityspoke.io.enactment_index import collect_enactments

FACTOR_SUBCLASSES = {
    class_obj.__name__: class_obj
    for class_obj in (Allegation, Entity, Exhibit, Evidence, Fact, Pleading)
}


def read_fact(record: RawFactor) -> Fact:
    r"""
    Construct a :class:`Fact` after loading a dict from YAML.

    :param record:
        parameter values to pass to :class:`authorityspoke.schemas_yaml.FactSchema`\.

    :returns:
        a :class:`Fact`, with optional mentioned factors
    """
    record, mentioned = index_names(record)
    schema = schemas_yaml.FactSchema()
    schema.context["mentioned"] = mentioned
    return schema.load(record)


def read_factor(record: RawFactor, client: Optional[Client] = None, **kwargs) -> Factor:
    r"""
    Turn fields from YAML into a :class:`Factor` object.

    :param record:
        parameter values to pass to schema

    :param client:
        to look up any :class:`.Enactment` references

    """
    schema = schemas_yaml.FactorSchema(many=False)
    record, enactment_index = collect_enactments(record)
    if client:
        enactment_index = client.update_entries_in_enactment_index(enactment_index)
    schema.context["enactment_index"] = enactment_index
    record, schema.context["mentioned"] = index_names(record)

    return schema.load(record)


def read_factors(
    record: List[RawFactor], client: Optional[Client] = None, **kwargs
) -> Factor:
    r"""
    Turn fields from YAML into a :class:`Factor` object.

    :param record:
        parameter values to pass to schema

    :parame regime:
        to look up any :class:`.Enactment` references
    """
    schema = schemas_yaml.FactorSchema(many=True)
    record, enactment_index = collect_enactments(record)
    if client:
        enactment_index = client.update_entries_in_enactment_index(enactment_index)
    schema.context["enactment_index"] = enactment_index
    record, schema.context["mentioned"] = index_names(record)
    return schema.load(record)


def read_procedure(
    record: Dict, client: Optional[Client] = None, many=False
) -> Procedure:
    r"""
    Turn fields from YAML into a :class:`Procedure` object.

    :param record:
        parameter values to pass to schema

    :param many:
        whether to use the "many" form of the Marshmallow
        schema (whether there are multiple Procedures)

    :parame regime:
        to look up any :class:`.Enactment` references
    """
    schema = schemas_yaml.ProcedureSchema(many=many)
    record, enactment_index = collect_enactments(record)
    if client:
        enactment_index = client.update_entries_in_enactment_index(enactment_index)
    schema.context["enactment_index"] = enactment_index
    record, schema.context["mentioned"] = index_names(record)
    return schema.load(record)


def read_holding(record: RawHolding, client: Optional[Client] = None) -> Holding:
    r"""
    Create new :class:`Holding` object from simple datatypes from JSON input.

    Will yield multiple items if ``exclusive: True`` is present in ``record``.

    :param record:
        dict of values for constructing :class:`.Holding`

    :param client:
        Legislice client for downloading missing fields from `record`

    :param many:
        if True, record represents a list of :class:`Holding`\s rather than
        just one.

    :returns:
        New :class:`.Holding`, and an updated dictionary with mentioned
        :class:`.Factor`\s as keys and their :class:`.TextQuoteSelector`\s
        as values.
    """

    schema = schemas_yaml.HoldingSchema(many=False)

    record, enactment_index = collect_enactments(record)
    if client:
        enactment_index = client.update_entries_in_enactment_index(enactment_index)
    anchors, enactment_index = collect_anchors_from_index(enactment_index, "enactment")
    schema.context["enactment_index"] = enactment_index

    record, factor_index = index_names(record)
    anchors, factor_index = collect_anchors_from_index(factor_index, "name")
    schema.context["mentioned"] = factor_index

    return schema.load(deepcopy(record))


class HoldingsIndexed(NamedTuple):
    """Lists :class:`.Holding` objects with corresponding text selectors."""

    holdings: List[Holding]
    mentioned: Mentioned
    holding_anchors: List[List[TextQuoteSelector]]


def collect_anchors_from_index(object_index, field_name: str):
    anchors = []
    for key, value in object_index.items():
        if value.get("anchors"):
            anchored_object: Dict[str, Any] = {}
            anchored_object["anchors"] = value.pop("anchors")
            anchored_object[field_name] = value
            anchors.append(anchored_object)
    return anchors, object_index


def read_holdings_with_anchors(
    record: Dict[str, Union[List[RawHolding], List[RawSelector]]],
    client: Optional[Client] = None,
    many: bool = True,
) -> AnchoredHoldings:
    r"""
    Load a list of Holdings from JSON, with text links.

    :param record:
        a list of dicts representing holdings, in the JSON input format

    :param client:
        Legislice client for downloading missing fields from `record`

    :param many:
        a bool indicating whether to use the "many" form of the Marshmallow
        schema (whether there are multiple Holdings)

    :returns:
        a namedtuple listing :class:`.Holding` objects with
        a list matching :class:`.Holding`\s to selectors and
        an index matching :class:`.Factor`\s to selectors.
    """
    schema = schemas_yaml.AnchoredHoldingsSchema()

    record, enactment_index = collect_enactments(record)
    if client:
        enactment_index = client.update_entries_in_enactment_index(enactment_index)

    # move anchors out of enactments
    anchors, enactment_index = collect_anchors_from_index(enactment_index, "enactment")
    if not record.get("enactment_anchors"):
        record["enactment_anchors"] = []
    record["enactment_anchors"] = record["enactment_anchors"] + anchors
    schema.context["enactment_index"] = enactment_index

    record["holdings"], factor_index = index_names(record["holdings"])

    # move anchors out of factors
    anchors, factor_index = collect_anchors_from_index(factor_index, "name")
    if not record.get("factor_anchors"):
        record["factor_anchors"] = []
    record["factor_anchors"] = record["factor_anchors"] + anchors
    schema.context["mentioned"] = factor_index

    holdings, holding_anchors, named_anchors, enactment_anchors = schema.load(
        deepcopy(record)
    )
    return AnchoredHoldings(holdings, holding_anchors, named_anchors, enactment_anchors)


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
    schema = schemas_yaml.HoldingSchema(many=True)

    record, enactment_index = collect_enactments(record)
    if client:
        enactment_index = client.update_entries_in_enactment_index(enactment_index)
    anchors, enactment_index = collect_anchors_from_index(enactment_index, "enactment")
    schema.context["enactment_index"] = enactment_index

    record, factor_index = index_names(record)
    anchors, factor_index = collect_anchors_from_index(factor_index, "name")
    schema.context["mentioned"] = factor_index

    return schema.load(deepcopy(record))


def read_decision(decision: Union[RawDecision, Decision]) -> DecisionReading:
    r"""
    Create and return a :class:`~authorityspoke.decisions.DecisionReading` from a dict API response.

    Relies on the JSON format from the `Caselaw Access Project
    API <https://api.case.law/v1/cases/>`_.

    :param decision_dict:
        A dict created from a Caselaw Access Project API response.
    """
    if not isinstance(decision, Decision):
        decision = Decision(**decision)
    return DecisionReading(decision)


def read_rules_with_index(
    record: List[RawRule], client: Optional[Client] = None, many: bool = True
) -> Tuple[List[Rule], Mentioned]:
    r"""Make :class:`Rule` and "mentioned" index from dict of fields and :class:`.Regime`\."""

    schema = schemas_yaml.RuleSchema(many=many)
    record, enactment_index = collect_enactments(record)

    if client:
        enactment_index = client.update_entries_in_enactment_index(enactment_index)
    record, mentioned = index_names(record)
    schema.context["enactment_index"] = enactment_index

    schema.context["mentioned"] = mentioned

    rules = schema.load(deepcopy(record))
    return rules, mentioned


def read_rule(record: Dict, client: Optional[Client] = None) -> Rule:
    r"""
    Make :class:`Rule` from a :class:`dict` of fields and a :class:`.Regime`\.

    :param record:

    :param client:
        Legislice client for downloading missing fields from `record`

    :returns:
        iterator yielding :class:`Rule`\s with the items
        from ``mentioned_entities`` as ``terms``
    """
    schema = schemas_yaml.RuleSchema()
    record, enactment_index = collect_enactments(record)
    record, schema.context["mentioned"] = index_names(record)

    if client:
        enactment_index = client.update_entries_in_enactment_index(enactment_index)
    schema.context["enactment_index"] = enactment_index
    return schema.load(record)


def read_rules(record: List[Dict], client: Optional[Client] = None) -> List[Rule]:
    r"""
    Make :class:`Rule`\s from a list of fields and a :class:`.Regime`\.

    :param record:

    :param client:
        Legislice client for downloading missing fields from `record`

    :returns:
        iterator yielding :class:`Rule`\s with the items
        from ``mentioned_entities`` as ``terms``
    """

    schema = schemas_yaml.RuleSchema(many=True)
    record, enactment_index = collect_enactments(record)
    record, schema.context["mentioned"] = index_names(record)

    if client:
        enactment_index = client.update_entries_in_enactment_index(enactment_index)
    schema.context["enactment_index"] = enactment_index
    return schema.load(record)
