from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from datetime import datetime

@dataclass
class OddsChange:
    timestamp: str
    timestamp_utc: datetime
    timestamp_nst: datetime
    old: int
    new: int

    def pirate(self, nfc: NeoFoodClub) -> PartialPirate:
        """:class:`PartialPirate`: The pirate that changed odds."""

    @property
    def pirate_index(self) -> int:
        """:class:`int`: The index of the pirate that changed odds."""

    @property
    def arena_index(self) -> int:
        """:class:`int`: The index of the arena that changed odds."""

    @property
    def arena(self) -> str:
        """:class:`str`: The name of the arena that changed odds."""

    def pirate_id(self, nfc: NeoFoodClub) -> int:
        """:class:`int`: The ID of the pirate that changed odds."""

@dataclass
class Chance:
    """Represents the probabilities of a singular chance of odds.
    This class is not to be constructed manually.

    Attributes
    ----------
    value: :class:`int`
        The actual odds of this instance. For example, if value == 0, this is the Chance object of busting.
    probability: :class:`float`
        The probability that this outcome will occur.
    cumulative: :class:`float`
        The sum of the probabilities per Chance where `value` <= this Chance's `value`.
    tail: :class:`float`
        The difference of the sum of the probabilities per Chance where `value` < this Chance's `value`, from 1.

    """

    value: int
    probability: float
    cumulative: float
    tail: float

class Math:
    BIT_MASKS: tuple[int, ...]
    BET_AMOUNT_MIN: int
    BET_AMOUNT_MAX: int

    @staticmethod
    def pirate_binary(index: int, arena: int) -> int:
        """:class:`int`: Returns the bet-binary representation of a pirate in an arena.

        Parameters
        ----------
        index: :class:`int`
            The index of the pirate in the arena. Can be 0 to 4. If 0, then there is no pirate.
        arena: :class:`int`
            The arena's index. Can be 0 to 4.

        """

    @staticmethod
    def pirates_binary(bets_indices: Sequence[int]) -> int:
        """:class:`int`: Returns the bet-binary representation of bet indices.

        Turns something like (1, 2, 3, 4, 2) for example into 0b10000100001000010100, a bet-binary number.

        This is fundamentally the inverse of binary_to_indices.

        Parameters
        ----------
        bets_indices: Sequence[:class:`int`]
            A sequence of integers from 0 to 4 to represent a bet.

        """

    @staticmethod
    def binary_to_indices(bet_binary: int) -> tuple[int, int, int, int, int]:
        """Tuple[int, int, int, int, int]: Returns the bet indices of a bet-binary value.

        Parameters
        ----------
        bet_binary: :class:`int`
            An integer representing a bet.

        """

    @staticmethod
    def bets_hash_to_bets_count(bets_hash: str, /) -> int:
        """:class:`int`: Returns the amount of bets for a given bets hash.

        Parameters
        ----------
        bets_hash: :class:`str`
            The hash of bet amounts.

        """

    @staticmethod
    def bets_hash_to_bet_binaries(bets_hash: str, /) -> tuple[int, ...]:
        """Tuple[:class:`int`, ...]: Returns the bet-binary representations of the bets hash provided.

        Parameters
        ----------
        bets_hash: :class:`str`
            The hash of bet amounts.

        """

    @staticmethod
    def bets_indices_to_bet_binaries(
        bets_indices: Sequence[Sequence[int]],
        /,
    ) -> tuple[int, ...]:
        """Tuple[:class:`int`, ...]: Returns the bet-binary representations of the bets indices provided.

        Parameters
        ----------
        bets_indices: Sequence[Sequence[:class:`int`]]
            A sequence of a sequence of integers from 0 to 4 to represent a bet.

        """

    @staticmethod
    def bets_hash_to_bet_indices(bets_hash: str) -> list[list[int]]:
        """List[List[:class:`int`]]: Returns a list of lists of bet indices from the provided bets hash.

        Parameters
        ----------
        bets_hash: :class:`str`
            The hash of bet amounts.

        """

    @staticmethod
    def bet_amounts_to_amounts_hash(bet_amounts: Sequence[int]) -> str:
        """:class:`str`: Returns the hash for the provided bet amounts.

        This is fundamentally the inverse of amounts_hash_to_bet_amounts.

        Parameters
        ----------
        bet_amounts: Sequence[int]
            A sequence of bet amount integers.

        """

    @staticmethod
    def bets_hash_value(bets_indices: Sequence[Sequence[int]]) -> str:
        """:class:`str`: Returns a hash for the bets indices provided.

        Parameters
        ----------
        bets_indices: Sequence[Sequence[:class:`int`]]
            A sequence of a sequence of integers from 0 to 4 to represent a bet.

        """

    @staticmethod
    def amounts_hash_to_bet_amounts(amounts_hash: str, /) -> tuple[int | None, ...]:
        """Tuple[Optional[:class:`int`], ...]: Returns a tuple of bet amounts from the provided amounts hash.

        Parameters
        ----------
        amounts_hash: :class:`str`
            The hash of bet amounts.

        """
    @staticmethod
    def build_chance_objects(
        bets: Sequence[Sequence[int]],
        bet_odds: Sequence[int],
        probabilities: Sequence[Sequence[float]],
    ) -> list[Chance]: ...
    @staticmethod
    def expand_ib_object(
        bets: Sequence[Sequence[int]],
        bet_odds: Sequence[int],
    ) -> dict[int, int]: ...

