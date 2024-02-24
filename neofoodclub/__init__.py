__title__ = "neofoodclub"
__author__ = "diceroll123"
__license__ = "MIT"
__copyright__ = "Copyright 2021-present diceroll123"
__version__ = "0.0.1a"

from .neofoodclub import *

from .arenas import *
from .bets import *
from .chance import *
from .errors import *
from .models import *
from .modifier import *
from .nfc import *
from .odds import *
from .odds_change import *
from .pirates import *

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
)
