from collections.abc import Sequence

import pytest

from neofoodclub import (
    Math,
)


@pytest.mark.parametrize(
    ("bet_binary", "expected"),
    [
        (0x84210, (1, 2, 3, 4, 0)),
        (0x88888, (1, 1, 1, 1, 1)),
        (0x44444, (2, 2, 2, 2, 2)),
        (0x22222, (3, 3, 3, 3, 3)),
        (0x11111, (4, 4, 4, 4, 4)),
        (0x00000, (0, 0, 0, 0, 0)),
    ],
)
def test_binary_to_indices(bet_binary: int, expected: Sequence[int]) -> None:
    assert expected == Math.binary_to_indices(bet_binary)


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
    assert expected == Math.amounts_hash_to_bet_amounts(amount_hash)


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
    assert Math.bet_amounts_to_amounts_hash(bet_amounts) == expected


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
    assert expected == Math.bets_hash_to_bets_count(bets_hash)


def test_amount_hash_to_bet_amounts_below_50() -> None:
    assert Math.amounts_hash_to_bet_amounts("AaX") == (49,)


def test_expand_ib_object() -> None:
    assert (Math.expand_ib_object([Math.binary_to_indices(0x80000)], [1])) == {
        524287: 0,
        589823: 1,
    }
