import datetime
from typing import Any, Dict

from neofoodclub import NeoFoodClub
from neofoodclub.neofoodclub import Modifier


def test_nfc_copy(nfc: NeoFoodClub, nfc_from_url: NeoFoodClub):
    # making sure that setting the bet amount in a copy will in fact not touch the original
    # just testing to make sure the copy was a deep copy
    def copy(n: NeoFoodClub):
        new_nfc = n.copy(cache=False)
        new_nfc.bet_amount = 8000
        assert new_nfc.bet_amount != n.bet_amount

    copy(nfc)
    copy(nfc_from_url)


def test_bet_amount(nfc: NeoFoodClub, nfc_from_url: NeoFoodClub):
    def amount(n: NeoFoodClub):
        new_nfc = n.copy(cache=False)
        new_nfc.bet_amount = 8000
        assert new_nfc.bet_amount == 8000

    amount(nfc)
    amount(nfc_from_url)


def test_modifier(nfc: NeoFoodClub, nfc_from_url: NeoFoodClub):
    def modify(n: NeoFoodClub):
        new_nfc = n.copy(cache=False)
        new_nfc.modifier = Modifier(Modifier.REVERSE)
        assert new_nfc.modifier == Modifier(Modifier.REVERSE)

    modify(nfc)
    modify(nfc_from_url)


def test_modified(nfc: NeoFoodClub, nfc_from_url: NeoFoodClub):
    def modify(n: NeoFoodClub):
        new_nfc = n.copy(cache=False)
        new_nfc.modifier = Modifier(custom_odds={1: 2})
        assert new_nfc.modified is True

    modify(nfc)
    modify(nfc_from_url)


def test_not_modified(nfc: NeoFoodClub):
    new_nfc = nfc.copy(cache=False)
    assert new_nfc.modified is False


def test_modified_opening_odds(nfc: NeoFoodClub):
    new_nfc = nfc.copy(cache=False)
    new_nfc.modifier = Modifier(Modifier.OPENING)
    assert new_nfc.modified is True


def test_modified_time(nfc: NeoFoodClub):
    new_nfc = nfc.copy(cache=False)
    new_nfc.modifier = Modifier(custom_time=datetime.time(hour=12, minute=0))
    assert new_nfc.modified is True


def test_with_modifier(nfc: NeoFoodClub):
    new_nfc = nfc.copy(cache=False)
    m = Modifier(Modifier.ALL_MODIFIERS)
    assert new_nfc.with_modifier(m).modifier == m


def test_round(nfc: NeoFoodClub, nfc_from_url: NeoFoodClub):
    assert nfc.round == 7956

    assert nfc_from_url.round == 7956


def test_is_over(nfc: NeoFoodClub, nfc_from_url: NeoFoodClub):
    assert nfc.is_over is True

    assert nfc_from_url.is_over is True


def test_changes_count(nfc: NeoFoodClub, nfc_from_url: NeoFoodClub):
    assert len(nfc.changes) == 4

    # changes are not provided or parsed in the url, so it's 0
    assert len(nfc_from_url.changes) == 0


def test_cc_perk(nfc: NeoFoodClub, nfc_from_url: NeoFoodClub):
    new_nfc = nfc.copy(cache=False)
    new_nfc.modifier = Modifier(cc_perk=True)
    bets = new_nfc.make_max_ter_bets()
    assert len(bets) == 15
    assert new_nfc.max_amount_of_bets == 15

    new_nfc = nfc_from_url.copy(cache=False)
    new_nfc.modifier = Modifier(cc_perk=True)
    bets = new_nfc.make_max_ter_bets()
    assert len(bets) == 15
    assert new_nfc.max_amount_of_bets == 15


def test_mer_winning_odds(nfc: NeoFoodClub, nfc_from_url: NeoFoodClub):
    # this set wins 24 units
    bets = nfc.make_bets_from_hash("aukacfukycuulacauutcbukdc")
    assert nfc.get_win_units(bets) == 24

    bets = nfc_from_url.make_bets_from_hash("aukacfukycuulacauutcbukdc")
    assert nfc_from_url.get_win_units(bets) == 24


def test_changes(nfc_no_cache: NeoFoodClub, test_round_data: Dict[str, Any]):
    # doing it all at once since it's literally one object
    assert nfc_no_cache.changes[0].index == 0
    assert nfc_no_cache.changes[0].data == test_round_data["changes"][0]
    assert nfc_no_cache.changes[0].old == 5
    assert nfc_no_cache.changes[0].new == 6
    assert nfc_no_cache.changes[0].pirate_index == 4
    assert nfc_no_cache.changes[0].arena_index == 1
    assert nfc_no_cache.changes[0].pirate.name == "Squire"
    assert nfc_no_cache.changes[0].arena == "Lagoon"
