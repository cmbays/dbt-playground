# dbt-playground - Project Context

## Project Purpose

This is a dbt learning project for data transformation best practices, agent orchestration, and dbt-mcp integration.

**Key Philosophy**: Leave the codebase better than you found it. Fight entropy.

## Current Phase

**Status**: Analytics Layer Complete (v0.6.0) + GitHub Actions MVP

- dbt 1.11.2 + duckdb-adapter 1.10.0 working
- 28 models total (staging, intermediate, dimensional, analytics)
- 171+ data tests passing
- Interactive playgrounds: Workflow Hub, Workflow Chronicle, Worktree Coordinator, Mermaid Designer
- Agent context management with inter-agent reports
- uv workflow fully implemented (pyproject.toml, uv.lock, PEP 723 scripts)
- GitHub Actions automation: PR validation, issue linking, auto-labeling, dbt CI tests

**Next**: v0.7 - Data quality enhancements (dbt_expectations).

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

The canonical 5-stage workflow for all development work. See [WORKFLOW_STAGES.md](docs/reference/WORKFLOW_STAGES.md) for complete reference.

1. **UNDERSTAND** - Read existing files, check architecture docs
2. **PLAN** - Create `temp/v[X.Y]_PLAN.md`, get approval
3. **BUILD** - Implement, test as you go
4. **VERIFY** - Test, document in `temp/v[X.Y]_TESTING.md`
5. **DEPLOY** - Update docs, tag version via git-master

Quality gates are enforced by the Supervisor agent at each stage transition.

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
- Write agent reports to `temp/AGENT_REPORTS/[feature]/` for tracked features

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

### Inter-Agent Reports

For multi-agent workflows, agents write to shared artifact folders:

```text
temp/AGENT_REPORTS/[feature-name]/
├── PM_REPORT.md          # Product Manager scope and decisions
├── ARCH_REPORT.md        # Architect design and trade-offs
├── TEST_SPEC.md          # Tester coverage and test plan
├── DEV_REPORT.md         # Developer implementation notes
├── CODE_REVIEW.md        # Code reviewer findings
└── SECURITY_REVIEW.md    # Security reviewer assessment
```

**Workflow**: Orchestrators pass file paths, not content summaries. Downstream agents read upstream reports directly. See `docs/templates/agent-reports/` for templates.

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

## Git Worktrees (Parallel Development)

This project supports parallel Claude Code sessions using git worktrees. Each worktree provides an isolated directory with its own branch.

### Detecting Worktree Context

Check if you are in a worktree or the main repo:

```bash
git worktree list  # Shows all worktrees
pwd                # Current directory
git branch --show-current  # Current branch
```

**Directory naming**: `dbt-playground--{branch-slug}` (e.g., `dbt-playground--tuva`)

### Worktree Workflow Rules

| Rule | Rationale |
|------|-----------|
| One branch per worktree | Git enforces this to prevent conflicts |
| Commit early and often | Per-model or per-feature granularity |
| Push after each commit | So other worktrees see changes via `git fetch` |
| Draft PRs at worktree creation | Track work-in-progress in GitHub |

### State Tracking

- **WORKFLOW_STATE.md** lives in the **main repo** (`temp/WORKFLOW_STATE.md`)
- PR description is the source of truth for feature scope
- Each worktree may have local state but it is not committed

### Key Commands

```bash
# Create worktree with new branch
git worktree add ../dbt-playground--feat-x -b feat/x main

# List all worktrees
git worktree list

# Remove worktree after merge
git worktree remove ../dbt-playground--feat-x
```

**Full guide**: See `docs/for_chris/GIT-WORKTREE-WORKFLOW.md`

## Interactive Playgrounds

Visual tools for learning and development. Launch via commands or explore the HTML files directly.

| Playground | Command | Purpose | Status |
|------------|---------|---------|--------|
| Workflow Hub | `/playground:hub` | Central command center, session resume | ✅ v0.6.0 |
| Workflow Chronicle | `/playground:chronicle` | Timeline visualization, health pulse, agent tracking | ✅ v0.7.0 |
| Worktree Coordinator | `/playground:worktrees` | Manage parallel git worktree sessions | ✅ v0.6.0 |
| Mermaid Designer | `/playground:mermaid` | Create architecture diagrams visually | ✅ v0.6.0 |
| Agent Visualizer | `/playground:agents` | View agent workflows and handoffs | Planned v0.7.1 |
| Schema Explorer | `/playground:schema` | Browse Synthea healthcare data | Planned v0.7.1 |
| Lineage Explorer | `/playground:lineage` | Trace dbt data flow | Planned v0.7.2 |
| Dashboard Builder | `/playground:dashboards` | Mock analytics layouts | Planned v0.7.3 |

**Quick Start**: Run `/playground` to open the Workflow Hub (default entry point).

**Location**: `playgrounds/` directory contains single-file HTML implementations.

See `docs/for_chris/PLAYGROUND-TOOLS.md` for detailed guide.

## GitHub Actions (CI/CD)

Automated enforcement via GitHub Actions provides server-side checks that cannot be bypassed.

### Active Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| PR Validation | PR open/edit | Enforce conventional commit titles |
| Issue Linker | PR open/edit | Require issue references |
| PR Labeler | PR open/sync | Auto-apply type/size/layer labels |
| dbt Tests | PR + push to main | Run dbt build and tests |

### PR Requirements

For a PR to pass all checks:

1. **Title format**: `type(scope): description` (e.g., `feat(staging): add model`)
2. **Issue reference**: `Closes #N` or `Related to #N` in description
3. **dbt tests pass**: If dbt files changed

### Quick Commands

```bash
# View PR check status
gh pr checks

# View recent workflow runs
gh run list

# Re-run failed workflow
gh run rerun <run-id> --failed
```

**Documentation**:

- `docs/reference/GITHUB_ENFORCEMENT.md` - Workflow details
- `docs/reference/GITHUB_ACTIONS.md` - Quick reference
- `docs/for_chris/GITHUB_ACTIONS_GUIDE.md` - Setup and testing guide

## Notes for Claude

- ASK rather than assume
- Default to simpler solutions
- Explain technical decisions
- Use agents for complex work, manual for simple tasks
