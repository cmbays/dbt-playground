---
audience: [multi-agent]
priority: high
size: medium
dependencies: []
last_updated: 2026-01-28
status: active
tags: [reference, structure, organization]
---

# Project Structure

## Directory Overview

```
dbt-playground/
├── CLAUDE.md                  # Project context for Claude (auto-loaded)
├── README.md                  # Public readme
├── CHANGELOG.md               # Version history
├── DOCUMENTATION_INDEX.md     # Documentation navigation
│
├── docs/                      # Documentation
│   ├── reference/            # Technical reference docs
│   │   ├── PROJECT_STRUCTURE.md  # This file
│   │   ├── ARCHITECTURE.md
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

### Adding New Features

1. Create PRD in `docs/specs/PRD-XXX.md`
2. Create TDD in `docs/tdd/TDD-XXX.md`
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

*Last Updated: 2026-01-28*
