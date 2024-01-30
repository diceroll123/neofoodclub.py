from typing import Any, Dict, Tuple

import pytest

from neofoodclub import Bets, NeoFoodClub
from neofoodclub.models.multinomial_logit import MultinomialLogitModel


# I picked the smallest round I could quickly find.
# Changing this object will require changing tests,
# as some of the tests rely on specific qualities
# that this round provides, such as arena ratios,
# bets winning, etc.
@pytest.fixture()
def test_round_data() -> Dict[str, Any]:
    return {
        "currentOdds": [
            [1, 2, 13, 3, 5],
            [1, 4, 2, 4, 6],
            [1, 3, 13, 7, 2],
            [1, 13, 2, 3, 3],
            [1, 8, 2, 4, 12],
        ],
        "foods": [
            [26, 25, 4, 9, 21, 1, 33, 11, 7, 10],
            [12, 9, 14, 35, 25, 6, 21, 19, 40, 37],
            [17, 30, 21, 39, 37, 15, 29, 40, 31, 10],
            [10, 18, 35, 9, 34, 23, 27, 32, 28, 12],
            [11, 20, 9, 33, 7, 14, 4, 23, 31, 26],
        ],
        "lastChange": "2021-02-16T23:47:18+00:00",
        "openingOdds": [
            [1, 2, 13, 3, 5],
            [1, 4, 2, 4, 5],
            [1, 3, 13, 7, 2],
            [1, 13, 2, 3, 3],
            [1, 12, 2, 6, 13],
        ],
        "pirates": [
            [2, 8, 14, 11],
            [20, 7, 6, 10],
            [19, 4, 12, 15],
            [3, 1, 5, 13],
            [17, 16, 18, 9],
        ],
        "round": 7956,
        "start": "2021-02-15T23:47:41+00:00",
        "timestamp": "2021-02-16T23:47:37+00:00",
        "winners": [1, 3, 4, 2, 4],
        "changes": [
            {
                "arena": 1,
                "new": 6,
                "old": 5,
                "pirate": 4,
                "t": "2021-02-16T23:47:18+00:00",
            },
            {
                "arena": 4,
                "new": 8,
                "old": 12,
                "pirate": 1,
                "t": "2021-02-16T23:47:18+00:00",
            },
            {
                "arena": 4,
                "new": 4,
                "old": 6,
                "pirate": 3,
                "t": "2021-02-16T23:47:18+00:00",
            },
            {
                "arena": 4,
                "new": 12,
                "old": 13,
                "pirate": 4,
                "t": "2021-02-16T23:47:18+00:00",
            },
        ],
    }


@pytest.fixture()
def test_round_url() -> str:
    return "/#round=7956&pirates=[[2,8,14,11],[20,7,6,10],[19,4,12,15],[3,1,5,13],[17,16,18,9]]&openingOdds=[[1,2,13,3,5],[1,4,2,4,5],[1,3,13,7,2],[1,13,2,3,3],[1,12,2,6,13]]&currentOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&foods=[[26,25,4,9,21,1,33,11,7,10],[12,9,14,35,25,6,21,19,40,37],[17,30,21,39,37,15,29,40,31,10],[10,18,35,9,34,23,27,32,28,12],[11,20,9,33,7,14,4,23,31,26]]&winners=[1,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00"


@pytest.fixture()
def test_round_url_invalid_opening_odds() -> str:
    return "/#round=7956&pirates=[[2,8,14,11],[20,7,6,10],[19,4,12,15],[3,1,5,13],[17,16,18,9]]&openingOdds=[[1,1,13,3,5],[1,4,2,4,5],[1,3,13,7,2],[1,13,2,3,3],[1,12,2,6,13]]&currentOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&foods=[[26,25,4,9,21,1,33,11,7,10],[12,9,14,35,25,6,21,19,40,37],[17,30,21,39,37,15,29,40,31,10],[10,18,35,9,34,23,27,32,28,12],[11,20,9,33,7,14,4,23,31,26]]&winners=[1,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00"


