import numpy as np

import neofoodclub.math as NFCMath

__all__ = ("fix_bet_amounts",)


def fix_bet_amounts(amts: np.ndarray) -> np.ndarray:
    # fix any values below 50 to be 50, to maintain working bets
    # floor any values above max bet amount
    return np.clip(amts, 50, NFCMath.BET_AMOUNT_MAX)
