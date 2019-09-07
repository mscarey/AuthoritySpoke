"""
Converting simple structured data from XML or JSON into authorityspoke objects.

These functions will usually be called by functions from the io.loaders module
after they import some data from a file.
"""
import datetime
from functools import partial
import re

from typing import Any, Dict, List, Iterable, Iterator, Optional, Tuple, Type, Union

from pint import UnitRegistry

from authorityspoke.io import references
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



ureg = UnitRegistry()

FACTOR_SUBCLASSES = {
    class_obj.__name__: class_obj
    for class_obj in (Allegation, Entity, Exhibit, Evidence, Fact, Pleading)
}

@references.log_mentioned_context
def read_enactment(
    enactment_dict: Dict[str, str],
    code: Optional[Code] = None,
    mentioned: Optional[TextLinkDict] = None,
    regime: Optional[Regime] = None,
    report_mentioned: bool = False,
    **kwargs,
) -> Union[Enactment, Tuple[Enactment, TextLinkDict]]:
    r"""
    Create a new :class:`Enactment` object using imported JSON data.

    The new :class:`Enactment` can be composed from a :class:`.Code`
    referenced in the ``regime`` parameter.

    :param enactment_dict:
        :class:`dict` with string fields from JSON for constructing
        new :class:`.Enactment`

    :param code:
        the :class:`.Code` that is the source for this
        :class:`Enactment`

    :param mentioned:
        :class:`.TextLinkDict` for known :class:`.Factor`\s
        and :class:`.Enactment`\s

    :param regime:
        the :class:`.Regime` where the :class:`.Code` that is the
        source for this :class:`Enactment` can be found, or where
        it should be added

    :param report_mentioned:
        if True, return a new :class:`.TextLinkDict` in addition to
        the :class:`.Enactment`\.

    :returns:
        a new :class:`Enactment` object, optionally with text links.
    """
    if regime and not code:
        code = regime.get_code(enactment_dict["path"])
    if code is None and enactment_dict.get("file"):
        code = Code(enactment_dict["file"])
    if code is None:
        raise ValueError(
            "Must either specify a Regime and a path to find the "
            + "Code within the Regime, or specify a filename for an XML "
            + "file that can be used to build the Code"
        )
    if regime:
        regime.set_code(code)

    name = enactment_dict.get("name")
    if name:
        del enactment_dict["name"]
    selector = references.read_selector(record=enactment_dict, source=code)
    answer = Enactment(code=code, selector=selector, name=name)
    mentioned = mentioned or {}
    return (answer, mentioned) if report_mentioned else answer


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

    :param code:
        the :class:`.Code` that is the source for this
        :class:`Enactment`

    :param mentioned:
        :class:`.TextLinkDict` for known :class:`.Factor`\s
        and :class:`.Enactment`\s

    :param regime:
        the :class:`.Regime` where the :class:`.Code` that is the
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
    mentioned = mentioned or {}
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
    return content, context_factors


def read_quantity(quantity: str) -> Union[float, int, ureg.Quantity]:
    """
    Create `pint <https://pint.readthedocs.io/en/0.9/tutorial.html>`_ quantity object from text.

    :param quantity:
        when a string is being parsed for conversion to a
        :class:`Predicate`, this is the part of the string
        after the equals or inequality sign.
    :returns:
        a Python number object or a :class:`Quantity`
        object created with `pint.UnitRegistry
        <https://pint.readthedocs.io/en/0.9/tutorial.html>`_.
    """
    quantity = quantity.strip()
    if quantity.isdigit():
        return int(quantity)
    float_parts = quantity.split(".")
    if len(float_parts) == 2 and all(
        substring.isnumeric() for substring in float_parts
    ):
        return float(quantity)
    return ureg.Quantity(quantity)


