from typing import List, Literal, Optional, TypedDict


class OddsChangeDict(TypedDict):
    arena: int
    pirate: int
    old: int
    new: int
    t: str


class RoundData(TypedDict, total=False):
    pirates: List[List[int]]
    openingOdds: List[List[int]]
    currentOdds: List[List[int]]
    customOdds: List[List[int]]  # this is used internally ONLY
    changes: List[OddsChangeDict]
    round: int
    start: str
    timestamp: str
    lastChange: Optional[str]
    winners: Optional[List[int]]
    foods: Optional[List[List[int]]]


class BetOdds(TypedDict):
    value: int
    probability: float
    cumulative: float
    tail: float
