"""
Validator module - Check instruction files for consistency across all agent files.

Validates:
- Most recent update was added to all files (--check-latest)
- Core instructions/guidance exists across all files (--check-all)
- Content similarity and coverage across files
"""

from pathlib import Path
from typing import Dict, List, Tuple, Set
import re
from difflib import SequenceMatcher


def validate_instructions(
    files: List[Path], 
    project_path: Path,
    check_latest: bool = False,
    check_all: bool = True
) -> Tuple[bool, List[str]]:
    """
    Validate instruction files for consistency across all agent files.
    
    Args:
        files: List of instruction file paths to validate
        project_path: Root directory of the project
        check_latest: If True, verify the most recent update appears in all files
        check_all: If True, check that all core instructions exist across files
        
    Returns:
        Tuple of (all_valid: bool, issues: List[str])
    """
    issues = []
    
    if not files:
        issues.append("No instruction files found")
        return False, issues
    
    if len(files) < 2:
        # Only one file, nothing to compare
        return True, []
    
    # Check each file exists and is readable
    file_contents = {}
    for file_path in files:
        if not file_path.exists():
            issues.append(f"File not found: {file_path}")
            continue
        
        try:
            file_contents[file_path] = file_path.read_text()
        except OSError as e:
            issues.append(f"Cannot read {file_path.name}: {e}")
    
    if len(file_contents) < 2:
        return len(issues) == 0, issues
    
    # Check for most recent update consistency
    if check_latest:
        latest_issues = _check_latest_update(file_contents)
        issues.extend(latest_issues)
    
    # Check for overall instruction consistency
    if check_all:
        consistency_issues = _check_instruction_consistency(file_contents)
        issues.extend(consistency_issues)
    
    return len(issues) == 0, issues


def _check_latest_update(file_contents: Dict[Path, str]) -> List[str]:
    """
    Check if the most recent update appears in all files.
    
    Strategy: Find the newest modification time, extract recent content,
    and check if similar content exists in other files.
    
    Args:
        file_contents: Dict mapping file paths to their content
        
    Returns:
        List of issues found
    """
    issues = []
    
    # Find the most recently modified file
    files_by_mtime = sorted(
        file_contents.keys(),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )
    
    if len(files_by_mtime) < 2:
        return issues
    
    newest_file = files_by_mtime[0]
    newest_content = file_contents[newest_file]
    
    # Extract the last instruction section (heuristic: last major section before EOF)
    newest_instructions = _extract_recent_instructions(newest_content)
    
    if not newest_instructions:
        return issues
    
    # Check if similar content exists in other files
    missing_in = []
    for file_path in files_by_mtime[1:]:
        content = file_contents[file_path]
        if not _content_contains_similar(content, newest_instructions):
            missing_in.append(file_path.name)
    
    if missing_in:
        issues.append(
            f"Recent update in '{newest_file.name}' may be missing from: {', '.join(missing_in)}"
        )
    
    return issues


def _check_instruction_consistency(file_contents: Dict[Path, str]) -> List[str]:
    """
    Check that core instructions/guidance exist across all files.
    
    Strategy: Extract key instruction topics from each file and check
    that they're covered (conceptually) across all files.
    
    Args:
        file_contents: Dict mapping file paths to their content
        
    Returns:
        List of issues found
    """
    issues = []
    
    # Extract instruction topics from each file
    file_topics = {}
    for file_path, content in file_contents.items():
        topics = _extract_instruction_topics(content)
        file_topics[file_path] = topics
    
    # Find topics that appear in some files but not others
    all_topics = set()
    for topics in file_topics.values():
        all_topics.update(topics)
    
    # Check each file for missing topics
    for file_path, topics in file_topics.items():
        missing_topics = []
        for topic in all_topics:
            # Check if this topic appears in at least one other file
            appears_in_others = any(
                topic in other_topics 
                for other_path, other_topics in file_topics.items() 
                if other_path != file_path
            )
            
            if appears_in_others and topic not in topics:
                missing_topics.append(topic)
        
        if missing_topics:
            # Check if the content is actually missing (fuzzy match)
            actually_missing = []
            for topic in missing_topics:
                if not _has_similar_topic(file_contents[file_path], topic):
                    actually_missing.append(topic)
            
            if actually_missing:
                issues.append(
                    f"'{file_path.name}' may be missing guidance on: {', '.join(actually_missing[:3])}"
                    + (f" (+{len(actually_missing) - 3} more)" if len(actually_missing) > 3 else "")
                )
    
    return issues


