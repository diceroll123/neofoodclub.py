from dataclasses import dataclass


@dataclass
class Chance:
    """Represents the probabilities of a singular chance of odds.
    This serves as a type hint for the Chance struct in our Rust code.
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
