# TDD-004: Dimensional Models

## Overview

**Source PRD**: PRD-004-DIMENSIONAL-MODELS
**Author**: Technical Architect
**Status**: Draft
**Created**: 2026-01-29
**Updated**: 2026-01-29

### Summary

This TDD specifies the technical implementation for building a Kimball-style dimensional model layer consisting of 5 dimension tables, 2 fact tables, 2 intermediate models, and 2 aggregate fact tables. The design leverages existing staging models (v0.3) and follows established project patterns for SQL formatting, testing, and documentation.

Key implementation decisions:

- **Surrogate keys**: `row_number()` for deterministic, order-dependent keys
- **SCD Type 2**: Initial load pattern for `dim_patients` with valid_from/valid_to
- **Union pattern**: `fct_clinical_events` consolidates conditions, medications, procedures
- **Date dimension**: 1909-01-01 to 2025-12-31 using `dbt_date.get_date_dimension()`

---

## Architecture

### High-Level Design

```text
                        STAGING LAYER (v0.3)
    +----------------------------------------------------------+
    |  stg_synthea__patients    stg_synthea__encounters        |
    |  stg_synthea__providers   stg_synthea__conditions        |
    |  stg_synthea__organizations  stg_synthea__medications    |
    |  stg_synthea__payers      stg_synthea__procedures        |
    +----------------------------------------------------------+
                              |
                              v
                       DIMENSIONAL LAYER (v0.4)
    +----------------------------------------------------------+
    |                                                          |
    |  DIMENSIONS (Descriptive Context)                        |
    |  +------------+  +-------------+  +-----------------+    |
    |  | dim_date   |  | dim_patients|  | dim_organizations|   |
    |  | (calendar) |  | (SCD Type 2)|  |                  |   |
    |  +------------+  +-------------+  +-----------------+    |
    |  +-------------+  +-------------+                        |
    |  | dim_payers  |  | dim_providers|                       |
    |  +-------------+  +-------------+                        |
    |                                                          |
    |  FACTS (Measurable Events)                               |
    |  +----------------+  +----------------------+             |
    |  | fct_encounters |  | fct_clinical_events  |            |
    |  | (grain: 1/enc) |  | (grain: 1/event)     |            |
    |  +----------------+  +----------------------+             |
    |                              |                            |
    |  INTERMEDIATE (Pre-computed)                             |
    |  +------------------------+  +---------------------------+|
    |  | int_encounters__enriched|  | int_patients__with_cond  ||
    |  +------------------------+  +---------------------------+|
    |                              |                            |
    |  AGGREGATES (Performance)                                |
    |  +------------------------+  +------------------------+  |
    |  | fct_encounters_monthly |  | fct_encounters_yearly  |  |
    |  +------------------------+  +------------------------+  |
    +----------------------------------------------------------+
```

### Model Dependency DAG

```text
dim_date ─────────────────────────────────────┐
                                              │
dim_organizations ────────────────────────────┼──┐
         │                                    │  │
         v                                    │  │
dim_providers ────────────────────────────────┼──┼──┐
                                              │  │  │
dim_payers ───────────────────────────────────┼──┼──┼──┐
                                              │  │  │  │
dim_patients ─────────────────────────────────┼──┼──┼──┼──┐
                                              │  │  │  │  │
                                              v  v  v  v  v
                                         fct_encounters
                                              │
                      ┌───────────────────────┼───────────────────────┐
                      v                       v                       v
              fct_clinical_events   int_encounters__enriched   int_patients__with_conditions
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      v                                               v
              fct_encounters_monthly                        fct_encounters_yearly
```

### Components

