from collections import namedtuple
import datetime
import json

import numpy as np

import neofoodclub.math as NFCMath
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Set, Sequence

import dateutil
from dateutil.tz import UTC, tzutc

from dateutil.parser import parse

from neofoodclub.types import (
    RoundData,
    FoodID,
    ValidOdds,
    ValidIndex,
    PirateID,
)

ARENA_NAMES = ["Shipwreck", "Lagoon", "Treasure", "Hidden", "Harpoon"]
PIRATE_NAMES = {
    1: "Dan",
    2: "Sproggie",
    3: "Orvinn",
    4: "Lucky",
    5: "Edmund",
    6: "Peg Leg",
    7: "Bonnie",
    8: "Puffo",
    9: "Stuff",
    10: "Squire",
    11: "Crossblades",
    12: "Stripey",
    13: "Ned",
    14: "Fairfax",
    15: "Gooblah",
    16: "Franchisco",
    17: "Federismo",
    18: "Blackbeard",
    19: "Buck",
    20: "Tailhook",
}

__all__ = ("NeoFoodClub",)


class PirateMixin:
    @property
    def name(self):
        return PIRATE_NAMES[self.id]

    @property
    def image(self):
        return f"http://images.neopets.com/pirates/fc/fc_pirate_{self.id}.gif"


class PartialPirate(PirateMixin):
    def __init__(self, _id: int):
        self._id = _id

    @property
    def id(self) -> int:
        return self._id

    def __repr__(self):
        return f"<NaivePirate name={self.name}>"


class OddsChange:
    __slots__ = (
        "_index",
        "_data",
        "_round_data",
    )

    def __init__(self, *, index: int, data, round_data):
        self._index = index
        self._data = data  # to check against each other
        self._round_data = round_data

    @property
    def data(self) -> Dict:
        return self._data

    @property
    def index(self) -> int:
        return self._index

    @property
    def raw_timestamp(self) -> str:
        return self._data["t"]

    @property
    def timestamp(self) -> datetime.datetime:
        return dateutil.parser.parse(self.raw_timestamp).astimezone(UTC)

    @property
    def old(self) -> int:
        return self._data["old"]

    @property
    def new(self) -> int:
        return self._data["new"]

    @property
    def pirate_index(self) -> int:
        return self._data["pirate"]

    @property
    def pirate(self) -> PartialPirate:
        return PartialPirate(
            self._round_data["pirates"][self.arena_index][self.pirate_index - 1]
        )

    @property
    def arena_index(self) -> int:
        return self._data["arena"]

    @property
    def arena(self) -> str:
        return ARENA_NAMES[self.arena_index]

    def __repr__(self):
        return f"<OddsChange index={self.index} pirate={self.pirate} old={self.old} new={self.new} timestamp={self.timestamp}>"

    def __eq__(self, other):  # for the "in" list check
        return self._data == other.data

    def __iter__(self):
        yield from self._data.items()

    def __hash__(self):
        return hash(repr(self))


