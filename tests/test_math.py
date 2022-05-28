from typing import Sequence

import pytest

from neofoodclub.errors import InvalidData
from neofoodclub.math import (
    amounts_hash_to_bet_amounts_numba,
    bets_hash_to_bets,
    bets_hash_to_bets_count,
    binary_to_indices_numba,
    make_probabilities,
)


@pytest.mark.parametrize(
    "bet_binary,expected",
    [
        (0x88888, [1, 1, 1, 1, 1]),
        (0x44444, [2, 2, 2, 2, 2]),
        (0x22222, [3, 3, 3, 3, 3]),
        (0x11111, [4, 4, 4, 4, 4]),
        (0x00000, [0, 0, 0, 0, 0]),
    ],
)
def test_binary_to_indices_numba(bet_binary: int, expected: Sequence[int]):
    assert expected == binary_to_indices_numba(bet_binary)


@pytest.mark.parametrize(
    "amount_hash,expected",
    [
        ("CXSCXSCXSCXSCXSCXSCXSCXSCXSCXS", [8000] * 10),
        ("BAQBAQBAQBAQBAQBAQBAQBAQBAQBAQ", [4098] * 10),
    ],
)
def test_amounts_hash_to_bet_amounts_numba(amount_hash: str, expected: Sequence[int]):
    assert expected == amounts_hash_to_bet_amounts_numba(amount_hash)


@pytest.mark.parametrize(
    "bets_hash,expected",
    [
        ("", 0),
        ("f", 1),
        ("faa", 1),
        ("ltqvqwgimhqtvrnywrwvijwnn", 10),
        ("ltqvqwgimhqtvrnywrwvijwnnxgslqmrylolnk", 15),
    ],
)
def test_bets_hash_to_bets_count(bets_hash: str, expected: int):
    assert expected == bets_hash_to_bets_count(bets_hash)


@pytest.mark.parametrize(
    "bets_hash",
    [
        "",  # zero bets
        "faafaafaafaafaafaafaafaafaafaafaafaafaafaafaafaa",  # 16 bets
    ],
)
def test_bets_hash_to_bets_invalid(bets_hash: str):
    with pytest.raises(InvalidData):
        bets_hash_to_bets(bets_hash)


@pytest.mark.parametrize(
    "bets_hash,expected",
    [
        ("faa", 1),
        ("faafaa", 2),
        ("faafaafaafaafaafaafaafaafaafaafaafaafaafaafaa", 15),
    ],
)
def test_bets_hash_to_bets_(bets_hash: str, expected: int):
    assert expected == len(bets_hash_to_bets(bets_hash))


def test_make_probabilities():
    # this is more for code coverage purposes, to hit the `if std_total == 1: break`
    # line in the make_probabilities method
    make_probabilities(
        [
            [1, 11, 4, 2, 3],
            [1, 12, 8, 5, 2],
            [1, 11, 13, 2, 2],
            [1, 2, 13, 13, 11],
            [1, 5, 11, 7, 2],
        ]
    )
    assert True
