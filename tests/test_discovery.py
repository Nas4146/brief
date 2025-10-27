"""
Basic tests for discovery module.
"""

import tempfile
from pathlib import Path

from brief.discovery import discover_instruction_files, is_instruction_file, get_file_type


def test_discover_agents_md():
    """Test discovery of AGENTS.md file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        agents_file = project_path / "AGENTS.md"
        agents_file.write_text("# Agent Instructions")
        
        discovered = discover_instruction_files(project_path)
        assert len(discovered) == 1
        assert discovered[0].name == "AGENTS.md"


def test_discover_multiple_files():
    """Test discovery of multiple instruction files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        
        # Create multiple instruction files
        (project_path / "AGENTS.md").write_text("# Agents")
        (project_path / "CLAUDE.md").write_text("# Claude")
        
        github_dir = project_path / ".github"
        github_dir.mkdir()
        (github_dir / "copilot-instructions.md").write_text("# Copilot")
        
        discovered = discover_instruction_files(project_path)
        assert len(discovered) == 3
        
        names = {f.name for f in discovered}
        assert "AGENTS.md" in names
        assert "CLAUDE.md" in names
        assert "copilot-instructions.md" in names


def test_discover_empty_directory():
    """Test discovery in directory with no instruction files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        discovered = discover_instruction_files(project_path)
        assert len(discovered) == 0


def test_is_instruction_file():
    """Test instruction file recognition."""
    assert is_instruction_file(Path("AGENTS.md"))
    assert is_instruction_file(Path("CLAUDE.md"))
    assert is_instruction_file(Path(".cursorrules"))
    assert is_instruction_file(Path(".github/copilot-instructions.md"))
    assert not is_instruction_file(Path("README.md"))
    assert not is_instruction_file(Path("random.txt"))


def test_get_file_type():
    """Test file type detection."""
    assert get_file_type(Path("AGENTS.md")) == "agents"
    assert get_file_type(Path("CLAUDE.md")) == "claude"
    assert get_file_type(Path(".cursorrules")) == "cursor"
    assert get_file_type(Path(".github/copilot-instructions.md")) == "copilot"
    assert get_file_type(Path("unknown.md")) == "unknown"
