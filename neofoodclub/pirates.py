from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

from . import math
from .food_adjustments import NEGATIVE_FOOD, POSITIVE_FOOD

if TYPE_CHECKING:
    from .neofoodclub import NeoFoodClub

__all__ = (
    "Pirate",
    "PartialPirate",
    "PIRATE_NAMES",
)

PIRATE_NAMES = {
    1: "Dan",
    2: "Sproggie",
    3: "Orvinn",
    4: "Lucky",
    5: "Edmund",
    6: "Peg Leg",
    7: "Bonnie",
    8: "Puffo",
    9: "Stuff",
    10: "Squire",
    11: "Crossblades",
    12: "Stripey",
    13: "Ned",
    14: "Fairfax",
    15: "Gooblah",
    16: "Franchisco",
    17: "Federismo",
    18: "Blackbeard",
    19: "Buck",
    20: "Tailhook",
}


class PirateMixin:
    id: int

    @property
    def name(self):
        return PIRATE_NAMES[self.id]

    @property
    def image(self):
        return f"http://images.neopets.com/pirates/fc/fc_pirate_{self.id}.gif"


class PartialPirate(PirateMixin):
    """Represents a "partial" pirate that only has an ID.

    Attributes
    -----------
    id: :class:`int`
        The pirate's ID.
    name: :class:`str`
        The pirate's name.
    image: :class:`str`
        The pirates image.
    """

    def __init__(self, _id: int):
        self._id = _id

    @property
    def id(self) -> int:
        return self._id

    def __repr__(self):
        return f"<NaivePirate name={self.name}>"


class Pirate(PirateMixin):
    """Represents a single pirate.

    Attributes
    -----------
    name: :class:`str`
        The pirate's name.
    image: :class:`str`
        The pirates image.
    """

    __slots__ = (
        "nfc",
        "_id",
        "_arena",
        "_index",
        "_odds",
        "_opening_odds",
        "_std",
        "_er",
        "_fa",
    )

    def __init__(self, *, nfc: NeoFoodClub, id: int, arena: int, index: int):
        self.nfc = nfc
        self._id = id
        self._arena = arena
        self._index = index
        self._odds: int = nfc._data["customOdds"][arena][index]  # type: ignore
        self._opening_odds: int = nfc._data["openingOdds"][arena][index]
        if nfc._stds:
            self._std = nfc._stds[arena][index]
            self._er = self._std * self._odds
        else:
            self._std = None
            self._er = None
        self._fa = None

        if foods := nfc._data.get("foods", None):
            self._fa = sum(
                -NEGATIVE_FOOD[id][f] + POSITIVE_FOOD[id][f] for f in foods[arena]
            )

    @property
    def id(self) -> int:
        """:class:`int`: The pirate's ID."""
        return self._id

    @property
    def arena(self) -> int:
        """:class:`int`: The ID of the arena this pirate is in."""
        return self._arena

    @property
    def index(self) -> int:
        """:class:`int`: The pirate's index in the arena the pirate is in."""
        return self._index

    @property
    def std(self) -> Optional[float]:
        """Optional[:class:`float`]: The pirate's std probability. If this is None, the NeoFoodClub object has not been cached yet."""
        return self._std

    @property
    def odds(self) -> int:
        """:class:`int`: The pirate's current odds."""
        return self._odds

    @property
    def er(self) -> Optional[float]:
        """Optional[:class:`float`]: The pirate's expected ratio. This is equal to std * odds. If this is None, the NeoFoodClub object has not been cached yet."""
        return self._er

    @property
    def fa(self) -> Optional[int]:
        """Optional[:class:`int`]: The pirate's food adjustment. Can be None if no foods are found."""
        return self._fa

    @property
    def opening_odds(self) -> int:
        """:class:`int`: The pirate's opening odds."""
        return self._opening_odds

    @property
    def binary(self) -> int:
        """:class:`int`: The pirate's bet-binary representation."""
        return math.pirate_binary(self._index, self._arena)

    @property
    def positive_foods(self) -> List[int]:
        """List[:class:`int`]: Returns a list of the positive Food IDs for this pirate's arena that affect this pirate, where applicable."""
        if foods := self.nfc.foods:
            return [f for f in foods[self._arena] if POSITIVE_FOOD[self._id][f] != 0]
        return []

    @property
    def negative_foods(self) -> List[int]:
        """List[:class:`int`]: Returns a list of the negative Food IDs for this pirate's arena that affect this pirate, where applicable."""
        if foods := self.nfc.foods:
            return [f for f in foods[self._arena] if NEGATIVE_FOOD[self._id][f] != 0]
        return []

    def __int__(self) -> int:
        return math.pirate_binary(self._index, self._arena)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and int(self) == int(other)

    def __repr__(self):
        attrs = [
            ("name", self.name),
            ("arena", self.arena),
            ("index", self.index),
            ("odds", self.odds),
            ("fa", self.fa),
            ("opening_odds", self.opening_odds),
            ("binary", self.binary),
        ]
        joined = " ".join("%s=%r" % t for t in attrs)
        return f"<Pirate {joined}>"
