from typing import TypedDict, List, Literal, Optional


FoodID = Literal[tuple(range(1, 41))]
PirateID = Literal[tuple(range(1, 21))]
ValidOdds = Literal[tuple(range(1, 14))]
ValidIndex = Literal[tuple(range(5))]


class OddsChange(TypedDict):
    arena: ValidIndex
    pirate: PirateID
    old: ValidOdds
    new: ValidOdds
    t: str


class RoundData(TypedDict):
    pirates: List[List[PirateID]]
    openingOdds: List[List[ValidOdds]]
    currentOdds: List[List[ValidOdds]]
    changes: List[OddsChange]
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
