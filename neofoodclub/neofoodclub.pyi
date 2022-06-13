from typing import Dict, List, Sequence, Tuple


def binary_to_indices_rust(bet_binary: int) -> Tuple[int, ...]: ...

def make_probabilities_rust(opening_odds: Sequence[Sequence[int]]) -> List[List[float]]: ...

def ib_prob_rust(ib: int, probabilities: Sequence[Sequence[float]]) -> float: ...

def expand_ib_object_rust(bets: Sequence[Sequence[int]], bet_odds: Sequence[int]) -> Dict[int, int]: ...