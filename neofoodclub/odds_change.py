from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterator

import dateutil.parser
from dateutil.tz import UTC

from neofoodclub.arenas import ARENA_NAMES
from neofoodclub.pirates import PartialPirate

if TYPE_CHECKING:
    import datetime

    from neofoodclub.types import OddsChangeDict

__all__ = ("OddsChange",)


class OddsChange:
    """Represents a single change of a pirate's odds.
    This class is not to be constructed manually.
    """

    __slots__ = (
        "_index",
        "_data",
        "_round_data",
    )

    def __init__(
        self, *, index: int, data: OddsChangeDict, round_data: dict[str, Any]
    ) -> None:
        self._index = index
        self._data = data  # to check against each other
        self._round_data = round_data

    @property
    def data(self) -> OddsChangeDict:
        """:class:`OddsChangeDict`: Returns the data that makes up this single change of odds."""
        return self._data

    @property
    def index(self) -> int:
        """:class:`int`: Returns the zero-based index of this change, in chronological order."""
        return self._index

    @property
    def raw_timestamp(self) -> str:
        """:class:`str`: Returns the string of the timestamp that this change occurred."""
        return self._data["t"]

    @property
    def timestamp(self) -> datetime.datetime:
        """:class:`datetime.datetime`: Returns the datetime object of the timestamp that this change occurred."""
        return dateutil.parser.parse(self.raw_timestamp).astimezone(UTC)

    @property
    def old(self) -> int:
        """:class:`int`: Returns the previous odds before this change occurred."""
        return self._data["old"]

    @property
    def new(self) -> int:
        """:class:`int`: Returns the current odds after this change occurred."""
        return self._data["new"]

    @property
    def pirate_index(self) -> int:
        """:class:`int`: Returns the one-based index of the pirate's position in the arena."""
        return self._data["pirate"]

    @property
    def pirate(self) -> PartialPirate:
        """:class:`PartialPirate`: Returns a partial pirate object, which is a convenience object storing the pirate's ID."""
        return PartialPirate(
            self._round_data["pirates"][self.arena_index][self.pirate_index - 1]
        )

    @property
    def arena_index(self) -> int:
        """:class:`int`: Returns the zero-based index of the arena's position in the round data."""
        return self._data["arena"]

    @property
    def arena(self) -> str:
        """:class:`str`: Returns name of the arena that this change occurred in."""
        return ARENA_NAMES[self.arena_index]

    def __repr__(self) -> str:
        return f"<OddsChange arena={self.arena_index!r} index={self.index!r} pirate={self.pirate!r} old={self.old!r} new={self.new!r} timestamp={self.timestamp!r}>"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self._data == other.data

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        yield from self._data.items()

    def __hash__(self) -> int:
        return hash(repr(self))