class Modifier:
    EMPTY: int
    GENERAL: int
    OPENING_ODDS: int
    REVERSE: int
    CHARITY_CORNER: int
    ALL_MODIFIERS: int

    def __init__(
        self,
        modifier_value: int = 0,
        custom_odds: dict[int, int] | None = None,
        custom_time: str | None = None,
    ) -> None: ...
    @property
    def value(self) -> int:
        """:class:`int`: The value of the modifier."""

    @property
    def custom_odds(self) -> dict[int, int] | None:
        """Optional[Dict[:class:`int`, :class:`int`]]: The custom odds of the modifier."""

    @property
    def custom_time(self) -> str | None:
        """Optional[:class:`str`]: The custom time of the modifier."""

    @property
    def is_empty(self) -> bool:
        """:class:`bool`: Whether or not the modifier is empty."""

    @property
    def is_general(self) -> bool:
        """:class:`bool`: Whether or not the modifier is general."""

    @property
    def is_opening_odds(self) -> bool:
        """:class:`bool`: Whether or not the modifier is opening odds."""

    @property
    def is_reverse(self) -> bool:
        """:class:`bool`: Whether or not the modifier is reverse."""

    @property
    def is_charity_corner(self) -> bool:
        """:class:`bool`: Whether or not the modifier has the Charity Corner perk on."""

    @property
    def modified(self) -> bool:
        """:class:`bool`: Whether or not the modifier is modifying actual data."""

    def copy(self) -> Modifier: ...
    def __eq__(self, other: object) -> bool: ...

class PartialPirate:
    """Represents a "partial" pirate that only has an ID.

    Attributes
    ----------
    id: :class:`int`
        The pirate's ID.
    name: :class:`str`
        The pirate's name.
    image: :class:`str`
        The pirates image.

    """

    def __init__(self, id: int) -> None: ...
    @property
    def id(self) -> int:
        """:class:`int`: The pirate's ID."""
    @property
    def name(self) -> str:
        """:class:`str`: The pirate's name."""
    @property
    def image(self) -> str:
        """:class:`str`: The pirate's image URL."""

