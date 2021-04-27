from __future__ import annotations
import datetime
import json
import re

import numpy as np

import neofoodclub.math as NFCMath
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Sequence

import dateutil
from dateutil.tz import UTC, tzutc

from dateutil.parser import parse
from typing import TYPE_CHECKING

from . import utils
from .errors import InvalidData, MissingData


if TYPE_CHECKING:
    from .pirates import PartialPirate, Pirate
    from .arenas import Arenas
    from neofoodclub.types import (
        RoundData,
        FoodID,
        ValidOdds,
        ValidIndex,
        PirateID,
    )

NEO_FC_REGEX = re.compile(
    r"(/(?P<perk>15/)?)#(?P<query>[a-zA-Z0-9=&\[\],%-:+]+)",
    re.IGNORECASE,
)


__all__ = (
    "NeoFoodClub",
    "OddsChange",
    "Modifier",
    "Bets",
    "Odds",
    "NEO_FC_REGEX",
)


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
        from .pirates import PartialPirate  # to prevent circular imports

        return PartialPirate(
            self._round_data["pirates"][self.arena_index][self.pirate_index - 1]
        )

    @property
    def arena_index(self) -> int:
        return self._data["arena"]

    @property
    def arena(self) -> str:
        from .arenas import ARENA_NAMES  # to prevent circular imports

        return ARENA_NAMES[self.arena_index]

    def __repr__(self):
        return f"<OddsChange index={self.index} pirate={self.pirate} old={self.old} new={self.new} timestamp={self.timestamp}>"

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._data == other.data

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
        "_cc_perk",
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
        *,
        cc_perk: bool = False,
        custom_odds: Optional[Dict[PirateID, ValidOdds]] = None,
        custom_time: Optional[datetime.time] = None,
    ):
        self.value = flags
        self._custom_odds = custom_odds or {}
        self._nfc = None
        self._time = custom_time
        self._cc_perk = cc_perk

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
    def cc_perk(self) -> bool:
        return self._cc_perk

    @cc_perk.setter
    def cc_perk(self, val: bool):
        self._cc_perk = val

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
        return type(self)(
            self.value,
            cc_perk=self._cc_perk,
            custom_odds=self._custom_odds,
            custom_time=self._time,
        )

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
            isinstance(other, self.__class__)
            and self.opening_odds == other.opening_odds
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
    __slots__ = (
        "_odds_values",
        "_odds",
        "best",
        "bust",
        "most_likely_winner",
        "partial_rate",
    )

    def __init__(self, bets: Bets):
        self._odds_values = bets.nfc._data_dict["odds"][bets._indices]
        odds = NFCMath.get_bet_odds_from_bets(
            bets.indices, self._odds_values, bets.nfc._stds
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

    def _iterator(self):
        yield from self._odds_values

    def __iter__(self):
        return self._iterator()

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
        "_bet_amounts",
        "nfc",
    )

    def __init__(
        self,
        *,
        nfc: NeoFoodClub,
        indices: np.ndarray,
        amounts: Optional[Sequence[Optional[int]]] = None,
    ):
        self.nfc = nfc
        self._indices = indices

        self.bet_amounts = amounts or None

    @property
    def net_expected(self) -> float:
        if self.nfc._net_expected_cache is not None:
            return np.sum(self.nfc._net_expected_cache[self._indices])
        return 0.0

    @property
    def er(self) -> float:
        return np.sum(self.nfc._data_dict["ers"][self._indices])

    @property
    def bet_amounts(self) -> Optional[np.ndarray]:
        # user-defined (and sometimes generated) bet amounts
        if self._bet_amounts is not None:
            return self._bet_amounts

        if self.nfc._maxbet_odds_cache is not None:
            return self.nfc._maxbet_odds_cache[self._indices].astype(int)

        return None

    @bet_amounts.setter
    def bet_amounts(self, val: Optional[Sequence[int]]):
        if val is None:
            self._bet_amounts = None
            return

        # strictly enforcing amount of values provided
        if len(val) != self._indices.size:
            raise InvalidData(
                f"Invalid bet amounts provided. Expected length: {self._indices.size}, but received {len(val)}."
            )

        amts = np.array([v or 50 for v in val])

        self._bet_amounts = utils.fix_bet_amounts(amts)

    @property
    def indices(self) -> Tuple[Tuple[int, ...], ...]:
        return tuple(
            NFCMath.binary_to_indices(binary)
            for binary in self.nfc._data_dict["bins"][self._indices].astype(int)
        )

    @property
    def bets_hash(self) -> str:
        return NFCMath.bets_url_value(self.indices)

    @property
    def amounts_hash(self) -> str:
        return NFCMath.bet_amounts_to_string(
            dict(zip(range(len(self.bet_amounts)), self.bet_amounts))
        )

    def __repr__(self):
        attrs = [
            ("ne", self.net_expected),
            ("er", self.er),
            ("bets_hash", self.bets_hash),
            ("amounts_hash", self.amounts_hash),
        ]
        joined = " ".join("%s=%r" % t for t in attrs)
        return f"<Bets {joined}>"

    @classmethod
    def _from_generator(cls, *, indices: np.ndarray, nfc: NeoFoodClub):
        # here is where we will take indices and sort as needed
        # to avoid confusion with "manually" making bets
        if not nfc._modifier.reverse:
            indices = indices[::-1]

        indices = indices[: nfc.max_amount_of_bets]
        return cls(nfc=nfc, indices=indices)

    @classmethod
    def from_binary(cls, *bins: int, nfc: NeoFoodClub):
        # duplicate bins are removed
        int_bins = nfc._data_dict["bins"].astype(int)
        np_bins = np.array([b for b in dict.fromkeys(bins)])

        # thanks @mikeshardmind
        intersection = np.where(np_bins[:, np.newaxis] == int_bins)[1]

        if intersection.size == 0:
            raise InvalidData(
                "Bets class requires at least one valid bet binary integer."
            )

        if intersection.size != np_bins.size:
            diff = np.setdiff1d(np_bins, np_bins[intersection])
            raise InvalidData(
                f"Invalid bet binaries entered: {', '.join([hex(b) for b in diff])}"
            )

        return cls(nfc=nfc, indices=intersection)

    def __len__(self):
        return self._indices.size

    @property
    def odds(self) -> Odds:
        return Odds(self)

    @property
    def is_bustproof(self) -> bool:
        return self.odds.bust is None

    @property
    def is_guaranteed_win(self) -> bool:  # guaranteed to profit, that is
        amounts = self.bet_amounts

        if amounts is None or np.sum(amounts) <= 0:
            return False

        highest_bet_amount = np.max(amounts)
        bets_odds = self.nfc._data_dict["odds"][self._indices]
        lowest_winning_bet_amount = np.min(bets_odds * amounts)

        return highest_bet_amount < lowest_winning_bet_amount and self.is_bustproof

    def _iterator(self):
        int_bins = self.nfc._data_dict["bins"].astype(int)
        yield from int_bins[self._indices]

    def __iter__(self):
        return self._iterator()

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.bets_hash == other.bets_hash
            and self.amounts_hash == other.amounts_hash
        )


