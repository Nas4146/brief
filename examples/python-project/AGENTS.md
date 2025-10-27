# Agent Instructions

This file contains custom agent behaviors and instructions for AI coding assistants working on this Python/FastAPI project.

## Project Context

- **Languages**: Python 3.9+
- **Framework**: FastAPI
- **Testing**: pytest
- **Key directories**:
  - `main.py` - FastAPI application entry point
  - `tests/` - Test suite

## Core Behaviors

### behavior_test_before_commit

**When**: Before committing any code changes

**Steps**:
1. Run `pytest` to execute all tests
2. Ensure all tests pass
3. Check test coverage is maintained
4. Only commit if tests are green

### behavior_add_type_hints

**When**: Writing or modifying Python functions

**Steps**:
1. Add type hints to all function parameters
2. Add return type annotations
3. Use `typing` module for complex types
4. Keep hints compatible with Python 3.9+

### behavior_async_routes

**When**: Creating FastAPI route handlers

**Steps**:
1. Prefer `async def` for route handlers
2. Use `await` for I/O operations (database, external APIs)
3. Document async behavior in docstrings
4. Handle exceptions properly with try/except

## Code Style

- Follow PEP 8
- Use Black for formatting (line length: 100)
- Use Ruff for linting
- Maximum line length: 100 characters

## Documentation

- Add docstrings to all public functions
- Include examples in docstrings where helpful
- Update README.md when adding new features
- Keep API documentation in sync with code
## Additional Instructions

- Always validate input parameters
- Mock external API calls in tests
