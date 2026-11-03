"""AuthoritySpoke re-export of nettlesome FactorGroup."""

from __future__ import annotations

from authorityspoke.nettlesome.groups import FactorGroup, unique_explanations

from legislice.groups import (
    EnactmentGroup,
    EnactmentGroupItem,
    SortablePassage,
    ConsolidatablePassage,
    consolidate_passages,
    sort_passages,
)

__all__ = [
    "FactorGroup",
    "unique_explanations",
    "EnactmentGroup",
    "EnactmentGroupItem",
    "SortablePassage",
    "ConsolidatablePassage",
    "consolidate_passages",
    "sort_passages",
]