def _extract_recent_instructions(content: str, lines: int = 10) -> str:
    """
    Extract the most recent instruction content.
    
    Args:
        content: File content
        lines: Number of lines to extract from the end
        
    Returns:
        Recent instruction text
    """
    content_lines = content.strip().split("\n")
    
    # Skip empty lines and metadata at the end
    while content_lines and (
        not content_lines[-1].strip() or 
        content_lines[-1].strip().startswith("---") or
        content_lines[-1].strip().startswith("Last updated:")
    ):
        content_lines.pop()
    
    # Get last N lines that have substance
    recent_lines = content_lines[-lines:]
    return "\n".join(recent_lines)


def _extract_instruction_topics(content: str) -> Set[str]:
    """
    Extract key instruction topics from content.
    
    Looks for:
    - Headers (## Topic Name)
    - Bold directives (**Always do X**)
    - List items with instructions
    
    Args:
        content: File content
        
    Returns:
        Set of normalized topic strings
    """
    topics = set()
    
    lines = content.split("\n")
    for line in lines:
        line = line.strip()
        
        # Extract from headers
        if line.startswith("##"):
            topic = line.lstrip("#").strip()
            topics.add(_normalize_topic(topic))
        
        # Extract from bold text
        bold_pattern = r'\*\*(.+?)\*\*'
        for match in re.finditer(bold_pattern, line):
            topic = match.group(1)
            if len(topic.split()) <= 6:  # Keep reasonably short topics
                topics.add(_normalize_topic(topic))
        
        # Extract from list items (bullets)
        if line.startswith(("-", "*", "•")) or re.match(r'^\d+\.', line):
            # Remove list marker
            topic = re.sub(r'^[-*•]|\d+\.', '', line).strip()
            if topic and len(topic.split()) <= 8:
                topics.add(_normalize_topic(topic))
    
    return topics


def _normalize_topic(topic: str) -> str:
    """
    Normalize a topic string for comparison.
    
    Args:
        topic: Raw topic string
        
    Returns:
        Normalized topic
    """
    # Remove common prefixes
    topic = re.sub(r'^(always|never|must|should|do not|don\'t)\s+', '', topic.lower())
    # Remove punctuation
    topic = re.sub(r'[^\w\s]', '', topic)
    # Normalize whitespace
    topic = ' '.join(topic.split())
    return topic


def _content_contains_similar(content: str, target: str, threshold: float = 0.6) -> bool:
    """
    Check if content contains text similar to target.
    
    Args:
        content: Content to search in
        target: Text to search for
        threshold: Similarity threshold (0.0 to 1.0)
        
    Returns:
        True if similar content found
    """
    content_lower = content.lower()
    target_lower = target.lower()
    
    # Direct substring match
    if target_lower in content_lower:
        return True
    
    # Check similarity with sliding window
    target_words = target_lower.split()
    if len(target_words) < 3:
        return False
    
    content_words = content_lower.split()
    window_size = len(target_words)
    
    for i in range(len(content_words) - window_size + 1):
        window = ' '.join(content_words[i:i + window_size])
        similarity = SequenceMatcher(None, target_lower, window).ratio()
        if similarity >= threshold:
            return True
    
    return False


def _has_similar_topic(content: str, topic: str, threshold: float = 0.5) -> bool:
    """
    Check if content discusses a similar topic.
    
    Args:
        content: Content to check
        topic: Topic to look for
        threshold: Similarity threshold
        
    Returns:
        True if similar topic found
    """
    content_topics = _extract_instruction_topics(content)
    
    # Check for exact match
    if topic in content_topics:
        return True
    
    # Check for similar topics using fuzzy matching
    topic_words = set(topic.lower().split())
    for content_topic in content_topics:
        content_words = set(content_topic.lower().split())
        
        # Calculate word overlap
        if len(topic_words) == 0:
            continue
        
        overlap = len(topic_words & content_words)
        similarity = overlap / len(topic_words)
        
        if similarity >= threshold:
            return True
    
    return False


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
