"""
Excel Adapter Base - Common interface for Excel adapters
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from .sheet_model import SheetModel


class ExcelAdapter(Protocol):
    """
    Common interface for Excel file access.

    Implementations:
      - OpenpyxlAdapter: For regular Excel files (development/testing)
      - Win32Adapter: For DRM-protected Excel files (production, Windows only)

    Design principles:
      - Path-based API (no COM object exposure)
      - Returns pure data (SheetModel, list, etc.)
      - Each adapter handles its own constraints internally
    """

    def list_sheets_from_file(self, file_path: str | Path) -> list[str]:
        """
        List all sheet names from an Excel file.

        Args:
            file_path: Path to Excel file

        Returns:
            List of sheet names

        Note:
            Opens and closes the file internally. No external state.
        """
        ...

    def get_sheet_model_from_file(
        self, file_path: str | Path, sheet_name: str
    ) -> SheetModel:
        """
        Extract a specific sheet as SheetModel from an Excel file.

        Args:
            file_path: Path to Excel file
            sheet_name: Name of the sheet to extract

        Returns:
            SheetModel (values, used_range, merged_regions)

        Note:
            Opens and closes the file internally. No external state.
        """
        ...

    def shutdown(self) -> None:
        """Clean up resources (if any)."""
        ...