class Modifier:
    __slots__ = (
        "value",
        "_custom_odds",
        "_nfc",
        "_time",
    )
    # if any are added, be sure to put it in ALL_MODIFIERS and add a letter in LETTERS.
    GENERAL = 1
    OPENING_ODDS = 2
    REVERSE = 4
    ALL_MODIFIERS = GENERAL | OPENING_ODDS | REVERSE
    LETTERS = "GOR"

    def __init__(
        self,
        flags: int = 0,
        custom_odds: Optional[Dict[PirateID, ValidOdds]] = None,
        custom_time: Optional[datetime.time] = None,
    ):
        self.value = flags
        self._custom_odds = custom_odds or {}
        self._nfc = None
        self._time = custom_time

    def __repr__(self):
        return f"<Modifier value={self.value} letters={self.letters} time={self.time}>"

    def _has_flag(self, o):
        return (self.value & o) == o

    @property
    def general(self):
        return self._has_flag(self.GENERAL)

    @property
    def opening_odds(self):
        return self._has_flag(self.OPENING_ODDS)

    @property
    def reverse(self):
        return self._has_flag(self.REVERSE)

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, val: datetime.time):
        self._time = val
        if self._nfc:
            self._nfc.reset()

    @property
    def custom_odds(self) -> Dict[PirateID, ValidOdds]:
        # custom_odds is a Dict[int, int] of {pirate_id: odds}
        return self._custom_odds

    @custom_odds.setter
    def custom_odds(self, val: Dict[PirateID, ValidOdds]):
        self._custom_odds = val
        if self._nfc:
            self._nfc.reset()

    def copy(self):
        return type(self)(self.value)

    @classmethod
    def from_type(cls, letters):
        letters = letters.lower()
        value = 0
        for index, letter in enumerate(cls.LETTERS.lower()):
            value |= (1 << index) if letter in letters else 0
        return cls(value)

    @property
    def letters(self) -> str:
        return "".join(
            self.LETTERS[bit]
            for bit in range(self.ALL_MODIFIERS.bit_length() + 1)
            if self._has_flag(1 << bit)
        )

    def __eq__(self, other):
        return (
            self.opening_odds == other.opening_odds
            and self.custom_odds == other.custom_odds
        )

    def __bool__(self):
        return self.opening_odds or bool(self._custom_odds) or bool(self._time)

    @property
    def nfc(self):
        return self._nfc

    @nfc.setter
    def nfc(self, value):
        self._nfc = value


@dataclass
class Odd:
    value: int
    probability: float
    cumulative: float
    tail: float


class Odds:
    def __init__(self, bets: "Bets"):
        odds = NFCMath.get_bet_odds_from_bets(
            bets.indices, bets.nfc._data_dict["odds"][bets._indices], bets.nfc._stds
        )
        self._odds = [Odd(**odd) for odd in odds]
        self.best = self._odds[-1]  # highest odds
        self.bust = self._odds[0] if self._odds[0].value == 0 else None  # lowest odds
        self.most_likely_winner = max(
            self._odds[1 if self.bust else 0 :], key=lambda o: o.probability
        )

        amount_of_bets = max(0, min(len(bets), 15))

        self.partial_rate = sum(
            o.probability for o in self._odds if 0 < int(o.value) < amount_of_bets
        )

    def __repr__(self):
        attrs = [
            ("best", self.best),
            ("bust", self.bust),
            ("most_likely_winner", self.most_likely_winner),
            ("partial_rate", self.partial_rate),
        ]
        joined = " ".join("%s=%r" % t for t in attrs)
        return f"<Odds {joined}>"


class Bets:
    __slots__ = (
        "_indices",
        "nfc",
    )

    def __init__(self, *, nfc: "NeoFoodClub", indices: np.ndarray):
        # TODO: custom bet amounts
        self.nfc = nfc
        self._indices = indices

    @property
    def net_expected(self) -> float:
        if self.nfc._net_expected_cache is not None:
            return np.sum(self.nfc._net_expected_cache[self._indices])
        return 0.0

    @property
    def er(self) -> float:
        return np.sum(self.nfc._data_dict["ers"][self._indices])

    @property
    def bet_amounts(self) -> np.ndarray:
        # TODO: custom bet amounts
        if self.nfc._maxbet_odds_cache is not None:
            return self.nfc._maxbet_odds_cache[self._indices].astype(int)

        return np.full(self._indices.size, 0)

    @property
    def indices(self) -> Tuple[Tuple[int, ...], ...]:
        return tuple(
            NFCMath.binary_to_indices(binary)
            for binary in self.nfc._data_dict["bins"][self._indices].astype(int)
        )

    @property
    def bet_hash(self) -> str:
        return NFCMath.bet_url_value(self.indices)

    @property
    def amounts_hash(self) -> str:
        return NFCMath.bet_amounts_to_string(
            dict(zip(range(len(self.bet_amounts)), self.bet_amounts))
        )

    def __repr__(self):
        attrs = [
            ("ne", self.net_expected),
            ("er", self.er),
            ("bet_hash", self.bet_hash),
            ("amount_hash", self.amounts_hash),
        ]
        joined = " ".join("%s=%r" % t for t in attrs)
        return f"<Bets {joined}>"

    @classmethod
    def _from_generator(cls, *, nfc: "NeoFoodClub", indices: np.ndarray):
        # here is where we will take indices and sort as needed
        # to avoid confusion with "manually" making bets
        if not nfc._modifier.reverse:
            indices = indices[::-1]

        indices = indices[: nfc.max_amount_of_bets]
        return cls(nfc=nfc, indices=indices)

    @classmethod
    def from_binary(cls, nfc: "NeoFoodClub", *bins: int):
        # TODO: raise duplicate errors
        # TODO: maintain order of bins
        int_bins = nfc._data_dict["bins"].astype(int)
        intersection = np.where(np.isin(int_bins, bins))[0]

        if intersection.size == 0:
            raise ValueError(
                "Bets class requires at least one valid index (an integer from 0-3124 inclusive)"
            )

        return cls(nfc=nfc, indices=intersection)

    def __len__(self):
        return self._indices.size

    @property
    def odds(self) -> Odds:
        return Odds(self)

    def _iterator(self):
        int_bins = self.nfc._data_dict["bins"].astype(int)
        yield from int_bins[self._indices]

    def __iter__(self):
        return self._iterator()

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.bet_hash == other.bet_hash
            and self.amounts_hash == other.amounts_hash
        )


