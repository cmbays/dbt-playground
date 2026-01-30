---
audience: [pm, architect, developer]
priority: high
size: large
status: approved
epic: E5 - Advanced Metrics & Aggregations
version: 1.0
last_updated: 2026-01-30
---

# PRD-005: v0.5 Marts Layer Enhancements

## Overview

**Version**: v0.5.0-v0.5.2
**Theme**: Analytics-Ready Models with Advanced Aggregations
**Duration**: 3 sprints (phased delivery)
**Epic**: E5 - Extend marts layer with specialized analytics models

## Problem Statement

The v0.4 marts layer provides a solid Kimball dimensional foundation with core dimensions and fact tables. However, it lacks specialized analytic models for three critical healthcare analytics use cases:

1. **Patient Outcomes Tracking**: No annual patient summaries or condition-based cohort analysis
2. **Provider Performance**: No provider utilization or quality metrics by time period
3. **Cost Analysis**: No detailed financial breakdowns by payer, provider, or encounter type

Current state forces analysts to write custom aggregations for every query, introducing inconsistency and maintenance burden.

## Vision

Extend the v0.4 marts layer with 7-11 specialized analytic models covering three balanced healthcare analytics use cases while maintaining strict Kimball methodology and data quality standards.

## Goals (SMART)

### Functional Goals

