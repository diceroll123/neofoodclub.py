from __future__ import annotations

from typing import TYPE_CHECKING, Generator, Iterator, Sequence

from . import math
from .pirates import Pirate

if TYPE_CHECKING:
    from .nfc import NeoFoodClub

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
        "_pirate_ids",
        "_pirates",
        "_id",
        "_odds",
    )

    def __init__(
        self, *, nfc: NeoFoodClub, arena_id: int, pirate_ids: Sequence[int]
    ) -> None:
        self.nfc: NeoFoodClub = nfc
        self._id = arena_id
        self._pirate_ids = tuple(pirate_ids)
        self._pirates = tuple(  # adding 1 to index because the original list has a length of 4, but everything else has 5
            Pirate(nfc=nfc, id=p_id, arena=arena_id, index=idx + 1)
            for idx, p_id in enumerate(pirate_ids)
        )
        self._odds = sum(1 / p._odds for p in self._pirates)

    @property
    def id(self) -> int:
        """:class:`int`: Alias for Arena.index."""
        return self.index

    @property
    def index(self) -> int:
        """:class:`int`: The arena's zero-based index, correlating to its place in the list ["Shipwreck", "Lagoon", "Treasure", "Hidden", "Harpoon"]."""
        return self._id

    @property
    def name(self) -> str:
        """:class:`str`: The name of this arena, can be one of ["Shipwreck", "Lagoon", "Treasure", "Hidden", "Harpoon"]."""
        return ARENA_NAMES[self._id]

    @property
    def best(self) -> list[Pirate]:
        """List[:class:`Pirate`]: Returns a list of the pirates in this arena sorted from least to greatest odds."""
        return sorted(self._pirates, key=lambda a: a._odds)

    @property
    def ids(self) -> tuple[int, ...]:
        """Tuple[:class:`int`]: Returns a list of the IDs of the pirates in this arena."""
        return self._pirate_ids

    @property
    def odds(self) -> float:
        """:class:`float`: Returns the odds of this arena, which is equal to the sum of (1 / odds) of each pirate."""
        # do note that arena odds are not the same as pirate odds
        return self._odds

    @property
    def ratio(self) -> float:
        """:class:`float`: Returns the ratio of this arena, which is `1 / Arena.odds - 1`."""
        return 1 / self._odds - 1

    @property
    def pirates(self) -> tuple[Pirate, ...]:
        """Tuple[:class:`Pirate`]: Returns a tuple of the pirates in this arena."""
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
    def foods(self) -> tuple[int, ...]:
        """Tuple[:class:`int`]: Returns a list of the IDs of the foods in this arena, where applicable."""
        return tuple(foods[self._id]) if (foods := self.nfc.foods) else ()

    def __getitem__(self, item: int) -> Pirate:
        return self._pirates[item]

    def __iter__(self) -> Iterator[Pirate]:
        return self._pirates.__iter__()

    def __repr__(self) -> str:
        return (
            f"<Arena name={self.name!r} odds={self._odds!r} pirates={self.pirates!r}>"
        )


class Arenas:
    """A container object for all of the arenas for a given round of Food Club.
    This class is not to be constructed manually.
    """

    __slots__ = ("_arenas",)

    def __init__(self, nfc: NeoFoodClub) -> None:
        self._arenas = tuple(
            Arena(nfc=nfc, arena_id=idx, pirate_ids=a)
            for idx, a in enumerate(nfc._data["pirates"])
        )

    def get_pirate_by_id(self, pirate_id: int, /) -> Pirate:
        """:class:`Pirate`: Returns a single pirate where their ID matches pirate_id."""
        for p in self.all_pirates:
            if p.id == pirate_id:
                return p
        raise ValueError(
            f"Could not find pirate with ID {pirate_id}. Only 1 through 20 are valid."
        )

    def get_pirates_by_id(self, *pirate_ids: int) -> tuple[Pirate, ...]:
        """Tuple[:class:`Pirate`]: Returns a list of pirates where their IDs match IDs in pirate_ids."""
        return tuple(p for p in self.all_pirates if p.id in pirate_ids)

    @property
    def all_pirates(self) -> tuple[Pirate, ...]:
        """Tuple[:class:`Pirate`]: Returns a flat list of all pirates in arena-order."""
        pirates: tuple[Pirate, ...] = ()
        for a in self._arenas:
            pirates += a.pirates
        return pirates

    def get_pirates_from_binary(self, binary: int, /) -> tuple[Pirate, ...]:
        """Tuple[:class:`Pirate`]: Return a list of pirates based on their bet-binary representation.

        Note: This will only provide the left-most filled pirate per-arena.
        """
        return tuple(
            self._arenas[arena][index - 1]
            for arena, index in enumerate(math.binary_to_indices(binary))
            if index > 0
        )

    @property
    def pirates(self) -> tuple[tuple[Pirate, ...], ...]:
        """Tuple[Tuple[:class:`Pirate`]]: Returns a nested tuple of all pirates in arena-order."""
        return tuple(arena.pirates for arena in self._arenas)

    @property
    def best(self) -> list[Arena]:
        """List[:class:`Arena`]: Returns a list of the arenas sorted from least to greatest odds."""
        return sorted(self._arenas, key=lambda a: a._odds)

    @property
    def pirate_ids(self) -> tuple[tuple[int, ...], ...]:
        """Tuple[Tuple[:class:`int`]]: Returns a nested tuple of all pirate IDs in arena-order."""
        return tuple(arena.ids for arena in self._arenas)

    @property
    def positives(self) -> list[Arena]:
        """List[:class:`Arena`]: Returns a list of positive arenas sorted from least to greatest odds."""
        return sorted((a for a in self._arenas if a.positive), key=lambda _a: _a._odds)

    def get_arena(self, arena_id: int, /) -> Arena:
        return self._arenas[arena_id]

    def __getitem__(self, key: int) -> Arena:
        return self._arenas[key]

    def __iter__(self) -> Generator[Arena, None, None]:
        yield from self._arenas

    def __repr__(self) -> str:
        return f"<Arenas {self._arenas!r}>"
