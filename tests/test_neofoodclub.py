import unittest
from typing import Tuple

from neofoodclub import NeoFoodClub  # type: ignore
from neofoodclub.types import RoundData  # type: ignore

# i picked the smallest round I could quickly find
test_round_data: RoundData = {
    "currentOdds": [
        [1, 2, 13, 3, 5],
        [1, 4, 2, 4, 6],
        [1, 3, 13, 7, 2],
        [1, 13, 2, 3, 3],
        [1, 8, 2, 4, 13],
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
        [1, 4, 2, 4, 6],
        [1, 3, 13, 7, 2],
        [1, 13, 2, 3, 3],
        [1, 8, 2, 4, 12],
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
        {"arena": 1, "new": 6, "old": 5, "pirate": 4, "t": "2021-02-16T23:47:18+00:00"},
        {
            "arena": 4,
            "new": 8,
            "old": 12,
            "pirate": 1,
            "t": "2021-02-16T23:47:18+00:00",
        },
        {"arena": 4, "new": 4, "old": 6, "pirate": 3, "t": "2021-02-16T23:47:18+00:00"},
        {
            "arena": 4,
            "new": 12,
            "old": 13,
            "pirate": 4,
            "t": "2021-02-16T23:47:18+00:00",
        },
    ],
}

test_bet_hash = "ltqvqwgimhqtvrnywrwvijwnn"
test_indices: Tuple[Tuple[int, ...], ...] = (
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
test_binaries: Tuple[int, ...] = (
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

test_expected_results = (test_bet_hash, test_indices, test_binaries)

test_nfc = NeoFoodClub(test_round_data)

hash_bets = test_nfc.make_bets_from_hash(test_bet_hash)
indices_bets = test_nfc.make_bets_from_indices(test_indices)  # type: ignore
binaries_bets = test_nfc.make_bets_from_binaries(*test_binaries)

########################################################################################################################


class BetDecodingTest(unittest.TestCase):
    def test_bet_hash_encoding(self):
        self.assertEqual(
            (hash_bets.bets_hash, hash_bets.indices, tuple(hash_bets)),
            test_expected_results,
        )

    def test_bet_indices_encoding(self):
        self.assertEqual(
            (indices_bets.bets_hash, indices_bets.indices, tuple(indices_bets)),
            test_expected_results,
        )

    def test_bet_binary_encoding(self):
        self.assertEqual(
            (binaries_bets.bets_hash, binaries_bets.indices, tuple(binaries_bets)),
            test_expected_results,
        )


class BetEquivalenceTest(unittest.TestCase):
    def test_bet_equivalence(self):
        self.assertTrue(hash_bets == indices_bets and indices_bets == binaries_bets)
