"""
Converting simple structured data from XML or JSON into authorityspoke objects.

These functions will usually be called by functions from the io.loaders module
after they import some data from a file.
"""
from copy import deepcopy
from typing import NamedTuple

from bs4 import BeautifulSoup

from typing import Any, Dict, List, Iterable, Iterator
from typing import Optional, Sequence, Tuple, Type, Union

from anchorpoint.textselectors import TextQuoteSelector

from authorityspoke.decisions import Decision
from authorityspoke.codes import Code, USCCode, USLMCode, USConstCode, CalCode, CFRCode
from authorityspoke.enactments import Enactment
from authorityspoke.entities import Entity
from authorityspoke.evidence import Exhibit, Evidence
from authorityspoke.factors import Factor
from authorityspoke.facts import Fact
from authorityspoke.holdings import Holding
from authorityspoke.jurisdictions import Regime
from authorityspoke.opinions import AnchoredHoldings
from authorityspoke.pleadings import Allegation, Pleading
from authorityspoke.predicates import Predicate
from authorityspoke.procedures import Procedure
from authorityspoke.rules import Rule

from authorityspoke.io import anchors, schemas
from authorityspoke.io.schemas import (
    RawEnactment,
    RawHolding,
    RawRule,
    RawPredicate,
    RawFactor,
    RawDecision,
)
from authorityspoke.io.name_index import index_names, Mentioned

FACTOR_SUBCLASSES = {
    class_obj.__name__: class_obj
    for class_obj in (Allegation, Entity, Exhibit, Evidence, Fact, Pleading)
}


def get_code_uri(xml, title: str) -> str:
    """
    Build a URI for the ``Code`` based on its XML metadata.

    .. note::
        This handles California state statutes only with a
        mockup, which can only refer to the Penal and Evidence
        Codes.

    :returns:
        The `United States Legislative Markup (USLM)
        <https://github.com/usgpo/uslm>`_ identifier that
        describes the document as a whole, if available in
        the XML. Otherwise returns a pseudo-USLM identifier.
    """
    main_element = xml.find("main")
    if main_element:
        identifier = main_element.findChild()["identifier"]
        return identifier
    if title == "Constitution of the United States":
        return "/us/const"
    if title.startswith("Title"):
        return xml.find("main").find("title")["identifier"]
    if title.startswith("California"):
        uri = "/us-ca"
        if "Penal" in title:
            return uri + "/pen"
        else:
            return uri + "/evid"
    if title.startswith("Code of Federal Regulations"):
        title_num = title.split()[-1]
        return f"/us/cfr/t{title_num}"
    raise NotImplementedError


def get_code_title(xml) -> str:
    r"""
    Provide "title" identifier for the :class:`Code` XML.

    :returns:
        the contents of an XML ``title`` element that
        describes the ``Code``, if any. Otherwise
        returns a descriptive name that may not exactly
        appear in the XML.
    """
    uslm_title = xml.find("title")
    if uslm_title:
        return uslm_title.text
    cal_title = xml.h3
    if cal_title:
        code_name = cal_title.b.text.split(" - ")[0]
        return f"California {code_name}"
    cfr_title = xml.CFRGRANULE.FDSYS.CFRTITLE
    if cfr_title:
        return f"Code of Federal Regulations Title {cfr_title.text}"
    raise NotImplementedError


def has_uslm_schema(soup: BeautifulSoup) -> bool:
    """
    Determine if the Code XML has the USLM schema.
    """
    return soup.find(xmlns="http://xml.house.gov/schema/uslm/1.0")


def read_code(xml):
    title = get_code_title(xml)
    uri = get_code_uri(xml, title)
    if uri.startswith("/us/const"):
        code_class = USConstCode
    elif uri.startswith("/us/cfr"):
        code_class = CFRCode
    elif uri.startswith("/us/"):
        code_class = USCCode
    elif uri.startswith("/us-ca"):
        code_class = CalCode
    elif has_uslm_schema(xml):
        code_class = USLMCode
    else:
        return Code(xml, title, uri)
    return code_class(xml, title, uri)