def get_references_from_string(
    content: str, mentioned: TextLinkDict
) -> Tuple[str, List[Entity], TextLinkDict]:
    r"""
    Make :class:`.Entity` context :class:`.Factor`\s from string.

    This function identifies context :class:`.Factor`\s by finding
    brackets around them, while :func:`get_references_from_mentioned`
    depends on knowing the names of the context factors in advance.
    Also, this function works only when all the context_factors
    are type :class:`.Entity`.

    Despite "placeholder" being defined as a variable elsewhere,
    this function isn't compatible with any placeholder string other
    than "{}".

    :param content:
        a string containing a clause making an assertion.
        Curly brackets surround the names of :class:`.Entity`
        context factors to be created.

    :param content:
        a :class:`.TextLinkDict` of known :class:`.Factor`\s.
        It will not be searched for :class:`.Factor`\s to add
        to `context_factors`, but newly created :class:`.Entity`
        object will be added to it.

    :returns:
        a :class:`Predicate` and :class:`.Entity` objects
        from a string that has curly brackets around the
        context factors and the comparison/quantity.
    """
    pattern = r"\{([^\{]+)\}"
    entities_as_text = re.findall(pattern, content)

    context_factors = []
    for entity_name in entities_as_text:
        entity = Entity(name=entity_name)
        content = content.replace(entity_name, "")
        context_factors.append(entity)
        mentioned[entity] = []

    return content, context_factors, mentioned


def read_fact(
    content: str = "",
    truth: bool = True,
    reciprocal: bool = False,
    standard_of_proof: Optional[str] = None,
    name: Optional[str] = None,
    mentioned: Optional[TextLinkDict] = None,
    report_mentioned: bool = False,
    absent: bool = False,
    generic: bool = False,
    **kwargs,
) -> Union[Fact, Tuple[Fact, TextLinkDict]]:
    r"""
    Construct a :class:`Fact` from strings and bools.

    :param content:
        a string containing a clause making an assertion.

    :param truth:
        whether the assertion in `content` is claimed to be true

    :param reciprocal:
        whether the order of the first two entities in `content`
        can be changed without changing the meaning

    :param mentioned:
        a list of :class:`.Factor`\s that may be included by reference to their ``name``\s.

    :param standard_of_proof:
        the finding as to the strength of the evidence supporting
        the assertion, if any

    :param name:
        a string identifier

    :param mentioned:
        known :class:`.Factors`. Can be reused.

    :param report_mentioned:
        if True, return a new :class:`.TextLinkDict` in addition to
        the :class:`.Fact`\.

    :param absent:
        whether the :class:`.Fact` can be considered absent from the case

    :param generic:
        whether the :class:`.Fact` is interchangeable with other generic
        facts without changing the meaning of a :class:`.Rule` where it is
        mentioned

    :returns:
        a :class:`Fact`, with optional mentioned factors
    """
    mentioned = mentioned or {}
    placeholder = "{}"  # to be replaced in the Fact's string method
    if not name:
        name = f'{"false " if not truth else ""}{content}'
    name = name.replace("{", "").replace("}", "")

    comparison = ""
    quantity = None
    if content:
        if placeholder[0] in content:
            content, context_factors, mentioned = get_references_from_string(
                content, mentioned
            )
        else:
            content, context_factors = get_references_from_mentioned(
                content, mentioned, placeholder
            )
    for item in Predicate.opposite_comparisons:
        if item in content:
            comparison = item
            content, quantity_text = content.split(item)
            quantity = read_quantity(quantity_text)
            content += placeholder

    predicate = Predicate(
        content=content,
        truth=truth,
        reciprocal=reciprocal,
        comparison=comparison,
        quantity=quantity,
    )

    answer = Fact(
        predicate,
        context_factors,
        name=name,
        standard_of_proof=standard_of_proof,
        absent=absent,
        generic=generic,
    )
    return (answer, mentioned) if report_mentioned else answer

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

