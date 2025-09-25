"""
Excel Search MCP Server 사용 예제

MCP 서버의 각 도구를 사용하는 방법을 보여주는 예제입니다.
"""

import json
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.server import call_tool, list_tools


def example_list_excel_files():
    """Excel 파일 목록 검색 예제"""
    print("=== Excel 파일 목록 검색 예제 ===")

    # 도구 목록 확인
    tools = list_tools()
    print(f"사용 가능한 도구 수: {len(tools)}")

    # list_excel_files 도구 호출
    arguments = {"directory_path": "/Users/username/Documents", "recursive": True}

    result = call_tool("list_excel_files", arguments)
    data = json.loads(result[0].text)

    print(f"검색 결과: {data['total_files']}개 파일 발견")
    for file_info in data["files"]:
        print(f"  - {file_info['file_name']} ({file_info['file_size']} bytes)")


def example_get_excel_summary():
    """Excel 파일 요약 정보 조회 예제"""
    print("\n=== Excel 파일 요약 정보 예제 ===")

    # 단일 파일 요약
    print("1. 단일 파일 요약:")
    arguments = {"file_path": "/path/to/sample.xlsx"}

    result = call_tool("get_excel_summary", arguments)
    data = json.loads(result[0].text)

    print(f"파일: {data['file_name']}")
    print(f"워크시트 수: {data['total_worksheets']}")
    for worksheet in data["worksheets"]:
        print(
            f"  - {worksheet['name']}: {worksheet['row_count']}행 x "
            f"{worksheet['column_count']}열"
        )

    # 여러 파일 요약
    print("\n2. 여러 파일 요약:")
    arguments = {
        "file_paths": [
            "/path/to/sample1.xlsx",
            "/path/to/sample2.xlsx",
            "/path/to/sample3.xlsx"
        ]
    }

    result = call_tool("get_excel_summary", arguments)
    data = json.loads(result[0].text)

    print(f"총 {data['total_files']}개 파일 처리:")
    for i, summary in enumerate(data["summaries"]):
        print(f"  파일 {i+1}: {summary['file_name']}")
        print(f"    워크시트 수: {summary['total_worksheets']}")
        print(f"    파일 크기: {summary['file_size']} bytes")


def example_read_excel_data():
    """Excel 데이터 읽기 예제"""
    print("\n=== Excel 데이터 읽기 예제 ===")

    arguments = {
        "file_path": "/path/to/sample.xlsx",
        "worksheet_name": "Sheet1",
        "max_rows": 10,
    }

    result = call_tool("read_excel_data", arguments)
    data = json.loads(result[0].text)

    print(f"워크시트: {data['worksheet_name']}")
    print(f"데이터 크기: {data['row_count']}행 x {data['column_count']}열")
    print("헤더:", data["data"]["headers"])
    print("첫 5행 데이터:")
    for i, row in enumerate(data["data"]["rows"][:5]):
        print(f"  {i + 1}: {row}")


def example_error_handling():
    """에러 처리 예제"""
    print("\n=== 에러 처리 예제 ===")

    # 잘못된 도구 호출
    result = call_tool("invalid_tool", {})
    data = json.loads(result[0].text)
    print(f"잘못된 도구 호출: {data['error']}")

    # 필수 매개변수 누락
    result = call_tool("list_excel_files", {})
    data = json.loads(result[0].text)
    print(f"필수 매개변수 누락: {data['error']}")


def main():
    """모든 예제 실행"""
    print("Excel Search MCP Server 사용 예제")
    print("=" * 50)

    try:
        example_list_excel_files()
        example_get_excel_summary()
        example_read_excel_data()
        example_error_handling()

        print("\n모든 예제가 성공적으로 실행되었습니다!")

    except Exception as e:
        print(f"예제 실행 중 오류 발생: {e}")


if __name__ == "__main__":
    main()
