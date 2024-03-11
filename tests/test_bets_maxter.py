from neofoodclub import Modifier, NeoFoodClub


def test_mer_bets_binaries_no_bet_amount(nfc: NeoFoodClub) -> None:
    # make sure it creates the same bets, regardless of order
    bets = nfc.make_max_ter_bets()

    assert set(bets.binaries) == {
        0x1104,
        0x1004,
        0x81104,
        0x11104,
        0x104,
        0x81004,
        0x1204,
        0x1124,
        0x1114,
        0x21104,
    }


def test_mer_bets_binaries_with_amounts(nfc_with_bet_amount: NeoFoodClub) -> None:
    # make sure it creates the same bets, regardless of order
    bets = nfc_with_bet_amount.make_max_ter_bets()

    assert set(bets.binaries) == {
        0x1104,
        0x1004,
        0x81104,
        0x11104,
        0x104,
        0x81004,
        0x1204,
        0x1124,
        0x21104,
        0x1114,
    }


def test_mer_bet_amounts(nfc_with_bet_amount: NeoFoodClub) -> None:
    bets = nfc_with_bet_amount.make_max_ter_bets()
    assert sum(bets.bet_amounts) == 80000  # type: ignore


def test_mer_reverse(nfc_with_bet_amount: NeoFoodClub) -> None:
    new_nfc = nfc_with_bet_amount.copy()
    new_nfc.modifier = Modifier(Modifier.REVERSE)

    bets = new_nfc.make_max_ter_bets()

    assert sum(bets.bet_amounts) == 68181  # type: ignore