class BetMixin:
    @property
    def max_amount_of_bets(self) -> int:
        if self._modifier._cc_perk:
            return 15
        return 10

    def _max_ter_indices(self) -> np.ndarray:
        # use net expected only if needed
        if self._modifier.general or self._net_expected_cache is None:
            return np.argsort(self._data_dict["ers"])
        else:
            return np.argsort(self._net_expected_cache)

    def make_max_ter_bets(self) -> Bets:
        return Bets._from_generator(indices=self._max_ter_indices(), nfc=self)

    def _crazy_bets_indices(self) -> np.ndarray:
        return np.random.choice(
            NFCMath.FULL_BETS, size=self.max_amount_of_bets, replace=False
        )

    def make_crazy_bets(self) -> Bets:
        return Bets._from_generator(indices=self._crazy_bets_indices(), nfc=self)

    def _random_indices(self) -> np.ndarray:
        return np.random.choice(3124, size=self.max_amount_of_bets, replace=False)

    def make_random_bets(self) -> Bets:
        return Bets._from_generator(indices=self._random_indices(), nfc=self)

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
            indices=self._gambit_indices(five_bet=five_bet, random=random), nfc=self
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
            raise InvalidData("You must pick at least 1 pirate, and at most 3.")

        if amount_of_pirates > 3:
            raise InvalidData("You must pick 3 pirates at most.")

        return Bets._from_generator(
            indices=self._tenbet_indices(pirate_binary), nfc=self
        )

    def _unit_indices(self, units: int) -> np.ndarray:
        sorted_std = np.argsort(self._data_dict["std"], kind="mergesort", axis=0)
        possible_indices = np.where(self._data_dict["odds"][sorted_std] >= units)[0]
        return sorted_std[possible_indices]

    def make_units_bets(self, units: int) -> Bets:
        return Bets._from_generator(indices=self._unit_indices(units), nfc=self)

    def make_bustproof_bets(self) -> Optional[Bets]:
        arenas = self.arenas
        positives = arenas.positives
        if not positives:
            # nothing to do here!
            return None

        if len(positives) == 1:
            # If only one arena is positive, we place 1 bet on each of the pirates of that arena. Total bets = 4.
            best_arena = arenas.best[0]
            bets = Bets.from_binary(*[p.binary for p in best_arena.pirates], nfc=self)
        elif len(positives) == 2:
            # If two arenas are positive, we place 1 bet on each of the three worst pirates of the best arena and
            # 1 bet on each of the pirates of the second arena + the best pirate of the best arena. Total bets = 7
            best_arena, second_arena = arenas.best[:2]
            bets = Bets.from_binary(
                *[p.binary for p in best_arena.best[-3:]],
                *[p.binary | best_arena.best[0].binary for p in second_arena.pirates],
                nfc=self,
            )
        else:
            # If three arenas are positive, we place 1 bet on each of the three worst pirates of the best arena,
            # If four or more arenas are positive, we only play the three best arenas, seen below
            # 1 bet on each of the three worst pirates of the second arena + the best pirate of the best arena,
            # and 1 bet on each of the pirates of the third arena + the best pirate of the best arena + the best pirate
            # of the second arena. Total bets = 10.
            best_arena, second_arena, third_arena = arenas.best[:3]

            bets = Bets.from_binary(
                *[p.binary for p in best_arena.best[-3:]],
                *[p.binary | best_arena.best[0].binary for p in second_arena.best[-3:]],
                *[
                    p.binary | best_arena.best[0].binary | second_arena.best[0].binary
                    for p in third_arena.best
                ],
                nfc=self,
            )

        bet_amount = self.bet_amount
        if bet_amount:
            current_odds = self._data_dict["odds"][bets._indices]
            lowest_odds_index = np.argmin(current_odds)
            lowest_odds = current_odds[lowest_odds_index]

            new_bet_amounts = (bet_amount * lowest_odds // current_odds).astype(int)
            bets.bet_amounts = new_bet_amounts

        return bets

    # bet decoding methods
    def make_bets_from_indices(self, indices: Sequence[Sequence[int]]) -> Bets:
        # Takes a list of indices like [[1, 2, 3, 4, 2], ...] and turns it into Bets
        return Bets.from_binary(
            *NFCMath.bets_indices_to_bet_binaries(indices), nfc=self
        )

    def make_bets_from_hash(
        self, bets_hash: str, amounts_hash: Optional[str] = None
    ) -> Bets:
        # Takes a bet hash and turns it into Bets
        bets = Bets.from_binary(*NFCMath.bets_hash_to_bet_binaries(bets_hash), nfc=self)
        if amounts_hash:
            amounts = NFCMath.amounts_hash_to_bet_amounts(amounts_hash)
            bets.bet_amounts = amounts

        return bets

    def make_bets_from_binaries(self, *binaries: int) -> Bets:
        # Takes bet-compatible binary numbers and turns them into Bets
        return Bets.from_binary(*binaries, nfc=self)


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

        if bet_amount:
            mb_copy = self._data_dict["maxbets"].copy()
            mb_copy[mb_copy > bet_amount] = bet_amount
            self._maxbet_odds_cache = utils.fix_bet_amounts(mb_copy)

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
        from .arenas import Arenas  # to prevent circular imports

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
    def modifier(self, val: Optional[Modifier]):
        val = val or Modifier()
        reset = False
        if (
            self._modifier.opening_odds,
            self._modifier.custom_odds,
            self._modifier.time,
        ) != (
            val.opening_odds,
            val.custom_odds,
            val.time,
        ):
            # data is only changed with differing opening odds, custom odds, or custom time
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

    def to_dict(self, keep_custom: bool = False) -> RoundData:
        # return a deep copy of this round's dict
        data = json.loads(json.dumps(self._data))
        if not keep_custom:
            data.pop("customOdds", None)
        return data

    @property
    def pirates(self) -> List[List[PirateID]]:
        return self._data["pirates"]

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
        start = self._data.get("start")
        if start:
            return parse(start).astimezone(UTC)
        return None

    @property
    def timestamp(self) -> Optional[datetime.datetime]:
        timestamp = self._data.get("timestamp")
        if timestamp:
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
    def winners_pirates(self) -> List[Pirate]:
        return self.arenas.get_pirates_from_binary(self.winners_binary)

    @property
    def foods(self) -> Optional[List[List[FoodID]]]:
        return self._data.get("foods")

    @property
    def changes(self) -> List[OddsChange]:
        copied_data = self.to_dict()
        changed = [
            OddsChange(index=idx, round_data=copied_data, data=c)
            for idx, c in enumerate(copied_data.get("changes") or [])
        ]
        return list(sorted(changed, key=lambda oc: oc.timestamp))

    def _get_winning_bet_indices(self, bets: Bets) -> np.ndarray:
        bet_bins = self._data_dict["bins"][bets._indices].astype(int)
        winning_bet_indices = np.where(bet_bins & self.winners_binary == bet_bins)[0]
        return bets._indices[winning_bet_indices]

    def _get_winning_odds(self, bets: Bets) -> np.ndarray:
        winning_bet_bins = self._get_winning_bet_indices(bets)
        return self._data_dict["odds"][winning_bet_bins]

    def get_win_units(self, bets: Bets) -> int:
        return np.sum(self._get_winning_odds(bets)).astype(int)

    def get_win_np(self, bets: Bets, use_bet_amount_if_none: bool = True) -> int:
        winning_bins_indices = self._get_winning_bet_indices(bets)

        if winning_bins_indices.size == 0:
            # these bets lost
            return 0

        use_backup_if_needed = use_bet_amount_if_none and self.bet_amount

        if bets.bet_amounts is not None:
            multiplier = bets.bet_amounts
        elif use_backup_if_needed:
            multiplier = np.full(bets._indices.size, self.bet_amount)
        else:
            return 0

        mask = np.in1d(bets._indices, winning_bins_indices)
        bets_odds = self._data_dict["odds"][bets._indices]
        winnings = bets_odds * multiplier

        return np.sum(np.clip(winnings[mask], 0, 1_000_000)).astype(int)

    def make_url(self, bets: Optional[Bets] = None) -> str:
        def encode(int_lists) -> str:
            return json.dumps(int_lists, separators=(",", ":"))

        use_15 = bets and 10 < len(bets) <= 15 or self._modifier._cc_perk

        url = (
            "https://foodclub.neocities.org/"
            + ("15/" if use_15 else "")
            + "#round="
            + str(self.round)
            + "&pirates="
            + encode(self.pirates)
            + "&openingOdds="
            + encode(self.opening_odds)
            + "&currentOdds="
            + encode(self.current_odds)
        )

        if self.foods is not None:
            url += "&foods=" + encode(self.foods)

        if self.is_over:
            url += "&winners=" + encode(self.winners)

        if self.timestamp:
            url += (
                "&timestamp="
                + self.timestamp.replace(
                    microsecond=0, tzinfo=datetime.timezone.utc
                ).isoformat()
            )

        if bets:
            url += "&b=" + bets.bets_hash
            if np.sum(bets.bet_amounts):
                url += "&a=" + bets.amounts_hash

        return url

    @classmethod
    def from_url(
        cls,
        url: str,
        *,
        bet_amount: Optional[int] = None,
        modifier: Optional[Modifier] = None,
    ):
        neo_fc = NEO_FC_REGEX.search(url)
        if neo_fc is None:
            raise MissingData("No relevant NeoFoodClub-like URL data found.")

        if modifier is None:
            modifier = Modifier()

        if bool(neo_fc.group("perk")):
            modifier.cc_perk = True

        querystring = url.partition("#")[-1]

        import urllib.parse
        import json

        olddata = urllib.parse.parse_qs(urllib.parse.unquote(querystring))

        # gather relevant variables from the query string
        data = {
            key: json.loads(olddata[key][0])
            for key in [
                "pirates",  # required
                "openingOdds",  # required
                "currentOdds",  # required
                "round",
                "winners",
                "foods",
            ]
            if key in olddata
        }

        # validate

        if data["round"] and type(data["round"]) is not int:
            # we only need the round number to make a proper URL
            # the actual value doesn't matter
            raise InvalidData("Improper value for current round number")

        has_proper_ids = sorted(set(sum(data["pirates"], []))) == [*range(1, 21)]
        has_proper_shape = [len(row) for row in data["pirates"]] == [4, 4, 4, 4, 4]
        if not all([has_proper_ids, has_proper_shape]):
            raise InvalidData("Improper pirates array")

        for odd_type in ["openingOdds", "currentOdds"]:
            odds = data[odd_type]
            for odd in odds:
                first, *rest = odd

                if first != 1:
                    raise InvalidData("Improper odds passed")

                for num in rest:
                    if not 2 <= num <= 13:
                        raise InvalidData("Improper odds passed")

        return cls(data, bet_amount=bet_amount, modifier=modifier)

    def copy(self, keep_custom: bool = False) -> NeoFoodClub:
        return NeoFoodClub(
            self.to_dict(keep_custom=keep_custom),
            bet_amount=self._bet_amount,
            modifier=self._modifier,
        )

    def __repr__(self):
        attrs = [
            ("round", self.round),
            ("bet_amount", self._bet_amount),
            ("timestamp", self.timestamp),
            ("is_over", self.is_over),
        ]
        joined = " ".join("%s=%r" % t for t in attrs if t[1] is not None)
        return f"<NeoFoodClub {joined}>"
