"""
Discovery module - Find AI assistant instruction files in a project.

Automatically discovers instruction files for:
- AGENTS.md (custom agent behaviors)
- CLAUDE.md (Claude Project instructions)
- .github/copilot-instructions.md (GitHub Copilot)
- .cursorrules (Cursor IDE)
"""

from pathlib import Path
from typing import List


# Standard instruction file patterns to search for
INSTRUCTION_FILE_PATTERNS = [
    "AGENTS.md",
    "CLAUDE.md",
    ".clinerules",
    ".cursorrules",
    ".github/copilot-instructions.md",
]


def discover_instruction_files(project_path: Path) -> List[Path]:
    """
    Discover AI assistant instruction files in a project.
    
    Args:
        project_path: Root directory of the project to search
        
    Returns:
        List of paths to discovered instruction files
    """
    discovered = []
    
    for pattern in INSTRUCTION_FILE_PATTERNS:
        file_path = project_path / pattern
        if file_path.exists() and file_path.is_file():
            discovered.append(file_path)
    
    return discovered


def is_instruction_file(file_path: Path) -> bool:
    """
    Check if a file is a recognized instruction file.
    
    Args:
        file_path: Path to check
        
    Returns:
        True if the file is a recognized instruction file
    """
    # Get relative path from project root (if possible)
    try:
        # Check if any standard pattern matches
        for pattern in INSTRUCTION_FILE_PATTERNS:
            if file_path.name == Path(pattern).name:
                return True
            # Check full path match for nested files like .github/copilot-instructions.md
            if str(file_path).endswith(pattern):
                return True
    except (ValueError, OSError):
        pass
    
    return False


def get_file_type(file_path: Path) -> str:
    """
    Determine the type of instruction file.
    
    Args:
        file_path: Path to the instruction file
        
    Returns:
        File type identifier (e.g., "agents", "claude", "copilot", "cursor")
    """
    name = file_path.name.lower()
    
    if name == "agents.md":
        return "agents"
    elif name == "claude.md" or name == ".clinerules":
        return "claude"
    elif name == "copilot-instructions.md":
        return "copilot"
    elif name == ".cursorrules":
        return "cursor"
    else:
        return "unknown"
