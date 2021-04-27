from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from .food_adjustments import NEGATIVE_FOOD, POSITIVE_FOOD
import neofoodclub.math as NFCMath


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
    @property
    def name(self):
        return PIRATE_NAMES[self.id]

    @property
    def image(self):
        return f"http://images.neopets.com/pirates/fc/fc_pirate_{self.id}.gif"


class PartialPirate(PirateMixin):
    def __init__(self, _id: int):
        self._id = _id

    @property
    def id(self) -> int:
        return self._id

    def __repr__(self):
        return f"<NaivePirate name={self.name}>"


class Pirate(PirateMixin):
    __slots__ = (
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
        self._id = id
        self._arena = arena
        self._index = index
        self._odds: int = nfc._data["customOdds"][arena][index]
        self._opening_odds: int = nfc._data["openingOdds"][arena][index]
        self._std: float = nfc._stds[arena][index]
        self._er: float = self.std * self.odds
        self._fa = None

        if "foods" in nfc._data:
            foods = nfc._data["foods"][arena]
            self._fa = sum(-NEGATIVE_FOOD[id][f] + POSITIVE_FOOD[id][f] for f in foods)

    @property
    def id(self) -> int:
        return self._id

    @property
    def arena(self) -> int:
        return self._arena

    @property
    def index(self) -> int:
        return self._index

    @property
    def std(self) -> float:
        return self._std

    @property
    def odds(self) -> int:
        return self._odds

    @property
    def er(self) -> float:
        return self._er

    @property
    def fa(self) -> Optional[int]:
        return self._fa

    @property
    def opening_odds(self) -> int:
        return self._opening_odds

    @property
    def binary(self) -> int:
        return NFCMath.pirate_binary(self._index, self._arena)

    def __int__(self):
        return NFCMath.pirate_binary(self._index, self._arena)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and int(self) == int(other)

    def __repr__(self):
        attrs = [
            ("name", self.name),
            ("arena", self.arena),
            ("index", self.index),
            ("odds", self.odds),
            ("fa", self.fa),
            ("opening_odds", self.opening_odds),
            ("int", hex(self.binary)),
        ]
        joined = " ".join("%s=%r" % t for t in attrs)
        return f"<Pirate {joined}>"
