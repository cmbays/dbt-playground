# dbt-playground Project Roadmap

## Project Vision

Transform the dbt-playground into a fully operational dbt learning environment using synthetic healthcare data (Synthea) with DuckDB, enabling AI-assisted data modeling through MCP integration.

## Goals

1. **Learn dbt fundamentals** through hands-on implementation
2. **Practice dimensional modeling** with realistic healthcare data
3. **Enable AI-assisted development** via dbt-mcp integration
4. **Establish data quality patterns** through comprehensive testing
5. **Document learnings** for future reference and skill development

---

## Epics Overview

| Epic | Name | Description | Version Target |
|------|------|-------------|----------------|
| E1 | Environment Setup | DuckDB, dbt-duckdb adapter, profiles, MCP configuration | v0.2.0 |
| E2 | Data Acquisition | Synthea generation, CSV loading, data exploration | v0.2.0 |
| E3 | Staging Layer | 9 staging models with source definitions and basic tests | v0.3.0 |
| E4 | Dimensional Models | Facts, dimensions, intermediate models for analytics | v0.4.0 |
| E5 | Testing & Quality | Comprehensive testing, documentation, semantic layer | v0.5.0 |
| E6 | MCP Integration | AI-assisted workflows, agent verification | v0.5.0 |

---

## Epic Details

### E1: Environment Setup

**Goal**: Establish a working dbt development environment with DuckDB and MCP tooling.

**PRD**: [PRD-001-ENVIRONMENT-SETUP](../specs/PRD-001-ENVIRONMENT-SETUP.md)

**Scope**:

- Install dbt-duckdb adapter
- Create and configure `~/.dbt/profiles.yml`
- Initialize dbt project structure
- Configure `.mcp.json` for dbt-mcp
- Update `.gitignore` for dbt artifacts

**Agent Assignments**:

| Task | Primary Agent | Supporting |
|------|---------------|------------|
| Profile configuration | developer | architect |
| Project initialization | dbt-developer | - |
| MCP configuration | developer | architect |
| Verification | dbt-tester | - |

**Success Criteria**:

- `dbt debug` passes successfully
- `dbt deps` installs packages
- MCP server responds to queries

**Dependencies**: None (starting point)

---

### E2: Data Acquisition

**Goal**: Generate or obtain Synthea synthetic healthcare data and make it accessible to dbt.

**PRD**: [PRD-002-DATA-ACQUISITION](../specs/PRD-002-DATA-ACQUISITION.md)

**Scope**:

- Generate 500 synthetic patients via Synthea
- Copy CSV files to `dbt_project/data/synthea/`
- Verify CSV structure and row counts
- Create data exploration queries

**Agent Assignments**:

| Task | Primary Agent | Supporting |
|------|---------------|------------|
| Synthea generation | developer | - |
| Data verification | dbt-tester | - |
| Exploration queries | data-modeler | - |

**Success Criteria**:

- All 9+ CSV files present in data directory
- Each file has expected columns
- DuckDB can read all CSVs via `read_csv_auto()`

**Dependencies**: E1 (Environment Setup)

---

### E3: Staging Layer

**Goal**: Create clean, typed staging models for all Synthea source tables with documentation and basic tests.

**PRD**: [PRD-003-STAGING-LAYER](../specs/PRD-003-STAGING-LAYER.md)

**Scope**:

- Create `_synthea__sources.yml` source definition
- Implement 9 staging models:
  - `stg_synthea__patients`
  - `stg_synthea__encounters`
  - `stg_synthea__conditions`
  - `stg_synthea__medications`
  - `stg_synthea__procedures`
  - `stg_synthea__observations`
  - `stg_synthea__providers`
  - `stg_synthea__organizations`
  - `stg_synthea__payers`
- Add schema tests (unique, not_null)
- Document all models and columns

**Agent Assignments**:

| Task | Primary Agent | Supporting |
|------|---------------|------------|
| Source definition | data-modeler | - |
| Model design | data-modeler | architect |
| Model implementation | dbt-developer | - |
| Schema tests | dbt-tester | - |
| Documentation | dbt-documenter | - |
| Code review | code-reviewer | - |

**Success Criteria**:

- All 9 staging models compile and run
- `dbt test` passes for staging layer
- All models documented with descriptions
- Consistent naming conventions applied

**Dependencies**: E2 (Data Acquisition)

---

### E4: Dimensional Models

**Goal**: Build dimensional models (facts and dimensions) for healthcare analytics.

**PRD**: [PRD-004-DIMENSIONAL-MODELS](../specs/PRD-004-DIMENSIONAL-MODELS.md)

**Scope**:

**Dimension Models**:

- `dim_patients` - Patient demographics and attributes
- `dim_providers` - Healthcare provider information
- `dim_organizations` - Healthcare facilities
- `dim_date` - Calendar dimension for time-based analysis

**Fact Models**:

- `fct_encounters` - Healthcare visits/encounters
- `fct_clinical_events` - Unified clinical events (conditions, medications, procedures)

**Intermediate Models**:

- `int_encounters__enriched` - Encounters with computed fields
- `int_patients__with_conditions` - Patients with condition history

**Agent Assignments**:

| Task | Primary Agent | Supporting |
|------|---------------|------------|
| Dimensional design | data-modeler | architect |
| Dimension implementation | dbt-developer | - |
| Fact implementation | dbt-developer | - |
| Intermediate models | dbt-developer | data-modeler |
| Testing | dbt-tester | - |
| Documentation | dbt-documenter | - |
| Code review | code-reviewer | - |

**Success Criteria**:

- All dimension and fact models compile and run
- Referential integrity tests pass
- Documentation complete for all marts models
- Query performance acceptable for analytics

**Dependencies**: E3 (Staging Layer)

