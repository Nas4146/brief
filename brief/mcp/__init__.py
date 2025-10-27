"""
Brief MCP Server - Model Context Protocol integration.

Exposes Brief functionality as MCP tools for AI assistants.

Note: MCP is an optional dependency. Install with: pip install ai-brief[mcp]
"""

__all__ = ["BriefMCPServer"]

def __getattr__(name):
    """Lazy import to avoid requiring mcp package for CLI-only users."""
    if name == "BriefMCPServer":
        try:
            from brief.mcp.server import BriefMCPServer
            return BriefMCPServer
        except ImportError as e:
            raise ImportError(
                "MCP support requires the 'mcp' package. "
                "Install it with: pip install ai-brief[mcp]"
            ) from e
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
