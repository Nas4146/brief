# Example Python FastAPI Project

This is an example project showing how Brief works with a Python/FastAPI application.

## Project Structure

```
python-project/
├── AGENTS.md                          # Custom agent behaviors
├── CLAUDE.md                          # Claude instructions
├── .github/
│   └── copilot-instructions.md       # Copilot instructions
├── main.py                            # FastAPI application
├── requirements.txt                   # Dependencies
└── tests/
    └── test_main.py                   # Tests
```

## Usage

```bash
# Initialize brief
brief init

# Add an instruction
brief update "Always add type hints to function signatures"

# Validate
brief validate

# List files
brief list
```

## Expected Output

```
📋 Instruction files in: python-project
   ✅ AGENTS.md (1,234 bytes)
   ✅ CLAUDE.md (987 bytes)
   ✅ .github/copilot-instructions.md (1,456 bytes)
📊 Total: 3 file(s)
```
