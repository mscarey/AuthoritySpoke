"""
Converting simple structured data from XML or JSON into authorityspoke objects.

These functions will usually be called by functions from the io.loaders module
after they import some data from a file.
"""
from copy import deepcopy
import datetime
from functools import partial

from typing import Any, Dict, List, Iterable, Iterator
from typing import Optional, Tuple, Type, Union

from pint import UnitRegistry

from authorityspoke.enactments import Code, Enactment
from authorityspoke.entities import Entity
from authorityspoke.evidence import Exhibit, Evidence
from authorityspoke.factors import Factor
from authorityspoke.facts import Fact
from authorityspoke.holdings import Holding
from authorityspoke.jurisdictions import Regime
from authorityspoke.opinions import Opinion, TextLinkDict
from authorityspoke.pleadings import Allegation, Pleading
from authorityspoke.predicates import Predicate
from authorityspoke.procedures import Procedure
from authorityspoke.rules import Rule

from authorityspoke.io import anchors, schemas
from authorityspoke.io.schemas import RawSelector, RawEnactment, RawHolding
from authorityspoke.io.schemas import RawPredicate, RawFactor
from authorityspoke.io.name_index import index_names


ureg = UnitRegistry()

FACTOR_SUBCLASSES = {
    class_obj.__name__: class_obj
    for class_obj in (Allegation, Entity, Exhibit, Evidence, Fact, Pleading)
}


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
    schema.context["mentioned"] = index_names(record)
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
    schema.context["mentioned"] = index_names(record)
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
    mentioned = index_names(record)
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
    schema.context["mentioned"] = index_names(record)
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
    schema = schemas.FactorSchema(many=False)
    schema.context["mentioned"] = index_names(record)
    schema.context["regime"] = regime
    return schema.load(record)


def read_procedure(
    record: Dict, regime: Optional[Regime] = None, many=False
) -> Procedure:
    schema = schemas.ProcedureSchema(many=many)
    schema.context["mentioned"] = index_names(record)
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
    schema.context["mentioned"] = index_names(record)
    schema.context["regime"] = regime
    return schema.load(deepcopy(record))


def read_holdings(
    record: List[RawHolding], regime: Optional[Regime] = None
) -> List[Holding]:
    r"""
    Load a list of :class:`Holdings`\s from JSON, with optional text links.

    :param record:
        a list of dicts representing holdings, in the JSON input format

    :parame regime:
        A collection of :class:`.Jurisdiction`\s and the :class:`.Code`\s
        that have been enacted in each. Used for constructing
        :class:`.Enactment`\s referenced by :class:`.Holding`\s.

    :param index_anchors:
        whether to also return an index of text links to the created object(s)

    :returns:
        a list of :class:`.Holding` objects, optionally with
        an index matching :class:`.Factor`\s to selectors.
    """
    schema = schemas.HoldingSchema(many=True)
    schema.context["mentioned"] = index_names(record)
    schema.context["regime"] = regime
    return schema.load(deepcopy(record))


def read_case(
    decision_dict: Dict[str, Any], lead_only: bool = True, as_generator: bool = False
) -> Union[Opinion, Iterator[Opinion], List[Opinion]]:
    r"""
    Create and return one or more :class:`.Opinion` objects from a dict API response.

    Relies on the JSON format from the `Caselaw Access Project
    API <https://api.case.law/v1/cases/>`_.

    This function is a more convenient way to call read_opinions with an entire
    case from the CAP API as a single parameter.

    :param decision_dict:
        A dict created from a Caselaw Access Project API response.

    :param lead_only:
        If True, returns a single :class:`.Opinion` object,
        otherwise returns an iterator that yields every
        :class:`.Opinion` in the case.

    :param as_generator:
        if True, returns a generator that
        yields all opinions meeting the query.
    """

    return read_opinions(
        lead_only=lead_only, as_generator=as_generator, **decision_dict
    )


