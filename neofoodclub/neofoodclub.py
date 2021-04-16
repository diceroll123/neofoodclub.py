from collections import namedtuple
import datetime
import json
import neofoodclub.math as NFCMath
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import dateutil
from dateutil.tz import UTC, tzutc


from dateutil.parser import parse

from neofoodclub.food_adjustments import NEGATIVE_FOOD, POSITIVE_FOOD
from neofoodclub.types import RoundData, FoodID, ValidOdds, ValidIndex

ARENA_NAMES = ["Shipwreck", "Lagoon", "Treasure", "Hidden", "Harpoon"]

PartialPirate = namedtuple("PartialPirate", ["id"])


__all__ = ("NeoFoodClub",)


@dataclass
class Pirate:
    id: int
    arena: int
    index: int
    nfc: "NeoFoodClub"
    std: float
    odds: int
    opening_odds: int
    er: float = field(init=False)
    bin: int = field(init=False)

    def __post_init__(self):
        self.er = self.std * self.odds
        self.bin = NFCMath.pirate_binary(self.index, self.arena)

    @property
    def fa(self) -> int:
        foods = self.nfc.data["foods"]
        if foods:
            return sum(
                -NEGATIVE_FOOD[self.id][f] + POSITIVE_FOOD[self.id][f]
                for f in foods[self.arena]
            )

        return 0

    def __int__(self):
        return self.bin

    def __hash__(self):
        return hash(self.bin)


class Arena:
    __slots__ = (
        "_id",
        "_pirates",
        "_odds",
    )

    def __init__(self, arena_id: int):
        self._id = arena_id
        self._pirates: List[Pirate] = []
        self._odds = 0

    @property
    def name(self) -> Optional[str]:
        if self._pirates:
            return ARENA_NAMES[self._id]
        return None

    def add(self, pirate):
        self._pirates.append(pirate)
        self._odds += 1 / pirate.odds

    @property
    def best(self) -> List[Pirate]:
        return sorted(self._pirates, key=lambda a: a.odds)

    @property
    def ids(self) -> List[int]:
        return [p.id for p in self._pirates]

    @property
    def odds(self) -> float:
        return self._odds

    @property
    def ratio(self) -> float:
        return 1 / self._odds - 1

    @property
    def pirates(self) -> List[Pirate]:
        return self._pirates

    @property
    def positive(self) -> bool:
        return self._odds < 1

    @property
    def negative(self) -> bool:
        return not self.positive

    def __getitem__(self, item) -> Optional[Pirate]:
        try:
            return self._pirates[item]
        except KeyError:
            return None

    def __iter__(self):
        return self._pirates.__iter__()

    def __repr__(self):
        return f"<Arena name={self.name} odds={self._odds} pirates={self.pirates}>"


class Arenas:
    __slots__ = (
        "_data",
        "_stds",
        "_arenas",
        "_all_pirates",
        "_ids",
        "_positives",
    )

    def __init__(self, nfc):
        self._data = nfc.data
        self._stds = NFCMath.make_probabilities(self._data["openingOdds"])

        self._arenas: List[Arena] = []
        self._all_pirates: Dict[int, Pirate] = {}

        odds_key = "customOdds" if nfc._modifier else "currentOdds"

        for idx, a in enumerate(self._data.get("pirates")):
            arena = Arena(arena_id=idx)

            for i, pirate_id in enumerate(a):
                i += 1
                p = Pirate(
                    id=pirate_id,
                    arena=idx,
                    index=i,
                    odds=nfc._data[odds_key][idx][i],
                    opening_odds=nfc._data["openingOdds"][idx][i],
                    nfc=nfc,
                    std=self._stds[idx][i],
                )
                arena.add(p)
                self._all_pirates[pirate_id] = p

            self._arenas.append(arena)

        self._ids: List[List[int]] = [a.ids for a in self._arenas]
        self._positives: List[Arena] = sorted(
            [a for a in self._arenas if a.positive], key=lambda _a: _a.odds
        )

    def get_pirate_by_id(self, pirate_id: int) -> Pirate:
        return self._all_pirates[pirate_id]

    def get_pirates_by_id(self, pirate_ids: List[int]) -> List[Pirate]:
        return [self._all_pirates[num] for num in pirate_ids]

    @property
    def all_pirates(self) -> List[Pirate]:
        return list(self._all_pirates.values())

    @property
    def pirates(self) -> List[List[Pirate]]:
        return [arena.pirates for arena in self._arenas]

    @property
    def best(self) -> List[Arena]:
        return sorted(self._arenas, key=lambda a: a.odds)

    @property
    def ids(self) -> List[List[int]]:  # pirate ids
        return self._ids

    @property
    def positives(self) -> List[Arena]:
        return self._positives

    @property
    def probability_list(self) -> List[List[float]]:
        return self._stds

    def __getitem__(self, item):
        try:
            return self._arenas[item]
        except KeyError:
            return None

    def __iter__(self):
        return self._arenas.__iter__()


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
            id=self._round_data["pirates"][self.arena_index][self.pirate_index - 1]
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
        custom_odds=None,
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
    def custom_odds(self):
        # custom_odds is a Dict[int, int] of {pirate_id: odds}
        return self._custom_odds

    @custom_odds.setter
    def custom_odds(self, val: Dict):
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


class NeoFoodClub:
    def __init__(
        self,
        data: RoundData,
        *,
        bet_amount: Optional[int] = None,
        modifier: Optional[Modifier] = None,
    ):
        # so it's not changing old cache data around, have a deep copy (safety precaution for custom odds)
        self._data = json.loads(json.dumps(data))
        self.bet_amount = bet_amount

        self._arenas: Arenas

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
        if not self._modifier.time:
            return

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
        if self._modifier.opening_odds:
            self._data["customOdds"] = json.loads(json.dumps(self._data["openingOdds"]))
        else:
            self._data["customOdds"] = json.loads(json.dumps(self._data["currentOdds"]))

        self._do_snapshot()

        self._add_custom_odds()

        self._arenas = Arenas(self)

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

    @property
    def arenas(self) -> Arenas:
        return self._arenas

    @property
    def winners_pirates(self) -> Optional[Tuple[Pirate, ...]]:
        # TODO: turn into a Bet object
        if self.is_over:
            return tuple(
                self.arenas[idx][p_idx - 1] for idx, p_idx in enumerate(self.winners)
            )
        return None

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
        return f"<NeoFoodClub round={self.round} timestamp={self.timestamp!r}>"
