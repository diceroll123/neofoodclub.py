from neofoodclub.neofoodclub import NeoFoodClub


def test_mer_bets_binaries_no_bet_amount(nfc: NeoFoodClub):
    # make sure it creates the same bets, regardless of order
    bets = nfc.make_max_ter_bets()

    assert set(bets) == {
        0x104,
        0x4,
        0x80104,
        0x1104,
        0x10104,
        0x80004,
        0x101,
        0x2104,
        0x8104,
        0x204,
    }


def test_mer_bets_binaries_with_amounts(nfc_with_bet_amount: NeoFoodClub):
    # make sure it creates the same bets, regardless of order
    bets = nfc_with_bet_amount.make_max_ter_bets()

    assert set(bets) == {
        0x104,
        0x4,
        0x80104,
        0x1104,
        0x10104,
        0x80004,
        0x101,
        0x2104,
        0x8104,
        0x204,
    }


def test_mer_bet_amounts(nfc_with_bet_amount: NeoFoodClub):
    bets = nfc_with_bet_amount.make_max_ter_bets()
    assert bets.bet_amounts.sum() == 80000
