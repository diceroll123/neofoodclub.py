from typing import Sequence

import pytest

from neofoodclub.math import (
    amounts_hash_to_bet_amounts,
    bet_amounts_to_amounts_hash,
    bets_hash_to_bets_count,
    binary_to_indices,
    make_probabilities,
)


@pytest.mark.parametrize(
    ("bet_binary", "expected"),
    [
        (0x84210, [1, 2, 3, 4, 0]),
        (0x88888, [1, 1, 1, 1, 1]),
        (0x44444, [2, 2, 2, 2, 2]),
        (0x22222, [3, 3, 3, 3, 3]),
        (0x11111, [4, 4, 4, 4, 4]),
        (0x00000, [0, 0, 0, 0, 0]),
    ],
)
def test_binary_to_indices(bet_binary: int, expected: Sequence[int]) -> None:
    assert expected == binary_to_indices(bet_binary)


@pytest.mark.parametrize(
    ("amount_hash", "expected"),
    [
        ("BAQBAQBAQBAQBAQBAQBAQBAQBAQBAQ", (4098,) * 10),
        ("AtmAtmAtmAtmAtmAtmAtmAtmAtmAtm", (1000,) * 10),
        ("AMyAMyAMyAMyAMyAMyAMyAMyAMyAMy", (2000,) * 10),
        ("BfKBfKBfKBfKBfKBfKBfKBfKBfKBfK", (3000,) * 10),
        ("ByWByWByWByWByWByWByWByWByWByW", (4000,) * 10),
        ("BSiBSiBSiBSiBSiBSiBSiBSiBSiBSi", (5000,) * 10),
        ("CluCluCluCluCluCluCluCluCluClu", (6000,) * 10),
        ("CEGCEGCEGCEGCEGCEGCEGCEGCEGCEG", (7000,) * 10),
        ("CXSCXSCXSCXSCXSCXSCXSCXSCXSCXS", (8000,) * 10),
        ("DreDreDreDreDreDreDreDreDreDre", (9000,) * 10),
        ("DKqDKqDKqDKqDKqDKqDKqDKqDKqDKq", (10000,) * 10),
        ("SzCSzCSzCSzCSzCSzCSzCSzCSzCSzC", (50000,) * 10),
        ("ZUiZUiZUiZUiZUiZUiZUiZUiZUiZUi", (70000,) * 10),
    ],
)
def test_amounts_hash_to_bet_amounts(amount_hash: str, expected: Sequence[int]) -> None:
    assert expected == amounts_hash_to_bet_amounts(amount_hash)


@pytest.mark.parametrize(
    ("expected", "bet_amounts"),
    [
        ("BAQBAQBAQBAQBAQBAQBAQBAQBAQBAQ", (4098,) * 10),
        ("AtmAtmAtmAtmAtmAtmAtmAtmAtmAtm", (1000,) * 10),
        ("AMyAMyAMyAMyAMyAMyAMyAMyAMyAMy", (2000,) * 10),
        ("BfKBfKBfKBfKBfKBfKBfKBfKBfKBfK", (3000,) * 10),
        ("ByWByWByWByWByWByWByWByWByWByW", (4000,) * 10),
        ("BSiBSiBSiBSiBSiBSiBSiBSiBSiBSi", (5000,) * 10),
        ("CluCluCluCluCluCluCluCluCluClu", (6000,) * 10),
        ("CEGCEGCEGCEGCEGCEGCEGCEGCEGCEG", (7000,) * 10),
        ("CXSCXSCXSCXSCXSCXSCXSCXSCXSCXS", (8000,) * 10),
        ("DreDreDreDreDreDreDreDreDreDre", (9000,) * 10),
        ("DKqDKqDKqDKqDKqDKqDKqDKqDKqDKq", (10000,) * 10),
        ("SzCSzCSzCSzCSzCSzCSzCSzCSzCSzC", (50000,) * 10),
        ("ZUiZUiZUiZUiZUiZUiZUiZUiZUiZUi", (70000,) * 10),
    ],
)
def test_bet_amounts_to_amounts_hash(expected: str, bet_amounts: Sequence[int]) -> None:
    assert bet_amounts_to_amounts_hash(bet_amounts) == expected


@pytest.mark.parametrize(
    ("bets_hash", "expected"),
    [
        ("", 0),
        ("f", 1),
        ("faa", 1),
        ("ltqvqwgimhqtvrnywrwvijwnn", 10),
        ("ltqvqwgimhqtvrnywrwvijwnnxgslqmrylolnk", 15),
    ],
)
def test_bets_hash_to_bets_count(bets_hash: str, expected: int) -> None:
    assert expected == bets_hash_to_bets_count(bets_hash)


def test_make_probabilities() -> None:
    # this is more for code coverage purposes, to hit the `if std_total == 1: break`
    # line in the make_probabilities method
    probs = make_probabilities(
        (
            (1, 11, 4, 2, 3),
            (1, 12, 8, 5, 2),
            (1, 11, 13, 2, 2),
            (1, 2, 13, 13, 11),
            (1, 5, 11, 7, 2),
        )
    )
    assert len(probs) == 5


def test_amount_hash_to_bet_amounts_below_50() -> None:
    assert amounts_hash_to_bet_amounts("AaX") == (None,)
