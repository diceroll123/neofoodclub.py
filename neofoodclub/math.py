import functools
import itertools
import math
from collections import defaultdict
from string import ascii_lowercase, ascii_uppercase
from typing import Tuple, Dict, Optional, List

import numpy as np

from .types import ValidOdds, ValidIndex, BetOdds
from numba import njit
from numba.core import types
from numba.typed import Dict as TypedDict

# at least for now, we won't be exposing the numba methods.
__all__ = (
    "precompile",
    "pirate_binary",
    "pirates_binary",
    "binary_to_indices",
    "bet_amounts_to_string",
    "bet_string_to_bet_amounts",
    "bet_string_to_bet_indices",
    "bet_string_to_bets_amount",
    "bet_string_to_bets",
    "bet_url_value",
    "make_probabilities",
    "get_bet_odds_from_bets",
    "make_round_dicts",
    "FULL_BETS",
)


BET_AMOUNT_MIN = 50

BET_AMOUNT_MAX = 70304
# this fixed number is the max that NeoFoodClub can encode,
# given the current bet (and bet amount) encoding specification

float_array = types.float64[:]


def precompile():
    # run the numba methods to compile, and fill some caches so they're speedier
    # using garbage data is fine for compiling with.
    bet_string_to_bet_amounts("aaa")
    make_round_dicts(
        tuple((1.0, 1.0, 1.0, 1.0, 1.0) for _ in range(5)),
        tuple((1.0, 1.0, 1.0, 1.0, 1.0) for _ in range(5)),
    )

    for a in range(5):
        for b in range(5):
            for c in range(5):
                for d in range(5):
                    for e in range(5):
                        bet_binary = pirates_binary((a, b, c, d, e))
                        binary_to_indices(bet_binary)


@functools.lru_cache(maxsize=None)
def pirate_binary(index: int, arena: int) -> int:
    # binary position of the pirate in its arena, it's just a 1 with 19 zeros surrounding it
    # this assumes the index is actually index+1 because of odds etc starting with a 1 in the 0th index
    if index == 0:
        return 0
    return 1 << (19 - (index - 1 + arena * 4))


@functools.lru_cache(maxsize=None)
def pirates_binary(bet_indices: Tuple[int, ...]) -> int:
    # the inverse of binary_to_indices
    # turns (1, 2, 3, 4, 2) (for example) into 0b10000100001000010100, a bet-binary compatible number
    return sum(pirate_binary(index, arena) for arena, index in enumerate(bet_indices))


@njit()
def binary_to_indices_numba(bet_binary: int) -> List[int]:
    # thanks @mikeshardmind
    # the inverse of pirates_binary
    ret = [1 for _ in range(0)]
    for mask in (0xF0000, 0xF000, 0xF00, 0xF0, 0xF):
        val = mask & bet_binary
        if val:
            # bit length intentionally offset here
            # numba doesn't implement .bit_length for int
            bit_length, v2 = -1, val
            while v2:
                v2 >>= 1
                bit_length += 1
            val = 4 - (bit_length % 4)
        ret.append(val)
    return ret


@functools.lru_cache(maxsize=3125)
def binary_to_indices(bet_binary: int) -> Tuple[int, ...]:
    # convenience method to cache the list as a tuple because i don't think Numba can *do* tuples.
    return tuple(binary_to_indices_numba(bet_binary))


def bet_amounts_to_string(bet_amounts: Dict[int, int]) -> str:
    letters = ""
    for idx, value in bet_amounts.items():
        e = ""
        letter = int(value) % BET_AMOUNT_MAX + BET_AMOUNT_MAX
        for _ in range(3):
            e = (ascii_lowercase + ascii_uppercase)[letter % 52] + e
            letter //= 52
        letters += e

    return letters


@njit()
def bet_string_to_bet_amounts_numba(bet_string: str) -> List[Optional[int]]:
    nums: List[Optional[int]] = []
    chunked = [bet_string[i : i + 3] for i in range(0, len(bet_string), 3)]

    for p in chunked:
        e = 0
        for n in p:
            e *= 52
            e += (ascii_lowercase + ascii_uppercase).index(n)

        value = e - BET_AMOUNT_MAX
        if value < BET_AMOUNT_MIN:
            nums.append(None)
        else:
            nums.append(value)

    return nums


