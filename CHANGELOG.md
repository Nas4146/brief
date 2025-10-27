# Changelog

All notable changes to Brief will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-10-27

### Added
- Initial release of Brief
- Core CLI commands: `init`, `update`, `list`, `validate`
- Auto-discovery of instruction files (AGENTS.md, CLAUDE.md, .clinerules, .github/copilot-instructions.md, .cursorrules)
- Context-aware instruction updates (detects languages, frameworks, test frameworks)
- Beautiful terminal UI with Rich library (panels, tables, color-coded output)
- Duplicate prevention with fuzzy matching
- Smart section detection and insertion
- Optional MCP (Model Context Protocol) server support
- MCP tools: brief.read, brief.update, brief.validate, brief.list, brief.context
- Comprehensive test suite (18 tests)
- Documentation: README, Installation Guide, MCP Server Guide

### Features
- 🔍 Auto-discovery of 5 instruction file types
- 🧠 Context-aware updates based on project structure
- ✅ Validation for consistency
- 🎯 Zero configuration required
- 🪶 Lightweight with minimal dependencies
- ✨ Professional terminal UI
- 🔒 Duplicate prevention
- 👀 Preview mode before applying changes
- 🤖 Optional MCP support for AI assistant integration

[Unreleased]: https://github.com/Nas4146/brief/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Nas4146/brief/releases/tag/v0.1.0
