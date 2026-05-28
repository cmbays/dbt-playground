---
audience: [architect, developer]
priority: high
size: medium
dependencies: [PROJECT_STRUCTURE]
last_updated: 2026-01-29
status: active
tags: [reference, architecture, technical]
---

# Architecture Overview

## Project Architecture

### High-Level Structure

```text
┌─────────────────────────────────────────┐
│         dbt-playground                  │
│    Data Analytics Development           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Agent Orchestration             │
│                                         │
│  Personas: PM, Arch, Dev, Review, etc.  │
│  Commands: /plan, /commit, /deploy      │
│  Skills: TDD, code-review, deployment   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      dbt Project (healthcare_analytics) │
│                                         │
│  16 Synthea sources, Staging models     │
│  DuckDB 1.10.0, dbt-mcp integration     │
└─────────────────────────────────────────┘
```

### Key Architectural Decisions

#### Agent-First Development

- Multi-persona system for specialized tasks
- Structured workflows (PRD → TDD → Implementation)
- Git governance via git-master agent

Benefits:

- Consistent development patterns
- Quality gates at each phase
- Knowledge accumulation via Sage persona

#### Documentation-Driven

- Living documentation kept current
- PRDs for requirements
- TDDs for technical specifications

Benefits:

- Clear requirements before implementation
- Traceable decisions
- Onboarding support for future development

#### dbt for Data Transformation

- SQL-based transformations (healthcare_analytics project)
- Version-controlled data models (staging, intermediate, marts)
- Built-in testing and documentation

Benefits:

- Industry-standard data tooling
- Reproducible transformations via uv-managed environment
- Self-documenting data pipelines

---

## Agent Orchestration Architecture

### Persona System

```text
┌─────────────────────────────────────────┐
│           Assembly Line Flow            │
├─────────────────────────────────────────┤
│ 1. PM         → Draft PRD               │
│ 2. Architect  → Create TDD              │
│ 3. Tester     → Write test spec         │
│ 4. Developer  → Implement               │
│ 5. Reviewers  → Code + Design review    │
│ 6. Documenter → Update docs             │
│ 7. Sage       → Extract learnings       │
└─────────────────────────────────────────┘
```

### Git Governance

```text
┌─────────────────────────────────────────┐
│         Git-Master Enforcement          │
├─────────────────────────────────────────┤
│ Layer 1: CLAUDE.md rules                │
│ Layer 2: pre-bash-check.js hook         │
│ Layer 3: git-master agent validation    │
└─────────────────────────────────────────┘
```

---

## Technology Stack

### Current

- **Python Environment**: uv-managed (pyproject.toml, uv.lock)
- **dbt**: Data transformation framework (dbt 1.11.2)
- **Database**: DuckDB 1.10.0 (dev.duckdb)
- **Documentation**: Markdown with YAML frontmatter
- **Version Control**: Git with conventional commits
- **Agent System**: Claude Code with MCP servers
- **Hooks**: JavaScript-based pre/post tool hooks

### Python Dependencies

| Package | Purpose |
|---------|---------|
| `dbt-duckdb>=1.10.0` | dbt adapter for DuckDB |
| `sqlfluff>=3.0.0` | SQL linting (dev) |
| `pre-commit>=3.7.0` | Git hooks (dev) |

### MCP Integration

- **dbt-mcp**: AI-assisted dbt development

---

## File Organization

For complete directory structure, see **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)**.

Key organizational principles:

- **Documentation hierarchy** (docs/)
- **Claude Code configuration** (.claude/)
- **Version control** via git tags

---

## Future Considerations

### dbt Project Structure

```text
dbt_project/
├── dbt_project.yml   # dbt configuration (healthcare_analytics)
├── packages.yml      # dbt packages (dbt-utils, codegen, etc.)
├── models/           # dbt models
│   ├── staging/      # Source transformations (16 Synthea tables)
│   ├── intermediate/ # Business logic
│   └── marts/        # Analytics-ready tables
├── tests/            # Data tests
├── macros/           # Reusable SQL
├── seeds/            # Static data
├── snapshots/        # SCD tracking
└── analyses/         # Ad-hoc queries
```

### MCP Server Integration

- **dbt-mcp**: For AI-assisted dbt development (configured in .mcp.json)

---

## Architectural Principles

1. **Documentation First**: Understand before implementing
2. **Agent Orchestration**: Use specialized personas for quality
3. **Git Governance**: All changes through proper workflow
4. **Test-Driven**: Write tests before implementation
5. **Learning Accumulation**: Capture patterns via Sage

---

## Related Documentation

- [[PROJECT_STRUCTURE.md]] - Detailed file organization
- [[../CLAUDE.md]] - Project context and workflow
- [[TECH_STACK.md]] - Technology versions and rationale

---

*Last Updated: 2026-01-29*
