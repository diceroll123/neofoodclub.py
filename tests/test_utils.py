import numpy as np
from neofoodclub.math import BET_AMOUNT_MAX, BET_AMOUNT_MIN
from neofoodclub.nfc import NeoFoodClub
from neofoodclub.utils import fix_bet_amounts


def test_fix_bet_amounts_min():
    # make sure it makes 50 the minimum
    amounts = fix_bet_amounts(np.array([-1000] * 10))
    assert np.sum(amounts) == BET_AMOUNT_MIN * 10


def test_fix_bet_amounts_max():
    # make sure it makes 70304 the maximum
    amounts = fix_bet_amounts(np.array([100000] * 10))
    assert np.sum(amounts) == BET_AMOUNT_MAX * 10


def test_fix_bet_amounts_same():
    # should be the same numbers in and out
    amounts = fix_bet_amounts(np.array([69420] * 10))
    assert np.sum(amounts) == 694200


def test_bets_table(nfc: NeoFoodClub):
    bets = nfc.make_bustproof_bets()
    table = bets.table
    table_str = """
+---+-----------+--------+----------+--------+------------+
| # | Shipwreck | Lagoon | Treasure | Hidden |  Harpoon   |
+---+-----------+--------+----------+--------+------------+
| 1 |           |        |          |        | Federismo  |
| 2 |           |        |          |        | Franchisco |
| 3 |           |        |          |        | Blackbeard |
| 4 |           |        |          |        |   Stuff    |
+---+-----------+--------+----------+--------+------------+
""".strip()
    assert table == table_str


def test_bets_stats_table(nfc: NeoFoodClub):
    bets = nfc.make_bustproof_bets()
    table = bets.stats_table
    table_str = """
+--------+------+---------+--------+-----+-----------+--------+----------+--------+------------+
|   #    | Odds |   ER    | MaxBet | Hex | Shipwreck | Lagoon | Treasure | Hidden |  Harpoon   |
+--------+------+---------+--------+-----+-----------+--------+----------+--------+------------+
|   1    |  8   | 0.641:1 | 125000 | 0x8 |           |        |          |        | Federismo  |
|   2    |  2   | 1.430:1 | 500000 | 0x4 |           |        |          |        | Franchisco |
|   3    |  4   | 0.619:1 | 250000 | 0x2 |           |        |          |        | Blackbeard |
|   4    |  12  | 0.600:1 | 83334  | 0x1 |           |        |          |        |   Stuff    |
+--------+------+---------+--------+-----+-----------+--------+----------+--------+------------+
| Total: |      |  3.290  |        |     |           |        |          |        |            |
+--------+------+---------+--------+-----+-----------+--------+----------+--------+------------+
""".strip()
    assert table == table_str


def test_bets_stats_table_with_net_expected(nfc: NeoFoodClub):
    # we are testing for NE > 0, so we need a bet amount
    new_nfc = nfc.copy()
    new_nfc.bet_amount = 8000
    bets = new_nfc.make_bustproof_bets()
    table = bets.stats_table
    table_str = """
+--------+----------+------+--------+---------+----------+--------+-----+-----------+--------+----------+--------+------------+
|   #    | Bet Amt. | Odds | Payoff |   ER    |    NE    | MaxBet | Hex | Shipwreck | Lagoon | Treasure | Hidden |  Harpoon   |
+--------+----------+------+--------+---------+----------+--------+-----+-----------+--------+----------+--------+------------+
|   1    |   2000   |  8   | 16000  | 0.641:1 | -717.95  | 125000 | 0x8 |           |        |          |        | Federismo  |
|   2    |   8000   |  2   | 16000  | 1.430:1 | 3441.76  | 500000 | 0x4 |           |        |          |        | Franchisco |
|   3    |   4000   |  4   | 16000  | 0.619:1 | -1523.81 | 250000 | 0x2 |           |        |          |        | Blackbeard |
|   4    |   1333   |  12  | 15996  | 0.600:1 | -533.20  | 83334  | 0x1 |           |        |          |        |   Stuff    |
+--------+----------+------+--------+---------+----------+--------+-----+-----------+--------+----------+--------+------------+
| Total: |  15,333  |      |        |  3.290  |  666.80  |        |     |           |        |          |        |            |
+--------+----------+------+--------+---------+----------+--------+-----+-----------+--------+----------+--------+------------+
""".strip()
    assert table == table_str
