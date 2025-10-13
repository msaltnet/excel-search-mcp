"""
MCP Server Core Tests

Tests basic functionality and tool calls of the server.
"""

import json
import pytest
from unittest.mock import patch

from src.server import (
    call_tool,
    list_tools,
)


class TestMCPServer:
    """MCP server tests"""

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test tool list return"""
        tools = await list_tools()

        assert len(tools) == 3  # 3 tools available

        tool_names = [tool.name for tool in tools]
        assert "list_excel_files" in tool_names
        assert "read_excel_data" in tool_names
        assert "search_in_excel" in tool_names

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

        result = await call_tool("read_excel_data", arguments)

        assert len(result) == 1
        assert result[0].type == "text"

        data = json.loads(result[0].text)
        assert data["success"] is False
        assert "required" in data["error"]


if __name__ == "__main__":
    pytest.main([__file__])
