from typing import List

import pytest
from neofoodclub.errors import InvalidData
from neofoodclub.math import (
    amounts_hash_to_bet_amounts_numba,
    bets_hash_to_bets,
    bets_hash_to_bets_count,
    binary_to_indices_numba,
)


@pytest.mark.parametrize(
    "bet_binary,expected",
    [
        (0x88888, [1, 1, 1, 1, 1]),
        (0x11111, [4, 4, 4, 4, 4]),
        (0x00000, [0, 0, 0, 0, 0]),
    ],
)
def test_binary_to_indices_numba(bet_binary: int, expected: List[int]):
    assert expected == binary_to_indices_numba(bet_binary)


@pytest.mark.parametrize(
    "amount_hash,expected",
    [
        ("CXSCXSCXSCXSCXSCXSCXSCXSCXSCXS", [8000] * 10),
        ("BAQBAQBAQBAQBAQBAQBAQBAQBAQBAQ", [4098] * 10),
    ],
)
def test_amounts_hash_to_bet_amounts_numba(amount_hash: str, expected: List[int]):
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