---

### E5: Testing & Quality

**Goal**: Implement comprehensive testing, documentation site, and data quality monitoring.

**Scope**:

- Add `dbt_expectations` tests for data quality
- Create singular tests for business rules
- Generate and serve dbt docs
- Add source freshness monitoring
- Create README documentation

**Agent Assignments**:

| Task | Primary Agent | Supporting |
|------|---------------|------------|
| dbt_expectations tests | dbt-tester | - |
| Singular tests | dbt-tester | data-modeler |
| Documentation site | dbt-documenter | - |
| Source freshness | dbt-developer | - |

**Success Criteria**:

- `dbt test` passes all tests
- `dbt docs serve` displays documentation site
- Source freshness configured and monitoring
- All models have 80%+ column documentation

**Dependencies**: E4 (Dimensional Models)

---

### E6: MCP Integration

**Goal**: Verify and optimize AI-assisted dbt development workflows.

**Scope**:

- Test all MCP tools (discovery, SQL, CLI)
- Verify agent workflows (model, test, document)
- Create agent workflow documentation
- Validate semantic layer queries (if applicable)

**Agent Assignments**:

| Task | Primary Agent | Supporting |
|------|---------------|------------|
| MCP tool testing | developer | dbt-developer |
| Agent workflow verification | sage | all dbt agents |
| Documentation | dbt-documenter | sage |

**Success Criteria**:

- All MCP tools functional
- Agent team can create/test/document models via MCP
- Workflow documented in LEARNINGS.md

**Dependencies**: E5 (Testing & Quality)

---

## Milestones

### M1: v0.2.0 - Foundation

**Target**: Week 1

**Scope**: Epics E1 + E2

**Deliverables**:

- Working dbt environment with DuckDB
- Synthea data loaded and accessible
- MCP configuration in place
- `dbt debug` passes

**Success Metrics**:

- [ ] `dbt debug` shows successful connection
- [ ] `dbt compile` completes without errors
- [ ] All 9 Synthea CSVs present and readable
- [ ] MCP server responds to health check

---

### M2: v0.3.0 - Staging Complete

**Target**: Week 2

**Scope**: Epic E3

**Deliverables**:

- All 9 staging models implemented
- Source definitions complete
- Basic schema tests passing
- Model documentation in place

**Success Metrics**:

- [ ] `dbt run --select staging` completes
- [ ] `dbt test --select staging` passes
- [ ] All staging models have descriptions
- [ ] Naming conventions consistent (`stg_synthea__*`)

---

### M3: v0.4.0 - Analytics Ready

**Target**: Week 3

**Scope**: Epic E4

**Deliverables**:

- All dimension models implemented
- All fact models implemented
- Intermediate models for complex logic
- Referential integrity tests

**Success Metrics**:

- [ ] `dbt run` completes for all models
- [ ] `dbt test` passes all tests
- [ ] Lineage graph shows proper dependencies
- [ ] Query performance meets expectations

---

### M4: v0.5.0 - Production Quality

**Target**: Week 4

**Scope**: Epics E5 + E6

**Deliverables**:

- Comprehensive test suite
- Documentation site generated
- MCP integration verified
- Agent workflows documented

**Success Metrics**:

- [ ] `dbt test` runs 50+ tests
- [ ] `dbt docs serve` shows complete documentation
- [ ] All MCP tools functional
- [ ] LEARNINGS.md updated with patterns

---

## Dependency Graph

```text
E1 Environment Setup
    │
    ▼
E2 Data Acquisition
    │
    ▼
E3 Staging Layer
    │
    ▼
E4 Dimensional Models
    │
    ├─────────────┐
    ▼             ▼
E5 Testing    E6 MCP Integration
    │             │
    └──────┬──────┘
           ▼
      v0.5.0 Complete
```

---

## Agent Team Assignments

### Primary Responsibilities

| Agent | Primary Areas | Epic Focus |
|-------|---------------|------------|
| **data-modeler** | Model design, naming, relationships | E3, E4 |
| **dbt-developer** | SQL implementation, Jinja, optimization | E1, E3, E4 |
| **dbt-tester** | Schema tests, singular tests, freshness | E2, E3, E4, E5 |
| **dbt-documenter** | Model docs, column descriptions, site | E3, E4, E5 |
| **developer** | Environment, MCP, scripts | E1, E2, E6 |
| **architect** | Design decisions, technical direction | E1, E4 |
| **code-reviewer** | Code quality, patterns, standards | E3, E4 |
| **sage** | Learning extraction, pattern documentation | E6 |

### Assembly Line for dbt Models

```text
For each model:

1. data-modeler  → Design model (grain, columns, relationships)
2. dbt-developer → Implement SQL with Jinja
3. dbt-tester    → Add schema and singular tests
4. code-reviewer → Review for patterns and quality
5. dbt-documenter → Add descriptions and examples
```

---

## Risk Mitigation

| Risk | Mitigation | Owner |
|------|------------|-------|
| Synthea Java dependency | Provide pre-generated CSV option | developer |
| DuckDB path issues | Document absolute path requirements | architect |
| MCP compatibility | Test early in E1, have fallback workflow | developer |
| Data quality issues | Validate CSVs before model development | dbt-tester |
| Scope creep | PRDs define clear boundaries per epic | pm (this role) |

---

## Related Documentation

- [Implementation Plan](./DBT-PROJECT-INITIALIZATION.md) - Detailed technical plan
- [GitHub Issues](./GITHUB-ISSUES.md) - Actionable work items
- [Architecture](../reference/ARCHITECTURE.md) - System design
- [Agent Guide](../../.claude/agents/AGENTS.md) - Agent orchestration

---

*Last Updated: 2026-01-28*
*Status: Active Planning*
