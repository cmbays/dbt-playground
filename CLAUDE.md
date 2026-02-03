# dbt-playground - Project Context

## Project Purpose

This is a dbt learning project for data transformation best practices, agent orchestration, and dbt-mcp integration.

**Key Philosophy**: Leave the codebase better than you found it. Fight entropy.

## Current Phase

**Status**: v0.8.0 - Data Quality Quarantine Complete (2026-02-01)

- dbt 1.11.2 + duckdb-adapter 1.10.0 working
- 31 models total (staging, intermediate, dimensional, analytics, quarantine)
- 425 tests passing (0 errors) - improved from 405 PASS, 2 ERROR
- **Data Quality Quarantine System** (v0.8 Phase 5):
  - 3 reusable macros: `add_dq_flags()`, `quarantine_filter()`, `generate_quarantine_model()`
  - 2 quarantine tables: encounters (1 record), medications (5 records)
  - DQ monitoring mart: `mart_dq_summary` with entity-level metrics
  - Individual validation flags for precise debugging
  - 6 records quarantined (0.006% rate)
  - Documentation: ADR-004, reference guide, macro README
- Interactive playgrounds: Workflow Hub, Workflow Chronicle, Worktree Coordinator, Mermaid Designer, Agent Visualizer
- Agent context management with inter-agent reports
- uv workflow fully implemented (pyproject.toml, uv.lock, PEP 723 scripts)
- GitHub Actions automation: PR validation, issue linking, auto-labeling, dbt CI tests
- Issue creation CLI with YAML batch templates (`scripts/github-ops.py`)
- Milestone tracking with CLI commands and CLAUDE.md status section
- Enhanced PR-Issue linking with extended keyword support
- GitHub Projects integration using built-in automation
- ADR tracking: 14 ADRs indexed (ADR-004: quarantine pattern)

**Next**: v0.9 - TBD (incremental models, advanced analytics, or monitoring)

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

## Testing

### Test Best Practices

- Always use `datetime.now(UTC)` for timezone-aware timestamps
- Use fixed test dates for determinism: `TEST_DATE = datetime(2026, 2, 15, tzinfo=UTC)`
- Explicit `encoding='utf-8'` on all file open() operations
- Specific exception handling: `except CalledProcessError` not `except Exception`
- Test coverage artifacts (.coverage, htmlcov/, coverage.xml) are gitignored

### Running Tests

```bash
uv run pytest tests/ -v                    # Full test suite
uv run pytest tests/ -v --tb=short         # Abbreviated tracebacks
uv run pytest tests/ -q --tb=no            # Quick run, no output
```

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

### Multi-Agent Orchestration Patterns

**Parallel Execution**: Launch multiple agents concurrently using single message with multiple Task calls:

```bash
# Example: Launch 2 agents in parallel
Task(subagent_type="code-reviewer", prompt="Review scripts/")
Task(subagent_type="security-reviewer", prompt="Review for vulnerabilities")
```

**Competitive Implementation**: For complex features, use competing teams:

1. **Planning Phase**: Assemble team to create initial plan
2. **Review Phase**: Spin up second team to review and identify gaps
3. **Implementation Phase**: Launch competing teams (Alpha/Beta) to independently solve
4. **Convergence Phase**: Review both solutions and create hybrid/best-of-breed

**Benefits**:
- Reduces single-point-of-failure in design decisions
- Surfaces alternative approaches
- Higher quality through competitive pressure

**Example workflow** (FS1 Agent Memory):
- Planning team → Review team → Gap analysis → Competing implementation → Final convergence

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
| `/readiness-check` | Assess capability gaps before new work |

## Session Memory (v0.10+)

The Agent Memory System enables compound learning across sessions through persistent logging and automated pattern extraction.

### Directory Structure

```text
memory/
  |-- 2026-02-02.md       # Daily append-only session log
  |-- MEMORY_INDEX.md     # Weekly summary and pattern index
  |-- events.jsonl        # Machine-readable events for metrics
```

### Quick Commands

| Command | Purpose |
|---------|---------|
| `sage: log session` | Full interactive session logging |
| `sage: log "[task]"` | Quick log with auto-defaults |
| `sage: consolidate week` | Weekly pattern extraction |
| `uv run scripts/log-session.py` | CLI session logging |
| `uv run scripts/consolidate-memory.py` | CLI consolidation |

