from __future__ import annotations

from typing import TYPE_CHECKING

from neofoodclub.models import BaseModel

if TYPE_CHECKING:
    from neofoodclub.nfc import NeoFoodClub

from neofoodclub import math


class OriginalModel(BaseModel):
    __slots__ = ("probabilities",)

    def __init__(self, nfc: NeoFoodClub) -> None:
        self.probabilities = tuple(
            tuple(row)
            for row in math.make_probabilities(
                tuple(tuple(x) for x in nfc._data["openingOdds"]),
            )
        )
