"""AuthoritySpoke re-export of nettlesome FactorGroup."""

from __future__ import annotations

from authorityspoke.nettlesome.groups import FactorGroup, unique_explanations

import textwrap
from typing import List, Sequence, Tuple, Union

from legislice.enactments import Enactment, EnactmentPassage, consolidate_enactments
from pydantic import RootModel, field_validator, model_validator


def sort_passages(passages: List[EnactmentPassage]) -> List[EnactmentPassage]:
    """
    Sort EnactmentPassages in group, in place.

    Sorts federal before state; constitutional before statute before regulation;
    and then alphabetically
    """
    passages.sort(key=lambda x: x.node)
    passages.sort(key=lambda x: x.level)
    passages.sort(key=lambda x: x.is_federal, reverse=True)
    return passages


def consolidate_passages(
    obj: EnactmentGroup
    | Enactment
    | EnactmentPassage
    | Sequence[Enactment | EnactmentPassage],
) -> list[EnactmentPassage]:
    """Consolidate overlapping EnactmentPassages into fewer objects."""
    if isinstance(obj, EnactmentGroup):
        return obj.passages
    if isinstance(obj, (Enactment, EnactmentPassage)):
        obj = [obj]
    consolidated: List[EnactmentPassage] = consolidate_enactments(list(obj))
    return consolidated


class EnactmentGroup(RootModel[Tuple[EnactmentPassage, ...]]):
    """Group of Enactments with comparison methods."""

    root: Tuple[EnactmentPassage, ...] = ()

    def __init__(self, /, *args, **kwargs):
        if "passages" in kwargs:
            if "root" in kwargs:
                raise TypeError("Use either 'root' or 'passages', not both.")
            kwargs["root"] = kwargs.pop("passages")
        elif not args and "root" not in kwargs:
            kwargs["root"] = ()
        super().__init__(*args, **kwargs)

    @model_validator(mode="before")
    @classmethod
    def normalize_root(cls, value):
        if isinstance(value, dict):
            if "root" in value:
                value = value["root"]
            elif "passages" in value:
                value = value["passages"]
            elif not value:
                value = ()

        if value is None:
            return ()
        if isinstance(value, cls):
            return tuple(value.sequence)
        if isinstance(value, (Enactment, EnactmentPassage)):
            value = [value]

        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            items = list(value)
            if all(isinstance(item, (Enactment, EnactmentPassage)) for item in items):
                passages = sort_passages(consolidate_enactments(items))
                return tuple(passages)
            return tuple(items)

        return (value,)

    @field_validator("root")
    @classmethod
    def validate_root(
        cls, value: Sequence[EnactmentPassage]
    ) -> tuple[EnactmentPassage, ...]:
        value = sort_passages(list(value))
        for passage in value:
            if not isinstance(passage, EnactmentPassage):
                raise TypeError(
                    f'Object "{passage}" could not be included in '
                    f"{cls.__name__} because it is type "
                    f"{passage.__class__.__name__}, not type EnactmentPassage"
                )
        return tuple(value)

    @property
    def sequence(self) -> Tuple[EnactmentPassage, ...]:
        return tuple(self.root)

    @sequence.setter
    def sequence(self, value: Sequence[EnactmentPassage]) -> None:
        self.root = tuple(value)

    @property
    def passages(self) -> List[EnactmentPassage]:
        return list(self.sequence)

    @passages.setter
    def passages(self, value: Sequence[Enactment | EnactmentPassage]) -> None:
        self.root = self.__class__(root=value).root

    def _at_index(self, key: int) -> EnactmentPassage:
        return self.passages[key]

    def __getitem__(
        self, key: Union[int, slice]
    ) -> Union[EnactmentPassage, EnactmentGroup]:
        if isinstance(key, slice):
            start, stop, step = key.indices(len(self))
            return self.__class__(
                passages=[self._at_index(i) for i in range(start, stop, step)]
            )
        return self._at_index(key)

    def __iter__(self):
        yield from self.passages

    def __len__(self):
        return len(self.passages)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(list(self.passages))})"

    def __str__(self):
        result = "the group of Enactments:"
        indent = "  "
        for factor in self.passages:
            result += f"\n{textwrap.indent(str(factor), prefix=indent)}"
        return result

    def _add_group(self, other: EnactmentGroup) -> EnactmentGroup:
        combined = self.passages[:] + other.passages[:]
        return self.__class__(passages=combined)

    def __add__(
        self,
        other: Union[
            EnactmentGroup,
            Sequence[Enactment | EnactmentPassage],
            Enactment,
            EnactmentPassage,
        ],
    ) -> EnactmentGroup:
        """Combine two EnactmentGroups, consolidating any duplicate Enactments."""
        if isinstance(other, self.__class__):
            return self._add_group(other)
        passages = consolidate_passages(other)
        to_add = self.__class__(passages=passages)
        return self._add_group(to_add)

    def __ge__(self, other: Union[Enactment, EnactmentPassage, EnactmentGroup]) -> bool:
        """Test whether ``self`` implies ``other`` and ``self`` != ``other``."""
        return bool(self.implies(other))

    def __gt__(self, other: Union[Enactment, EnactmentPassage, EnactmentGroup]) -> bool:
        """Test whether ``self`` implies ``other`` and ``self`` != ``other``."""
        return bool(self.implies(other))

    def _implies_enactment(self, other: Union[Enactment, EnactmentPassage]) -> bool:
        return any(self_enactment.implies(other) for self_enactment in self)

    def _implies(self, other: EnactmentGroup) -> bool:
        return all(self._implies_enactment(other_law) for other_law in other)

    def implies(
        self, other: Union[Enactment, EnactmentPassage, EnactmentGroup]
    ) -> bool:
        """Determine whether self includes all the text of another Enactment or EnactmentGroup."""
        if isinstance(other, (Enactment, EnactmentPassage)):
            return self._implies_enactment(other)
        return self._implies(other)
