# dbt-playground - Project Context

## Project Purpose

This is a dbt learning project for data transformation best practices, agent orchestration, and dbt-mcp integration.

**Key Philosophy**: Leave the codebase better than you found it. Fight entropy.

## Current Phase

**Status**: Staging Models Complete (v0.3)

- dbt 1.11.2 + duckdb-adapter 1.10.0 working
- 16 Synthea source tables defined + data loading macro
- 9 staging models with comprehensive tests (80 data tests)
- dbt-mcp configured (restart Claude Code for MCP tools)
- uv workflow fully implemented (pyproject.toml, uv.lock, PEP 723 scripts)

**Next**: v0.4 - Build intermediate models with business logic.

## Project Structure

```text
dbt-playground/
├── CLAUDE.md              # This file
├── docs/reference/        # Architecture, coding standards
├── temp/                  # Work-in-progress
└── .claude/               # Agent config (agents/, commands/, rules/)
```

See `docs/reference/PROJECT_STRUCTURE.md` for complete structure.

## Standard Workflow

1. **UNDERSTAND** - Read existing files, check architecture docs
2. **PLAN** - Create `temp/v[X.Y]_PLAN.md`, get approval
3. **BUILD** - Implement, test as you go
4. **VERIFY** - Test, document in `temp/v[X.Y]_TESTING.md`
5. **DEPLOY** - Update docs, tag version via git-master

## Critical Rules

### Never

- Push/merge directly to main (use PRs)
- Execute git writes directly (use git-master: `/commit`, `/branch`, `git:`)
- Skip planning for non-trivial work
- Commit without testing

### Always

- Use `temp/` for work-in-progress
- Use feature branches (`feat/`, `fix/`, etc.)
- Use `uv` for Python packages (never `pip`)
- Update CHANGELOG for feat/fix PRs

## Development Environment

### Python: Use `uv` exclusively

This project uses [uv](https://docs.astral.sh/uv/) for reproducible Python environment management.

#### Initial Setup

```bash
# Install dependencies from pyproject.toml
uv sync

# Install with dev dependencies (sqlfluff, pre-commit)
uv sync --all-extras
```

#### Common Commands

| Command | Purpose |
|---------|---------|
| `uv sync` | Install/update dependencies |
| `uv add <package>` | Add production dependency |
| `uv add --dev <package>` | Add development dependency |
| `uv run <command>` | Run command in project venv |
| `uv run dbt build` | Run dbt commands |
| `uvx <tool>` | Run tool without installing |

#### Running Scripts

Scripts use PEP 723 inline metadata for dependencies. Run with:

```bash
# Run scripts with uv (automatically respects Python version)
uv run scripts/extract_content.py <args>

# Or activate venv first
source .venv/bin/activate
python scripts/extract_content.py <args>
```

#### Key Project Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project metadata, dependencies, tool configs |
| `uv.lock` | Locked dependency versions (committed for reproducibility) |
| `.python-version` | Python version pin (3.11) |
| `scripts/*.py` | Standalone scripts with PEP 723 headers |

### Pre-commit Hooks

| File Type | Linter | Auto-fix |
|-----------|--------|----------|
| Markdown | markdownlint-cli2 | Yes |
| YAML | yamllint | No |
| SQL | sqlfluff | Manual: `npm run lint:sql:fix` |

## Agent System

See `.claude/agents/AGENTS.md` for orchestration details.

### Key Personas

| Persona | Prefix | Focus |
|---------|--------|-------|
| Git-Master | `git:` | Git operations (required for commits) |
| dbt Developer | `dbt-dev:` | SQL models, macros |
| Data Modeler | `dbt-model:` | Model design |
| dbt Tester | `dbt-test:` | Testing |

### Commands

| Command | Purpose |
|---------|---------|
| `/commit` | Git commit via git-master |
| `/branch` | Branch creation via git-master |
| `/plan` | Structured planning |
| `/dbt-run` | Execute dbt commands |

## Notes for Claude

- ASK rather than assume
- Default to simpler solutions
- Explain technical decisions
- Use agents for complex work, manual for simple tasks