def read_enactment(
    record: RawEnactment, code: Optional[Code] = None, regime: Optional[Regime] = None
) -> Enactment:
    r"""
    Create a new :class:`.Enactment` object using imported JSON data.

    The new :class:`.Enactment` can be composed from a :class:`.Code`
    referenced in the ``regime`` parameter.

    :param record:
        :class:`dict` with string fields from JSON for constructing
        new :class:`.Enactment`

    :param code:
        the :class:`.Code` that is the source for this
        :class:`Enactment`

    :param regime:
        the :class:`.Regime` where the :class:`.Code` that is the
        source for this :class:`Enactment` can be found, or where
        it should be added

    :returns:
        a new :class:`Enactment` object, optionally with text links.
    """
    schema = schemas.EnactmentSchema(many=False)
    record, schema.context["mentioned"] = index_names(record)
    schema.context["regime"] = regime
    schema.context["code"] = code
    return schema.load(deepcopy(record))


def read_enactments(
    record: List[RawEnactment],
    code: Optional[Code] = None,
    regime: Optional[Regime] = None,
) -> List[Enactment]:
    r"""
    Create a new :class:`Enactment` object using imported JSON data.

    The new :class:`Enactment` can be composed from a :class:`.Code`
    referenced in the ``regime`` parameter.

    :param record:
        sequence of :class:`dict`\s with string fields from JSON for
        constructing new :class:`.Enactment`\s

    :param code:
        a :class:`.Code` that is the source for every :class:`Enactment`
        to be loaded, if they all come from the same :class:`.Code`

    :param regime:
        the :class:`.Regime` where the :class:`.Code`\s that are the
        source for this :class:`Enactment` can be found, or where
        it should be added

    :returns:
        a list of new :class:`Enactment` objects, optionally with text links.
    """
    schema = schemas.EnactmentSchema(many=True)
    record, schema.context["mentioned"] = index_names(record)
    schema.context["regime"] = regime
    schema.context["code"] = code
    return schema.load(deepcopy(record))


def read_predicate(value: RawPredicate) -> Predicate:
    schema = schemas.PredicateSchema(partial=True)
    return schema.load(value)


def read_fact(record: RawFactor) -> Fact:
    r"""
    Construct a :class:`Fact` after loading a dict from JSON.

    :param record:
        parameter values to pass to :class:`.FactSchema`\.

    :returns:
        a :class:`Fact`, with optional mentioned factors
    """
    record, mentioned = index_names(record)
    schema = schemas.FactSchema()
    schema.context["mentioned"] = mentioned
    return schema.load(record)


def read_factor(record: RawFactor, regime: Optional[Regime] = None, **kwargs) -> Factor:
    r"""
    Turn fields from JSON into a :class:`Factor` object.

    :param record:
        parameter values to pass to schema

    :parame regime:
        to look up any :class:`.Enactment` references

    """
    schema = schemas.FactorSchema(many=False)
    record, schema.context["mentioned"] = index_names(record)
    schema.context["regime"] = regime
    return schema.load(record)


def read_factors(
    record: List[RawFactor], regime: Optional[Regime] = None, **kwargs
) -> Factor:
    r"""
    Turn fields from JSON into a :class:`Factor` object.

    :param record:
        parameter values to pass to schema

    :parame regime:
        to look up any :class:`.Enactment` references

    """
    schema = schemas.FactorSchema(many=True)
    record, schema.context["mentioned"] = index_names(record)
    schema.context["regime"] = regime
    return schema.load(record)


def read_procedure(
    record: Dict, regime: Optional[Regime] = None, many=False
) -> Procedure:
    schema = schemas.ProcedureSchema(many=many)
    record, schema.context["mentioned"] = index_names(record)
    schema.context["regime"] = regime
    return schema.load(record)


def read_holding(record: RawHolding, regime: Optional[Regime] = None) -> Holding:
    r"""
    Create new :class:`Holding` object from simple datatypes from JSON input.

    Will yield multiple items if ``exclusive: True`` is present in ``record``.

    :param record:
        dict of values for constructing :class:`.Holding`

    :param regime:
        Collection of :class:`.Jurisdiction`\s and corresponding
        :class:`.Code`\s for discovering :class:`.Enactment`\s to
        reference in the new :class:`Holding`.

    :param many:
        if True, record represents a list of :class:`Holding`\s rather than
        just one.

    :returns:
        New :class:`.Holding`, and an updated dictionary with mentioned
        :class:`.Factor`\s as keys and their :class:`.TextQuoteSelector`\s
        as values.
    """
    schema = schemas.HoldingSchema(many=False)
    record, schema.context["mentioned"] = index_names(record)
    schema.context["regime"] = regime
    return schema.load(deepcopy(record))


