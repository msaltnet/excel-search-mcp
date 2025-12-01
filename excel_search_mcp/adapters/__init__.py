"""
Excel Adapters Package

Provides different implementations for reading Excel files.
"""

from .adapter_base import ExcelAdapter
from .sheet_model import CellRange, SheetModel, col_to_name

__all__ = ["ExcelAdapter", "SheetModel", "CellRange", "col_to_name"]
