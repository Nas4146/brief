"""
Brief - Brief your AI coding assistants once, update them all.

A minimal CLI tool for keeping AI assistant instruction files synchronized
across Claude, Copilot, Cursor, and custom agents.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__license__ = "MIT"

from brief.discovery import discover_instruction_files
from brief.context import analyze_project_context
from brief.updater import update_instruction_files

__all__ = [
    "discover_instruction_files",
    "analyze_project_context",
    "update_instruction_files",
]
