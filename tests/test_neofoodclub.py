import datetime
import json
from typing import Any, Dict, Optional

import orjson
import pytest

from neofoodclub import Modifier, NeoFoodClub


def test_nfc_reset(nfc: NeoFoodClub) -> None:
    new_nfc = nfc.copy()

    # making a bet will run the wrapper's reset
    assert len(new_nfc.make_bets_from_binaries([0x1])) == 1


def test_nfc_copy(nfc: NeoFoodClub, nfc_from_url: NeoFoodClub) -> None:
    # making sure that setting the bet amount in a copy will in fact not touch the original
    # just testing to make sure the copy was a deep copy
    def copy(n: NeoFoodClub) -> None:
        new_nfc = n.copy()
        new_nfc.bet_amount = 8000
        assert new_nfc.bet_amount != n.bet_amount

    copy(nfc)
    copy(nfc_from_url)


def test_bet_amount(nfc: NeoFoodClub, nfc_from_url: NeoFoodClub) -> None:
    def amount(n: NeoFoodClub) -> None:
        new_nfc = n.copy()
        new_nfc.bet_amount = 8000
        assert new_nfc.bet_amount == 8000

    amount(nfc)
    amount(nfc_from_url)


def test_modifier(nfc: NeoFoodClub, nfc_from_url: NeoFoodClub) -> None:
    def modify(n: NeoFoodClub) -> None:
        new_nfc = n.copy()
        new_nfc.modifier = Modifier(Modifier.REVERSE)
        assert new_nfc.modifier == Modifier(Modifier.REVERSE)

    modify(nfc)
    modify(nfc_from_url)


def test_modified(nfc: NeoFoodClub, nfc_from_url: NeoFoodClub) -> None:
    def modify(n: NeoFoodClub) -> None:
        new_nfc = n.copy()
        new_nfc.modifier = Modifier(Modifier.EMPTY, custom_odds={1: 2})
        assert new_nfc.modified is True

    modify(nfc)
    modify(nfc_from_url)


def test_not_modified(nfc: NeoFoodClub) -> None:
    new_nfc = nfc.copy()
    assert new_nfc.modified is False


def test_modified_opening_odds(nfc: NeoFoodClub) -> None:
    new_nfc = nfc.copy()
    new_nfc.modifier = Modifier(Modifier.OPENING_ODDS)
    assert new_nfc.modified is True


def test_modified_time(nfc: NeoFoodClub) -> None:
    new_nfc = nfc.copy()
    new_nfc.modifier = Modifier(custom_time=datetime.time(hour=12, minute=0))
    assert new_nfc.modified is True


def test_with_modifier(nfc: NeoFoodClub) -> None:
    new_nfc = nfc.copy()
    m = Modifier(Modifier.ALL_MODIFIERS)
    assert new_nfc.with_modifier(m).modifier == m


def test_round(nfc: NeoFoodClub, nfc_from_url: NeoFoodClub) -> None:
    assert nfc.round == 7956

    assert nfc_from_url.round == 7956


def test_is_over(nfc: NeoFoodClub, nfc_from_url: NeoFoodClub) -> None:
    assert nfc.is_over is True

    assert nfc_from_url.is_over is True


def test_changes_count(nfc: NeoFoodClub, nfc_from_url: NeoFoodClub) -> None:
    assert len(nfc.changes) == 4

    # changes are not provided or parsed in the url, so it's 0
    assert len(nfc_from_url.changes) == 0


def test_cc_perk(nfc: NeoFoodClub, nfc_from_url: NeoFoodClub) -> None:
    new_nfc = nfc.copy()
    new_nfc.modifier = Modifier(Modifier.CHARITY_CORNER)
    bets = new_nfc.make_max_ter_bets()
    assert len(bets) == 15
    assert new_nfc.max_amount_of_bets == 15

    new_nfc = nfc_from_url.copy()
    new_nfc.modifier = Modifier(Modifier.CHARITY_CORNER)
    bets = new_nfc.make_max_ter_bets()
    assert len(bets) == 15
    assert new_nfc.max_amount_of_bets == 15


@pytest.mark.parametrize(
    ("bet_hash", "winnings"),
    [
        ("aukacfukycuulacauutcbukdc", 24),
        ("ltqvqwgimhqtvrnywrwvijwnn", 0),
    ],
)
def test_get_win_units(
    nfc: NeoFoodClub,
    nfc_from_url: NeoFoodClub,
    bet_hash: str,
    winnings: int,
) -> None:
    bets = nfc.make_bets_from_hash(bet_hash)
    assert nfc.get_win_units(bets) == winnings

    bets_for_url = nfc_from_url.make_bets_from_hash(bet_hash)
    assert nfc_from_url.get_win_units(bets_for_url) == winnings


