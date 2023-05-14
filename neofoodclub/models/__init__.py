from __future__ import annotations

from typing import TYPE_CHECKING, Union

from neofoodclub.models.base import BaseModel
from neofoodclub.models.multinomial_logit import MultinomialLogitModel
from neofoodclub.models.original import OriginalModel

if TYPE_CHECKING:
    from typing_extensions import TypeAlias


ProbabilityModel: TypeAlias = Union[OriginalModel, MultinomialLogitModel]

__all__ = [
    "BaseModel",
    "OriginalModel",
    "MultinomialLogitModel",
    "ProbabilityModel",
]