@references.log_mentioned_context
def read_factor(
    factor_record: Dict,
    mentioned: Optional[TextLinkDict] = None,
    report_mentioned: bool = False,
    **kwargs,
) -> Union[Optional[Factor], Tuple[Optional[Factor], TextLinkDict]]:
    r"""
    Turn fields from a chunk of JSON into a :class:`Factor` object.

    :param factor_record:
        parameter values to pass to :meth:`Factor.__init__`.

    :param mentioned:
        a list of relevant :class:`Factor`\s that have already been
        constructed and can be used in composition of the output
        :class:`Factor`, instead of constructing new ones.
    """
    cname = factor_record["type"]
    mentioned = mentioned or {}
    target_class = subclass_from_str(cname)
    if target_class == Fact:
        created_factor, mentioned = read_fact(
            mentioned=mentioned, report_mentioned=True, **factor_record
        )
    else:
        created_factor, mentioned = read_factor_subclass(
            target_class, factor_record, mentioned, report_mentioned=True
        )
    return (created_factor, mentioned) if report_mentioned else created_factor


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
    mentioned = mentioned or {}
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
    mentioned = mentioned or {}
    answer = tuple(created_list)
    return (answer, mentioned) if report_mentioned else answer


def read_holding(
    outputs: Optional[Union[str, Dict, List[Union[str, Dict]]]],
    inputs: Optional[Union[str, Dict, List[Union[str, Dict]]]] = None,
    despite: Optional[Union[str, Dict, List[Union[str, Dict]]]] = None,
    exclusive: bool = False,
    rule_valid: bool = True,
    decided: bool = True,
    mandatory: bool = False,
    universal: bool = False,
    generic: bool = False,
    enactments: Optional[Union[Dict, Iterable[Dict]]] = None,
    enactments_despite: Optional[Union[Dict, Iterable[Dict]]] = None,
    anchors: Optional[Union[str, Dict, Iterable[Union[str, Dict]]]] = None,
    mentioned: Optional[TextLinkDict] = None,
    regime: Optional[Regime] = None,
    report_mentioned: bool = False,
) -> Iterator[Union[Holding, Tuple[Holding, TextLinkDict]]]:
    r"""
    Create new :class:`Holding` object from simple datatypes from JSON input.

    Will yield multiple items if ``exclusive: True`` is present in ``record``.

    :param inputs:
        data for constructing :class:`.Factor` inputs for a :class:`.Rule`

    :param despite:
        data for constructing despite :class:`.Factor`\s for a :class:`.Rule`

    :param outputs:
        data for constructing :class:`.Factor` outputs for a :class:`.Rule`

    :param enactments:
        the :class:`.Enactment`\s cited as authority for
        invoking the ``procedure``.

    :param enactments_despite:
        the :class:`.Enactment`\s specifically cited as failing
        to preclude application of the ``procedure``.

    :param mandatory:
        whether the ``procedure`` is mandatory for the
        court to apply whenever the :class:`.Rule` is properly invoked.
        ``False`` means that the ``procedure`` is "discretionary".

    :param universal:
        ``True`` if the ``procedure`` is applicable whenever
        its inputs are present. ``False`` means that the ``procedure`` is
        applicable in "some" situation where the inputs are present.

    :param generic:
        whether the :class:`Rule` is being mentioned in a generic
        context. e.g., if the :class:`Rule` is being mentioned in
        an :class:`.Argument` object merely as an example of the
        kind of :class:`Rule` that might be mentioned in such an
        :class:`.Argument`.

    :param name:
        an identifier used to retrieve the :class:`Rule` when
        needed for the composition of another :class:`.Factor`
        object.

    :param rule_valid:
        Whether the :class:`.Rule` is asserted to be valid (or
        useable by a court in litigation).

    :param decided:
        Whether it should be deemed decided whether the :class:`.Rule`
        is valid. If not, the :class:`.Holding` have the effect
        of overruling prior :class:`.Holding`\s finding the :class:`.Rule`
        to be either valid or invalid.

    :param anchors:
        Text selectors for the whole :class:`Holding`, not for any
        individual :class:`.Factor`. Often selects text used to
        indicate whether the :class:`.Rule` is ``mandatory``, ``universal``,
        ``valid``, or ``decided``, or shows the ``exclusive`` way to reach
        the outputs.

    :param mentioned:
        Known :class:`.Factor`\s that may be reused in constructing
        the new :class:`Holding`.

    :param regime:
        Collection of :class:`.Jurisdiction`\s and corresponding
        :class:`.Code`\s for discovering :class:`.Enactment`\s to
        reference in the new :class:`Holding`.

    :returns:
        New :class:`.Holding`, and an updated dictionary with mentioned
        :class:`.Factor`\s as keys and their :class:`.TextQuoteSelector`\s
        as values.
    """

    # If lists were omitted around single elements in the JSON,
    # add them back

    mentioned = mentioned or {}

    selectors = references.read_selectors(anchors)

    basic_rule, mentioned = read_rule(
        outputs=outputs,
        inputs=inputs,
        despite=despite,
        mandatory=mandatory,
        universal=universal,
        generic=generic,
        enactments=enactments,
        enactments_despite=enactments_despite,
        mentioned=mentioned,
        regime=regime,
        report_mentioned=True,
    )
    answer = Holding(
        rule=basic_rule, rule_valid=rule_valid, decided=decided, selectors=selectors
    )
    yield (answer, mentioned) if report_mentioned else answer

    if exclusive:
        if not rule_valid:
            raise NotImplementedError(
                "The ability to state that it is not 'valid' to assert "
                + "that a Rule is the 'exclusive' way to reach an output is "
                + "not implemented, so 'rule_valid' cannot be False while "
                + "'exclusive' is True. Try expressing this in another way "
                + "without the 'exclusive' keyword."
            )
        if not decided:
            raise NotImplementedError(
                "The ability to state that it is not 'decided' whether "
                + "a Rule is the 'exclusive' way to reach an output is "
                + "not implemented. Try expressing this in another way "
                + "without the 'exclusive' keyword."
            )
        for modified_rule in basic_rule.get_contrapositives():
            answer = Holding(rule=modified_rule, selectors=selectors)
            yield (answer, mentioned) if report_mentioned else answer


