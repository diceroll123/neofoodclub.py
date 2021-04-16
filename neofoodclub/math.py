import functools
import itertools
from collections import defaultdict
from string import ascii_lowercase, ascii_uppercase
from typing import Tuple, Dict, Optional, List

from numba import njit
from .types import ValidOdds, ValidIndex, BetOdds

# at least for now, we won't be exposing the numba methods.
__all__ = (
    "precompile",
    "pirate_binary",
    "pirates_binary",
    "binary_to_indices",
    "bet_amounts_to_string",
    "bet_string_to_bet_amounts",
    "bet_string_to_bet_indices",
    "bet_string_to_bets_amount",
    "bet_string_to_bets",
    "bet_url_value",
    "make_probabilities",
    "get_bet_odds_from_bets",
)


BET_AMOUNT_MIN = 50

BET_AMOUNT_MAX = 70304
# this fixed number is the max that NeoFoodClub can encode,
# given the current bet (and bet amount) encoding specification


def precompile():
    # run the numba methods to compile, and fill some caches so they're speedier

    bet_string_to_bet_amounts("aaa")

    for a in range(5):
        for b in range(5):
            for c in range(5):
                for d in range(5):
                    for e in range(5):
                        bet_binary = pirates_binary((a, b, c, d, e))
                        binary_to_indices(bet_binary)


@functools.lru_cache(maxsize=None)
def pirate_binary(index: int, arena: int) -> int:
    # binary position of the pirate in its arena, it's just a 1 with 19 zeros surrounding it
    # this assumes the index is actually index+1 because of odds etc starting with a 1 in the 0th index
    if index == 0:
        return 0
    return 1 << (19 - (index - 1 + arena * 4))


@functools.lru_cache(maxsize=None)
def pirates_binary(bet_indices: Tuple[int, ...]) -> int:
    # the inverse of binary_to_indices
    # turns (1, 2, 3, 4, 2) (for example) into 0b10000100001000010100, a bet-binary compatible number
    return sum(pirate_binary(index, arena) for arena, index in enumerate(bet_indices))


@njit()
def binary_to_indices_numba(bet_binary: int) -> List[int]:
    # thanks @mikeshardmind
    # the inverse of pirates_binary
    ret = [1 for _ in range(0)]
    for mask in (0xF0000, 0xF000, 0xF00, 0xF0, 0xF):
        val = mask & bet_binary
        if val:
            # bit length intentionally offset here
            # numba doesn't implement .bit_length for int
            bit_length, v2 = -1, val
            while v2:
                v2 >>= 1
                bit_length += 1
            val = 4 - (bit_length % 4)
        ret.append(val)
    return ret


@functools.lru_cache(maxsize=3125)
def binary_to_indices(bet_binary: int) -> Tuple[int, ...]:
    # convenience method to cache the list as a tuple because i don't think Numba can *do* tuples.
    return tuple(binary_to_indices_numba(bet_binary))


def bet_amounts_to_string(bet_amounts: Dict) -> str:
    # TODO: look into numba-fying
    letters = ""
    for idx, value in bet_amounts.items():
        e = ""
        letter = int(value) % BET_AMOUNT_MAX + BET_AMOUNT_MAX
        for _ in range(3):
            e = (ascii_lowercase + ascii_uppercase)[letter % 52] + e
            letter //= 52
        letters += e

    return letters


@njit()
def bet_string_to_bet_amounts_numba(bet_string: str) -> List[Optional[int]]:
    nums: List[Optional[int]] = []
    chunked = [bet_string[i : i + 3] for i in range(0, len(bet_string), 3)]

    for p in chunked:
        e = 0
        for n in p:
            e *= 52
            e += (ascii_lowercase + ascii_uppercase).index(n)

        value = e - BET_AMOUNT_MAX
        if value < BET_AMOUNT_MIN:
            nums.append(None)
        else:
            nums.append(value)

    return nums


@functools.lru_cache
def bet_string_to_bet_amounts(bet_string: str) -> Tuple[Optional[int], ...]:
    # convenience method to cache the list as a tuple because i don't think Numba can *do* tuples.
    return tuple(bet_string_to_bet_amounts_numba(bet_string))


