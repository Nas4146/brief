"""
Context module - Analyze project structure to provide context-aware updates.

Detects:
- Programming languages used
- Frameworks and libraries
- Testing frameworks
- Project structure
"""

from pathlib import Path
from typing import Dict, List, Set


def analyze_project_context(project_path: Path) -> Dict:
    """
    Analyze project structure to understand context.
    
    Args:
        project_path: Root directory of the project
        
    Returns:
        Dictionary with project context information:
        - languages: List of detected programming languages
        - frameworks: List of detected frameworks
        - test_framework: Detected testing framework (if any)
        - package_manager: Detected package manager
        - project_type: Type of project (web, cli, library, etc.)
    """
    context = {
        "languages": [],
        "frameworks": [],
        "test_framework": None,
        "package_manager": None,
        "project_type": None,
    }
    
    # Detect languages by file extensions
    languages = _detect_languages(project_path)
    context["languages"] = list(languages)
    
    # Detect frameworks and tools
    if _has_file(project_path, "requirements.txt") or _has_file(project_path, "pyproject.toml"):
        context["package_manager"] = "pip"
        frameworks = _detect_python_frameworks(project_path)
        context["frameworks"].extend(frameworks)
        
        # Detect test framework
        if _has_file(project_path, "pytest.ini") or _has_directory(project_path, "tests"):
            context["test_framework"] = "pytest"
        elif _has_directory(project_path, "test"):
            context["test_framework"] = "unittest"
    
    if _has_file(project_path, "package.json"):
        context["package_manager"] = "npm"
        frameworks = _detect_js_frameworks(project_path)
        context["frameworks"].extend(frameworks)
        
        # Detect test framework
        package_json = project_path / "package.json"
        if package_json.exists():
            try:
                import json
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                    
                    if "jest" in deps:
                        context["test_framework"] = "jest"
                    elif "vitest" in deps:
                        context["test_framework"] = "vitest"
                    elif "mocha" in deps:
                        context["test_framework"] = "mocha"
            except (json.JSONDecodeError, OSError):
                pass
    
    if _has_file(project_path, "Cargo.toml"):
        context["package_manager"] = "cargo"
        context["test_framework"] = "cargo test"
    
    if _has_file(project_path, "go.mod"):
        context["package_manager"] = "go"
        context["test_framework"] = "go test"
    
    return context


def _detect_languages(project_path: Path, max_depth: int = 3) -> Set[str]:
    """Detect programming languages by file extensions."""
    languages = set()
    
    # Language extension mapping
    extension_map = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".jsx": "JavaScript",
        ".tsx": "TypeScript",
        ".rs": "Rust",
        ".go": "Go",
        ".java": "Java",
        ".rb": "Ruby",
        ".php": "PHP",
        ".swift": "Swift",
        ".kt": "Kotlin",
        ".c": "C",
        ".cpp": "C++",
        ".cs": "C#",
    }
    
    # Walk directory tree (limited depth)
    for path in _walk_files(project_path, max_depth=max_depth):
        ext = path.suffix.lower()
        if ext in extension_map:
            languages.add(extension_map[ext])
    
    return languages


def _detect_python_frameworks(project_path: Path) -> List[str]:
    """Detect Python frameworks."""
    frameworks = []
    
    # Check for common Python frameworks by files/directories
    if _has_file(project_path, "manage.py"):
        frameworks.append("Django")
    
    if _has_directory(project_path, "app") or _has_file(project_path, "app.py"):
        # Could be Flask or FastAPI
        if _has_import_in_python_files(project_path, "fastapi"):
            frameworks.append("FastAPI")
        elif _has_import_in_python_files(project_path, "flask"):
            frameworks.append("Flask")
    
    return frameworks


def _detect_js_frameworks(project_path: Path) -> List[str]:
    """Detect JavaScript/TypeScript frameworks."""
    frameworks = []
    
    # Check package.json dependencies
    package_json = project_path / "package.json"
    if package_json.exists():
        try:
            import json
            with open(package_json) as f:
                data = json.load(f)
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                
                if "react" in deps:
                    frameworks.append("React")
                if "next" in deps:
                    frameworks.append("Next.js")
                if "vue" in deps:
                    frameworks.append("Vue")
                if "svelte" in deps:
                    frameworks.append("Svelte")
                if "express" in deps:
                    frameworks.append("Express")
                if "@nestjs/core" in deps:
                    frameworks.append("NestJS")
        except (json.JSONDecodeError, OSError):
            pass
    
    return frameworks


def _has_file(project_path: Path, filename: str) -> bool:
    """Check if a file exists in the project."""
    return (project_path / filename).exists()


def _has_directory(project_path: Path, dirname: str) -> bool:
    """Check if a directory exists in the project."""
    return (project_path / dirname).is_dir()


def _has_import_in_python_files(project_path: Path, module_name: str, max_files: int = 10) -> bool:
    """Check if a Python module is imported in any Python files."""
    checked = 0
    for py_file in project_path.rglob("*.py"):
        if checked >= max_files:
            break
        
        try:
            content = py_file.read_text()
            if f"import {module_name}" in content or f"from {module_name}" in content:
                return True
            checked += 1
        except (OSError, UnicodeDecodeError):
            continue
    
    return False


def _walk_files(project_path: Path, max_depth: int = 3, current_depth: int = 0) -> List[Path]:
    """Walk directory tree up to max_depth."""
    files = []
    
    if current_depth > max_depth:
        return files
    
    try:
        for item in project_path.iterdir():
            # Skip hidden directories and common ignore patterns
            if item.name.startswith(".") and item.name not in [".github"]:
                continue
            if item.name in ["node_modules", "__pycache__", "venv", "env", ".venv", "target", "build", "dist"]:
                continue
            
            if item.is_file():
                files.append(item)
            elif item.is_dir():
                files.extend(_walk_files(item, max_depth, current_depth + 1))
    except PermissionError:
        pass
    
    return files
