from __future__ import annotations

import contextlib
import datetime
import functools
import re
import urllib.parse
from typing import TYPE_CHECKING, Any, Callable, Sequence, TypeVar, overload

import dateutil
import dateutil.parser
import numpy as np
import orjson
from dateutil.tz import UTC, tzutc
from typing_extensions import ParamSpec, Self

from neofoodclub.bets import Bets
from neofoodclub.models import OriginalModel, ProbabilityModel
from neofoodclub.modifier import Modifier
from neofoodclub.odds_change import OddsChange

from . import math, utils
from .arenas import Arena, Arenas
from .errors import InvalidAmountHash, InvalidBetHash, InvalidData, NoPositiveArenas

if TYPE_CHECKING:
    import numpy.typing as npt

    from neofoodclub.types import RoundData

    from .pirates import Pirate


NEO_FC_REGEX = re.compile(
    r"(/(?P<perk>15/)?)#(?P<query>[a-zA-Z0-9=&\[\],%-:+]+)",
    re.IGNORECASE,
)
PIRATES_REGEX = re.compile(r"^\[((\[(\d+,){3}\d+\]),){4}(\[(\d+,){3}\d+\])\]$")
ODDS_REGEX = re.compile(
    r"^\[(\[1,(([2-9]|1[0-3]),){3}([2-9]|1[0-3])\],){4}\[1,(([2-9]|1[0-3]),){3}([2-9]|1[0-3])\]\]$"
)
WINNERS_REGEX = re.compile(r"^\[((([1-4],){4}[1-4])|(0,0,0,0,0))\]$")
FOODS_REGEX = re.compile(r"^\[((\[(\d+,){9}\d+\]),){4}(\[(\d+,){9}\d+\])\]$")

BET_HASH_REGEX = re.compile(r"^[a-y]+$")
AMOUNT_HASH_REGEX = re.compile(r"^[a-zA-Z]+$")

__all__ = (
    "NeoFoodClub",
    "NEO_FC_REGEX",
)

P = ParamSpec("P")
R = TypeVar("R")


def _require_cache(func: Callable[P, R]) -> Callable[P, R]:
    # for internal use only.
    # if the NFC object has no cache, it will after this runs.

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        self: NeoFoodClub = args[0]  # type: ignore
        if not self._data_dict or not self._stds:
            self.reset()
        return func(*args, **kwargs)

    return wrapper


