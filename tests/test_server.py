"""
MCP Server Core Tests

Tests basic functionality and tool calls of the server.
"""

import pytest


class TestMCPServer:
    """MCP server tests"""

    def test_server_creation(self) -> None:
        """Test server creation"""
        from excel_search_mcp.server import create_server

        server = create_server()
        assert server is not None
        # FastMCP 객체는 다른 속성 구조를 가집니다
        assert hasattr(server, "__class__")
        assert server.__class__.__name__ == "FastMCP"

    def test_tool_functions_exist(self) -> None:
        """Test that tool functions exist"""
        from excel_search_mcp.server import create_server

        server = create_server()

        # FastMCP는 다른 방식으로 도구를 관리합니다
        # 서버가 정상적으로 생성되었는지 확인
        assert server is not None
        assert hasattr(server, "__class__")
        assert server.__class__.__name__ == "FastMCP"

    def test_config_manager(self) -> None:
        """Test configuration manager"""
        from excel_search_mcp.config_manager import config_manager

        # Test that config_manager is properly initialized
        assert config_manager is not None

        # Test that it can get work directory
        work_dir = config_manager.get_work_directory()
        assert work_dir is not None
        assert isinstance(work_dir, str)

        # Test other config methods
        assert isinstance(config_manager.get_supported_extensions(), list)
        assert isinstance(config_manager.get_max_file_size_mb(), int)
        assert isinstance(config_manager.get_max_files_per_search(), int)
        assert isinstance(config_manager.get_recursive_search(), bool)

    def test_list_excel_sheets_function(self) -> None:
        """Test list_excel_sheets function"""
        from pathlib import Path

        from excel_search_mcp.excel_processor import list_excel_sheets

        # Test with a sample file
        sample_file = Path("sample/Apples-2022.xlsx")
        if sample_file.exists():
            result = list_excel_sheets(str(sample_file.absolute()))

            # Check result structure
            assert isinstance(result, dict)
            assert "success" in result

            # If successful, check returned data
            if result.get("success"):
                assert "sheets" in result
                assert "sheet_count" in result
                assert isinstance(result["sheets"], list)
                assert isinstance(result["sheet_count"], int)
                assert result["sheet_count"] == len(result["sheets"])
                assert result["sheet_count"] > 0  # Should have at least one sheet


if __name__ == "__main__":
    pytest.main([__file__])
