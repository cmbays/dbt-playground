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
├── CLAUDE.md                  # Project context for Claude (auto-loaded)
├── README.md                  # Public readme
├── CHANGELOG.md               # Version history
├── DOCUMENTATION_INDEX.md     # Documentation navigation
│
├── pyproject.toml             # Python project config (uv)
├── uv.lock                    # Locked dependency versions
├── .python-version            # Python version (3.11)
│
├── dbt_project/               # dbt Project
│   ├── dbt_project.yml           # dbt configuration
│   ├── packages.yml              # dbt packages
│   ├── models/                   # dbt models
│   │   ├── staging/              # Source transformations
│   │   ├── intermediate/         # Business logic
│   │   └── marts/                # Analytics-ready tables
│   ├── seeds/                    # Static data
│   ├── macros/                   # Reusable SQL
│   ├── tests/                    # Data tests
│   ├── snapshots/                # SCD tracking
│   └── analyses/                 # Ad-hoc queries
│
├── docs/                      # Documentation
│   ├── reference/            # Technical reference docs
│   │   ├── PROJECT_STRUCTURE.md  # This file
│   │   ├── ARCHITECTURE.md
│   │   ├── UV_MIGRATION.md       # uv workflow guide
│   │   └── LEARNINGS.md
│   ├── guides/               # How-to guides
│   ├── standards/            # Rules and conventions
│   ├── specs/                # PRDs
│   └── tdd/                  # Technical Design Documents
│
├── temp/                      # Working Files (development)
│   ├── v[X.Y]_PLAN.md
│   ├── v[X.Y]_TESTING.md
│   └── [prototype files]
│
├── scripts/                   # Build & Utility Scripts
│
├── playgrounds/               # Interactive Visual Tools
│   ├── worktree-coordinator.html  # Git worktree management
│   ├── agent-visualizer.html      # Agent workflow visualization
│   ├── schema-explorer.html       # Healthcare data browser
│   ├── lineage-explorer.html      # dbt DAG explorer
│   └── dashboard-builder.html     # Analytics mockup tool
│
└── .claude/                   # Agent Configuration
    ├── agents/               # Persona definitions
    │   ├── AGENTS.md             # Orchestration guide
    │   ├── git-master.md         # Git operations agent
    │   ├── documenter.md         # Documentation agent
    │   └── [other personas]
    ├── commands/             # Slash commands
    │   ├── commit.md             # /commit - validated commits
    │   ├── branch.md             # /branch - validated branches
    │   ├── deploy.md             # /deploy - version deployment
    │   └── [other commands]
    ├── hooks/                # Pre/post tool hooks
    │   └── pre-bash-check.js     # Git enforcement, safety gates
    ├── rules/                # Coding standards
    │   ├── git-workflow.md       # Git conventions + Agent Git Governance
    │   ├── coding-style.md
    │   └── [other rules]
    └── skills/               # Workflow definitions
        ├── git-operations.md         # Git workflow steps
        ├── worktree-orchestration.md # Parallel development
        ├── deployment-workflow.md
        └── [other skills]
```

---

## For Developers

### Key Entry Points

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Project context - READ FIRST |
| `.claude/agents/AGENTS.md` | Agent orchestration guide |
| `docs/reference/ARCHITECTURE.md` | System architecture |
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

### Standard Process

```
1. UNDERSTAND → Read CLAUDE.md, docs/
2. PLAN       → Create temp/v[X.Y]_PLAN.md
3. PROTOTYPE  → Build prototype in temp/
4. BUILD      → Create implementation
5. VERIFY     → Test, document in temp/v[X.Y]_TESTING.md
6. DEPLOY     → Finalize, tag version
```

### File Protection Rules

**NEVER**:

- Overwrite files without backup
- Skip prototype step for new features
- Deploy without testing

**ALWAYS**:

- Work in temp/ first
- Test changes
- Update documentation

---

## Related Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design
- [CLAUDE.md](../../CLAUDE.md) - Project context
- [coding-style.md](../../.claude/rules/coding-style.md) - Standards
- [git-workflow.md](../../.claude/rules/git-workflow.md) - Version control

---

*Last Updated: 2026-01-29*