class BetMixin:
    # TODO: bustproof bets

    @property
    def max_amount_of_bets(self) -> int:
        # if self._modifier.cc_perk:
        #     return 15
        return 10

    def _max_ter_indices(self) -> np.ndarray:
        # use net expected if we've got it
        return np.argsort(
            self._net_expected_cache
            if self._net_expected_cache is not None
            else self._data_dict["ers"]
        )

    def make_max_ter_set(self) -> Bets:
        return Bets._from_generator(nfc=self, indices=self._max_ter_indices())

    def _crazy_bets_indices(self) -> np.ndarray:
        return np.random.choice(
            NFCMath.FULL_BETS, size=self.max_amount_of_bets, replace=False
        )

    def make_crazy_bets(self) -> Bets:
        return Bets._from_generator(nfc=self, indices=self._crazy_bets_indices())

    def _random_indices(self) -> np.ndarray:
        return np.random.choice(3124, size=self.max_amount_of_bets, replace=False)

    def make_random_bets(self) -> Bets:
        return Bets._from_generator(nfc=self, indices=self._random_indices())

    def _gambit_indices(
        self, *, five_bet: Optional[int] = None, random: bool = False
    ) -> np.ndarray:
        if five_bet is not None:
            bins = self._data_dict["bins"].astype(int)
            possible_indices = np.where(bins & five_bet == bins)[0]

            odds = (
                self._data_dict["odds"][possible_indices]
                + self._data_dict["std"][possible_indices]
                # this gives us the highest ER bets first
            )
            sorted_odds = np.argsort(odds, kind="mergesort", axis=0)

            return possible_indices[sorted_odds]

        # these are lazy but they get the job done well enough
        if random:
            random_five_bet = self._data_dict["bins"][
                np.random.choice(NFCMath.FULL_BETS, size=1)
            ]
            return self._gambit_indices(five_bet=random_five_bet.astype(int)[0])

        # get highest ER pirates
        ers = self._data_dict["ers"][NFCMath.FULL_BETS]
        highest_er = np.argsort(ers, kind="mergesort", axis=0)[::-1][0]
        pirate_bin = self._data_dict["bins"][NFCMath.FULL_BETS[highest_er]]
        return self._gambit_indices(five_bet=pirate_bin.astype(int))

    def make_gambit_bets(
        self, *, five_bet: Optional[int] = None, random: bool = False
    ) -> Bets:
        return Bets._from_generator(
            nfc=self, indices=self._gambit_indices(five_bet=five_bet, random=random)
        )

    def _tenbet_indices(self, pirate_binary: int) -> np.ndarray:
        bins = self._data_dict["bins"].astype(int)
        possible_indices = np.where(bins & pirate_binary == pirate_binary)[0]

        ers = (
            self._net_expected_cache
            if self._net_expected_cache is not None
            else self._data_dict["ers"]
        )

        sorted_odds = np.argsort(ers[possible_indices], kind="mergesort", axis=0)

        return possible_indices[sorted_odds]

    def make_tenbet_bets(self, pirate_binary: int) -> Bets:
        amount_of_pirates = sum(1 for mask in NFCMath.BIT_MASKS if pirate_binary & mask)

        if amount_of_pirates == 0:
            raise ValueError("You must pick at least 1 pirate, and at most 3.")

        if amount_of_pirates > 3:
            raise ValueError("You must pick 3 pirates at most.")

        return Bets._from_generator(
            nfc=self, indices=self._tenbet_indices(pirate_binary)
        )

    def _unit_indices(self, units: int) -> np.ndarray:
        sorted_std = np.argsort(self._data_dict["std"], kind="mergesort", axis=0)
        possible_indices = np.where(self._data_dict["odds"][sorted_std] >= units)[0]
        return sorted_std[possible_indices]

    def make_units_bets(self, units: int) -> Bets:
        return Bets._from_generator(nfc=self, indices=self._unit_indices(units))

    def make_bets_from_indices(self, indices: Sequence[Sequence[int]]) -> Bets:
        # Takes a list of indices like [[1, 2, 3, 4, 2], ...] and turns it into Bets
        return Bets.from_binary(nfc=self, *NFCMath.bet_indices_to_bet_binaries(indices))

    def make_bets_from_hash(self, bet_hash: str) -> Bets:
        # Takes a bet hash and turns it into Bets
        return Bets.from_binary(nfc=self, *NFCMath.bet_string_to_bet_binaries(bet_hash))

    def make_bets_from_binaries(self, *binaries: int) -> Bets:
        # Takes bet-compatible binary numbers and turns them into Bets
        return Bets.from_binary(nfc=self, *binaries)


