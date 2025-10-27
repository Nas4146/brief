# 🤖 Brief

**Brief your AI coding assistants once, update them all.**

[![PyPI](https://img.shields.io/pypi/v/ai-brief)](https://pypi.org/project/ai-brief/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## The Problem

You're using Claude Projects, GitHub Copilot, and Cursor. You want them all to follow your project's conventions:

- ✅ Run tests before committing
- ✅ Update docs after code changes  
- ✅ Follow your team's architectural patterns

But maintaining 3+ instruction files manually is tedious and error-prone.

## The Solution

```bash
pip install ai-brief

# One command updates all your AI assistants
brief update "Run pytest before committing any code"

# ✅ .github/copilot-instructions.md updated
# ✅ CLAUDE.md updated
# ✅ AGENTS.md updated
# ✅ .cursorrules updated
```

---

## Installation

```bash
# CLI only (recommended for most users)
pip install ai-brief

# CLI + MCP server (for AI assistant integration)
pip install 'ai-brief[mcp]'

# Or install from source
git clone https://github.com/Nas4146/brief.git
cd brief
pip install -e .              # CLI only
pip install -e '.[mcp]'       # CLI + MCP
```

**Requirements:** Python 3.9+

**Dependencies**: Minimal!
- **Core** (always installed):
  - `click>=8.0.0` - CLI framework
  - `pyyaml>=6.0.0` - Config file support
  - `rich>=13.0.0` - Beautiful terminal output
- **Optional** (only if you want MCP):
  - `mcp>=0.1.0` - Model Context Protocol support

**Install what you need:**
- Just want the CLI? → `pip install ai-brief`
- Want AI assistants to use Brief? → `pip install 'ai-brief[mcp]'`

---

## Quick Start

```bash
# 1. Navigate to your project
cd your-project

# 2. Initialize brief (discovers existing instruction files)
brief init
# ╭───────────────────╮
# │ Initializing brief│
# │ your-project      │
# ╰───────────────────╯
# 
# Found 3 instruction files:
# ✓ AGENTS.md
# ✓ CLAUDE.md
# ✓ .github/copilot-instructions.md

# 3. Add an instruction
brief update "Always use async/await for database calls"
# Preview changes with color-coded diffs
# Confirm with y/n

# 4. Validate everything is consistent
brief validate
# ✅ All instruction files are consistent!

# 5. List all instruction files
brief list
# Displays table with files and sizes
```

---

## Features

- 🔍 **Auto-discovery** - Finds all instruction files automatically
- 🧠 **Context-aware** - Understands your project structure and conventions
- ✅ **Validation** - Ensures consistency across all files
- 🎯 **Zero config** - Works out of the box, customizable when needed
- 🪶 **Lightweight** - Minimal dependencies (Click + PyYAML + Rich)
- ✨ **Beautiful UI** - Professional terminal output with tables, panels, and color coding
- 🔒 **Duplicate prevention** - Fuzzy matching prevents redundant instructions
- 👀 **Preview mode** - See exactly what changes before applying
- 🤖 **MCP Support** - AI assistants can update their own instructions via Model Context Protocol

---

## MCP Server (Optional)

Brief includes an **optional** MCP server that lets AI assistants update their own instruction files.

**Note**: MCP support is completely optional. The CLI works perfectly without it!

### Installation

```bash
# Install Brief with MCP support
pip install 'ai-brief[mcp]'
```

### Configuration

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "brief": {
      "command": "brief-mcp"
    }
  }
}
```

**Don't use AI assistants with Brief?** Skip this section! The CLI works independently.

See [docs/MCP_SERVER.md](docs/MCP_SERVER.md) for full MCP documentation.

---

## Supported Files

Brief automatically discovers and updates these instruction files:

| File | Tool |
|------|------|
| `AGENTS.md` | Custom agent instructions |
| `CLAUDE.md` | Claude Projects |
| `.clinerules` | Cline (VS Code extension) |
| `.github/copilot-instructions.md` | GitHub Copilot |
| `.cursorrules` | Cursor IDE |

---

## Commands

### `brief init`

Initialize brief in your project. Discovers existing instruction files and analyzes project structure.

```bash
brief init

# Output:
# 🚀 Initializing brief in /Users/you/project
# 📝 Scanning for instruction files...
# ✅ Found 3 instruction file(s):
#    • AGENTS.md
#    • CLAUDE.md
#    • .github/copilot-instructions.md
# 🔍 Analyzing project structure...
#    Languages: Python, TypeScript
#    Frameworks: FastAPI, React
# ✅ Configuration file ready: .brief.yaml
```

### `brief update "instruction"`

Add a new instruction to all files with context awareness.

```bash
brief update "Run tests before committing any code"

# Output:
# 📝 Analyzing project: your-project
# ✨ Updating 3 file(s) with context:
#    Languages: Python
#    Test framework: pytest
# 📊 Adding instruction: "Run tests before committing any code"
#    ✅ AGENTS.md
#    ✅ CLAUDE.md
#    ✅ .github/copilot-instructions.md
```

### `brief validate`

Check instruction files for consistency and issues.

```bash
brief validate

# Output:
# 🔍 Validating instructions in: your-project
# 📋 Checking 3 file(s)...
# ✅ All instruction files are consistent!
```

### `brief list`

List all discovered instruction files.

```bash
brief list

# Output:
# 📋 Instruction files in: your-project
#    ✅ AGENTS.md (2,456 bytes)
#    ✅ CLAUDE.md (1,832 bytes)
#    ✅ .github/copilot-instructions.md (3,120 bytes)
# 📊 Total: 3 file(s)
```

---

## Use Cases

### For Solo Developers

Keep your personal AI assistant instructions consistent across tools without manual copy-paste.

### For Teams

Onboard new developers faster by baking project conventions into AI tools.

### For Open Source

Help contributors understand your project's workflow through AI assistants.

---

## Project Structure

```
your-project/
├── AGENTS.md                          # Custom instructions
├── CLAUDE.md                          # Claude instructions
├── .github/
│   └── copilot-instructions.md       # Copilot instructions
├── .cursorrules                       # Cursor instructions
├── .brief.yaml                        # Brief config (optional)
└── src/
    └── ...
```

---

## Configuration (Optional)

Brief works with zero configuration, but you can customize behavior with `.brief.yaml`:

```yaml
version: 1

# Instruction files to manage
instruction_files:
  - AGENTS.md
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .cursorrules

# Project metadata
project:
  languages:
    - Python
    - TypeScript
  frameworks:
    - FastAPI
    - React

# Enabled behaviors (coming soon)
behaviors:
  enabled:
    - test_before_commit
    - update_docs_after_changes
```

---

## Development

```bash
# Clone the repository
git clone https://github.com/Nas4146/brief.git
cd brief

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .

# Format code
black .
```

---

## Roadmap

### V0.1 (Current) 
- ✅ CLI with `init`, `update`, `validate`, `list` commands
- ✅ Auto-discovery of instruction files
- ✅ Context-aware updates (language, framework detection)
- ✅ Basic validation

---

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT © 2025

---

## Why "Brief"?

**Brief** (verb): *to give essential information to someone*

Perfect for giving your AI assistants the essential context they need, once, and having it propagate everywhere.

---

## Links

- **GitHub**: [https://github.com/Nas4146/brief](https://github.com/Nas4146/brief)
- **Issues**: [https://github.com/Nas4146/brief/issues](https://github.com/Nas4146/brief/issues)

---

