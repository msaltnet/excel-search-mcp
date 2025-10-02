"""
Simple Functionality Tests

Simple tests for actually implemented functionality.
"""

import pytest
from pathlib import Path
import tempfile
import os

from src.file_scanner import FileScanner, list_excel_files
from src.excel_processor import ExcelProcessor, get_excel_summary
from src.data_formatter import DataFormatter


class TestFileScanner:
    """File scanner tests"""

    def test_file_scanner_initialization(self):
        """Test FileScanner initialization"""
        scanner = FileScanner()
        assert scanner.supported_extensions == {".xlsx", ".xls", ".xlsm", ".xlsb"}

    def test_is_excel_file(self):
        """Test Excel file extension check"""
        scanner = FileScanner()

        # Excel files
        assert scanner.is_excel_file(Path("test.xlsx")) is True
        assert scanner.is_excel_file(Path("test.xls")) is True
        assert scanner.is_excel_file(Path("test.xlsm")) is True
        assert scanner.is_excel_file(Path("test.xlsb")) is True

        # Non-Excel files
        assert scanner.is_excel_file(Path("test.txt")) is False
        assert scanner.is_excel_file(Path("test.pdf")) is False
        assert scanner.is_excel_file(Path("test.docx")) is False

    def test_scan_nonexistent_directory(self):
        """Test scanning non-existent directory"""
        result = list_excel_files("/nonexistent/directory")

        assert result["success"] is False
        assert "error" in result
        assert "does not exist" in result["error"]

    def test_scan_file_instead_of_directory(self):
        """Test scanning file as directory"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            result = list_excel_files(tmp_path)

            assert result["success"] is False
            assert "error" in result
            assert "not a directory" in result["error"]
        finally:
            os.unlink(tmp_path)


class TestExcelProcessor:
    """Excel processor tests"""

    def test_excel_processor_initialization(self):
        """Test ExcelProcessor initialization"""
        processor = ExcelProcessor()
        assert processor.supported_formats == [".xlsx", ".xls", ".xlsm", ".xlsb"]

    def test_is_supported_file(self):
        """Test supported file format check"""
        processor = ExcelProcessor()

        # Supported formats
        assert processor.is_supported_file(Path("test.xlsx")) is True
        assert processor.is_supported_file(Path("test.xls")) is True
        assert processor.is_supported_file(Path("test.xlsm")) is True
        assert processor.is_supported_file(Path("test.xlsb")) is True

        # Unsupported formats
        assert processor.is_supported_file(Path("test.txt")) is False
        assert processor.is_supported_file(Path("test.pdf")) is False

    def test_get_file_info_nonexistent_file(self):
        """Test getting information for non-existent file"""
        result = get_excel_summary("/nonexistent/file.xlsx")

        assert result["success"] is False
        assert "error" in result


class TestDataFormatter:
    """Data formatter tests"""

    def test_data_formatter_initialization(self):
        """Test DataFormatter initialization"""
        formatter = DataFormatter()
        assert len(formatter.date_formats) > 0

    def test_format_value(self):
        """Test value formatting"""
        formatter = DataFormatter()

        # None value
        assert formatter.format_value(None) is None

        # String value
        assert formatter.format_value("test") == "test"

        # Numeric values
        assert formatter.format_value(123) == 123
        assert formatter.format_value(123.45) == 123.45


if __name__ == "__main__":
    pytest.main([__file__])
