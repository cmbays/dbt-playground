---
audience: [architect, developer]
priority: high
size: medium
dependencies: [PROJECT_STRUCTURE]
last_updated: 2026-01-28
status: active
tags: [reference, architecture, technical]
---

# Architecture Overview

## Project Architecture

### High-Level Structure

```
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
│         dbt Project (TBD)               │
│                                         │
│  Models, Sources, Tests, Documentation  │
│  dbt-mcp integration                    │
└─────────────────────────────────────────┘
```

### Key Architectural Decisions

**1. Agent-First Development**
- Multi-persona system for specialized tasks
- Structured workflows (PRD → TDD → Implementation)
- Git governance via git-master agent

**Benefits**:
- Consistent development patterns
- Quality gates at each phase
- Knowledge accumulation via Sage persona

**2. Documentation-Driven**
- Living documentation kept current
- PRDs for requirements
- TDDs for technical specifications

**Benefits**:
- Clear requirements before implementation
- Traceable decisions
- Onboarding support for future development

**3. dbt for Data Transformation (Planned)**
- SQL-based transformations
- Version-controlled data models
- Built-in testing and documentation

**Benefits**:
- Industry-standard data tooling
- Reproducible transformations
- Self-documenting data pipelines

---

## Agent Orchestration Architecture

### Persona System

```
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

```
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
- **Documentation**: Markdown with YAML frontmatter
- **Version Control**: Git with conventional commits
- **Agent System**: Claude Code with MCP servers
- **Hooks**: JavaScript-based pre/post tool hooks

### Planned (dbt Integration)
- **dbt**: Data transformation framework
- **SQL**: Data modeling language
- **dbt-mcp**: AI-assisted dbt development
- **Database**: TBD (PostgreSQL, DuckDB, etc.)

---

## File Organization

For complete directory structure, see **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)**.

**Key organizational principles**:
- **Documentation hierarchy** (docs/, temp/)
- **Agent configuration** (.claude/)
- **Work-in-progress isolation** (temp/)
- **Version control** via git tags (no separate archive needed)

---

## Future Considerations

### dbt Project Structure (When Added)

```
dbt-playground/
├── models/           # dbt models
│   ├── staging/      # Source transformations
│   ├── intermediate/ # Business logic
│   └── marts/        # Analytics-ready tables
├── tests/            # Data tests
├── macros/           # Reusable SQL
├── seeds/            # Static data
└── dbt_project.yml   # dbt configuration
```

### MCP Server Integration

- **dbt-mcp**: For AI-assisted dbt development
- **Playwright MCP**: For web-based testing/visualization

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
- [[../.claude/agents/AGENTS.md]] - Agent orchestration guide
- [[../.claude/rules/git-workflow.md]] - Git standards

---

*Last Updated: 2026-01-28*
