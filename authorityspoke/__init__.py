"""AuthoritySpoke: Reading the law for the last time."""

from .enactments import Code, Enactment
from .entities import Entity
from .factors import Factor
from .jurisdictions import Jurisdiction, Regime
from .opinions import Opinion
from .rules import Rule
from .io.dump import to_dict, to_json

__version__ = "0.3.4"
