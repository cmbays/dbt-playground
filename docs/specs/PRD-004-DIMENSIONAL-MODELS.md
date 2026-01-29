---
title: Dimensional Models
prd_number: PRD-004
epic: E4-Dimensional-Models
version: 0.4.0
status: draft
author: pm
created: 2026-01-28
last_updated: 2026-01-28
---

## Overview

### Problem Statement

While staging models provide clean source data, analysts need dimensional models optimized for analytics queries. Following the Kimball methodology, we need fact tables (measurable events) and dimension tables (descriptive context) to enable efficient healthcare analytics.

### Goal

Build a dimensional model layer (marts) consisting of 4 dimension tables, 2 fact tables, and 2 intermediate models that enable healthcare analytics use cases such as patient cohort analysis, encounter trends, and clinical event tracking.

### Success Metrics

- All dimension and fact models compile and run
- Referential integrity tests pass between facts and dimensions
- Query performance acceptable for analytics (sub-second for typical queries)
- Models support common healthcare analytics patterns
- All models documented with descriptions and examples

---

## Requirements

### Functional Requirements

#### FR-1: Dimension - Patients (dim_patients)

**Priority**: P0 (Critical)

Patient dimension with demographics and derived attributes.

**Acceptance Criteria**:

- [ ] Surrogate key generated
- [ ] All demographic attributes included
- [ ] Derived fields: age, is_deceased, full_name
- [ ] Current state (no SCD yet - Type 1)

**Columns**:

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| patient_key | INTEGER | Generated | Surrogate key |
| patient_id | VARCHAR | stg_patients | Natural key (UUID) |
| first_name | VARCHAR | stg_patients | |
| last_name | VARCHAR | stg_patients | |
| full_name | VARCHAR | Derived | first_name + last_name |
| birth_date | DATE | stg_patients | |
| death_date | DATE | stg_patients | Nullable |
| age_years | INTEGER | Derived | Current age or age at death |
| is_deceased | BOOLEAN | Derived | death_date IS NOT NULL |
| gender | VARCHAR | stg_patients | |
| race | VARCHAR | stg_patients | |
| ethnicity | VARCHAR | stg_patients | |
| marital_status | VARCHAR | stg_patients | |
| city | VARCHAR | stg_patients | |
| state | VARCHAR | stg_patients | |
| zip_code | VARCHAR | stg_patients | |
| latitude | DOUBLE | stg_patients | |
| longitude | DOUBLE | stg_patients | |
| total_healthcare_expenses | DECIMAL | stg_patients | |
| total_healthcare_coverage | DECIMAL | stg_patients | |

#### FR-2: Dimension - Providers (dim_providers)

**Priority**: P1 (High)

Provider dimension with specialization and organization context.

**Acceptance Criteria**:

- [ ] Surrogate key generated
- [ ] Specialty information included
- [ ] Organization linkage maintained
- [ ] Provider name formatted

**Columns**:

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| provider_key | INTEGER | Generated | Surrogate key |
| provider_id | VARCHAR | stg_providers | Natural key |
| provider_name | VARCHAR | stg_providers | |
| specialty | VARCHAR | stg_providers | Medical specialty |
| organization_id | VARCHAR | stg_providers | FK to organization |
| address | VARCHAR | stg_providers | |
| city | VARCHAR | stg_providers | |
| state | VARCHAR | stg_providers | |
| zip_code | VARCHAR | stg_providers | |

#### FR-3: Dimension - Organizations (dim_organizations)

**Priority**: P1 (High)

Healthcare facility dimension.

**Acceptance Criteria**:

- [ ] Surrogate key generated
- [ ] All location attributes included
- [ ] Revenue information included

**Columns**:

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| organization_key | INTEGER | Generated | Surrogate key |
| organization_id | VARCHAR | stg_organizations | Natural key |
| organization_name | VARCHAR | stg_organizations | |
| address | VARCHAR | stg_organizations | |
| city | VARCHAR | stg_organizations | |
| state | VARCHAR | stg_organizations | |
| zip_code | VARCHAR | stg_organizations | |
| latitude | DOUBLE | stg_organizations | |
| longitude | DOUBLE | stg_organizations | |
| phone | VARCHAR | stg_organizations | |
| revenue | DECIMAL | stg_organizations | |
| utilization | INTEGER | stg_organizations | |

