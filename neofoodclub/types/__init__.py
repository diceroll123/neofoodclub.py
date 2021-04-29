from typing import List, Literal, Optional, TypedDict

# fmt: off
FoodID = Literal[
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
    31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
]

PirateID = Literal[
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20
]

ValidOdds = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

ValidIndex = Literal[0, 1, 2, 3, 4]
# fmt: on


class OddsChangeDict(TypedDict):
    arena: ValidIndex
    pirate: PirateID
    old: ValidOdds
    new: ValidOdds
    t: str


class RoundData(TypedDict, total=False):
    pirates: List[List[PirateID]]
    openingOdds: List[List[ValidOdds]]
    currentOdds: List[List[ValidOdds]]
    customOdds: List[List[ValidOdds]]  # this is used internally ONLY
    changes: List[OddsChangeDict]
    round: int
    start: str
    timestamp: str
    lastChange: Optional[str]
    winners: Optional[List[ValidIndex]]
    foods: Optional[List[List[FoodID]]]


class BetOdds(TypedDict):
    value: int
    probability: float
    cumulative: float
    tail: float
