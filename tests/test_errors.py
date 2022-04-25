import copy

import pytest
from neofoodclub.errors import (
    InvalidAmountHash,
    InvalidBetHash,
    InvalidData,
    NoPositiveArenas,
)
from neofoodclub.neofoodclub import NeoFoodClub


def test_bustproof_generator_no_positives(nfc: NeoFoodClub):
    with pytest.raises(NoPositiveArenas):
        # modify our round object to have no positives (just need to change the last arena for this one)
        round_data = copy.deepcopy(nfc._data)
        # will give the arena a -50% ratio
        round_data["currentOdds"][-1] = [1, 2, 2, 2, 2]
        no_positive_nfc = NeoFoodClub(round_data)
        no_positive_nfc.make_bustproof_bets()


def test_too_many_bet_amounts_from_binaries(nfc: NeoFoodClub):
    with pytest.raises(InvalidData):
        nfc.make_bets_from_binaries(0x1, amounts=[50, 50])


def test_too_many_bet_amounts_from_indices(nfc: NeoFoodClub):
    with pytest.raises(InvalidData):
        nfc.make_bets_from_indices([(1, 0, 0, 0, 0)], amounts=[50, 50])


def test_too_many_bet_amounts_from_hash(nfc: NeoFoodClub):
    with pytest.raises(InvalidData):
        nfc.make_bets_from_hash("faa", amounts=[50, 50])


def test_invalid_bet_hash(nfc: NeoFoodClub):
    with pytest.raises(InvalidBetHash):
        nfc.make_bets_from_hash("faz")


def test_invalid_amounts_hash(nfc: NeoFoodClub):
    with pytest.raises(InvalidAmountHash):
        nfc.make_bets_from_hash("faa", amounts_hash="???")


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
def test_error_cases_in_from_url(url: str):
    with pytest.raises(InvalidData):
        NeoFoodClub.from_url(url)
