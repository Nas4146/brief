"""
Updater module - Apply updates to instruction files.

Handles smart insertion of instructions while maintaining file structure,
formatting, and context-awareness.
"""

import difflib
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def update_instruction_files(
    files: List[Path],
    instruction: str,
    context: Dict,
    preview: bool = True
) -> Dict[Path, Tuple[str, str, bool]]:
    """
    Update instruction files with a new instruction.
    
    Args:
        files: List of instruction file paths to update
        instruction: The instruction text to add
        context: Project context from analyze_project_context()
        preview: If True, return changes without modifying files
        
    Returns:
        Dictionary mapping file paths to tuples of:
        - old_content: Original file content
        - new_content: Updated file content
        - was_updated: True if file was actually modified
    """
    updates = {}
    
    for file_path in files:
        # Read current content
        try:
            content = file_path.read_text()
        except OSError:
            continue
        
        # Check for duplicates
        if _instruction_exists(content, instruction):
            updates[file_path] = (content, content, False)
            continue
        
        # Generate context-aware instruction
        contextualized = _contextualize_instruction(instruction, context)
        
        # Determine where to insert based on file type and content
        updated_content = _insert_instruction(content, contextualized, file_path, context)
        
        updates[file_path] = (content, updated_content, True)
        
        # Write if not preview mode and content actually changed
        if not preview and updated_content != content:
            try:
                file_path.write_text(updated_content)
            except OSError:
                pass
    
    return updates


def _contextualize_instruction(instruction: str, context: Dict) -> str:
    """
    Add project-specific context to an instruction.
    
    Args:
        instruction: Base instruction text
        context: Project context information
        
    Returns:
        Contextualized instruction with project details
    """
    contextualized = instruction
    
    # Add language-specific context
    if context.get("languages"):
        langs = context["languages"]
        if len(langs) == 1:
            contextualized = f"{instruction} (this is a {langs[0]} project)"
        elif len(langs) > 1:
            contextualized = f"{instruction} (languages: {', '.join(langs)})"
    
    # Add test framework context if instruction mentions testing
    if "test" in instruction.lower() and context.get("test_framework"):
        contextualized += f" using {context['test_framework']}"
    
    return contextualized


def _instruction_exists(content: str, instruction: str) -> bool:
    """
    Check if an instruction already exists in the content.
    
    Args:
        content: File content to search
        instruction: Instruction to look for
        
    Returns:
        True if instruction already exists (exact or similar match)
    """
    # Normalize both for comparison
    normalized_content = content.lower().strip()
    normalized_instruction = instruction.lower().strip()
    
    # Check for exact substring match
    if normalized_instruction in normalized_content:
        return True
    
    # Check for similar lines (handle minor variations)
    instruction_words = set(normalized_instruction.split())
    for line in content.split("\n"):
        line_words = set(line.lower().split())
        # If 80%+ of instruction words appear in this line, consider it a duplicate
        if len(instruction_words) > 0:
            overlap = len(instruction_words & line_words) / len(instruction_words)
            if overlap >= 0.8:
                return True
    
    return False


def _find_best_section(content: str, instruction: str, context: Dict) -> Optional[str]:
    """
    Find the best section header to insert the instruction under.
    
    Args:
        content: File content
        instruction: Instruction to insert
        context: Project context
        
    Returns:
        Section header name (without ##) or None
    """
    instruction_lower = instruction.lower()
    
    # Map keywords to section preferences
    section_keywords = {
        "## Behaviors": ["behavior", "workflow", "process", "procedure"],
        "## Development Workflow": ["commit", "test", "deploy", "build", "workflow"],
        "## Testing": ["test", "pytest", "jest", "validate"],
        "## Code Style": ["style", "format", "lint", "convention"],
        "## Documentation": ["document", "doc", "comment", "readme"],
        "## Security": ["security", "secret", "auth", "vulnerability"],
    }
    
    # Find sections that exist in the content
    existing_sections = []
    for line in content.split("\n"):
        if line.strip().startswith("##") and not line.strip().startswith("###"):
            existing_sections.append(line.strip())
    
    # Score each existing section based on keyword matches
    best_section = None
    best_score = 0
    
    for section in existing_sections:
        score = 0
        section_lower = section.lower()
        
        # Check keyword matches
        for section_key, keywords in section_keywords.items():
            if section_key.lower() in section_lower:
                for keyword in keywords:
                    if keyword in instruction_lower:
                        score += 1
        
        if score > best_score:
            best_score = score
            best_section = section
    
    return best_section


