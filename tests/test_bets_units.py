from neofoodclub.neofoodclub import NeoFoodClub


def test_unit_bets_empty(nfc: NeoFoodClub):
    bets = nfc.make_units_bets(400000)  # higher than possible
    assert len(bets) == 0


def test_unit_bets_equivalence(nfc: NeoFoodClub):
    bets = nfc.make_units_bets(20)  # higher than possible
    assert bets.bets_hash == "uukycjalewfxoamecokcsanfc"


def test_unit_bets(nfc: NeoFoodClub):
    bets = nfc.make_units_bets(20)
    assert len(bets) == 10
