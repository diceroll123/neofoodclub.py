import numpy as np

import neofoodclub.math as NFCMath

__all__ = ("fix_bet_amounts",)


def fix_bet_amounts(amts: np.ndarray) -> np.ndarray:
    """:class:`np.ndarray`: Returns a "clamped" array of the bet amounts passed in where the minimum value is 50 and
    the maximum value is 70304, which is the highest value that the current hashing algorithm can understand."""
    # fix any values below 50 to be 50, to maintain working bets
    # floor any values above max bet amount
    return np.clip(amts, 50, NFCMath.BET_AMOUNT_MAX)
