"""AuthoritySpoke specialization of nettlesome FactorGroup."""

from authorityspoke.facts import AbsenceOfFactor
from authorityspoke.nettlesome.groups import (
    FactorGroup as NettlesomeFactorGroup,
    unique_explanations,
)


class FactorGroup(NettlesomeFactorGroup):
    """A FactorGroup that accepts AuthoritySpoke's AbsenceOfFactor."""

    absence_class = AbsenceOfFactor


__all__ = ["FactorGroup", "unique_explanations"]
