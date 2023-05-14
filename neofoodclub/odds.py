from __future__ import annotations

from typing import TYPE_CHECKING, Generator

from neofoodclub import math

if TYPE_CHECKING:
    from neofoodclub.bets import Bets
    from neofoodclub.chance import Chance

__all__ = (
    "Odds",
)


class Odds:
    """A container class containing the probabilities of a set of bets.
    This class is not to be constructed manually.

    Attributes
    ----------
    best: :class:`Chance`
        The Chance object with the highest odds value.
    bust: Optional[:class:`Chance`]
        The Chance object for busting. Can be None if this bet set is bustproof.
    most_likely_winner: :class:`Chance`
        The Chance object with the highest probability value.
    partial_rate: :class:`float`
        The sum of probabilities where you'd make a partial return.
    """

    __slots__ = (
        "_odds_values",
        "_odds",
        "best",
        "bust",
        "most_likely_winner",
        "partial_rate",
    )

    def __init__(self, bets: Bets) -> None:
        self._odds_values = bets.nfc._data_dict["odds"][bets._indices]
        self._odds = math.build_chance_objects(
            bets.indices, self._odds_values, bets.nfc._stds
        )

        # highest odds
        self.best: Chance = self._odds[-1]

        # bust chance, can be None
        self.bust: Chance | None = self._odds[0] if self._odds[0].value == 0 else None

        self.most_likely_winner: Chance = max(
            self._odds[1 if self.bust else 0 :], key=lambda o: o.probability
        )

        amount_of_bets = max(0, min(len(bets), 15))

        self.partial_rate: float = sum(
            o.probability for o in self._odds if 0 < int(o.value) < amount_of_bets
        )

    def _iterator(self) -> Generator[int, None, None]:
        yield from self._odds_values

    def __iter__(self) -> Generator[int, None, None]:
        return self._iterator()

    def __repr__(self) -> str:
        attrs = [
            ("best", self.best),
            ("bust", self.bust),
            ("most_likely_winner", self.most_likely_winner),
            ("partial_rate", self.partial_rate),
        ]
        joined = " ".join("{}={!r}".format(*t) for t in attrs)
        return f"<Odds {joined}>"