@pytest.mark.parametrize(
    ("bet_hash", "bet_amount", "winnings"),
    [
        ("aukacfukycuulacauutcbukdc", 8000, 192000),
        ("aukacfukycuulacauutcbukdc", None, 0),
        ("ltqvqwgimhqtvrnywrwvijwnn", 8000, 0),
        ("ltqvqwgimhqtvrnywrwvijwnn", None, 0),
    ],
)
def test_get_win_np(
    nfc: NeoFoodClub,
    nfc_from_url: NeoFoodClub,
    bet_hash: str,
    bet_amount: Optional[int],
    winnings: int,
) -> None:
    new_nfc = nfc.copy()
    new_nfc.bet_amount = bet_amount
    bets = new_nfc.make_bets_from_hash(bet_hash)
    assert new_nfc.get_win_np(bets) == winnings

    new_nfc_from_url = nfc_from_url.copy()
    new_nfc_from_url.bet_amount = bet_amount
    bets_for_url = new_nfc_from_url.make_bets_from_hash(bet_hash)
    assert new_nfc_from_url.get_win_np(bets_for_url) == winnings


def test_changes(nfc_no_cache: NeoFoodClub, test_round_data: Dict[str, Any]) -> None:
    # doing it all at once since it's literally one object
    assert nfc_no_cache.changes[0].index == 0
    assert nfc_no_cache.changes[0].data == test_round_data["changes"][0]
    assert nfc_no_cache.changes[0].old == 5
    assert nfc_no_cache.changes[0].new == 6
    assert nfc_no_cache.changes[0].pirate_index == 4
    assert nfc_no_cache.changes[0].arena_index == 1
    assert nfc_no_cache.changes[0].pirate.name == "Squire"
    assert nfc_no_cache.changes[0].arena == "Lagoon"


def test_get_arena(nfc: NeoFoodClub) -> None:
    assert nfc.get_arena(0).name == "Shipwreck"


def test_pirates(nfc: NeoFoodClub) -> None:
    assert nfc.pirates[0][0] == 2


def test_changes_equivalence(nfc: NeoFoodClub) -> None:
    changes = list(set(nfc.changes))  # tests __hash__

    assert changes[0] != changes[1]


def test_change_bet_amount_twice(nfc: NeoFoodClub) -> None:
    # this runs the bet_amount setter code which recalculates
    # the inner dicts instead of making new ones
    # this is more for code coverage than testing anything
    new_nfc = nfc.copy()

    assert new_nfc._data_dict == {}
    new_nfc.bet_amount = 8000

    new_nfc.bet_amount = 5000
    assert new_nfc._data_dict != {}


def test_removed_timestamp(nfc: NeoFoodClub) -> None:
    # timestamp isn't really needed, so if it doesn't exist,
    # we just return None
    data = orjson.loads(nfc.to_json())

    data.pop("timestamp")

    new_nfc = NeoFoodClub(json.dumps(data), bet_amount=None)
    assert new_nfc.timestamp is None


def test_outdated_lock(nfc: NeoFoodClub) -> None:
    # we're not even in the same year anymore
    # so this should be True
    assert nfc.is_outdated_lock is True


def test_outdated_lock_false(nfc: NeoFoodClub) -> None:
    now = datetime.datetime.now(datetime.timezone.utc)
    data = orjson.loads(nfc.to_json())
    data["start"] = now.isoformat()
    new_nfc = NeoFoodClub(json.dumps(data), bet_amount=None)
    assert new_nfc.is_outdated_lock is False


def test_outdated_lock_none(nfc: NeoFoodClub) -> None:
    data = orjson.loads(nfc.to_json())

    # if there's no start attribute, assume it's over
    data.pop("start")

    new_nfc = NeoFoodClub(json.dumps(data), bet_amount=None)
    assert new_nfc.is_outdated_lock is True


def test_winning_pirates(nfc: NeoFoodClub) -> None:
    assert len(nfc.winning_pirates) == 5  # type: ignore


def test_winning_pirates_empty(nfc: NeoFoodClub) -> None:
    data = orjson.loads(nfc.to_json())
    # monkeypatching in no winners
    data["winners"] = (0, 0, 0, 0, 0)

    new_nfc = NeoFoodClub(json.dumps(data), bet_amount=None)
    assert len(new_nfc.winning_pirates or []) == 0


def test_from_url_exception() -> None:
    with pytest.raises(BaseException):
        NeoFoodClub.from_url("", bet_amount=None)


