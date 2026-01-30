---
title: Dimensional Models
prd_number: PRD-004
epic: E4-Dimensional-Models
version: 0.4.0
status: approved
author: pm
created: 2026-01-28
last_updated: 2026-01-29
---

## Overview

### Problem Statement

While staging models provide clean source data, analysts need dimensional models optimized for analytics queries. Following the Kimball methodology, we need fact tables (measurable events) and dimension tables (descriptive context) to enable efficient healthcare analytics.

### Goal

Build a dimensional model layer (marts) consisting of 5 dimension tables, 4 fact tables (including 2 aggregates), and 2 intermediate models that enable healthcare analytics use cases such as patient cohort analysis, encounter trends, and clinical event tracking.

### Success Metrics

- All dimension and fact models compile and run
- Referential integrity tests pass between facts and dimensions
- Query performance acceptable for analytics (sub-second for typical queries)
- Models support common healthcare analytics patterns
- All models documented with descriptions and examples

---

## Design Decisions

The following design decisions have been finalized:

| Question | Decision | Rationale |
|----------|----------|-----------|
| SCD Type 2 for patients? | **Yes** | Track patient history with valid_from/valid_to for historical analysis |
| Full payers dimension? | **Yes** | Create `dim_payers` with all coverage and performance attributes |
| Aggregate fact tables? | **Yes** | Monthly and yearly aggregates for performance on time-series queries |
| Date range for dim_date? | **1909-01-01 to 2025-12-31** | Data spans 1909-2020; buffer for future data |

---

## Requirements

### Functional Requirements

#### FR-1: Dimension - Patients (dim_patients)

**Priority**: P0 (Critical)

Patient dimension with demographics, derived attributes, and SCD Type 2 history tracking.

**Acceptance Criteria**:

- [ ] Surrogate key generated (patient_key)
- [ ] All demographic attributes included
- [ ] Derived fields: age, is_deceased, full_name
- [ ] SCD Type 2 columns: valid_from, valid_to, is_current

**Columns**:

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| patient_key | INTEGER | Generated | Surrogate key (unique per version) |
| patient_id | VARCHAR | stg_patients | Natural key (UUID) |
| first_name | VARCHAR | stg_patients | |
| last_name | VARCHAR | stg_patients | |
| full_name | VARCHAR | Derived | first_name + last_name |
| name_prefix | VARCHAR | stg_patients | |
| name_suffix | VARCHAR | stg_patients | |
| birth_date | DATE | stg_patients | |
| death_date | DATE | stg_patients | Nullable |
| age_years | INTEGER | Derived | Current age or age at death |
| is_deceased | BOOLEAN | Derived | death_date IS NOT NULL |
| gender | VARCHAR | stg_patients | |
| race | VARCHAR | stg_patients | |
| ethnicity | VARCHAR | stg_patients | |
| marital_status | VARCHAR | stg_patients | |
| address | VARCHAR | stg_patients | |
| city | VARCHAR | stg_patients | |
| state | VARCHAR | stg_patients | |
| county | VARCHAR | stg_patients | |
| zip_code | VARCHAR | stg_patients | |
| latitude | DOUBLE | stg_patients | |
| longitude | DOUBLE | stg_patients | |
| healthcare_expenses | DECIMAL | stg_patients | |
| healthcare_coverage | DECIMAL | stg_patients | |
| valid_from | DATE | SCD2 | Record start date |
| valid_to | DATE | SCD2 | Record end date (NULL = current) |
| is_current | BOOLEAN | SCD2 | Current record flag |

**Note**: For initial load, all records will have valid_from = birth_date, valid_to = NULL, is_current = TRUE.

#### FR-2: Dimension - Providers (dim_providers)

**Priority**: P1 (High)

Provider dimension with specialization and organization context.

**Acceptance Criteria**:

- [ ] Surrogate key generated
- [ ] Specialty information included
- [ ] Organization linkage maintained (organization_key FK)
- [ ] Provider name formatted

**Columns**:

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| provider_key | INTEGER | Generated | Surrogate key |
| provider_id | VARCHAR | stg_providers | Natural key |
| organization_key | INTEGER | dim_organizations | FK to organization |
| organization_id | VARCHAR | stg_providers | Organization natural key |
| provider_name | VARCHAR | stg_providers | |
| gender | VARCHAR | stg_providers | |
| specialty | VARCHAR | stg_providers | Medical specialty |
| address | VARCHAR | stg_providers | |
| city | VARCHAR | stg_providers | |
| state | VARCHAR | stg_providers | |
| zip_code | VARCHAR | stg_providers | |
| latitude | DOUBLE | stg_providers | |
| longitude | DOUBLE | stg_providers | |
| utilization | INTEGER | stg_providers | |

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