def read_opinions(
    citations: List[Dict[str, str]],
    decision_date: str,
    court: Dict[str, Union[str, int]],
    casebody: Optional[Dict] = None,
    name: str = "",
    name_abbreviation: str = "",
    first_page: str = "",
    last_page: str = "",
    lead_only: bool = True,
    as_generator: bool = False,
    **kwargs,
) -> Union[Opinion, Iterator[Opinion], List[Opinion]]:
    r"""
    Create and return one or more :class:`.Opinion` objects.

    This function uses the model of a judicial decision from
    the `Caselaw Access Project API <https://api.case.law/v1/cases/>`_.
    One of these records may contain multiple :class:`.Opinion`\s.

    Typically one record will contain all the :class:`.Opinion`\s
    from one appeal, but not necessarily from the whole lawsuit. One
    lawsuit may contain multiple appeals or other petitions, and
    if more then one of those generates published :class:`.Opinion`\s,
    the CAP API will divide those :class:`.Opinion`\s into a separate
    record for each appeal.

    The lead opinion is commonly, but not always, the only
    :class:`.Opinion` that creates binding legal authority.
    Usually every :class:`.Rule` posited by the lead :class:`.Opinion` is
    binding, but some may not be, often because parts of the
    :class:`.Opinion` fail to command a majority of the panel
    of judges.

    :param citations:
        Page references that would be used to locate the decision in
        printed volumes. May be the closest things to accepted
        identifiers for a decision.

    :param casebody:
        A large section of the CAP API response containing all the
        text that was printed in the reporter volume. Only available
        if the ``full_case`` flag was used in the API request.

    :param decision_date:
        The day the :class:`.Opinion`\s were issued, in ISO format.

    :param court:
        A dict containing the :class:`.Court` slug, hopefully a unique
        identifier of the court. Also contains the "id", which can be
        resorted to when the slug turns out not to be unique.

    :param name:
        Full name of the lawsuit. Sometimes the same lawsuit may change
        its name as time passes between multiple appeals.

    :param name_abbreviation:
        A shorter name for the lawsuit. Courts may or may not have
        deterministic rules for creating the abbreviation given
        the full name. This may be only one of many possible abbreviations.

    :param first_page:
        The first printed page where any of the :class:`.Opinion`\s for this
        decision can be found. Does not come with an identifier of the reporter,
        but in most cases there is only one official reporter, which is the most
        likely choice.

    :param last_page:
        The last printed page where any of the :class:`.Opinion`\s for this
        decision can be found.

    :param lead_only:
        If ``True``, returns a single :class:`.Opinion` object
        from the first opinion found in the
        ``casebody/data/opinions`` section of the dict, which should
        usually be the lead opinion. If ``False``, returns an iterator that yields
        :class:`.Opinion` objects from every opinion in the case.
    """

    def make_opinion(
        name: str,
        name_abbreviation: str,
        citations: Iterable[str],
        first_page: Optional[int],
        last_page: Optional[int],
        decision_date: datetime.date,
        court: str,
        opinion_dict: Dict[str, str],
    ) -> Opinion:

        author = opinion_dict.get("author")
        if author:
            author = author.strip(",:")

        return Opinion(
            name=name,
            name_abbreviation=name_abbreviation,
            citations=citations,
            first_page=first_page,
            last_page=last_page,
            decision_date=decision_date,
            court=court,
            position=opinion_dict.get("type"),
            author=author,
            text=opinion_dict.get("text"),
        )

    if not casebody:
        casebody = {}

    opinions = casebody.get("data", {}).get(
        "opinions", [{"type": "majority", "author": None}]
    )

    make_opinion_given_case = partial(
        make_opinion,
        name=name,
        name_abbreviation=name_abbreviation,
        first_page=int(first_page) if first_page else None,
        last_page=int(last_page) if last_page else None,
        decision_date=datetime.date.fromisoformat(decision_date),
        court=court["slug"],
        citations=tuple(c["cite"] for c in citations),
    )
    if lead_only:
        if as_generator:
            return iter([make_opinion_given_case(opinion_dict=opinions[0])])
        else:
            return make_opinion_given_case(opinion_dict=opinions[0])
    elif as_generator:
        return iter(
            make_opinion_given_case(opinion_dict=opinion_dict)
            for opinion_dict in opinions
        )
    return [
        make_opinion_given_case(opinion_dict=opinion_dict) for opinion_dict in opinions
    ]


def read_rule(record: Dict, regime: Optional[Regime] = None) -> Rule:
    r"""
    Make :class:`Rule` from a :class:`dict` of fields and a :class:`.Regime`\.

    :param record:

    :param regime:

    :returns:
        iterator yielding :class:`Rule`\s with the items
        from ``mentioned_entities`` as ``context_factors``
    """
    mentioned = index_names(record)
    schema = schemas.RuleSchema()
    schema.context["mentioned"] = mentioned
    schema.context["regime"] = regime
    return schema.load(record)
