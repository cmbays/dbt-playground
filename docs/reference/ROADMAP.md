---
audience: [pm, architect]
priority: medium
size: medium
dependencies: []
last_updated: 2026-01-31
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

### v0.4.0 - Dimensional Models

**Theme**: Kimball Dimensional Modeling

**Status**: Complete (2026-01-30)

**Deliverables**:

- [x] 5 dimension tables (patients, providers, organizations, payers, date)
- [x] 4 fact tables (encounters, clinical_events, monthly/yearly aggregates)
- [x] 2 intermediate models (enriched encounters, patients with conditions)
- [x] 1 SCD Type 2 snapshot (patient demographics)
- [x] Comprehensive testing and documentation

### v0.5.0 - Analytics Layer

**Theme**: Healthcare Analytics & BI Integration

**Status**: Complete (2026-01-30)

**Deliverables**:

- [x] 7 analytics models (conditions, patient summary, provider metrics, cohorts, cost analysis)
- [x] 2 analytical views (current conditions, active patients)
- [x] 91 data quality tests (dbt_expectations patterns)
- [x] BI integration guide (Tableau, Looker, Power BI, Metabase, Superset)

### v0.6.0 - Playgrounds & Agent Context

**Theme**: Developer Tools & Workflow Management

**Status**: Complete (2026-01-31)

**Deliverables**:

- [x] Interactive playgrounds (Workflow Hub, Worktree Coordinator, Mermaid Designer)
- [x] Inter-agent report templates and workflow
- [x] Session summary templates
- [x] Agent job descriptions and orchestration docs

---

## Current Phase

### v0.7.0 - Workflow Hub Enhancements (In Progress)

**Theme**: Multi-Session Orchestration

**Goals**:

- Session state management and persistence
- Resume capability across sessions
- Token usage tracking and visualization
- Workflow health monitoring

**Deliverables**:

- [ ] PRD-019: Workflow Hub v0.7 specification
- [ ] Technical design document (TDD-019)
- [ ] Enhanced Workflow Hub with session management
- [ ] Integration with Claude Code CLI

**Related Issues**: #85 (Epic), #86 (Research)

---

## Upcoming Phases

### GitHub Actions Enforcement (Phased)

**Theme**: Automated Quality Gates

**Status**: Phase 1 Complete (2026-01-31)

**Completed** (Phase 1 - MVP):

- [x] PR validation (conventional commits)
- [x] Issue linking enforcement
- [x] Auto-labeling (type, size, layer)
- [x] dbt CI tests

**Planned** (Phases 2-4):

- [ ] Phase 1b: Branch protection rules
- [ ] Phase 2: CHANGELOG enforcement, agent tracker, stale PR notifier
- [ ] Phase 3: Secrets scanner, WIP detector, lint checks, dbt docs generator
- [ ] Phase 4: Merge audit, release notes, admin compliance reports

**Related**: See `docs/plans/GITHUB_ACTIONS_PLAN.md` for full 4-phase roadmap

### Data Quality Enhancements

**Theme**: Advanced Testing & Monitoring

**Status**: Planned

**Goals**:

- Expand dbt_expectations usage
- Create singular tests for complex business rules
- Generate and deploy dbt documentation site
- Implement data freshness monitoring

**Related Issues**: #35, #36, #37

### Epic E13: Decision Management (ADR Adoption)

**Theme**: Formalized Decision Tracking

**Status**: Phase 1 Complete (2026-01-31)

**Problem**: Technical decisions are made but not systematically findable. We spend time re-discovering rationale and re-debating settled questions.

**Goal**: Reduce decision archaeology time by 80% (decisions findable in <2 minutes).

**Phases**:

| Phase | Version | Status | Deliverables |
|-------|---------|--------|--------------|
| Phase 1: Foundation | v0.7 | Complete | TDD-TEMPLATE ADR section, ADR_INDEX.md with 5 ADRs |
| Phase 2: Integration | v0.8 | Planned | ADR-to-LEARNINGS promotion, Sage integration, historical backfill |
| Phase 3: Maturity | v0.9+ | Planned | Metrics, FOR_CHRIS doc, template refinement |

**Phase 1 Deliverables** (Complete):

- [x] PRD-021: ADR Adoption Initiative
- [x] TDD-TEMPLATE.md updated with ADR section and examples
- [x] ADR_INDEX.md created with TDD-001 entries (ADR-1 through ADR-5)
- [x] Significance criteria and approval chain documented

**Phase 2 Deliverables** (Planned):

- [ ] ADR-to-LEARNINGS promotion workflow
- [ ] Sage persona update for promotion reviews
- [ ] Session resume checklist with ADR review
- [ ] 3-5 historical ADRs backfilled from v0.3-v0.6

**Phase 3 Deliverables** (Quarterly):

- [ ] ADR adoption metrics (count, promotion rate)
- [ ] FOR_CHRIS: Understanding Decision-Making Patterns
- [ ] Template refinements based on usage

**Related**: [PRD-021](../specs/PRD-021-ADR-ADOPTION.md), [ADR_INDEX](./ADR_INDEX.md)

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

*Last Updated: 2026-01-31*
