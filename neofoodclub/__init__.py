from importlib.metadata import version as _version

__title__ = "neofoodclub"
__author__ = "diceroll123"
__license__ = "MIT"
__copyright__ = "Copyright 2021-present diceroll123"
__version__ = _version("neofoodclub")

from .neofoodclub import *  # noqa
from .probability_model import *  # noqa

__all__ = (  # noqa
    "Math",
    "Arena",
    "Arenas",
    "Bets",
    "Chance",
    "NeoFoodClub",
    "Odds",
    "OddsChange",
    "Pirate",
    "PartialPirate",
    "ProbabilityModel",
)
