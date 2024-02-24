from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    import numpy as np
    import numpy.typing as npt

    from neofoodclub.chance import Chance

def pirate_binary(index: int, arena: int) -> int:
    """:class:`int`: Returns the bet-binary representation of a pirate in an arena.

    Parameters
    ----------
    index: :class:`int`
        The index of the pirate in the arena. Can be 0 to 4. If 0, then there is no pirate.
    arena: :class:`int`
        The arena's index. Can be 0 to 4.
    """

def pirates_binary(bets_indices: Sequence[int]) -> int:
    """:class:`int`: Returns the bet-binary representation of bet indices.

    Turns something like (1, 2, 3, 4, 2) for example into 0b10000100001000010100, a bet-binary number.

    This is fundamentally the inverse of binary_to_indices.

    Parameters
    ----------
    bets_indices: Sequence[:class:`int`]
        A sequence of integers from 0 to 4 to represent a bet.
    """

def binary_to_indices(bet_binary: int) -> tuple[int]:
    """Tuple[int, ...]: Returns the bet indices of a bet-binary value.

    Parameters
    ----------
    bet_binary: :class:`int`
        An integer representing a bet.
    """

def bets_hash_to_bet_indices(bets_hash: str) -> list[list[int]]:
    """List[List[:class:`int`]]: Returns a list of lists of bet indices from the provided bets hash.

    Parameters
    ----------
    bets_hash: :class:`str`
        The hash of bet amounts.
    """

def bet_amounts_to_amounts_hash(bet_amounts: Sequence[int]) -> str:
    """:class:`str`: Returns the hash for the provided bet amounts.

    This is fundamentally the inverse of amounts_hash_to_bet_amounts.

    Parameters
    ----------
    bet_amounts: Sequence[int]
        A sequence of bet amount integers.
    """

def bets_hash_value(bets_indices: Sequence[Sequence[int]]) -> str:
    """:class:`str`: Returns a hash for the bets indices provided.

    Parameters
    ----------
    bets_indices: Sequence[Sequence[:class:`int`]]
        A sequence of a sequence of integers from 0 to 4 to represent a bet.
    """

def amounts_hash_to_bet_amounts(amounts_hash: str, /) -> tuple[int | None, ...]:
    """Tuple[Optional[:class:`int`], ...]: Returns a tuple of bet amounts from the provided amounts hash.

    Parameters
    ----------
    amounts_hash: :class:`str`
        The hash of bet amounts.
    """

def make_probabilities(
    opening_odds: Sequence[Sequence[int]],
) -> list[list[float]]: ...
def make_round_dicts(
    stds: Sequence[Sequence[float]], odds: tuple[tuple[int, ...], ...]
) -> tuple[
    npt.NDArray[np.int_],
    npt.NDArray[np.float64],
    npt.NDArray[np.int_],
    npt.NDArray[np.float64],
    npt.NDArray[np.int_],
]: ...
def build_chance_objects(
    bets: Sequence[Sequence[int]],
    bet_odds: Sequence[int],
    probabilities: Sequence[Sequence[float]],
) -> list[Chance]: ...
