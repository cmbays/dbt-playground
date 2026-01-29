---
audience: [pm, architect]
priority: medium
size: medium
dependencies: []
last_updated: 2026-01-28
status: active
tags: [reference, roadmap, planning]
---

# dbt-playground Roadmap

## Vision

Build a dbt analytics project while learning data transformation best practices and AI-assisted development with dbt-mcp.

## Current Phase

### Phase 0: Foundation (v0.1) - Current

**Theme**: Project Setup & Scaffolding

**Status**: In Progress

**Goals**:

- [x] Agent orchestration scaffold
- [x] Documentation framework
- [ ] dbt project initialization
- [ ] Database connection setup
- [ ] dbt-mcp integration

**Deliverables**:

- Working dbt project structure
- Connected database (local or cloud)
- dbt-mcp configured and functional

---

## Upcoming Phases

### Phase 1: Sample Data Project (v0.2)

**Theme**: First End-to-End Pipeline

**Goals**:

- Create sample source data (seeds or external)
- Build staging models
- Build intermediate models
- Build mart models
- Add data tests
- Document models

**Potential Data Domains**:

- E-commerce (orders, customers, products)
- SaaS metrics (users, events, subscriptions)
- Financial data (transactions, accounts)

**Deliverables**:

- Complete dbt project with 10-20 models
- Full test coverage
- Generated dbt docs

### Phase 2: Advanced Patterns (v0.3)

**Theme**: dbt Best Practices

**Goals**:

- Incremental models
- Snapshots (SCD Type 2)
- Custom macros
- Jinja templating
- Advanced testing patterns

**Deliverables**:

- Production-ready patterns demonstrated
- Macro library
- Testing utilities

### Phase 3: Integration & Automation (v0.4)

**Theme**: Production Workflows

**Goals**:

- CI/CD for dbt
- Data quality monitoring
- Documentation generation
- Orchestration patterns

**Deliverables**:

- Automated testing pipeline
- Quality dashboards or reports

---

## Future Considerations

### Potential Extensions

- **Multiple databases**: Test with different data warehouses
- **dbt Cloud**: Explore cloud deployment options
- **Semantic layer**: Implement dbt metrics/semantic layer
- **BI integration**: Connect to visualization tools

### Learning Objectives

1. **dbt Fundamentals**: Models, tests, docs, sources
2. **Data Modeling**: Dimensional modeling, fact/dimension design
3. **SQL Best Practices**: CTEs, window functions, optimization
4. **Data Quality**: Testing strategies, monitoring
5. **Agent-Assisted Development**: dbt-mcp workflows

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-28 | Start with local database | Simpler setup for learning |
| 2026-01-28 | Use agent orchestration | Practice multi-persona workflows |

---

## Related

- [[FUTURE_FEATURES.md]] - Feature ideas backlog
- [[../specs/]] - PRDs for approved features
- [[../tdd/]] - Technical designs
- [[../../CLAUDE.md]] - Project context

---

*Last Updated: 2026-01-28*
