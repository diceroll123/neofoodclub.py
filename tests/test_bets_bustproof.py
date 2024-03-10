import copy

import pytest

from neofoodclub import Modifier, NeoFoodClub
from neofoodclub.bets import Bets
from neofoodclub.errors import NoPositiveArenas


def test_bustproof_generator(nfc: NeoFoodClub) -> None:
    bets = nfc.make_bustproof_bets()
    assert bets is not None
    assert bets.is_bustproof is True


def test_bustproof_generator_amount(nfc: NeoFoodClub) -> None:
    # for this round data we have, this makes 4 bets.
    bets = nfc.make_bustproof_bets()
    assert bets is not None
    assert len(bets) == 4


def test_bustproof_minimal(nfc: NeoFoodClub) -> None:
    assert nfc.make_bets_from_binaries([0x1, 0x2, 0x4, 0x8]).is_bustproof is True


def test_not_bustproof_single(nfc: NeoFoodClub) -> None:
    assert nfc.make_bets_from_binaries([0x1]).is_bustproof is False


def test_not_bustproof(crazy_bets: Bets) -> None:
    assert crazy_bets.is_bustproof is False


def test_bustproof_with_two_positives(nfc: NeoFoodClub) -> None:
    # test with 2 positives
    new_nfc = nfc.copy()
    # setting Buck to 4 sets arena to positive, giving us 2 positives
    new_nfc.modifier = Modifier(custom_odds={19: 4})
    bets = new_nfc.make_bustproof_bets()
    assert bets is not None
    assert bets.is_bustproof is True


def test_bustproof_with_three_positives(nfc: NeoFoodClub) -> None:
    # test with 3 positives
    new_nfc = nfc.copy()
    # setting Buck to 4 and Fairfax to 5 sets arenas to positive, giving us 3 positives
    new_nfc.modifier = Modifier(custom_odds={19: 4, 14: 5})
    bets = new_nfc.make_bustproof_bets()
    assert bets is not None
    assert bets.is_bustproof is True


def test_bustproof_equivalence(nfc_with_bet_amount: NeoFoodClub) -> None:
    # bet amounts are NEEDED to make bustproof + guaranteed wins
    bets = nfc_with_bet_amount.make_bustproof_bets()
    assert bets is not None
    assert bets.bets_hash == "aafacaapae"


def test_bustproof_generator_no_positives(nfc: NeoFoodClub) -> None:
    with pytest.raises(NoPositiveArenas):
        # modify our round object to have no positives (just need to change the last arena for this one)
        round_data = copy.deepcopy(nfc._data)
        # will give the arena a -50% ratio
        round_data["currentOdds"][-1] = [1, 2, 2, 2, 2]
        no_positive_nfc = NeoFoodClub(round_data)  # type: ignore
        no_positive_nfc.make_bustproof_bets()
