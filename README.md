---
audience: [human, multi-agent]
priority: low
size: small
last_updated: 2026-01-29
status: active
tags: [overview, readme, introduction]
---

# dbt-playground

A learning project for dbt (data build tool) and data analytics development using Claude Code's agent orchestration system.

**Purpose**: Learn dbt, data modeling, and analytics engineering while leveraging multi-agent workflows for development.

**Status**: v0.2 Environment Ready - dbt 1.11.2 + DuckDB 1.10.0 with 16 Synthea source tables

---

## Quick Start

### Prerequisites

- [uv](https://docs.astral.sh/uv/) - Python package manager

### Setup

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone <repo-url>
cd dbt-playground
uv sync

# Verify installation
uv run dbt --version   # Should show dbt 1.11.2
uv run dbt debug       # Should connect to dev.duckdb
```

### Run dbt

```bash
# From dbt_project/ directory
cd dbt_project
uv run dbt compile     # Compile models
uv run dbt build       # Build and test
uv run dbt docs generate && uv run dbt docs serve  # Documentation
```

### For Developers

1. **Start here**: Read `CLAUDE.md` for complete project context
2. **uv Guide**: See `docs/reference/UV_MIGRATION.md` for Python workflow
3. **Agent guide**: See `.claude/agents/AGENTS.md` for orchestration workflows
4. **Documentation**: Browse `docs/` for standards and references

---

## Project Overview

### What This Is

A dbt project scaffold with comprehensive agent orchestration infrastructure for:

- **dbt development**: Data transformations, models, tests
- **Data analytics**: SQL-based analytics and reporting
- **Agent workflows**: Multi-persona development methodology

### Technology Stack

- **Python**: Managed by uv (pyproject.toml, uv.lock)
- **dbt**: Data transformation framework (1.11.2)
- **DuckDB**: Analytical database (1.10.0)
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
├── pyproject.toml         # Python project config (uv)
├── uv.lock                # Locked dependency versions
├── .python-version        # Python version (3.11)
│
├── dbt_project/           # dbt project
│   ├── dbt_project.yml       # dbt configuration
│   ├── models/               # staging/, intermediate/, marts/
│   └── ...                   # seeds, macros, tests, etc.
│
├── docs/                  # Documentation
│   ├── reference/         # Architecture, UV_MIGRATION.md
│   ├── guides/            # How-to workflows
│   ├── standards/         # Rules and conventions
│   ├── specs/             # PRDs
│   └── tdd/               # Technical design docs
│
├── scripts/               # Utility scripts (uv run compatible)
│
├── temp/                  # Working files (development)
│
└── .claude/               # Agent configuration
    ├── agents/            # Persona definitions
    ├── commands/          # Slash commands
    ├── skills/            # Reusable workflows
    ├── rules/             # Coding standards
    └── hooks/             # Pre/post tool hooks
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

The dbt project is fully configured with:

- **Project**: `healthcare_analytics` using DuckDB
- **Data Source**: Synthea (synthetic healthcare data) - 16 tables
- **Layers**: staging (views), intermediate (views), marts (tables)

### Common Commands

Run from `dbt_project/` directory:

| Task | Command |
|------|---------|
| Install dependencies | `uv sync` (from repo root) |
| Run all models | `uv run dbt build` |
| Compile SQL | `uv run dbt compile` |
| Run tests | `uv run dbt test` |
| Generate docs | `uv run dbt docs generate` |
| Serve docs | `uv run dbt docs serve` |

See `docs/reference/UV_MIGRATION.md` for complete uv workflow guide

---

## License

To be determined.

---

**Ready to develop?** Read `CLAUDE.md` for complete context.