def test_from_url_with_cc_perk(test_max_ter_15_bets: str) -> None:
    nfc = NeoFoodClub.from_url(test_max_ter_15_bets, bet_amount=None)
    assert nfc.modifier.is_charity_corner is True


def test_from_url_without_winners(test_round_url_no_winners: str) -> None:
    nfc = NeoFoodClub.from_url(test_round_url_no_winners, bet_amount=None)
    assert nfc.winners == (0, 0, 0, 0, 0)


def test_from_url_without_round_exception(test_round_url_no_round: str) -> None:
    with pytest.raises(BaseException):
        NeoFoodClub.from_url(test_round_url_no_round, bet_amount=None)


def test_from_url_without_pirates_exception(test_round_url_no_pirates: str) -> None:
    with pytest.raises(BaseException):
        NeoFoodClub.from_url(test_round_url_no_pirates, bet_amount=None)


def test_from_url_with_invalid_pirates_exception(
    test_round_url_invalid_pirates: str,
) -> None:
    with pytest.raises(BaseException):
        NeoFoodClub.from_url(test_round_url_invalid_pirates, bet_amount=None)


def test_from_url_with_no_opening_odds(test_round_url_no_opening_odds: str) -> None:
    with pytest.raises(BaseException):
        NeoFoodClub.from_url(test_round_url_no_opening_odds, bet_amount=None)


def test_from_url_with_no_current_odds(test_round_url_no_current_odds: str) -> None:
    with pytest.raises(BaseException):
        NeoFoodClub.from_url(test_round_url_no_current_odds, bet_amount=None)


def test_from_url_with_invalid_opening_odds(
    test_round_url_invalid_opening_odds: str,
) -> None:
    with pytest.raises(BaseException):
        NeoFoodClub.from_url(test_round_url_invalid_opening_odds, bet_amount=None)


@pytest.mark.parametrize(
    "url",
    [
        # round is a string
        "/#round=x&pirates=[[2,8,14,11],[20,7,6,10],[19,4,12,15],[3,1,5,13],[17,16,18,9]]&openingOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&currentOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,13]]&foods=[[26,25,4,9,21,1,33,11,7,10],[12,9,14,35,25,6,21,19,40,37],[17,30,21,39,37,15,29,40,31,10],[10,18,35,9,34,23,27,32,28,12],[11,20,9,33,7,14,4,23,31,26]]&winners=[1,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00",
        # pirates has a 0 in it
        "/#round=7956&pirates=[[0,8,14,11],[20,7,6,10],[19,4,12,15],[3,1,5,13],[17,16,18,9]]&openingOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&currentOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,13]]&foods=[[26,25,4,9,21,1,33,11,7,10],[12,9,14,35,25,6,21,19,40,37],[17,30,21,39,37,15,29,40,31,10],[10,18,35,9,34,23,27,32,28,12],[11,20,9,33,7,14,4,23,31,26]]&winners=[1,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00",
        # opening odds has a 0 in it
        "/#round=7956&pirates=[[2,8,14,11],[20,7,6,10],[19,4,12,15],[3,1,5,13],[17,16,18,9]]&openingOdds=[[1,0,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&currentOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,13]]&foods=[[26,25,4,9,21,1,33,11,7,10],[12,9,14,35,25,6,21,19,40,37],[17,30,21,39,37,15,29,40,31,10],[10,18,35,9,34,23,27,32,28,12],[11,20,9,33,7,14,4,23,31,26]]&winners=[1,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00",
        # current odds has a 0 in it
        "/#round=7956&pirates=[[2,8,14,11],[20,7,6,10],[19,4,12,15],[3,1,5,13],[17,16,18,9]]&openingOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&currentOdds=[[1,0,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,13]]&foods=[[26,25,4,9,21,1,33,11,7,10],[12,9,14,35,25,6,21,19,40,37],[17,30,21,39,37,15,29,40,31,10],[10,18,35,9,34,23,27,32,28,12],[11,20,9,33,7,14,4,23,31,26]]&winners=[1,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00",
        # winners has a 0 in it
        "/#round=7956&pirates=[[2,8,14,11],[20,7,6,10],[19,4,12,15],[3,1,5,13],[17,16,18,9]]&openingOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&currentOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,13]]&foods=[[26,25,4,9,21,1,33,11,7,10],[12,9,14,35,25,6,21,19,40,37],[17,30,21,39,37,15,29,40,31,10],[10,18,35,9,34,23,27,32,28,12],[11,20,9,33,7,14,4,23,31,26]]&winners=[0,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00",
    ],
)
def test_error_cases_in_from_url(url: str) -> None:
    with pytest.raises(BaseException):
        NeoFoodClub.from_url(url, bet_amount=None)