- [ ] Date range covers 1909-01-01 to 2025-12-31 (117 years)
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
| is_us_holiday | BOOLEAN | US federal holiday |
| holiday_name | VARCHAR | Holiday name if applicable |

#### FR-4b: Dimension - Payers (dim_payers)

**Priority**: P1 (High)

Insurance payer dimension with coverage and performance metrics.

**Acceptance Criteria**:

- [ ] Surrogate key generated
- [ ] All payer attributes included
- [ ] Coverage metrics included
- [ ] Derived coverage_rate calculated

**Columns**:

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| payer_key | INTEGER | Generated | Surrogate key |
| payer_id | VARCHAR | stg_payers | Natural key (UUID) |
| payer_name | VARCHAR | stg_payers | Insurance company name |
| address | VARCHAR | stg_payers | |
| city | VARCHAR | stg_payers | |
| state | VARCHAR | stg_payers | |
| zip_code | VARCHAR | stg_payers | |
| phone | VARCHAR | stg_payers | |
| amount_covered | DECIMAL | stg_payers | Total covered amount |
| amount_uncovered | DECIMAL | stg_payers | Total uncovered amount |
| revenue | DECIMAL | stg_payers | Payer revenue |
| covered_encounters | INTEGER | stg_payers | Count of covered encounters |
| uncovered_encounters | INTEGER | stg_payers | Count of uncovered encounters |
| covered_medications | INTEGER | stg_payers | Count of covered medications |
| uncovered_medications | INTEGER | stg_payers | Count of uncovered medications |
| covered_procedures | INTEGER | stg_payers | Count of covered procedures |
| uncovered_procedures | INTEGER | stg_payers | Count of uncovered procedures |
| covered_immunizations | INTEGER | stg_payers | Count of covered immunizations |
| uncovered_immunizations | INTEGER | stg_payers | Count of uncovered immunizations |
| unique_customers | INTEGER | stg_payers | Distinct customer count |
| average_quality_of_life_score | DECIMAL | stg_payers | QoL score |
| member_months | INTEGER | stg_payers | Total member months |
| coverage_rate | DECIMAL | Derived | amount_covered / (amount_covered + amount_uncovered) |

#### FR-5: Fact - Encounters (fct_encounters)

**Priority**: P0 (Critical)

Grain: One row per healthcare encounter.

**Acceptance Criteria**:

- [ ] All dimension keys present (patient, provider, organization, payer, date)
- [ ] All measures included
- [ ] Derived measures calculated
- [ ] Patient context denormalized

**Columns**:

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| encounter_key | INTEGER | Generated | Surrogate key |
| encounter_id | VARCHAR | stg_encounters | Natural key |
| patient_key | INTEGER | dim_patients | FK to dim_patients |
| patient_id | VARCHAR | stg_encounters | Patient natural key |
| provider_key | INTEGER | dim_providers | FK to dim_providers |
| provider_id | VARCHAR | stg_encounters | Provider natural key |
| organization_key | INTEGER | dim_organizations | FK to dim_organizations |
| organization_id | VARCHAR | stg_encounters | Organization natural key |
| payer_key | INTEGER | dim_payers | FK to dim_payers |
| payer_id | VARCHAR | stg_encounters | Payer natural key |
| encounter_start_date_key | INTEGER | Derived | FK to dim_date |
| encounter_end_date_key | INTEGER | Derived | FK to dim_date |
| encounter_class | VARCHAR | stg_encounters | ambulatory, inpatient, etc. |
| encounter_code | VARCHAR | stg_encounters | SNOMED code |
| encounter_description | VARCHAR | stg_encounters | |
| reason_code | VARCHAR | stg_encounters | |
| reason_description | VARCHAR | stg_encounters | |
| encounter_start_at | TIMESTAMP | stg_encounters | |
| encounter_end_at | TIMESTAMP | stg_encounters | |
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
| patient_key | INTEGER | dim_patients | FK to dim_patients |
| patient_id | VARCHAR | Source | Patient natural key |
| encounter_id | VARCHAR | Source | FK to fct_encounters |
| event_date_key | INTEGER | Derived | FK to dim_date |
| event_start_date | DATE | Source | |
| event_end_date | DATE | Source | Nullable |
| code | VARCHAR | Source | SNOMED/RxNorm code |
| code_system | VARCHAR | Derived | SNOMED-CT, RXNORM, etc. |
| description | VARCHAR | Source | Event description |
| reason_code | VARCHAR | Source | Reason code (nullable) |
| reason_description | VARCHAR | Source | Reason description (nullable) |
| event_cost | DECIMAL | Source | Cost if applicable |