class Pirate:
    """Represents a single pirate."""

    def __init__(
        self,
        id: int,
        arena_id: int,
        index: int,
        current_odds: int,
        opening_odds: int,
        is_winner: bool,
        pfa: int | None,
        nfa: int | None,
        fa: int | None,
    ) -> None: ...
    @property
    def id(self) -> int:
        """:class:`int`: The pirate's ID."""
    @property
    def name(self) -> str:
        """:class:`str`: The pirate's name."""

    @property
    def arena_id(self) -> int:
        """:class:`int`: The index of the arena this pirate is in."""

    @property
    def is_winner(self) -> bool:
        """:class:`bool`: Whether or not the pirate is a winner."""

    @property
    def image(self) -> str:
        """:class:`str`: The pirate's image URL."""
    @property
    def index(self) -> int:
        """:class:`int`: The pirate's index in the arena the pirate is in. One-based."""
    @property
    def std(self) -> float | None:
        """Optional[:class:`float`]: The pirate's std probability. If this is None, the NeoFoodClub object has not been cached yet."""
    @property
    def current_odds(self) -> int:
        """:class:`int`: The pirate's current odds."""
    @property
    def er(self) -> float | None:
        """Optional[:class:`float`]: The pirate's expected ratio. This is equal to std * odds. If this is None, the NeoFoodClub object has not been cached yet."""
    @property
    def fa(self) -> int | None:
        """Optional[:class:`int`]: The pirate's food adjustment. Can be None if no foods are found."""
    @property
    def nfa(self) -> int | None:
        """Optional[:class:`int`]: The pirate's negative food adjustment. Can be None if no foods are found."""
    @property
    def pfa(self) -> int | None:
        """Optional[:class:`int`]: The pirate's positive food adjustment. Can be None if no foods are found."""
    @property
    def opening_odds(self) -> int:
        """:class:`int`: The pirate's opening odds."""
    @property
    def binary(self) -> int:
        """:class:`int`: The pirate's bet-binary representation."""

    def positive_foods(self, nfc: NeoFoodClub) -> tuple[int, ...] | None:
        """Tuple[:class:`int`, ...]: The IDs of the positive foods for this pirate."""

    def negative_foods(self, nfc: NeoFoodClub) -> tuple[int, ...] | None:
        """Tuple[:class:`int`, ...]: The IDs of the negative foods for this pirate."""

    def __int__(self) -> int:
        """Returns the pirate's binary representation."""

    def __eq__(self, other: object) -> bool: ...

class Odds:
    @property
    def best(self) -> Chance:
        """:class:`Chance`: The best odds."""

    @property
    def bust(self) -> Chance | None:
        """Optional[:class:`Chance`]: The bust odds."""

    @property
    def most_likely_winner(self) -> Chance:
        """:class:`Chance`: The most likely winner."""

    @property
    def partial_rate(self) -> float:
        """:class:`float`: The partial rate."""

    @property
    def chances(self) -> list[Chance]:
        """List[:class:`Chance`]: The chances of the odds."""

class Bets:
    @property
    def bet_amounts(self) -> tuple[int | None, ...] | None:
        """Optional[Tuple[Optional[:class:`int`], ...]]: The amounts of the bets."""

    def remove_amounts(self) -> None:
        """Removes the bet amounts from the bets."""

    def set_amounts_with_hash(self, amounts_hash: str) -> None:
        """Sets the bet amounts with a hash.

        Parameters
        ----------
        amounts_hash: :class:`str`
            The hash of the bet amounts.

        """

    def set_amounts_with_int(self, amount: int) -> None:
        """Sets the bet amounts with an integer.

        Parameters
        ----------
        amount: :class:`int`
            The bet amount.

        """

    def set_amounts_with_list(self, amounts: Sequence[int]) -> None:
        """Sets the bet amounts with a sequence of integers.

        Parameters
        ----------
        amounts: Sequence[:class:`int`]
            The bet amounts.

        """

    @property
    def odds(self) -> Odds:
        """:class:`Odds`: The odds of the bets."""

    def __len__(self) -> int: ...
    @property
    def binaries(self) -> tuple[int, ...]:
        """Tuple[:class:`int`, ...]: The bet-binary representations of the bets."""

    @property
    def bets_hash(self) -> str:
        """:class:`str`: The hash of the bet amounts."""

    @property
    def amounts_hash(self) -> str | None:
        """Optional[:class:`str`]: The hash of the bet amounts, if applicable."""

    @property
    def is_bustproof(self) -> bool:
        """:class:`bool`: Whether or not the bets are bustproof."""

    @property
    def is_crazy(self) -> bool:
        """:class:`bool`: Whether or not the bets are crazy."""

    @property
    def is_gambit(self) -> bool:
        """:class:`bool`: Whether or not the bets are gambit."""

    @property
    def is_tenbet(self) -> bool:
        """:class:`bool`: Whether or not the bets are a tenbet."""

    def is_guaranteed_win(self, nfc: NeoFoodClub) -> bool:
        """:class:`bool`: Whether or not the bets are guaranteed to win."""

    def odds_values(self, nfc: NeoFoodClub) -> tuple[int, ...]:
        """Tuple[:class:`int`, ...]: The odds of the bets."""

    @property
    def indices(self) -> tuple[tuple[int, ...], ...]:
        """Tuple[Tuple[:class:`int`, ...], ...]: The indices of the bets."""

    def net_expected(self, nfc: NeoFoodClub) -> float:
        """:class:`float`: Returns the net expected value of the bets."""

    def expected_return(self, nfc: NeoFoodClub) -> float:
        """:class:`float`: Returns the expected return of the bets."""

    def fill_bet_amounts(self, nfc: NeoFoodClub) -> None:
        """Fills the bet amounts of the bets such that they are either capped to what
        would equal 1M per bet,or the max bet amount, using `nfc.bet_amount`.
        """

    def make_url(
        self,
        nfc: NeoFoodClub,
        *,
        include_domain: bool = True,
        all_data: bool = False,
    ) -> str:
        """Returns a URL for the bets.

        Parameters
        ----------
        nfc: :class:`NeoFoodClub`
            The NeoFoodClub object to use.
        include_domain: :class:`bool`
            Whether or not to include the domain in the URL.
        all_data: :class:`bool`
            Whether or not to include all data in the URL.

        """

