"""AuthoritySpoke: Reading the law for the last time."""

from justopinion import Opinion
from justopinion.decisions import Decision
from justopinion.download import CAPClient, CourtListenerClient
from legislice import Enactment
from legislice.download import Client as LegisClient

from authorityspoke.nettlesome.entities import Entity
from authorityspoke.nettlesome.predicates import Predicate
from authorityspoke.nettlesome.quantities import Comparison

from .decisions import DecisionReading
from .facts import Allegation, Evidence, Exhibit, Fact, Pleading
from .holdings import Holding
from .opinions import OpinionReading
from .rules import Rule

__version__ = "0.10.0"

__all__ = [
    "Allegation",
    "CAPClient",
    "Comparison",
    "CourtListenerClient",
    "Decision",
    "DecisionReading",
    "Enactment",
    "Entity",
    "Evidence",
    "Exhibit",
    "Fact",
    "Holding",
    "LegisClient",
    "Opinion",
    "OpinionReading",
    "Pleading",
    "Predicate",
    "Rule",
]