#### FR-4: Dimension - Date (dim_date)

**Priority**: P0 (Critical)

Calendar dimension for time-based analysis.

**Acceptance Criteria**:

- [ ] Date range covers all encounter dates
- [ ] Standard calendar attributes
- [ ] Fiscal calendar attributes (optional)
- [ ] Holiday flags (US holidays)

**Columns**:

| Column | Type | Description |
|--------|------|-------------|
| date_key | INTEGER | YYYYMMDD format |
| date_actual | DATE | Actual date |
| day_of_week | INTEGER | 1-7 (Monday = 1) |
| day_name | VARCHAR | Monday, Tuesday, etc. |
| day_of_month | INTEGER | 1-31 |
| day_of_year | INTEGER | 1-366 |
| week_of_year | INTEGER | 1-53 |
| month_actual | INTEGER | 1-12 |
| month_name | VARCHAR | January, February, etc. |
| month_name_short | VARCHAR | Jan, Feb, etc. |
| quarter_actual | INTEGER | 1-4 |
| quarter_name | VARCHAR | Q1, Q2, Q3, Q4 |
| year_actual | INTEGER | YYYY |
| is_weekend | BOOLEAN | Saturday or Sunday |
| is_holiday | BOOLEAN | US federal holiday |
| holiday_name | VARCHAR | Holiday name if applicable |

#### FR-5: Fact - Encounters (fct_encounters)

**Priority**: P0 (Critical)

Grain: One row per healthcare encounter.

**Acceptance Criteria**:

- [ ] All dimension keys present
- [ ] All measures included
- [ ] Derived measures calculated
- [ ] Patient context denormalized

**Columns**:

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| encounter_key | INTEGER | Generated | Surrogate key |
| encounter_id | VARCHAR | stg_encounters | Natural key |
| patient_id | VARCHAR | stg_encounters | FK to dim_patients |
| provider_id | VARCHAR | stg_encounters | FK to dim_providers |
| organization_id | VARCHAR | stg_encounters | FK to dim_organizations |
| payer_id | VARCHAR | stg_encounters | FK to payers |
| encounter_date_key | INTEGER | Derived | FK to dim_date |
| encounter_class | VARCHAR | stg_encounters | ambulatory, inpatient, etc. |
| encounter_code | VARCHAR | stg_encounters | SNOMED code |
| encounter_description | VARCHAR | stg_encounters | |
| reason_code | VARCHAR | stg_encounters | |
| reason_description | VARCHAR | stg_encounters | |
| start_timestamp | TIMESTAMP | stg_encounters | |
| stop_timestamp | TIMESTAMP | stg_encounters | |
| duration_minutes | INTEGER | Derived | stop - start |
| base_encounter_cost | DECIMAL | stg_encounters | |
| total_claim_cost | DECIMAL | stg_encounters | |
| payer_coverage | DECIMAL | stg_encounters | |
| patient_responsibility | DECIMAL | Derived | total - payer_coverage |
| patient_age_at_encounter | INTEGER | Derived | From patient birth_date |

#### FR-6: Fact - Clinical Events (fct_clinical_events)

**Priority**: P1 (High)

Grain: One row per clinical event (condition, medication, procedure).

**Acceptance Criteria**:

- [ ] Unified event model from multiple sources
- [ ] Event type discriminator
- [ ] Temporal attributes (start/stop)
- [ ] Code systems preserved