| Component | Purpose | Location |
|-----------|---------|----------|
| dim_date | Calendar dimension (1909-2025) | `models/marts/core/dim_date.sql` |
| dim_patients | Patient dimension with SCD Type 2 | `models/marts/core/dim_patients.sql` |
| dim_providers | Provider dimension | `models/marts/core/dim_providers.sql` |
| dim_organizations | Healthcare facility dimension | `models/marts/core/dim_organizations.sql` |
| dim_payers | Insurance payer dimension | `models/marts/core/dim_payers.sql` |
| fct_encounters | Encounter fact table | `models/marts/core/fct_encounters.sql` |
| fct_clinical_events | Unified clinical events fact | `models/marts/core/fct_clinical_events.sql` |
| int_encounters__enriched | Pre-computed encounter metrics | `models/intermediate/healthcare/int_encounters__enriched.sql` |
| int_patients__with_conditions | Pre-computed patient conditions | `models/intermediate/healthcare/int_patients__with_conditions.sql` |
| fct_encounters_monthly | Monthly aggregate | `models/marts/core/fct_encounters_monthly.sql` |
| fct_encounters_yearly | Yearly aggregate | `models/marts/core/fct_encounters_yearly.sql` |

---

## Architecture Decisions

### AD-1: Surrogate Key Generation Strategy

**Decision**: Use `row_number() over (order by natural_key)` for surrogate keys

**Options Evaluated**:

| Option | Pros | Cons |
|--------|------|------|
| `row_number()` | Deterministic, integer type, efficient joins | Order-dependent, may change on full refresh |
| `hash(natural_key)` | Order-independent, stable across refreshes | Larger storage (string), collision risk |
| `dbt_utils.generate_surrogate_key()` | Handles composite keys well | String type, less efficient for joins |

**Rationale**: For this learning project with small data volumes and full refreshes, `row_number()` provides:

- Simple, readable SQL
- Integer keys (better join performance in DuckDB)
- Deterministic ordering when natural key ordering is consistent

**Pattern**:

```sql
row_number() over (order by patient_id) as patient_key
```

**Note**: Production systems with incremental loads should consider hash-based keys for stability.

### AD-2: SCD Type 2 Implementation for dim_patients

**Decision**: Implement SCD Type 2 structure with initial load pattern (all records current)

**SCD Type 2 Columns**:

| Column | Type | Purpose |
|--------|------|---------|
| valid_from | DATE | Record effective start date |
| valid_to | DATE | Record effective end date (NULL = current) |
| is_current | BOOLEAN | Flag for current record (TRUE/FALSE) |

**Initial Load Pattern**:

For the first load where no historical changes exist:

```sql
-- All records are current with no history
, current_date as valid_from
, cast(null as date) as valid_to
, true as is_current
```

**Future Change Tracking Pattern** (for reference, not implemented in v0.4):

```sql
-- When detecting changes via snapshots
, lag(effective_date) over (partition by patient_id order by effective_date) as valid_from
, lead(effective_date) over (partition by patient_id order by effective_date) as valid_to
, row_number() over (partition by patient_id order by effective_date desc) = 1 as is_current
```

**Rationale**: This establishes the SCD Type 2 schema structure for future change tracking while keeping v0.4 scope manageable. The `is_current = true` filter enables efficient queries for current state.

### AD-3: Union Pattern for fct_clinical_events

**Decision**: Use UNION ALL with explicit type discriminator column

**Pattern**:

```sql
with conditions as (
    select
        'CONDITION' as event_type
        , condition_id as event_id
        , patient_id
        , encounter_id
        , condition_start_date as event_start_date
        , condition_end_date as event_end_date
        , condition_code as code
        , 'SNOMED-CT' as code_system
        , condition_description as description
        , cast(null as decimal(18,2)) as event_cost
    from {{ ref('stg_synthea__conditions') }}
),

medications as (
    select
        'MEDICATION' as event_type
        , medication_id as event_id
        , patient_id
        , encounter_id
        , cast(medication_start_at as date) as event_start_date
        , cast(medication_end_at as date) as event_end_date
        , medication_code as code
        , 'RXNORM' as code_system
        , medication_description as description
        , total_cost as event_cost
    from {{ ref('stg_synthea__medications') }}
),

procedures as (
    select
        'PROCEDURE' as event_type
        , procedure_id as event_id
        , patient_id
        , encounter_id
        , cast(procedure_at as date) as event_start_date
        , cast(null as date) as event_end_date
        , procedure_code as code
        , 'SNOMED-CT' as code_system
        , procedure_description as description
        , base_cost as event_cost
    from {{ ref('stg_synthea__procedures') }}
),

unioned as (
    select * from conditions
    union all
    select * from medications
    union all
    select * from procedures
)

select
    row_number() over (order by event_type, event_id) as clinical_event_key
    , *
from unioned
```

