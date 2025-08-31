# AtlasMogo Test Suite

This directory contains the test suite for AtlasMogo, organized by application layer.

## Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for layer interactions
├── ui/            # UI tests for presentation layer
└── fixtures/      # Test data and fixtures
```

## Running Tests

### Prerequisites
- Python 3.10+
- pytest
- MongoDB instance running (for integration tests)

### Install Test Dependencies
```bash
pip install pytest pytest-qt pytest-cov
```

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# UI tests only
pytest tests/ui/
```

### Run with Coverage
```bash
pytest --cov=atlasmogo tests/
```

## Test Categories

### Unit Tests
- Test individual functions and methods in isolation
- Mock external dependencies
- Fast execution
- High coverage

### Integration Tests
- Test interactions between layers
- Use real MongoDB connections
- Slower execution
- Test data flow

### UI Tests
- Test PySide6 GUI components
- Use pytest-qt for Qt integration
- Test user interactions
- Verify UI behavior

## Writing Tests

Follow these guidelines:
1. Use descriptive test names
2. Test one behavior per test
3. Use fixtures for common setup
4. Mock external dependencies in unit tests
5. Clean up test data after tests

## Example Test

```python
import pytest
from business.mongo_service import MongoService

def test_mongo_service_initialization():
    """Test that MongoService initializes correctly."""
    service = MongoService()
    assert service is not None
    assert not service.is_connected()
```