def read_holdings(
    holdings: Dict[str, Iterable],  # TODO: remove "mentioned_factors" from JSON format
    regime: Optional[Regime] = None,
    mentioned: Optional[TextLinkDict] = None,
    report_mentioned: bool = False,
) -> Union[List[Holding], Tuple[List[Holding], TextLinkDict]]:
    r"""
    Load a list of :class:`Holdings`\s from JSON, with optional text links.

    :param holdings:
        the record from JSON in the format that lists ``mentioned_factors``
        followed by a list of holdings

    :parame regime:
        A collection of :class:`.Jurisdiction`\s and the :class:`.Code`\s
        that have been enacted in each. Used for constructing
        :class:`.Enactment`\s referenced by :class:`.Holding`\s.

    :param mentioned:
        A dict of :class:`.Factor`\s that the method needs to
        expect to find in the :class:`.Holding`\s,
        linked to lists of :class:`.TextQuoteSelector`\s indicating
        where each :class:`.Factor` can be found in the :class:`.Opinion`\.

    :returns:
        a list of :class:`.Holding` objects, optionally with
        an index matching :class:`.Factor`\s to selectors.
    """
    # populates mentioned with context factors that don't
    # appear in inputs, outputs, or despite
    mentioned_factors = holdings.get("mentioned_factors")
    if mentioned_factors:
        if isinstance(mentioned_factors, dict):
            mentioned_factors = [mentioned_factors]
        for factor_dict in mentioned_factors:
            _, mentioned = read_factor(
                factor_record=factor_dict,
                mentioned=mentioned,
                regime=regime,
                report_mentioned=True,
            )

    finished_holdings: List[Holding] = []
    for holding_record in holdings["holdings"]:

        for generated_holding in read_holding(
            mentioned=mentioned, regime=regime, report_mentioned=True, **holding_record
        ):
            finished_holding, mentioned = generated_holding
            finished_holdings.append(finished_holding)
    mentioned = mentioned or {}
    return (finished_holdings, mentioned) if report_mentioned else finished_holdings


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


