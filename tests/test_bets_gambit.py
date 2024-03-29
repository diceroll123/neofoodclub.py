import pytest

from neofoodclub import Bets, NeoFoodClub


def test_gambit_bet_generator(nfc: NeoFoodClub) -> None:
    assert nfc.make_best_gambit_bets().is_gambit is True


def test_gambit_bets(gambit_bets: Bets) -> None:
    # test pre-generated gambit bets
    assert gambit_bets.is_gambit is True


def test_not_gambit_bets(crazy_bets: Bets) -> None:
    # crazy bets will never be gambits
    assert crazy_bets.is_gambit is False


def test_minimum_gambit_bets(nfc: NeoFoodClub) -> None:
    # the very arbitrary rules, bare minimum.
    assert nfc.make_bets_from_binaries([0x88888, 0x8]).is_gambit is True


def test_gambit_bets_for_one_bet(nfc: NeoFoodClub) -> None:
    # the very arbitrary rules, bare minimum.
    assert nfc.make_bets_from_binaries([0x88888]).is_gambit is False


def test_gambit_bets_for_non_full_arena(nfc: NeoFoodClub) -> None:
    # the very arbitrary rules, bare minimum.
    assert nfc.make_bets_from_binaries([0x8888, 0x8]).is_gambit is False


def test_random_gambit_bets(nfc: NeoFoodClub) -> None:
    bets = nfc.make_random_gambit_bets()
    assert bets.is_gambit is True
    assert len(bets) == 10


@pytest.mark.parametrize(
    ("five_bet"),
    [
        (0x88888),
        (0x44444),
        (0x22222),
        (0x11111),
    ],
)
def test_gambit_bets_subsets(
    nfc: NeoFoodClub,
    five_bet: int,
) -> None:
    bets = nfc.make_gambit_bets(five_bet)

    assert bets.is_gambit is True
    assert all(five_bet & bet == bet for bet in bets.binaries)
