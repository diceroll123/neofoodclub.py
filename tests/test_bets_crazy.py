from neofoodclub.neofoodclub import Bets, NeoFoodClub


def test_crazy_bet_generator(nfc: NeoFoodClub):
    assert nfc.make_crazy_bets().is_crazy is True


def test_crazy_bets(crazy_bets: Bets):
    # test pre-generated crazy bets
    assert crazy_bets.is_crazy is True


def test_non_crazy_bets(nfc: NeoFoodClub):
    # test non-crazy bets
    assert nfc.make_bets_from_binaries(0x1, 0x2, 0x4, 0x8).is_crazy is False


def test_net_expected_equality_no_amount(crazy_bets: Bets):
    assert crazy_bets.net_expected == 0.0
