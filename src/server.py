"""
MCP Server Core

Excel 파일 검색 및 처리를 위한 MCP 서버의 메인 모듈
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP 서버 인스턴스 생성
app = Server("excel-search-mcp")


# Excel 관련 함수들을 dummy로 구현
def list_excel_files_dummy(
    directory_path: str, recursive: bool = True
) -> Dict[str, Any]:
    """Excel 파일 목록을 반환하는 dummy 함수"""
    logger.info(
        "Searching Excel files in: %s (recursive: %s)", directory_path, recursive
    )

    # Dummy 데이터 반환
    dummy_files = [
        {
            "file_path": "/path/to/sample1.xlsx",
            "file_name": "sample1.xlsx",
            "file_size": 1024000,
            "modified_time": "2024-01-15T10:30:00Z",
            "is_directory": False,
        },
        {
            "file_path": "/path/to/sample2.xlsx",
            "file_name": "sample2.xlsx",
            "file_size": 2048000,
            "modified_time": "2024-01-16T14:20:00Z",
            "is_directory": False,
        },
        {
            "file_path": "/path/to/old_file.xls",
            "file_name": "old_file.xls",
            "file_size": 512000,
            "modified_time": "2024-01-10T09:15:00Z",
            "is_directory": False,
        },
    ]

    return {
        "success": True,
        "directory": directory_path,
        "recursive": recursive,
        "total_files": len(dummy_files),
        "files": dummy_files,
    }


def get_excel_summary_dummy(file_path: str) -> Dict[str, Any]:
    """Excel 파일 요약 정보를 반환하는 dummy 함수 (단일 파일)"""
    logger.info("Getting summary for Excel file: %s", file_path)

    # Dummy 데이터 반환
    return {
        "success": True,
        "file_path": file_path,
        "file_name": Path(file_path).name,
        "file_size": 1024000,
        "worksheets": [
            {
                "name": "Sheet1",
                "index": 0,
                "row_count": 100,
                "column_count": 10,
                "has_data": True,
            },
            {
                "name": "Sheet2",
                "index": 1,
                "row_count": 50,
                "column_count": 5,
                "has_data": True,
            },
        ],
        "total_worksheets": 2,
        "created_time": "2024-01-15T10:30:00Z",
        "modified_time": "2024-01-16T14:20:00Z",
    }

def get_multiple_excel_summaries_dummy(file_paths: List[str]) -> Dict[str, Any]:
    """여러 Excel 파일의 요약 정보를 반환하는 dummy 함수"""
    logger.info("Getting summaries for %d Excel files", len(file_paths))
    
    summaries = []
    for i, file_path in enumerate(file_paths):
        summary = get_excel_summary_dummy(file_path)
        summaries.append(summary)
    
    return {
        "success": True,
        "total_files": len(file_paths),
        "summaries": summaries
    }


def read_excel_data_dummy(
    file_path: str, worksheet_name: Optional[str] = None, max_rows: Optional[int] = None
) -> Dict[str, Any]:
    """Excel 파일 데이터를 JSON으로 반환하는 dummy 함수"""
    logger.info("Reading Excel data from: %s", file_path)
    logger.info("Worksheet: %s, Max rows: %s", worksheet_name, max_rows)

    # Dummy 데이터 반환
    dummy_data = {
        "headers": ["ID", "Name", "Age", "Department", "Salary"],
        "rows": [
            [1, "John Doe", 30, "Engineering", 75000],
            [2, "Jane Smith", 28, "Marketing", 65000],
            [3, "Bob Johnson", 35, "Sales", 70000],
            [4, "Alice Brown", 32, "Engineering", 80000],
            [5, "Charlie Wilson", 29, "HR", 60000],
        ],
    }

    return {
        "success": True,
        "file_path": file_path,
        "worksheet_name": worksheet_name or "Sheet1",
        "data": dummy_data,
        "row_count": len(dummy_data["rows"]),
        "column_count": len(dummy_data["headers"]),
        "max_rows_applied": max_rows,
    }


# MCP 도구 정의
@app.list_tools()
async def list_tools() -> List[Tool]:
    """사용 가능한 도구 목록을 반환합니다."""
    return [
        Tool(
            name="list_excel_files",
            description=(
                "Search and return a list of Excel files in the specified directory"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": ("Directory path to search for Excel files"),
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": (
                            "Whether to search recursively in subdirectories"
                        ),
                        "default": True,
                    },
                },
                "required": ["directory_path"],
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
                        "description": "Absolute path to a single Excel file"
                    },
                    "file_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of Excel file paths to process"
                    }
                },
                "anyOf": [
                    {"required": ["file_path"]},
                    {"required": ["file_paths"]}
                ]
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
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """도구 호출을 처리합니다."""
    try:
        logger.info("Calling tool: %s with arguments: %s", name, arguments)

        if name == "list_excel_files":
            directory_path = arguments.get("directory_path")
            recursive = arguments.get("recursive", True)

            if not directory_path:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"success": False, "error": "directory_path is required"},
                            ensure_ascii=False,
                            indent=2,
                        ),
                    )
                ]

            result = list_excel_files_dummy(directory_path, recursive)
            return [
                TextContent(
                    type="text", text=json.dumps(result, ensure_ascii=False, indent=2)
                )
            ]

        elif name == "get_excel_summary":
            file_path = arguments.get("file_path")
            file_paths = arguments.get("file_paths")

            # 단일 파일 처리
            if file_path and not file_paths:
                result = get_excel_summary_dummy(file_path)
                return [
                    TextContent(
                        type="text", text=json.dumps(result, ensure_ascii=False, indent=2)
                    )
                ]
            
            # 여러 파일 처리
            elif file_paths is not None and not file_path:
                if not isinstance(file_paths, list) or len(file_paths) == 0:
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps(
                                {"success": False, "error": "file_paths must be a non-empty list"},
                                ensure_ascii=False,
                                indent=2,
                            ),
                        )
                    ]
                
                result = get_multiple_excel_summaries_dummy(file_paths)
                return [
                    TextContent(
                        type="text", text=json.dumps(result, ensure_ascii=False, indent=2)
                    )
                ]
            
            # 매개변수 오류
            else:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"success": False, "error": "Either file_path or file_paths is required, but not both"},
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

            result = read_excel_data_dummy(file_path, worksheet_name, max_rows)
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
    """MCP 서버를 시작합니다."""
    logger.info("Starting Excel Search MCP Server...")

    # stdio 서버를 통해 실행
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="excel-search-mcp",
                server_version="0.1.0",
                capabilities={
                    "tools": {}
                }
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
