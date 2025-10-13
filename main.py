#!/usr/bin/env python3
"""
Excel Search MCP Server 실행 스크립트

이 스크립트를 통해 MCP 서버를 실행할 수 있습니다.
"""

import sys
import traceback
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from excel_search_mcp.server import create_server  # noqa: E402


def main():
    """MCP 서버를 실행합니다."""
    try:
        # FastMCP 서버 생성
        server = create_server()

        # FastMCP의 표준 실행 방식 사용 (anyio.run 내부 호출)
        server.run()
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        print(f"Traceback: {traceback.format_exc()}", file=sys.stderr)
        raise


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Server stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        print(f"Traceback: {traceback.format_exc()}", file=sys.stderr)
        sys.exit(1)
