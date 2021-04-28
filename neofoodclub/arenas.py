from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Sequence

import neofoodclub.math as NFCMath

from .neofoodclub import NeoFoodClub
from .pirates import Pirate

if TYPE_CHECKING:
    from neofoodclub.types import PirateID, ValidIndex

__all__ = (
    "Arena",
    "Arenas",
    "ARENA_NAMES",
)

ARENA_NAMES = ["Shipwreck", "Lagoon", "Treasure", "Hidden", "Harpoon"]


class Arena:
    __slots__ = (
        "_pirates",
        "_id",
    )

    def __init__(self, *, nfc: NeoFoodClub, arena_id: int, pirate_ids: Sequence[int]):
        self._id = arena_id
        self._pirates = [  # adding 1 to index because the original list has a length of 4, but everything else has 5
            Pirate(nfc=nfc, id=p_id, arena=arena_id, index=idx + 1)
            for idx, p_id in enumerate(pirate_ids)
        ]

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return ARENA_NAMES[self._id]

    @property
    def best(self) -> List[Pirate]:
        return sorted(self._pirates, key=lambda a: a.odds)

    @property
    def ids(self):
        return [p.id for p in self._pirates]

    @property
    def odds(self) -> float:
        # do note that arena odds are not the same as pirate odds
        return sum(1 / p.odds for p in self._pirates)

    @property
    def ratio(self) -> float:
        return 1 / self.odds - 1

    @property
    def pirates(self) -> List[Pirate]:
        return self._pirates

    @property
    def positive(self) -> bool:
        return self.odds < 1

    @property
    def negative(self) -> bool:
        return not self.positive

    def __getitem__(self, item: ValidIndex) -> Optional[Pirate]:
        try:
            return self._pirates[item]
        except KeyError:
            return None

    def __iter__(self):
        return self._pirates.__iter__()

    def __repr__(self):
        return f"<Arena name={self.name} odds={self.odds} pirates={self.pirates}>"


class Arenas:
    __slots__ = ("_arenas",)

    def __init__(self, nfc: NeoFoodClub):
        self._arenas = [
            Arena(nfc=nfc, arena_id=idx, pirate_ids=a)
            for idx, a in enumerate(nfc._data["pirates"])
        ]

    def get_pirate_by_id(self, pirate_id: PirateID) -> Pirate:
        for p in self.all_pirates:
            if p.id == pirate_id:
                return p

    def get_pirates_by_id(self, *pirate_ids: Sequence[PirateID]) -> List[Pirate]:
        return [p for p in self.all_pirates if p.id in pirate_ids]

    @property
    def all_pirates(self) -> List[Pirate]:
        pirates = []
        for a in self._arenas:
            for p in a.pirates:
                pirates.append(p)
        return pirates

    def get_pirates_from_binary(self, binary: int) -> List[Pirate]:
        return [
            self._arenas[arena][index - 1]
            for arena, index in enumerate(NFCMath.binary_to_indices(binary))
            if index > 0
        ]

    @property
    def pirates(self) -> List[List[Pirate]]:
        return [arena.pirates for arena in self._arenas]

    @property
    def best(self) -> List[Arena]:
        return sorted(self._arenas, key=lambda a: a.odds)

    @property
    def pirate_ids(self) -> List[List[int]]:
        return [arena.ids for arena in self._arenas]

    @property
    def positives(self) -> List[Arena]:
        return sorted([a for a in self._arenas if a.positive], key=lambda _a: _a.odds)

    def __iter__(self):
        yield from self._arenas

    def __repr__(self):
        return f"<Arenas {self._arenas!r}>"