class Pirate(PirateMixin):
    __slots__ = (
        "_id",
        "_arena",
        "_index",
        "_odds",
        "_opening_odds",
        "_std",
        "_er",
    )

    def __init__(self, *, nfc: "NeoFoodClub", id: int, arena: int, index: int):
        self._id = id
        self._arena = arena
        self._index = index
        self._odds: int = nfc._data["customOdds"][arena][index]
        self._opening_odds: int = nfc._data["openingOdds"][arena][index]
        self._std: float = nfc._stds[arena][index]
        self._er: float = self.std * self.odds

    @property
    def id(self) -> int:
        return self._id

    @property
    def arena(self) -> int:
        return self._arena

    @property
    def index(self) -> int:
        return self._index

    @property
    def std(self) -> float:
        return self._std

    @property
    def odds(self) -> int:
        return self._odds

    @property
    def er(self) -> float:
        return self._er

    @property
    def opening_odds(self) -> int:
        return self._opening_odds

    def __int__(self):
        return NFCMath.pirate_binary(self._index, self._arena)

    def __repr__(self):
        attrs = [
            ("name", self.name),
            ("arena", self.arena),
            ("index", self.index),
            ("odds", self.odds),
            ("opening_odds", self.opening_odds),
        ]
        joined = " ".join("%s=%r" % t for t in attrs)
        return f"<Pirate {joined}>"


