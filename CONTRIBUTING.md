# Contributing to Excel Search MCP

Thank you for your interest in contributing to Excel Search MCP! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/msaltnet/excel-search-mcp.git`
3. Create a feature branch: `git checkout -b feature/amazing-feature`
4. Install dependencies: `pip install -r requirements.txt`
5. Install development dependencies: `pip install -e ".[dev]"`

## 🧪 Testing

Before submitting a pull request, please ensure:

1. All tests pass: `pytest tests/`
2. Code follows style guidelines: `black src/ tests/` and `isort src/ tests/`
3. No linting errors: `flake8 src/ tests/`
4. Type checking passes: `mypy src/`

## 📝 Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting
- Use isort for import sorting
- Add type hints to all functions
- Write comprehensive docstrings

## 🔧 Development Setup

### Prerequisites

- Python 3.8 or higher
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/msaltnet/excel-search-mcp.git
cd excel-search-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## 📋 Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation if needed
6. Submit a pull request with a clear description

## 🐛 Bug Reports

When reporting bugs, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages (if any)

## 💡 Feature Requests

For feature requests, please:

- Describe the feature clearly
- Explain the use case
- Consider backward compatibility
- Provide examples if possible

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.
