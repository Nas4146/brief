"""
Basic tests for context module.
"""

import tempfile
from pathlib import Path

from brief.context import analyze_project_context


def test_python_project_detection():
    """Test detection of Python project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        
        # Create Python files
        (project_path / "main.py").write_text("print('hello')")
        (project_path / "requirements.txt").write_text("click==8.0.0")
        
        context = analyze_project_context(project_path)
        
        assert "Python" in context["languages"]
        assert context["package_manager"] == "pip"


def test_javascript_project_detection():
    """Test detection of JavaScript project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        
        # Create JS files and package.json
        (project_path / "index.js").write_text("console.log('hello');")
        (project_path / "package.json").write_text('{"name": "test", "dependencies": {"react": "^18.0.0"}}')
        
        context = analyze_project_context(project_path)
        
        assert "JavaScript" in context["languages"]
        assert context["package_manager"] == "npm"
        assert "React" in context["frameworks"]


def test_test_framework_detection():
    """Test detection of testing frameworks."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        
        # Create Python project with pytest
        (project_path / "main.py").write_text("def hello(): pass")
        (project_path / "requirements.txt").write_text("pytest>=7.0.0")  # Add this to trigger pip detection
        tests_dir = project_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("def test_hello(): pass")
        
        context = analyze_project_context(project_path)
        
        assert context["test_framework"] == "pytest"


def test_empty_project():
    """Test analysis of empty project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        
        context = analyze_project_context(project_path)
        
        assert context["languages"] == []
        assert context["frameworks"] == []
        assert context["test_framework"] is None
