"""AuthoritySpoke: Reading the law for the last time."""

from legislice import Enactment

from .entities import Entity
from .factors import Factor
from .facts import Fact
from .opinions import Opinion
from .predicates import Predicate, Comparison
from .rules import Rule
from .io.dump import to_dict, to_json

__version__ = "0.5.0"
