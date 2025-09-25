# MCP 서버 테스트 가이드

Excel Search MCP 서버의 다양한 테스트 방법을 설명합니다.

## 📋 목차

- [1. 단위 테스트](#1-단위-테스트)
- [2. 수동 기능 테스트](#2-수동-기능-테스트)
- [3. 성능 및 메모리 테스트](#3-성능-및-메모리-테스트)
- [4. 실제 MCP 서버 실행](#4-실제-mcp-서버-실행)
- [5. 코드 품질 테스트](#5-코드-품질-테스트)
- [6. 통합 테스트](#6-통합-테스트)
- [7. 테스트 결과 해석](#7-테스트-결과-해석)

## 1. 단위 테스트

가장 기본적인 테스트 방법입니다. 각 함수와 도구의 개별 동작을 검증합니다.

### 전체 테스트 실행
```bash
python -m pytest tests/ -v
```

### 특정 테스트 실행
```bash
# 특정 클래스 테스트
python -m pytest tests/test_server.py::TestDummyFunctions -v

# 특정 함수 테스트
python -m pytest tests/test_server.py::TestMCPServer::test_call_tool_get_excel_summary_multiple_files -v

# 키워드로 필터링
python -m pytest tests/ -k "excel_summary" -v
```

### 커버리지 포함 테스트
```bash
# HTML 리포트 생성
python -m pytest tests/ --cov=src --cov-report=html

# 터미널에서 커버리지 표시
python -m pytest tests/ --cov=src --cov-report=term
```

### 테스트 결과 예시
```
============================= test session starts =============================
collected 12 items

tests/test_server.py::TestDummyFunctions::test_list_excel_files_dummy PASSED [  8%]
tests/test_server.py::TestDummyFunctions::test_get_excel_summary_dummy PASSED [ 16%]
tests/test_server.py::TestDummyFunctions::test_read_excel_data_dummy PASSED [ 25%]
tests/test_server.py::TestDummyFunctions::test_get_multiple_excel_summaries_dummy PASSED [ 33%]
tests/test_server.py::TestMCPServer::test_list_tools PASSED [ 41%]
tests/test_server.py::TestMCPServer::test_call_tool_list_excel_files PASSED [ 50%]
tests/test_server.py::TestMCPServer::test_call_tool_get_excel_summary_single_file PASSED [ 58%]
tests/test_server.py::TestMCPServer::test_call_tool_get_excel_summary_multiple_files PASSED [ 66%]
tests/test_server.py::TestMCPServer::test_call_tool_get_excel_summary_invalid_parameters PASSED [ 75%]
tests/test_server.py::TestMCPServer::test_call_tool_read_excel_data PASSED [ 83%]
tests/test_server.py::TestMCPServer::test_call_tool_invalid_tool PASSED [ 91%]
tests/test_server.py::TestMCPServer::test_call_tool_missing_required_parameter PASSED [100%]

======================== 12 passed, 1 warning in 0.32s =======================
```

## 2. 수동 기능 테스트

MCP 서버의 실제 동작을 시뮬레이션하여 테스트합니다.

### 기본 기능 테스트
```bash
python test_mcp_server.py
```

### 테스트 내용
- 🔧 **도구 목록 테스트**: 등록된 MCP 도구들 확인
- 📄 **단일 파일 요약**: `get_excel_summary` 단일 파일 처리
- 📚 **여러 파일 요약**: `get_excel_summary` 여러 파일 처리
- 📁 **파일 목록**: `list_excel_files` 디렉토리 검색
- 📊 **데이터 읽기**: `read_excel_data` Excel 데이터 추출
- ❌ **에러 처리**: 잘못된 입력에 대한 오류 처리

### 테스트 결과 예시
```
🧪 MCP 서버 수동 테스트
============================================================

🔧 도구 목록 테스트
==================================================
총 3개의 도구가 등록되어 있습니다:
1. list_excel_files
   설명: Search and return a list of Excel files in the specified directory
   매개변수: ['directory_path', 'recursive']

2. get_excel_summary
   설명: Get summary information about Excel file(s) including worksheets and metadata. Can process single file or multiple files.
   매개변수: ['file_path', 'file_paths']

3. read_excel_data
   설명: Read Excel file data and convert it to JSON format
   매개변수: ['file_path', 'worksheet_name', 'max_rows']

✅ 모든 테스트가 성공적으로 완료되었습니다!
```

## 3. 성능 및 메모리 테스트

서버의 성능과 메모리 사용량을 측정합니다.

### 성능 테스트 실행
```bash
python test_mcp_server.py
```

### 테스트 항목
- ⚡ **처리 속도**: 단일/여러 파일 처리 시간 측정
- 💾 **메모리 사용량**: 대량 데이터 처리 시 메모리 사용량
- 🌐 **MCP 통신**: 실제 MCP 프로토콜 통신 테스트

### 성능 기준
- **단일 파일 처리**: 평균 < 10ms
- **여러 파일 처리**: 100개 파일 < 1초
- **메모리 사용량**: 1000개 파일 처리 시 < 100MB 증가

## 4. 실제 MCP 서버 실행

실제 MCP 서버를 실행하여 클라이언트와의 통신을 테스트합니다.

### 서버 실행
```bash
# 터미널 1: MCP 서버 시작
python main.py
```

### 클라이언트 테스트
```bash
# 터미널 2: MCP 클라이언트로 연결
mcp-client stdio python main.py
```

### 수동 테스트 명령어
MCP 클라이언트에서 다음 명령어들을 테스트할 수 있습니다:

```json
// 도구 목록 조회
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}

// 단일 파일 요약
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "get_excel_summary",
    "arguments": {
      "file_path": "/path/to/file.xlsx"
    }
  }
}

// 여러 파일 요약
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "get_excel_summary",
    "arguments": {
      "file_paths": ["/path/to/file1.xlsx", "/path/to/file2.xlsx"]
    }
  }
}
```

## 5. 코드 품질 테스트

코드의 품질과 스타일을 검사합니다.

### 포매팅 검사
```bash
# Black 포매터 실행
python -m black src/ tests/ examples/ main.py

# isort로 import 정렬
python -m isort src/ tests/ examples/ main.py
```

### 린터 검사
```bash
# flake8로 코드 스타일 검사
python -m flake8 src/ tests/ examples/ main.py --ignore=E402

# mypy로 타입 검사
python -m mypy src/
```

### Pre-commit Hook 설정
```bash
# pre-commit 설치
pip install pre-commit

# Git hook 설정
pre-commit install

# 모든 파일에 대해 pre-commit 실행
pre-commit run --all-files
```

## 6. 통합 테스트

모든 테스트를 종합적으로 실행합니다.

### 전체 테스트 스위트
```bash
# 모든 테스트 + 커버리지
python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term

# 특정 태그가 있는 테스트만 실행
python -m pytest tests/ -m "not slow" -v
```

### CI/CD 파이프라인 테스트
```bash
# 코드 품질 검사
python -m black --check src/ tests/ examples/ main.py
python -m flake8 src/ tests/ examples/ main.py --ignore=E402
python -m mypy src/

# 테스트 실행
python -m pytest tests/ --cov=src --cov-fail-under=90
```

## 7. 테스트 결과 해석

### 성공적인 테스트 결과
- ✅ **모든 테스트 통과**: 12/12 테스트 성공
- ✅ **코드 커버리지**: 90% 이상 권장
- ✅ **린터 검사**: 오류 없음
- ✅ **성능 기준**: 목표 성능 달성

### 문제가 있는 경우
- ❌ **테스트 실패**: 실패한 테스트 확인 및 수정
- ❌ **낮은 커버리지**: 테스트 케이스 추가
- ❌ **린터 오류**: 코드 스타일 수정
- ❌ **성능 저하**: 알고리즘 최적화 필요

### 디버깅 팁
```bash
# 상세한 오류 정보 출력
python -m pytest tests/ -v -s --tb=long

# 특정 테스트만 디버깅
python -m pytest tests/test_server.py::TestMCPServer::test_call_tool_get_excel_summary_multiple_files -v -s

# 로그 레벨 조정
python -m pytest tests/ --log-cli-level=DEBUG
```

## 🎯 테스트 체크리스트

개발 완료 후 다음 항목들을 확인하세요:

- [ ] 단위 테스트 모두 통과 (12/12)
- [ ] 수동 기능 테스트 통과
- [ ] 성능 기준 달성
- [ ] 메모리 사용량 정상
- [ ] 코드 포매팅 완료
- [ ] 린터 검사 통과
- [ ] 타입 검사 통과
- [ ] 커버리지 90% 이상
- [ ] 문서 업데이트 완료

## 📚 추가 리소스

- [pytest 공식 문서](https://docs.pytest.org/)
- [MCP 프로토콜 명세](https://modelcontextprotocol.io/)
- [Black 포매터 가이드](https://black.readthedocs.io/)
- [flake8 린터 가이드](https://flake8.pycqa.org/)
