from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generator, Sequence

import numpy as np

from neofoodclub import math, utils
from neofoodclub.arenas import ARENA_NAMES
from neofoodclub.errors import InvalidData
from neofoodclub.odds import Odds

if TYPE_CHECKING:
    import numpy.typing as npt

    from neofoodclub.nfc import NeoFoodClub

__all__ = ("Bets",)


class Bets:
    """A container class containing a set of bets.
    This class is not to be constructed manually.
    """

    __slots__ = (
        "_indices",
        "_bet_amounts",
        "_odds",
        "nfc",
    )

    def __init__(
        self,
        *,
        nfc: NeoFoodClub,
        indices: npt.NDArray[np.int16],
        amounts: Sequence[int | None] | None = None,
    ) -> None:
        self.nfc: NeoFoodClub = nfc
        self._indices = indices

        self.bet_amounts = amounts
        self._odds: Odds | None = None

    @property
    def net_expected(self) -> float:
        """:class:`float`: Returns the total net expected of this bet set.

        This is equal to (bet_amount * expected_ratio - bet_amount) for each bet and its associated bet amount.

        Returns 0.0 if there is no bet amount set for the NeoFoodClub object, or the bets.
        """
        if np.all(self.bet_amounts > -1000):
            return np.sum(
                self.bet_amounts * self.nfc._data_dict["ers"][self._indices]
                - self.bet_amounts
            )
        return 0.0

    ne = net_expected

    @property
    def expected_ratio(self) -> float:
        """:class:`float`: Returns the total expected ratio of this bet set."""
        return np.sum(self.nfc._data_dict["ers"][self._indices])

    er = expected_ratio

    @property
    def bet_amounts(self) -> npt.NDArray[np.int32]:
        """:class:`np.ndarray`: Returns a numpy array of bet amounts corresponding by index to these bets.

        These can be user-defined, and generated.

        If the NeoFoodClub object has a bet_amount set, and this bet object has no bet amounts, we will
        fall back to using the NeoFoodClub object's amount, capped at the max bet amount per bet.
        """
        if np.all(self._bet_amounts > -1000):
            return self._bet_amounts

        if self.nfc._maxbet_odds_cache.size:
            return self.nfc._maxbet_odds_cache[self._indices]

        return np.array([-1000] * self._indices.size)

    @bet_amounts.setter
    def bet_amounts(
        self, val: Sequence[int | None] | npt.NDArray[np.int32] | None
    ) -> None:
        if val is None:
            self._bet_amounts: npt.NDArray[np.int32] = np.array(
                [-1000] * self._indices.size
            )
            return

        # remove trailing None's
        while len(val) and val[-1] is None:
            val = val[:-1]

        # strictly enforcing amount of values provided
        if len(val) != self._indices.size:
            raise InvalidData(
                f"Invalid bet amounts provided. Expected length: {self._indices.size}, but received {len(val)}."
            )

        amts: npt.NDArray[np.int32] = np.array([v or math.BET_AMOUNT_MIN for v in val])

        self._bet_amounts = utils.fix_bet_amounts(amts)

    @property
    def indices(self) -> tuple[tuple[int, ...], ...]:
        """Tuple[Tuple[:class:`int`, ...], ...]: Returns a nested array of the indices of the pirates in their arenas
        making up these bets.
        """
        return tuple(
            math.binary_to_indices(binary)
            for binary in self.nfc._data_dict["bins"][self._indices]
        )

    @property
    def bets_hash(self) -> str:
        """:class:`str`: Returns a NeoFoodClub-compatible encoded hash of bet indices."""
        return math.bets_hash_value(self.indices)

    @property
    def amounts_hash(self) -> str:
        """:class:`str`: Returns a NeoFoodClub-compatible encoded hash of bet amounts."""
        if np.all(self.bet_amounts > -1000):
            return math.bet_amounts_to_amounts_hash(self.bet_amounts)  # type: ignore

        return ""

    def __repr__(self) -> str:
        attrs: list[tuple[str, Any]] = [
            ("ne", self.net_expected),
            ("er", self.expected_ratio),
            ("bets_hash", self.bets_hash),
            ("amounts_hash", self.amounts_hash),
        ]
        joined = " ".join("{}={!r}".format(*t) for t in attrs)
        return f"<Bets {joined}>"

    @classmethod
    def _from_generator(
        cls, *, indices: npt.NDArray[np.int16], nfc: NeoFoodClub
    ) -> Bets:
        # here is where we will take indices and sort as needed
        # to avoid confusion with "manually" making bets

        indices = indices[::-1][: nfc.max_amount_of_bets]
        return cls(nfc=nfc, indices=indices)

    @classmethod
    def from_binary(cls, *bins: int, nfc: NeoFoodClub) -> Bets:
        """:class:`Bets`: Returns a Bets object from a binary representation of bets.

        Raises
        ------
        ~neofoodclub.InvalidData
        Invalid binaries were passed.
        """
        np_bins = np.array(bins)
        # duplicate bins are removed here
        _, idx = np.unique(np_bins, return_index=True)
        np_bins = np_bins[np.sort(idx)]

        # thanks @mikeshardmind
        intersection = np.where(np_bins[:, np.newaxis] == nfc._data_dict["bins"])[1]

        if intersection.size == 0:
            raise InvalidData(
                "Bets class requires at least one valid bet binary integer."
            )

        if intersection.size != np_bins.size:
            diff = np.setxor1d(np_bins, intersection)
            raise InvalidData(
                f"Invalid bet binaries entered: {', '.join([hex(b) for b in diff])}"
            )

        return cls(nfc=nfc, indices=intersection)

    def __len__(self) -> int:
        return self._indices.size

    @property
    def odds(self) -> Odds:
        """:class:`Odds`: Creates an Odds object of this bet set."""
        if self._odds is None:
            # this is a somewhat expensive operation, so we cache it
            self._odds = Odds(self)
        return self._odds

    @property
    def is_bustproof(self) -> bool:
        """:class:`bool`: Returns whether or not this set is capable of busting."""
        return self.odds.bust is None

    @property
    def is_crazy(self) -> bool:
        """:class:`bool`: Returns whether or not this set is "crazy". This returns True if all of the bets have all arenas filled. Mostly just for fun."""
        return all(mask & bet for mask in math.BIT_MASKS for bet in self)

    @property
    def is_gambit(self) -> bool:
        """:class:`bool`: Returns whether or not this is a gambit set.

        The rules for what a gambit is, is *somewhat* arbitrary:
          - The largest integer in the binary representation of the bet set must have five 1's.
          - All bets must be subsets of the largest integer.
          - There must be at least 2 bets.
        """
        if len(self) < 2:
            return False

        int_bins = self.nfc._data_dict["bins"][self._indices]
        highest = np.max(int_bins)

        # make sure the highest has a population count of 5
        if np.array(np.unpackbits(np.array([highest]).view("uint8"))).sum() != 5:
            return False

        return bool(np.all((highest & int_bins) == int_bins))

    @property
    def is_guaranteed_win(self) -> bool:
        """:class:`bool`: Returns whether or not this set is guaranteed to profit."""
        amounts = self.bet_amounts

        if amounts is None or np.sum(amounts) <= 0:
            return False

        highest_bet_amount = np.max(amounts)
        bets_odds = self.nfc._data_dict["odds"][self._indices]
        lowest_winning_bet_amount = np.min(bets_odds * amounts)

        return highest_bet_amount < lowest_winning_bet_amount and self.is_bustproof

    def make_url(
        self,
        *,
        all_data: bool = False,
        include_domain: bool = True,
    ) -> str:
        """:class:`str`: Returns an optionally-fully-loaded NeoFoodClub URL to describe these bets.

        Parameters
        ----------
        all_data: :class:`bool`
            Whether or not you want the URL with all pirates, odds, etc. included. Usually, this is not necessary.
            Default = False.
        include_domain: :class:`bool`
            Whether or not you want the output URL to include the preferred neofoodclub website's domain.
            Default = True.
        """
        return self.nfc.make_url(self, all_data=all_data, include_domain=include_domain)

    def get_win_units(self) -> int:
        """Returns the amount of units that won from this bet set."""
        return self.nfc.get_win_units(self)

    def get_win_np(self) -> int:
        """Returns the amount of neopoints won from this bet set.
        If this Bets object has no bet amounts, will return 0.
        """
        return self.nfc.get_win_np(self)

    @property
    def table(self) -> str:
        """:class:`str`: Returns a formatted table of this bet set."""
        headers: list[str] = ["#", *ARENA_NAMES]
        rows: list[list[str]] = []

        for bet_index, bet_row in enumerate(self.indices):
            current_row: list[str] = [str(bet_index + 1)]  # add bet index!
            for key, pirate_index in enumerate(bet_row):
                name: str = ""
                if pirate_index != 0:
                    name: str = self.nfc.get_arena(key).pirates[pirate_index - 1].name
                current_row.append(name)
            rows.append(current_row)
        return utils.Table.render(rows, headers=headers)

    @property
    def stats_table(self) -> str:
        """:class:`str`: Returns a formatted table of this bet set + stats."""
        row_nums = np.arange(len(self)) + 1
        bet_amounts = self.bet_amounts
        odds = self.nfc._data_dict["odds"][self._indices]
        payoffs = odds * bet_amounts
        payoffs[payoffs > 1_000_000] = 1_000_000
        ers = self.nfc._data_dict["ers"][self._indices]
        nes = bet_amounts * ers - bet_amounts
        maxbets = self.nfc._data_dict["maxbets"][self._indices]
        bins = self.nfc._data_dict["bins"][self._indices]

        arena_pirates: list[list[str]] = []
        for bet_row in self.indices:
            current_row: list[str] = []

            for key, pirate_index in enumerate(bet_row):
                name: str = ""
                if pirate_index != 0:
                    name: str = self.nfc.get_arena(key).pirates[pirate_index - 1].name
                current_row.append(name)
            arena_pirates.append(current_row)

        rows: list[Any] = []

        headers: list[str] = []
        footers: list[str] = []

        headers.append("#")
        rows.append(row_nums)
        footers.append("Total:")

        has_bet_amounts = np.all(bet_amounts > -1000)

        if has_bet_amounts:
            headers.append("Bet Amt.")
            rows.append(bet_amounts)
            footers.append(f"{np.sum(bet_amounts):,}")

        headers.append("Odds")
        rows.append(odds)
        footers.append("")

        if has_bet_amounts:
            headers.append("Payoff")
            rows.append(payoffs)
            footers.append("")

        headers.append("ER")
        er_vector = np.vectorize(lambda er: f"{er:.3f}:1")
        rows.append(er_vector(ers))
        footers.append(f"{np.sum(ers):.3f}")

        if has_bet_amounts:
            headers.append("NE")
            ne_vector = np.vectorize(lambda ne: f"{ne:.2f}")
            rows.append(ne_vector(nes))
            footers.append(f"{np.sum(nes):.2f}")

        headers.append("MaxBet")
        rows.append(maxbets.astype(int))
        footers.append("")

        hexer = np.vectorize(hex)
        headers.append("Hex")
        rows.append(hexer(bins.astype(int)))
        footers.append("")

        headers.extend(ARENA_NAMES)
        rows.extend(np.array(arena_pirates).T)
        footers.extend(["", "", "", "", ""])

        return utils.Table.render(np.array(rows).T, headers=headers, footers=footers)  # type: ignore

    def _iterator(self) -> Generator[int, None, None]:
        int_bins = self.nfc._data_dict["bins"]
        yield from int_bins[self._indices]

    def __iter__(self) -> Generator[int, None, None]:
        return self._iterator()

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.bets_hash == other.bets_hash
            and self.amounts_hash == other.amounts_hash
        )