**Rationale**:

- Enables unified querying across all clinical event types
- Preserves source-specific attributes via discriminator column
- Code system column enables filtering by terminology
- Explicit NULL casts ensure column alignment

### AD-4: Aggregate Fact Design

**Decision**: Create pre-aggregated fact tables at monthly and yearly grain

**Monthly Grain**: `fct_encounters_monthly`

- Grain: One row per (year, month, encounter_class)
- Metrics: count, distinct patients, costs, avg duration

**Yearly Grain**: `fct_encounters_yearly`

- Grain: One row per (year, encounter_class)
- Metrics: Same as monthly plus encounters_per_patient

**Rationale**:

- Common analytics queries aggregate to month/year level
- Pre-aggregation improves dashboard query performance
- Materialized as tables for consistent performance

---

## Data Model

### Entity-Relationship Diagram

```text
                     +------------------+
                     |    dim_date      |
                     +------------------+
                     | date_key (PK)    |
                     | date_actual      |
                     | day_of_week      |
                     | month_actual     |
                     | year_actual      |
                     | is_weekend       |
                     | is_us_holiday    |
                     +--------+---------+
                              |
        +---------------------+---------------------+
        |                     |                     |
        v                     v                     v
+-------+--------+   +--------+--------+   +-------+--------+
| fct_encounters |   |fct_clinical_evts|   | fct_enc_monthly|
+----------------+   +-----------------+   +----------------+
| encounter_key  |   | clinical_evt_key|   | year_month     |
| encounter_id   |   | event_type      |   | encounter_class|
| patient_key    |-->| patient_key     |   | encounter_count|
| provider_key   |   | encounter_id    |   | total_cost     |
| org_key        |   | event_date_key  |   +----------------+
| payer_key      |   | code            |
| start_date_key |   | description     |
| total_cost     |   | event_cost      |
+-------+--------+   +--------+--------+
        |                     |
        |                     |
        v                     v
+-------+--------+   +--------+--------+
|  dim_patients  |   |  dim_providers  |
+----------------+   +-----------------+
| patient_key    |   | provider_key    |
| patient_id     |   | provider_id     |
| full_name      |   | provider_name   |
| birth_date     |   | specialty       |
| age_years      |   | org_key --------|--+
| is_deceased    |   +-----------------+  |
| valid_from     |                        |
| valid_to       |                        v
| is_current     |            +-----------+------+
+----------------+            | dim_organizations |
                              +------------------+
+----------------+            | organization_key |
|   dim_payers   |            | organization_id  |
+----------------+            | organization_name|
| payer_key      |            | city, state      |
| payer_id       |            | revenue          |
| payer_name     |            +------------------+
| coverage_rate  |
+----------------+
```

### Grain Definitions

| Model | Grain | Natural Key | Description |
|-------|-------|-------------|-------------|
| dim_date | One row per calendar day | date_actual | All dates from 1909-01-01 to 2025-12-31 |
| dim_patients | One row per patient version | patient_id + valid_from | SCD Type 2 (v0.4: one version per patient) |
| dim_providers | One row per provider | provider_id | Static dimension |
| dim_organizations | One row per organization | organization_id | Static dimension |
| dim_payers | One row per payer | payer_id | Static dimension |
| fct_encounters | One row per encounter | encounter_id | Transactional fact |
| fct_clinical_events | One row per clinical event | event_type + event_id | Union of conditions, medications, procedures |
| fct_encounters_monthly | One row per month + class | year_month + encounter_class | Periodic snapshot |
| fct_encounters_yearly | One row per year + class | year_actual + encounter_class | Periodic snapshot |

### Dimension Type Classifications

