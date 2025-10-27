"""
Brief MCP Server - Exposes Brief as MCP tools for AI assistants.

Implements Model Context Protocol server that allows AI assistants to:
- Read current instruction files
- Update instructions across all files
- Validate instruction consistency
- List instruction files with metadata

Security:
- File operations are scoped to the workspace directory
- No authentication required (local-only, file-based tool)
- All operations logged for transparency
- Read-only by default unless explicitly approved

Note: This module requires the 'mcp' package. Install with: pip install ai-brief[mcp]
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

# Check for MCP dependency
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
    from pydantic import AnyUrl
except ImportError:
    print(
        "ERROR: MCP support requires the 'mcp' package.\n"
        "Install it with: pip install ai-brief[mcp]\n"
        "Or install Brief with MCP support: pip install 'ai-brief[mcp]'",
        file=sys.stderr
    )
    sys.exit(1)

from brief import __version__
from brief.discovery import discover_instruction_files, get_file_type
from brief.context import analyze_project_context
from brief.updater import update_instruction_files
from brief.validator import validate_instructions


logger = logging.getLogger(__name__)


class BriefMCPServer:
    """
    MCP server exposing Brief functionality to AI assistants.
    
    Security Model:
    - Local-only: All operations are file-system based, no network access
    - Workspace-scoped: Operations limited to specified project directory
    - Transparent: All actions logged with rationale
    - Safe defaults: Read operations allowed, write operations require explicit approval
    
    Note: Unlike guideAI which requires OAuth for cloud services, Brief operates
    entirely on local files and doesn't need authentication. However, we follow
    the same architectural principles:
    - Clear tool boundaries and scopes
    - Audit logging for all operations
    - Least-privilege access (read vs write)
    - User consent for destructive operations
    """
    
    def __init__(self):
        """Initialize the Brief MCP server."""
        self.server = Server("brief")
        self._register_handlers()
        logger.info(f"Brief MCP Server v{__version__} initialized")
    
    def _register_handlers(self):
        """Register MCP protocol handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available Brief tools."""
            return [
                Tool(
                    name="brief.read",
                    description=(
                        "Read current instruction files in a project. "
                        "Returns content of all discovered instruction files "
                        "(AGENTS.md, CLAUDE.md, copilot-instructions.md, etc.). "
                        "Safe read-only operation, no modifications made."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_path": {
                                "type": "string",
                                "description": "Absolute path to project directory"
                            }
                        },
                        "required": ["project_path"]
                    }
                ),
                Tool(
                    name="brief.update",
                    description=(
                        "Update all instruction files with a new instruction. "
                        "Adds the instruction to all discovered files with project context. "
                        "WRITE OPERATION: Modifies files on disk. "
                        "Use brief.read first to understand current state. "
                        "Includes duplicate prevention and smart section detection."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_path": {
                                "type": "string",
                                "description": "Absolute path to project directory"
                            },
                            "instruction": {
                                "type": "string",
                                "description": "Instruction to add to all files"
                            },
                            "preview": {
                                "type": "boolean",
                                "description": "If true, show what would change without applying",
                                "default": True
                            },
                            "rationale": {
                                "type": "string",
                                "description": "Why this instruction is being added (for audit log)"
                            }
                        },
                        "required": ["project_path", "instruction"]
                    }
                ),
                Tool(
                    name="brief.validate",
                    description=(
                        "Validate instruction file consistency. "
                        "Checks that all files are syntactically valid and consistent. "
                        "Safe read-only operation."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_path": {
                                "type": "string",
                                "description": "Absolute path to project directory"
                            }
                        },
                        "required": ["project_path"]
                    }
                ),
                Tool(
                    name="brief.list",
                    description=(
                        "List all instruction files in a project. "
                        "Returns file paths, types, and sizes. "
                        "Safe read-only operation."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_path": {
                                "type": "string",
                                "description": "Absolute path to project directory"
                            }
                        },
                        "required": ["project_path"]
                    }
                ),
                Tool(
                    name="brief.context",
                    description=(
                        "Analyze project context (languages, frameworks, test tools). "
                        "Returns structured data about the project for context-aware updates. "
                        "Safe read-only operation."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_path": {
                                "type": "string",
                                "description": "Absolute path to project directory"
                            }
                        },
                        "required": ["project_path"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
            """Handle tool invocation."""
            
            # Security: Validate project_path is provided and absolute
            project_path_str = arguments.get("project_path")
            if not project_path_str:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "project_path is required",
                        "status": "ERROR"
                    })
                )]
            
            project_path = Path(project_path_str).resolve()
            
            # Security: Verify path exists and is a directory
            if not project_path.exists():
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Project path does not exist: {project_path}",
                        "status": "ERROR"
                    })
                )]
            
            if not project_path.is_dir():
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Project path is not a directory: {project_path}",
                        "status": "ERROR"
                    })
                )]
            
            # Log operation for transparency
            logger.info(f"MCP tool invoked: {name} on {project_path}")
            
            # Route to appropriate handler
            if name == "brief.read":
                return await self._handle_read(project_path)
            elif name == "brief.update":
                return await self._handle_update(
                    project_path,
                    arguments["instruction"],
                    arguments.get("preview", True),
                    arguments.get("rationale", "No rationale provided")
                )
            elif name == "brief.validate":
                return await self._handle_validate(project_path)
            elif name == "brief.list":
                return await self._handle_list(project_path)
            elif name == "brief.context":
                return await self._handle_context(project_path)
            else:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Unknown tool: {name}",
                        "status": "ERROR"
                    })
                )]
    
    async def _handle_read(self, project_path: Path) -> Sequence[TextContent]:
        """
        Handle brief.read tool - read all instruction files.
        
        Security: Read-only operation, safe to execute.
        """
        try:
            files = discover_instruction_files(project_path)
            
            if not files:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "NO_FILES",
                        "message": "No instruction files found in project",
                        "supported_files": [
                            "AGENTS.md",
                            "CLAUDE.md",
                            ".github/copilot-instructions.md",
                            ".cursorrules",
                            ".clinerules"
                        ]
                    })
                )]
            
            # Read all files
            file_contents = {}
            for file_path in files:
                rel_path = str(file_path.relative_to(project_path))
                file_type = get_file_type(file_path)
                content = file_path.read_text(encoding="utf-8")
                
                file_contents[rel_path] = {
                    "type": file_type,
                    "size": len(content),
                    "content": content
                }
            
            logger.info(f"Read {len(files)} instruction files from {project_path}")
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "SUCCESS",
                    "project": str(project_path),
                    "file_count": len(files),
                    "files": file_contents
                }, indent=2)
            )]
        
        except Exception as e:
            logger.error(f"Error reading files: {e}", exc_info=True)
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "ERROR",
                    "error": str(e)
                })
            )]
    
    async def _handle_update(
        self, 
        project_path: Path, 
        instruction: str,
        preview: bool,
        rationale: str
    ) -> Sequence[TextContent]:
        """
        Handle brief.update tool - update instruction files.
        
        Security: WRITE operation. Logs rationale for audit trail.
        """
        try:
            files = discover_instruction_files(project_path)
            
            if not files:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "NO_FILES",
                        "message": "No instruction files found in project"
                    })
                )]
            
            # Analyze context
            context = analyze_project_context(project_path)
            
            # Get updates (preview mode first)
            updates = update_instruction_files(files, instruction, context, preview=True)
            
            # Check if any files will be updated
            files_to_update = []
            files_skipped = []
            
            for file_path, (old_content, new_content, was_updated) in updates.items():
                rel_path = str(file_path.relative_to(project_path))
                if was_updated:
                    files_to_update.append(rel_path)
                else:
                    files_skipped.append(rel_path)
            
            if not files_to_update:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "NO_CHANGES",
                        "message": "Instruction already exists in all files",
                        "files_checked": [str(f.relative_to(project_path)) for f in files]
                    })
                )]
            
            # If preview mode, return what would change
            if preview:
                logger.info(f"Preview mode: Would update {len(files_to_update)} files")
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "PREVIEW",
                        "message": "Preview mode - no files modified",
                        "instruction": instruction,
                        "context": context,
                        "files_to_update": files_to_update,
                        "files_skipped": files_skipped,
                        "rationale": rationale,
                        "action_required": "Set preview=false to apply changes"
                    }, indent=2)
                )]
            
            # Apply changes
            update_instruction_files(files, instruction, context, preview=False)
            
            logger.info(
                f"Updated {len(files_to_update)} files with instruction. "
                f"Rationale: {rationale}"
            )
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "SUCCESS",
                    "message": f"Successfully updated {len(files_to_update)} file(s)",
                    "instruction": instruction,
                    "files_updated": files_to_update,
                    "files_skipped": files_skipped,
                    "context": context,
                    "rationale": rationale
                }, indent=2)
            )]
        
        except Exception as e:
            logger.error(f"Error updating files: {e}", exc_info=True)
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "ERROR",
                    "error": str(e)
                })
            )]
    
    async def _handle_validate(self, project_path: Path) -> Sequence[TextContent]:
        """
        Handle brief.validate tool - validate file consistency.
        
        Security: Read-only operation, safe to execute.
        """
        try:
            files = discover_instruction_files(project_path)
            
            if not files:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "NO_FILES",
                        "message": "No instruction files found in project"
                    })
                )]
            
            # Run validation
            is_valid, errors = validate_instructions(files, project_path)
            
            logger.info(f"Validated {len(files)} files: {'valid' if is_valid else 'errors found'}")
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "VALID" if is_valid else "INVALID",
                    "file_count": len(files),
                    "files": [str(f.relative_to(project_path)) for f in files],
                    "errors": errors if not is_valid else []
                }, indent=2)
            )]
        
        except Exception as e:
            logger.error(f"Error validating files: {e}", exc_info=True)
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "ERROR",
                    "error": str(e)
                })
            )]
    
    async def _handle_list(self, project_path: Path) -> Sequence[TextContent]:
        """
        Handle brief.list tool - list instruction files.
        
        Security: Read-only operation, safe to execute.
        """
        try:
            files = discover_instruction_files(project_path)
            
            if not files:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "NO_FILES",
                        "message": "No instruction files found in project",
                        "supported_files": [
                            "AGENTS.md",
                            "CLAUDE.md",
                            ".github/copilot-instructions.md",
                            ".cursorrules",
                            ".clinerules"
                        ]
                    })
                )]
            
            # Build file list with metadata
            file_list = []
            total_size = 0
            
            for file_path in sorted(files):
                rel_path = str(file_path.relative_to(project_path))
                file_type = get_file_type(file_path)
                size = file_path.stat().st_size
                total_size += size
                
                file_list.append({
                    "path": rel_path,
                    "type": file_type,
                    "size": size
                })
            
            logger.info(f"Listed {len(files)} instruction files")
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "SUCCESS",
                    "file_count": len(files),
                    "total_size": total_size,
                    "files": file_list
                }, indent=2)
            )]
        
        except Exception as e:
            logger.error(f"Error listing files: {e}", exc_info=True)
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "ERROR",
                    "error": str(e)
                })
            )]
    
    async def _handle_context(self, project_path: Path) -> Sequence[TextContent]:
        """
        Handle brief.context tool - analyze project context.
        
        Security: Read-only operation, safe to execute.
        """
        try:
            context = analyze_project_context(project_path)
            
            logger.info(f"Analyzed project context for {project_path}")
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "SUCCESS",
                    "project": str(project_path),
                    "context": context
                }, indent=2)
            )]
        
        except Exception as e:
            logger.error(f"Error analyzing context: {e}", exc_info=True)
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "ERROR",
                    "error": str(e)
                })
            )]
    
    async def run(self):
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Brief MCP server starting...")
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    """Entry point for Brief MCP server."""
    import asyncio
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    server = BriefMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
