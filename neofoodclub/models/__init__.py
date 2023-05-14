from __future__ import annotations

from typing import TYPE_CHECKING

from neofoodclub.models.base import BaseModel
from neofoodclub.models.original import OriginalModel

if TYPE_CHECKING:
    from typing_extensions import TypeAlias


ProbabilityModel: TypeAlias = OriginalModel

__all__ = [
    "BaseModel",
    "OriginalModel",
    "ProbabilityModel",
]