| Dimension | Type | Rationale |
|-----------|------|-----------|
| dim_date | Role-playing | Used for encounter start, end, event dates |
| dim_patients | SCD Type 2 | Demographics may change over time |
| dim_providers | SCD Type 1 | Provider changes overwrite (no history needed) |
| dim_organizations | SCD Type 1 | Facility changes overwrite |
| dim_payers | SCD Type 1 | Payer changes overwrite |

---

## Technical Specifications

### Materialization Strategy

| Model | Materialization | Rationale |
|-------|-----------------|-----------|
| dim_date | table | Large static dimension, queried frequently |
| dim_patients | table | SCD Type 2 requires table for versioning |
| dim_providers | table | Performance for joins |
| dim_organizations | table | Performance for joins |
| dim_payers | table | Performance for joins |
| fct_encounters | table | Core fact, aggregation performance |
| fct_clinical_events | table | Large union, aggregation performance |
| int_encounters__enriched | view | Derived from fact, low overhead |
| int_patients__with_conditions | view | Derived from staging, low overhead |
| fct_encounters_monthly | table | Pre-aggregated for dashboards |
| fct_encounters_yearly | table | Pre-aggregated for dashboards |

### dbt Configuration

```yaml
# dbt_project.yml additions
models:
  healthcare_analytics:
    marts:
      core:
        +materialized: table
        +schema: marts
        +tags: ['marts', 'dimensional']
    intermediate:
      healthcare:
        +materialized: view
        +schema: intermediate
        +tags: ['intermediate']

# Project variables for dim_date
vars:
  "dbt_date:time_zone": "America/New_York"
```

### Model Configurations

```sql
-- Dimension table config
{{
  config(
    materialized='table',
    unique_key='patient_key'
  )
}}

-- Fact table config
{{
  config(
    materialized='table',
    unique_key='encounter_key'
  )
}}

-- Intermediate view config
{{
  config(
    materialized='view'
  )
}}
```

### Package Dependencies

| Package | Version | Usage |
|---------|---------|-------|
| dbt_utils | 1.3.3 | `generate_surrogate_key`, `unique_combination_of_columns` |
| dbt_date | 0.17.1 | `get_date_dimension` for dim_date |
| dbt_expectations | 0.10.10 | Data quality tests |

---

## SQL Patterns

### Pattern 1: Surrogate Key Generation

```sql
with source as (
    select * from {{ ref('stg_synthea__patients') }}
),

final as (
    select
        -- Surrogate key (integer, deterministic order)
        row_number() over (order by patient_id) as patient_key

        -- Natural key
        , patient_id

        -- Attributes
        , first_name
        , last_name
        -- ... additional columns

        -- Metadata
        , current_timestamp as _loaded_at
    from source
)

select * from final
```

### Pattern 2: SCD Type 2 for Initial Load

```sql
with source as (
    select * from {{ ref('stg_synthea__patients') }}
),

with_scd_columns as (
    select
        -- Surrogate key (unique per version)
        row_number() over (order by patient_id) as patient_key

        -- Natural key
        , patient_id

        -- Attributes
        , first_name
        , last_name
        , first_name || ' ' || last_name as full_name
        , birth_date
        , death_date

        -- Derived attributes
        , case
            when death_date is not null
            then date_diff('year', birth_date, death_date)
            else date_diff('year', birth_date, current_date)
          end as age_years
        , death_date is not null as is_deceased

        -- SCD Type 2 columns (initial load: all current)
        , current_date as valid_from
        , cast(null as date) as valid_to
        , true as is_current

        -- Metadata
        , current_timestamp as _loaded_at
    from source
)

select * from with_scd_columns
```

### Pattern 3: Date Key Derivation

```sql
-- Convert date/timestamp to integer date key (YYYYMMDD format)
, cast(strftime(encounter_start_at, '%Y%m%d') as integer) as encounter_start_date_key
, cast(strftime(encounter_end_at, '%Y%m%d') as integer) as encounter_end_date_key

-- For date columns
, cast(strftime(event_start_date, '%Y%m%d') as integer) as event_date_key
```

### Pattern 4: Dimension Key Lookup