@pytest.fixture()
def test_round_url_no_opening_odds() -> str:
    return "/#round=7956&pirates=[[2,8,14,11],[20,7,6,10],[19,4,12,15],[3,1,5,13],[17,16,18,9]]&currentOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&foods=[[26,25,4,9,21,1,33,11,7,10],[12,9,14,35,25,6,21,19,40,37],[17,30,21,39,37,15,29,40,31,10],[10,18,35,9,34,23,27,32,28,12],[11,20,9,33,7,14,4,23,31,26]]&winners=[1,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00"


@pytest.fixture()
def test_round_url_no_current_odds() -> str:
    return "/#round=7956&pirates=[[2,8,14,11],[20,7,6,10],[19,4,12,15],[3,1,5,13],[17,16,18,9]]&openingOdds=[[1,2,13,3,5],[1,4,2,4,5],[1,3,13,7,2],[1,13,2,3,3],[1,12,2,6,13]]&foods=[[26,25,4,9,21,1,33,11,7,10],[12,9,14,35,25,6,21,19,40,37],[17,30,21,39,37,15,29,40,31,10],[10,18,35,9,34,23,27,32,28,12],[11,20,9,33,7,14,4,23,31,26]]&winners=[1,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00"


@pytest.fixture()
def test_round_url_invalid_pirates() -> str:
    return "/#round=7956&pirates=0&openingOdds=[[1,2,13,3,5],[1,4,2,4,5],[1,3,13,7,2],[1,13,2,3,3],[1,12,2,6,13]]&currentOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&foods=[[26,25,4,9,21,1,33,11,7,10],[12,9,14,35,25,6,21,19,40,37],[17,30,21,39,37,15,29,40,31,10],[10,18,35,9,34,23,27,32,28,12],[11,20,9,33,7,14,4,23,31,26]]&winners=[1,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00"


@pytest.fixture()
def test_round_url_no_pirates() -> str:
    return "/#round=7956&openingOdds=[[1,2,13,3,5],[1,4,2,4,5],[1,3,13,7,2],[1,13,2,3,3],[1,12,2,6,13]]&currentOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&foods=[[26,25,4,9,21,1,33,11,7,10],[12,9,14,35,25,6,21,19,40,37],[17,30,21,39,37,15,29,40,31,10],[10,18,35,9,34,23,27,32,28,12],[11,20,9,33,7,14,4,23,31,26]]&winners=[1,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00"


@pytest.fixture()
def test_round_url_no_round() -> str:
    return "/#pirates=[[2,8,14,11],[20,7,6,10],[19,4,12,15],[3,1,5,13],[17,16,18,9]]&openingOdds=[[1,2,13,3,5],[1,4,2,4,5],[1,3,13,7,2],[1,13,2,3,3],[1,12,2,6,13]]&currentOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&foods=[[26,25,4,9,21,1,33,11,7,10],[12,9,14,35,25,6,21,19,40,37],[17,30,21,39,37,15,29,40,31,10],[10,18,35,9,34,23,27,32,28,12],[11,20,9,33,7,14,4,23,31,26]]&winners=[1,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00"


@pytest.fixture()
def test_round_url_no_food() -> str:
    return "/#round=7956&pirates=[[2,8,14,11],[20,7,6,10],[19,4,12,15],[3,1,5,13],[17,16,18,9]]&openingOdds=[[1,2,13,3,5],[1,4,2,4,5],[1,3,13,7,2],[1,13,2,3,3],[1,12,2,6,13]]&currentOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&winners=[1,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00"


@pytest.fixture()
def test_round_url_no_winners() -> str:
    return "/#round=7956&pirates=[[2,8,14,11],[20,7,6,10],[19,4,12,15],[3,1,5,13],[17,16,18,9]]&openingOdds=[[1,2,13,3,5],[1,4,2,4,5],[1,3,13,7,2],[1,13,2,3,3],[1,12,2,6,13]]&currentOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&timestamp=2021-02-16T23:47:37+00:00"