class Arena:
    __slots__ = (
        "_pirates",
        "_id",
    )

    def __init__(self, *, nfc: "NeoFoodClub", arena_id: int, pirate_ids: Sequence[int]):
        self._id = arena_id
        self._pirates = [  # adding 1 to index because the original list has a length of 4, but everything else has 5
            Pirate(nfc=nfc, id=p_id, arena=arena_id, index=idx + 1)
            for idx, p_id in enumerate(pirate_ids)
        ]

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return ARENA_NAMES[self._id]

    @property
    def best(self) -> List[Pirate]:
        return sorted(self._pirates, key=lambda a: a.odds)

    @property
    def ids(self):
        return [p.id for p in self._pirates]

    @property
    def odds(self) -> float:
        # do note that arena odds are not the same as pirate odds
        return 5 / sum(p.odds for p in self._pirates)

    @property
    def ratio(self) -> float:
        return 1 / self.odds - 1

    @property
    def pirates(self) -> List[Pirate]:
        return self._pirates

    @property
    def positive(self) -> bool:
        return self.odds < 1

    @property
    def negative(self) -> bool:
        return not self.positive

    def __getitem__(self, item: ValidIndex) -> Optional[Pirate]:
        try:
            return self._pirates[item]
        except KeyError:
            return None

    def __iter__(self):
        return self._pirates.__iter__()

    def __repr__(self):
        return f"<Arena name={self.name} odds={self.odds} pirates={self.pirates}>"


class Arenas:
    __slots__ = ("_arenas",)

    def __init__(self, nfc: "NeoFoodClub"):
        self._arenas = [
            Arena(nfc=nfc, arena_id=idx, pirate_ids=a)
            for idx, a in enumerate(nfc._data["pirates"])
        ]

    def get_pirate_by_id(self, pirate_id: PirateID) -> Pirate:
        for p in self.all_pirates:
            if p.id == pirate_id:
                return p

    def get_pirates_by_id(self, *pirate_ids: Sequence[PirateID]) -> List[Pirate]:
        return [p for p in self.all_pirates if p.id in pirate_ids]

    @property
    def all_pirates(self) -> List[Pirate]:
        pirates = []
        for a in self._arenas:
            for p in a.pirates:
                pirates.append(p)
        return pirates

    @property
    def pirates(self) -> List[List[Pirate]]:
        return [arena.pirates for arena in self._arenas]

    @property
    def best(self) -> List[Arena]:
        return sorted(self._arenas, key=lambda a: a.odds)

    @property
    def pirate_ids(self) -> List[List[int]]:
        return [arena.ids for arena in self._arenas]

    @property
    def positives(self) -> List[Arena]:
        return sorted([a for a in self._arenas if a.positive], key=lambda _a: _a.odds)

    def __repr__(self):
        return f"<Arenas {self._arenas!r}>"


