# Excel Search MCP

로컬 PC의 엑셀 파일을 검색하고 내용을 읽어오는 MCP(Model Context Protocol) 서버

[한국어 문서](README_ko.md) | [English Documentation](README.md)

## 📋 프로젝트 개요

이 프로젝트는 MCP(Model Context Protocol)를 통해 로컬 PC의 Excel 파일들을 검색하고, 내용을 읽어와서 AI 모델이 활용할 수 있는 형태로 제공하는 서버입니다. Claude Desktop, Cursor 등 MCP를 지원하는 AI 클라이언트에서 Excel 파일을 직접 검색하고 분석할 수 있습니다.

## 🎯 주요 기능

- **엑셀 파일 검색**: 지정된 디렉토리에서 Excel 파일들을 재귀적으로 검색
- **파일 목록 제공**: 발견된 Excel 파일들의 절대 경로, 크기, 수정일시 등 메타데이터 제공
- **데이터 추출**: Excel 파일의 내용을 JSON 형태로 변환하여 제공
- **텍스트 검색**: Excel 파일 내에서 특정 텍스트 검색 기능
- **워크시트 관리**: 다중 워크시트 지원 및 개별 워크시트 접근
- **보안 제어**: 작업 디렉토리 제한을 통한 파일 접근 보안

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

1. **MCP Server Core** (`src/server.py`)
   - MCP 프로토콜 구현
   - 클라이언트와의 통신 관리
   - 요청/응답 처리

2. **Excel Processor** (`src/excel_processor.py`)
   - Excel 파일 읽기/파싱
   - 워크시트 데이터 추출
   - JSON 변환 로직

3. **File Scanner** (`src/file_scanner.py`)
   - 디렉토리 재귀 검색
   - Excel 파일 필터링
   - 파일 메타데이터 수집

4. **Config Manager** (`src/config_manager.py`)
   - 설정 파일 관리
   - 보안 정책 적용
   - 작업 디렉토리 제한

## 🛠️ 기술 스택

- **언어**: Python 3.8+
- **MCP 프레임워크**: mcp (Model Context Protocol)
- **Excel 처리**: openpyxl, pandas
- **파일 시스템**: pathlib, os
- **데이터 변환**: json
- **로깅**: logging
- **테스트**: pytest

## 📁 프로젝트 구조

```
excel-search-mcp/
├── src/
│   ├── __init__.py
│   ├── server.py              # MCP 서버 메인
│   ├── excel_processor.py     # Excel 파일 처리
│   ├── file_scanner.py        # 파일 검색
│   ├── config_manager.py      # 설정 관리
│   └── data_formatter.py      # 데이터 변환
├── tests/
│   ├── test_server.py
│   ├── test_simple.py
│   └── test_integration.py
├── examples/
│   ├── sample_excel_files/
│   └── usage_examples.py
├── sample/                    # 샘플 Excel 파일들
├── requirements.txt
├── pyproject.toml
├── config.json               # 설정 파일
└── README.md
```

## 🚀 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 설정 파일 구성

`config.json` 파일을 생성하여 작업 디렉토리를 설정합니다:

```json
{
  "work_directory": "/path/to/your/excel/files",
  "excel": {
    "supported_extensions": [".xlsx", ".xls", ".xlsm", ".xlsb"],
    "max_file_size_mb": 100,
    "max_files_per_search": 1000,
    "recursive_search": true
  }
}
```

### 3. MCP 클라이언트 설정