```sql
with encounters as (
    select * from {{ ref('stg_synthea__encounters') }}
),

dim_patients as (
    select patient_key, patient_id
    from {{ ref('dim_patients') }}
    where is_current = true  -- SCD Type 2: current records only
),

dim_providers as (
    select provider_key, provider_id
    from {{ ref('dim_providers') }}
),

dim_organizations as (
    select organization_key, organization_id
    from {{ ref('dim_organizations') }}
),

dim_payers as (
    select payer_key, payer_id
    from {{ ref('dim_payers') }}
),

joined as (
    select
        row_number() over (order by e.encounter_id) as encounter_key
        , e.encounter_id

        -- Dimension keys (with -1 for missing)
        , coalesce(p.patient_key, -1) as patient_key
        , coalesce(pr.provider_key, -1) as provider_key
        , coalesce(o.organization_key, -1) as organization_key
        , coalesce(py.payer_key, -1) as payer_key

        -- Natural keys (for debugging/audit)
        , e.patient_id
        , e.provider_id
        , e.organization_id
        , e.payer_id

        -- Measures and attributes
        , e.total_claim_cost
        -- ... additional columns

    from encounters e
    left join dim_patients p on e.patient_id = p.patient_id
    left join dim_providers pr on e.provider_id = pr.provider_id
    left join dim_organizations o on e.organization_id = o.organization_id
    left join dim_payers py on e.payer_id = py.payer_id
)

select * from joined
```

### Pattern 5: Union Pattern for Clinical Events

```sql
with conditions as (
    select
        'CONDITION' as event_type
        , condition_id as event_id
        , patient_id
        , encounter_id
        , condition_start_date as event_start_date
        , condition_end_date as event_end_date
        , condition_code as code
        , 'SNOMED-CT' as code_system
        , condition_description as description
        , cast(null as decimal(18,2)) as event_cost
        , cast(null as varchar) as reason_code
        , cast(null as varchar) as reason_description
    from {{ ref('stg_synthea__conditions') }}
),

medications as (
    select
        'MEDICATION' as event_type
        , medication_id as event_id
        , patient_id
        , encounter_id
        , cast(medication_start_at as date) as event_start_date
        , cast(medication_end_at as date) as event_end_date
        , medication_code as code
        , 'RXNORM' as code_system
        , medication_description as description
        , total_cost as event_cost
        , reason_code
        , reason_description
    from {{ ref('stg_synthea__medications') }}
),

procedures as (
    select
        'PROCEDURE' as event_type
        , procedure_id as event_id
        , patient_id
        , encounter_id
        , cast(procedure_at as date) as event_start_date
        , cast(null as date) as event_end_date
        , procedure_code as code
        , 'SNOMED-CT' as code_system
        , procedure_description as description
        , base_cost as event_cost
        , reason_code
        , reason_description
    from {{ ref('stg_synthea__procedures') }}
),

unioned as (
    select * from conditions
    union all
    select * from medications
    union all
    select * from procedures
)

select
    row_number() over (order by event_type, event_id) as clinical_event_key
    , *
    , current_timestamp as _loaded_at
from unioned
```

### Pattern 6: Aggregate Fact Pattern

```sql
-- fct_encounters_monthly.sql
with encounters as (
    select * from {{ ref('fct_encounters') }}
),

dim_date as (
    select * from {{ ref('dim_date') }}
),

monthly_aggregates as (
    select
        -- Grain columns
        d.year_actual || '-' || lpad(cast(d.month_actual as varchar), 2, '0') as year_month
        , d.year_actual
        , d.month_actual
        , e.encounter_class

        -- Measures
        , count(*) as encounter_count
        , count(distinct e.patient_id) as unique_patients
        , sum(e.total_claim_cost) as total_claim_cost
        , sum(e.payer_coverage) as total_payer_coverage
        , sum(e.patient_responsibility) as total_patient_responsibility
        , avg(e.duration_minutes) as avg_duration_minutes

    from encounters e
    inner join dim_date d on e.encounter_start_date_key = d.date_key
    group by 1, 2, 3, 4
)

select
    *
    , current_timestamp as _loaded_at
from monthly_aggregates
```