class HoldingsIndexed(NamedTuple):
    holdings: List[Holding]
    mentioned: Mentioned
    holding_anchors: List[List[TextQuoteSelector]]


def read_holdings_with_index(
    record: List[RawHolding], regime: Optional[Regime] = None, many: bool = True
) -> HoldingsIndexed:
    record, mentioned = index_names(record)
    schema = schemas.HoldingSchema(many=many)
    schema.context["regime"] = regime
    schema.context["mentioned"] = mentioned
    anchor_list = anchors.get_holding_anchors(record)
    holdings = schema.load(deepcopy(record))
    return HoldingsIndexed(holdings, mentioned, anchor_list)


def read_holdings_with_anchors(
    record: List[RawHolding], regime: Optional[Regime] = None, many: bool = True
) -> AnchoredHoldings:
    holdings, mentioned, holding_anchors = read_holdings_with_index(
        record=record, regime=regime, many=many
    )
    text_anchors = anchors.get_named_anchors(mentioned)
    return AnchoredHoldings(holdings, holding_anchors, text_anchors)


def read_holdings(
    record: List[RawHolding],
    regime: Optional[Regime] = None,
    code: Optional[Code] = None,
) -> List[Holding]:
    r"""
    Load a list of :class:`Holdings`\s from JSON, with optional text links.

    :param record:
        a list of dicts representing holdings, in the JSON input format

    :parame regime:
        A collection of :class:`.Jurisdiction`\s and the :class:`.Code`\s
        that have been enacted in each. Used for constructing
        :class:`.Enactment`\s referenced by :class:`.Holding`\s.

    :returns:
        a list of :class:`.Holding` objects, optionally with
        an index matching :class:`.Factor`\s to selectors.
    """
    schema = schemas.HoldingSchema(many=True)
    record, schema.context["mentioned"] = index_names(record)
    schema.context["regime"] = regime
    schema.context["code"] = code
    return schema.load(deepcopy(record))


def read_decision(decision_dict: RawDecision) -> Decision:
    r"""
    Create and return one or more :class:`.Opinion` objects from a dict API response.

    Relies on the JSON format from the `Caselaw Access Project
    API <https://api.case.law/v1/cases/>`_.

    This function is a more convenient way to call read_opinions with an entire
    case from the CAP API as a single parameter.

    :param decision_dict:
        A dict created from a Caselaw Access Project API response.
    """
    schema = schemas.DecisionSchema()
    return schema.load(decision_dict)


def read_rules_with_index(
    record: List[RawRule], regime: Optional[Regime] = None, many: bool = True
) -> Tuple[List[Rule], Mentioned]:
    record, mentioned = index_names(record)
    schema = schemas.RuleSchema(many=many)
    schema.context["regime"] = regime
    schema.context["mentioned"] = mentioned
    rules = schema.load(deepcopy(record))
    return rules, mentioned


def read_rule(record: Dict, regime: Optional[Regime] = None) -> Rule:
    r"""
    Make :class:`Rule` from a :class:`dict` of fields and a :class:`.Regime`\.

    :param record:

    :param regime:

    :returns:
        iterator yielding :class:`Rule`\s with the items
        from ``mentioned_entities`` as ``context_factors``
    """
    record, mentioned = index_names(record)
    schema = schemas.RuleSchema()
    schema.context["mentioned"] = mentioned
    schema.context["regime"] = regime
    return schema.load(record)


def read_rules(record: List[Dict], regime: Optional[Regime] = None) -> List[Rule]:
    r"""
    Make :class:`Rule`\s from a list of fields and a :class:`.Regime`\.

    :param record:

    :param regime:

    :returns:
        iterator yielding :class:`Rule`\s with the items
        from ``mentioned_entities`` as ``context_factors``
    """
    record, mentioned = index_names(record)
    schema = schemas.RuleSchema(many=True)
    schema.context["mentioned"] = mentioned
    schema.context["regime"] = regime
    return schema.load(record)