#### FR-7: Intermediate - Enriched Encounters

**Priority**: P2 (Medium)

Pre-compute common encounter enrichments.

**Acceptance Criteria**:

- [ ] Condition count per encounter
- [ ] Medication count per encounter
- [ ] Procedure count per encounter
- [ ] Total event cost per encounter

**Columns**:

| Column | Type | Description |
|--------|------|-------------|
| encounter_id | VARCHAR | FK to fct_encounters |
| condition_count | INTEGER | Count of conditions |
| medication_count | INTEGER | Count of medications |
| procedure_count | INTEGER | Count of procedures |
| total_event_count | INTEGER | Sum of all events |
| total_condition_cost | DECIMAL | Sum of condition costs |
| total_medication_cost | DECIMAL | Sum of medication costs |
| total_procedure_cost | DECIMAL | Sum of procedure costs |
| total_event_cost | DECIMAL | Sum of all event costs |

#### FR-8: Intermediate - Patients with Conditions

**Priority**: P2 (Medium)

Pre-compute patient condition history.

**Acceptance Criteria**:

- [ ] Active conditions list
- [ ] Condition count
- [ ] First diagnosis date
- [ ] Chronic condition flags

**Columns**:

| Column | Type | Description |
|--------|------|-------------|
| patient_id | VARCHAR | FK to dim_patients |
| total_conditions | INTEGER | Total condition count |
| active_conditions | INTEGER | Conditions without end date |
| first_condition_date | DATE | Earliest condition |
| last_condition_date | DATE | Most recent condition |
| has_diabetes | BOOLEAN | Chronic condition flag |
| has_hypertension | BOOLEAN | Chronic condition flag |
| has_heart_disease | BOOLEAN | Chronic condition flag |
| chronic_condition_count | INTEGER | Count of chronic conditions |

#### FR-9: Fact - Encounters Monthly (fct_encounters_monthly)

**Priority**: P2 (Medium)

Grain: One row per month x encounter_class for time-series analysis.

**Acceptance Criteria**:

- [ ] Monthly aggregation of encounter metrics
- [ ] Unique patient counts per period
- [ ] Cost summaries by period and class
- [ ] Average duration calculations

**Columns**:

| Column | Type | Description |
|--------|------|-------------|
| year_month | VARCHAR | YYYY-MM format |
| year_actual | INTEGER | Year |
| month_actual | INTEGER | Month (1-12) |
| encounter_class | VARCHAR | ambulatory, inpatient, etc. |
| encounter_count | INTEGER | Count of encounters |
| unique_patients | INTEGER | Distinct patient count |
| total_claim_cost | DECIMAL | Sum of claims |
| total_payer_coverage | DECIMAL | Sum of coverage |
| total_patient_responsibility | DECIMAL | Sum of patient cost |
| avg_duration_minutes | DECIMAL | Average encounter duration |

#### FR-10: Fact - Encounters Yearly (fct_encounters_yearly)

**Priority**: P2 (Medium)

Grain: One row per year x encounter_class for annual reporting.

**Acceptance Criteria**:

- [ ] Yearly aggregation of encounter metrics
- [ ] Unique patient counts per year
- [ ] Cost summaries by year and class
- [ ] Encounters per patient ratio

**Columns**:

| Column | Type | Description |
|--------|------|-------------|
| year_actual | INTEGER | Year |
| encounter_class | VARCHAR | ambulatory, inpatient, etc. |
| encounter_count | INTEGER | Count of encounters |
| unique_patients | INTEGER | Distinct patient count |
| total_claim_cost | DECIMAL | Sum of claims |
| total_payer_coverage | DECIMAL | Sum of coverage |
| total_patient_responsibility | DECIMAL | Sum of patient cost |
| avg_duration_minutes | DECIMAL | Average encounter duration |
| encounters_per_patient | DECIMAL | Average encounters per patient |

