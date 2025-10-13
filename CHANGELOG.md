# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Smithery marketplace integration
- GitHub Actions CI/CD pipeline
- Comprehensive documentation updates

## [0.9.0] - 2025-10-13

### Added
- Initial release of Excel Search MCP server
- Excel file search functionality
- Multi-worksheet support
- Text search within Excel files
- JSON data conversion
- Security controls and access restrictions
- Support for .xlsx, .xls, .xlsm, .xlsb formats
- Comprehensive file metadata
- Configuration management
- Sample data
- Unit tests

### Features
- `list_excel_files`: Search for Excel files in directories
- `read_excel_data`: Convert Excel data to JSON format
- `search_in_excel`: Search for text within Excel files

### Security
- Work directory restrictions
- File size limits
- Permission validation
- Path traversal prevention