@functools.lru_cache(maxsize=256)
def bet_string_to_bet_indices(bet_string: str) -> Tuple[Tuple[int, ...], ...]:
    # TODO: look into numba-fying (tried once now, it was about 3x slower to get the same result uncached)
    indices = [ord(letter) - 97 for letter in bet_string]
    s = itertools.chain.from_iterable((e // 5, e % 5) for e in indices)
    # https://docs.python.org/3/library/itertools.html#itertools-recipes (see "grouper" recipe)
    return tuple(
        bet for bet in itertools.zip_longest(*[iter(s)] * 5, fillvalue=0) if any(bet)
    )


def bet_string_to_bets_amount(bet_string: str) -> int:
    # the amount of bets in the set, that is
    return len(bet_string_to_bet_indices(bet_string))


def bet_string_to_bets(bet_string: str) -> Dict:
    bets = bet_string_to_bet_indices(bet_string)

    bet_length = len(bets)
    if bet_length not in range(1, 16):
        # currently support 15 bets still for reverse-compatibility i guess
        raise ValueError

    return dict(zip(range(1, bet_length + 1), bets))


def bet_url_value(bet_indices: Dict) -> str:
    # TODO: look into numba-fying
    flat = itertools.chain.from_iterable(bet_indices.values())
    return "".join(
        ascii_lowercase[multiplier * 5 + adder]
        for multiplier, adder in itertools.zip_longest(*[iter(flat)] * 2, fillvalue=0)
    )


def make_probabilities(opening_odds: List[List[ValidOdds]]) -> List[List[float]]:
    # TODO: look into numba-fying, so far any attempts have been *SLOWER*

    _min = [
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
    ]

    _max = [
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
    ]

    _std = [
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
    ]

    # turns out we only use _std values in the python implementation of NFC
    # keeping the _used math to avoid confusion between NFC impls
    # _used = [
    #     [1.0, 0.0, 0.0, 0.0, 0.0],
    #     [1.0, 0.0, 0.0, 0.0, 0.0],
    #     [1.0, 0.0, 0.0, 0.0, 0.0],
    #     [1.0, 0.0, 0.0, 0.0, 0.0],
    #     [1.0, 0.0, 0.0, 0.0, 0.0],
    # ]

    for e in range(5):

        min_prob = 0.0
        max_prob = 0.0
        for r in range(1, 5):
            pirate_odd = opening_odds[e][r]
            if pirate_odd == 13:
                _min[e][r] = 0
                _max[e][r] = 1 / 13
            elif pirate_odd == 2:
                _min[e][r] = 1 / 3
                _max[e][r] = 1
            else:
                _min[e][r] = 1 / (1 + pirate_odd)
                _max[e][r] = 1 / pirate_odd
            min_prob += _min[e][r]
            max_prob += _max[e][r]

        for r in range(1, 5):
            min_original = _min[e][r]
            max_original = _max[e][r]

            _min[e][r] = max(min_original, 1 + max_original - max_prob)
            _max[e][r] = min(max_original, 1 + min_original - min_prob)
            _std[e][r] = (
                0.05 if opening_odds[e][r] == 13 else (_min[e][r] + _max[e][r]) / 2
            )

        for rectify_level in range(2, 13):
            rectify_count = 0
            std_total = 0.0
            rectify_value = 0.0
            max_rectify_value = 1.0
            for r in range(1, 5):
                std_total += _std[e][r]
                if opening_odds[e][r] <= rectify_level:
                    rectify_count += 1
                    rectify_value += _std[e][r] - _min[e][r]
                    max_rectify_value = min(
                        [
                            max_rectify_value,
                            _max[e][r] - _min[e][r],
                        ]
                    )

            if std_total == 1:
                break

            if not (
                std_total - rectify_value > 1
                or rectify_count == 0
                or max_rectify_value * rectify_count < rectify_value + 1 - std_total
            ):
                rectify_value += 1 - std_total
                rectify_value /= rectify_count
                for r in range(1, 5):
                    if opening_odds[e][r] <= rectify_level:
                        _std[e][r] = _min[e][r] + rectify_value
                break

    #     return_sum = 0.0
    #     for r in range(1, 5):
    #         _used[e][r] = _std[e][r]
    #         return_sum += _used[e][r]
    #
    #     for r in range(1, 5):
    #         _used[e][r] /= return_sum
    #
    # return dict(min=_min, max=_max, std=_std, used=_used)

    return _std


def get_bet_odds_from_bets(
    bets: List[List[ValidIndex]],
    bet_odds: List[ValidOdds],
    probabilities: List[List[float]],
) -> List[BetOdds]:
    # TODO: look into numba-fying

    # ib is a binary format to represent bets.
    # It works on 20 bits (because there are 20 pirates).
    # Each of the bits of an ib represents whether it accepts some pirate. (whether the bet can win if this pirate wins)
    # From most significant to least significant bits, the pirates are in the usual arena-by-arena order.
    # This binary format allows some easy operations:
    # ib1&ib2 accepts the pirates that both ib1 and ib2 accepts. The winning combinations of ib1&ib2 is the intersection of the winning combinations of ib1 and ib2.
    # ib1|ib2 accepts the pirates that ib1 or ib2 accepts. The winning combinations of ib1&ib2 is BIGGER or equal to the union of the winning combinations of ib1 and ib2.

    # bit_masks[i] will accept pirates from arena i and only them. bit_masks[4] == 0b1111, bit_masks[3] == 0b11110000, etc...

    # all_ib will accept all pirates. all_ib = 0b11111111111111111111 (20 '1's)
    all_ib = 0xFFFFF

    # pir_ib[i] will accept pirates of index i (from 0 to 3) pir_ib[0] = 0b10001000100010001000, pir_ib[1] = 0b01000100010001000100, pir_ib[2] = 0b00100010001000100010, pir_ib[3] = 0b00010001000100010001
    pir_ib = [0x88888, 0x44444, 0x22222, 0x11111]

    bit_masks = (0xF0000, 0xF000, 0xF00, 0xF0, 0xF)

    # checks if there are possible winning combinations for ib
    def ib_doable(_ib) -> bool:
        return (
            _ib & bit_masks[0]
            and _ib & bit_masks[1]
            and _ib & bit_masks[2]
            and _ib & bit_masks[3]
            and _ib & bit_masks[4]
        )

    # expand_ib_object takes an ibObj and returns an ibObj.
    # The returned bet set "res" satisfies the following properties:
    # - for all possible winning combination it has the same value as the old set
    # - two different bets in "res" will have 0 common accepted winning combinations
    # - all winning combinations are accepted by a bet in "res" (giving the value 0 to combinations that busts)
    # It's done so that the probability distribution becomes easy to compute.
    def expand_ib_object(ib_obj) -> Dict[int, int]:
        res = {all_ib: 0}
        for ib_bet, winnings in sorted(ib_obj.items()):
            for ib_key in list(res.keys()):
                com = ib_bet & ib_key
                if ib_doable(com):
                    val_key = res.pop(ib_key)
                    res[com] = winnings + val_key
                    for _ar in bit_masks:
                        tst = ib_key ^ (com & _ar)
                        if ib_doable(tst):
                            res[tst] = val_key
                            ib_key = (ib_key & ~_ar) | (com & _ar)
        return res

    # computes the probability that the winning combination is accepted by ib
    def ib_prob(_ib: int) -> float:
        total_prob = 1.0
        for _i in range(5):
            ar_prob = 0.0
            for _j in range(4):
                if _ib & bit_masks[_i] & pir_ib[_j]:
                    ar_prob += probabilities[_i][_j + 1]
            total_prob *= ar_prob
        return total_prob

    # Takes a bet set in ibObj satisfying the following condition:
    # - two different bets in the bet set will have 0 common accepted winning combinations
    # and computes its win table.
    def compute_win_table(ib_exp_obj: Dict[int, int]) -> List[BetOdds]:
        win_table: Dict[int, float] = defaultdict(float)
        for k, v in ib_exp_obj.items():
            win_table[v] += ib_prob(k)

        sorted_e: List[BetOdds] = sorted(
            [
                {
                    "value": value,
                    "probability": probability,
                    "cumulative": 0.0,
                    "tail": 1.0,
                }
                for value, probability in win_table.items()
            ],
            key=lambda ee: ee["value"],
        )

        cumulative = 0.0
        tail = 1.0
        for _a in range(len(sorted_e)):
            cumulative += sorted_e[_a]["probability"]
            sorted_e[_a]["cumulative"] = cumulative
            sorted_e[_a]["tail"] = tail
            tail -= sorted_e[_a]["probability"]

        return sorted_e

    convert_pir_ib = [all_ib] + pir_ib
    bets_to_ib: Dict[int, int] = defaultdict(int)
    for key, bet_value in enumerate(bets):
        ib = 0
        for _x in range(5):
            # this adds pirates meant by bet[i] to the pirates accepted by ib.
            ib |= convert_pir_ib[bet_value[_x]] & bit_masks[_x]
        bets_to_ib[ib] += bet_odds[key]

    return compute_win_table(expand_ib_object(bets_to_ib))