class NeoFoodClub(BetMixin):
    __slots__ = (
        "_data",
        "_modifier",
        "_bet_amount",
        "_stds",
        "_data_dict",
        "_maxbet_odds_cache",
        "_net_expected_cache",
    )

    def __init__(
        self,
        data: RoundData,
        *,
        bet_amount: Optional[int] = None,
        modifier: Optional[Modifier] = None,
    ):
        # so it's not changing old cache data around, have a deep copy (safety precaution for custom odds)
        self._data = json.loads(json.dumps(data))
        self._bet_amount = bet_amount
        self._data_dict = None
        self._maxbet_odds_cache = None
        self._net_expected_cache = None
        self._stds = NFCMath.make_probabilities(self._data["openingOdds"])

        if modifier is None:
            modifier = Modifier()
        self._modifier = modifier
        self._modifier.nfc = self

        self.reset()

    def _add_custom_odds(self):
        for k1, a in enumerate(self._data["pirates"]):
            for k2, p in enumerate(a):
                # custom, user-added odds
                if p in self._modifier.custom_odds:
                    self._data["customOdds"][k1][k2 + 1] = self._modifier.custom_odds[p]

    def _do_snapshot(self):
        dt = self.get_round_time(self._modifier.time)
        if dt is None:
            return

        for change in self.changes:
            if change.timestamp < dt:
                self._data["customOdds"][change.arena_index][
                    change.pirate_index
                ] = change.new

    def reset(self):
        # start with the desired odds
        key = "openingOdds" if self._modifier.opening_odds else "currentOdds"
        self._data["customOdds"] = json.loads(json.dumps(self._data[key]))

        if self._modifier.time:
            self._do_snapshot()

        self._add_custom_odds()

        self._cache_dicts()

    def _cache_bet_amount_dicts(self):
        # cache maxbets, we'll need these a lot later,
        # but only if we need them at all
        bet_amount = self._bet_amount
        if bet_amount and not self._modifier.general:
            mb_copy = self._data_dict["maxbets"].copy()
            mb_copy[mb_copy > bet_amount] = bet_amount
            self._maxbet_odds_cache = mb_copy

            # for making maxter faster...
            self._net_expected_cache = mb_copy * self._data_dict["ers"] - mb_copy

    def _cache_dicts(self):
        # most of the binary/odds/std data sits here
        self._data_dict = NFCMath.make_round_dicts(
            tuple(tuple(row) for row in self._stds),
            tuple(tuple(row) for row in self._data["customOdds"]),
        )

        self._cache_bet_amount_dicts()

    @property
    def arenas(self) -> Arenas:
        return Arenas(self)

    @property
    def bet_amount(self) -> Optional[int]:
        return self._bet_amount

    @bet_amount.setter
    def bet_amount(self, val: Optional[int]):
        if val != self._bet_amount:
            self._bet_amount = val
            self._cache_bet_amount_dicts()

    @property
    def modifier(self):
        return self._modifier

    @modifier.setter
    def modifier(self, val: Modifier):
        reset = False
        if (self._modifier.opening_odds, self._modifier.custom_odds) != (
            val.opening_odds,
            val.custom_odds,
        ):
            # data is only changed with differing opening odds, or custom odds
            reset = True

        self._modifier = val
        self._modifier.nfc = self

        if reset:
            self.reset()

    @property
    def modified(self) -> bool:
        return bool(self._modifier)

    def with_modifier(self, modifier: Optional[Modifier] = None):
        if modifier is None:
            modifier = Modifier()

        self.modifier = modifier
        return self

    @property
    def data(self) -> RoundData:
        return self._data

    @property
    def opening_odds(self) -> List[List[ValidOdds]]:
        return self._data["openingOdds"]

    @property
    def current_odds(self) -> List[List[ValidOdds]]:
        return self._data["currentOdds"]

    @property
    def custom_odds(self) -> List[List[ValidOdds]]:
        return self._data["customOdds"]

    @property
    def round(self) -> int:
        return int(self._data["round"])

    @property
    def start(self) -> Optional[datetime.datetime]:
        if start := self._data.get("start"):
            return parse(start).astimezone(UTC)
        return None

    @property
    def timestamp(self) -> Optional[datetime.datetime]:
        if timestamp := self._data.get("timestamp"):
            return parse(timestamp).astimezone(UTC)
        return None

    def get_round_time(self, t: datetime.time) -> Optional[datetime.datetime]:
        if self.start is None or self.timestamp is None:
            return None

        dt = self.start

        # fix before/after round times
        for add_days in range(2):
            dt = datetime.datetime.combine(
                date=(self.start + datetime.timedelta(days=add_days)).date(),
                time=t,
                tzinfo=self.start.tzinfo,
            )
            if dt > self.start:
                break

        return max(self.start, min(dt, self.timestamp))

    @property
    def is_outdated_lock(self) -> bool:
        if self.start is None:
            return True
        return self.start <= datetime.datetime.now(tzutc()) - datetime.timedelta(days=1)

    @property
    def is_over(self) -> bool:
        # if any of them are > 0, it's over. might as well check just the first.
        return bool(self.winners[0])

    @property
    def winners(self) -> List[ValidIndex]:
        return self._data.get("winners") or [0, 0, 0, 0, 0]

    @property
    def winners_binary(self) -> int:
        return NFCMath.pirates_binary(tuple(self.winners))

    @property
    def foods(self) -> Optional[List[List[FoodID]]]:
        return self._data.get("foods")

    @property
    def changes(self) -> List[OddsChange]:
        changed = [
            OddsChange(index=idx, round_data=self._data, data=c)
            for idx, c in enumerate(self._data.get("changes", []))
        ]
        return list(sorted(changed, key=lambda oc: oc.timestamp))

    def __repr__(self):
        return f"<NeoFoodClub round={self.round} timestamp={self.timestamp!r} is_over={self.is_over}>"
