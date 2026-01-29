---
audience: [human, multi-agent]
priority: low
size: small
last_updated: 2026-01-28
status: active
tags: [overview, readme, introduction]
---

# dbt-playground

A learning project for dbt (data build tool) and data analytics development using Claude Code's agent orchestration system.

**Purpose**: Learn dbt, data modeling, and analytics engineering while leveraging multi-agent workflows for development.

**Status**: Initial setup - scaffolding agent orchestration for dbt project

---

## Quick Start

### For Developers

1. **Start here**: Read `CLAUDE.md` for complete project context
2. **Agent guide**: See `.claude/agents/AGENTS.md` for orchestration workflows
3. **Documentation**: Browse `docs/` for standards and references

---

## Project Overview

### What This Is

A dbt project scaffold with comprehensive agent orchestration infrastructure for:

- **dbt development**: Data transformations, models, tests
- **Data analytics**: SQL-based analytics and reporting
- **Agent workflows**: Multi-persona development methodology

### Technology Stack

- **dbt**: Data transformation framework
- **SQL**: Data modeling and analytics
- **MCP servers**: dbt-mcp for AI-assisted development
- **Claude Code**: Agent orchestration system

---

## Project Structure

```text
dbt-playground/
├── README.md              # This file
├── CLAUDE.md              # Project context for Claude
├── CHANGELOG.md           # Version history
│
├── docs/                  # Documentation
│   ├── reference/         # Architecture, structure docs
│   ├── guides/            # How-to workflows
│   ├── standards/         # Rules and conventions
│   ├── specs/             # PRDs (when created)
│   └── tdd/               # Technical design docs
│
├── temp/                  # Working files (development)
│
└── .claude/               # Agent configuration
    ├── agents/            # Persona definitions
    ├── commands/          # Slash commands
    ├── skills/            # Reusable workflows
    ├── rules/             # Coding standards
    ├── hooks/             # Pre/post tool hooks
    └── scripts/           # Utility scripts
```

---

## Agent Orchestration

This project includes a full agent orchestration system with specialized personas:

| Persona           | Prefix      | Purpose              |
| ----------------- | ----------- | -------------------- |
| Product Manager   | `pm:`       | Requirements, PRDs   |
| Architect         | `arch:`     | System design, TDDs  |
| Developer         | `dev:`      | Implementation       |
| Code Reviewer     | `review:`   | Code quality         |
| Tester            | `test:`     | Testing, verification|
| Documenter        | `docs:`     | Documentation        |
| Security Reviewer | `security:` | Security audit       |
| Git-Master        | `git:`      | Git operations       |
| Sage              | `sage:`     | Learning curation    |

See `.claude/agents/AGENTS.md` for detailed orchestration guide.

---

## Documentation

| Document                                                               | Purpose                   |
| ---------------------------------------------------------------------- | ------------------------- |
| **[CLAUDE.md](CLAUDE.md)**                                             | Project context for Claude|
| **[.claude/agents/AGENTS.md](.claude/agents/AGENTS.md)**               | Agent orchestration guide |
| **[docs/reference/ARCHITECTURE.md](docs/reference/ARCHITECTURE.md)**   | System architecture       |
| **[docs/reference/PROJECT_STRUCTURE.md](docs/reference/PROJECT_STRUCTURE.md)** | File organization |

---

## Getting Started with dbt

To be configured:

- dbt project initialization
- Database connection (dbt-mcp integration)
- Sample models and transformations

---

## License

To be determined.

---

**Ready to develop?** Read `CLAUDE.md` for complete context.
