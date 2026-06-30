"""
Converting simple structured data from XML or JSON into authorityspoke objects.

These functions will usually be called by functions from the io.loaders module
after they import some data from a file.
"""

from typing import Dict, Union


from authorityspoke.nettlesome.entities import Entity

from authorityspoke.decisions import Decision, DecisionReading, RawDecision
from authorityspoke.facts import Fact, Exhibit, Evidence, Allegation, Pleading

RawSelector = Union[str, Dict[str, str]]


FACTOR_SUBCLASSES = {
    class_obj.__name__: class_obj
    for class_obj in (Allegation, Entity, Exhibit, Evidence, Fact, Pleading)
}


def read_decision(decision: Union[RawDecision, Decision]) -> DecisionReading:
    r"""
    Create and return a :class:`~authorityspoke.decisions.Decision` from a dict API response.

    Relies on the JSON format from the `Caselaw Access Project
    API <https://api.case.law/v1/cases/>`_.

    :param decision_dict:
        A dict created from a Caselaw Access Project API response.
    """
    if not isinstance(decision, Decision):
        decision = Decision(**decision)  # ty: ignore[invalid-argument-type]
    return DecisionReading(decision=decision)
