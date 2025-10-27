# GitHub Copilot Instructions

## Project: FastAPI Application

### Language & Framework
- Python 3.9+
- FastAPI web framework
- pytest for testing

### Code Style
- Follow PEP 8 conventions
- Use Black formatter (line length: 100)
- Add type hints to all functions
- Prefer async/await for I/O operations

### Testing
- Run `pytest` before committing
- Write tests for new features
- Maintain test coverage
- Mock external dependencies

### FastAPI Best Practices
- Use `async def` for route handlers
- Include response models in route decorators
- Handle errors with `HTTPException`
- Add docstrings to all routes

### Common Tasks

#### Creating a new route
```python
@app.get("/endpoint", response_model=ResponseModel)
async def endpoint_name() -> ResponseModel:
    """Brief description of what this endpoint does."""
    # Implementation
    pass
```

#### Error handling
```python
from fastapi import HTTPException

if not valid:
    raise HTTPException(status_code=400, detail="Error message")
```

### Before Committing
1. Run `pytest` - all tests must pass
2. Check type hints are present
3. Verify docstrings are updated
4. Ensure code is formatted with Black
## Additional Instructions

- Always validate input parameters
- Mock external API calls in tests