---

### Non-Functional Requirements

#### NFR-1: Materialization

- Dimensions: TABLE (for performance)
- Facts: TABLE (for aggregation performance)
- Intermediate: VIEW or TABLE (based on size)
- Aggregates: TABLE (for dashboard performance)

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
select
    p.gender,
    p.age_years,
    count(distinct e.encounter_id) as encounter_count
from dim_patients p
join fct_encounters e on p.patient_id = e.patient_id
where p.state = 'Massachusetts'
  and p.age_years between 40 and 60
  and p.is_current = true
group by 1, 2
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
select
    year_month,
    encounter_class,
    encounter_count,
    total_claim_cost,
    avg_duration_minutes
from fct_encounters_monthly
where year_actual = 2020
order by year_month, encounter_class
```

### US-3: Clinical Event Tracking

**As a** clinical researcher
**I want** to track clinical events across patients
**So that** I can analyze treatment patterns

**Acceptance Criteria**:

- Can query conditions, medications, procedures uniformly
- Can analyze event sequences
- Can identify common co-occurrences

### US-4: Payer Analysis

**As a** financial analyst
**I want** to analyze payer performance and coverage
**So that** I can optimize payer contracts

**Acceptance Criteria**:

- Can compare coverage rates across payers
- Can analyze payer costs by encounter class
- Can identify high-value payers

**Example Query**:

```sql
select
    py.payer_name,
    py.coverage_rate,
    count(e.encounter_id) as encounter_count,
    sum(e.payer_coverage) as total_coverage,
    sum(e.patient_responsibility) as total_patient_responsibility
from dim_payers py
join fct_encounters e on py.payer_id = e.payer_id
group by 1, 2
order by total_coverage desc
```

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
│       ├── _healthcare__models.yml
│       ├── int_encounters__enriched.sql
│       └── int_patients__with_conditions.sql
└── marts/
    └── core/
        ├── _core__models.yml
        ├── dim_date.sql
        ├── dim_organizations.sql
        ├── dim_payers.sql
        ├── dim_providers.sql
        ├── dim_patients.sql
        ├── fct_encounters.sql
        ├── fct_clinical_events.sql
        ├── fct_encounters_monthly.sql
        └── fct_encounters_yearly.sql
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
          config:
            where: "is_current = true"
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

- name: fct_encounters_monthly
  data_tests:
    - dbt_utils.unique_combination_of_columns:
        combination_of_columns:
          - year_month
          - encounter_class
```

---

## Implementation Notes

### Date Dimension Generation

Use `dbt_date` package for date spine:

```sql
{{ dbt_date.get_date_dimension('1909-01-01', '2025-12-31') }}
```

Or generate manually:

```sql
with date_spine as (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="'1909-01-01'",
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

### SCD Type 2 Implementation

For initial load:

```sql
select
    row_number() over (order by patient_id) as patient_key,
    patient_id,
    -- ... attributes ...
    birth_date as valid_from,
    null::date as valid_to,
    true as is_current
from source
```

---

## Agent Assignment

| Task | Agent | Notes |
|------|-------|-------|
| Dimensional design | data-modeler | Overall design decisions |
| dim_date | dbt-developer | Use dbt_date package |
| dim_organizations | dbt-developer | Simple dimension |
| dim_payers | dbt-developer | Full dimension with derived fields |
| dim_providers | dbt-developer | Depends on dim_organizations |
| dim_patients | dbt-developer | SCD Type 2 implementation |
| fct_encounters | dbt-developer | Core fact with all dimension keys |
| fct_clinical_events | dbt-developer | Union pattern |
| Aggregate facts | dbt-developer | Monthly and yearly rollups |
| Intermediate models | dbt-developer | Views for common enrichments |
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
| Date range size (117 years) | Low | Low | Use dbt_date, test performance |
| SCD Type 2 complexity | Medium | Low | Start with initial load pattern |

---

## References

- [Kimball Dimensional Modeling](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
- [dbt Marts Best Practices](https://docs.getdbt.com/guides/best-practices/how-we-structure/4-marts)
- [dbt_utils Testing](https://github.com/dbt-labs/dbt-utils#schema-tests)
- [dbt_date Package](https://github.com/calogica/dbt-date)
- [v0.4 Implementation Plan](../plans/v0.4_PLAN.md)

---

*PRD Status: Approved - Ready for Implementation*
