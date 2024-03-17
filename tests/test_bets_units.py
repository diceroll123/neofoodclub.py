from neofoodclub import NeoFoodClub


def test_unit_bets_empty(nfc: NeoFoodClub) -> None:
    bets = nfc.make_units_bets(400000)  # higher than possible
    assert bets is None


def test_unit_bets_equivalence(nfc: NeoFoodClub) -> None:
    bets = nfc.make_units_bets(20)
    assert bets is not None
    assert all(b >= 20 for b in bets.odds_values(nfc))


def test_unit_bets(nfc: NeoFoodClub) -> None:
    bets = nfc.make_units_bets(20)
    assert bets is not None
    assert len(bets) == 10