@functools.lru_cache
def bet_string_to_bet_amounts(bet_string: str) -> Tuple[Optional[int], ...]:
    # convenience method to cache the list as a tuple because i don't think Numba can *do* tuples.
    return tuple(bet_string_to_bet_amounts_numba(bet_string))


@functools.lru_cache(maxsize=256)
def bet_string_to_bet_indices(bet_string: str) -> Tuple[Tuple[int, ...], ...]:
    # TODO: look into numba-fying (tried once now, it was about 3x slower to get the same result uncached)
    indices = [ord(letter) - 97 for letter in bet_string]
    s = itertools.chain.from_iterable((e // 5, e % 5) for e in indices)
    # https://docs.python.org/3/library/itertools.html#itertools-recipes (see "grouper" recipe)
    return tuple(
        bet for bet in itertools.zip_longest(*[iter(s)] * 5, fillvalue=0) if any(bet)
    )


def bet_string_to_bets_amount(bet_string: str) -> int:
    # the amount of bets in the set, that is
    return len(bet_string_to_bet_indices(bet_string))


def bet_string_to_bets(bet_string: str) -> Dict:
    bets = bet_string_to_bet_indices(bet_string)

    bet_length = len(bets)
    if bet_length not in range(1, 16):
        # currently support 15 bets still for reverse-compatibility i guess
        raise ValueError

    return dict(zip(range(1, bet_length + 1), bets))


def bet_url_value(bet_indices: Tuple[Tuple[int, ...], ...]) -> str:
    flat = itertools.chain.from_iterable(bet_indices)
    return "".join(
        ascii_lowercase[multiplier * 5 + adder]
        for multiplier, adder in itertools.zip_longest(*[iter(flat)] * 2, fillvalue=0)
    )


def make_probabilities(opening_odds: List[List[ValidOdds]]) -> List[List[float]]:
    # TODO: look into numba-fying, so far any attempts have been *SLOWER*

    _min = [
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
    ]

    _max = [
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
    ]

    _std = [
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0],
    ]

    # turns out we only use _std values in the python implementation of NFC
    # keeping the _used math to avoid confusion between NFC impls
    # _used = [
    #     [1.0, 0.0, 0.0, 0.0, 0.0],
    #     [1.0, 0.0, 0.0, 0.0, 0.0],
    #     [1.0, 0.0, 0.0, 0.0, 0.0],
    #     [1.0, 0.0, 0.0, 0.0, 0.0],
    #     [1.0, 0.0, 0.0, 0.0, 0.0],
    # ]

    for e in range(5):

        min_prob = 0.0
        max_prob = 0.0
        for r in range(1, 5):
            pirate_odd = opening_odds[e][r]
            if pirate_odd == 13:
                _min[e][r] = 0
                _max[e][r] = 1 / 13
            elif pirate_odd == 2:
                _min[e][r] = 1 / 3
                _max[e][r] = 1
            else:
                _min[e][r] = 1 / (1 + pirate_odd)
                _max[e][r] = 1 / pirate_odd
            min_prob += _min[e][r]
            max_prob += _max[e][r]

        for r in range(1, 5):
            min_original = _min[e][r]
            max_original = _max[e][r]

            _min[e][r] = max(min_original, 1 + max_original - max_prob)
            _max[e][r] = min(max_original, 1 + min_original - min_prob)
            _std[e][r] = (
                0.05 if opening_odds[e][r] == 13 else (_min[e][r] + _max[e][r]) / 2
            )

        for rectify_level in range(2, 13):
            rectify_count = 0
            std_total = 0.0
            rectify_value = 0.0
            max_rectify_value = 1.0
            for r in range(1, 5):
                std_total += _std[e][r]
                if opening_odds[e][r] <= rectify_level:
                    rectify_count += 1
                    rectify_value += _std[e][r] - _min[e][r]
                    max_rectify_value = min(
                        [
                            max_rectify_value,
                            _max[e][r] - _min[e][r],
                        ]
                    )

            if std_total == 1:
                break

            if not (
                std_total - rectify_value > 1
                or rectify_count == 0
                or max_rectify_value * rectify_count < rectify_value + 1 - std_total
            ):
                rectify_value += 1 - std_total
                rectify_value /= rectify_count
                for r in range(1, 5):
                    if opening_odds[e][r] <= rectify_level:
                        _std[e][r] = _min[e][r] + rectify_value
                break

    #     return_sum = 0.0
    #     for r in range(1, 5):
    #         _used[e][r] = _std[e][r]
    #         return_sum += _used[e][r]
    #
    #     for r in range(1, 5):
    #         _used[e][r] /= return_sum
    #
    # return dict(min=_min, max=_max, std=_std, used=_used)

    return _std


def get_bet_odds_from_bets(
    bets: Tuple[Tuple[ValidIndex, ...], ...],
    bet_odds: List[ValidOdds],
    probabilities: List[List[float]],
) -> List[BetOdds]:
    # ib is a binary format to represent bets.
    # It works on 20 bits (because there are 20 pirates).
    # Each of the bits of an ib represents whether it accepts some pirate. (whether the bet can win if this pirate wins)
    # From most significant to least significant bits, the pirates are in the usual arena-by-arena order.
    # This binary format allows some easy operations:
    # ib1&ib2 accepts the pirates that both ib1 and ib2 accepts. The winning combinations of ib1&ib2 is the intersection of the winning combinations of ib1 and ib2.
    # ib1|ib2 accepts the pirates that ib1 or ib2 accepts. The winning combinations of ib1&ib2 is BIGGER or equal to the union of the winning combinations of ib1 and ib2.

    # bit_masks[i] will accept pirates from arena i and only them. bit_masks[4] == 0b1111, bit_masks[3] == 0b11110000, etc...

    # all_ib will accept all pirates. all_ib = 0b11111111111111111111 (20 '1's)
    all_ib = 0xFFFFF

    # pir_ib[i] will accept pirates of index i (from 0 to 3) pir_ib[0] = 0b10001000100010001000, pir_ib[1] = 0b01000100010001000100, pir_ib[2] = 0b00100010001000100010, pir_ib[3] = 0b00010001000100010001
    pir_ib = [0x88888, 0x44444, 0x22222, 0x11111]

    bit_masks = (0xF0000, 0xF000, 0xF00, 0xF0, 0xF)

    # checks if there are possible winning combinations for ib
    def ib_doable(_ib) -> bool:
        return (
            _ib & bit_masks[0]
            and _ib & bit_masks[1]
            and _ib & bit_masks[2]
            and _ib & bit_masks[3]
            and _ib & bit_masks[4]
        )

    # expand_ib_object takes an ibObj and returns an ibObj.
    # The returned bet set "res" satisfies the following properties:
    # - for all possible winning combination it has the same value as the old set
    # - two different bets in "res" will have 0 common accepted winning combinations
    # - all winning combinations are accepted by a bet in "res" (giving the value 0 to combinations that busts)
    # It's done so that the probability distribution becomes easy to compute.
    def expand_ib_object(ib_obj) -> Dict[int, int]:
        res = {all_ib: 0}
        for ib_bet, winnings in sorted(ib_obj.items()):
            for ib_key in list(res.keys()):
                com = ib_bet & ib_key
                if ib_doable(com):
                    val_key = res.pop(ib_key)
                    res[com] = winnings + val_key
                    for _ar in bit_masks:
                        tst = ib_key ^ (com & _ar)
                        if ib_doable(tst):
                            res[tst] = val_key
                            ib_key = (ib_key & ~_ar) | (com & _ar)
        return res

    # computes the probability that the winning combination is accepted by ib
    def ib_prob(_ib: int) -> float:
        total_prob = 1.0
        for _i in range(5):
            ar_prob = 0.0
            for _j in range(4):
                if _ib & bit_masks[_i] & pir_ib[_j]:
                    ar_prob += probabilities[_i][_j + 1]
            total_prob *= ar_prob
        return total_prob

    # Takes a bet set in ibObj satisfying the following condition:
    # - two different bets in the bet set will have 0 common accepted winning combinations
    # and computes its win table.
    def compute_win_table(ib_exp_obj: Dict[int, int]) -> List[BetOdds]:
        win_table: Dict[int, float] = defaultdict(float)
        for k, v in ib_exp_obj.items():
            win_table[v] += ib_prob(k)

        sorted_e: List[BetOdds] = sorted(
            [
                {
                    "value": value,
                    "probability": probability,
                    "cumulative": 0.0,
                    "tail": 1.0,
                }
                for value, probability in win_table.items()
            ],
            key=lambda ee: ee["value"],
        )

        cumulative = 0.0
        tail = 1.0
        for _a in range(len(sorted_e)):
            cumulative += sorted_e[_a]["probability"]
            sorted_e[_a]["cumulative"] = cumulative
            sorted_e[_a]["tail"] = tail
            tail -= sorted_e[_a]["probability"]

        return sorted_e

    convert_pir_ib = [all_ib] + pir_ib
    bets_to_ib: Dict[int, int] = defaultdict(int)
    for key, bet_value in enumerate(bets):
        ib = 0
        for _x in range(5):
            # this adds pirates meant by bet[i] to the pirates accepted by ib.
            ib |= convert_pir_ib[bet_value[_x]] & bit_masks[_x]
        bets_to_ib[ib] += bet_odds[key]

    return compute_win_table(expand_ib_object(bets_to_ib))


@njit()
def make_round_dicts(
    stds: Tuple[Tuple[types.float32, ...], ...],
    odds: Tuple[Tuple[types.int8, ...], ...],
):
    _dict = TypedDict.empty(
        key_type=types.unicode_type,
        value_type=float_array,
    )

    _bins = np.zeros(3124)
    _stds = np.zeros(3124)
    _odds = np.zeros(3124)
    _ers = np.zeros(3124)
    _maxbets = np.zeros(3124)

    arr_index = 0

    for _a in range(5):
        for _b in range(5):
            for _c in range(5):
                for _d in range(5):
                    for _e in range(5):
                        total_bin = 0
                        total_stds = 1.0
                        total_odds = 1.0

                        for arena, index in enumerate((_a, _b, _c, _d, _e)):
                            if index == 0:
                                continue
                            total_bin += 1 << (19 - (index - 1 + arena * 4))
                            total_stds *= stds[arena][index]
                            total_odds *= odds[arena][index]

                        if total_bin == 0:
                            continue

                        _bins[arr_index] = total_bin
                        _stds[arr_index] = total_stds
                        _odds[arr_index] = total_odds
                        _ers[arr_index] = total_stds * total_odds
                        _maxbets[arr_index] = math.ceil(1_000_000 / total_odds)

                        arr_index += 1

    _dict["bins"] = _bins
    _dict["std"] = _stds
    _dict["odds"] = _odds
    _dict["ers"] = _ers
    _dict["maxbets"] = _maxbets

    return _dict


# fmt: off
FULL_BETS = np.array([780, 781, 782, 783, 785, 786, 787, 788, 790, 791, 792, 793, 795, 796, 797, 798, 805, 806, 807, 808, 810, 811, 812, 813, 815, 816, 817, 818, 820, 821, 822, 823, 830, 831, 832, 833, 835, 836, 837, 838, 840, 841, 842, 843, 845, 846, 847, 848, 855, 856, 857, 858, 860, 861, 862, 863, 865, 866, 867, 868, 870, 871, 872, 873, 905, 906, 907, 908, 910, 911, 912, 913, 915, 916, 917, 918, 920, 921, 922, 923, 930, 931, 932, 933, 935, 936, 937, 938, 940, 941, 942, 943, 945, 946, 947, 948, 955, 956, 957, 958, 960, 961, 962, 963, 965, 966, 967, 968, 970, 971, 972, 973, 980, 981, 982, 983, 985, 986, 987, 988, 990, 991, 992, 993, 995, 996, 997, 998, 1030, 1031, 1032, 1033, 1035, 1036, 1037, 1038, 1040, 1041, 1042, 1043, 1045, 1046, 1047, 1048, 1055, 1056, 1057, 1058, 1060, 1061, 1062, 1063, 1065, 1066, 1067, 1068, 1070, 1071, 1072, 1073, 1080, 1081, 1082, 1083, 1085, 1086, 1087, 1088, 1090, 1091, 1092, 1093, 1095, 1096, 1097, 1098, 1105, 1106, 1107, 1108, 1110, 1111, 1112, 1113, 1115, 1116, 1117, 1118, 1120, 1121, 1122, 1123, 1155, 1156, 1157, 1158, 1160, 1161, 1162, 1163, 1165, 1166, 1167, 1168, 1170, 1171, 1172, 1173, 1180, 1181, 1182, 1183, 1185, 1186, 1187, 1188, 1190, 1191, 1192, 1193, 1195, 1196, 1197, 1198, 1205, 1206, 1207, 1208, 1210, 1211, 1212, 1213, 1215, 1216, 1217, 1218, 1220, 1221, 1222, 1223, 1230, 1231, 1232, 1233, 1235, 1236, 1237, 1238, 1240, 1241, 1242, 1243, 1245, 1246, 1247, 1248, 1405, 1406, 1407, 1408, 1410, 1411, 1412, 1413, 1415, 1416, 1417, 1418, 1420, 1421, 1422, 1423, 1430, 1431, 1432, 1433, 1435, 1436, 1437, 1438, 1440, 1441, 1442, 1443, 1445, 1446, 1447, 1448, 1455, 1456, 1457, 1458, 1460, 1461, 1462, 1463, 1465, 1466, 1467, 1468, 1470, 1471, 1472, 1473, 1480, 1481, 1482, 1483, 1485, 1486, 1487, 1488, 1490, 1491, 1492, 1493, 1495, 1496, 1497, 1498, 1530, 1531, 1532, 1533, 1535, 1536, 1537, 1538, 1540, 1541, 1542, 1543, 1545, 1546, 1547, 1548, 1555, 1556, 1557, 1558, 1560, 1561, 1562, 1563, 1565, 1566, 1567, 1568, 1570, 1571, 1572, 1573, 1580, 1581, 1582, 1583, 1585, 1586, 1587, 1588, 1590, 1591, 1592, 1593, 1595, 1596, 1597, 1598, 1605, 1606, 1607, 1608, 1610, 1611, 1612, 1613, 1615, 1616, 1617, 1618, 1620, 1621, 1622, 1623, 1655, 1656, 1657, 1658, 1660, 1661, 1662, 1663, 1665, 1666, 1667, 1668, 1670, 1671, 1672, 1673, 1680, 1681, 1682, 1683, 1685, 1686, 1687, 1688, 1690, 1691, 1692, 1693, 1695, 1696, 1697, 1698, 1705, 1706, 1707, 1708, 1710, 1711, 1712, 1713, 1715, 1716, 1717, 1718, 1720, 1721, 1722, 1723, 1730, 1731, 1732, 1733, 1735, 1736, 1737, 1738, 1740, 1741, 1742, 1743, 1745, 1746, 1747, 1748, 1780, 1781, 1782, 1783, 1785, 1786, 1787, 1788, 1790, 1791, 1792, 1793, 1795, 1796, 1797, 1798, 1805, 1806, 1807, 1808, 1810, 1811, 1812, 1813, 1815, 1816, 1817, 1818, 1820, 1821, 1822, 1823, 1830, 1831, 1832, 1833, 1835, 1836, 1837, 1838, 1840, 1841, 1842, 1843, 1845, 1846, 1847, 1848, 1855, 1856, 1857, 1858, 1860, 1861, 1862, 1863, 1865, 1866, 1867, 1868, 1870, 1871, 1872, 1873, 2030, 2031, 2032, 2033, 2035, 2036, 2037, 2038, 2040, 2041, 2042, 2043, 2045, 2046, 2047, 2048, 2055, 2056, 2057, 2058, 2060, 2061, 2062, 2063, 2065, 2066, 2067, 2068, 2070, 2071, 2072, 2073, 2080, 2081, 2082, 2083, 2085, 2086, 2087, 2088, 2090, 2091, 2092, 2093, 2095, 2096, 2097, 2098, 2105, 2106, 2107, 2108, 2110, 2111, 2112, 2113, 2115, 2116, 2117, 2118, 2120, 2121, 2122, 2123, 2155, 2156, 2157, 2158, 2160, 2161, 2162, 2163, 2165, 2166, 2167, 2168, 2170, 2171, 2172, 2173, 2180, 2181, 2182, 2183, 2185, 2186, 2187, 2188, 2190, 2191, 2192, 2193, 2195, 2196, 2197, 2198, 2205, 2206, 2207, 2208, 2210, 2211, 2212, 2213, 2215, 2216, 2217, 2218, 2220, 2221, 2222, 2223, 2230, 2231, 2232, 2233, 2235, 2236, 2237, 2238, 2240, 2241, 2242, 2243, 2245, 2246, 2247, 2248, 2280, 2281, 2282, 2283, 2285, 2286, 2287, 2288, 2290, 2291, 2292, 2293, 2295, 2296, 2297, 2298, 2305, 2306, 2307, 2308, 2310, 2311, 2312, 2313, 2315, 2316, 2317, 2318, 2320, 2321, 2322, 2323, 2330, 2331, 2332, 2333, 2335, 2336, 2337, 2338, 2340, 2341, 2342, 2343, 2345, 2346, 2347, 2348, 2355, 2356, 2357, 2358, 2360, 2361, 2362, 2363, 2365, 2366, 2367, 2368, 2370, 2371, 2372, 2373, 2405, 2406, 2407, 2408, 2410, 2411, 2412, 2413, 2415, 2416, 2417, 2418, 2420, 2421, 2422, 2423, 2430, 2431, 2432, 2433, 2435, 2436, 2437, 2438, 2440, 2441, 2442, 2443, 2445, 2446, 2447, 2448, 2455, 2456, 2457, 2458, 2460, 2461, 2462, 2463, 2465, 2466, 2467, 2468, 2470, 2471, 2472, 2473, 2480, 2481, 2482, 2483, 2485, 2486, 2487, 2488, 2490, 2491, 2492, 2493, 2495, 2496, 2497, 2498, 2655, 2656, 2657, 2658, 2660, 2661, 2662, 2663, 2665, 2666, 2667, 2668, 2670, 2671, 2672, 2673, 2680, 2681, 2682, 2683, 2685, 2686, 2687, 2688, 2690, 2691, 2692, 2693, 2695, 2696, 2697, 2698, 2705, 2706, 2707, 2708, 2710, 2711, 2712, 2713, 2715, 2716, 2717, 2718, 2720, 2721, 2722, 2723, 2730, 2731, 2732, 2733, 2735, 2736, 2737, 2738, 2740, 2741, 2742, 2743, 2745, 2746, 2747, 2748, 2780, 2781, 2782, 2783, 2785, 2786, 2787, 2788, 2790, 2791, 2792, 2793, 2795, 2796, 2797, 2798, 2805, 2806, 2807, 2808, 2810, 2811, 2812, 2813, 2815, 2816, 2817, 2818, 2820, 2821, 2822, 2823, 2830, 2831, 2832, 2833, 2835, 2836, 2837, 2838, 2840, 2841, 2842, 2843, 2845, 2846, 2847, 2848, 2855, 2856, 2857, 2858, 2860, 2861, 2862, 2863, 2865, 2866, 2867, 2868, 2870, 2871, 2872, 2873, 2905, 2906, 2907, 2908, 2910, 2911, 2912, 2913, 2915, 2916, 2917, 2918, 2920, 2921, 2922, 2923, 2930, 2931, 2932, 2933, 2935, 2936, 2937, 2938, 2940, 2941, 2942, 2943, 2945, 2946, 2947, 2948, 2955, 2956, 2957, 2958, 2960, 2961, 2962, 2963, 2965, 2966, 2967, 2968, 2970, 2971, 2972, 2973, 2980, 2981, 2982, 2983, 2985, 2986, 2987, 2988, 2990, 2991, 2992, 2993, 2995, 2996, 2997, 2998, 3030, 3031, 3032, 3033, 3035, 3036, 3037, 3038, 3040, 3041, 3042, 3043, 3045, 3046, 3047, 3048, 3055, 3056, 3057, 3058, 3060, 3061, 3062, 3063, 3065, 3066, 3067, 3068, 3070, 3071, 3072, 3073, 3080, 3081, 3082, 3083, 3085, 3086, 3087, 3088, 3090, 3091, 3092, 3093, 3095, 3096, 3097, 3098, 3105, 3106, 3107, 3108, 3110, 3111, 3112, 3113, 3115, 3116, 3117, 3118, 3120, 3121, 3122, 3123])
