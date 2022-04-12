from neofoodclub.errors import NoPositiveArenas
from neofoodclub.neofoodclub import Bets, NeoFoodClub


def test_bustproof_generator(nfc: NeoFoodClub):
    assert nfc.make_bustproof_bets().is_bustproof is True


def test_bustproof_generator_amount(nfc: NeoFoodClub):
    # for this round data we have, this makes 4 bets.
    assert len(nfc.make_bustproof_bets()) == 4


def test_bustproof_minimal(nfc: NeoFoodClub):
    assert nfc.make_bets_from_binaries(0x1, 0x2, 0x4, 0x8).is_bustproof is True


def test_not_bustproof_single(nfc: NeoFoodClub):
    assert nfc.make_bets_from_binaries(0x1).is_bustproof is False


def test_not_bustproof(crazy_bets: Bets):
    assert crazy_bets.is_bustproof is False