**Columns**:

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| clinical_event_key | INTEGER | Generated | Surrogate key |
| event_type | VARCHAR | Derived | CONDITION, MEDICATION, PROCEDURE |
| event_id | VARCHAR | Source | Original ID |
| patient_id | VARCHAR | Source | FK to dim_patients |
| encounter_id | VARCHAR | Source | FK to fct_encounters |
| event_date_key | INTEGER | Derived | FK to dim_date |
| event_start_date | DATE | Source | |
| event_stop_date | DATE | Source | Nullable |
| code | VARCHAR | Source | SNOMED/RxNorm code |
| code_system | VARCHAR | Derived | SNOMED, RXNORM, etc. |
| description | VARCHAR | Source | Event description |
| event_cost | DECIMAL | Source | Cost if applicable |

#### FR-7: Intermediate - Enriched Encounters

**Priority**: P2 (Medium)

Pre-compute common encounter enrichments.

**Acceptance Criteria**:

- [ ] Condition count per encounter
- [ ] Medication count per encounter
- [ ] Procedure count per encounter
- [ ] Total event cost per encounter

#### FR-8: Intermediate - Patients with Conditions

**Priority**: P2 (Medium)

Pre-compute patient condition history.

**Acceptance Criteria**:

- [ ] Active conditions list
- [ ] Condition count
- [ ] First diagnosis date
- [ ] Chronic condition flags

---

### Non-Functional Requirements

#### NFR-1: Materialization

- Dimensions: TABLE (for performance)
- Facts: TABLE (for aggregation performance)
- Intermediate: VIEW or TABLE (based on size)

#### NFR-2: Surrogate Keys

Use `row_number()` or `dense_rank()` for deterministic surrogate keys.

#### NFR-3: Query Performance

Typical analytics queries should complete in <1 second for 500 patients.

---

## User Stories

### US-1: Patient Cohort Analysis

**As a** healthcare analyst
**I want** to query patients by demographics and conditions
**So that** I can identify patient cohorts for studies

**Acceptance Criteria**:

- Can filter by age range, gender, location
- Can filter by condition (diabetes, hypertension, etc.)
- Can count encounters per patient

**Example Query**:

```sql
SELECT
    p.gender,
    p.age_years,
    COUNT(DISTINCT e.encounter_id) as encounter_count
FROM dim_patients p
JOIN fct_encounters e ON p.patient_id = e.patient_id
WHERE p.state = 'Massachusetts'
  AND p.age_years BETWEEN 40 AND 60
GROUP BY 1, 2
```

### US-2: Encounter Trends

**As a** operations manager
**I want** to analyze encounter patterns over time
**So that** I can plan staffing and resources

**Acceptance Criteria**:

- Can aggregate by day, week, month
- Can filter by encounter class
- Can see cost trends

**Example Query**:

```sql
SELECT
    d.year_actual,
    d.month_name,
    e.encounter_class,
    COUNT(*) as encounter_count,
    SUM(e.total_claim_cost) as total_cost
FROM fct_encounters e
JOIN dim_date d ON e.encounter_date_key = d.date_key
GROUP BY 1, 2, 3
ORDER BY 1, 2
```

### US-3: Clinical Event Tracking

**As a** clinical researcher
**I want** to track clinical events across patients
**So that** I can analyze treatment patterns

**Acceptance Criteria**:

- Can query conditions, medications, procedures uniformly
- Can analyze event sequences
- Can identify common co-occurrences

---

## Technical Specifications

### Model Template - Dimension

```sql
-- models/marts/core/dim_[entity].sql

{{
  config(
    materialized='table',
    unique_key='[entity]_key'
  )
}}

with source as (
    select * from {{ ref('stg_synthea__[entity]s') }}
),

final as (
    select
        -- Surrogate key
        row_number() over (order by [entity]_id) as [entity]_key,

        -- Natural key
        [entity]_id,

        -- Attributes
        attribute_1,
        attribute_2,

        -- Derived attributes
        derived_field_1,

        -- Metadata
        current_timestamp as _loaded_at

    from source
)

select * from final
```

### Model Template - Fact

