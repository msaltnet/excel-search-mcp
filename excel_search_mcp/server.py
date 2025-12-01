"""
MCP Server Core

Main module of MCP server for Excel file search and processing
"""

import json
import logging
from typing import Annotated, Optional

from mcp.server.fastmcp import Context, FastMCP
from pydantic import Field

from .config_manager import config_manager
from .excel_processor import list_excel_sheets, read_excel_data, search_in_excel

# Local module imports
from .file_scanner import list_excel_files

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_server() -> FastMCP:
    """Create and return a FastMCP server instance with session config."""

    server = FastMCP(name="Excel Search MCP")

    @server.tool()
    def list_excel_files_tool(ctx: Context) -> str:
        """Search and return a list of Excel files in the configured work directory."""
        try:
            # Use config_manager instead of session_config
            directory_path = config_manager.get_work_directory()
            recursive = config_manager.get_recursive_search()
            max_files = config_manager.get_max_files_per_search()

            result = list_excel_files(directory_path, recursive, max_files)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error("Error in list_excel_files_tool: %s", str(e))
            return json.dumps(
                {"success": False, "error": f"Tool execution failed: {str(e)}"},
                ensure_ascii=False,
                indent=2,
            )

    @server.tool()
    def read_excel_data_tool(
        file_path: Annotated[
            str,
            Field(
                description="Path to the Excel file to read. Can be absolute or relative path. Must be within the configured work_directory."
            ),
        ],
        ctx: Context,
        worksheet_name: Annotated[
            Optional[str],
            Field(
                description="Name of the worksheet to read. If None, reads the first sheet in the workbook."
            ),
        ] = None,
        max_rows: Annotated[
            Optional[int],
            Field(
                description="Maximum number of rows to read from the sheet. If None, reads all rows. The first row is always treated as headers and excluded from the row count.",
                ge=1,
            ),
        ] = None,
    ) -> str:
        """Read Excel file data and convert it to JSON format."""
        try:
            if not file_path:
                return json.dumps(
                    {"success": False, "error": "file_path is required"},
                    ensure_ascii=False,
                    indent=2,
                )

            result = read_excel_data(file_path, worksheet_name, max_rows)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error("Error in read_excel_data_tool: %s", str(e))
            return json.dumps(
                {"success": False, "error": f"Tool execution failed: {str(e)}"},
                ensure_ascii=False,
                indent=2,
            )

    @server.tool()
    def search_in_excel_tool(
        file_path: Annotated[
            str,
            Field(
                description="Path to the Excel file to search in. Can be absolute or relative path. Must be within the configured work_directory."
            ),
        ],
        search_term: Annotated[
            str,
            Field(
                description="Text to search for within the Excel file. Searches all cell values in the specified worksheet."
            ),
        ],
        ctx: Context,
        worksheet_name: Annotated[
            Optional[str],
            Field(
                description="Name of the worksheet to search in. If None, searches the first sheet in the workbook."
            ),
        ] = None,
        case_sensitive: Annotated[
            bool,
            Field(
                description="Whether to perform case-sensitive search. Default is False (case-insensitive)."
            ),
        ] = False,
    ) -> str:
        """Search for specific text within Excel file(s)."""
        try:
            if not file_path or not search_term:
                return json.dumps(
                    {
                        "success": False,
                        "error": "file_path and search_term are required",
                    },
                    ensure_ascii=False,
                    indent=2,
                )

            result = search_in_excel(
                file_path, search_term, worksheet_name, case_sensitive
            )
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error("Error in search_in_excel_tool: %s", str(e))
            return json.dumps(
                {"success": False, "error": f"Tool execution failed: {str(e)}"},
                ensure_ascii=False,
                indent=2,
            )

    @server.tool()
    def list_excel_sheets_tool(
        file_path: Annotated[
            str,
            Field(
                description="Path to the Excel file. Can be absolute or relative path. Must be within the configured work_directory."
            ),
        ],
        ctx: Context,
    ) -> str:
        """List all sheet names in an Excel file."""
        try:
            if not file_path:
                return json.dumps(
                    {"success": False, "error": "file_path is required"},
                    ensure_ascii=False,
                    indent=2,
                )

            result = list_excel_sheets(file_path)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error("Error in list_excel_sheets_tool: %s", str(e))
            return json.dumps(
                {"success": False, "error": f"Tool execution failed: {str(e)}"},
                ensure_ascii=False,
                indent=2,
            )

    return server