class Arena:
    @property
    def id(self) -> int:
        """:class:`int`: The arena's ID."""

    @property
    def odds(self) -> float:
        """:class:`float`: The arena's odds."""

    @property
    def foods(self) -> tuple[int, ...] | None:
        """Optional[Tuple[:class:`int`, ...]]: The foods for this arena, if applicable."""

    @property
    def winner_index(self) -> int:
        """:class:`int`: The winning pirate's index, if applicable."""

    @property
    def winner_pirate(self) -> Pirate | None:
        """Optional[:class:`Pirate`]: The winning pirate, if applicable."""

    @property
    def pirates(self) -> tuple[Pirate, ...]:
        """Tuple[:class:`Pirate`, ...]: The pirates in the arena."""

    @property
    def name(self) -> str:
        """:class:`str`: The arena's name."""

    @property
    def is_positive(self) -> bool:
        """:class:`bool`: Whether or not the arena is positive."""

    @property
    def pirate_ids(self) -> tuple[int, int, int, int]:
        """Tuple[:class:`int`, ...]: The pirate IDs in the arena."""

    @property
    def ratio(self) -> float:
        """:class:`float`: The arena's ratio."""

    @property
    def is_negative(self) -> bool:
        """:class:`bool`: Whether or not the arena is negative."""

    @property
    def best(self) -> tuple[Pirate, Pirate, Pirate, Pirate]:
        """Tuple[:class:`Pirate`, ...]: The best pirates in the arena."""

    def __getitem__(self, key: int) -> Pirate:
        """Returns a pirate by index.

        Parameters
        ----------
        key: :class:`int`
            The index of the pirate to get.

        """

class Arenas:
    def get_pirate_by_id(self, id: int) -> Pirate | None:
        """Optional[:class:`Pirate`]: Returns a pirate by ID, if it exists.

        Parameters
        ----------
        id: :class:`int`
            The ID of the pirate.

        """

    def get_pirates_by_id(self, ids: Sequence[int]) -> tuple[Pirate, ...]:
        """Tuple[:class:`Pirate`, ...]: Returns a tuple of pirates by ID.

        Parameters
        ----------
        ids: Sequence[:class:`int`]
            The IDs of the pirates.

        """

    def get_all_pirates_flat(self) -> tuple[Pirate, ...]:
        """Tuple[:class:`Pirate`, ...]: Returns a tuple of all pirates in all arenas."""

    def get_pirates_from_binary(self, binary: int) -> tuple[Pirate, ...]:
        """Tuple[:class:`Pirate`, ...]: Returns a tuple of pirates from a binary.

        Parameters
        ----------
        binary: :class:`int`
            The binary to get the pirates from.

        """

    def get_all_pirates(self) -> tuple[tuple[Pirate, Pirate, Pirate, Pirate], ...]:
        """Tuple[Tuple[:class:`Pirate`, ...], ...]: Returns a tuple of tuples of pirates in each arena."""

    @property
    def best(self) -> tuple[Arena, Arena, Arena, Arena, Arena]:
        """Tuple[:class:`Arena`, ...]: Returns the best arenas sorted by best odds."""

    @property
    def pirate_ids(self) -> tuple[tuple[int, int, int, int, int], ...]:
        """Tuple[Tuple[:class:`int`, ...], ...]: Returns the pirate IDs in each arena."""

    @property
    def positives(self) -> tuple[Arena, ...]:
        """Tuple[:class:`Arena`, ...]: Returns the positive arenas."""

    def get_arena(self, index: int) -> Arena:
        """Returns an arena by index.

        Parameters
        ----------
        index: :class:`int`
            The index of the arena to get.

        """

    def __getitem__(self, key: int) -> Arena:
        """Returns an arena by index.

        Parameters
        ----------
        key: :class:`int`
            The index of the arena to get.

        """

    def __iter__(self) -> Iterator[Arena]:
        """Iterator[:class:`Arena`]: Returns an iterator of the arenas."""

    def __next__(self) -> Arena:
        """Returns the next arena in the iterator."""

    def __len__(self) -> int:
        """:class:`int`: Returns the amount of arenas. Should be 5."""

    @property
    def arenas(self) -> tuple[Arena, Arena, Arena, Arena, Arena]:
        """Tuple[:class:`Arena`, ...]: Returns the arenas."""