### Pattern 7: dim_date Generation

```sql
-- dim_date.sql
{{
  config(
    materialized='table',
    unique_key='date_key'
  )
}}

with date_dimension as (
    {{ dbt_date.get_date_dimension("1909-01-01", "2025-12-31") }}
)

select
    -- Surrogate key (YYYYMMDD integer)
    cast(strftime(date_day, '%Y%m%d') as integer) as date_key

    -- Date actual
    , date_day as date_actual

    -- Day attributes
    , day_of_week
    , day_of_week_name as day_name
    , day_of_week_name_short as day_name_short
    , day_of_month
    , day_of_year

    -- Week attributes
    , week_of_year
    , iso_week_of_year

    -- Month attributes
    , month_of_year as month_actual
    , month_name
    , month_name_short

    -- Quarter attributes
    , quarter_of_year as quarter_actual
    , 'Q' || cast(quarter_of_year as varchar) as quarter_name

    -- Year attributes
    , year_number as year_actual

    -- Flags
    , day_of_week in (6, 7) as is_weekend

    -- US Holiday placeholder (can enhance later)
    , false as is_us_holiday
    , cast(null as varchar) as holiday_name

    -- Metadata
    , current_timestamp as _loaded_at

from date_dimension
```

---

## Testing Strategy

### Required Tests by Model Type

| Model Type | Required Tests |
|------------|----------------|
| All dimensions | unique + not_null on surrogate key |
| All dimensions | unique on natural key |
| All facts | unique + not_null on surrogate key |
| Facts with FK | relationships to dimensions |
| Aggregates | unique_combination_of_columns on grain |
| SCD Type 2 | is_current validation |

### Referential Integrity Tests

```yaml
# _core__models.yml
version: 2

models:
  - name: fct_encounters
    description: Healthcare encounter fact table
    data_tests:
      # Grain test
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns:
            - encounter_id
    columns:
      - name: encounter_key
        description: Surrogate key
        data_tests:
          - unique
          - not_null
      - name: encounter_id
        description: Natural key (UUID)
        data_tests:
          - unique
          - not_null
      - name: patient_id
        description: Patient natural key
        data_tests:
          - not_null
          - relationships:
              to: ref('dim_patients')
              field: patient_id
              config:
                where: "is_current = true"
      - name: provider_id
        data_tests:
          - relationships:
              to: ref('dim_providers')
              field: provider_id
              config:
                severity: warn  # Allow orphans during transition
      - name: organization_id
        data_tests:
          - relationships:
              to: ref('dim_organizations')
              field: organization_id
      - name: payer_id
        data_tests:
          - relationships:
              to: ref('dim_payers')
              field: payer_id
      - name: encounter_start_date_key
        description: FK to dim_date
        data_tests:
          - not_null
          - relationships:
              to: ref('dim_date')
              field: date_key
```

### Grain Tests

```yaml
# Ensure no duplicate grains in aggregate facts
models:
  - name: fct_encounters_monthly
    data_tests:
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns:
            - year_month
            - encounter_class

  - name: fct_encounters_yearly
    data_tests:
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns:
            - year_actual
            - encounter_class
```

### SCD Type 2 Validation Tests

```yaml
# dim_patients specific tests
models:
  - name: dim_patients
    data_tests:
      # Each patient_id should have exactly one current record
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns:
            - patient_id
          config:
            where: "is_current = true"
    columns:
      - name: is_current
        data_tests:
          - not_null
          - accepted_values:
              values: [true, false]
      - name: valid_from
        data_tests:
          - not_null
```

### Data Quality Tests

```yaml
# Date range validation
columns:
  - name: date_actual
    data_tests:
      - dbt_expectations.expect_column_values_to_be_between:
          min_value: "'1909-01-01'"
          max_value: "'2025-12-31'"

# Non-negative costs
  - name: total_claim_cost
    data_tests:
      - dbt_expectations.expect_column_values_to_be_between:
          min_value: 0
          config:
            severity: warn

# Valid duration
  - name: duration_minutes
    data_tests:
      - dbt_expectations.expect_column_values_to_be_between:
          min_value: 0
          max_value: 525600  # 1 year in minutes
```

