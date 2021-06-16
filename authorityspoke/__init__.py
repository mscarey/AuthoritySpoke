"""AuthoritySpoke: Reading the law for the last time."""

from legislice import Enactment
from legislice.download import Client as LegisClient
from nettlesome.entities import Entity
from nettlesome.predicates import Predicate
from nettlesome.quantities import Comparison

from .facts import Fact
from .holdings import Holding
from .opinions import Opinion
from .rules import Rule
from .io.downloads import CAPClient
from .io.dump import to_dict, to_json

__version__ = "0.7.2"
