# Claude Project Instructions

You are an expert Python developer working on a FastAPI application.

## Project Overview

This is a FastAPI web application with the following structure:
- `main.py` - Main application entry point
- `tests/` - Test suite using pytest

## Key Principles

1. **Type Safety**: Always add type hints to function signatures
2. **Testing First**: Run tests before committing (`pytest`)
3. **Async Preferred**: Use `async def` for FastAPI route handlers
4. **Clean Code**: Follow PEP 8 and use Black for formatting

## When Editing Code

- Add type hints to all new functions
- Write tests for new functionality
- Use async/await for I/O operations
- Document complex logic with comments
- Update docstrings when changing function behavior

## Testing

- Run `pytest` to execute all tests
- Maintain or improve test coverage
- Write both unit tests and integration tests
- Mock external dependencies in tests
- Always validate input parameters
- Mock external API calls in tests



## Common Patterns

### FastAPI Route Example
```python
from fastapi import FastAPI, HTTPException
from typing import List

@app.get("/items", response_model=List[Item])
async def get_items() -> List[Item]:
    """Retrieve all items."""
    return await db.fetch_all_items()
```

### Error Handling
```python
try:
    result = await perform_operation()
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

## Questions to Ask

- Does this need to be async?
- Do I have type hints?
- Are there tests for this?
- Is the error handling clear?
