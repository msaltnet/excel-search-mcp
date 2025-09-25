#!/usr/bin/env python3
"""
Excel Search MCP Server 실행 스크립트

이 스크립트를 통해 MCP 서버를 실행할 수 있습니다.
"""

import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.server import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n서버가 사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"서버 실행 중 오류가 발생했습니다: {e}")
        sys.exit(1)
