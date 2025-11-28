# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 📐 Project Overview

Excel Search MCP is a Model Context Protocol (MCP) server that enables AI models to search and read Excel files from local PC storage. It provides three main tools:
- `list_excel_files_tool`: Search for Excel files in work directory
- `read_excel_data_tool`: Read and convert Excel data to JSON
- `search_in_excel_tool`: Search for text within Excel files

Built with FastMCP and uses an adapter pattern to support both `openpyxl` (fast, cross-platform) and `win32com` (DRM-protected files, Windows only).

## 🏗️ Architecture

### Adapter Pattern (Core Design)

The system uses an **Adapter Pattern** to support multiple Excel handlers:

```
ExcelProcessor
    ↓ (uses)
ExcelAdapter (Protocol)
    ↓ (implementations)
├── OpenpyxlAdapter (default, fast, cross-platform)
└── Win32Adapter (DRM support, Windows only, slower)
```

**Key principle**: Path-based API (no COM object exposure), returns pure data models (SheetModel).

### Module Structure

```
excel_search_mcp/
├── server.py              # FastMCP server, tool definitions
├── excel_processor.py     # ExcelProcessor class, validation logic
├── file_scanner.py        # Directory scanning, file filtering
├── config_manager.py      # Configuration, security policies
├── data_formatter.py      # Data formatting utilities
└── adapters/
    ├── adapter_base.py    # ExcelAdapter protocol (interface)
    ├── adapter_openpyxl.py # Openpyxl implementation
    ├── adapter_win32.py   # Win32 COM implementation
    └── sheet_model.py     # SheetModel data class
```

### Data Flow

```
MCP Client (Claude/Cursor)
    ↓ (JSON-RPC)
FastMCP Server (server.py)
    ↓ (tool calls)
ExcelProcessor (excel_processor.py)
    ↓ (adapter selection)
ExcelAdapter (OpenpyxlAdapter or Win32Adapter)
    ↓ (file I/O)
Excel Files (.xlsx, .xls, .xlsm, .xlsb)
```

## 🛠️ Development Commands

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -e ".[dev]"
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_server.py -v

# Run specific test class
pytest tests/test_server.py::TestMCPServer -v

# Run specific test function
pytest tests/test_server.py::TestMCPServer::test_call_tool_list_excel_files -v

# Run with coverage
pytest tests/ --cov=excel_search_mcp --cov-report=html --cov-report=term

# Filter tests by keyword
pytest tests/ -k "excel_summary" -v

# Debug mode (verbose output, no capture)
pytest tests/ -v -s --tb=long

# Async tests are auto-detected (asyncio_mode = "auto")
```

### Code Quality

```bash
# Format code (Black)
black excel_search_mcp/ tests/ main.py

# Sort imports (isort)
isort excel_search_mcp/ tests/ main.py

# Lint (flake8)
flake8 excel_search_mcp/ tests/ main.py --ignore=E402

# Type checking (mypy)
mypy excel_search_mcp/

# Pre-commit hooks (runs all checks)
pre-commit install
pre-commit run --all-files
```

### Running the Server

```bash
# Local testing via main.py
python main.py

# Via Smithery CLI (development mode)
dev

# Via Smithery playground
playground
```

## 🔑 Key Patterns & Conventions

### 1. Configuration Management

**Singleton Pattern**: `config_manager` is a global instance in `config_manager.py:129`

```python
from excel_search_mcp.config_manager import config_manager

work_dir = config_manager.get_work_directory()
handler = config_manager.get_excel_handler()  # "openpyxl" or "win32com"
```

**Configuration file**: `config.json` (root directory)
- `work_directory`: Root path for file access (security boundary)
- `excel.handler`: "openpyxl" (default) or "win32com"
- `excel.supported_extensions`: [".xlsx", ".xls", ".xlsm", ".xlsb"]
- `excel.max_file_size_mb`: Maximum file size (default: 100)
- `excel.max_files_per_search`: Search limit (default: 1000)
- `excel.recursive_search`: Enable subdirectory scanning (default: true)

### 2. Security Model

**Work Directory Restriction**: All file access is restricted to `work_directory` via `config_manager.is_path_within_work_directory()` (config_manager.py:94-114)

**Validation**: `ExcelProcessor.validate_file_path()` checks:
- File exists
- Is a file (not directory)
- Within work directory
- Size under limit

**Path Traversal Prevention**: Uses `Path.resolve()` and relative path checks to prevent `../` attacks.

### 3. Adapter Initialization

**Lazy initialization**: Adapter is created in `ExcelProcessor.__init__()` via `_initialize_adapter()` (excel_processor.py:30-48)

**Fallback logic**: If `win32com` is unavailable (ImportError), falls back to `openpyxl`

**Handler selection**:
```python
if handler == "win32com":
    from .adapters.adapter_win32 import Win32Adapter
    self.adapter = Win32Adapter()
else:
    self.adapter = OpenpyxlAdapter()
```

### 4. Data Model

**SheetModel**: Pure data class (sheet_model.py)
```python
@dataclass
class SheetModel:
    values: list[list[Any]]      # 2D array of cell values
    used_range: tuple[int, int]  # (rows, columns)
    merged_regions: list[tuple]  # Merged cell ranges
