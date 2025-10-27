"""
Validator module - Check instruction files for consistency and issues.

Validates:
- All files have consistent core behaviors
- File paths mentioned in instructions exist
- No conflicting rules
- Valid markdown syntax
"""

from pathlib import Path
from typing import Dict, List, Tuple


def validate_instructions(files: List[Path], project_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate instruction files for consistency and correctness.
    
    Args:
        files: List of instruction file paths to validate
        project_path: Root directory of the project
        
    Returns:
        Tuple of (all_valid: bool, issues: List[str])
    """
    issues = []
    
    if not files:
        issues.append("No instruction files found")
        return False, issues
    
    # Check each file exists and is readable
    for file_path in files:
        if not file_path.exists():
            issues.append(f"File not found: {file_path}")
            continue
        
        try:
            content = file_path.read_text()
            
            # Validate markdown syntax (basic check)
            if not _is_valid_markdown(content):
                issues.append(f"Invalid markdown in: {file_path.name}")
            
            # Check for referenced file paths
            invalid_paths = _check_referenced_paths(content, project_path)
            if invalid_paths:
                issues.append(f"Invalid paths in {file_path.name}: {', '.join(invalid_paths)}")
            
        except OSError as e:
            issues.append(f"Cannot read {file_path.name}: {e}")
    
    # Check for consistency across files
    # TODO: Implement consistency checks (e.g., same behaviors mentioned)
    
    return len(issues) == 0, issues


def _is_valid_markdown(content: str) -> bool:
    """
    Basic markdown syntax validation.
    
    Args:
        content: File content to validate
        
    Returns:
        True if content appears to be valid markdown
    """
    # Basic checks:
    # - No unclosed code blocks
    # - Headers have proper format
    
    lines = content.split("\n")
    code_block_count = 0
    
    for line in lines:
        if line.strip().startswith("```"):
            code_block_count += 1
    
    # Code blocks should be balanced (even count)
    if code_block_count % 2 != 0:
        return False
    
    return True


def _check_referenced_paths(content: str, project_path: Path) -> List[str]:
    """
    Check if file paths mentioned in content actually exist.
    
    Args:
        content: File content to check
        project_path: Root directory of the project
        
    Returns:
        List of invalid paths found
    """
    invalid = []
    
    # Look for common path patterns
    # Example: "in `src/utils.py`" or "see tests/"
    import re
    
    # Match backtick-enclosed paths
    path_pattern = r'`([a-zA-Z0-9_./\-]+)`'
    matches = re.findall(path_pattern, content)
    
    for match in matches:
        # Check if it looks like a file path (has extension or directory)
        if "/" in match or "." in match:
            path = project_path / match
            if not path.exists():
                invalid.append(match)
    
    return invalid


def get_consistency_score(files: List[Path]) -> float:
    """
    Calculate a consistency score across instruction files.
    
    Args:
        files: List of instruction files to analyze
        
    Returns:
        Consistency score between 0.0 and 1.0
    """
    # TODO: Implement consistency scoring
    # Compare instruction patterns across files
    
    return 1.0  # Placeholder
