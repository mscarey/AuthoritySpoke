"""
Converting simple structured data from XML or JSON into authorityspoke objects.

These functions will usually be called by functions from the io.loaders module
after they import some data from a file.
"""
from collections import defaultdict
from copy import deepcopy
import datetime
from functools import partial

from typing import Any, Dict, List, Iterable, Iterator
from typing import Optional, Set, Tuple, Type, Union

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
from authorityspoke.selectors import TextQuoteSelector

from authorityspoke.io import references
from authorityspoke.io import schemas
from authorityspoke.io.name_index import index_names


ureg = UnitRegistry()

FACTOR_SUBCLASSES = {
    class_obj.__name__: class_obj
    for class_obj in (Allegation, Entity, Exhibit, Evidence, Fact, Pleading)
}


def read_selector(
    record: Optional[Union[Dict, str]], many: bool = False
) -> Optional[TextQuoteSelector]:
    """
    Create new selector from JSON user input.

    :param record:
        a string or dict representing a text passage

    :returns: a new :class:`TextQuoteSelector`
    """
    if not record:
        return None
    selector_schema = schemas.SelectorSchema(many=many)
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
    return read_selector(record, many=True)


def read_enactment(
    enactment_dict: Dict[str, str],
    code: Optional[Code] = None,
    regime: Optional[Regime] = None,
    **kwargs,
) -> Enactment:
    r"""
    Create a new :class:`.Enactment` object using imported JSON data.

    The new :class:`.Enactment` can be composed from a :class:`.Code`
    referenced in the ``regime`` parameter.

    :param enactment_dict:
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
    schema = schemas.EnactmentSchema(context={"code": code, "regime": regime})
    answer = schema.load(enactment_dict)

    return answer


def read_enactments(
    record_list: Union[Dict[str, str], List[Dict[str, str]]],
    mentioned: Optional[TextLinkDict] = None,
    regime: Optional[Regime] = None,
    report_mentioned: bool = False,
) -> Union[Tuple[Enactment, ...], Tuple[Tuple[Enactment, ...], TextLinkDict]]:
    r"""
    Create a new :class:`Enactment` object using imported JSON data.

    The new :class:`Enactment` can be composed from a :class:`.Code`
    referenced in the ``regime`` parameter.

    :param record_list:
        sequence of :class:`dict`\s with string fields from JSON for
        constructing new :class:`.Enactment`\s

    :param mentioned:
        :class:`.TextLinkDict` for known :class:`.Factor`\s
        and :class:`.Enactment`\s

    :param regime:
        the :class:`.Regime` where the :class:`.Code`\s that are the
        source for this :class:`Enactment` can be found, or where
        it should be added

    :param report_mentioned:
        if True, return a new :class:`.TextLinkDict` in addition to
        the :class:`.Enactment`\.

    :returns:
        a list of new :class:`Enactment` objects, optionally with text links.
    """
    created_list: List[Enactment] = []
    if record_list is None:
        record_list = []
    if not isinstance(record_list, list):
        record_list = [record_list]
    for record in record_list:
        created, mentioned = read_enactment(
            record, mentioned=mentioned, regime=regime, report_mentioned=True
        )
        created_list.append(created)
    mentioned = mentioned or Mentioned({})
    answer = tuple(created_list)
    return (answer, mentioned) if report_mentioned else answer


def get_references_from_mentioned(
    content: str, mentioned: TextLinkDict, placeholder: str = "{}"
) -> Tuple[str, List[Union[Enactment, Factor]]]:
    r"""
    Retrieve known context :class:`Factor`\s for new :class:`Fact`.

    :param content:
        the content for the :class:`Fact`\'s :class:`Predicate`.

    :param mentioned:
        list of :class:`Factor`\s with names that could be
        referenced in content

    :param placeholder:
        a string to replace the names of
        referenced :class:`Factor`\s in content

    :returns:
        the content string with any referenced :class:`Factor`\s
        replaced by placeholder, and a list of referenced
        :class:`Factor`\s in the order they appeared in content.
    """
    sorted_mentioned = sorted(
        mentioned.keys(), key=lambda x: len(x.name) if x.name else 0, reverse=True
    )
    context_with_indices: Dict[Union[Enactment, Factor], int] = {}
    for factor in sorted_mentioned:
        if factor.name and factor.name in content and factor.name != content:
            factor_index = content.find(factor.name)
            for named_factor in context_with_indices:
                if context_with_indices[named_factor] > factor_index:
                    context_with_indices[named_factor] -= len(factor.name) - len(
                        placeholder
                    )
            context_with_indices[factor] = factor_index
            content = content.replace(factor.name, placeholder)
    context_factors = sorted(context_with_indices, key=context_with_indices.get)
    return content, tuple(context_factors)


def read_predicate(value: Dict) -> Predicate:
    schema = schemas.PredicateSchema(partial=True)
    return schema.load(value)


def read_fact(record: Dict) -> Fact:
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


def subclass_from_str(name: str) -> Type:
    """
    Find class for use in JSON deserialization process.

    Obtains a classname of a :class:`Factor`
    subclass from a string. The list of subclasses used
    here must be updated wheneven a new one is created.

    :param name: name of the desired subclass.

    :returns: the Class named ``name``.
    """
    answer = FACTOR_SUBCLASSES.get(name.capitalize())
    if answer is None:
        raise ValueError(
            f'"type" value in input must be one of '
            + f"{list(FACTOR_SUBCLASSES.keys())}, not {name}"
        )
    return answer


def read_factor(
    record: Dict, regime: Optional[Regime] = None, many: bool = False, **kwargs
) -> Factor:
    r"""
    Turn fields from a chunk of JSON into a :class:`Factor` object.

    :param record:
        parameter values to pass to :meth:`Factor.__init__`.

    """
    schema = schemas.FactorSchema(many=many)
    record, schema.context["mentioned"] = index_names(record)
    schema.context["regime"] = regime
    return schema.load(record)


def read_factor_subclass(
    cls,
    factor_record: Dict,
    mentioned: Optional[TextLinkDict] = None,
    report_mentioned: bool = False,
) -> Union[Factor, Tuple[Factor, TextLinkDict]]:
    prototype = cls()
    new_factor_dict = prototype.__dict__
    for attr in new_factor_dict:
        if attr in prototype.context_factor_names:
            value, mentioned = read_factor(
                factor_record=factor_record.get(attr),
                mentioned=mentioned,
                report_mentioned=True,
            )
        else:
            value = factor_record.get(attr)
        if value is not None:
            new_factor_dict[attr] = value
    answer: Factor = cls(**new_factor_dict)
    mentioned = mentioned or Mentioned({})
    return (answer, mentioned) if report_mentioned else answer


def read_factors(
    record_list: Union[Dict[str, str], List[Dict[str, str]]],
    mentioned: Optional[TextLinkDict] = None,
    regime: Optional[Regime] = None,
    report_mentioned: bool = False,
) -> Union[Tuple[Factor, ...], Tuple[Tuple[Factor, ...], TextLinkDict]]:
    created_list: List[Factor] = []
    if record_list is None:
        record_list = []
    if not isinstance(record_list, list):
        record_list = [record_list]
    for record in record_list:
        created, mentioned = read_factor(
            record, mentioned, regime=regime, report_mentioned=True
        )
        created_list.append(created)
    mentioned = mentioned or Mentioned({})
    answer = tuple(created_list)
    return (answer, mentioned) if report_mentioned else answer


def read_procedure(
    record: Dict, regime: Optional[Regime] = None, many=False
) -> Procedure:
    schema = schemas.ProcedureSchema(many=many)
    record, schema.context["mentioned"] = index_names(record)
    schema.context["regime"] = regime
    return schema.load(record)


def read_holding(
    record: Dict,
    regime: Optional[Regime] = None,
    many: bool = False,
    index_anchors: bool = False,
) -> Holding:
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
    record, mentioned = index_names(record)
    if index_anchors:
        holding_anchors = [collect_anchors(holding) for holding in record]
        anchors = collect_anchors(deepcopy(record), regime=regime)
    schema = schemas.HoldingSchema(many=many)

    proxy = deepcopy(mentioned)

    schema.context["mentioned"] = proxy
    schema.context["regime"] = regime
    answer = schema.load(record)
    return (answer, anchors) if index_anchors else answer


def read_holdings(
    record: List[Dict], regime: Optional[Regime] = None, index_anchors: bool = False
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
    return read_holding(
        record=record, regime=regime, many=True, index_anchors=index_anchors
    )


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
    record, mentioned = index_names(record)
    schema = schemas.RuleSchema()
    schema.context["mentioned"] = mentioned
    schema.context["regime"] = regime
    return schema.load(record)
