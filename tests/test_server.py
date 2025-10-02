"""
MCP Server Core Tests

Tests basic functionality and tool calls of the server.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from src.server import (
    call_tool,
    get_multiple_excel_summaries,
    list_tools,
)


class TestMCPServer:
    """MCP server tests"""

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test tool list return"""
        tools = await list_tools()

        assert len(tools) == 5  # 5 tools available

        tool_names = [tool.name for tool in tools]
        assert "list_excel_files" in tool_names
        assert "get_excel_summary" in tool_names
        assert "read_excel_data" in tool_names
        assert "search_in_excel" in tool_names
        assert "get_worksheet_summary" in tool_names

        # Validate each tool's schema
        for tool in tools:
            assert tool.name is not None
            assert tool.description is not None
            assert tool.inputSchema is not None
            assert tool.inputSchema["type"] == "object"
            assert "properties" in tool.inputSchema

    @pytest.mark.asyncio
    @patch("src.server.list_excel_files")
    async def test_call_tool_list_excel_files(self, mock_list_excel_files):
        """Test list_excel_files tool call"""
        # Mock setup
        mock_list_excel_files.return_value = {
            "success": True,
            "directory": "/test/directory",
            "recursive": True,
            "total_files": 2,
            "files": [
                {
                    "file_path": "/test/file1.xlsx",
                    "file_name": "file1.xlsx",
                    "file_size": 1024,
                    "modified_time": "2024-01-01T00:00:00Z",
                    "is_directory": False,
                },
                {
                    "file_path": "/test/file2.xlsx",
                    "file_name": "file2.xlsx",
                    "file_size": 2048,
                    "modified_time": "2024-01-02T00:00:00Z",
                    "is_directory": False,
                },
            ],
        }

        arguments = {"directory_path": "/test/directory", "recursive": True}

        result = await call_tool("list_excel_files", arguments)

        assert len(result) == 1
        assert result[0].type == "text"

        data = json.loads(result[0].text)
        assert data["success"] is True
        assert data["directory"] == "/test/directory"
        assert data["recursive"] is True
        assert data["total_files"] == 2

    @pytest.mark.asyncio
    @patch("src.server.get_excel_summary")
    async def test_call_tool_get_excel_summary_single_file(
        self, mock_get_excel_summary
    ):
        """Test get_excel_summary tool call (single file)"""
        # Mock setup
        mock_get_excel_summary.return_value = {
            "success": True,
            "file_path": "/test/file.xlsx",
            "file_name": "file.xlsx",
            "file_size": 1024,
            "worksheets": [
                {
                    "name": "Sheet1",
                    "index": 0,
                    "row_count": 100,
                    "column_count": 10,
                    "has_data": True,
                }
            ],
            "total_worksheets": 1,
        }

        arguments = {"file_path": "/test/file.xlsx"}

        result = await call_tool("get_excel_summary", arguments)

        assert len(result) == 1
        assert result[0].type == "text"

        data = json.loads(result[0].text)
        assert data["success"] is True
        assert data["file_path"] == "/test/file.xlsx"

    @pytest.mark.asyncio
    @patch("src.server.get_multiple_excel_summaries")
    async def test_call_tool_get_excel_summary_multiple_files(self, mock_get_multiple):
        """Test get_excel_summary tool call (multiple files)"""
        # Mock setup
        mock_get_multiple.return_value = {
            "success": True,
            "total_files": 3,
            "successful_files": 3,
            "failed_files": 0,
            "summaries": [
                {"success": True, "file_path": "/test/file1.xlsx"},
                {"success": True, "file_path": "/test/file2.xlsx"},
                {"success": True, "file_path": "/test/file3.xlsx"},
            ],
            "errors": [],
        }

        arguments = {
            "file_paths": ["/test/file1.xlsx", "/test/file2.xlsx", "/test/file3.xlsx"]
        }

        result = await call_tool("get_excel_summary", arguments)

        assert len(result) == 1
        assert result[0].type == "text"

        data = json.loads(result[0].text)
        assert data["success"] is True
        assert data["total_files"] == 3

    @pytest.mark.asyncio
    async def test_call_tool_get_excel_summary_invalid_parameters(self):
        """Test get_excel_summary tool call (invalid parameters)"""
        # Both provided
        arguments = {"file_path": "/test/file.xlsx", "file_paths": ["/test/file1.xlsx"]}

        result = await call_tool("get_excel_summary", arguments)
        data = json.loads(result[0].text)
        assert data["success"] is False
        assert "Either file_path or file_paths is required" in data["error"]

        # Neither provided
        arguments = {}

        result = await call_tool("get_excel_summary", arguments)
        data = json.loads(result[0].text)
        assert data["success"] is False
        assert "Either file_path or file_paths is required" in data["error"]

        # Empty list
        arguments = {"file_paths": []}

        result = await call_tool("get_excel_summary", arguments)
        data = json.loads(result[0].text)
        assert data["success"] is False
        assert "file_paths must be a non-empty list" in data["error"]

    @pytest.mark.asyncio
    @patch("src.server.read_excel_data")
    async def test_call_tool_read_excel_data(self, mock_read_excel_data):
        """Test read_excel_data tool call"""
        # Mock setup
        mock_read_excel_data.return_value = {
            "success": True,
            "file_path": "/test/file.xlsx",
            "worksheet_name": "Sheet1",
            "data": {
                "headers": ["ID", "Name", "Value"],
                "rows": [[1, "Item1", 100], [2, "Item2", 200]],
                "row_count": 2,
                "column_count": 3,
            },
            "max_rows_applied": 50,
        }

        arguments = {
            "file_path": "/test/file.xlsx",
            "worksheet_name": "Sheet1",
            "max_rows": 50,
        }

        result = await call_tool("read_excel_data", arguments)

        assert len(result) == 1
        assert result[0].type == "text"

        data = json.loads(result[0].text)
        assert data["success"] is True
        assert data["file_path"] == "/test/file.xlsx"
        assert data["worksheet_name"] == "Sheet1"
        assert data["max_rows_applied"] == 50

    @pytest.mark.asyncio
    @patch("src.server.search_in_excel")
    async def test_call_tool_search_in_excel(self, mock_search_in_excel):
        """Test search_in_excel tool call"""
        # Mock setup
        mock_search_in_excel.return_value = {
            "success": True,
            "file_path": "/test/file.xlsx",
            "worksheet_name": "Sheet1",
            "search_term": "test",
            "case_sensitive": False,
            "total_matches": 2,
            "matches": [
                {"row": 1, "column": "A", "cell_address": "A1", "value": "test value"},
                {
                    "row": 2,
                    "column": "B",
                    "cell_address": "B2",
                    "value": "another test",
                },
            ],
        }

        arguments = {
            "file_path": "/test/file.xlsx",
            "search_term": "test",
            "case_sensitive": False,
        }

        result = await call_tool("search_in_excel", arguments)

        assert len(result) == 1
        assert result[0].type == "text"

        data = json.loads(result[0].text)
        assert data["success"] is True
        assert data["file_path"] == "/test/file.xlsx"
        assert data["search_term"] == "test"
        assert data["total_matches"] == 2

    @pytest.mark.asyncio
    @patch("src.server.get_worksheet_summary")
    async def test_call_tool_get_worksheet_summary(self, mock_get_worksheet_summary):
        """Test get_worksheet_summary tool call"""
        # Mock setup
        mock_get_worksheet_summary.return_value = {
            "success": True,
            "file_path": "/test/file.xlsx",
            "file_name": "file.xlsx",
            "worksheets": [
                {
                    "name": "Sheet1",
                    "index": 0,
                    "row_count": 100,
                    "column_count": 10,
                    "has_data": True,
                    "data_range": {
                        "start_row": 1,
                        "end_row": 100,
                        "start_column": "A",
                        "end_column": "J",
                    },
                    "headers": ["ID", "Name", "Value"],
                    "header_count": 3,
                }
            ],
            "total_worksheets": 1,
        }

        arguments = {"file_path": "/test/file.xlsx"}

        result = await call_tool("get_worksheet_summary", arguments)

        assert len(result) == 1
        assert result[0].type == "text"

        data = json.loads(result[0].text)
        assert data["success"] is True
        assert data["file_path"] == "/test/file.xlsx"
        assert data["total_worksheets"] == 1

    @pytest.mark.asyncio
    async def test_call_tool_invalid_tool(self):
        """Test invalid tool call"""
        arguments = {"test": "value"}

        result = await call_tool("invalid_tool", arguments)

        assert len(result) == 1
        assert result[0].type == "text"

        data = json.loads(result[0].text)
        assert data["success"] is False
        assert "Unknown tool" in data["error"]

    @pytest.mark.asyncio
    async def test_call_tool_missing_required_parameter(self):
        """Test missing required parameter"""
        arguments = {}  # file_path missing

        result = await call_tool("get_excel_summary", arguments)

        assert len(result) == 1
        assert result[0].type == "text"

        data = json.loads(result[0].text)
        assert data["success"] is False
        assert "required" in data["error"]


if __name__ == "__main__":
    pytest.main([__file__])
