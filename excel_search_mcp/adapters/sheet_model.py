"""
Sheet Model - Data structures for Excel sheets
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class CellRange:
    """Cell range representation (1-based, Excel style)."""

    start_row: int
    start_col: int
    end_row: int
    end_col: int

    @property
    def address_a1(self) -> str:
        start = f"{col_to_name(self.start_col)}{self.start_row}"
        end = f"{col_to_name(self.end_col)}{self.end_row}"
        return f"{start}:{end}"


@dataclass
class SheetModel:
    """
    Minimal representation of an Excel sheet:
    - values: 2D array of data (0-based indexing, None allowed)
    - used_range: Actual used range in the sheet (1-based)
    - merged_regions: Merged cell information (optional)
    """

    name: str
    values: List[List[Any]]
    used_range: CellRange
    merged_regions: List[Any] = field(default_factory=list)

    @property
    def n_rows(self) -> int:
        return len(self.values)

    @property
    def n_cols(self) -> int:
        return len(self.values[0]) if self.values else 0

    @property
    def used_range_a1(self) -> str:
        return self.used_range.address_a1


def col_to_name(col_idx: int) -> str:
    """Convert 1-based column index to Excel column name (1 -> A, 27 -> AA)."""
    name = []
    n = col_idx
    while n > 0:
        n, rem = divmod(n - 1, 26)
        name.append(chr(ord("A") + rem))
    return "".join(reversed(name))