```

**Tool Response Format**: Always return JSON strings with `ensure_ascii=False`
```python
return json.dumps(result, ensure_ascii=False, indent=2)
```

### 5. Error Handling

**Consistent error format**:
```python
{
    "success": False,
    "error": "Error message",
    "error_code": "ERROR_CODE",  # Optional
    "file_path": "/path/to/file.xlsx"
}
```

**Common error codes** (excel_processor.py:58-116):
- `FILE_NOT_FOUND`
- `NOT_A_FILE`
- `ACCESS_DENIED`
- `FILE_TOO_LARGE`
- `VALIDATION_ERROR`

## 🔧 Adding New Features

### Adding a New Tool

1. **Define tool in server.py**:
```python
@server.tool()
def my_tool(file_path: str, ctx: Context, param: Optional[str] = None) -> str:
    """Tool description for AI clients"""
    try:
        result = my_function(file_path, param)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error in my_tool: {e}")
        return json.dumps(
            {"success": False, "error": f"Tool execution failed: {str(e)}"},
            ensure_ascii=False,
            indent=2,
        )
```

2. **Add implementation** in appropriate module (excel_processor.py, file_scanner.py, etc.)

3. **Add tests** in tests/test_server.py:
```python
class TestMCPServer:
    async def test_call_tool_my_tool(self, server):
        result = await server.call_tool("my_tool", {"file_path": "..."})
        assert result[0].text == ...
```

### Adding a New Adapter

1. **Create adapter file** in `adapters/` (e.g., `adapter_xlrd.py`)

2. **Implement ExcelAdapter protocol**:
```python
from .adapter_base import ExcelAdapter
from .sheet_model import SheetModel

class XlrdAdapter:
    def list_sheets_from_file(self, file_path: str | Path) -> list[str]:
        # Implementation
        pass

    def get_sheet_model_from_file(
        self, file_path: str | Path, sheet_name: str
    ) -> SheetModel:
        # Implementation
        pass

    def shutdown(self) -> None:
        # Cleanup
        pass
```

3. **Add initialization logic** in `ExcelProcessor._initialize_adapter()`:
```python
elif handler == "xlrd":
    from .adapters.adapter_xlrd import XlrdAdapter
    self.adapter = XlrdAdapter()
```

4. **Update config.json** to include new handler option

## 🐛 Common Issues

### "Win32 adapter not available" warning
- **Cause**: `pywin32` not installed or running on non-Windows platform
- **Solution**: Install `pywin32` on Windows, or use `openpyxl` handler (default)

### "File access denied" error
- **Cause**: File path outside work_directory
- **Solution**: Update `config.json` work_directory or move file to allowed location

### "File too large" error
- **Cause**: File exceeds max_file_size_mb limit
- **Solution**: Increase limit in `config.json` or use `max_rows` parameter

### Type checking errors with mypy
- **Cause**: Strict type checking enabled (pyproject.toml:88-101)
- **Solution**: Add proper type hints, use `# type: ignore` sparingly

## 📝 Code Style

- **Line length**: 88 characters (Black default)
- **Import sorting**: isort with Black profile
- **Type hints**: Required for all function signatures (mypy strict mode)
- **Docstrings**: Required for public APIs (classes, functions)
- **Logging**: Use `logger.info()` for important events, `logger.debug()` for verbose info
- **Naming conventions**:
  - Functions/methods: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Private members: `_leading_underscore`

## 🧪 Testing Strategy

### Unit Tests (tests/test_server.py)
- Test each tool independently
- Mock external dependencies (file system, Excel files)
- Focus on edge cases and error handling

### Integration Tests (how-to-test.md)
- Test actual MCP protocol communication
- Use real sample files (sample/ directory)
- Performance benchmarks (< 10ms single file, < 1s for 100 files)

### Test Coverage Target
- **Minimum**: 90% (enforced in CI/CD)
- **Focus areas**: Core logic (ExcelProcessor, adapters), error handling

## 🚀 Deployment

### MCP Client Configuration

**Claude Desktop** (claude_desktop_config.json):
```json
{
  "mcpServers": {
    "excel-search-mcp": {
      "command": "python",
      "args": ["C:/path/to/excel-search-mcp/main.py"],
      "env": {}
    }
  }
}
```

**Cursor** (cursor_mcp_config.json):
```json
{
  "mcpServers": {
    "excel-search-mcp": {
      "command": "python",
      "args": ["C:/path/to/excel-search-mcp/main.py"]
    }
  }
}
```

### Smithery Deployment

Server entry point is defined in `pyproject.toml:50-52`:
```toml
[tool.smithery]
server = "excel_search_mcp.server:create_server"
target = "local"
```

## 📚 Related Documentation

- **README.md**: User-facing documentation (installation, usage, features)
- **README_ko.md**: Korean translation
- **how-to-test.md**: Comprehensive testing guide
- **CONTRIBUTING.md**: Contribution guidelines
- **CHANGELOG.md**: Version history

---

**Last Updated**: 2025-11-28
**Python Version**: 3.10+
**MCP Version**: 1.15.0+
