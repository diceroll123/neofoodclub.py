from __future__ import annotations

import json

import pytest

from neofoodclub import Bets, NeoFoodClub, ProbabilityModel

# I picked the smallest round I could quickly find.
# Changing this object will require changing tests,
# as some of the tests rely on specific qualities
# that this round provides, such as arena ratios,
# bets winning, etc.

round_dict = {
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


@pytest.fixture
def test_round_data_json() -> str:
    return json.dumps(round_dict)


@pytest.fixture
def test_round_data_round_9088() -> str:
    # the significance of this round is that gmer and mer don't match
    # which is better for our tests
    return '{"foods":[[33,34,2,38,14,3,8,21,24,9],[16,5,15,8,9,29,3,39,38,4],[30,4,7,2,5,13,1,6,39,23],[29,7,37,15,27,18,34,8,30,20],[23,12,32,31,3,18,11,37,29,15]],"round":9088,"start":"2024-03-23T23:25:08+00:00","changes":[{"t":"2024-03-24T00:01:12+00:00","new":13,"old":10,"arena":2,"pirate":3},{"t":"2024-03-24T00:01:12+00:00","new":9,"old":7,"arena":3,"pirate":3},{"t":"2024-03-24T00:01:12+00:00","new":7,"old":5,"arena":3,"pirate":4},{"t":"2024-03-24T00:02:06+00:00","new":13,"old":10,"arena":4,"pirate":4},{"t":"2024-03-24T00:05:03+00:00","new":13,"old":12,"arena":1,"pirate":1},{"t":"2024-03-24T00:36:54+00:00","new":8,"old":9,"arena":0,"pirate":2},{"t":"2024-03-24T00:37:12+00:00","new":9,"old":8,"arena":0,"pirate":2},{"t":"2024-03-24T00:37:30+00:00","new":8,"old":9,"arena":0,"pirate":2},{"t":"2024-03-24T01:02:33+00:00","new":5,"old":6,"arena":1,"pirate":3},{"t":"2024-03-24T01:02:51+00:00","new":6,"old":5,"arena":1,"pirate":3},{"t":"2024-03-24T01:03:09+00:00","new":5,"old":6,"arena":1,"pirate":3},{"t":"2024-03-24T14:32:34+00:00","new":6,"old":5,"arena":1,"pirate":3},{"t":"2024-03-24T14:33:30+00:00","new":5,"old":6,"arena":1,"pirate":3},{"t":"2024-03-24T14:33:49+00:00","new":6,"old":5,"arena":1,"pirate":3}],"pirates":[[10,13,20,17],[14,4,5,16],[12,15,2,3],[9,1,8,7],[11,19,18,6]],"winners":[3,3,2,2,2],"timestamp":"2024-03-24T23:24:53+00:00","lastChange":"2024-03-24T14:33:49+00:00","currentOdds":[[1,13,8,2,2],[1,13,2,6,2],[1,13,2,13,13],[1,13,2,9,7],[1,13,2,13,13]],"openingOdds":[[1,13,9,2,2],[1,12,2,6,2],[1,13,2,10,13],[1,13,2,7,5],[1,13,2,13,10]]}'


@pytest.fixture
def test_round_url() -> str:
    return "/#round=7956&pirates=[[2,8,14,11],[20,7,6,10],[19,4,12,15],[3,1,5,13],[17,16,18,9]]&openingOdds=[[1,2,13,3,5],[1,4,2,4,5],[1,3,13,7,2],[1,13,2,3,3],[1,12,2,6,13]]&currentOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&foods=[[26,25,4,9,21,1,33,11,7,10],[12,9,14,35,25,6,21,19,40,37],[17,30,21,39,37,15,29,40,31,10],[10,18,35,9,34,23,27,32,28,12],[11,20,9,33,7,14,4,23,31,26]]&winners=[1,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00"


@pytest.fixture
def test_round_url_invalid_opening_odds() -> str:
    return "/#round=7956&pirates=[[2,8,14,11],[20,7,6,10],[19,4,12,15],[3,1,5,13],[17,16,18,9]]&openingOdds=[[1,1,13,3,5],[1,4,2,4,5],[1,3,13,7,2],[1,13,2,3,3],[1,12,2,6,13]]&currentOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&foods=[[26,25,4,9,21,1,33,11,7,10],[12,9,14,35,25,6,21,19,40,37],[17,30,21,39,37,15,29,40,31,10],[10,18,35,9,34,23,27,32,28,12],[11,20,9,33,7,14,4,23,31,26]]&winners=[1,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00"


@pytest.fixture
def test_round_url_no_opening_odds() -> str:
    return "/#round=7956&pirates=[[2,8,14,11],[20,7,6,10],[19,4,12,15],[3,1,5,13],[17,16,18,9]]&currentOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&foods=[[26,25,4,9,21,1,33,11,7,10],[12,9,14,35,25,6,21,19,40,37],[17,30,21,39,37,15,29,40,31,10],[10,18,35,9,34,23,27,32,28,12],[11,20,9,33,7,14,4,23,31,26]]&winners=[1,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00"


@pytest.fixture
def test_round_url_no_current_odds() -> str:
    return "/#round=7956&pirates=[[2,8,14,11],[20,7,6,10],[19,4,12,15],[3,1,5,13],[17,16,18,9]]&openingOdds=[[1,2,13,3,5],[1,4,2,4,5],[1,3,13,7,2],[1,13,2,3,3],[1,12,2,6,13]]&foods=[[26,25,4,9,21,1,33,11,7,10],[12,9,14,35,25,6,21,19,40,37],[17,30,21,39,37,15,29,40,31,10],[10,18,35,9,34,23,27,32,28,12],[11,20,9,33,7,14,4,23,31,26]]&winners=[1,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00"


@pytest.fixture
def test_round_url_invalid_pirates() -> str:
    return "/#round=7956&pirates=0&openingOdds=[[1,2,13,3,5],[1,4,2,4,5],[1,3,13,7,2],[1,13,2,3,3],[1,12,2,6,13]]&currentOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&foods=[[26,25,4,9,21,1,33,11,7,10],[12,9,14,35,25,6,21,19,40,37],[17,30,21,39,37,15,29,40,31,10],[10,18,35,9,34,23,27,32,28,12],[11,20,9,33,7,14,4,23,31,26]]&winners=[1,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00"


@pytest.fixture
def test_round_url_no_pirates() -> str:
    return "/#round=7956&openingOdds=[[1,2,13,3,5],[1,4,2,4,5],[1,3,13,7,2],[1,13,2,3,3],[1,12,2,6,13]]&currentOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&foods=[[26,25,4,9,21,1,33,11,7,10],[12,9,14,35,25,6,21,19,40,37],[17,30,21,39,37,15,29,40,31,10],[10,18,35,9,34,23,27,32,28,12],[11,20,9,33,7,14,4,23,31,26]]&winners=[1,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00"


@pytest.fixture
def test_round_url_no_round() -> str:
    return "/#pirates=[[2,8,14,11],[20,7,6,10],[19,4,12,15],[3,1,5,13],[17,16,18,9]]&openingOdds=[[1,2,13,3,5],[1,4,2,4,5],[1,3,13,7,2],[1,13,2,3,3],[1,12,2,6,13]]&currentOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&foods=[[26,25,4,9,21,1,33,11,7,10],[12,9,14,35,25,6,21,19,40,37],[17,30,21,39,37,15,29,40,31,10],[10,18,35,9,34,23,27,32,28,12],[11,20,9,33,7,14,4,23,31,26]]&winners=[1,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00"


@pytest.fixture
def test_round_url_no_food() -> str:
    return "/#round=7956&pirates=[[2,8,14,11],[20,7,6,10],[19,4,12,15],[3,1,5,13],[17,16,18,9]]&openingOdds=[[1,2,13,3,5],[1,4,2,4,5],[1,3,13,7,2],[1,13,2,3,3],[1,12,2,6,13]]&currentOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&winners=[1,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00"


@pytest.fixture
def test_round_url_no_winners() -> str:
    return "/#round=7956&pirates=[[2,8,14,11],[20,7,6,10],[19,4,12,15],[3,1,5,13],[17,16,18,9]]&openingOdds=[[1,2,13,3,5],[1,4,2,4,5],[1,3,13,7,2],[1,13,2,3,3],[1,12,2,6,13]]&currentOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&timestamp=2021-02-16T23:47:37+00:00"


@pytest.fixture
def test_max_ter_15_bets() -> str:
    return "/15/#round=7956&pirates=[[2,8,14,11],[20,7,6,10],[19,4,12,15],[3,1,5,13],[17,16,18,9]]&openingOdds=[[1,2,13,3,5],[1,4,2,4,5],[1,3,13,7,2],[1,13,2,3,3],[1,12,2,6,13]]&currentOdds=[[1,2,13,3,5],[1,4,2,4,6],[1,3,13,7,2],[1,13,2,3,3],[1,8,2,4,12]]&foods=[[26,25,4,9,21,1,33,11,7,10],[12,9,14,35,25,6,21,19,40,37],[17,30,21,39,37,15,29,40,31,10],[10,18,35,9,34,23,27,32,28,12],[11,20,9,33,7,14,4,23,31,26]]&winners=[1,3,4,2,4]&timestamp=2021-02-16T23:47:37+00:00&b=eukucjuoycaulucepkyreynycyakacfulxcefk"


# crazy bets mean(all arenas have a pirate bet)
# the crazy bet methods here all correspond to the exact same set!
@pytest.fixture
def crazy_test_hash() -> str:
    return "ltqvqwgimhqtvrnywrwvijwnn"


@pytest.fixture
def crazy_test_indices() -> tuple[tuple[int, ...], ...]:
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


@pytest.fixture
def crazy_test_binaries() -> tuple[int, ...]:
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


@pytest.fixture
def gambit_test_binaries() -> tuple[int, ...]:
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


@pytest.fixture
def nfc(test_round_data_json: str) -> NeoFoodClub:
    return NeoFoodClub(test_round_data_json)


@pytest.fixture
def nfc_with_bet_amount(test_round_data_json: str) -> NeoFoodClub:
    return NeoFoodClub(test_round_data_json, bet_amount=8000)


@pytest.fixture
def nfc_with_bet_amount_logit_model(test_round_data_json: str) -> NeoFoodClub:
    return NeoFoodClub(
        test_round_data_json,
        bet_amount=8000,
        probability_model=ProbabilityModel.MULTINOMIAL_LOGIT_MODEL.value,
    )


@pytest.fixture
def nfc_from_url(test_round_url) -> NeoFoodClub:
    return NeoFoodClub.from_url(test_round_url)


@pytest.fixture
def nfc_no_foods(test_round_url_no_food: str) -> NeoFoodClub:
    return NeoFoodClub.from_url(test_round_url_no_food)


@pytest.fixture
def crazy_bets(nfc: NeoFoodClub, crazy_test_hash: str) -> Bets:
    return nfc.make_bets_from_hash(crazy_test_hash)


@pytest.fixture
def gambit_bets(nfc: NeoFoodClub, gambit_test_binaries: tuple[int, ...]) -> Bets:
    return nfc.make_bets_from_binaries(gambit_test_binaries)


@pytest.fixture
def nfc_round_9088(test_round_data_round_9088: str) -> NeoFoodClub:
    return NeoFoodClub(test_round_data_round_9088)
