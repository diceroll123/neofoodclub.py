import numpy as np

from neofoodclub import Bets, NeoFoodClub

# fmt: off
__all__ = (
    "make_max_ter_bets_numpy",
)
# fmt: on


def make_max_ter_bets_numpy(nfc: NeoFoodClub) -> Bets:
    """A convenience method to make max-ter bets with numpy.

    The way to implement the underlying sorting algorithm that
    numpy uses for argsort escapes me, so in the meantime,
    we just use it.

    We do this because somehow it's got the best ROI.
    """

    values = nfc.max_ters()
    sorted_values = np.argsort(values)

    if not nfc.modifier.is_reverse:
        sorted_values = sorted_values[::-1]

    return nfc.make_bets_from_array_indices(sorted_values[: nfc.max_amount_of_bets])  # type: ignore