```sql
-- models/marts/core/fct_[event].sql

{{
  config(
    materialized='table',
    unique_key='[event]_key'
  )
}}

with events as (
    select * from {{ ref('stg_synthea__[events]') }}
),

dimensions as (
    select * from {{ ref('dim_[dimension]') }}
),

final as (
    select
        -- Surrogate key
        row_number() over (order by e.[event]_id) as [event]_key,

        -- Dimension keys
        d.[dimension]_key,
        date_key,

        -- Natural keys
        e.[event]_id,

        -- Measures
        e.measure_1,
        e.measure_2,

        -- Derived measures
        e.measure_1 - e.measure_2 as derived_measure,

        -- Metadata
        current_timestamp as _loaded_at

    from events e
    left join dimensions d on e.[dimension]_id = d.[dimension]_id
)

select * from final
```

### Directory Structure

```text
models/
├── intermediate/
│   └── healthcare/
│       ├── int_encounters__enriched.sql
│       └── int_patients__with_conditions.sql
└── marts/
    └── core/
        ├── _core__models.yml
        ├── dim_patients.sql
        ├── dim_providers.sql
        ├── dim_organizations.sql
        ├── dim_date.sql
        ├── fct_encounters.sql
        └── fct_clinical_events.sql
```

### Testing Strategy

**Referential Integrity**:

```yaml
models:
  - name: fct_encounters
    data_tests:
      - dbt_utils.relationships_where:
          to: ref('dim_patients')
          field: patient_id
    columns:
      - name: encounter_key
        data_tests:
          - unique
          - not_null
```

**Grain Tests**:

```yaml
- name: fct_encounters
  data_tests:
    - dbt_utils.unique_combination_of_columns:
        combination_of_columns:
          - encounter_id
```

---

## Implementation Notes

### Date Dimension Generation

Use `dbt_date` package for date spine:

```sql
{{ dbt_date.get_date_dimension('2015-01-01', '2025-12-31') }}
```

Or generate manually:

```sql
with date_spine as (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="'2015-01-01'",
        end_date="'2025-12-31'"
    ) }}
)
...
```

### Surrogate Key Generation

For deterministic keys:

```sql
-- Option 1: Row number (order matters)
row_number() over (order by natural_key) as surrogate_key

-- Option 2: Hash (order-independent)
abs(hash(natural_key)) as surrogate_key
```

### Handling Missing Dimensions

Use "Unknown" member pattern:

```sql
coalesce(d.dimension_key, -1) as dimension_key
```

Add unknown member to dimension:

```sql
union all
select
    -1 as dimension_key,
    'UNKNOWN' as natural_key,
    'Unknown' as name
    -- etc
```

---

## Agent Assignment

| Task | Agent | Notes |
|------|-------|-------|
| Dimensional design | data-modeler | Overall design decisions |
| dim_patients | dbt-developer | Core dimension |
| dim_providers | dbt-developer | |
| dim_organizations | dbt-developer | |
| dim_date | dbt-developer | Use dbt_date package |
| fct_encounters | dbt-developer | Core fact |
| fct_clinical_events | dbt-developer | Union pattern |
| Intermediate models | dbt-developer | |
| Referential tests | dbt-tester | |
| Documentation | dbt-documenter | |
| Code review | code-reviewer | Pattern consistency |

---

## Dependencies

### Upstream

- PRD-003: Staging Layer (all staging models must exist)

### Downstream

- E5: Testing & Quality (comprehensive tests)
- E6: MCP Integration (model queries)

---

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Performance issues | Medium | Medium | Test with full data early |
| Grain confusion | High | Low | Document grain clearly |
| Missing relationships | Medium | Medium | Validate FK mappings |
| Date range gaps | Low | Low | Use date spine for coverage |

---

## Open Questions

1. Should we implement SCD Type 2 for patients (track history)?
2. Should payers be a full dimension or just referenced by ID?
3. Should we add aggregate fact tables for performance?
4. What date range should dim_date cover?

---

## References

- [Kimball Dimensional Modeling](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
- [dbt Marts Best Practices](https://docs.getdbt.com/guides/best-practices/how-we-structure/4-marts)
- [dbt_utils Testing](https://github.com/dbt-labs/dbt-utils#schema-tests)
- [dbt_date Package](https://github.com/calogica/dbt-date)

---

*PRD Status: Draft - Ready for Review*
