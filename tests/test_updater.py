"""
Tests for updater module.
"""

import tempfile
from pathlib import Path

from brief.updater import (
    update_instruction_files,
    generate_diff,
    _instruction_exists,
    _find_best_section,
    _contextualize_instruction,
)


def test_contextualize_instruction_with_language():
    """Test instruction contextualization with language info."""
    instruction = "Use type hints"
    context = {"languages": ["Python"]}
    
    result = _contextualize_instruction(instruction, context)
    assert "Python" in result
    assert "Use type hints" in result


def test_contextualize_instruction_with_test_framework():
    """Test instruction contextualization with test framework."""
    instruction = "Run tests before committing"
    context = {"languages": ["Python"], "test_framework": "pytest"}
    
    result = _contextualize_instruction(instruction, context)
    assert "pytest" in result


def test_instruction_exists_exact_match():
    """Test duplicate detection with exact match."""
    content = """
    # Instructions
    - Run tests before committing
    - Use type hints
    """
    
    assert _instruction_exists(content, "Run tests before committing")
    assert not _instruction_exists(content, "Write documentation")


def test_instruction_exists_fuzzy_match():
    """Test duplicate detection with similar match."""
    content = """
    # Instructions
    - Always run pytest tests before you commit code
    """
    
    # Should match with significant word overlap
    assert _instruction_exists(content, "Always run pytest tests before you commit")
    # Should not match if words are very different
    assert not _instruction_exists(content, "write documentation for functions")


def test_find_best_section_testing():
    """Test section selection for testing instruction."""
    content = """
    # Project Instructions
    
    ## Development Workflow
    
    Some workflow info.
    
    ## Testing
    
    Test instructions here.
    
    ## Code Style
    
    Style guidelines.
    """
    
    instruction = "Run pytest before committing"
    section = _find_best_section(content, instruction, {})
    
    assert section is not None
    assert "Testing" in section or "Workflow" in section


def test_update_instruction_files_basic():
    """Test basic instruction file update."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        
        # Create a simple instruction file
        agents_file = project_path / "AGENTS.md"
        agents_file.write_text("""# Agent Instructions

## Development Workflow

- Existing instruction

## Code Style

- Use consistent formatting
""")
        
        # Update with a new instruction
        context = {"languages": ["Python"], "test_framework": "pytest"}
        instruction = "Run tests before committing"
        
        updates = update_instruction_files(
            [agents_file],
            instruction,
            context,
            preview=False
        )
        
        # Check that file was updated
        assert len(updates) == 1
        old_content, new_content, was_updated = updates[agents_file]
        assert was_updated
        assert instruction in new_content
        assert "Development Workflow" in new_content
        
        # Verify file was actually written
        updated_content = agents_file.read_text()
        assert instruction in updated_content


def test_update_instruction_files_duplicate_prevention():
    """Test that duplicate instructions are not added."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        
        # Create file with existing instruction
        agents_file = project_path / "AGENTS.md"
        agents_file.write_text("""# Agent Instructions

- Run tests before committing
""")
        
        context = {}
        instruction = "Run tests before committing"
        
        updates = update_instruction_files(
            [agents_file],
            instruction,
            context,
            preview=False
        )
        
        # Should not update (duplicate)
        old_content, new_content, was_updated = updates[agents_file]
        assert not was_updated
        assert old_content == new_content


def test_update_creates_additional_instructions_section():
    """Test that Additional Instructions section is created if needed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        
        # Create minimal file
        agents_file = project_path / "AGENTS.md"
        agents_file.write_text("# Agent Instructions\n")
        
        context = {}
        instruction = "New instruction"
        
        updates = update_instruction_files(
            [agents_file],
            instruction,
            context,
            preview=False
        )
        
        old_content, new_content, was_updated = updates[agents_file]
        assert was_updated
        assert "## Additional Instructions" in new_content
        assert instruction in new_content


def test_generate_diff():
    """Test diff generation."""
    old_content = """Line 1
Line 2
Line 3
"""
    
    new_content = """Line 1
Line 2 modified
Line 3
Line 4 added
"""
    
    diff = generate_diff(old_content, new_content, Path("test.md"))
    
    assert "test.md" in diff
    assert "-Line 2" in diff or "Line 2" in diff
    assert "+Line 2 modified" in diff or "Line 2 modified" in diff
    assert "+Line 4 added" in diff or "Line 4 added" in diff
