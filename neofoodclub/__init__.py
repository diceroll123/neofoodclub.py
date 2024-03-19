__title__ = "neofoodclub"
__author__ = "diceroll123"
__license__ = "MIT"
__copyright__ = "Copyright 2021-present diceroll123"
__version__ = "0.0.1a"

from .arenas import *
from .bets import *
from .errors import *
from .modifier import *
from .neofoodclub import *
from .odds import *
from .odds_change import *
from .probability_model import *

__all__ = (
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
