---
audience: [pm, architect]
priority: medium
size: medium
dependencies: []
last_updated: 2026-01-29
status: active
tags: [reference, roadmap, planning]
---

# dbt-playground Roadmap

## Vision

Build a dbt analytics project while learning data transformation best practices and AI-assisted development with dbt-mcp.

## Completed Phases

### v0.1.0 - Foundation

**Theme**: Project Setup & Agent Orchestration

**Status**: Complete (2026-01-28)

**Deliverables**:

- [x] Agent orchestration with 16 personas
- [x] 21 workflow skills including 6 dbt-specific
- [x] 13 slash commands
- [x] dbt project initialization
- [x] Database connection (DuckDB)
- [x] dbt-mcp integration

### v0.2.0 - Environment Ready

**Theme**: Source Data & uv Workflow

**Status**: Complete (2026-01-29)

**Deliverables**:

- [x] 16 Synthea source tables defined
- [x] uv workflow modernized (pyproject.toml, uv.lock)
- [x] Pre-commit hooks (markdownlint, yamllint, sqlfluff)
- [x] dbt-mcp configured

### v0.3.0 - Staging Layer

**Theme**: First Data Transformations

**Status**: Complete (2026-01-29)

**Deliverables**:

- [x] 9 staging models (440K+ rows)
- [x] 80 data tests (all passing)
- [x] Comprehensive model documentation
- [x] load_synthea_sources macro
- [x] Surrogate key patterns

---

## Current Phase

### v0.4.0 - Intermediate Layer (Next)

**Theme**: Business Logic & Transformations

**Goals**:

- Build intermediate models with business logic
- Implement date spine for time series
- Create reusable macros
- Add data quality assertions

**Deliverables**:

- 5-10 intermediate models
- Custom macro library
- Advanced testing patterns

---

## Upcoming Phases

### v0.5.0 - Marts Layer

**Theme**: Analytics-Ready Models

**Goals**:

- Build fact and dimension tables
- Implement Kimball dimensional modeling
- Create aggregated metrics
- Documentation generation

**Deliverables**:

- Complete dimensional model
- Generated dbt docs
- BI-ready tables

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

*Last Updated: 2026-01-29*
