import copy
import unittest
from typing import Any, Dict, Tuple

from neofoodclub import NeoFoodClub
from neofoodclub.errors import InvalidData, NoPositiveArenas

# i picked the smallest round I could quickly find
test_round_data: Dict[str, Any] = {
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

# this is a crazy bet! (all arenas have a pirate bet)
crazy_test_bet_hash = "ltqvqwgimhqtvrnywrwvijwnn"
crazy_test_indices: Tuple[Tuple[int, ...], ...] = (
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
crazy_test_binaries: Tuple[int, ...] = (
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

gambit_test_binaries: Tuple[int, ...] = (
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

test_expected_results = (crazy_test_bet_hash, crazy_test_indices, crazy_test_binaries)

test_nfc = NeoFoodClub(test_round_data)
test_nfc_with_amounts = NeoFoodClub(test_round_data, bet_amount=8000)

crazy_bets_from_hash = test_nfc.make_bets_from_hash(crazy_test_bet_hash)
crazy_bets_from_indices = test_nfc.make_bets_from_indices(crazy_test_indices)
crazy_bets_from_binaries = test_nfc.make_bets_from_binaries(*crazy_test_binaries)

########################################################################################################################


class BetDecodingTest(unittest.TestCase):
    def crazy_test_bet_hash_encoding(self):
        self.assertEqual(
            (
                crazy_bets_from_hash.bets_hash,
                crazy_bets_from_hash.indices,
                tuple(crazy_bets_from_hash),
            ),
            test_expected_results,
        )

    def test_bet_indices_encoding(self):
        self.assertEqual(
            (
                crazy_bets_from_indices.bets_hash,
                crazy_bets_from_indices.indices,
                tuple(crazy_bets_from_indices),
            ),
            test_expected_results,
        )

    def test_bet_binary_encoding(self):
        self.assertEqual(
            (
                crazy_bets_from_binaries.bets_hash,
                crazy_bets_from_binaries.indices,
                tuple(crazy_bets_from_binaries),
            ),
            test_expected_results,
        )


class BetEquivalenceTest(unittest.TestCase):
    def test_bet_equivalence(self):
        self.assertTrue(
            crazy_bets_from_hash == crazy_bets_from_indices
            and crazy_bets_from_indices == crazy_bets_from_binaries
        )


class BustproofTest(unittest.TestCase):
    def test_bustproof_generator(self):
        self.assertTrue(test_nfc.make_bustproof_bets().is_bustproof)

    def test_bustproof_generator_amount(self):
        # for this round data we have, this makes 4 bets.
        self.assertTrue(len(test_nfc.make_bustproof_bets()) == 4)

    def test_bustproof_generator_no_positives(self):
        with self.assertRaises(NoPositiveArenas):
            # modify our round object to have no positives (just need to change the last arena for this one)
            round_data = copy.deepcopy(test_round_data)
            # will give the arena a -50% ratio
            round_data["currentOdds"][-1] = [1, 2, 2, 2, 2]
            no_positive_nfc = NeoFoodClub(round_data)
            no_positive_nfc.make_bustproof_bets()

    def test_bustproof_minimal(self):
        self.assertTrue(
            test_nfc.make_bets_from_binaries(0x1, 0x2, 0x4, 0x8).is_bustproof
        )

    def test_not_bustproof_single(self):
        self.assertFalse(test_nfc.make_bets_from_binaries(0x1).is_bustproof)

    def test_not_bustproof(self):
        self.assertFalse(crazy_bets_from_binaries.is_bustproof)


class CrazyBetsTest(unittest.TestCase):
    def test_crazy_bet_generator(self):
        self.assertTrue(test_nfc.make_crazy_bets().is_crazy)

    def test_crazy_bets(self):
        self.assertTrue(crazy_bets_from_binaries.is_crazy)

    def test_not_crazy_bets(self):
        self.assertFalse(test_nfc.make_bets_from_binaries(0x1, 0x2, 0x4, 0x8).is_crazy)


class MaxterBetsTest(unittest.TestCase):
    def test_mer_bets_no_bet_amount(self):
        # make sure it creates the same bets, regardless of order
        bets = test_nfc.make_max_ter_bets()

        self.assertEqual(
            set(bets),
            {
                0x104,
                0x4,
                0x80104,
                0x1104,
                0x10104,
                0x80004,
                0x101,
                0x2104,
                0x8104,
                0x204,
            },
        )

    def test_mer_bets_with_amounts(self):
        # make sure it creates the same bets, regardless of order
        bets = test_nfc_with_amounts.make_max_ter_bets()

        self.assertEqual(
            set(bets),
            {
                0x104,
                0x4,
                0x80104,
                0x1104,
                0x10104,
                0x80004,
                0x101,
                0x2104,
                0x8104,
                0x204,
            },
        )

    def test_mer_winning_odds(self):
        # because the mer set for the test round we have happened to win 26 units
        bets = test_nfc_with_amounts.make_max_ter_bets()
        self.assertTrue(test_nfc_with_amounts.get_win_units(bets) == 26)

    def test_mer_bet_amounts(self):
        # because the mer set for the test round we have happened to win 26 units
        bets = test_nfc_with_amounts.make_max_ter_bets()
        self.assertEqual(bets.bet_amounts.sum(), 80000)


class GambitBetsTest(unittest.TestCase):
    def test_gambit_bet_generator(self):
        self.assertTrue(test_nfc.make_gambit_bets().is_gambit)

    def test_gambit_bets(self):
        self.assertTrue(
            test_nfc.make_bets_from_binaries(*gambit_test_binaries).is_gambit
        )

    def test_not_gambit_bets(self):
        self.assertFalse(crazy_bets_from_binaries.is_gambit)

    def test_minimum_gambit_bets(self):
        self.assertTrue(test_nfc.make_bets_from_binaries(0x88888, 0x8).is_gambit)


class BetsErrorsTest(unittest.TestCase):
    def test_too_many_bet_amounts_from_binaries(self):
        with self.assertRaises(InvalidData):
            test_nfc.make_bets_from_binaries(0x1, amounts=[50, 50])

    def test_too_many_bet_amounts_from_indices(self):
        with self.assertRaises(InvalidData):
            test_nfc.make_bets_from_indices([(1, 0, 0, 0, 0)], amounts=[50, 50])

    def test_too_many_bet_amounts_from_hash(self):
        with self.assertRaises(InvalidData):
            test_nfc.make_bets_from_hash("faa", amounts=[50, 50])