class NeoFoodClub:
    """Represents a Food Club round.
    This class is the basis of this library.
    """

    # fmt: off
    def __init__(
        self,
        json_string: str,
        *,
        bet_amount: int | None = None,
        probability_model: int | None = None,
        modifier: Modifier | None = None,
    ) -> None: ...

    @classmethod
    def from_json(
        cls,
        json_string: str,
        *,
        bet_amount: int | None = None,
        probability_model: int | None = None,
        modifier: Modifier | None = None,
    ) -> NeoFoodClub: ...

    @classmethod
    def from_url(
        cls,
        url: str,
        *,
        bet_amount: int | None = None,
        probability_model: int | None = None,
        modifier: Modifier | None = None,
    ) -> NeoFoodClub: ...

    # fmt: on

    @classmethod
    def copy(
        cls,
        *,
        probability_model: int | None = None,
        modifier: Modifier | None = None,
    ) -> NeoFoodClub:
        """Returns a copy of the NeoFoodClub object with an optional modifier.

        Parameters
        ----------
        probability_model: Optional[:class:`int`]
            The probability model to use.
        modifier: Optional[:class:`Modifier`]
            The modifier to use.

        """

    @property
    def bet_amount(self) -> int | None:
        """Optional[:class:`int`]: The amount of NP to make bets with."""

    @bet_amount.setter
    def bet_amount(self, value: int | None) -> None:
        """Optional[:class:`int`]: The amount of NP to make bets with."""

    @property
    def winners(self) -> tuple[int, int, int, int, int]:
        """Tuple[:class:`int`]: Returns the winning pirates, if applicable.
        A tuple of 5 zeroes if not applicable.
        """

    @property
    def winners_binary(self) -> int:
        """:class:`int`: Returns a bet-binary representation of the winning pirates."""

    @property
    def is_over(self) -> bool:
        """:class:`bool`: Returns whether or not the round is over based on having any winning pirates."""

    @property
    def round(self) -> int:
        """:class:`int`: The round's number."""

    @property
    def start(self) -> str | None:
        """Optional[:class:`str`]: When the round started in UTC, if applicable."""

    @property
    def start_nst(self) -> datetime | None:
        """Optional[:class:`datetime.datetime`]: When the round started in NST, as an aware datetime object if applicable."""

    @property
    def current_odds(
        self,
    ) -> tuple[
        tuple[int, int, int, int],
        tuple[int, int, int, int],
        tuple[int, int, int, int],
        tuple[int, int, int, int],
        tuple[int, int, int, int],
    ]:
        """Tuple[:class:`int`, ...]: Returns the current odds of the pirates."""

    @property
    def opening_odds(
        self,
    ) -> tuple[
        tuple[int, int, int, int],
        tuple[int, int, int, int],
        tuple[int, int, int, int],
        tuple[int, int, int, int],
        tuple[int, int, int, int],
    ]:
        """Tuple[:class:`int`, ...]: Returns the opening odds of the pirates."""

    @property
    def timestamp(self) -> datetime | None:
        """Optional[:class:`datetime.datetime`]: The timestamp of the round, if applicable."""

    @property
    def foods(self) -> tuple[tuple[int, ...], ...] | None:
        """Optional[Tuple[Tuple[:class:`int`, ...], ...]]: The foods for each arena, if applicable."""

    @property
    def max_amount_of_bets(self) -> int:
        """:class:`int`: The maximum amount of bets you can make. Generally, this is `10`."""

    def max_ters(self) -> tuple[int, ...]:
        """Tuple[:class:`int`, ...]: Returns the max ter values with the given modifiers applied beforehand."""

    @property
    def winning_pirates(self) -> tuple[Pirate, Pirate, Pirate, Pirate, Pirate] | None:
        """Optional[Tuple[:class:`Pirate`, :class:`Pirate`, :class:`Pirate`, :class:`Pirate`, :class:`Pirate`]]: The winning pirates, if applicable."""

    def make_random_bets(self) -> Bets:
        """:class:`Bets`: Returns a random bet object."""

    def make_max_ter_bets(self) -> Bets:
        """:class:`Bets`: Returns a maxter bet object."""

    def make_units_bets(self, units: int) -> Bets | None:
        """Optional[:class:`Bets`]: Returns a bet object with the given amount of units.

        If you provide too high of units, this will return None.
        """

    def make_gambit_bets(self, pirates_binary: int) -> Bets:
        """:class:`Bets`: Returns a gambit bet object."""

    def make_best_gambit_bets(self) -> Bets:
        """:class:`Bets`: Returns the best gambit bet object, based on max ter."""

    def make_winning_gambit_bets(self) -> Bets:
        """:class:`Bets`: Returns the winning gambit bet object."""

    def make_random_gambit_bets(self) -> Bets:
        """:class:`Bets`: Returns a random gambit bet object."""

    def make_tenbet_bets(self, pirate_binary: int) -> Bets:
        """:class:`Bets`: Returns a tenbet bet object."""

    def make_crazy_bets(self) -> Bets:
        """:class:`Bets`: Returns a crazy bet object."""

    def make_bustproof_bets(self) -> Bets | None:
        """Optional[:class:`Bets`]: Returns a bustproof bet object, if applicable."""

    def make_bets_from_hash(self, bets_hash: str) -> Bets:
        """:class:`Bets`: Returns a bet object from a bets hash."""

    def make_bets_from_binaries(self, bets_binaries: Sequence[int]) -> Bets:
        """:class:`Bets`: Returns a bet object from a sequence of bet binaries."""

    def make_bets_from_indices(self, bets_indices: Sequence[Sequence[int]]) -> Bets:
        """:class:`Bets`: Returns a bet object from a sequence of bet indices."""

    def make_bets_from_array_indices(self, array_indices: Sequence[int]) -> Bets:
        """:class:`Bets`: Returns a bet object from a sequence of RoundData array indices."""

    def get_win_units(self, bets: Bets) -> int:
        """:class:`int`: Returns the amount of units won from the provided bets."""

    def get_win_np(self, bets: Bets) -> int:
        """:class:`int`: Returns the amount of neopoints won from the provided bets."""

    @property
    def arenas(self) -> Arenas:
        """:class:`Arenas`: Returns the arenas object."""

    def get_arena(self, index: int) -> Arena:
        """Returns an arena by index.

        Parameters
        ----------
        index: :class:`int`
            The index of the arena to get.

        """

    @property
    def modifier(self) -> Modifier:
        """:class:`Modifier`: Returns the modifier object."""

    def make_url(
        self,
        *,
        bets: Bets | None = None,
        include_domain: bool = True,
        all_data: bool = False,
    ) -> str:
        """Returns a URL to the round.

        If bets is provided, it will include the bets in the URL. If bet amounts
        are provided, it will include the bet amounts in the URL.

        Parameters
        ----------
        bets: Optional[:class:`Bets`]
            The bets to make a URL for, if any.
        include_domain: :class:`bool`
            Whether or not to include the domain in the URL.
        all_data: :class:`bool`
            Whether or not to include all data in the URL.

        """

    @property
    def changes(self) -> tuple[OddsChange, ...]:
        """Tuple[:class:`OddsChange`, ...]: Returns the changes in the round."""

    @property
    def custom_odds(self) -> dict[int, int] | None:
        """Optional[Dict[:class:`int`, :class:`int`]]: The custom odds of the modifier."""

    @property
    def pirates(self) -> list[list[int]]:
        """List[List[:class:`int`]]: Returns the pirates in the round."""

    @property
    def modified(self) -> bool:
        """:class:`bool`: Whether or not the round data is modified."""

    @property
    def is_outdated_lock(self) -> bool:
        """:class:`bool`: Returns whether or not this round is to be considered over. 24 hours after the start time."""

    def to_json(self) -> str:
        """:class:`str`: Returns the JSON representation of the NeoFoodClub object."""

    def with_modifier(self, modifier: Modifier) -> None:
        """Modifies the NeoFoodClub object in-place with the provided modifier.

        Parameters
        ----------
        modifier: :class:`Modifier`
            The modifier to use.

        """
