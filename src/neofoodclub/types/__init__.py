from typing import List, Optional, TypedDict

from typing_extensions import NotRequired, Required


class OddsChangeDict(TypedDict):
    arena: int
    pirate: int
    old: int
    new: int
    t: str


class RoundData(TypedDict, total=False):
    pirates: Required[List[List[int]]]
    openingOdds: Required[List[List[int]]]
    currentOdds: Required[List[List[int]]]
    customOdds: NotRequired[List[List[int]]]  # this is used internally ONLY
    changes: Required[List[OddsChangeDict]]
    round: Required[int]
    start: Required[str]
    timestamp: Required[str]
    lastChange: Required[Optional[str]]
    winners: Required[Optional[List[int]]]
    foods: NotRequired[Optional[List[List[int]]]]


class BetOdds(TypedDict):
    value: int
    probability: float
    cumulative: float
    tail: float
