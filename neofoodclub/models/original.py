from __future__ import annotations

from typing import TYPE_CHECKING

from neofoodclub.models import BaseModel
from neofoodclub.neofoodclub import make_probabilities

if TYPE_CHECKING:
    from neofoodclub import NeoFoodClub


class OriginalModel(BaseModel):
    __slots__ = ("probabilities",)

    def __init__(self, nfc: NeoFoodClub) -> None:
        self.probabilities = tuple(
            tuple(row)
            for row in make_probabilities(
                tuple(tuple(x) for x in nfc._data["openingOdds"]),
            )
        )
