import numpy as np
from neofoodclub.math import BET_AMOUNT_MAX, BET_AMOUNT_MIN
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
