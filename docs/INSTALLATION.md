# Brief Installation Guide

Brief can be installed in two ways depending on your needs:

## 📦 Installation Options

### Option 1: CLI Only (Recommended for Most Users)

If you just want to use Brief from the command line:

```bash
pip install ai-brief
```

**What you get:**
- ✅ `brief` command-line tool
- ✅ All core features (init, update, list, validate)
- ✅ Beautiful terminal UI
- ✅ Context-aware updates
- ✅ Zero extra dependencies

**Package size:** ~700 KB  
**Dependencies:** 3 (click, pyyaml, rich)

**Use this if:**
- You manually run Brief commands
- You don't use AI assistants (Claude, Cursor, etc.)
- You want the lightest installation

---

### Option 2: CLI + MCP Server

If you want AI assistants to be able to update instruction files:

```bash
pip install 'ai-brief[mcp]'
```

**What you get:**
- ✅ Everything from Option 1
- ✅ `brief-mcp` MCP server
- ✅ AI assistant integration (Claude Desktop, Cursor, Cline)
- ✅ Tools for AI to read/update files

**Package size:** ~2 MB  
**Dependencies:** 4 (click, pyyaml, rich, mcp)

**Use this if:**
- You use Claude Desktop, Cursor, or Cline
- You want AI assistants to maintain their own instructions
- You need MCP protocol support

---

## 🔍 How to Choose

### Choose CLI Only if:
- ❌ You don't use AI coding assistants
- ❌ You don't know what MCP (Model Context Protocol) is
- ✅ You just want a command-line tool
- ✅ You want the smallest installation

### Choose CLI + MCP if:
- ✅ You use Claude Desktop, Cursor, or Cline
- ✅ You want AI assistants to update their own instructions
- ✅ You need MCP protocol integration
- ✅ You're okay with one extra dependency

---

## 📝 Verification

### Verify CLI Installation

```bash
# Check version
brief --version

# List available commands
brief --help

# Test in a project
cd your-project
brief list
```

### Verify MCP Installation

```bash
# Check MCP command exists
which brief-mcp

# Try to start MCP server (Ctrl+C to stop)
brief-mcp
```

If `brief-mcp` says "command not found", you have CLI-only installation.  
To add MCP: `pip install 'ai-brief[mcp]'`

---

## 🔄 Switching Between Options

### Upgrade: CLI → CLI + MCP

```bash
pip install 'ai-brief[mcp]'
```

Your existing CLI installation stays intact, MCP support is added.

### Downgrade: CLI + MCP → CLI Only

```bash
pip uninstall mcp
```

The `brief` CLI continues working, only `brief-mcp` will stop working.

### Complete Uninstall

```bash
pip uninstall ai-brief mcp
```

---

## 🚀 Quick Start Examples

### CLI Only Workflow

```bash
# Install
pip install ai-brief

# Use
cd your-project
brief init
brief update "Run tests before committing"
brief validate
```

### CLI + MCP Workflow

```bash
# Install
pip install 'ai-brief[mcp]'

# Configure Claude Desktop
cat > ~/Library/Application\ Support/Claude/claude_desktop_config.json <<EOF
{
  "mcpServers": {
    "brief": {
      "command": "brief-mcp"
    }
  }
}
EOF

# Restart Claude Desktop
# AI can now use: brief.read, brief.update, brief.validate, brief.list, brief.context
```

---

## ❓ FAQ

### Q: Will CLI work if I don't install MCP?
**A:** Yes! CLI is completely independent. MCP is optional.

### Q: If I install MCP, does it affect CLI?
**A:** No! Both work independently. MCP adds extra features, doesn't change CLI.

### Q: Can I use both CLI and MCP at the same time?
**A:** Yes! You can run `brief update` manually AND let AI assistants use `brief.update` tool.

### Q: What if I install Brief and MCP separately?
**A:** That works too:
```bash
pip install ai-brief
pip install mcp  # adds MCP support
```

### Q: Does MCP require authentication/API keys?
**A:** No! MCP just enables AI assistants to call Brief tools. All operations are local file-based.

### Q: What's the performance difference?
**A:** None. MCP code only loads when `brief-mcp` command runs, not when using CLI.

### Q: Can I have different versions of CLI vs MCP?
**A:** They're bundled together in `ai-brief` package, so version stays in sync.

---

## 🛠️ Troubleshooting

### CLI works but `brief-mcp` doesn't exist

**Cause:** You installed CLI-only version  
**Fix:** `pip install 'ai-brief[mcp]'`

### MCP import errors

**Cause:** MCP package not installed  
**Fix:** `pip install mcp` or `pip install 'ai-brief[mcp]'`

### Both CLI and MCP broken

**Cause:** Installation issue  
**Fix:** 
```bash
pip uninstall ai-brief mcp
pip install 'ai-brief[mcp]'  # or just 'ai-brief' for CLI only
```

---

## 📊 Comparison

| Feature | CLI Only | CLI + MCP |
|---------|----------|-----------|
| **Install size** | ~700 KB | ~2 MB |
| **Dependencies** | 3 | 4 |
| **`brief` command** | ✅ | ✅ |
| **`brief-mcp` command** | ❌ | ✅ |
| **AI assistant integration** | ❌ | ✅ |
| **Standalone usage** | ✅ | ✅ |
| **MCP tools (brief.read, etc.)** | ❌ | ✅ |
| **Claude Desktop integration** | ❌ | ✅ |

---

## 🎯 Recommendations

**Most users:** Start with CLI-only (`pip install ai-brief`)

**AI assistant users:** Install with MCP (`pip install 'ai-brief[mcp]'`)

**Not sure?** Install CLI-only first. Add MCP later if needed.

---

## 📚 Next Steps

- **CLI Guide:** [README.md](../README.md)
- **MCP Guide:** [MCP_SERVER.md](MCP_SERVER.md)
- **Examples:** [examples/](../examples/)
