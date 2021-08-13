"""AuthoritySpoke: Reading the law for the last time."""

from justopinion.decisions import Decision
from legislice import Enactment
from legislice.download import Client as LegisClient
from nettlesome.entities import Entity
from nettlesome.predicates import Predicate
from nettlesome.quantities import Comparison

from .decisions import DecisionReading
from .facts import Fact
from .holdings import Holding
from .opinions import Opinion, OpinionReading
from .rules import Rule
from .io.downloads import CAPClient
from .io.dump import to_dict, to_json

__version__ = "0.8.0"
