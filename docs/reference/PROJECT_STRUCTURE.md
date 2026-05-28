---
audience: [multi-agent]
priority: high
size: medium
dependencies: []
last_updated: 2026-01-29
status: active
tags: [reference, structure, organization]
---

# Project Structure

## Directory Overview

**Note**: When using git worktrees for parallel development, worktree directories are siblings to the main repo (e.g., `../dbt-playground--feat-x/`). See [Git Worktree Workflow](../for_chris/GIT-WORKTREE-WORKFLOW.md).

```text
dbt-playground/
├── CLAUDE.md                  # Project context for Claude
├── README.md                  # Public readme
├── CHANGELOG.md               # Version history
│
├── pyproject.toml             # Python project config (uv)
├── uv.lock                    # Locked dependency versions
├── .python-version            # Python version (3.11)
│
├── .github/                   # GitHub Configuration
│   └── workflows/             # GitHub Actions
│       ├── dbt-test.yml             # dbt CI tests
│       ├── claude.yml               # @claude mention handler
│       └── claude-code-review.yml   # Claude PR review
│
├── dbt_project/               # dbt Project
│   ├── dbt_project.yml           # dbt configuration
│   ├── packages.yml              # dbt packages
│   ├── models/                   # dbt models
│   │   ├── staging/              # Source transformations (Synthea)
│   │   ├── intermediate/         # Business logic + quarantine
│   │   └── marts/                # core/ + analytics/
│   ├── seeds/                    # Static data
│   ├── macros/                   # Reusable SQL (incl. data quality)
│   ├── tests/                    # Singular data tests
│   ├── snapshots/                # SCD tracking
│   └── analyses/                 # Ad-hoc queries
│
├── docs/                      # Documentation
│   ├── reference/            # Technical reference docs
│   │   ├── PROJECT_STRUCTURE.md  # This file
│   │   ├── ARCHITECTURE.md
│   │   ├── TECH_STACK.md
│   │   ├── DBT_CODING_STANDARDS.md
│   │   ├── DBT_TESTING_STANDARDS.md
│   │   ├── DATA_QUALITY_QUARANTINE.md
│   │   └── UV_MIGRATION.md       # uv workflow guide
│   ├── specs/                # PRDs + TDDs (per layer)
│   ├── decisions/            # dbt ADRs
│   └── for_chris/            # Kimball + uv references
│
├── scripts/                   # Lint wrappers
│   ├── lint-sql.sh              # sqlfluff lint
│   ├── lint-yaml.sh             # yamllint
│   └── fix-sql.sh               # sqlfluff fix
│
└── .claude/                   # Claude Code config (dbt-focused)
    ├── agents/               # dbt-* + data-modeler, healthcare/semantic analyst
    ├── commands/             # /dbt-run, /dbt-test, /dbt-model, ...
    └── skills/               # dbt model dev, testing, deployment, ...
```

---

## For Developers

### Key Entry Points

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Project context - READ FIRST |
| `docs/reference/ARCHITECTURE.md` | System architecture |
| `docs/reference/TECH_STACK.md` | Technology versions |
| `docs/reference/UV_MIGRATION.md` | Python/uv workflow guide |

### Key Files

| File | Purpose | Git Tracked |
|------|---------|-------------|
| `pyproject.toml` | Project metadata, dependencies | Yes |
| `uv.lock` | Locked dependency versions | Yes |
| `.python-version` | Python version (3.11) | Yes |
| `.venv/` | Virtual environment | No |
| `dev.duckdb` | Development database | No |

### Adding New Features

1. Create PRD in `docs/specs/PRD-XXX.md`
2. Create TDD in `docs/specs/TDD-XXX.md`
3. Implement with test-driven development
4. Document in relevant files

---

## Development Workflow

1. Branch + PR for everything; never push directly to `main`.
2. Build and test models with `uv run dbt build` from `dbt_project/`.
3. Lint before pushing (`npm run lint`); the pre-push hook runs
   `dbt compile` and rejects hardcoded `database.schema.table` refs.
4. Update `CHANGELOG.md` for feat/fix PRs.

---

## Related Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design
- [CLAUDE.md](../../CLAUDE.md) - Project context
- [coding-style.md](../../.claude/rules/coding-style.md) - Standards
- [git-workflow.md](../../.claude/rules/git-workflow.md) - Version control

---

*Last Updated: 2026-01-29*
