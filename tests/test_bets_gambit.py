import pytest
from neofoodclub.bets import Bets
from neofoodclub.nfc import NeoFoodClub


def test_gambit_bet_generator(nfc: NeoFoodClub):
    assert nfc.make_gambit_bets().is_gambit is True


def test_gambit_bets(gambit_bets: Bets):
    # test pre-generated gambit bets
    assert gambit_bets.is_gambit is True


def test_not_gambit_bets(crazy_bets: Bets):
    # crazy bets will never be gambits
    assert crazy_bets.is_gambit is False


def test_minimum_gambit_bets(nfc: NeoFoodClub):
    # the very arbitrary rules, bare minimum.
    assert nfc.make_bets_from_binaries(0x88888, 0x8).is_gambit is True


def test_gambit_bets_for_one_bet(nfc: NeoFoodClub):
    # the very arbitrary rules, bare minimum.
    assert nfc.make_bets_from_binaries(0x88888).is_gambit is False


def test_gambit_bets_for_non_full_arena(nfc: NeoFoodClub):
    # the very arbitrary rules, bare minimum.
    assert nfc.make_bets_from_binaries(0x8888, 0x8).is_gambit is False


def test_random_gambit_bets(nfc: NeoFoodClub):
    bets = nfc.make_gambit_bets(random=True)
    assert bets.is_gambit is True
    assert len(bets) == 10


@pytest.mark.parametrize(
    "five_bet,bets_hash",
    [
        (0x88888, "ggfgggbgbgbbggfaggaggffgf"),
        (0x44444, "mmmmckmmmkkkmmakmccamckmm"),
        (0x22222, "ssssddsssppsspsdpssadsddd"),
        (0x11111, "yyyuyyuuyyyayeyeeyyuueuye"),
    ],
)
def test_gambit_bets_equivalence(nfc: NeoFoodClub, five_bet: int, bets_hash: str):
    bets = nfc.make_gambit_bets(five_bet=five_bet)
    assert bets.bets_hash == bets_hash
