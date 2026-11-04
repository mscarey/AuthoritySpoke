"""AuthoritySpoke re-export of nettlesome FactorGroup."""

from __future__ import annotations

from legislice.groups import (
    ConsolidatablePassage,
    EnactmentGroup,
    EnactmentGroupItem,
    SortablePassage,
    consolidate_passages,
    sort_passages,
)

from authorityspoke.nettlesome.groups import FactorGroup, unique_explanations

__all__ = [
    "ConsolidatablePassage",
    "EnactmentGroup",
    "EnactmentGroupItem",
    "FactorGroup",
    "SortablePassage",
    "consolidate_passages",
    "sort_passages",
    "unique_explanations",
]
