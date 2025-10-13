# Excel Search MCP

A Model Context Protocol (MCP) server for searching and reading Excel files from your local PC

[한국어 문서](README_ko.md) | [English Documentation](README.md)

## 📋 Project Overview

This project provides a Model Context Protocol (MCP) server that enables AI models to search and read Excel files from your local PC. It allows AI clients supporting MCP (such as Claude Desktop, Cursor) to directly search and analyze Excel files through a standardized interface.

## 🎯 Key Features

- **Excel File Search**: Recursively search for Excel files in specified directories
- **File Metadata**: Provide comprehensive metadata including file paths, sizes, modification dates
- **Data Extraction**: Convert Excel file contents to JSON format for AI consumption
- **Text Search**: Search for specific text within Excel files
- **Multi-worksheet Support**: Handle multiple worksheets and individual worksheet access
- **Security Controls**: Restrict file access through work directory limitations

## 🏗️ Architecture

### System Diagram
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

### Core Components

1. **MCP Server Core** (`src/server.py`)
   - MCP protocol implementation
   - Client communication management
   - Request/response handling

2. **Excel Processor** (`src/excel_processor.py`)
   - Excel file reading/parsing
   - Worksheet data extraction
   - JSON conversion logic

3. **File Scanner** (`src/file_scanner.py`)
   - Recursive directory scanning
   - Excel file filtering
   - File metadata collection

4. **Config Manager** (`src/config_manager.py`)
   - Configuration file management
   - Security policy enforcement
   - Work directory restrictions

## 🛠️ Technology Stack

- **Language**: Python 3.8+
- **MCP Framework**: mcp (Model Context Protocol)
- **Excel Processing**: openpyxl, pandas
- **File System**: pathlib, os
- **Data Conversion**: json
- **Logging**: logging
- **Testing**: pytest

## 📁 Project Structure

```
excel-search-mcp/
├── src/
│   ├── __init__.py
│   ├── server.py              # MCP server main
│   ├── excel_processor.py     # Excel file processing
│   ├── file_scanner.py        # File scanning
│   ├── config_manager.py      # Configuration management
│   └── data_formatter.py      # Data formatting
├── tests/
│   ├── test_server.py
│   ├── test_simple.py
│   └── test_integration.py
├── examples/
│   ├── sample_excel_files/
│   └── usage_examples.py
├── sample/                    # Sample Excel files
├── requirements.txt
├── pyproject.toml
├── config.json               # Configuration file
└── README.md
```

## 🚀 Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Settings

Create a `config.json` file to set your work directory:

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

### 3. MCP Client Configuration

#### Claude Desktop Configuration (`claude_desktop_config.json`)
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

#### Cursor Configuration (`cursor_mcp_config.json`)
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

## 📊 Available Tools

### 1. `list_excel_files`
Returns a list of Excel files in the specified directory.

**Parameters**: None (uses work_directory from config file)

**Return Value**:
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
Reads Excel file data and converts it to JSON format.

**Parameters**:
- `file_path` (required): Absolute path to the Excel file
- `worksheet_name` (optional): Name of worksheet to read (default: first worksheet)
- `max_rows` (optional): Maximum number of rows to read (default: all rows)

**Return Value**:
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
Searches for specific text within Excel files.

**Parameters**:
- `file_path` (required): Absolute path to the Excel file
- `search_term` (required): Text to search for
- `worksheet_name` (optional): Specific worksheet to search
- `case_sensitive` (optional): Whether search should be case sensitive (default: false)

**Return Value**:
```json
{
  "success": true,
  "file_path": "/path/to/file.xlsx",
  "worksheet_name": "Sheet1",
  "search_term": "search term",
  "case_sensitive": false,
  "total_matches": 3,
  "matches": [
    {
      "row": 1,
      "column": "Column1",
      "column_index": 0,
      "value": "value containing search term",
      "cell_address": "A1"
    }
  ]
}
```

## 📁 Sample Data

The project includes various types of Excel file samples:  
from U.S Data.gov - https://catalog.data.gov/dataset/?q=excel

### Agricultural Data
- **Fruit Data**: `Apples-2022.xlsx`, `Avocados-2022.xlsx`, `Grapes-2022.xlsx`, etc.
- **Vegetable Data**: `Carrots-2020.xlsx`, `Tomatoes-2020.xlsx`, `Broccoli-2020.xlsx`, etc.
- **Grain Data**: `Black_beans-2020.xlsx`, `Corn_sweet-2020.xlsx`, etc.

### Government/Public Data
- **Education Data**: `SCH-0009-Limited-English-Proficient-Students-by-state.xlsx`
- **Agricultural Statistics**: `BiotechCropsAllTables2024.xlsx`
- **Trade Data**: `FoodImports.xlsx`, `hts_2025_revision_22_xls.xlsx`

### Scientific/Research Data
- **Bird Monitoring**: `NCRN LAND Bird Monitoring Data 2007 - 2017_Public.xlsx`
- **Agricultural Production**: `monsumtable.xlsx`, `vegtot.xlsx`

### Legacy Files
- **Legacy Excel Files**: `ELGL 2010 SH 042417.xls`, `FRVI 2010 SH 042417.xls`

These sample datasets can be used to test various Excel file formats and data structures.

## 🔧 Usage Examples

### Basic Usage

1. **List Excel Files**:
   ```
   Use the list_excel_files tool to find all Excel files in the work directory.
   ```

2. **Read Specific File Data**:
   ```
   Use the read_excel_data tool to convert specific Excel file contents to JSON.
   ```

3. **Search Text in Files**:
   ```
   Use the search_in_excel tool to search for specific text within Excel files.
   ```

### Advanced Usage

- **Large File Handling**: Use the `max_rows` parameter to limit memory usage
- **Specific Worksheet Access**: Use the `worksheet_name` parameter to read only desired worksheets
- **Case-Sensitive Search**: Use the `case_sensitive` parameter for precise searching

## 🔒 Security Considerations

- **Work Directory Restrictions**: Blocks access to files outside the configured work directory
- **File Size Limits**: Prevents memory exhaustion from large files
- **Permission Validation**: Verifies file access permissions for enhanced security
- **Path Traversal Prevention**: Protects against relative path attacks

## 🧪 Testing

```bash
# Run unit tests
pytest tests/test_simple.py

# Run integration tests
pytest tests/test_integration.py

# Run all tests
pytest tests/
```

## 📈 Performance Characteristics

- **File Search**: Under 5 seconds for 1000 files
- **Excel Reading**: Under 3 seconds for 10MB files
- **Memory Usage**: Typically under 100MB
- **Supported Formats**: .xlsx, .xls, .xlsm, .xlsb

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

If you encounter any issues or have questions, please create an issue.