class NeoFoodClub:
    """Represents a Food Club round.
    This class is the basis of this library.

    Parameters
    ----------
    data: :class:`RoundData`
        The all-encompassing Dict that provides the values to create a working object.
    bet_amount: Optional[:class:`int`]
        An integer representing a bet amount to be used for generating bets.
    modifier: Optional[:class:`Modifier`]
        The desired modifier for generating bets.
    cache: :class:`bool`
        Whether or not to instantly calculate and cache the round's data.
        Turning this off is useful for when you're just analyzing data and not generating bets.
    """

    __slots__ = (
        "_data",
        "_modifier",
        "_bet_amount",
        "_stds",
        "_data_dict",
        "_maxbet_odds_cache",
        "_net_expected_cache",
        "_arenas",
        "_probability_model",
    )

    def __init__(
        self,
        data: dict[str, Any],
        /,
        *,
        bet_amount: int | None = None,
        modifier: Modifier | None = None,
        cache: bool = True,
        probability_model: type[ProbabilityModel] = OriginalModel,
    ) -> None:
        # so it's not changing old cache data around, have a deep copy (safety precaution for custom odds)
        self._data: RoundData = orjson.loads(orjson.dumps(data))
        self._bet_amount = bet_amount
        self._data_dict = {}
        self._stds: tuple[tuple[float, ...], ...] = ()
        self._maxbet_odds_cache = np.array([])
        self._net_expected_cache = np.array([])

        self._modifier = modifier or Modifier()
        self._modifier._nfc = self
        self._arenas: Arenas | None = None
        self._probability_model = probability_model

        if cache:
            self.reset()
        else:
            self.soft_reset()

    def _add_custom_odds(self) -> None:
        if not self._modifier.custom_odds:
            return

        for k1, a in enumerate(self._data["pirates"]):
            for k2, p in enumerate(a):
                # custom, user-added odds
                if p in self._modifier.custom_odds:
                    self._data["customOdds"][k1][k2 + 1] = self._modifier.custom_odds[p]  # type: ignore

    def soft_reset(self) -> None:
        """Resets the custom odds used internally."""
        # the way custom odds + custom time works: (sorry!)
        # we determine if we have opening odds set,
        # if we do, our custom odds will start from there, otherwise current odds
        # if there's a custom time set, then we start from opening odds, and seek
        # changes up to the custom time
        # after that, we add custom odds.
        key = "openingOdds" if self._modifier.opening_odds else "currentOdds"

        # this is where customOdds gets set, which the rest of the NFC object is
        # based on.
        self._data["customOdds"] = orjson.loads(orjson.dumps(self._data[key]))

        if self._modifier.time and (dt := self._get_round_time(self._modifier.time)):
            # start custom odds from opening odds and add from there
            self._data["customOdds"] = orjson.loads(
                orjson.dumps(self._data["openingOdds"])
            )
            for change in self.changes:
                if change.timestamp < dt:
                    self._data["customOdds"][change.arena_index][
                        change.pirate_index
                    ] = change.new

        self._add_custom_odds()

    def reset(self) -> None:
        """Recalculates the odds used to create bets with."""
        self.soft_reset()

        self._cache_dicts()

    def _cache_bet_amount_dicts(self) -> None:
        # cache maxbets, we'll need these a lot later,
        # but only if we need them at all

        if bet_amount := self._bet_amount:
            mb_copy = self._data_dict["maxbets"].copy()
            mb_copy[mb_copy > bet_amount] = bet_amount
            self._maxbet_odds_cache = utils.fix_bet_amounts(mb_copy)

            # for making maxter faster...
            self._net_expected_cache = mb_copy * self._data_dict["ers"] - mb_copy

    def _cache_dicts(self) -> None:
        self._stds = self._probability_model(self).probabilities
        # most of the binary/odds/std data sits here
        (_bins, _stds, _odds, _ers, _maxbets) = math.make_round_dicts(
            self._stds,
            tuple(tuple(row) for row in self._data["customOdds"]),  # type: ignore
        )
        # convert the dict items to shapes we'll need:
        self._data_dict["std"] = _stds
        self._data_dict["ers"] = _ers
        self._data_dict["bins"] = _bins
        self._data_dict["odds"] = _odds.astype(int)
        self._data_dict["maxbets"] = _maxbets.astype(int)

        self._cache_bet_amount_dicts()

    def get_arena(self, arena_id: int, /) -> Arena:
        """:class:Arena: Returns the desired Arena object."""
        return self.arenas[arena_id]

    @property
    def arenas(self) -> Arenas:
        """:class:`Arenas`: Returns the Arenas object for this round."""
        if self._arenas:
            return self._arenas

        self._arenas = Arenas(self)
        return self._arenas

    @property
    def bet_amount(self) -> int | None:
        """Optional[:class:`int`]: An integer representing a bet amount to be used for generating bets."""
        return self._bet_amount

    @bet_amount.setter
    def bet_amount(self, val: int | None) -> None:
        if val != self._bet_amount:
            self._bet_amount = val
            if self._data_dict:
                self._cache_bet_amount_dicts()
            else:
                self._cache_dicts()

    @property
    def modifier(self) -> Modifier:
        """:class:`Modifier`: The desired modifier for generating bets."""
        return self._modifier

    @modifier.setter
    def modifier(self, val: Modifier | None) -> None:
        """Sets this NeoFoodClub object's modifier as a copy of the passed-in modifier."""
        val = val or Modifier()

        reset = self._modifier != val
        self._modifier = val
        self._modifier._nfc = self

        if reset:
            self.reset()

    @property
    def modified(self) -> bool:
        """:class:`bool`: Whether or not this NeoFoodClub object has been modified heavily enough that it does not
        resemble the original data.
        """
        if self._modifier.custom_odds:
            return True

        if self._modifier.time is not None:
            return True

        if self._modifier.opening_odds:
            return True

        return False

    def with_modifier(self, modifier: Modifier | None = None, /) -> Self:
        """Applies the supplied modifier to the NeoFoodClub object.

        Parameters
        ----------
        modifier: Optional[:class:`Modifier`]
        The modifier object you'd like to add to this NeoFoodClub object.
        """
        self.modifier = modifier
        return self

    def to_dict(self, *, keep_custom: bool = False) -> dict[str, Any]:
        """:class:`Dict[str, Any]`: Returns the data used to make this NeoFoodClub object.

        Parameters
        ----------
        keep_custom: :class:`bool`
            Whether or not you'd like to keep the customOdds data key. False by default.
        """
        # return a deep copy of this round's dict
        data = orjson.loads(orjson.dumps(self._data))
        if not keep_custom:
            data.pop("customOdds", None)
        return data

    @property
    def pirates(self) -> list[list[int]]:
        """List[List[:class:`int`]]: Returns a nested list of the pirate IDs per-arena."""
        return self._data["pirates"]

    @property
    def opening_odds(self) -> list[list[int]]:
        """List[List[:class:`int`]]: Returns a nested list of the opening odds per-arena."""
        return self._data["openingOdds"]

    @property
    def current_odds(self) -> list[list[int]]:
        """List[List[:class:`int`]]: Returns a nested list of the current odds per-arena."""
        return self._data["currentOdds"]

    @property
    def custom_odds(self) -> list[list[int]]:
        """List[List[:class:`int`]]: Returns a nested list of the custom odds per-arena.

        These values are mostly just used internally as a second layer of current_odds.
        This may or may not be identical to current_odds.
        """
        return self._data["customOdds"]  # type: ignore

    @property
    def round(self) -> int:
        """:class:`int`: The current round's number."""
        return int(self._data["round"])

    @property
    def start(self) -> datetime.datetime | None:
        """Optional[datetime.datetime]: When the round started in UTC, if applicable."""
        if start := self._data.get("start"):
            return dateutil.parser.parse(start).astimezone(UTC)
        return None

    @property
    def timestamp(self) -> datetime.datetime | None:
        """Optional[datetime.datetime]: When the round data was last updated in UTC, if applicable."""
        if timestamp := self._data.get("timestamp"):
            return dateutil.parser.parse(timestamp).astimezone(UTC)
        return None

    def _get_round_time(self, t: datetime.time) -> datetime.datetime | None:
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
        """:class:`bool`: Returns whether or not this round is to be considered over. 24 hours after the start time."""
        if self.start is None:
            return True
        today = self.start.astimezone(tzutc()) + datetime.timedelta(days=1)

        difference = utils.get_dst_offset(today)

        return not (self.start <= datetime.datetime.now(tzutc()) <= today + difference)

    @property
    def is_over(self) -> bool:
        """:class:`bool`: Returns whether or not the round is over based on having any winning pirates."""
        # if any of them are > 0, it's over. might as well check just the first.
        return bool(self.winners[0])

    @property
    def winners(self) -> tuple[int, ...]:
        """Tuple[:class:`int`]: Returns the winning pirates, if applicable.
        A tuple of 5 zeroes if not applicable.
        """
        return tuple(self._data.get("winners") or (0, 0, 0, 0, 0))

    @property
    def winners_binary(self) -> int:
        """:class:`int`: Returns a bet-binary representation of the winning pirates, if applicable.
        0 if not applicable.
        """
        return math.pirates_binary(tuple(self.winners))

    @property
    def winners_pirates(self) -> tuple[Pirate, ...]:
        """Tuple[:class:`Pirate`]: Returns a list of the winning pirates, as Pirate objects, if applicable.
        Empty tuple if not applicable.
        """
        return self.arenas.get_pirates_from_binary(self.winners_binary)

    @property
    def foods(self) -> list[list[int]] | None:
        """Optional[List[List[:class:`int`]]]: Returns a nested list of each arena's foods for this round.
        Can be None.
        """
        return self._data.get("foods")

    @property
    def changes(self) -> list[OddsChange]:
        """List[:class:`OddsChange`]: Returns a list of changes for this round."""
        copied_data = self.to_dict()
        changed = [
            OddsChange(index=idx, round_data=copied_data, data=c)
            for idx, c in enumerate(copied_data.get("changes") or [])
        ]
        return sorted(changed, key=lambda oc: oc.timestamp)

    @_require_cache
    def _get_winning_bet_indices(self, bets: Bets, /) -> npt.NDArray[np.int16]:
        bet_bins = self._data_dict["bins"][bets._indices]
        winning_bet_indices = np.where(bet_bins & self.winners_binary == bet_bins)[0]
        return bets._indices[winning_bet_indices]

    @_require_cache
    def _get_winning_odds(self, bets: Bets) -> npt.NDArray[np.int32]:
        winning_bet_bins = self._get_winning_bet_indices(bets)
        return self._data_dict["odds"][winning_bet_bins]

    @_require_cache
    def get_win_units(self, bets: Bets, /) -> int:
        """Returns the amount of units that won, given the provided bets.

        Parameters
        ----------
        bets: :class:`Bets`
            The bets you'd like to find the amount of winning units for.
        """
        return self._get_winning_odds(bets).sum()

    @_require_cache
    def get_win_np(self, bets: Bets, /) -> int:
        """Returns the amount of neopoints that won, given the provided bets.
        If the bets object has no bet amounts, will return 0.

        Parameters
        ----------
        bets: :class:`Bets`
            The bets you'd like to find the amount of winning neopoints for.
        """
        winning_bins_indices = self._get_winning_bet_indices(bets)

        if winning_bins_indices.size == 0:
            # these bets lost
            return 0

        if np.all(bets.bet_amounts > -1000):
            multiplier = bets.bet_amounts
        else:
            return 0

        mask = np.in1d(bets._indices, winning_bins_indices)
        bets_odds: npt.NDArray[np.int32] = self._data_dict["odds"][bets._indices]

        winnings: npt.NDArray[np.int32] = (bets_odds * multiplier)[mask]

        winnings.clip(0, 1_000_000, out=winnings)

        return winnings.sum()

    def make_url(
        self,
        bets: Bets | None = None,
        /,
        *,
        all_data: bool = False,
        include_domain: bool = True,
    ) -> str:
        """:class:`str`: Returns an optionally-fully-loaded NeoFoodClub URL to describe the provided bets.

        Parameters
        ----------
        bets: :class:`Bets`
            The bets you'd like to make the URL for.
        all_data: :class:`bool`
            Whether or not you want the URL with all pirates, odds, etc. included. Usually, this is not necessary.
            Default = False.
        include_domain: :class:`bool`
            Whether or not you want the output URL to include the preferred neofoodclub website's domain.
            Default = True.
        """

        use_15 = (
            len(bets or []) and 10 < len(bets or []) <= 15
        ) or self._modifier._cc_perk

        # begin building the URL!
        url = ""

        if include_domain:
            url += "https://neofood.club"

        if use_15:  # pragma: no cover
            url += "/15"

        url += f"/#round={self.round}"

        if all_data:  # pragma: no cover

            def encode(int_lists: Sequence[Any]) -> str:
                return orjson.dumps(int_lists).decode("utf-8")

            params: list[tuple[str, str]] = [
                ("pirates", encode(self.pirates)),
                ("openingOdds", encode(self.opening_odds)),
                ("currentOdds", encode(self.current_odds)),
            ]

            if self.foods is not None:
                params.append(("foods", encode(self.foods)))

            if self.is_over:
                params.append(("winners", encode(self.winners)))

            if self.timestamp:
                timestamp = self.timestamp.replace(
                    microsecond=0, tzinfo=datetime.timezone.utc
                ).isoformat()
                params.append(("timestamp", timestamp))

            url += "".join([f"&{k}={v}" for k, v in params])

        if bets:
            url += f"&b={bets.bets_hash}"
            if np.all(bets.bet_amounts > -1000):
                url += f"&a={bets.amounts_hash}"

        return url

    @classmethod
    def from_url(
        cls,
        url: str,
        /,
        *,
        bet_amount: int | None = None,
        modifier: Modifier | None = None,
        cache: bool = True,
    ) -> NeoFoodClub:
        """:class:`NeoFoodClub`: Create a NeoFoodClub object using just a URL.

        Parameters
        ----------
        url: :class:`str`
            The URL describing this NeoFoodClub round.
        bet_amount: Optional[:class:`int`]
            An integer representing a bet amounts to be used for generating bets.
        modifier: Optional[:class:`Modifier`]
            The desired modifier for generating bets.

        Raises
        ------
        ~neofoodclub.InvalidData
            The URL provided is invalid.
        """
        neo_fc = NEO_FC_REGEX.search(url)
        if neo_fc is None:
            raise InvalidData("No relevant NeoFoodClub-like URL data found.")

        if modifier is None:
            modifier = Modifier()

        if bool(neo_fc.group("perk")):
            modifier.cc_perk = True

        querystring = url.partition("#")[-1]

        olddata = urllib.parse.parse_qs(urllib.parse.unquote(querystring))

        # gather relevant variables from the query string
        data = {}

        # FOODS - OPTIONAL
        if foods := olddata.get("foods"):
            # optional! will ignore invalid foods.
            # foods is a list[list[int]]
            # with length of 5, but the inner tuples have a length of 10

            foods_string = foods[0]
            if FOODS_REGEX.match(foods_string):
                data["foods"] = orjson.loads(foods_string)

        # WINNERS - OPTIONAL
        if winners := olddata.get("winners"):
            # winners is a list[int] of length 5
            # if there are no winners, it's [0, 0, 0, 0, 0]
            # if there are winners, all ints any number from 1 to 4
            winners_string = winners[0]

            if not WINNERS_REGEX.match(winners_string):
                # if we have SOMETHING, it better be right!
                raise InvalidData("NeoFoodClub URL parameter `winners` is invalid.")

            data["winners"] = orjson.loads(winners_string)
        else:
            # don't raise an error if it's missing, just assume no winners.
            data["winners"] = [0, 0, 0, 0, 0]

        # ROUND NUMBER - MANDATORY
        # we only need the round number to make a proper URL
        # the actual value doesn't matter as long as it's a positive integer
        if not (bet_round := olddata.get("round")):
            raise InvalidData("NeoFoodClub URL parameter `round` is missing.")

        bet_number = bet_round[0]

        if re.match(r"^\d+$", bet_number) is None:
            raise InvalidData("NeoFoodClub URL parameter `round` is invalid.")

        data["round"] = orjson.loads(bet_number)

        # PIRATES - MANDATORY
        if not (pirates := olddata.get("pirates")):
            raise InvalidData("NeoFoodClub URL parameter `pirates` is missing.")

        pirate_string = pirates[0]
        if PIRATES_REGEX.match(pirate_string) is None:
            raise InvalidData("NeoFoodClub URL parameter `pirates` is invalid.")

        pirate_lists = orjson.loads(pirate_string)
        has_proper_ids = set(sum(pirate_lists, [])) == set(range(1, 21))
        if not has_proper_ids:
            raise InvalidData("NeoFoodClub URL parameter `pirates` is invalid.")

        data["pirates"] = pirate_lists

        # ODDS - MANDATORY
        # matches something like "[[1,2,2,2,2],[1,2,2,2,2],[1,2,2,2,2],[1,2,2,2,2],[1,2,2,2,2]]", the 2's can be any number from 2 to 13
        for odd_type in ["openingOdds", "currentOdds"]:
            if odd_type not in olddata:
                raise InvalidData(f"NeoFoodClub URL parameter `{odd_type}` is missing")

            odds = olddata[odd_type][0]
            if ODDS_REGEX.match(odds) is None:
                raise InvalidData(f"NeoFoodClub URL parameter `{odd_type}` is invalid")

            data[odd_type] = orjson.loads(odds)

        # START, TIMESTAMP - OPTIONAL
        for key in ["start", "timestamp"]:
            # optional! just need to be sure it doesn't break the parser.
            if timestamp := olddata.get(key):
                timestamp_string = timestamp[0]
                with contextlib.suppress(dateutil.parser.ParserError):
                    dateutil.parser.parse(timestamp_string).astimezone(UTC)
                    # if it works, let it through.
                    data[key] = timestamp_string

        return cls(data, bet_amount=bet_amount, modifier=modifier, cache=cache)

    def copy(self, *, keep_custom: bool = False, cache: bool = True) -> NeoFoodClub:
        """:class:`NeoFoodClub`: Returns a deep copy of this NeoFoodClub instance."""
        return NeoFoodClub(
            self.to_dict(keep_custom=keep_custom),
            bet_amount=self._bet_amount,
            modifier=self._modifier,
            cache=cache,
        )

    def __repr__(self) -> str:
        attrs = [
            ("round", self.round),
            ("bet_amount", self._bet_amount),
            ("timestamp", self.timestamp),
            ("is_over", self.is_over),
        ]
        joined = " ".join("{}={!r}".format(*t) for t in attrs if t[1] is not None)
        return f"<NeoFoodClub {joined}>"

    @property
    def max_amount_of_bets(self) -> int:
        """:class:`int`: Returns the maximum amount of bets that can be generated. Will be 10, unless
        this class' Modifier has the Charity Corner perk attribute set to True, in which case it returns 15.
        """
        return 15 if self._modifier._cc_perk else 10

    @_require_cache
    def _max_ter_indices(self) -> np.ndarray:
        # use net expected only if needed
        if self._modifier.general or self._net_expected_cache.size == 0:
            indices = self._data_dict["ers"]
        else:
            indices = self._net_expected_cache

        if self._modifier.reverse:
            indices = indices[::-1]

        return indices

    @_require_cache
    def make_max_ter_bets(self) -> Bets:
        """:class:`Bets`: Creates a Bets object that consists of the highest ERs."""
        return Bets._from_generator(
            indices=np.argsort(self._max_ter_indices()), nfc=self
        )

    @_require_cache
    def _crazy_bets_indices(self) -> np.ndarray:
        return math.FULL_BETS[
            np.random.randint(math.FULL_BETS.size, size=self.max_amount_of_bets)
        ]

    @_require_cache
    def make_crazy_bets(self) -> Bets:
        """:class:`Bets`: Creates a Bets object that consists of randomly-selected, full-arena bets.

        These bets are not for the faint of heart.
        """
        return Bets._from_generator(indices=self._crazy_bets_indices(), nfc=self)

    @_require_cache
    def _random_indices(self) -> np.ndarray:
        return np.random.randint(3124, size=self.max_amount_of_bets)

    @_require_cache
    def make_random_bets(self) -> Bets:
        """:class:`Bets`: Creates a Bets object that consists of randomly-selected bets.

        These bets are not for the faint of heart.
        """
        return Bets._from_generator(indices=self._random_indices(), nfc=self)

    @_require_cache
    def _gambit_indices(
        self, *, five_bet: int | None = None, random: bool = False
    ) -> np.ndarray:
        if five_bet is not None:
            bins = self._data_dict["bins"]
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
                math.FULL_BETS[np.random.randint(math.FULL_BETS.size, size=1)]
            ]
            return self._gambit_indices(five_bet=random_five_bet[0])

        # get highest ER pirates
        ers = self._max_ter_indices()[math.FULL_BETS]
        highest_er = np.argsort(ers, kind="mergesort", axis=0)[::-1][0]
        pirate_bin = self._data_dict["bins"][math.FULL_BETS[highest_er]]
        return self._gambit_indices(five_bet=pirate_bin)

    @_require_cache
    def make_all_bets(self, in_order: bool = False, max_ter: bool = False) -> Bets:
        """:class:`Bets`: Creates a Bets object that consists of all bets.

        This is mostly for debugging purposes.
        """
        if in_order and max_ter:
            raise ValueError("Cannot use both in_order and max_ter")

        bet_amounts = None

        if self._maxbet_odds_cache.size > 0:
            bet_amounts = list(self._maxbet_odds_cache)

        if max_ter:
            return Bets(
                indices=np.argsort(self._max_ter_indices())[::-1],
                nfc=self,
                amounts=bet_amounts,
            )

        return Bets(indices=np.arange(3124), nfc=self, amounts=bet_amounts)

    @overload
    def make_gambit_bets(self, *, five_bet: int | None = None) -> Bets:
        ...

    @overload
    def make_gambit_bets(self, *, random: bool = False) -> Bets:
        ...

    @_require_cache
    def make_gambit_bets(
        self, *, five_bet: int | None = None, random: bool = False
    ) -> Bets:
        """:class:`Bets`: Creates a Bets object that consists of the top-unit permutations
        of a single full-arena bet.
        """
        return Bets._from_generator(
            indices=self._gambit_indices(five_bet=five_bet, random=random), nfc=self
        )

    @_require_cache
    def _tenbet_indices(self, pirate_binary: int) -> np.ndarray:
        bins = self._data_dict["bins"]
        possible_indices = np.where(bins & pirate_binary == pirate_binary)[0]

        ers = (
            self._net_expected_cache
            if self._net_expected_cache.size > 0
            else self._data_dict["ers"]
        )

        sorted_odds = np.argsort(ers[possible_indices], kind="mergesort", axis=0)

        return possible_indices[sorted_odds]

    @_require_cache
    def make_tenbet_bets(self, pirate_binary: int, /) -> Bets:
        """:class:`Bets`: Creates a Bets object that consists of the highest Expected Ratio -- or Net Expected -- bets
        that include between 1 and 3 selected pirates.

        There is a hard limit on 3 because any more is impossible.

        Raises
        ------
        ~neofoodclub.InvalidData
        The amount of selected pirates is not between 1 and 3.
        """
        amount_of_pirates = sum(1 for mask in math.BIT_MASKS if pirate_binary & mask)

        if amount_of_pirates == 0:
            raise InvalidData("You must pick at least 1 pirate, and at most 3.")

        if amount_of_pirates > 3:
            raise InvalidData("You must pick 3 pirates at most.")

        return Bets._from_generator(
            indices=self._tenbet_indices(pirate_binary), nfc=self
        )

    @_require_cache
    def _unit_indices(self, units: int) -> np.ndarray:
        sorted_std = np.argsort(self._data_dict["std"], kind="mergesort", axis=0)
        possible_indices = np.where(self._data_dict["odds"][sorted_std] >= units)[0]
        return sorted_std[possible_indices]

    @_require_cache
    def make_units_bets(self, units: int, /) -> Bets:
        """:class:`Bets`: Creates a Bets object that consists of the highest STD probability that are greater than or
        equal to the units value.

        This CAN return an empty Bets object.
        """
        return Bets._from_generator(indices=self._unit_indices(units), nfc=self)

    @_require_cache
    def make_bustproof_bets(self) -> Bets:
        """:class:`Bets`: Creates a Bets object that consists of the bets made in such a way that with a given bet
        amount, you will not bust.

        This requires at least one positive arena, otherwise will throw :class:`NoPositiveArenas`.

        Raises
        ------
        ~neofoodclub.NoPositiveArenas
            There are no positive arenas, so a bustproof set can not be made.
        """
        arenas = self.arenas
        positives = arenas.positives
        if not positives:
            # nothing to do here!
            raise NoPositiveArenas

        positive_count = len(positives)

        if positive_count == 1:
            # If only one arena is positive, we place 1 bet on each of the pirates of that arena. Total bets = 4.
            best_arena = arenas.best[0]
            bets = Bets.from_binary(*(p.binary for p in best_arena.pirates), nfc=self)
        elif positive_count == 2:
            # If two arenas are positive, we place 1 bet on each of the three worst pirates of the best arena and
            # 1 bet on each of the pirates of the second arena + the best pirate of the best arena. Total bets = 7
            best_arena, second_arena = arenas.best[:2]

            best_arena_sorted = best_arena.best

            best_pirate_binary = best_arena_sorted[0].binary
            bets = Bets.from_binary(
                *(p.binary for p in best_arena_sorted[-3:]),
                *(p.binary | best_pirate_binary for p in second_arena.pirates),
                nfc=self,
            )
        else:
            # If three arenas are positive, we place 1 bet on each of the three worst pirates of the best arena,
            # If four or more arenas are positive, we only play the three best arenas, seen below
            # 1 bet on each of the three worst pirates of the second arena + the best pirate of the best arena,
            # and 1 bet on each of the pirates of the third arena + the best pirate of the best arena + the best pirate
            # of the second arena. Total bets = 10.
            best_arena, second_arena, third_arena = arenas.best[:3]

            best_arena_sorted = best_arena.best
            second_best_arena_sorted = second_arena.best
            best_pirate_binary = best_arena_sorted[0].binary
            second_best_pirate_binary = second_best_arena_sorted[0].binary

            bets = Bets.from_binary(
                *(p.binary for p in best_arena_sorted[-3:]),
                *(p.binary | best_pirate_binary for p in second_best_arena_sorted[-3:]),
                *(
                    p.binary | best_pirate_binary | second_best_pirate_binary
                    for p in third_arena.best
                ),
                nfc=self,
            )

        if bet_amount := self.bet_amount:
            current_odds = self._data_dict["odds"][bets._indices]
            lowest_odds = current_odds[np.argmin(current_odds)]

            new_bet_amounts = bet_amount * lowest_odds // current_odds
            bets.bet_amounts = new_bet_amounts

        return bets

    # bet decoding methods

    @overload
    def make_bets_from_indices(self, indices: Sequence[Sequence[int]], /) -> Bets:
        ...

    @overload
    def make_bets_from_indices(
        self, indices: Sequence[Sequence[int]], /, *, amounts_hash: str | None
    ) -> Bets:
        ...

    @overload
    def make_bets_from_indices(
        self, indices: Sequence[Sequence[int]], /, *, amounts: Sequence[int]
    ) -> Bets:
        ...

    @overload
    def make_bets_from_indices(
        self, indices: Sequence[Sequence[int]], /, *, amount: int
    ) -> Bets:
        ...

    @_require_cache
    def make_bets_from_indices(
        self,
        indices: Sequence[Sequence[int]],
        /,
        *,
        amounts_hash: str | None = None,
        amounts: Sequence[int] | None = None,
        amount: int | None = None,
    ) -> Bets:
        """:class:`Bets`: Creates a Bets object made up of arena indices.

        Raises
        ------
        ~neofoodclub.InvalidAmountHash
        The amount hash contains invalid characters.
        """
        bets = Bets.from_binary(*math.bets_indices_to_bet_binaries(indices), nfc=self)
        if amounts_hash:
            if not AMOUNT_HASH_REGEX.fullmatch(amounts_hash):
                raise InvalidAmountHash
            bets.bet_amounts = math.amounts_hash_to_bet_amounts(amounts_hash)
        if amounts is not None:
            bets.bet_amounts = amounts
        if amount is not None:
            bets.bet_amounts = [amount] * len(bets)

        return bets

    @overload
    def make_bets_from_hash(self, bets_hash: str, /) -> Bets:
        ...

    @overload
    def make_bets_from_hash(
        self, bets_hash: str, /, *, amounts_hash: str | None
    ) -> Bets:
        ...

    @overload
    def make_bets_from_hash(self, bets_hash: str, /, *, amounts: Sequence[int]) -> Bets:
        ...

    @overload
    def make_bets_from_hash(self, bets_hash: str, /, *, amount: int) -> Bets:
        ...

    @_require_cache
    def make_bets_from_hash(
        self,
        bets_hash: str,
        /,
        *,
        amounts_hash: str | None = None,
        amounts: Sequence[int] | None = None,
        amount: int | None = None,
    ) -> Bets:
        """:class:`Bets`: Creates a Bets object by decoding from bets_hash (and optionally an amounts_hash).

        Raises
        ------
        ~neofoodclub.InvalidBetHash
            The bet hash contains invalid characters.
        ~neofoodclub.InvalidAmountHash
        The amount hash contains invalid characters.
        """
        if not BET_HASH_REGEX.fullmatch(bets_hash):
            raise InvalidBetHash

        bets = Bets.from_binary(*math.bets_hash_to_bet_binaries(bets_hash), nfc=self)
        if amounts_hash:
            if not AMOUNT_HASH_REGEX.fullmatch(amounts_hash):
                raise InvalidAmountHash
            bets.bet_amounts = math.amounts_hash_to_bet_amounts(amounts_hash)
        if amounts is not None:
            bets.bet_amounts = amounts
        if amount is not None:
            bets.bet_amounts = [amount] * len(bets)

        return bets

    @overload
    def make_bets_from_binaries(self, *binaries: int) -> Bets:
        ...

    @overload
    def make_bets_from_binaries(self, *binaries: int, amounts_hash: str | None) -> Bets:
        ...

    @overload
    def make_bets_from_binaries(self, *binaries: int, amounts: Sequence[int]) -> Bets:
        ...

    @overload
    def make_bets_from_binaries(self, *binaries: int, amount: int) -> Bets:
        ...

    @_require_cache
    def make_bets_from_binaries(
        self,
        *binaries: int,
        amounts_hash: str | None = None,
        amounts: Sequence[int] | None = None,
        amount: int | None = None,
    ) -> Bets:
        """:class:`Bets`: Creates a Bets object made up of bet-compatible binary numbers.

        Raises
        ------
        ~neofoodclub.InvalidAmountHash
        The amount hash contains invalid characters.
        """
        bets = Bets.from_binary(*binaries, nfc=self)
        if amounts_hash:
            if not AMOUNT_HASH_REGEX.fullmatch(amounts_hash):
                raise InvalidAmountHash
            bets.bet_amounts = math.amounts_hash_to_bet_amounts(amounts_hash)
        if amounts is not None:
            bets.bet_amounts = amounts
        if amount is not None:
            bets.bet_amounts = [amount] * len(bets)

        return bets
