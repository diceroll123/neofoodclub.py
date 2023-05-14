from __future__ import annotations


class BaseModel:
    __slots__ = ("probabilities",)
    probabilities: tuple[tuple[float]]
