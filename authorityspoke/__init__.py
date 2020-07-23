"""AuthoritySpoke: Reading the law for the last time."""

from legislice import Enactment

from .codes import Code
from .entities import Entity
from .factors import Factor
from .jurisdictions import Jurisdiction, Regime
from .opinions import Opinion
from .rules import Rule
from .io.dump import to_dict, to_json

__version__ = "0.3.4"