### Test Commands

```bash
# Test all marts models
uv run dbt test --select tag:marts

# Test specific model with dependencies
uv run dbt test --select fct_encounters+

# Test referential integrity only
uv run dbt test --select tag:marts,test_type:relationships

# Full build with tests
uv run dbt build --select tag:marts
```

---

## File Changes

| File | Change Type | Description |
|------|-------------|-------------|
| `models/marts/core/dim_date.sql` | Create | Calendar dimension using dbt_date |
| `models/marts/core/dim_patients.sql` | Create | Patient dimension with SCD Type 2 |
| `models/marts/core/dim_providers.sql` | Create | Provider dimension |
| `models/marts/core/dim_organizations.sql` | Create | Organization dimension |
| `models/marts/core/dim_payers.sql` | Create | Payer dimension |
| `models/marts/core/fct_encounters.sql` | Create | Encounter fact table |
| `models/marts/core/fct_clinical_events.sql` | Create | Unified clinical events fact |
| `models/marts/core/fct_encounters_monthly.sql` | Create | Monthly aggregate fact |
| `models/marts/core/fct_encounters_yearly.sql` | Create | Yearly aggregate fact |
| `models/marts/core/_core__models.yml` | Create | Model documentation and tests |
| `models/intermediate/healthcare/int_encounters__enriched.sql` | Create | Enriched encounters view |
| `models/intermediate/healthcare/int_patients__with_conditions.sql` | Create | Patient conditions view |
| `models/intermediate/healthcare/_healthcare__models.yml` | Create | Intermediate model docs |
| `dbt_project.yml` | Modify | Add dbt_date timezone variable |

---

## Implementation Sequence

### Phase 1: Foundation Dimensions (No Dependencies)

1. [ ] Create `models/marts/core/` directory structure
2. [ ] Implement `dim_date.sql` using dbt_date package
3. [ ] Implement `dim_organizations.sql`
4. [ ] Implement `dim_payers.sql` with derived coverage_rate
5. [ ] Add basic tests and documentation

### Phase 2: Dependent Dimensions

6. [ ] Implement `dim_providers.sql` (references dim_organizations)
7. [ ] Implement `dim_patients.sql` with SCD Type 2 structure
8. [ ] Add dimension tests (unique, not_null, relationships)

### Phase 3: Core Facts

9. [ ] Implement `fct_encounters.sql` with all dimension joins
10. [ ] Implement `fct_clinical_events.sql` with union pattern
11. [ ] Add referential integrity tests

### Phase 4: Intermediate Models

12. [ ] Create `models/intermediate/healthcare/` directory
13. [ ] Implement `int_encounters__enriched.sql`
14. [ ] Implement `int_patients__with_conditions.sql`
15. [ ] Add intermediate model documentation

### Phase 5: Aggregate Facts

16. [ ] Implement `fct_encounters_monthly.sql`
17. [ ] Implement `fct_encounters_yearly.sql`
18. [ ] Add grain tests for aggregates

### Phase 6: Validation

19. [ ] Run full test suite: `dbt build --select tag:marts`
20. [ ] Validate example queries from PRD-004
21. [ ] Generate documentation: `dbt docs generate`
22. [ ] Update CHANGELOG

---

## Performance Considerations

### dim_date Size

- **Date range**: 1909-01-01 to 2025-12-31 = 42,735 rows
- **Storage**: Minimal (~5MB with all columns)
- **Recommendation**: No concerns for this size; materialized as table for join performance

### Query Optimization Notes

**Star Schema Joins**: DuckDB handles star schema joins efficiently. No special indexing required for this data volume.

**Date Key Pattern**: Integer date keys (YYYYMMDD) enable:

- Efficient range queries: `WHERE date_key BETWEEN 20200101 AND 20201231`
- Simple partition pruning
- Human-readable values in results

**Aggregate Tables**: Pre-aggregated monthly/yearly tables should be used for:

