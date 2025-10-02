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
    get_excel_summary,
    read_excel_data,
    get_worksheet_summary,
    search_in_excel,
)
from .config_manager import config_manager

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP server instance creation
app = Server("excel-search-mcp")


# Excel related functions - using actual implementation
def get_multiple_excel_summaries(file_paths: List[str]) -> Dict[str, Any]:
    """Function that returns summary information for multiple Excel files"""
    logger.info("Getting summaries for %d Excel files", len(file_paths))

    summaries = []
    errors = []

    for file_path in file_paths:
        try:
            summary = get_excel_summary(file_path)
            summaries.append(summary)
        except Exception as e:
            logger.error(
                "Failed to get file summary information: %s - %s", file_path, e
            )
            errors.append({"file_path": file_path, "error": str(e)})

    return {
        "success": True,
        "total_files": len(file_paths),
        "successful_files": len(summaries),
        "failed_files": len(errors),
        "summaries": summaries,
        "errors": errors,
    }


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
            name="get_excel_summary",
            description=(
                "Get summary information about Excel file(s) including "
                "worksheets and metadata. Can process single file or multiple files."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to a single Excel file",
                    },
                    "file_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of Excel file paths to process",
                    },
                },
                "anyOf": [{"required": ["file_path"]}, {"required": ["file_paths"]}],
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
        Tool(
            name="get_worksheet_summary",
            description="Get detailed summary of all worksheets in an Excel file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the Excel file",
                    }
                },
                "required": ["file_path"],
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

        elif name == "get_excel_summary":
            file_path = arguments.get("file_path")
            file_paths = arguments.get("file_paths")

            # Single file processing
            if file_path and not file_paths:
                result = get_excel_summary(file_path)
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2),
                    )
                ]

            # Multiple files processing
            elif file_paths is not None and not file_path:
                if not isinstance(file_paths, list) or len(file_paths) == 0:
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps(
                                {
                                    "success": False,
                                    "error": "file_paths must be a non-empty list",
                                },
                                ensure_ascii=False,
                                indent=2,
                            ),
                        )
                    ]

                result = get_multiple_excel_summaries(file_paths)
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2),
                    )
                ]

            # Parameter error
            else:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "success": False,
                                "error": "Either file_path or file_paths is required, but not both",
                            },
                            ensure_ascii=False,
                            indent=2,
                        ),
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

        elif name == "get_worksheet_summary":
            file_path = arguments.get("file_path")

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

            result = get_worksheet_summary(file_path)
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
