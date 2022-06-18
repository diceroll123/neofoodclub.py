from typing import Dict, List, Sequence, Tuple


def pirate_binary_rust(index: int, arena: int) -> int:
    """:class:`int`: Returns the bet-binary representation of a pirate in an arena.

    Parameters
    -----------
    index: :class:`int`
        The index of the pirate in the arena. Can be 0 to 4. If 0, then there is no pirate.
    arena: :class:`int`
        The arena's index. Can be 0 to 4.
    """
    ...

def pirates_binary_rust(bets_indices: Sequence[int]) -> int:
    """:class:`int`: Returns the bet-binary representation of bet indices.

    Turns something like (1, 2, 3, 4, 2) for example into 0b10000100001000010100, a bet-binary number.

    This is fundamentally the inverse of binary_to_indices.

    Parameters
    -----------
    bets_indices: Sequence[:class:`int`]
        A sequence of integers from 0 to 4 to represent a bet.
    """
    ...

def binary_to_indices_rust(bet_binary: int) -> Tuple[int, ...]:
    """Tuple[int, ...]: Returns the bet indices of a bet-binary value.
    Parameters
    -----------
    bet_binary: :class:`int`
        An integer representing a bet.
    """
    ...

def bets_hash_to_bet_indices_rust(bets_hash: str) -> List[List[int]]:
    """List[List[:class:`int`]]: Returns a list of lists of bet indices from the provided bets hash.

    Parameters
    -----------
    bets_hash: :class:`str`
        The hash of bet amounts.
    """
    ...

def bet_amounts_to_amounts_hash_rust(bet_amounts: Dict[int, int]) -> str:
    """:class:`str`: Returns the hash for the provided bet amounts.

    This is fundamentally the inverse of amounts_hash_to_bet_amounts.

    Parameters
    -----------
    bet_amounts: Dict[int, int]
        A dict of bet amounts where the key is the index and the value is the bet amount.
    """
    ...

def make_probabilities_rust(opening_odds: Sequence[Sequence[int]]) -> List[List[float]]: ...

def ib_prob_rust(ib: int, probabilities: Sequence[Sequence[float]]) -> float: ...

def expand_ib_object_rust(bets: Sequence[Sequence[int]], bet_odds: Sequence[int]) -> Dict[int, int]: ...

def make_round_dicts_rust(stds: Tuple[Tuple[float, ...], ...], odds: Tuple[Tuple[int, ...], ...]): ...