- Dashboard queries
- Trend analysis
- Any query that would otherwise scan full fact table

### Estimated Row Counts

| Model | Estimated Rows | Notes |
|-------|----------------|-------|
| dim_date | 42,735 | 117 years of dates |
| dim_patients | ~500 | From Synthea sample |
| dim_providers | ~100 | From Synthea sample |
| dim_organizations | ~10 | From Synthea sample |
| dim_payers | ~10 | From Synthea sample |
| fct_encounters | ~10,000 | ~20 per patient avg |
| fct_clinical_events | ~50,000 | ~100 events per patient avg |
| fct_encounters_monthly | ~1,000 | ~100 months x ~10 classes |
| fct_encounters_yearly | ~100 | ~10 years x ~10 classes |

---

## Migration/Rollback

### Deployment Steps

```bash
# 1. Ensure staging models are current
uv run dbt build --select tag:staging

# 2. Build dimensions first (dependency order)
uv run dbt run --select dim_date dim_organizations dim_payers
uv run dbt run --select dim_providers dim_patients

# 3. Build facts
uv run dbt run --select fct_encounters fct_clinical_events

# 4. Build intermediate models
uv run dbt run --select int_encounters__enriched int_patients__with_conditions

# 5. Build aggregates
uv run dbt run --select fct_encounters_monthly fct_encounters_yearly

# 6. Run all tests
uv run dbt test --select tag:marts

# 7. Generate documentation
uv run dbt docs generate
```

### Rollback Procedure

If issues are discovered after deployment:

```bash
# 1. Drop all marts tables (DuckDB specific)
# Connect to DuckDB and run:
DROP SCHEMA IF EXISTS marts CASCADE;

# 2. Revert code changes
git checkout main -- models/marts/
git checkout main -- models/intermediate/

# 3. Rebuild staging if needed
uv run dbt build --select tag:staging
```

### Validation Queries

```sql
-- Verify dim_date range
SELECT min(date_actual), max(date_actual), count(*) as row_count
FROM marts.dim_date;
-- Expected: 1909-01-01, 2025-12-31, 42735

-- Verify SCD Type 2 (all patients current)
SELECT is_current, count(*) as patient_count
FROM marts.dim_patients
GROUP BY is_current;
-- Expected: true, [patient count]

-- Verify referential integrity
SELECT count(*) as orphan_encounters
FROM marts.fct_encounters e
WHERE NOT EXISTS (
    SELECT 1 FROM marts.dim_patients p
    WHERE p.patient_id = e.patient_id AND p.is_current = true
);
-- Expected: 0

-- Verify grain (no duplicates)
SELECT encounter_id, count(*) as cnt
FROM marts.fct_encounters
GROUP BY encounter_id
HAVING count(*) > 1;
-- Expected: 0 rows
```

---

## Security Considerations

- Patient PII (SSN) is already hashed in staging layer
- No additional PII masking required in dimensional models
- Location data (lat/lon) retained for geographic analysis
- Costs retained as business metrics (no special handling)

---

## Open Questions

1. **Holiday calendar**: Should we populate US federal holidays in dim_date, or leave as placeholder?
   - *Recommendation*: Leave as placeholder for v0.4, enhance in future sprint

2. **Unknown dimension members**: Should we add explicit "Unknown" rows (key = -1) to dimensions?
   - *Recommendation*: Use COALESCE pattern in facts; add Unknown members in v0.5 if needed

3. **Incremental loads**: Should we design for incremental updates?
   - *Recommendation*: Full refresh for v0.4; consider incremental in v0.5 with higher data volumes

---

## Related

- **PRD**: [PRD-004-DIMENSIONAL-MODELS](./PRD-004-DIMENSIONAL-MODELS.md)
- **Plan**: [v0.4_PLAN](../plans/v0.4_PLAN.md)
- **Standards**: [DBT_CODING_STANDARDS](../reference/DBT_CODING_STANDARDS.md)
- **Testing**: [DBT_TESTING_STANDARDS](../reference/DBT_TESTING_STANDARDS.md)

---

*TDD Status: Draft - Ready for Review*
