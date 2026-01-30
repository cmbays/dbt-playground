---
title: Semantic Layer Foundation
prd_number: PRD-012
epic: E12-Semantic-Layer
version: 0.5.5
status: draft
author: pm
created: 2026-01-29
last_updated: 2026-01-29
---

## Overview

### Problem Statement

While dimensional models provide optimized structures for analytics, business users and BI tools often need standardized metric definitions to ensure consistent calculations across the organization. Without a semantic layer, metrics can be defined inconsistently in different queries, leading to conflicting results and eroded trust in data.

The dbt Semantic Layer (powered by MetricFlow) provides a way to define metrics once and expose them consistently. However, DuckDB has limited support for the MetricFlow query engine, requiring a hybrid approach.

### Goal

Establish a foundational metrics layer that provides consistent metric definitions for the healthcare analytics domain. Given DuckDB limitations with MetricFlow, **metric marts are the first rollout solution** - queryable SQL models that implement standardized metric calculations.

Full dbt Semantic Layer (YAML semantic models + MetricFlow) is deferred to a future phase when we evaluate warehouse solutions that support it (see Future Features).

### Success Metrics

- Metric mart model (`mrt_encounters_summary`) built and tested
- 4-5 core metrics implemented: total_encounters, total_claims_paid, avg_cost_per_encounter, patient_volume, avg_duration
- Metrics documented with business descriptions in schema YAML
- Example queries provided for business users
- Reconciliation tests pass (mart totals match source facts)

---

## Prerequisites

This feature should not be started until the following are complete:

| Prerequisite | Epic | Description | Verification |
|--------------|------|-------------|--------------|
| Dimensional Models | E4 | `fct_encounters`, `dim_patients`, `dim_date` stable | `dbt test --select marts` passes |
| Testing & Quality | E5 | Comprehensive tests on dimensional models | 80%+ test coverage on marts |
| Model Documentation | E5 | All mart models documented | `dbt docs generate` succeeds |

**Recommended timing**: v0.5.5 (after E5 Testing & Quality, before E7 Tuva Foundation)

---

## DuckDB Limitations and Approach

### MetricFlow Query Engine Limitations

The dbt Semantic Layer relies on MetricFlow to execute semantic queries. DuckDB has limited support:

| Capability | DuckDB Status | Notes |
|------------|---------------|-------|
| `dbt sl query` command | Limited | MetricFlow query engine not fully compatible |
| `dbt sl list` command | Supported | Can list definitions |
| BI tool integration | Not supported | Requires MetricFlow server |

### First Rollout: Metric Marts

**Given these limitations, metric marts are our v0.5.5 solution:**

1. **Metric Marts** (Primary Deliverable)
   - Build `models/marts/metrics/` layer
   - SQL models implementing standardized metric calculations
   - Directly queryable with DuckDB
   - Works today, no limitations

2. **YAML Semantic Models** (Deferred)
   - Full dbt Semantic Layer definitions deferred
   - Will implement when we migrate to a supported warehouse
   - See "Future: Warehouse Evaluation" in FUTURE_FEATURES.md

### Future: Full Semantic Layer

When the project matures, we may evaluate warehouse solutions that fully support dbt Semantic Layer:

- Snowflake
- BigQuery
- Databricks
- PostgreSQL (partial support)

This evaluation is tracked in FUTURE_FEATURES.md as a separate initiative.

---

## Requirements

### Functional Requirements

#### FR-1: Metric Mart - Encounters Summary

**Priority**: P1 (High)

Build queryable metric mart implementing the same calculations.

**Acceptance Criteria**:

- [ ] Model at `models/marts/metrics/mrt_encounters_summary.sql`
- [ ] Implements same 4-5 metrics as YAML definitions
- [ ] Supports date dimension grouping
- [ ] Supports encounter_class dimension grouping
- [ ] Calculations verified against YAML definitions

**Columns**:

| Column | Type | Description |
|--------|------|-------------|
| date_key | INTEGER | FK to dim_date (grain: day) |
| date_actual | DATE | Date for grouping |
| year_month | VARCHAR | YYYY-MM for monthly analysis |
| encounter_class | VARCHAR | Encounter classification |
| total_encounters | INTEGER | Count of encounters |
| unique_patients | INTEGER | Distinct patient count |
| total_claim_cost | DECIMAL | Sum of total claim costs |
| total_claims_paid | DECIMAL | Sum of payer coverage |
| total_patient_responsibility | DECIMAL | Sum of patient costs |
| avg_cost_per_encounter | DECIMAL | Average cost per encounter |
| avg_duration_minutes | DECIMAL | Average duration |

#### FR-2: Documentation and Governance

**Priority**: P2 (Medium)

Document metrics for business users.

**Acceptance Criteria**:

- [ ] Each metric has a description
- [ ] Each metric has calculation notes
- [ ] Data dictionary includes metrics section
- [ ] Example queries provided

---

### Non-Functional Requirements

#### NFR-1: Directory Structure

```text
models/
└── marts/
    └── metrics/
        ├── _metrics__models.yml       # Schema documentation
        └── mrt_encounters_summary.sql # Queryable metric mart
```

#### NFR-2: Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Metric mart model | `mrt_[entity]_[scope].sql` | `mrt_encounters_summary.sql` |
| Metric mart schema | `_metrics__models.yml` | Standard dbt pattern |

#### NFR-3: Metric Documentation

Each metric implemented in mart models MUST be documented with:

- Business description
- Calculation formula
- Source columns
- Any caveats or exclusions

---

## User Stories

### US-1: Consistent Metric Definitions

**As a** data analyst
**I want** a single source of truth for metric definitions
**So that** I can trust that "Total Encounters" means the same thing everywhere

**Acceptance Criteria**:

- Metric definitions documented in YAML
- Same calculations in metric marts
- Documentation accessible via dbt docs

### US-2: Queryable Metrics

**As a** business user
**I want** to query pre-calculated metrics by date and dimension
**So that** I can build reports without writing complex SQL

**Example Query**:

```sql
select
    year_month,
    encounter_class,
    total_encounters,
    total_claims_paid,
    avg_cost_per_encounter
from mrt_encounters_summary
where date_actual >= '2020-01-01'
order by year_month, encounter_class
```

### US-3: Future Semantic Layer Migration

**As an** architect
**I want** metric marts designed with semantic layer patterns in mind
**So that** we can migrate to full dbt Semantic Layer when we adopt a supported warehouse

---

## Phased Implementation

### Phase 1: Metric Marts Foundation (v0.5.5)

**Scope**: Queryable metric marts for core healthcare KPIs

1. Create `models/marts/metrics/` directory
2. Build `mrt_encounters_summary` metric mart
3. Implement 4-5 core metrics in SQL
4. Add tests and documentation

**Deliverables**:

- 1 metric mart model (`mrt_encounters_summary`)
- 4-5 metrics: total_encounters, total_claims_paid, avg_cost_per_encounter, patient_volume, avg_duration
- Schema documentation with metric definitions
- Example queries

### Phase 2: Expansion (v0.6+)

**Scope**: Additional metric marts as needed

1. Add patient-level metrics mart
2. Add clinical events metrics mart
3. Expand metric coverage based on business needs

**Note**: Phase 2 should only proceed if Phase 1 provides value.

### Phase 3: Full Semantic Layer (Future - Post Warehouse Migration)

**Scope**: dbt Semantic Layer with YAML definitions + MetricFlow

**Prerequisites**:

- Migrate to warehouse that supports MetricFlow (Snowflake, BigQuery, etc.)
- See FUTURE_FEATURES.md for warehouse evaluation initiative

**When migrated**:

1. Define YAML semantic models
2. Define YAML metrics
3. Enable `dbt sl query` commands
4. Integrate with BI tools

---

## Testing Strategy

### Metric Calculation Tests

```yaml
# Verify metric calculations
models:
  - name: mrt_encounters_summary
    columns:
      - name: avg_cost_per_encounter
        data_tests:
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 100000
      - name: total_encounters
        data_tests:
          - not_null
```

### Reconciliation Tests

```sql
-- Singular test: Verify mart totals match source fact
-- tests/marts/metrics/test_encounters_summary_reconciliation.sql

with mart_totals as (
    select sum(total_encounters) as mart_total
    from {{ ref('mrt_encounters_summary') }}
),

fact_totals as (
    select count(*) as fact_total
    from {{ ref('fct_encounters') }}
)

select *
from mart_totals
cross join fact_totals
where mart_total != fact_total
```

---

## Agent Assignment

| Task | Agent | Notes |
|------|-------|-------|
| Metric definitions | data-modeler | Business logic, calculation formulas |
| Metric mart SQL | dbt-developer | Queryable models |
| Testing | dbt-tester | Calculation verification, reconciliation |
| Documentation | dbt-documenter | Business descriptions, examples |
| Architecture review | architect | Verify mart patterns |

---

## Dependencies

### Upstream

- PRD-004: Dimensional Models (fct_encounters, dim_* must exist and be stable)
- E5: Testing & Quality (comprehensive tests must be in place)

### Downstream

- E7: Tuva Foundation (may use semantic layer patterns)
- BI Tools (future integration)

---

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| MetricFlow DuckDB never improves | Low | Medium | Hybrid approach provides value regardless |
| Maintaining parity between YAML and marts | Medium | Medium | Add parity tests, document process |
| Over-engineering for small dataset | Medium | Low | Start minimal (4-5 metrics), expand only if needed |
| Metric definitions drift from business meaning | High | Low | Document with business users, review regularly |
| Learning curve for semantic layer concepts | Low | Medium | Start simple, document patterns |

---

## GitHub Issues to Create

1. **Metric Marts Foundation Setup** (E12)
   - Create `models/marts/metrics/` directory structure
   - Add schema YAML with metric definitions
   - Labels: `enhancement`, `metrics`, `E12`

2. **Encounters Metric Mart** (E12)
   - Build `mrt_encounters_summary` model
   - Implement 4-5 core metric calculations
   - Add reconciliation tests
   - Labels: `enhancement`, `metrics`, `E12`

3. **Metric Documentation** (E12)
   - Document metric definitions in schema YAML
   - Add example queries
   - Update data dictionary
   - Labels: `documentation`, `metrics`, `E12`

---

## References

- [dbt Semantic Layer](https://docs.getdbt.com/docs/build/semantic-layer)
- [MetricFlow](https://docs.getdbt.com/docs/build/semantic-models)
- [dbt Maturity Model](https://www.getdbt.com/blog/analytics-engineering-maturity-model)
- [DuckDB Adapter Limitations](https://docs.getdbt.com/docs/core/connect-data-platform/duckdb-setup)

---

*PRD Status: Draft - Pending Prerequisites (E4, E5)*