def _insert_instruction(content: str, instruction: str, file_path: Path, context: Dict) -> str:
    """
    Insert instruction into file content at the appropriate location.
    
    Args:
        content: Current file content
        instruction: Instruction to insert (contextualized)
        file_path: Path to the file (used to determine type)
        context: Project context
        
    Returns:
        Updated file content
    """
    lines = content.split("\n")
    
    # Find the best section to insert into
    best_section = _find_best_section(content, instruction, context)
    
    if best_section:
        # Insert after the section header
        insert_position = None
        for i, line in enumerate(lines):
            if line.strip() == best_section:
                # Find the end of this section's content (before next ## header or end)
                insert_position = i + 1
                
                # Skip any empty lines after header
                while insert_position < len(lines) and not lines[insert_position].strip():
                    insert_position += 1
                
                # If there's already content, insert before the next empty line or next section
                if insert_position < len(lines) and lines[insert_position].strip():
                    # Find next empty line or section
                    while insert_position < len(lines):
                        if not lines[insert_position].strip() or lines[insert_position].strip().startswith("##"):
                            break
                        insert_position += 1
                
                break
        
        if insert_position is not None:
            # Format as markdown list item
            lines.insert(insert_position, f"- {instruction}")
            lines.insert(insert_position + 1, "")  # Add blank line after
            return "\n".join(lines)
    
    # Fallback: Create or append to "Additional Instructions" section
    additional_section = "## Additional Instructions"
    
    # Check if section exists
    section_exists = False
    insert_position = None
    
    for i, line in enumerate(lines):
        if additional_section in line:
            section_exists = True
            # Insert after the header
            insert_position = i + 1
            # Skip empty lines
            while insert_position < len(lines) and not lines[insert_position].strip():
                insert_position += 1
            # Find end of existing items
            while insert_position < len(lines):
                current_line = lines[insert_position].strip()
                if not current_line or current_line.startswith("##"):
                    break
                insert_position += 1
            break
    
    if section_exists and insert_position is not None:
        # Insert into existing section
        lines.insert(insert_position, f"- {instruction}")
        return "\n".join(lines)
    else:
        # Create new section at the end
        if content.rstrip():
            instruction_block = f"\n{additional_section}\n\n- {instruction}\n"
        else:
            instruction_block = f"{additional_section}\n\n- {instruction}\n"
        return content.rstrip() + instruction_block


def generate_diff(old_content: str, new_content: str, file_path: Path) -> str:
    """
    Generate a unified diff between old and new content.
    
    Args:
        old_content: Original file content
        new_content: Updated file content
        file_path: Path to the file (for diff header)
        
    Returns:
        Unified diff string
    """
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"a/{file_path.name}",
        tofile=f"b/{file_path.name}",
        lineterm=""
    )
    
    return "".join(diff)


def create_instruction_file(file_path: Path, template: str, context: Dict) -> bool:
    """
    Create a new instruction file from a template.
    
    Args:
        file_path: Path where the file should be created
        template: Template name or content
        context: Project context for customization
        
    Returns:
        True if file was created successfully
    """
    # TODO: Load template from brief/templates/files/
    # TODO: Customize template with context
    # TODO: Write to file_path
    
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        # Placeholder content
        content = f"# AI Assistant Instructions\n\nProject type: {', '.join(context.get('languages', ['Unknown']))}\n"
        file_path.write_text(content)
        return True
    except OSError:
        return False