def read_rule(
    outputs: Optional[Union[str, Dict, List[Union[str, Dict]]]],
    inputs: Optional[Union[str, Dict, List[Union[str, Dict]]]] = None,
    despite: Optional[Union[str, Dict, List[Union[str, Dict]]]] = None,
    mandatory: bool = False,
    universal: bool = False,
    generic: bool = False,
    enactments: Optional[Union[Dict, Iterable[Dict]]] = None,
    enactments_despite: Optional[Union[Dict, Iterable[Dict]]] = None,
    mentioned: Optional[TextLinkDict] = None,
    regime: Optional[Regime] = None,
    report_mentioned: bool = False,
) -> Union[Rule, Tuple[Rule, TextLinkDict]]:
    r"""
    Make :class:`Rule` from a :class:`dict` of strings and a list of mentioned :class:`.Factor`\s.

    :param inputs:
        data for constructing :class:`.Factor` inputs for a :class:`.Rule`

    :param despite:
        data for constructing despite :class:`.Factor`\s for a :class:`.Rule`

    :param outputs:
        data for constructing :class:`.Factor` outputs for a :class:`.Rule`

    :param enactments:
        the :class:`.Enactment`\s cited as authority for
        invoking the ``procedure``.

    :param enactments_despite:
        the :class:`.Enactment`\s specifically cited as failing
        to preclude application of the ``procedure``.

    :param mandatory:
        whether the ``procedure`` is mandatory for the
        court to apply whenever the :class:`.Rule` is properly invoked.
        ``False`` means that the ``procedure`` is "discretionary".

    :param universal:
        ``True`` if the ``procedure`` is applicable whenever
        its inputs are present. ``False`` means that the ``procedure`` is
        applicable in "some" situation where the inputs are present.

    :param generic:
        whether the :class:`Rule` is being mentioned in a generic
        context. e.g., if the :class:`Rule` is being mentioned in
        an :class:`.Argument` object merely as an example of the
        kind of :class:`Rule` that might be mentioned in such an
        :class:`.Argument`.

    :param mentioned:
        a series of context factors, including any generic
        :class:`.Factor`\s that need to be mentioned in
        :class:`.Predicate`\s. These will have been constructed
        from the ``mentioned_entities`` section of the input
        JSON.

    :param regime:

    :returns:
        iterator yielding :class:`Rule`\s with the items
        from ``mentioned_entities`` as ``context_factors``
    """

    factor_groups = {
        "outputs": outputs,
        "inputs": inputs,
        "despite": despite,
    }
    enactment_groups = {
        "enactments": enactments,
        "enactments_despite": enactments_despite,
    }
    built_factors: Dict[str, Tuple[Factor]] = {}
    built_enactments: Dict[str, Tuple[Enactment]] = {}

    for category_name, factor_group in factor_groups.items():
        built_factors[category_name], mentioned = read_factors(
            record_list=factor_group,
            mentioned=mentioned,
            regime=regime,
            report_mentioned=True,
        )
    for category_name, enactment_group in enactment_groups.items():
        built_enactments[category_name], mentioned = read_enactments(
            record_list=enactment_group,
            mentioned=mentioned,
            regime=regime,
            report_mentioned=True,
        )

    procedure = Procedure(
        outputs=built_factors["outputs"],
        inputs=built_factors["inputs"],
        despite=built_factors["despite"]
    )

    answer = Rule(
        procedure=procedure,
        enactments=built_enactments["enactments"],
        enactments_despite=built_enactments["enactments_despite"],
        mandatory=mandatory,
        universal=universal,
        generic=generic,
    )
    mentioned = mentioned or {}
    return (answer, mentioned) if report_mentioned else answer