#### Claude Desktop 설정 (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "excel-search-mcp": {
      "command": "python",
      "args": ["C:/path/to/excel-search-mcp/src/server.py"],
      "env": {}
    }
  }
}
```

#### Cursor 설정 (`cursor_mcp_config.json`)
```json
{
  "mcpServers": {
    "excel-search-mcp": {
      "command": "python",
      "args": ["C:/path/to/excel-search-mcp/src/server.py"]
    }
  }
}
```

## 📊 사용 가능한 도구

### 1. `list_excel_files`
지정된 디렉토리에서 Excel 파일 목록을 반환합니다.

**매개변수**: 없음 (설정 파일의 work_directory 사용)

**반환값**:
```json
{
  "success": true,
  "directory": "/path/to/directory",
  "total_files": 5,
  "scanned_files": 100,
  "files": [
    {
      "file_path": "/path/to/file.xlsx",
      "file_name": "file.xlsx",
      "file_size": 1024000,
      "modified_time": "2024-01-01T12:00:00Z",
      "created_time": "2024-01-01T10:00:00Z",
      "extension": ".xlsx"
    }
  ],
  "supported_extensions": [".xlsx", ".xls", ".xlsm", ".xlsb"]
}
```

### 2. `read_excel_data`
Excel 파일의 데이터를 JSON으로 읽어옵니다.

**매개변수**:
- `file_path` (필수): Excel 파일의 절대 경로
- `worksheet_name` (선택): 읽을 워크시트 이름 (기본값: 첫 번째 워크시트)
- `max_rows` (선택): 읽을 최대 행 수 (기본값: 모든 행)

**반환값**:
```json
{
  "success": true,
  "file_path": "/path/to/file.xlsx",
  "worksheet_name": "Sheet1",
  "headers": ["Column1", "Column2", "Column3"],
  "rows": [
    ["Value1", "Value2", "Value3"],
    ["Value4", "Value5", "Value6"]
  ],
  "row_count": 2,
  "column_count": 3,
  "data_types": {
    "Column1": "object",
    "Column2": "int64",
    "Column3": "float64"
  }
}
```

### 3. `search_in_excel`
Excel 파일 내에서 특정 텍스트를 검색합니다.

**매개변수**:
- `file_path` (필수): Excel 파일의 절대 경로
- `search_term` (필수): 검색할 텍스트
- `worksheet_name` (선택): 검색할 워크시트 이름
- `case_sensitive` (선택): 대소문자 구분 여부 (기본값: false)

**반환값**:
```json
{
  "success": true,
  "file_path": "/path/to/file.xlsx",
  "worksheet_name": "Sheet1",
  "search_term": "검색어",
  "case_sensitive": false,
  "total_matches": 3,
  "matches": [
    {
      "row": 1,
      "column": "Column1",
      "column_index": 0,
      "value": "검색어가 포함된 값",
      "cell_address": "A1"
    }
  ]
}
```

## 📁 샘플 데이터

프로젝트에는 다양한 종류의 Excel 파일 샘플이 포함되어 있습니다:  
from U.S Data.gov - https://catalog.data.gov/dataset/?q=excel

### 농업 데이터
- **과일 데이터**: `Apples-2022.xlsx`, `Avocados-2022.xlsx`, `Grapes-2022.xlsx` 등
- **채소 데이터**: `Carrots-2020.xlsx`, `Tomatoes-2020.xlsx`, `Broccoli-2020.xlsx` 등
- **곡물 데이터**: `Black_beans-2020.xlsx`, `Corn_sweet-2020.xlsx` 등

### 정부/공공 데이터
- **교육 데이터**: `SCH-0009-Limited-English-Proficient-Students-by-state.xlsx`
- **농업 통계**: `BiotechCropsAllTables2024.xlsx`
- **무역 데이터**: `FoodImports.xlsx`, `hts_2025_revision_22_xls.xlsx`

### 과학/연구 데이터
- **조류 모니터링**: `NCRN LAND Bird Monitoring Data 2007 - 2017_Public.xlsx`
- **농업 생산량**: `monsumtable.xlsx`, `vegtot.xlsx`

### 레거시 파일
- **구형 Excel 파일**: `ELGL 2010 SH 042417.xls`, `FRVI 2010 SH 042417.xls`

이 샘플 데이터들은 다양한 Excel 파일 형식과 데이터 구조를 테스트하는 데 사용할 수 있습니다.

## 🔧 사용 예제

### 기본 사용법

1. **Excel 파일 목록 조회**:
   ```
   list_excel_files 도구를 사용하여 작업 디렉토리의 모든 Excel 파일을 찾습니다.
   ```

2. **특정 파일 데이터 읽기**:
   ```
   read_excel_data 도구를 사용하여 특정 Excel 파일의 내용을 JSON으로 변환합니다.
   ```

3. **파일 내 텍스트 검색**:
   ```
   search_in_excel 도구를 사용하여 Excel 파일 내에서 특정 텍스트를 검색합니다.
   ```

### 고급 사용법

- **대용량 파일 처리**: `max_rows` 매개변수를 사용하여 메모리 사용량을 제한합니다.
- **특정 워크시트 접근**: `worksheet_name` 매개변수로 원하는 워크시트만 읽습니다.
- **대소문자 구분 검색**: `case_sensitive` 매개변수로 정확한 검색을 수행합니다.

## 🔒 보안 고려사항

- **작업 디렉토리 제한**: 설정된 작업 디렉토리 외부의 파일 접근을 차단합니다.
- **파일 크기 제한**: 대용량 파일로 인한 메모리 부족을 방지합니다.
- **권한 검증**: 파일 접근 권한을 확인하여 보안을 강화합니다.
- **경로 조작 방지**: 상대 경로 공격을 방지합니다.

## 🧪 테스트

```bash
# 단위 테스트 실행
pytest tests/test_simple.py

# 통합 테스트 실행
pytest tests/test_integration.py

# 모든 테스트 실행
pytest tests/
```
