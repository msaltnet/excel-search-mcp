"""
Win32 COM Excel Adapter

For production environments and DRM-protected Excel files.
Windows-only, requires Excel application installed.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .adapter_base import ExcelAdapter
from .sheet_model import CellRange, SheetModel

logger = logging.getLogger(__name__)


class Win32Adapter(ExcelAdapter):
    """
    Excel adapter using win32com (COM).

    Pros:
    - Can read DRM-protected Excel files
    - Uses native Excel engine (100% compatibility)
    - Handles complex formulas correctly

    Cons:
    - Windows-only
    - Requires Excel installation
    - Slower than openpyxl
    - Cannot run in parallel (COM threading issues)

    Note:
    - merged_regions field is not yet implemented (returns empty list)
    """

    def __init__(self) -> None:
        """Initialize Win32 adapter."""
        import pythoncom
        import win32com.client

        # Initialize COM
        try:
            pythoncom.CoInitialize()
        except Exception:
            pass

        logger.info("Creating Excel Application via COM")
        self.app = win32com.client.DispatchEx("Excel.Application")
        self.app.Visible = False
        self.app.DisplayAlerts = False
        self.app.ScreenUpdating = False
        self.app.EnableEvents = False

        try:
            self.app.IgnoreRemoteRequests = True
        except Exception:
            pass

        logger.info("Excel Application created successfully")

    def list_sheets_from_file(self, file_path: str | Path) -> list[str]:
        """List all sheet names from Excel file."""
        abs_path = Path(file_path).resolve()

        if not abs_path.exists():
            raise FileNotFoundError(f"Excel file not found: {abs_path}")

        wb = self.app.Workbooks.Open(
            str(abs_path),
            UpdateLinks=0,
            ReadOnly=True,
            IgnoreReadOnlyRecommended=True,
            Notify=False,
        )

        try:
            sheets = [ws.Name for ws in wb.Worksheets]
            logger.debug(f"Found {len(sheets)} sheets in {abs_path.name}")
            return sheets
        finally:
            wb.Close(SaveChanges=False)
            self._restore_settings()

    def get_sheet_model_from_file(
        self, file_path: str | Path, sheet_name: str
    ) -> SheetModel:
        """Extract SheetModel from Excel file."""
        abs_path = Path(file_path).resolve()

        if not abs_path.exists():
            raise FileNotFoundError(f"Excel file not found: {abs_path}")

        wb = self.app.Workbooks.Open(
            str(abs_path),
            UpdateLinks=0,
            ReadOnly=True,
            IgnoreReadOnlyRecommended=True,
            Notify=False,
        )

        try:
            logger.debug(f"Extracting sheet '{sheet_name}' from {abs_path.name}")
            return self._extract_sheet_model(wb, sheet_name)
        finally:
            wb.Close(SaveChanges=False)
            self._restore_settings()

    def _extract_sheet_model(self, workbook: Any, sheet_name: str) -> SheetModel:
        """Extract SheetModel from an open workbook."""
        from win32com.client import constants

        ws = workbook.Worksheets(sheet_name)

        # Get UsedRange
        used = ws.UsedRange
        top_row = used.Row
        left_col = used.Column
        used_col_count = used.Columns.Count

        # Find actual last row with data
        max_row = 0
        total_rows = ws.Rows.Count

        for rel_col in range(1, used_col_count + 1):
            col = left_col + rel_col - 1
            last = ws.Cells(total_rows, col).End(constants.xlUp).Row

            if ws.Cells(last, col).Value is None:
                continue

            if last > max_row:
                max_row = last

        # Handle empty sheet
        if max_row == 0:
            used_range = CellRange(
                start_row=top_row,
                start_col=left_col,
                end_row=top_row,
                end_col=left_col,
            )
            return SheetModel(
                name=sheet_name,
                values=[],
                used_range=used_range,
                merged_regions=[],
            )

        # Read data range
        last_col = left_col + used_col_count - 1
        data_range = ws.Range(
            ws.Cells(top_row, left_col),
            ws.Cells(max_row, last_col),
        )
        raw_values = data_range.Value

        row_count = max_row - top_row + 1
        col_count = used_col_count

        values_2d = self._normalize_values(raw_values, row_count, col_count)

        used_range = CellRange(
            start_row=top_row,
            start_col=left_col,
            end_row=max_row,
            end_col=last_col,
        )

        merged_regions: list[Any] = []

        return SheetModel(
            name=sheet_name,
            values=values_2d,
            used_range=used_range,
            merged_regions=merged_regions,
        )

    @staticmethod
    def _normalize_win32_value(value: Any) -> Any:
        """
        Normalize Win32COM cell values to standard Python types.

        Converts pywintypes.TimeType to naive datetime.
        """
        try:
            import pywintypes  # type: ignore

            if isinstance(value, pywintypes.TimeType):
                from datetime import datetime

                return datetime(
                    value.year,
                    value.month,
                    value.day,
                    value.hour,
                    value.minute,
                    value.second,
                    value.microsecond,
                )
        except (ImportError, AttributeError):
            pass

        return value

    @staticmethod
    def _normalize_values(raw: Any, rows: int, cols: int) -> list[list[Any]]:
        """
        Normalize COM Value to 2D list.

        COM returns different formats:
        - 1x1: scalar
        - 1xN: tuple
        - Nx1: tuple
        - NxM: tuple of tuples
        """
        if rows == 0 or cols == 0:
            return []

        # 1x1
        if rows == 1 and cols == 1:
            return [[Win32Adapter._normalize_win32_value(raw)]]

        # 1xN (single row)
        if rows == 1:
            return [[Win32Adapter._normalize_win32_value(v) for v in raw]]

        # Nx1 (single column)
        if cols == 1:
            return [[Win32Adapter._normalize_win32_value(v)] for v in raw]

        # NxM (general case)
        return [[Win32Adapter._normalize_win32_value(v) for v in row] for row in raw]

    def _restore_settings(self) -> None:
        """
        Restore Excel Application settings to defaults.

        CRITICAL: IgnoreRemoteRequests must be reset to False!
        """
        try:
            self.app.IgnoreRemoteRequests = False
            self.app.ScreenUpdating = True
            self.app.EnableEvents = True
            self.app.DisplayAlerts = True
        except Exception as e:
            logger.debug(f"Failed to restore Excel settings: {e}")

    def shutdown(self) -> None:
        """Shutdown Excel Application and clean up resources."""
        if self.app is None:
            return

        try:
            # Close all workbooks
            try:
                while self.app.Workbooks.Count > 0:
                    self.app.Workbooks(1).Close(SaveChanges=False)
            except Exception as e:
                logger.debug(f"Failed to close workbooks: {e}")

            # Restore settings
            self._restore_settings()

            # Quit Excel
            self.app.Quit()
            logger.info("Excel Application shut down successfully")

        finally:
            self.app = None

            # Garbage collection
            import gc

            gc.collect()