- **G1**: Build 7-11 new analytic models covering patient outcomes, provider performance, and cost analysis use cases
- **G2**: Achieve 18-22 total marts models (expanding from v0.4's 11 models) with complete dimensional structure
- **G3**: Create 3 operational views for dashboard performance (pre-aggregated common queries)
- **G4**: Document all models with example queries demonstrating each use case

### Quality Goals

- **Q1**: Achieve 100% test coverage on all new models (schema + data quality + grain tests)
- **Q2**: Maintain zero referential integrity violations (all FKs tested)
- **Q3**: Enable dbt docs generation with complete lineage visualization
- **Q4**: Ensure all analytics queries execute in <1 second for typical datasets

### Strategic Goals

- **S1**: Enable seamless BI tool integration (Tableau/Looker/Power BI patterns)
- **S2**: Create reusable analytic patterns for future v0.6+ enhancements
- **S3**: Build institutional knowledge of healthcare analytics modeling

## Success Criteria

### Definition of Done

- [ ] All 7-11 new models compile without errors
- [ ] All new model tests pass (100% pass rate)
- [ ] All referential integrity tests pass (no orphan records)
- [ ] All data quality tests pass (costs ≥0, counts ≥0, coverage ≤100%, etc.)
- [ ] All new models documented in YAML with column descriptions
- [ ] Example queries provided for all three use cases
- [ ] `dbt docs generate` succeeds with complete lineage
- [ ] All models tagged with analytics tags for selective execution

### Acceptance Criteria per Model

**Analytics Facts** (4 models):

- Grain clearly defined (one row per X combination)
- All foreign keys have relationships tests
- All measures have data quality tests (non-negative, range validation)
- No null values in grain columns
- Row counts align with expected aggregations

**Dimensions** (1 new):

- Unique on natural key
- No null values in key columns
- All referenced by facts

**Operational Views** (3 models):

- Base on materialized facts (not dynamic calculations)
- Used in documented example queries
- Performance validated

## Requirements

### Phase 1: MVP Core Models (v0.5.0)

**New Models**:

1. **dim_conditions** (Dimension)
   - Source: stg_synthea__conditions
   - Grain: One row per condition code
   - Tests: unique on code, not_null on description

2. **fct_patient_summary** (Fact - Annual)
   - Grain: One row per patient per calendar year
   - Measures: encounter count, procedure count, condition count, total cost, payer coverage
   - Dimensions: dim_patients, dim_date (year), dim_payers
   - Use case: Patient outcomes tracking

3. **fct_provider_metrics** (Fact - Monthly)
   - Grain: One row per provider per calendar month
   - Measures: encounter count, unique patient count, avg patient age, total cost per encounter
   - Dimensions: dim_providers, dim_organizations, dim_date (month)
   - Use case: Provider performance and utilization

4. **fct_condition_cohorts** (Fact - Patient-Condition)
   - Grain: One row per patient-condition combination
   - Measures: months with condition, encounter count with condition, total cost
   - Dimensions: dim_patients, dim_conditions, dim_date (diagnosis date)
   - Use case: Condition-based outcomes research and disease management

5. **fct_cost_analysis** (Fact - Encounter-Payer-Provider)
   - Grain: One row per encounter-payer-provider combination
   - Measures: total cost, payer coverage, patient responsibility, cost per procedure
   - Dimensions: dim_encounters (FK), dim_payers, dim_providers, dim_date
   - Use case: Financial analysis and payer contract management

**Operational Views**:

6. **v_patient_current_conditions** (View)
   - Purpose: Current active conditions per patient (used in dashboards)
   - Base: fct_condition_cohorts filtered to is_active = true

7. **v_provider_active_patients** (View)
   - Purpose: Current patient panel size per provider (used in utilization dashboards)
   - Base: fct_condition_cohorts and fct_encounters aggregated by provider

**Result**: 18 total marts models (v0.4's 11 + v0.5's 7)

### Phase 2: Comprehensive Testing (v0.5.1)

- Add schema tests (unique, not_null, relationships) to all new models
- Add data quality tests (cost ranges, count validations, percentage bounds)
- Add grain tests (unique_combination_of_columns for aggregate facts)
- Validate all example queries from use cases execute successfully
- Run full `dbt test` suite with 100% pass rate
- Generate `dbt docs` and validate lineage diagram

### Phase 3: Documentation & BI Integration (v0.5.2)

- Create `_analytics__models.yml` with full documentation
- Add column descriptions and data dictionaries
- Create example queries for each analytics use case
- Update dbt docs with model relationships and lineage
- Update CHANGELOG with v0.5.0, v0.5.1, v0.5.2 sections
- Create BI integration guide with Tableau/Looker patterns
- Tag release v0.5.0 and push to origin

## Data Models Overview

### Dimensional Structure

```
dim_conditions (NEW)
├── condition_code (PK)
├── condition_name
├── category
└── chronic_flag

dim_patients (v0.4)
├── patient_id (PK)
├── gender, age_at_load
└── ...

dim_providers (v0.4)
├── provider_id (PK)
└── ...

dim_organizations (v0.4)
├── organization_id (PK)
└── ...

dim_payers (v0.4)
├── payer_id (PK)
└── ...

dim_date (v0.4)
├── date_id (PK)
├── year_actual, month_actual
└── ...
```

### Fact Table Specifications

**fct_patient_summary** (Annual Grain)

- Surrogate key: hash(patient_id || year_actual)
- Grain: (patient_id, year_actual)
- Measures:
  - encounter_count: sum of encounters per patient-year
  - procedure_count: sum of procedures per patient-year
  - condition_count: distinct conditions per patient-year
  - total_cost: aggregate cost per patient-year
  - payer_coverage_pct: avg coverage percentage
  - unique_providers: distinct provider_ids per patient-year
- Relationships:
  - fk_patient -> dim_patients
  - fk_year_date -> dim_date (year grain)
  - fk_payer -> dim_payers

**fct_provider_metrics** (Monthly Grain)

- Grain: (provider_id, year_month)
- Measures:
  - encounter_count: sum per provider-month
  - unique_patient_count: distinct patients per provider-month
  - avg_patient_age: average age of patients seen
  - avg_encounter_duration: average duration in days
  - total_procedures: sum of procedures per provider-month
  - total_cost: sum of cost per provider-month
  - avg_cost_per_encounter: total_cost / encounter_count
  - encounters_per_patient_avg: encounter_count / unique_patient_count
- Relationships:
  - fk_provider -> dim_providers
  - fk_organization -> dim_organizations
  - fk_month_date -> dim_date (month grain)

**fct_condition_cohorts** (Patient-Condition Grain)

- Grain: (patient_id, condition_code)
- Measures:
  - months_with_condition: duration calculation (end_date - start_date)
  - encounter_count_with_condition: encounters during condition period
  - procedure_count_with_condition: procedures during condition period
  - total_cost_for_condition: cost during condition period
  - is_active: boolean (no end_date = true)
  - first_diagnosis_date_id: FK to dim_date
  - last_diagnosis_date_id: FK to dim_date (null if active)
- Relationships:
  - fk_patient -> dim_patients
  - fk_condition -> dim_conditions
  - fk_first_date -> dim_date
  - fk_last_date -> dim_date (nullable)

**fct_cost_analysis** (Encounter-Payer-Provider Grain)

- Grain: (encounter_id, payer_id, provider_id)
- Measures:
  - total_cost: claim total cost
  - payer_coverage: amount paid by insurance
  - patient_responsibility: copay + coinsurance + deductible
  - coverage_pct: payer_coverage / total_cost
  - cost_per_procedure: cost allocation per procedure (if relevant)
  - out_of_pocket_pct: patient_responsibility / total_cost
- Relationships:
  - fk_encounter -> fct_encounters (or encounter_id direct)
  - fk_payer -> dim_payers
  - fk_provider -> dim_providers
  - fk_encounter_date -> dim_date

## Testing Strategy

### Test Coverage Matrix

| Model | Grain Test | Referential Integrity | Data Quality | Example |
|-------|------------|----------------------|--------------|---------|
| dim_conditions | unique(code) | - | not_null(name) | 1 |
| fct_patient_summary | unique(patient,year) | 3 FKs | 4 quality | 7 |
| fct_provider_metrics | unique(provider,month) | 3 FKs | 4 quality | 7 |
| fct_condition_cohorts | unique(patient,condition) | 4 FKs | 4 quality | 7 |
| fct_cost_analysis | unique(enc,payer,prov) | 4 FKs | 5 quality | 8 |
| v_* views | implicit | via base facts | - | - |
| **TOTAL** | **5** | **15** | **17** | **30** |

### Test Types

**Schema Tests** (per model):

- `unique` on grain columns (ensure no duplicates)
- `not_null` on key columns (ensure complete grain)
- `relationships` on foreign keys (ensure referential integrity)

**Data Quality Tests** (per measure):

- Costs: `>= 0` (dbt_expectations.expect_column_values_to_be_between)
- Counts: `>= 0`
- Percentages: `between 0 and 100`
- Dates: `first_date <= last_date`

**Grain Tests**:

- `dbt_utils.unique_combination_of_columns` on grain columns
- Validate no duplicate rows at grain level

**Example Queries** (per use case):

- Patient outcomes: Top 10 highest cost patients by year
- Provider metrics: Provider utilization trending month-over-month
- Cost analysis: Cost per encounter by payer and provider

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Complex grain definitions | Data quality issues, analyst confusion | Document grain clearly, include grain test examples, create example queries |
| Missing dimension values | Null FK errors, lost data | Implement "Unknown" pattern for missing dimension values with surrogate keys |
| Large aggregate fact tables | Query performance degradation | Use incremental materialization, partition on date, create indexes |
| Synthea data quirks (nulls) | Test failures, incomplete analysis | Document known data quality issues, use coalesce with defaults |

## Out of Scope

- Semantic layer / dbt metrics (deferred to v0.6)
- BI tool-specific models (patterns only, not tool-specific)
- Real-time / streaming models (requires architecture change)
- Incremental materialization (start with full refresh in v0.5.0, optimize in v0.6)
- Machine learning models (separate track)

## Success Metrics

### Quantitative

- **0** compilation errors
- **100%** test pass rate on all new models
- **0** referential integrity violations
- **18-22** total marts models
- **30+** data quality + referential tests
- **3+** operational views for dashboard use
- **<1 second** query time for typical analytics queries

### Qualitative

- All models documented with clear use cases
- Example queries demonstrate all three use cases
- Analysts can write new reports without custom aggregations
- BI tool integration patterns clear and reusable

## Timeline

| Phase | Name | Duration | Target Version | Deliverables |
|-------|------|----------|-----------------|--------------|
| 1 | MVP Core Models | 2 sprints | v0.5.0 | 7 new models + TDD + PRD |
| 2 | Testing | 1 sprint | v0.5.1 | 30+ tests + test specs |
| 3 | Docs | 1 sprint | v0.5.2 | Documentation + BI guide + CHANGELOG |
| 4 | Deployment | 1 day | v0.5.0 (tag) | Git tag + release notes |

## Related Documents

- **TDD-005-MARTS-ENHANCEMENTS.md** - Technical design details
- **v0.5_PLAN.md** - Implementation sequencing and git workflow
- **v0.5_TESTING.md** - Comprehensive test specifications
- **ROADMAP.md** - Project roadmap and vision
- **PRD-004-DIMENSIONAL-MODELS.md** - v0.4 foundation (reference)

## Approval

| Role | Name | Status | Date |
|------|------|--------|------|
| Product Manager | dbt-playground team | Approved | 2026-01-30 |
| Architect | dbt-playground team | Approved | 2026-01-30 |

---

**Document Version**: 1.0
**Last Updated**: 2026-01-30
**Status**: Approved for implementation
