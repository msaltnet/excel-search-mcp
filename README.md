# Excel Search MCP

로컬 PC의 엑셀 파일을 검색하고 내용을 읽어오는 MCP(Model Context Protocol) 서버

## 📋 프로젝트 개요

이 프로젝트는 MCP(Model Context Protocol)를 통해 로컬 PC의 Excel 파일들을 검색하고, 내용을 읽어와서 AI 모델이 활용할 수 있는 형태로 제공하는 서버입니다.

## 🎯 주요 기능

- **엑셀 파일 검색**: 지정된 디렉토리에서 Excel 파일들을 재귀적으로 검색
- **파일 목록 제공**: 발견된 Excel 파일들의 절대 경로 목록 제공
- **파일 요약**: Excel 파일의 기본 정보 및 구조 요약 제공
- **데이터 추출**: Excel 파일의 내용을 JSON 형태로 변환하여 제공
- **워크시트 관리**: 다중 워크시트 지원 및 개별 워크시트 접근

## 🏗️ 아키텍처

### 시스템 구성도
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Client     │◄──►│  MCP Server     │◄──►│  Excel Files    │
│   (Claude, etc) │    │  (Python)       │    │  (.xlsx, .xls)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  File System    │
                       │  (Directory     │
                       │   Scanning)     │
                       └─────────────────┘
```

### 핵심 컴포넌트

1. **MCP Server Core**
   - MCP 프로토콜 구현
   - 클라이언트와의 통신 관리
   - 요청/응답 처리

2. **Excel Processor**
   - Excel 파일 읽기/파싱
   - 워크시트 데이터 추출
   - JSON 변환 로직

3. **File Scanner**
   - 디렉토리 재귀 검색
   - Excel 파일 필터링
   - 파일 메타데이터 수집

4. **Data Formatter**
   - Excel 데이터를 JSON으로 변환
   - 요약 정보 생성
   - 에러 처리 및 검증

## 📝 작업 계획

### Phase 1: 프로젝트 초기 설정 (1-2일)
- [ ] Python 프로젝트 구조 설정
- [ ] MCP 서버 기본 프레임워크 구현
- [ ] 의존성 관리 (requirements.txt, pyproject.toml)
- [ ] 기본 설정 파일 구성

### Phase 2: 핵심 기능 구현 (3-4일)
- [ ] Excel 파일 검색 기능
  - [ ] 디렉토리 재귀 스캔
  - [ ] Excel 파일 확장자 필터링 (.xlsx, .xls)
  - [ ] 파일 메타데이터 수집
- [ ] Excel 파일 읽기 기능
  - [ ] openpyxl/pandas를 사용한 Excel 파싱
  - [ ] 다중 워크시트 지원
  - [ ] 데이터 타입 처리 (문자열, 숫자, 날짜 등)

### Phase 3: MCP 도구 구현 (2-3일)
- [ ] `list_excel_files` 도구
  - [ ] 지정된 디렉토리에서 Excel 파일 목록 반환
  - [ ] 파일 경로, 크기, 수정일시 정보 포함
- [ ] `get_excel_summary` 도구
  - [ ] Excel 파일의 기본 정보 제공
  - [ ] 워크시트 목록, 행/열 수, 데이터 타입 정보
- [ ] `read_excel_data` 도구
  - [ ] Excel 파일 내용을 JSON으로 변환
  - [ ] 특정 워크시트 선택 옵션
  - [ ] 데이터 범위 제한 옵션

### Phase 4: 고급 기능 및 최적화 (2-3일)
- [ ] 성능 최적화
  - [ ] 대용량 파일 처리 개선
  - [ ] 메모리 사용량 최적화
  - [ ] 캐싱 메커니즘 구현
- [ ] 에러 처리 강화
  - [ ] 파일 접근 권한 에러 처리
  - [ ] 손상된 Excel 파일 처리
  - [ ] 메모리 부족 상황 처리
- [ ] 로깅 및 모니터링
  - [ ] 상세한 로그 기록
  - [ ] 성능 메트릭 수집

### Phase 5: 테스트 및 문서화 (1-2일)
- [ ] 단위 테스트 작성
- [ ] 통합 테스트 구현
- [ ] 사용 예제 및 문서 작성
- [ ] README 업데이트

## 🛠️ 기술 스택

- **언어**: Python 3.8+
- **MCP 프레임워크**: mcp (Model Context Protocol)
- **Excel 처리**: openpyxl, pandas
- **파일 시스템**: pathlib, os
- **데이터 변환**: json
- **로깅**: logging
- **테스트**: pytest

## 📁 프로젝트 구조 (예상)

```
excel-search-mcp/
├── src/
│   ├── __init__.py
│   ├── server.py              # MCP 서버 메인
│   ├── excel_processor.py     # Excel 파일 처리
│   ├── file_scanner.py        # 파일 검색
│   └── data_formatter.py      # 데이터 변환
├── tests/
│   ├── __init__.py
│   ├── test_server.py
│   ├── test_excel_processor.py
│   └── test_file_scanner.py
├── examples/
│   ├── sample_excel_files/
│   └── usage_examples.py
├── requirements.txt
├── pyproject.toml
├── README.md
└── .gitignore
```

## 🚀 사용 예시

```python
# MCP 클라이언트에서 사용 예시
tools = [
    {
        "name": "list_excel_files",
        "description": "지정된 디렉토리에서 Excel 파일 목록을 반환합니다",
        "parameters": {
            "directory_path": "string",
            "recursive": "boolean"
        }
    },
    {
        "name": "get_excel_summary", 
        "description": "Excel 파일의 요약 정보를 제공합니다",
        "parameters": {
            "file_path": "string"
        }
    },
    {
        "name": "read_excel_data",
        "description": "Excel 파일의 데이터를 JSON으로 읽어옵니다",
        "parameters": {
            "file_path": "string",
            "worksheet_name": "string",
            "max_rows": "integer"
        }
    }
]
```

## 📊 성능 목표

- **파일 검색**: 1000개 파일 기준 5초 이내
- **Excel 읽기**: 10MB 파일 기준 3초 이내
- **메모리 사용량**: 100MB 이하
- **동시 처리**: 최대 10개 파일 동시 처리

## 🔒 보안 고려사항

- 파일 접근 권한 검증
- 경로 조작 공격 방지
- 메모리 사용량 제한
- 민감한 데이터 마스킹 옵션

## 📈 향후 확장 계획

- [ ] Excel 파일 쓰기 기능
- [ ] 실시간 파일 모니터링
- [ ] 원격 Excel 파일 지원 (URL, 클라우드)
- [ ] 고급 필터링 및 검색 기능
- [ ] 데이터 시각화 지원