@pytest.fixture()
def test_max_ter_15_bets() -> str:
    return "/15/#round=7956&pirates=[[2,8,14,11],[20,7,6,10],[19,4,12,15],[3,1,5,13],[17,16,18,9]]&openingOdds=[[1,2,13,3,5],[1,4,2,4,5],[1,3,13,7,2],[1,13,2,3,3],[1,12,2,6,13]]&currentOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&foods=[[26,25,4,9,21,1,33,11,7,10],[12,9,14,35,25,6,21,19,40,37],[17,30,21,39,37,15,29,40,31,10],[10,18,35,9,34,23,27,32,28,12],[11,20,9,33,7,14,4,23,31,26]]&winners=[1,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00&b=eukucjuoycaulucepkyreynycyakacfulxcefk"


# crazy bets mean(all arenas have a pirate bet)
# the crazy bet methods here all correspond to the exact same set!
@pytest.fixture()
def crazy_test_hash() -> str:
    return "ltqvqwgimhqtvrnywrwvijwnn"


@pytest.fixture()
def crazy_test_indices() -> Tuple[Tuple[int, ...], ...]:
    return (
        (2, 1, 3, 4, 3),
        (1, 4, 1, 3, 1),
        (4, 2, 1, 1, 1),
        (3, 2, 2, 1, 2),
        (3, 1, 3, 4, 4),
        (1, 3, 2, 2, 3),
        (4, 4, 4, 2, 3),
        (2, 4, 2, 4, 1),
        (1, 3, 1, 4, 4),
        (2, 2, 3, 2, 3),
    )


@pytest.fixture()
def crazy_test_binaries() -> Tuple[int, ...]:
    return (
        0x48212,
        0x81828,
        0x14888,
        0x24484,
        0x28211,
        0x82442,
        0x11142,
        0x41418,
        0x82811,
        0x44242,
    )


@pytest.fixture()
def gambit_test_binaries() -> Tuple[int, ...]:
    # just a random gambit set
    return (
        0x11842,
        0x11042,
        0x1842,
        0x11840,
        0x11802,
        0x1042,
        0x10842,
        0x11040,
        0x11002,
        0x1840,
    )


@pytest.fixture()
def nfc(test_round_data: Dict[str, Any]) -> NeoFoodClub:
    return NeoFoodClub(test_round_data)


@pytest.fixture()
def nfc_no_cache(test_round_data: Dict[str, Any]) -> NeoFoodClub:
    return NeoFoodClub(test_round_data, cache=False)


@pytest.fixture()
def nfc_with_bet_amount(test_round_data: Dict[str, Any]) -> NeoFoodClub:
    return NeoFoodClub(test_round_data, bet_amount=8000)


@pytest.fixture()
def nfc_with_bet_amount_logit_model(test_round_data: Dict[str, Any]) -> NeoFoodClub:
    return NeoFoodClub(
        test_round_data,
        bet_amount=8000,
        probability_model=MultinomialLogitModel,
    )


@pytest.fixture()
def nfc_from_url(test_round_url) -> NeoFoodClub:
    return NeoFoodClub.from_url(test_round_url)


@pytest.fixture()
def nfc_no_foods(test_round_url_no_food: str) -> NeoFoodClub:
    return NeoFoodClub.from_url(test_round_url_no_food)


@pytest.fixture()
def crazy_bets(nfc: NeoFoodClub, crazy_test_hash: str) -> Bets:
    return nfc.make_bets_from_hash(crazy_test_hash)


@pytest.fixture()
def gambit_bets(nfc: NeoFoodClub, gambit_test_binaries: Tuple[int, ...]) -> Bets:
    return nfc.make_bets_from_binaries(*gambit_test_binaries)
