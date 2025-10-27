# Contributing to Brief

Thank you for your interest in contributing to Brief! 🎉

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, Brief version)

### Suggesting Features

Feature suggestions are welcome! Please open an issue with:
- A clear description of the feature
- Why it would be useful
- Example usage (if applicable)

### Submitting Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clear, concise code
   - Add tests for new functionality
   - Update documentation as needed

4. **Run tests**
   ```bash
   python -m pytest tests/ -v
   ```

5. **Ensure code quality**
   ```bash
   # Format code
   black brief/ tests/
   
   # Run linter
   ruff check brief/ tests/
   ```

6. **Commit your changes**
   ```bash
   git commit -m "feat: add awesome new feature"
   ```
   
   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test changes
   - `refactor:` for code refactoring

7. **Push and create a PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Development Setup

```bash
# Clone the repository
git clone https://github.com/Nas4146/brief.git
cd brief

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e '.[mcp]'

# Install development dependencies
pip install pytest black ruff

# Run tests
python -m pytest tests/ -v
```

## Project Structure

```
brief/
├── brief/              # Source code
│   ├── cli.py         # CLI commands
│   ├── discovery.py   # File discovery
│   ├── context.py     # Project analysis
│   ├── updater.py     # Update logic
│   ├── validator.py   # Validation
│   └── mcp/           # MCP server (optional)
├── tests/             # Test suite
├── docs/              # Documentation
└── examples/          # Example projects
```

## Code Style

- Follow PEP 8
- Use type hints where applicable
- Write docstrings for public functions
- Keep functions focused and small
- Use descriptive variable names

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage
- Test edge cases and error handling

## Documentation

- Update README.md if adding user-facing features
- Update docs/ for detailed documentation
- Add docstrings for new functions/classes
- Update CHANGELOG.md with your changes

## Questions?

Feel free to open an issue for questions or clarifications!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
