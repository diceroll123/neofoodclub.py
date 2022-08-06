from __future__ import annotations

from typing import Sequence

import numpy as np

from . import math

__all__ = (
    "fix_bet_amounts",
    "Table",
)


class Table:
    @staticmethod
    def render(
        rows: Sequence[Sequence[str]],
        /,
        headers: Sequence[str] | None = None,
        footers: Sequence[str] | None = None,
    ) -> str:
        """Renders the table as a string.

        headers = ["#", "Shipwreck", "Lagoon", "Treasure", "Hidden", "Harpoon"]
        rows = [
            ["1", "", "", "", "", "Federismo"],
            ["2", "", "", "", "", "Franchisco"],
            ["3", "", "", "", "", "Blackbeard"],
            ["4", "", "", "", "", "Stuff"],
        ]

        print(Table(rows, headers=headers))

        Would look like this:
        +---+-----------+--------+----------+--------+------------+
        | # | Shipwreck | Lagoon | Treasure | Hidden |  Harpoon   |
        +---+-----------+--------+----------+--------+------------+
        | 1 |           |        |          |        | Federismo  |
        | 2 |           |        |          |        | Franchisco |
        | 3 |           |        |          |        | Blackbeard |
        | 4 |           |        |          |        |   Stuff    |
        +---+-----------+--------+----------+--------+------------+
        """

        _headers: list[str] = list(headers) if headers is not None else []
        _rows: list[list[str]] = [list(row) for row in rows]
        _footers: list[str] = list(footers) if footers is not None else []

        lists: list[list[str]] = []
        if _headers:
            lists.append(_headers)
        lists.extend(_rows)
        if _footers:
            lists.append(_footers)

        sizes = np.char.str_len(np.array([lists])) + 2
        widths = sizes[0].max(axis=0)

        def make_line(row: Sequence[str]) -> str:
            return "|" + "|".join(f"{v:^{widths[k]}}" for k, v in enumerate(row)) + "|"

        line = "+" + "+".join(["-" * w for w in widths]) + "+"

        lines: list[str] = [line]
        if _headers:
            # add the headers, and a separator line
            lines.append(make_line(_headers))
            lines.append(line)

        for row in _rows:
            lines.append(make_line(row))

        if _footers:
            lines.append(line)
            lines.append(make_line(_footers))

        lines.append(line)
        return "\n".join(lines)


def fix_bet_amounts(amts: np.ndarray) -> np.ndarray:
    """:class:`np.ndarray`: Returns a "clamped" array of the bet amounts passed in where the minimum value is 50 and
    the maximum value is 70304, which is the highest value that the current hashing algorithm can understand."""
    # fix any values below 50 to be 50, to maintain working bets
    # floor any values above max bet amount
    return np.clip(amts, math.BET_AMOUNT_MIN, math.BET_AMOUNT_MAX)
