from __future__ import annotations

import contextlib
import datetime
import functools
import operator
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
from neofoodclub.neofoodclub import Math, make_round_dicts
from neofoodclub.odds_change import OddsChange

from . import utils
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
    r"^\[(\[1,(([2-9]|1[0-3]),){3}([2-9]|1[0-3])\],){4}\[1,(([2-9]|1[0-3]),){3}([2-9]|1[0-3])\]\]$",
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
                orjson.dumps(self._data["openingOdds"]),
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
        (_bins, _stds, _odds, _ers, _maxbets) = make_round_dicts(
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
        return Math.pirates_binary(tuple(self.winners))

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
                    microsecond=0, tzinfo=datetime.timezone.utc,
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
        has_proper_ids = set(functools.reduce(operator.iadd, pirate_lists, [])) == set(
            range(1, 21),
        )
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
            indices=np.argsort(self._max_ter_indices()), nfc=self,
        )

    @_require_cache
    def _crazy_bets_indices(self) -> np.ndarray:
        return FULL_BETS[
            np.random.randint(FULL_BETS.size, size=self.max_amount_of_bets)
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
        self, *, five_bet: int | None = None, random: bool = False,
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
                FULL_BETS[np.random.randint(FULL_BETS.size, size=1)]
            ]
            return self._gambit_indices(five_bet=random_five_bet[0])

        # get highest ER pirates
        ers = self._max_ter_indices()[FULL_BETS]
        highest_er = np.argsort(ers, kind="mergesort", axis=0)[::-1][0]
        pirate_bin = self._data_dict["bins"][FULL_BETS[highest_er]]
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
        self, *, five_bet: int | None = None, random: bool = False,
    ) -> Bets:
        """:class:`Bets`: Creates a Bets object that consists of the top-unit permutations
        of a single full-arena bet.
        """
        return Bets._from_generator(
            indices=self._gambit_indices(five_bet=five_bet, random=random), nfc=self,
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
        amount_of_pirates = sum(bool(pirate_binary & mask) for mask in Math.BIT_MASKS)

        if amount_of_pirates == 0:
            raise InvalidData("You must pick at least 1 pirate, and at most 3.")

        if amount_of_pirates > 3:
            raise InvalidData("You must pick 3 pirates at most.")

        return Bets._from_generator(
            indices=self._tenbet_indices(pirate_binary), nfc=self,
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
        self, indices: Sequence[Sequence[int]], /, *, amounts_hash: str | None,
    ) -> Bets:
        ...

    @overload
    def make_bets_from_indices(
        self, indices: Sequence[Sequence[int]], /, *, amounts: Sequence[int],
    ) -> Bets:
        ...

    @overload
    def make_bets_from_indices(
        self, indices: Sequence[Sequence[int]], /, *, amount: int,
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
        bets = Bets.from_binary(*Math.bets_indices_to_bet_binaries(indices), nfc=self)
        if amounts_hash:
            if not AMOUNT_HASH_REGEX.fullmatch(amounts_hash):
                raise InvalidAmountHash
            bets.bet_amounts = Math.amounts_hash_to_bet_amounts(amounts_hash)
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
        self, bets_hash: str, /, *, amounts_hash: str | None,
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

        bets = Bets.from_binary(*Math.bets_hash_to_bet_binaries(bets_hash), nfc=self)
        if amounts_hash:
            if not AMOUNT_HASH_REGEX.fullmatch(amounts_hash):
                raise InvalidAmountHash

            bets.bet_amounts = Math.amounts_hash_to_bet_amounts(amounts_hash)
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
            bets.bet_amounts = Math.amounts_hash_to_bet_amounts(amounts_hash)
        if amounts is not None:
            bets.bet_amounts = amounts
        if amount is not None:
            bets.bet_amounts = [amount] * len(bets)

        return bets


# fmt: off
FULL_BETS = np.array([780, 781, 782, 783, 785, 786, 787, 788, 790, 791, 792, 793, 795, 796, 797, 798, 805, 806, 807, 808, 810, 811, 812, 813, 815, 816, 817, 818, 820, 821, 822, 823, 830, 831, 832, 833, 835, 836, 837, 838, 840, 841, 842, 843, 845, 846, 847, 848, 855, 856, 857, 858, 860, 861, 862, 863, 865, 866, 867, 868, 870, 871, 872, 873, 905, 906, 907, 908, 910, 911, 912, 913, 915, 916, 917, 918, 920, 921, 922, 923, 930, 931, 932, 933, 935, 936, 937, 938, 940, 941, 942, 943, 945, 946, 947, 948, 955, 956, 957, 958, 960, 961, 962, 963, 965, 966, 967, 968, 970, 971, 972, 973, 980, 981, 982, 983, 985, 986, 987, 988, 990, 991, 992, 993, 995, 996, 997, 998, 1030, 1031, 1032, 1033, 1035, 1036, 1037, 1038, 1040, 1041, 1042, 1043, 1045, 1046, 1047, 1048, 1055, 1056, 1057, 1058, 1060, 1061, 1062, 1063, 1065, 1066, 1067, 1068, 1070, 1071, 1072, 1073, 1080, 1081, 1082, 1083, 1085, 1086, 1087, 1088, 1090, 1091, 1092, 1093, 1095, 1096, 1097, 1098, 1105, 1106, 1107, 1108, 1110, 1111, 1112, 1113, 1115, 1116, 1117, 1118, 1120, 1121, 1122, 1123, 1155, 1156, 1157, 1158, 1160, 1161, 1162, 1163, 1165, 1166, 1167, 1168, 1170, 1171, 1172, 1173, 1180, 1181, 1182, 1183, 1185, 1186, 1187, 1188, 1190, 1191, 1192, 1193, 1195, 1196, 1197, 1198, 1205, 1206, 1207, 1208, 1210, 1211, 1212, 1213, 1215, 1216, 1217, 1218, 1220, 1221, 1222, 1223, 1230, 1231, 1232, 1233, 1235, 1236, 1237, 1238, 1240, 1241, 1242, 1243, 1245, 1246, 1247, 1248, 1405, 1406, 1407, 1408, 1410, 1411, 1412, 1413, 1415, 1416, 1417, 1418, 1420, 1421, 1422, 1423, 1430, 1431, 1432, 1433, 1435, 1436, 1437, 1438, 1440, 1441, 1442, 1443, 1445, 1446, 1447, 1448, 1455, 1456, 1457, 1458, 1460, 1461, 1462, 1463, 1465, 1466, 1467, 1468, 1470, 1471, 1472, 1473, 1480, 1481, 1482, 1483, 1485, 1486, 1487, 1488, 1490, 1491, 1492, 1493, 1495, 1496, 1497, 1498, 1530, 1531, 1532, 1533, 1535, 1536, 1537, 1538, 1540, 1541, 1542, 1543, 1545, 1546, 1547, 1548, 1555, 1556, 1557, 1558, 1560, 1561, 1562, 1563, 1565, 1566, 1567, 1568, 1570, 1571, 1572, 1573, 1580, 1581, 1582, 1583, 1585, 1586, 1587, 1588, 1590, 1591, 1592, 1593, 1595, 1596, 1597, 1598, 1605, 1606, 1607, 1608, 1610, 1611, 1612, 1613, 1615, 1616, 1617, 1618, 1620, 1621, 1622, 1623, 1655, 1656, 1657, 1658, 1660, 1661, 1662, 1663, 1665, 1666, 1667, 1668, 1670, 1671, 1672, 1673, 1680, 1681, 1682, 1683, 1685, 1686, 1687, 1688, 1690, 1691, 1692, 1693, 1695, 1696, 1697, 1698, 1705, 1706, 1707, 1708, 1710, 1711, 1712, 1713, 1715, 1716, 1717, 1718, 1720, 1721, 1722, 1723, 1730, 1731, 1732, 1733, 1735, 1736, 1737, 1738, 1740, 1741, 1742, 1743, 1745, 1746, 1747, 1748, 1780, 1781, 1782, 1783, 1785, 1786, 1787, 1788, 1790, 1791, 1792, 1793, 1795, 1796, 1797, 1798, 1805, 1806, 1807, 1808, 1810, 1811, 1812, 1813, 1815, 1816, 1817, 1818, 1820, 1821, 1822, 1823, 1830, 1831, 1832, 1833, 1835, 1836, 1837, 1838, 1840, 1841, 1842, 1843, 1845, 1846, 1847, 1848, 1855, 1856, 1857, 1858, 1860, 1861, 1862, 1863, 1865, 1866, 1867, 1868, 1870, 1871, 1872, 1873, 2030, 2031, 2032, 2033, 2035, 2036, 2037, 2038, 2040, 2041, 2042, 2043, 2045, 2046, 2047, 2048, 2055, 2056, 2057, 2058, 2060, 2061, 2062, 2063, 2065, 2066, 2067, 2068, 2070, 2071, 2072, 2073, 2080, 2081, 2082, 2083, 2085, 2086, 2087, 2088, 2090, 2091, 2092, 2093, 2095, 2096, 2097, 2098, 2105, 2106, 2107, 2108, 2110, 2111, 2112, 2113, 2115, 2116, 2117, 2118, 2120, 2121, 2122, 2123, 2155, 2156, 2157, 2158, 2160, 2161, 2162, 2163, 2165, 2166, 2167, 2168, 2170, 2171, 2172, 2173, 2180, 2181, 2182, 2183, 2185, 2186, 2187, 2188, 2190, 2191, 2192, 2193, 2195, 2196, 2197, 2198, 2205, 2206, 2207, 2208, 2210, 2211, 2212, 2213, 2215, 2216, 2217, 2218, 2220, 2221, 2222, 2223, 2230, 2231, 2232, 2233, 2235, 2236, 2237, 2238, 2240, 2241, 2242, 2243, 2245, 2246, 2247, 2248, 2280, 2281, 2282, 2283, 2285, 2286, 2287, 2288, 2290, 2291, 2292, 2293, 2295, 2296, 2297, 2298, 2305, 2306, 2307, 2308, 2310, 2311, 2312, 2313, 2315, 2316, 2317, 2318, 2320, 2321, 2322, 2323, 2330, 2331, 2332, 2333, 2335, 2336, 2337, 2338, 2340, 2341, 2342, 2343, 2345, 2346, 2347, 2348, 2355, 2356, 2357, 2358, 2360, 2361, 2362, 2363, 2365, 2366, 2367, 2368, 2370, 2371, 2372, 2373, 2405, 2406, 2407, 2408, 2410, 2411, 2412, 2413, 2415, 2416, 2417, 2418, 2420, 2421, 2422, 2423, 2430, 2431, 2432, 2433, 2435, 2436, 2437, 2438, 2440, 2441, 2442, 2443, 2445, 2446, 2447, 2448, 2455, 2456, 2457, 2458, 2460, 2461, 2462, 2463, 2465, 2466, 2467, 2468, 2470, 2471, 2472, 2473, 2480, 2481, 2482, 2483, 2485, 2486, 2487, 2488, 2490, 2491, 2492, 2493, 2495, 2496, 2497, 2498, 2655, 2656, 2657, 2658, 2660, 2661, 2662, 2663, 2665, 2666, 2667, 2668, 2670, 2671, 2672, 2673, 2680, 2681, 2682, 2683, 2685, 2686, 2687, 2688, 2690, 2691, 2692, 2693, 2695, 2696, 2697, 2698, 2705, 2706, 2707, 2708, 2710, 2711, 2712, 2713, 2715, 2716, 2717, 2718, 2720, 2721, 2722, 2723, 2730, 2731, 2732, 2733, 2735, 2736, 2737, 2738, 2740, 2741, 2742, 2743, 2745, 2746, 2747, 2748, 2780, 2781, 2782, 2783, 2785, 2786, 2787, 2788, 2790, 2791, 2792, 2793, 2795, 2796, 2797, 2798, 2805, 2806, 2807, 2808, 2810, 2811, 2812, 2813, 2815, 2816, 2817, 2818, 2820, 2821, 2822, 2823, 2830, 2831, 2832, 2833, 2835, 2836, 2837, 2838, 2840, 2841, 2842, 2843, 2845, 2846, 2847, 2848, 2855, 2856, 2857, 2858, 2860, 2861, 2862, 2863, 2865, 2866, 2867, 2868, 2870, 2871, 2872, 2873, 2905, 2906, 2907, 2908, 2910, 2911, 2912, 2913, 2915, 2916, 2917, 2918, 2920, 2921, 2922, 2923, 2930, 2931, 2932, 2933, 2935, 2936, 2937, 2938, 2940, 2941, 2942, 2943, 2945, 2946, 2947, 2948, 2955, 2956, 2957, 2958, 2960, 2961, 2962, 2963, 2965, 2966, 2967, 2968, 2970, 2971, 2972, 2973, 2980, 2981, 2982, 2983, 2985, 2986, 2987, 2988, 2990, 2991, 2992, 2993, 2995, 2996, 2997, 2998, 3030, 3031, 3032, 3033, 3035, 3036, 3037, 3038, 3040, 3041, 3042, 3043, 3045, 3046, 3047, 3048, 3055, 3056, 3057, 3058, 3060, 3061, 3062, 3063, 3065, 3066, 3067, 3068, 3070, 3071, 3072, 3073, 3080, 3081, 3082, 3083, 3085, 3086, 3087, 3088, 3090, 3091, 3092, 3093, 3095, 3096, 3097, 3098, 3105, 3106, 3107, 3108, 3110, 3111, 3112, 3113, 3115, 3116, 3117, 3118, 3120, 3121, 3122, 3123])
