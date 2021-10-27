"""AuthoritySpoke: Reading the law for the last time."""

from justopinion.decisions import Decision
from justopinion import CAPClient, Opinion
from legislice import Enactment
from legislice.download import Client as LegisClient
from nettlesome.entities import Entity
from nettlesome.predicates import Predicate
from nettlesome.quantities import Comparison

from .decisions import DecisionReading
from .facts import Fact, Exhibit, Evidence, Allegation, Pleading
from .holdings import Holding
from .opinions import OpinionReading
from .rules import Rule

__version__ = "0.9.0"
