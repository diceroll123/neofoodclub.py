import functools
import itertools
from string import ascii_lowercase, ascii_uppercase
from typing import Tuple, Dict, Optional, List

from numba import njit

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


@functools.lru_cache(maxsize=25)
def pirate_binary(index: int, arena: int) -> int:
    # binary position of the pirate in its arena, it's just a 1 with 19 zeros surrounding it
    # this assumes the index is actually index+1 because of odds etc starting with a 1 in the 0th index
    return 1 << (19 - (index - 1 + arena * 4))


@functools.lru_cache(maxsize=3125)
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
    # TODO: look into numba-fying
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
