from neofoodclub.neofoodclub import Bets, NeoFoodClub


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