### Session Logging

```bash
# Quick mode - minimal input
uv run scripts/log-session.py -t "Implemented feature X" -o SUCCESS

# Interactive mode - full prompts
uv run scripts/log-session.py

# With task ID for Kanban correlation
uv run scripts/log-session.py -t "Task description" -i TASK-42
```

### Pattern Detection

Weekly consolidation scans logs for recurring patterns:
- Patterns with 2+ occurrences are identified (appeared at least twice)
- Multi-factor scoring: frequency (40%), recency (30%), consistency (30%)
- Promotion candidates can be added to LEARNINGS.md

```bash
# Run weekly consolidation
uv run scripts/consolidate-memory.py

# Preview without writing
uv run scripts/consolidate-memory.py --dry-run
```

See `.claude/agents/sage.md` for Workflow J (logging) and Workflow K (consolidation) details.

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
| Agent Visualizer | `/playground:agents` | View agent workflows and handoffs | ✅ v0.7.1 |
| Schema Explorer | `/playground:schema` | Browse Synthea healthcare data | Planned v0.7.2 |
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
| Task File Sync | Issue open/close | Auto-create/archive task files |

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

## Self-Hosted GitHub Actions Runner

This project uses a self-hosted runner for CI to avoid consuming GitHub Actions minutes on the private repository.

### For Users

**Daily workflow**:

1. Start runner before development: `./scripts/runner-start.sh`
2. Work normally (CI runs on local machine)
3. Stop runner when done: `./scripts/runner-stop.sh`

**Quick commands**:

| Command | Purpose |
|---------|---------|
| `./scripts/runner-start.sh` | Start runner (keep terminal open) |
| `./scripts/runner-stop.sh` | Stop runner |
| `./scripts/runner-status.sh` | Check status + recent runs |

**First-time setup**: `./scripts/setup-github-runner.sh`

**Full guide**: `docs/for_chris/SELF_HOSTED_RUNNER_GUIDE.md`

### For Agents

**CRITICAL**: CI jobs will queue indefinitely if runner is not running.

**Before CI operations**:

1. Check runner status: `./scripts/runner-status.sh`
2. If not running, inform user: "GitHub Actions runner is not running. Please start it with `./scripts/runner-start.sh`"
3. If CI jobs are queued: Verify runner is online at GitHub Settings → Actions → Runners
3. Do NOT attempt to start/stop runner automatically

**CI operations requiring runner**:

- Pushing commits that trigger workflows
- Creating/updating PRs
- Running dbt tests via CI

**Important**: Agents should NEVER start or stop the runner. Only inform the user if it's needed.

## Milestone Status

Tracking progress toward v0.8, v0.10, and v1.0 releases.

| Milestone | Target | Open | Closed | Progress |
|-----------|--------|------|--------|----------|
| v0.7.0 | Jan 31, 2026 | 0 | 4 | 100% (Complete) |
| v0.8.0 | Feb 1, 2026 | 0 | 5 | 100% (Complete) |
| v0.9 | Mar 31, 2026 | 0 | 15 | 100% (Complete) |
| v0.10 | Apr 30, 2026 | 20 | 0 | Planned |
| v1.0 | Jun 30, 2026 | 2 | 0 | Planned |

### v0.10 Feature Sets (Agent Orchestration)

| Feature Set | Epic | Status |
|-------------|------|--------|
| Agent Memory & Learning | #143 | Planned |
| Kanban Workflow Engine | #144 | Planned |
| QA & Testing Enforcement | #145 | Planned |
| Metrics & Dashboard | #146 | Planned |
| GitHub Integration | #147 | Planned |

See `docs/specs/ROADMAP-v0.10.md` for detailed planning.

**Update Command**:

```bash
gh api repos/{owner}/{repo}/milestones --jq '.[] | "\(.title): \(.open_issues) open, \(.closed_issues) closed"'
```

## Notes for Claude

- ASK rather than assume
- Default to simpler solutions
- Explain technical decisions
- Use agents for complex work, manual for simple tasks
- Address CodeRabbit feedback in batches by category (tests, exceptions, formatting)
- When user corrects you, those corrections reveal gaps in best practices
- Pre-existing linting failures ≠ new failures - document the distinction
- Include ADRs in the same PR as the feature they document
- Group related fixes into themed commits for easier review
