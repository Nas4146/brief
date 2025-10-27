# Brief MCP Server

Brief's Model Context Protocol (MCP) server exposes Brief functionality as tools that AI assistants can use directly.

## Overview

The Brief MCP server allows AI assistants (Claude Desktop, Cursor, Cline, etc.) to:
- Read current instruction files
- Update instructions across all files
- Validate file consistency
- List instruction files
- Analyze project context

## Security Model

Unlike guideAI which requires OAuth for cloud services, Brief operates entirely on local files and follows a simpler security model:

- **Local-only**: All operations are file-system based, no network access required
- **Workspace-scoped**: Operations limited to specified project directory
- **Transparent**: All actions logged with rationale for audit trail
- **Safe defaults**: Read operations allowed, write operations logged
- **No authentication needed**: Since all operations are local file manipulation

### Architectural Principles (from guideAI)

While Brief doesn't need OAuth, we follow the same security principles:

1. **Clear tool boundaries** - Each tool has well-defined scope (read vs write)
2. **Audit logging** - All operations logged with context and rationale
3. **Least-privilege** - Tools only access what they need
4. **User transparency** - Preview mode shows what will change before applying

## Installation

```bash
# Install Brief with MCP support
pip install ai-brief[mcp]

# Or install MCP dependency separately
pip install mcp>=0.1.0
```

## Configuration

Add Brief MCP server to your MCP settings file:

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "brief": {
      "command": "brief-mcp",
      "env": {}
    }
  }
}
```

### Cursor / Cline

Add to your IDE's MCP configuration:

```json
{
  "mcp": {
    "servers": {
      "brief": {
        "command": "brief-mcp"
      }
    }
  }
}
```

## Available Tools

### 1. `brief.read`

**Purpose**: Read all instruction files in a project  
**Type**: Read-only (safe)  
**Returns**: Content of all discovered instruction files

```json
{
  "project_path": "/path/to/project"
}
```

### 2. `brief.update`

**Purpose**: Update all instruction files with a new instruction  
**Type**: Write operation (modifies files)  
**Security**: Logs rationale for audit trail

```json
{
  "project_path": "/path/to/project",
  "instruction": "Always run tests before committing",
  "preview": true,
  "rationale": "Ensuring code quality across all AI assistants"
}
```

### 3. `brief.validate`

**Purpose**: Validate instruction file consistency  
**Type**: Read-only (safe)

### 4. `brief.list`

**Purpose**: List all instruction files  
**Type**: Read-only (safe)

### 5. `brief.context`

**Purpose**: Analyze project context  
**Type**: Read-only (safe)

## Usage Example

AI assistants can use Brief MCP tools to maintain their own instruction files:

1. User: "Make sure all AI assistants know to run tests before committing"
2. AI uses `brief.list` to discover instruction files
3. AI uses `brief.context` to understand project
4. AI uses `brief.update` with preview=true to see changes
5. AI shows user the preview
6. User confirms
7. AI uses `brief.update` with preview=false to apply

## Comparison to guideAI MCP

| Aspect | guideAI MCP | Brief MCP |
|--------|-------------|-----------|
| **Auth Required** | Yes (OAuth for cloud) | No (local files only) |
| **Scope** | Cloud services, workflows | File operations only |
| **Consent** | JIT prompts for scopes | Preview mode for writes |
| **Audit** | Action IDs, WORM logs | Operation logging |
| **Network** | Required (APIs) | Not required (local) |

Both follow same principles:
- Clear tool boundaries
- Least-privilege access
- Transparent operations
- Audit logging
