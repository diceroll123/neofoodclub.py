import datetime

import numpy as np
from dateutil import tz

from neofoodclub import Math, utils
from neofoodclub.utils import fix_bet_amounts


def test_fix_bet_amounts_min() -> None:
    # make sure it makes 50 the minimum
    amounts = fix_bet_amounts(np.array([-1000] * 10))
    assert np.sum(amounts) == Math.BET_AMOUNT_MIN * 10


def test_fix_bet_amounts_max() -> None:
    # make sure it makes 70304 the maximum
    amounts = fix_bet_amounts(np.array([100000] * 10))
    assert np.sum(amounts) == Math.BET_AMOUNT_MAX * 10


def test_fix_bet_amounts_same() -> None:
    # should be the same numbers in and out
    amounts = fix_bet_amounts(np.array([69420] * 10))
    assert np.sum(amounts) == 694200


def test_dst_offset_fall_back() -> None:
    # starting at America/New_York because I live there and I hate timezone math
    offset = utils.get_dst_offset(
        datetime.datetime(2023, 11, 5, 8, 0, 0, 0, tzinfo=tz.gettz("America/New_York")),
    )
    assert offset == datetime.timedelta(hours=-1)


def test_dst_offset_spring_forward() -> None:
    # starting at America/New_York because I live there and I hate timezone math
    offset = utils.get_dst_offset(
        datetime.datetime(2024, 3, 10, 8, 0, 0, 0, tzinfo=tz.gettz("America/New_York")),
    )
    assert offset == datetime.timedelta(hours=1)


def test_dst_offset_no_dst() -> None:
    # starting at America/New_York because I live there and I hate timezone math
    offset = utils.get_dst_offset(
        datetime.datetime(2024, 1, 1, 8, 0, 0, 0, tzinfo=tz.gettz("America/New_York")),
    )
    assert offset == datetime.timedelta(hours=0)
