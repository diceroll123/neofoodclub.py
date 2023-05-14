from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from neofoodclub.nfc import NeoFoodClub

__all__ = ("Modifier",)


class Modifier:
    """An object that tells a NeoFoodClub object to behave differently.

    Parameters
    ----------
    flags: :class:`int`
        A bit field of the modifiers you'd like to use.
        For example if you'd like to have a general modifier and an opening modifier, you would
        pass in the two values, bitwise-or'd together like so: Modifier.GENERAL | Modifier.OPENING
    cc_perk: :class:`bool`
        Whether or not you want this modifier to enable up to 15 bets to be made instead of 10. Defaults to False.
    custom_odds: Optional[Dict[int, int]]
        A dictionary containing a pirate ID (1-20) as the key, and desired odds (2-13) as the value. The NeoFoodClub
        object will be recalculated using these odds on top of the current odds.
    custom_time: Optional[datetime.time]
        A timestamp that the NeoFoodClub object will seek to and recalculate using the odds from that time.

    Attributes
    ----------
    GENERAL: :class:`int`
        This flag value means that bets will be generated without bet amount in mind.
        When this value is true, Max TER for example will use actual Expected Ratio instead of Net Expected.
        Net Expected = (bet_amount * expected_ratio - bet_amount).
    OPENING_ODDS: :class:`int`
        This flag value means that bets will be generated with opening odds, as if the current odds are opening odds.
    OPENING: :class:`int`
        This is an alias for OPENING_ODDS.
    REVERSE: :class:`int`
        This flag value flips the algorithms upside-down, essentially giving you the Min TER bets instead of Max TER.
    ALL_MODIFIERS: :class:`int`
        This value is all of the other flag values, bitwise-or'd together. Only use this if you want true chaos.
    """

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
    OPENING = 2
    REVERSE = 4
    ALL_MODIFIERS = GENERAL | OPENING_ODDS | REVERSE
    LETTERS = "GOR"

    def __init__(
        self,
        flags: int = 0,
        *,
        cc_perk: bool = False,
        custom_odds: dict[int, int] | None = None,
        custom_time: datetime.time | None = None,
    ) -> None:
        self.value: int = flags
        self._custom_odds = custom_odds or {}
        self._time = custom_time
        self._cc_perk = cc_perk

        # the _nfc var will only be written to by the NeoFoodClub object.
        self._nfc: NeoFoodClub | None = None

    def __repr__(self) -> str:
        return f"<Modifier value={self.value!r} letters={self.letters!r} time={self.time!r}>"

    def _has_flag(self, o: int) -> bool:
        return (self.value & o) == o

    @property
    def general(self) -> bool:
        """:class:`bool`: Returns whether or not this modifier is set to general."""
        return self._has_flag(self.GENERAL)

    @property
    def opening_odds(self) -> bool:
        """:class:`bool`: Returns whether or not this modifier is set to opening odds."""
        return self._has_flag(self.OPENING_ODDS)

    @property
    def reverse(self) -> bool:
        """:class:`bool`: Returns whether or not this modifier is set to reverse."""
        return self._has_flag(self.REVERSE)

    @property
    def time(self) -> datetime.time | None:
        """Optional[:class:`datetime.time`]: Returns the custom time provided, can be None."""
        return self._time

    @time.setter
    def time(self, val: datetime.time) -> None:
        if not isinstance(val, datetime.time):
            raise TypeError(
                f"Expected datetime.time but received {val.__class__.__name__}"
            )
        self._time = val
        if self._nfc:
            self._nfc.reset()

    @property
    def cc_perk(self) -> bool:
        """:class:`bool`: Returns whether or not this modifier is set to generate 15 bets, for the Charity Corner perk."""
        return self._cc_perk

    @cc_perk.setter
    def cc_perk(self, val: bool) -> None:
        if not isinstance(val, bool):
            raise TypeError(f"Expected bool but received {val.__class__.__name__}")

        self._cc_perk = val

    @property
    def custom_odds(self) -> dict[int, int]:
        """Dict[int, int]: A dictionary containing a pirate ID (1-20) as the key, and
        desired odds (2-13) as the value. The NeoFoodClub object will be recalculated using these odds on
        top of the current odds.
        """
        return self._custom_odds

    @custom_odds.setter
    def custom_odds(self, val: dict[int, int]) -> None:
        if not isinstance(val, dict):
            raise TypeError(
                f"Expected Dict[int, int] but received {val.__class__.__name__}"
            )

        for k, v in val.items():
            if k not in range(1, 21):
                raise ValueError(
                    f"Expected int between 1 and 20 for Pirate ID but received {k}"
                )

            if v not in range(2, 14):
                raise ValueError(
                    f"Expected int between 2 and 13 for Pirate Odds but received {v}"
                )

        self._custom_odds = val
        if self._nfc:
            self._nfc.reset()

    def copy(self) -> Modifier:
        """:class:`Modifier`: Returns a shallow copy of the modifier."""
        return type(self)(
            self.value,
            cc_perk=self._cc_perk,
            custom_odds=self._custom_odds,
            custom_time=self._time,
        )

    @classmethod
    def from_type(cls, letters: str, /, *, cc_perk: bool = False) -> Modifier:
        """:class:`Modifier`: Creates a Modifier using the letters of the modifiers you'd like. For example, passing in
        "ROG" will result in a modifier with General, Opening, and Reverse modifiers set to True.
        These are generally used as a prefix for commands in NeoBot, such as `?rogmer` for example.
        """
        letters = letters.lower()
        value = 0
        for index, letter in enumerate(cls.LETTERS.lower()):
            value |= (1 << index) if letter in letters else 0
        return cls(value, cc_perk=cc_perk)

    @property
    def letters(self) -> str:
        """:class:`str`: Returns the letters that make up this Modifier."""
        return "".join(
            self.LETTERS[bit]
            for bit in range(self.ALL_MODIFIERS.bit_length() + 1)
            if self._has_flag(1 << bit)
        )

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.value == other.value
            and self.opening_odds == other.opening_odds
            and self.custom_odds == other.custom_odds
            and self.time == other.time
            and self.cc_perk == other.cc_perk
        )

    @property
    def nfc(self) -> NeoFoodClub | None:
        """Optional[:class:`NeoFoodClub`:] The NeoFoodClub round that this modifier is connected to. Can be None if not set yet."""
        return self._nfc
