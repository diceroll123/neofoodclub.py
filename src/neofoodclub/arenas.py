from __future__ import annotations

from typing import TYPE_CHECKING, List, Sequence

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
    """Represents an arena for a given round of Food Club.
    This class is not to be constructed manually.
    """

    __slots__ = (
        "nfc",
        "_pirates",
        "_id",
        "_odds",
    )

    def __init__(
        self, *, nfc: NeoFoodClub, arena_id: ValidIndex, pirate_ids: Sequence[PirateID]
    ):
        self.nfc = nfc
        self._id = arena_id
        self._pirates = [  # adding 1 to index because the original list has a length of 4, but everything else has 5
            Pirate(nfc=nfc, id=p_id, arena=arena_id, index=idx + 1)
            for idx, p_id in enumerate(pirate_ids)
        ]
        self._odds = sum(1 / p._odds for p in self._pirates)  # type: ignore

    @property
    def id(self) -> int:
        """:class:`int`: The arena's zero-based ID, correlating to its place in the list ["Shipwreck", "Lagoon", "Treasure", "Hidden", "Harpoon"]"""
        return self._id

    @property
    def name(self) -> str:
        """:class:`str`: The name of this arena, can be one of ["Shipwreck", "Lagoon", "Treasure", "Hidden", "Harpoon"]"""
        return ARENA_NAMES[self._id]

    @property
    def best(self) -> List[Pirate]:
        """List[:class:`Pirate`]: Returns a list of the pirates in this arena sorted from least to greatest odds."""
        return sorted(self._pirates, key=lambda a: a._odds)  # type: ignore

    @property
    def ids(self) -> List[int]:
        """List[:class:`int`]: Returns a list of the IDs of the pirates in this arena."""
        return [p.id for p in self._pirates]

    @property
    def odds(self) -> float:
        """:class:`float`: Returns the odds of this arena, which is equal to the sum of (1 / odds) of each pirate."""
        # do note that arena odds are not the same as pirate odds
        return self._odds

    @property
    def ratio(self) -> float:
        """:class:`float`: Returns the ratio of this arena, which is `1 / Arena.odds - 1`"""
        return 1 / self._odds - 1

    @property
    def pirates(self) -> List[Pirate]:
        """List[:class:`Pirate`]: Returns a list of the pirates in this arena."""
        return self._pirates

    @property
    def positive(self) -> bool:
        """:class:`bool`: Returns whether or not `Arena.odds` is greater than 1."""
        return self._odds < 1

    @property
    def negative(self) -> bool:
        """:class:`bool`: Returns whether or not `Arena.odds` is less than 1."""
        return not self.positive

    @property
    def foods(self) -> List[int]:
        """List[:class:`int`]: Returns a list of the IDs of the foods in this arena, where applicable."""
        foods = self.nfc.foods
        if foods:
            return foods[self._id]
        return []

    def __getitem__(self, item: ValidIndex) -> Pirate:
        return self._pirates[item]

    def __iter__(self):
        return self._pirates.__iter__()

    def __repr__(self):
        return f"<Arena name={self.name} odds={self._odds} pirates={self.pirates}>"


class Arenas:
    """A container object for all of the arenas for a given round of Food Club.
    This class is not to be constructed manually.
    """

    __slots__ = ("_arenas",)

    def __init__(self, nfc: NeoFoodClub):
        self._arenas = [
            Arena(nfc=nfc, arena_id=idx, pirate_ids=a)  # type: ignore
            for idx, a in enumerate(nfc._data["pirates"])  # type: ignore
        ]

    def get_pirate_by_id(self, pirate_id: PirateID) -> Pirate:  # type: ignore
        """:class:`Pirate`: Returns a single pirate where their ID matches pirate_id."""
        for p in self.all_pirates:
            if p.id == pirate_id:
                return p

    def get_pirates_by_id(self, *pirate_ids: Sequence[PirateID]) -> List[Pirate]:
        """List[:class:`Pirate`]: Returns a list of pirates where their IDs match IDs in pirate_ids."""
        return [p for p in self.all_pirates if p.id in pirate_ids]

    @property
    def all_pirates(self) -> List[Pirate]:
        """List[:class:`Pirate`]: Returns a flat list of all pirates in arena-order."""
        pirates: List[Pirate] = []
        for a in self._arenas:
            pirates.extend(iter(a.pirates))
        return pirates

    def get_pirates_from_binary(self, binary: int) -> List[Pirate]:
        """List[:class:`Pirate`]: Return a list of pirates based on their bet-binary representation."""
        return [
            self._arenas[arena][index - 1]  # type: ignore
            for arena, index in enumerate(NFCMath.binary_to_indices(binary))
            if index > 0
        ]

    @property
    def pirates(self) -> List[List[Pirate]]:
        """List[List[:class:`Pirate`]]: Returns a nested list of all pirates in arena-order."""
        return [arena.pirates for arena in self._arenas]

    @property
    def best(self) -> List[Arena]:
        """List[:class:`Arena`]: Returns a list of the arenas sorted from least to greatest odds."""
        return sorted(self._arenas, key=lambda a: a._odds)  # type: ignore

    @property
    def pirate_ids(self) -> List[List[int]]:
        """List[List[:class:`int`]]: Returns a nested list of all pirate IDs in arena-order."""
        return [arena.ids for arena in self._arenas]

    @property
    def positives(self) -> List[Arena]:
        """List[:class:`Arena`]: Returns a list of positive arenas sorted from least to greatest odds."""
        return sorted([a for a in self._arenas if a.positive], key=lambda _a: _a._odds)  # type: ignore

    def get_arena(self, arena_id: ValidIndex) -> Arena:
        return self._arenas[arena_id]

    def __getitem__(self, key: int) -> Arena:
        return self._arenas[key]

    def __iter__(self):
        yield from self._arenas

    def __repr__(self):
        return f"<Arenas {self._arenas!r}>"
