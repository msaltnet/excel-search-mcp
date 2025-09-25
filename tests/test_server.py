"""
MCP Server Core 테스트

서버의 기본 기능과 도구 호출을 테스트합니다.
"""

import json

import pytest

# from unittest.mock import patch, MagicMock  # 향후 사용 예정
from src.server import (
    call_tool,
    get_excel_summary_dummy,
    get_multiple_excel_summaries_dummy,
    list_excel_files_dummy,
    list_tools,
    read_excel_data_dummy,
)


class TestDummyFunctions:
    """Dummy 함수들의 테스트"""

    def test_list_excel_files_dummy(self):
        """list_excel_files_dummy 함수 테스트"""
        result = list_excel_files_dummy("/test/directory", True)

        assert result["success"] is True
        assert result["directory"] == "/test/directory"
        assert result["recursive"] is True
        assert "files" in result
        assert len(result["files"]) > 0
        assert result["total_files"] == len(result["files"])

        # 파일 정보 검증
        for file_info in result["files"]:
            assert "file_path" in file_info
            assert "file_name" in file_info
            assert "file_size" in file_info
            assert "modified_time" in file_info
            assert file_info["is_directory"] is False

    def test_get_excel_summary_dummy(self):
        """get_excel_summary_dummy 함수 테스트"""
        result = get_excel_summary_dummy("/test/file.xlsx")

        assert result["success"] is True
        assert result["file_path"] == "/test/file.xlsx"
        assert "worksheets" in result
        assert result["total_worksheets"] > 0
        assert len(result["worksheets"]) == result["total_worksheets"]

        # 워크시트 정보 검증
        for worksheet in result["worksheets"]:
            assert "name" in worksheet
            assert "index" in worksheet
            assert "row_count" in worksheet
            assert "column_count" in worksheet
            assert "has_data" in worksheet

    def test_read_excel_data_dummy(self):
        """read_excel_data_dummy 함수 테스트"""
        result = read_excel_data_dummy("/test/file.xlsx", "Sheet1", 100)

        assert result["success"] is True
        assert result["file_path"] == "/test/file.xlsx"
        assert result["worksheet_name"] == "Sheet1"
        assert result["max_rows_applied"] == 100
        assert "data" in result
        assert "headers" in result["data"]
        assert "rows" in result["data"]
        assert result["row_count"] == len(result["data"]["rows"])
        assert result["column_count"] == len(result["data"]["headers"])

    def test_get_multiple_excel_summaries_dummy(self):
        """get_multiple_excel_summaries_dummy 함수 테스트"""
        file_paths = ["/test/file1.xlsx", "/test/file2.xlsx", "/test/file3.xlsx"]
        result = get_multiple_excel_summaries_dummy(file_paths)

        assert result["success"] is True
        assert result["total_files"] == 3
        assert "summaries" in result
        assert len(result["summaries"]) == 3

        # 각 요약 정보 검증
        for i, summary in enumerate(result["summaries"]):
            assert summary["success"] is True
            assert summary["file_path"] == file_paths[i]
            assert "worksheets" in summary
            assert summary["total_worksheets"] > 0


class TestMCPServer:
    """MCP 서버 테스트"""

    def test_list_tools(self):
        """도구 목록 반환 테스트"""
        tools = list_tools()

        assert len(tools) == 3

        tool_names = [tool.name for tool in tools]
        assert "list_excel_files" in tool_names
        assert "get_excel_summary" in tool_names
        assert "read_excel_data" in tool_names

        # 각 도구의 스키마 검증
        for tool in tools:
            assert tool.name is not None
            assert tool.description is not None
            assert tool.inputSchema is not None
            assert tool.inputSchema["type"] == "object"
            assert "properties" in tool.inputSchema

    def test_call_tool_list_excel_files(self):
        """list_excel_files 도구 호출 테스트"""
        arguments = {"directory_path": "/test/directory", "recursive": True}

        result = call_tool("list_excel_files", arguments)

        assert len(result) == 1
        assert result[0].type == "text"

        data = json.loads(result[0].text)
        assert data["success"] is True
        assert data["directory"] == "/test/directory"
        assert data["recursive"] is True

    def test_call_tool_get_excel_summary_single_file(self):
        """get_excel_summary 도구 호출 테스트 (단일 파일)"""
        arguments = {"file_path": "/test/file.xlsx"}

        result = call_tool("get_excel_summary", arguments)

        assert len(result) == 1
        assert result[0].type == "text"

        data = json.loads(result[0].text)
        assert data["success"] is True
        assert data["file_path"] == "/test/file.xlsx"

    def test_call_tool_get_excel_summary_multiple_files(self):
        """get_excel_summary 도구 호출 테스트 (여러 파일)"""
        arguments = {
            "file_paths": ["/test/file1.xlsx", "/test/file2.xlsx", "/test/file3.xlsx"]
        }

        result = call_tool("get_excel_summary", arguments)

        assert len(result) == 1
        assert result[0].type == "text"

        data = json.loads(result[0].text)
        assert data["success"] is True
        assert data["total_files"] == 3
        assert "summaries" in data
        assert len(data["summaries"]) == 3

    def test_call_tool_get_excel_summary_invalid_parameters(self):
        """get_excel_summary 도구 호출 테스트 (잘못된 매개변수)"""
        # 둘 다 제공
        arguments = {
            "file_path": "/test/file.xlsx",
            "file_paths": ["/test/file1.xlsx"]
        }

        result = call_tool("get_excel_summary", arguments)
        data = json.loads(result[0].text)
        assert data["success"] is False
        assert "Either file_path or file_paths is required" in data["error"]

        # 둘 다 없음
        arguments = {}

        result = call_tool("get_excel_summary", arguments)
        data = json.loads(result[0].text)
        assert data["success"] is False
        assert "Either file_path or file_paths is required" in data["error"]

        # 빈 리스트
        arguments = {"file_paths": []}

        result = call_tool("get_excel_summary", arguments)
        data = json.loads(result[0].text)
        assert data["success"] is False
        assert "file_paths must be a non-empty list" in data["error"]

    def test_call_tool_read_excel_data(self):
        """read_excel_data 도구 호출 테스트"""
        arguments = {
            "file_path": "/test/file.xlsx",
            "worksheet_name": "Sheet1",
            "max_rows": 50,
        }

        result = call_tool("read_excel_data", arguments)

        assert len(result) == 1
        assert result[0].type == "text"

        data = json.loads(result[0].text)
        assert data["success"] is True
        assert data["file_path"] == "/test/file.xlsx"
        assert data["worksheet_name"] == "Sheet1"
        assert data["max_rows_applied"] == 50

    def test_call_tool_invalid_tool(self):
        """존재하지 않는 도구 호출 테스트"""
        arguments = {"test": "value"}

        result = call_tool("invalid_tool", arguments)

        assert len(result) == 1
        assert result[0].type == "text"

        data = json.loads(result[0].text)
        assert data["success"] is False
        assert "Unknown tool" in data["error"]

    def test_call_tool_missing_required_parameter(self):
        """필수 매개변수 누락 테스트"""
        arguments = {}  # directory_path 누락

        result = call_tool("list_excel_files", arguments)

        assert len(result) == 1
        assert result[0].type == "text"

        data = json.loads(result[0].text)
        assert data["success"] is False
        assert "required" in data["error"]


if __name__ == "__main__":
    pytest.main([__file__])
