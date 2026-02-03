# Contributing to NASA ADS Metadata Retriever

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Welcome all suggestions and constructive criticism
- Focus on collaboration and improvement

## Getting Started

### 1. Fork and Clone

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/your-username/NASA-ADS-metadata-retriever.git
cd NASA-ADS-metadata-retriever
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### 3. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

## Development Workflow

### Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines
- Use [Black](https://github.com/psf/black) for code formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting

```bash
# Format code
black .
isort .

# Check style
flake8 nasa_ads/ tests/
```

### Type Hints

- Add type hints to all function signatures
- Use type hints for class attributes
- Use `typing` module for complex types

```python
from typing import List, Optional, Dict, Any

def search(self, query: Query) -> Results:
    """Search for papers."""
    pass
```

### Documentation

- Write docstrings for all modules, classes, and functions
- Use Google-style docstrings
- Include examples for complex functionality

```python
def example_function(param: str, count: int = 10) -> List[str]:
    """
    Brief description of function.

    Longer description if needed.

    Args:
        param: Description of param
        count: Description of count (default: 10)

    Returns:
        List of processed strings

    Raises:
        ValueError: If param is empty

    Example:
        >>> result = example_function("test", count=5)
        >>> len(result)
        5
    """
    pass
```

### Testing

Write tests for all new functionality:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api_client.py

# Run with coverage
pytest --cov=nasa_ads

# Run specific test
pytest tests/test_models.py::TestPaper::test_create_paper_valid
```

Test file structure:

```python
import pytest

class TestMyFeature:
    """Tests for my feature."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        # Arrange
        # Act
        # Assert
        pass
    
    def test_error_handling(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            # Code that should raise
            pass
```

## Submitting Changes

### 1. Write Descriptive Commits

```bash
git commit -m "Add support for BibTeX export

- Implement BibTeXFormatter class
- Add BibTeX export to CLI
- Add tests for BibTeX formatter
- Update README with BibTeX examples"
```

### 2. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 3. Create Pull Request

- Provide clear description of changes
- Reference any related issues
- Include examples if applicable
- Ensure all tests pass

### PR Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass (`pytest`)
- [ ] Code is properly documented
- [ ] Type hints are present
- [ ] CHANGELOG.md is updated (if applicable)
- [ ] README.md is updated (if applicable)

## Adding Features

### New Output Formatter

1. Create class inheriting from `Formatter`
2. Implement `format()` and `save()` methods
3. Add to `get_formatter()` function
4. Write tests in `test_formatters.py`
5. Update README with example

### New Validator

1. Create function in `utils/validators.py`
2. Raise `ValidationError` on invalid input
3. Add tests to `test_validators.py`
4. Update type hints and docstrings

### New CLI Command

1. Create function in `cli.py`
2. Add subparser with arguments
3. Set function as default handler
4. Add help text and examples
5. Test manually with CLI

## Documentation

### README Updates

- Update examples if changing API
- Document new features
- Add to table of contents if needed

### Docstring Format

Use Google-style docstrings:

```python
def my_function(param1: str, param2: int) -> bool:
    """
    Brief description.

    Longer description explaining the function in more detail,
    including edge cases and important notes.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: If param1 is empty
        TypeError: If param2 is not an integer

    Example:
        >>> my_function("test", 5)
        True
    """
    pass
```

## Reporting Issues

### Bug Reports

Include:
- Python version
- Package version
- OS and environment
- Minimal reproducible example
- Expected vs actual behavior

### Feature Requests

Include:
- Use case and motivation
- Proposed API/interface
- Potential alternatives
- Links to related issues

## Questions?

- Check [GitHub Issues](https://github.com/deepakdeo/NASA-ADS-metadata-retriever/issues)
- Start a [GitHub Discussion](https://github.com/deepakdeo/NASA-ADS-metadata-retriever/discussions)
- Review [API Reference](README.md#api-reference)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
