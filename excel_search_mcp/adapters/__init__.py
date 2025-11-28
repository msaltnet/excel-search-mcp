"""
Excel Adapters Package

Provides different implementations for reading Excel files.
"""

from .adapter_base import ExcelAdapter
from .sheet_model import SheetModel, CellRange

__all__ = ["ExcelAdapter", "SheetModel", "CellRange"]
