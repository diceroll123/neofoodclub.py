from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, DefaultDict


# this is just a convoluted way of pre-allocating food adjustment values
class FA(DefaultDict[int, int]):
    def __new__(
        cls,
        *,
        one: tuple[int, ...] | None = None,
        two: tuple[int, ...] | None = None,
    ) -> DefaultDict[int, int]:
        data: dict[int, int] = {}

        for fa_value, values in zip((1, 2), (one, two)):
            for food_id in values or ():
                data[food_id] = fa_value

        return defaultdict(int, data)

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            one: tuple[int, ...] | None = None,
            two: tuple[int, ...] | None = None,
        ) -> None:
            ...


# the keys are the pirate IDs
POSITIVE_FOOD: dict[int, dict[int, int]] = {
    1: FA(one=(4, 6, 7, 8, 10, 25), two=(1, 12, 33)),
    2: FA(one=(1, 4, 5, 6, 7, 8, 10, 12, 13, 33, 35, 36)),
    3: FA(one=(14, 15, 16, 17, 18, 19, 20, 21, 22, 28, 32, 34, 37, 40)),
    4: FA(one=(3, 11, 17, 25, 28, 39, 40)),
    5: FA(one=(18, 23, 24, 29, 31, 38, 39)),
    6: FA(one=(10, 26, 27, 34)),
    7: FA(one=(14, 15, 16, 23, 24, 28, 31, 32, 38)),
    8: FA(one=(14, 15, 16, 20, 21, 22, 23, 24, 28, 31, 32, 37, 38)),
    9: FA(one=(17, 18, 19, 34, 40)),
    10: FA(one=(8, 9, 29, 32)),
    11: FA(one=(17, 18, 19, 20, 21, 22, 34, 37, 40)),
    12: FA(one=(1, 4, 6, 7, 8, 10, 12, 20, 21, 22, 33, 37)),
    13: FA(one=(1, 4, 6, 7, 8, 10, 12, 33)),
    14: FA(one=(2, 11, 18, 19, 23, 24, 26, 27, 29, 30, 34)),
    15: FA(one=(1, 4, 6, 7, 8, 10, 12, 33)),
    16: FA(one=(1, 4, 6, 7, 8, 12, 26, 27, 33, 34), two=(10,)),
    17: FA(one=(3, 11, 18, 19, 25, 28, 34, 39), two=(17, 40)),
    18: FA(one=(2, 11, 18, 19, 23, 24, 26, 27, 29, 30, 34)),
    19: FA(one=(14, 15, 16, 28, 32)),
    20: FA(one=(2, 18, 26, 27, 30, 34)),
}

NEGATIVE_FOOD: dict[int, dict[int, int]] = {
    1: FA(one=(14, 15, 16, 28, 32)),
    2: FA(one=(3, 11, 17, 25, 28, 39, 40)),
    3: FA(one=(11, 19, 23, 24, 29)),
    4: FA(one=(17, 18, 19, 34, 40)),
    5: FA(one=(8, 9, 29, 32)),
    6: FA(one=(23, 24, 31, 38)),
    7: FA(one=(10, 26, 27, 34)),
    8: FA(one=(1, 4, 6, 7, 8, 10, 12, 33)),
    9: FA(one=(5, 13, 35, 36)),
    10: FA(one=(11, 19, 23, 24, 29)),
    11: FA(one=(1, 12, 25, 33)),
    12: FA(one=(8, 9, 29, 32)),
    13: FA(one=(18, 23, 24, 29, 31, 38, 39)),
    14: FA(one=(1, 12, 25, 33)),
    15: FA(one=(20, 21, 22, 37)),
    16: FA(one=(14, 15, 16, 28, 32)),
    17: FA(one=(23, 24, 31, 38)),
    18: FA(one=(18, 23, 24, 29, 31, 38, 39)),
    19: FA(one=(2, 18, 26, 27, 30, 34)),
    20: FA(one=(5, 13, 35, 36)),
}
