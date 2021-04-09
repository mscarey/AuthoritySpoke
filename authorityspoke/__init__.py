"""AuthoritySpoke: Reading the law for the last time."""

from legislice import Enactment
from nettlesome.entities import Entity
from nettlesome.predicates import Predicate
from nettlesome.quantities import Comparison

from .facts import Fact
from .holdings import Holding
from .opinions import Opinion
from .rules import Rule
from .io.dump import to_dict, to_json

__version__ = "0.6.0"
