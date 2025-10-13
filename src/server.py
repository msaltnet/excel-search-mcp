"""
MCP Server Core

Main module of MCP server for Excel file search and processing
"""

import asyncio
import json
import logging
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)

# Local module imports
from .file_scanner import list_excel_files
from .excel_processor import (
    read_excel_data,
    search_in_excel,
)
from .config_manager import config_manager

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP server instance creation
app = Server("excel-search-mcp")


# MCP tool definitions
@app.list_tools()
async def list_tools() -> List[Tool]:
    """Returns a list of available tools."""
    return [
        Tool(
            name="list_excel_files",
            description=(
                "Search and return a list of Excel files in the configured work directory"
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="read_excel_data",
            description="Read Excel file data and convert it to JSON format",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": ("Absolute path to the Excel file"),
                    },
                    "worksheet_name": {
                        "type": "string",
                        "description": (
                            "Name of the worksheet to read (defaults to first "
                            "worksheet if not specified)"
                        ),
                    },
                    "max_rows": {
                        "type": "integer",
                        "description": (
                            "Maximum number of rows to read (reads all rows if "
                            "not specified)"
                        ),
                    },
                },
                "required": ["file_path"],
            },
        ),
        Tool(
            name="search_in_excel",
            description="Search for specific text within Excel file(s)",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the Excel file",
                    },
                    "search_term": {
                        "type": "string",
                        "description": "Text to search for",
                    },
                    "worksheet_name": {
                        "type": "string",
                        "description": "Specific worksheet to search (optional)",
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "Whether search should be case sensitive",
                        "default": False,
                    },
                },
                "required": ["file_path", "search_term"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handles tool calls."""
    try:
        logger.info("Calling tool: %s with arguments: %s", name, arguments)

        if name == "list_excel_files":
            directory_path = config_manager.get_work_directory()
            recursive = config_manager.get_recursive_search()
            max_files = config_manager.get_max_files_per_search()

            result = list_excel_files(directory_path, recursive, max_files)
            return [
                TextContent(
                    type="text", text=json.dumps(result, ensure_ascii=False, indent=2)
                )
            ]

        elif name == "read_excel_data":
            file_path = arguments.get("file_path")
            worksheet_name = arguments.get("worksheet_name")
            max_rows = arguments.get("max_rows")

            if not file_path:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"success": False, "error": "file_path is required"},
                            ensure_ascii=False,
                            indent=2,
                        ),
                    )
                ]

            result = read_excel_data(file_path, worksheet_name, max_rows)
            return [
                TextContent(
                    type="text", text=json.dumps(result, ensure_ascii=False, indent=2)
                )
            ]

        elif name == "search_in_excel":
            file_path = arguments.get("file_path")
            search_term = arguments.get("search_term")
            worksheet_name = arguments.get("worksheet_name")
            case_sensitive = arguments.get("case_sensitive", False)

            if not file_path or not search_term:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "success": False,
                                "error": "file_path and search_term are required",
                            },
                            ensure_ascii=False,
                            indent=2,
                        ),
                    )
                ]

            result = search_in_excel(
                file_path, search_term, worksheet_name, case_sensitive
            )
            return [
                TextContent(
                    type="text", text=json.dumps(result, ensure_ascii=False, indent=2)
                )
            ]

        else:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"success": False, "error": f"Unknown tool: {name}"},
                        ensure_ascii=False,
                        indent=2,
                    ),
                )
            ]

    except (ValueError, TypeError, FileNotFoundError, PermissionError) as e:
        logger.error("Error calling tool %s: %s", name, str(e))
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"success": False, "error": f"Tool execution failed: {str(e)}"},
                    ensure_ascii=False,
                    indent=2,
                ),
            )
        ]


async def main():
    """Starts the MCP server."""
    logger.info("Starting Excel Search MCP Server...")

    # Run through stdio server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="excel-search-mcp",
                server_version="0.1.0",
                capabilities={"tools": {}},
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
