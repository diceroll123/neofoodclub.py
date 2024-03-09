from __future__ import annotations

import math
from typing import TYPE_CHECKING

from neofoodclub.models import BaseModel

if TYPE_CHECKING:
    from neofoodclub import NeoFoodClub

__all__ = [
    "MultinomialLogitModel",
]


# credit to @arsdragonfly on Github
# https://github.com/diceroll123/neofoodclub/pull/380


class MultinomialLogitModel(BaseModel):
    __slots__ = ("probabilities",)

    def __init__(self, nfc: NeoFoodClub) -> None:
        probs: list[list[float]] = [
            [1, 0, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [1, 0, 0, 0, 0],
        ]

        for arena in nfc.arenas:
            capabilities = [0, 0, 0, 0, 0]
            for pirate in arena.pirates:
                pirate_index = pirate.index - 1
                pirate_strength = LOGIT_INTERCEPTS[pirate.id]
                favorite = pirate.pfa or 0
                allergy = pirate.nfa or 0
                pirate_strength += LOGIT_PFA[pirate.id] * favorite
                pirate_strength += LOGIT_NFA[pirate.id] * allergy

                if pirate_index == 1:
                    pirate_strength += LOGIT_IS_POS2[pirate.id]
                elif pirate_index == 2:
                    pirate_strength += LOGIT_IS_POS3[pirate.id]
                elif pirate_index == 3:
                    pirate_strength += LOGIT_IS_POS4[pirate.id]

                capabilities[pirate_index + 1] = math.e**pirate_strength
                capabilities[0] += capabilities[pirate_index + 1]

            for pirate in arena.pirates:
                probs[arena.index][pirate.index] = (
                    capabilities[pirate.index] / capabilities[0]
                )
        self.probabilities = tuple(tuple(p) for p in probs)


# these magic numbers are to be updated from time to time, surely.
# for more info: https://github.com/arsdragonfly/neofoodclub

LOGIT_INTERCEPTS = {
    1: -0.5505653467394124,
    2: -2.3848388387111976,
    3: -3.478558254027841,
    4: -1.3890053586244873,
    5: -1.9176565939575803,
    6: -2.5675152075793033,
    7: -2.3143353273249554,
    8: -2.8313558799919383,
    9: -3.9019335823968233,
    10: -3.5882258128035347,
    11: -3.148241571143587,
    12: -2.169326502336402,
    13: -1.7062936735036478,
    14: -2.5503454346078662,
    15: 0.0,
    16: -1.2578784592762349,
    17: -1.059757385133957,
    18: -2.1826351058662317,
    19: -0.5605783719468618,
    20: -1.6608180038196982,
}

LOGIT_PFA = {
    1: 0.15751645987509694,
    2: 0.26306055273281875,
    3: 0.2510034096704227,
    4: 0.15957937973235922,
    5: 0.2765431062703744,
    6: 0.31686653297964323,
    7: 0.24768920967758712,
    8: 0.285786215512296,
    9: 0.41136162216849836,
    10: 0.19728776166082862,
    11: 0.1734956834280819,
    12: 0.1990091706829303,
    13: 0.21651930132706249,
    14: 0.24635467349368864,
    15: 0.2830290762546854,
    16: 0.18232531437739224,
    17: 0.16134106567663997,
    18: 0.17818977312520964,
    19: 0.22463869805679468,
    20: 0.263746530591703,
}

LOGIT_NFA = {
    1: 0.4848181644060171,
    2: 0.29222662204607447,
    3: 0.3081939124010599,
    4: 0.5563766549979002,
    5: 0.3769723616138682,
    6: 0.40991670899985494,
    7: 0.27537280651947094,
    8: 0.30379969759393904,
    9: 0.23787936378849991,
    10: 0.36415617245862325,
    11: 0.39280999692152224,
    12: 0.4926557869840621,
    13: 0.47491197095698306,
    14: 0.3458679227200068,
    15: 0.5148615215428655,
    16: 0.4190387704162794,
    17: 0.467664111731556,
    18: 0.47126361294532254,
    19: 0.39898657940724974,
    20: 0.3496888311601071,
}

LOGIT_IS_POS2 = {
    1: 0.03925417444943404,
    2: 0.021158502802025428,
    3: 0.26431710202585473,
    4: 0.31204429700932157,
    5: 0.2958881513832007,
    6: 0.35684570379893654,
    7: 0.29791053710022725,
    8: -0.11960842734248468,
    9: 0.14139644699383916,
    10: 0.5322022445170629,
    11: 0.5803122626887958,
    12: 0.1789614080028699,
    13: 0.35757006302708166,
    14: 0.17338557991857295,
    15: 0.09614330673313873,
    16: 0.04440766774743298,
    17: 0.005601266028481538,
    18: 0.3639425702087654,
    19: 0.2017361653921105,
    20: 0.22341637538608014,
}

LOGIT_IS_POS3 = {
    1: 0.2939627190206121,
    2: 0.4130356702811393,
    3: 0.6063865575638252,
    4: 0.552110704899289,
    5: 0.6067388559201926,
    6: 0.535076605287585,
    7: 0.6017889410092438,
    8: 0.09687539841588022,
    9: 0.5246865975316289,
    10: 0.955721909292628,
    11: 0.638887704243457,
    12: 0.5345584917407379,
    13: 0.6023746907980592,
    14: 0.4677057109696638,
    15: 0.41924324400559815,
    16: 0.3342400003455908,
    17: 0.1814355382118914,
    18: 0.5712980298733475,
    19: 0.5188904607014326,
    20: 0.6170900411945157,
}

LOGIT_IS_POS4 = {
    1: 0.47071198282107324,
    2: 0.6068520106680823,
    3: 0.8057835563581863,
    4: 0.8603270179693671,
    5: 0.8307141863013495,
    6: 0.7744623469044476,
    7: 0.7588736594904442,
    8: 0.537381718645823,
    9: 0.8503685148423967,
    10: 1.0968633716245804,
    11: 1.021466842781995,
    12: 0.9041512251652759,
    13: 0.9873876941901989,
    14: 0.7178740178709884,
    15: 0.542178134331314,
    16: 0.6754851261575676,
    17: 0.5015137805345499,
    18: 0.8849107940325963,
    19: 0.7538567262883,
    20: 0.9079073224460276,
}
