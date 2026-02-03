# Data Quality Quarantine - Reference Guide

A practical guide to implementing and monitoring the macro-based data quality quarantine pattern.

**See Also**: [ADR-004](../decisions/ADR-004-data-quality-quarantine.md) for architectural decisions and rationale.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core Concepts](#core-concepts)
3. [Adding Quarantine to a New Model](#adding-quarantine-to-a-new-model)
4. [Monitoring Data Quality](#monitoring-data-quality)
5. [Debugging Quarantined Records](#debugging-quarantined-records)
6. [Validation Rule Patterns](#validation-rule-patterns)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Add DQ flags to staging model

```sql
-- models/staging/synthea/stg_synthea__my_entity.sql

with source as (
    select * from {{ source('synthea_raw', 'my_table') }}
),

renamed as (
    select
        id as entity_id,
        cast(start_time as timestamp) as start_at,
        cast(end_time as timestamp) as end_at
    from source
),

with_dq_flags as (
    {{ add_dq_flags(
        source_cte='renamed',
        validations={
            'valid_timestamps': 'end_at >= start_at',
            'no_future_dates': 'start_at <= current_timestamp'
        }
    ) }}
),

final as (
    select
        *,
        current_timestamp as _loaded_at
    from with_dq_flags
)

select * from final
```

### 2. Create quarantine table

```sql
-- models/intermediate/quarantine/int_dq_quarantine__my_entity.sql

{{ config(
    materialized='table',
    tags=['intermediate', 'quarantine', 'data_quality']
) }}

{{ generate_quarantine_model(
    source_model='stg_synthea__my_entity',
    description='My entities quarantined due to data quality violations'
) }}
```

### 3. Filter in downstream models

```sql
-- models/marts/core/fct_my_entities.sql

with my_entities as (
    select * from {{ ref('stg_synthea__my_entity') }}
    {{ quarantine_filter() }}
)

select * from my_entities
```

### 4. Document in YAML

```yaml
# models/intermediate/quarantine/_quarantine__models.yml

models:
  - name: int_dq_quarantine__my_entity
    description: "Quarantined records with data quality violations"
    columns:
      - name: entity_id
        tests:
          - unique
          - not_null
      - name: is_dq_valid
        tests:
          - accepted_values:
              values: [false]
      - name: failed_dq_tests
        tests:
          - not_null
```

---

## Core Concepts

### The Quarantine Flow

```
┌─────────────────────────────────────────────────────────────┐
│ STAGING: Flag invalid records                              │
│   stg_synthea__encounters                                   │
│   ├─ All columns from source                                │
│   ├─ valid_encounter_timestamps: bool                       │
│   ├─ no_future_encounter_dates: bool                        │
│   ├─ is_dq_valid: bool (AND of all validations)            │
│   └─ failed_dq_tests: varchar[] (array of failed rules)    │
└─────────────────────────────────────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
            ▼                         ▼
┌──────────────────────┐  ┌──────────────────────────┐
│ VALID RECORDS        │  │ INVALID RECORDS          │
│ (is_dq_valid=true)   │  │ (is_dq_valid=false)      │
│                      │  │                          │
│ ↓                    │  │ ↓                        │
│ fct_encounters       │  │ int_dq_quarantine__...   │
│ fct_clinical_events  │  │                          │
│ Analytics marts      │  │ ↓                        │
└──────────────────────┘  │ mart_dq_summary          │
                          │ (monitoring)             │
                          └──────────────────────────┘
```

### Three Core Macros

#### `add_dq_flags(source_cte, validations)`

Adds data quality validation columns to a CTE.

**Parameters**:

- `source_cte` (string): Name of the CTE to validate
- `validations` (dict): Map of validation_name → SQL boolean expression

**Returns**:

- All original columns
- Individual boolean flags for each validation
- `is_dq_valid` (boolean): true if ALL validations pass
- `failed_dq_tests` (varchar[]): array of failed validation names

**Example**:

```sql
{{ add_dq_flags(
    source_cte='renamed',
    validations={
        'valid_timestamps': 'end_at >= start_at',
        'no_future_dates': 'start_at <= current_timestamp',
        'end_after_1900': 'end_at >= timestamp \'1900-01-01\''
    }
) }}
```

**Generated columns**:

- `valid_timestamps` (bool)
- `no_future_dates` (bool)
- `end_after_1900` (bool)
- `is_dq_valid` (bool)
- `failed_dq_tests` (varchar[])

#### `quarantine_filter(enabled=true, field_name='is_dq_valid')`

Generates a WHERE clause to filter out quarantined records.

**Parameters**:

- `enabled` (bool, default=true): Whether to apply the filter
- `field_name` (string, default='is_dq_valid'): Name of the validity flag

**Returns**:

- `WHERE is_dq_valid = true` (if enabled)
- Empty string (if disabled)

**Example**:

```sql
with encounters as (
    select * from {{ ref('stg_synthea__encounters') }}
    {{ quarantine_filter() }}
)

-- Debug mode: disable filter to see all records
with encounters_debug as (
    select * from {{ ref('stg_synthea__encounters') }}
    {{ quarantine_filter(enabled=false) }}
)
```

#### `generate_quarantine_model(source_model, description='')`

Generates a complete quarantine model that selects only invalid records.

**Parameters**:

- `source_model` (string): Name of the staging model
- `description` (string, optional): Comment for the model

**Returns**:

- Complete SQL: `SELECT * FROM ref(source_model) WHERE is_dq_valid = false`

**Example**:

```sql
{{ config(materialized='table', tags=['quarantine', 'data_quality']) }}

{{ generate_quarantine_model(
    source_model='stg_synthea__encounters',
    description='Encounters failing data quality validations'
) }}
```

---

## Adding Quarantine to a New Model

Follow this checklist to add data quality quarantine to any entity.

### Step 1: Define Validation Rules

Identify what makes a record "invalid" for your entity:

**Common patterns**:

- Timestamp sequences (end >= start)
- Future date checks (date <= today)
- Historical plausibility (date > 1900)
- Required field combinations
- Range constraints (amount >= 0)
- Foreign key existence

**Example for observations**:

```python
validations = {
    'valid_observation_timestamps': 'observation_at <= current_timestamp',
    'value_in_range': 'value_numeric >= 0 and value_numeric <= 999999',
    'has_code_or_description': 'observation_code is not null or observation_description is not null',
    'date_after_1900': 'observation_at >= timestamp \'1900-01-01\''
}
```

### Step 2: Update Staging Model

Add `with_dq_flags` CTE **before** the `final` CTE:

```sql
-- models/staging/synthea/stg_synthea__observations.sql

with source as (
    select * from {{ source('synthea_raw', 'observations') }}
),

renamed as (
    select
        -- your column mappings
        id as observation_id,
        cast(date as timestamp) as observation_at,
        value as value_numeric,
        code as observation_code,
        description as observation_description
    from source
),

-- NEW: Add this CTE
with_dq_flags as (
    {{ add_dq_flags(
        source_cte='renamed',
        validations={
            'valid_observation_timestamps': 'observation_at <= current_timestamp',
            'value_in_range': 'value_numeric >= 0 and value_numeric <= 999999',
            'has_code_or_description': 'observation_code is not null or observation_description is not null',
            'date_after_1900': 'observation_at >= timestamp \'1900-01-01\''
        }
    ) }}
),

final as (
    select
        *,
        current_timestamp as _loaded_at
    from with_dq_flags  -- CHANGED: was 'renamed'
)

select * from final
```

### Step 3: Create Quarantine Table

```sql
-- models/intermediate/quarantine/int_dq_quarantine__observations.sql

{{ config(
    materialized='table',
    tags=['intermediate', 'quarantine', 'data_quality']
) }}

{{ generate_quarantine_model(
    source_model='stg_synthea__observations',
    description='Observations quarantined due to data quality violations'
) }}
```

### Step 4: Document Quarantine Model

Add to `models/intermediate/quarantine/_quarantine__models.yml`:

```yaml
models:
  - name: int_dq_quarantine__observations
    description: |
      Observations failing data quality validations.

      Quarantine rules:
      - valid_observation_timestamps: observation_at <= current_timestamp
      - value_in_range: value_numeric >= 0 and <= 999999
      - has_code_or_description: code OR description must be present
      - date_after_1900: observation_at >= 1900-01-01

    columns:
      - name: observation_id
        tests:
          - unique
          - not_null

      - name: is_dq_valid
        description: "Always false in quarantine table"
        tests:
          - accepted_values:
              values: [false]

      - name: failed_dq_tests
        description: "Array of failed validation names"
        tests:
          - not_null

      - name: valid_observation_timestamps
        description: "Flag: observation_at <= current_timestamp"

      - name: value_in_range
        description: "Flag: value_numeric between 0 and 999999"

      - name: has_code_or_description
        description: "Flag: At least one of code or description present"

      - name: date_after_1900
        description: "Flag: observation_at >= 1900-01-01"
```

### Step 5: Apply Filter in Downstream Models

Update any fact table or intermediate model that uses the staging model:

```sql
-- BEFORE
with observations as (
    select * from {{ ref('stg_synthea__observations') }}
)

-- AFTER
with observations as (
    select * from {{ ref('stg_synthea__observations') }}
    {{ quarantine_filter() }}
)
```

**Important**: Apply the filter in **every** downstream model to ensure quarantined records never reach analytics.

### Step 6: Update DQ Summary Mart

Add metrics for the new entity to `mart_dq_summary.sql`:

```sql
-- Add this CTE
observation_metrics as (
    select
        'observations' as entity_type,
        count(*) filter (where is_dq_valid = false) as quarantined_count,
        count(*) as total_count,
        round(100.0 * count(*) filter (where is_dq_valid = false) / count(*), 2) as quarantine_rate_pct,
        count(*) filter (where not valid_observation_timestamps) as failed_valid_observation_timestamps,
        count(*) filter (where not value_in_range) as failed_value_in_range,
        count(*) filter (where not has_code_or_description) as failed_has_code_or_description,
        count(*) filter (where not date_after_1900) as failed_date_after_1900
    from {{ ref('stg_synthea__observations') }}
),

-- Add to UNION ALL
union all

select
    entity_type,
    quarantined_count,
    total_count,
    quarantine_rate_pct,
    failed_valid_observation_timestamps as failed_timestamp_validations,
    ...
from observation_metrics
```

### Step 7: Build and Test

```bash
# Build staging + quarantine
dbt run --select stg_synthea__observations int_dq_quarantine__observations

# Check quarantine count
dbt show --inline "
  select is_dq_valid, count(*)
  from {{ ref('stg_synthea__observations') }}
  group by is_dq_valid
"

# Verify quarantine table
dbt test --select int_dq_quarantine__observations

# Full build
dbt build --select stg_synthea__observations+
```

---

## Monitoring Data Quality

### Quarantine Summary Dashboard

Query `mart_dq_summary` for a high-level view:

```sql
select
    entity_type,
    quarantined_count,
    total_count,
    quarantine_rate_pct,
    failed_timestamp_validations,
    failed_future_date_validations
from {{ ref('mart_dq_summary') }}
order by quarantine_rate_pct desc
```

**Expected output**:

```text
entity_type  | quarantined | total  | rate_pct | timestamp_fails | future_date_fails
-------------|-------------|--------|----------|-----------------|------------------
encounters   | 1           | 53,346 | 0.00%    | 1               | 0
medications  | 5           | 42,989 | 0.01%    | 5               | 0
```

### Alert Thresholds

**Recommendation**: Alert when `quarantine_rate_pct > 1%`

**Severity levels**:

- **0-0.1%**: Normal (current baseline)
- **0.1-1%**: Warning (monitor trend)
- **1-5%**: Alert (investigate root cause)
- **>5%**: Critical (potential data pipeline issue)

### Trend Analysis

Track quarantine rates over time:

```sql
-- If you add _loaded_at to mart_dq_summary
select
    date_trunc('day', _generated_at) as day,
    entity_type,
    quarantine_rate_pct
from {{ ref('mart_dq_summary') }}
order by day desc, entity_type
```

### Failed Validation Distribution

See which validation rules fail most often:

```sql
-- For encounters
select
    unnest(failed_dq_tests) as failed_validation,
    count(*) as failure_count
from {{ ref('int_dq_quarantine__encounters') }}
group by 1
order by 2 desc
```

**Example output**:

```text
failed_validation             | failure_count
------------------------------|---------------
valid_encounter_timestamps    | 1
no_future_encounter_dates     | 0
```

---

## Debugging Quarantined Records

### View Quarantined Records

```sql
select
    encounter_id,
    encounter_start_at,
    encounter_end_at,
    is_dq_valid,
    valid_encounter_timestamps,
    no_future_encounter_dates,
    failed_dq_tests
from {{ ref('int_dq_quarantine__encounters') }}
order by encounter_start_at desc
```

### Identify Root Cause

**Example**: Why is encounter X quarantined?

```sql
select
    encounter_id,
    encounter_start_at,
    encounter_end_at,

    -- See which specific rules failed
    valid_encounter_timestamps,      -- false
    no_future_encounter_dates,       -- true
    end_after_1900,                  -- true
    start_after_1900,                -- true

    -- See all failed rules in one column
    failed_dq_tests                  -- ['valid_encounter_timestamps']
from {{ ref('int_dq_quarantine__encounters') }}
where encounter_id = '8cd80b4d-69b8-4b6...'
```

**Output interpretation**:

- `valid_encounter_timestamps = false` → End time before start time
- `failed_dq_tests = ['valid_encounter_timestamps']` → Only this rule failed

### Debug Mode: See All Records

Temporarily disable quarantine filter to see both valid and invalid records:

```sql
-- In your fact model
with encounters_debug as (
    select
        *,
        is_dq_valid  -- Include this column for debugging
    from {{ ref('stg_synthea__encounters') }}
    {{ quarantine_filter(enabled=false) }}  -- Disable filter
)

select * from encounters_debug
order by is_dq_valid, encounter_start_at  -- Invalid records first
```

### Verify No Leakage

Ensure quarantined records don't appear in downstream marts:

```sql
-- Should return 0 rows
select count(*) as leaked_count
from {{ ref('fct_encounters') }} f
join {{ ref('int_dq_quarantine__encounters') }} q
    on f.encounter_id = q.encounter_id
```

---

## Validation Rule Patterns

### Timestamp/Date Sequences

**Pattern**: End date/time must be >= start date/time

```sql
'valid_timestamps': 'end_at >= start_at'
'valid_date_sequence': 'discharge_date >= admission_date'
```

**Null handling**:

```sql
-- If end can be null (ongoing)
'valid_timestamps': 'end_at is null or end_at >= start_at'
```

### Future Date Prevention

**Pattern**: Dates must not be in the future

```sql
'no_future_dates': 'event_date <= current_date'
'no_future_timestamps': 'event_at <= current_timestamp'
```

**Grace period** (allow small clock skew):

```sql
'no_future_dates': 'event_date <= current_date + interval \'1 day\''
```

### Historical Plausibility

**Pattern**: Dates must be after a certain historical point

```sql
'date_after_1900': 'event_date >= date \'1900-01-01\''
'timestamp_after_1900': 'event_at >= timestamp \'1900-01-01\''
```

**Business rule example**:

```sql
-- Organization founded in 2010
'date_after_org_founded': 'event_date >= date \'2010-06-15\''
```

### Range Constraints

**Pattern**: Numeric values within expected range

```sql
'amount_non_negative': 'amount >= 0'
'percentage_0_to_100': 'percentage >= 0 and percentage <= 100'
'age_reasonable': 'age >= 0 and age <= 150'
```

### Required Field Combinations

**Pattern**: At least one of multiple fields must be present

```sql
'has_identifier': 'code is not null or description is not null'
'has_contact': 'email is not null or phone is not null'
```

### Foreign Key Existence

**Pattern**: Referenced entity must exist

```sql
-- In staging CTE, use LEFT JOIN
'patient_exists': 'patient_id in (select patient_id from {{ ref(\"dim_patients\") }})'
```

**Note**: This is expensive. Consider using relationship tests instead:

```yaml
tests:
  - relationships:
      to: ref('dim_patients')
      field: patient_id
```

### String Pattern Validation

**Pattern**: String matches expected format

```sql
'valid_zip_code': 'zip_code ~ \'^[0-9]{5}(-[0-9]{4})?$\''  -- DuckDB regex
'valid_email': 'email like \'%@%.%\''
```

### Conditional Validation

**Pattern**: Rule applies only when condition met

```sql
-- If status is 'completed', end_date must be present
'completed_has_end_date': 'status != \'completed\' or end_date is not null'

-- If amount > 0, payment method must be present
'paid_has_method': 'amount <= 0 or payment_method is not null'
```

---

## Testing

### Quarantine Table Tests

Add these standard tests to every quarantine table:

```yaml
models:
  - name: int_dq_quarantine__my_entity
    columns:
      - name: entity_id
        tests:
          - unique
          - not_null

      - name: is_dq_valid
        tests:
          - accepted_values:
              values: [false]  # Only invalid records
          - not_null

      - name: failed_dq_tests
        tests:
          - not_null
```

### Staging Model Tests

Add test to ensure `is_dq_valid` is always populated:

```yaml
models:
  - name: stg_synthea__my_entity
    columns:
      - name: is_dq_valid
        tests:
          - not_null
          - accepted_values:
              values: [true, false]
```

### No-Leakage Tests

Create custom tests to ensure quarantined records don't reach facts:

```sql
-- tests/data_quality/assert_no_quarantined_in_facts.sql

with quarantined_encounters as (
    select encounter_id
    from {{ ref('int_dq_quarantine__encounters') }}
),

fact_encounters as (
    select encounter_id
    from {{ ref('fct_encounters') }}
)

select f.encounter_id
from fact_encounters f
join quarantined_encounters q on f.encounter_id = q.encounter_id
```

This test should return **0 rows** (any rows = test fails).

### Quarantine Rate Test

Alert if quarantine rate exceeds threshold:

```sql
-- tests/data_quality/assert_quarantine_rate_below_threshold.sql

with dq_summary as (
    select
        entity_type,
        quarantine_rate_pct
    from {{ ref('mart_dq_summary') }}
    where quarantine_rate_pct > 1.0  -- 1% threshold
)

select * from dq_summary
```

---

## Troubleshooting

### Issue: Macro not found

**Error**:

```text
Compilation Error in model stg_synthea__encounters
  'add_dq_flags' is undefined
```

**Solution**:

```bash
# Verify macro exists
ls macros/data_quality/add_dq_flags.sql

# Reparse project
dbt parse

# Clean and rebuild
dbt clean && dbt deps && dbt parse
```

### Issue: Array syntax error

**Error**:

```text
Binder Error: list_value is not a valid function
```

**Cause**: Using Postgres/Snowflake adapter instead of DuckDB.

**Solution**: This implementation is DuckDB-specific. For other databases, modify `_collect_failed_tests()` macro:

```sql
-- Snowflake
ARRAY_CONSTRUCT(case when not valid then 'rule' else null end, ...)

-- BigQuery
[case when not valid then 'rule' else null end, ...]

-- Postgres
ARRAY[case when not valid then 'rule' else null end, ...]
```

### Issue: WHERE clause syntax error

**Error**:

```text
WHERE clause cannot contain aggregates
```

**Cause**: Using `quarantine_filter()` with aggregation context.

**Solution**: Apply filter before aggregation:

```sql
-- WRONG
select
    encounter_id,
    count(*) as event_count
from {{ ref('stg_synthea__encounters') }}
group by encounter_id
{{ quarantine_filter() }}  -- Too late!

-- CORRECT
with valid_encounters as (
    select * from {{ ref('stg_synthea__encounters') }}
    {{ quarantine_filter() }}
)

select
    encounter_id,
    count(*) as event_count
from valid_encounters
group by encounter_id
```

### Issue: Quarantine table empty

**Symptoms**: `int_dq_quarantine__my_entity` has 0 rows but expect violations.

**Debug steps**:

1. Check staging model has DQ flags:

```sql
select
    is_dq_valid,
    count(*)
from {{ ref('stg_synthea__my_entity') }}
group by is_dq_valid
```

2. Verify validation logic:

```sql
-- Show invalid records and why
select
    entity_id,
    valid_timestamps,
    no_future_dates,
    failed_dq_tests
from {{ ref('stg_synthea__my_entity') }}
where is_dq_valid = false
limit 10
```

3. Check quarantine model compiles:

```bash
dbt compile --select int_dq_quarantine__my_entity
cat target/compiled/.../int_dq_quarantine__my_entity.sql
```

### Issue: Fact table has quarantined records

**Symptoms**: Leakage test fails (quarantined records in fact table).

**Debug steps**:

1. Find which fact tables lack filter:

```bash
grep -r "ref('stg_synthea__encounters')" models/marts/
grep -r "quarantine_filter" models/marts/
```

2. Check for indirect references (via intermediate models):

```bash
# Find all models that reference the staging model
dbt ls --select +stg_synthea__encounters
```

3. Add missing filters to all downstream models.

### Issue: Build time too slow

**Symptoms**: `dbt build` takes >30% longer after adding quarantine.

**Optimization**:

1. Materialize staging as tables (not views):

```sql
{{ config(materialized='table') }}
```

2. Create index on `is_dq_valid`:

```sql
-- In post-hook
{{ config(
    post_hook=[
        "create index if not exists idx_is_dq_valid on {{ this }} (is_dq_valid)"
    ]
) }}
```

3. Sample quarantine for large datasets:

```sql
-- Instead of full quarantine
select *
from {{ ref('stg_synthea__my_entity') }}
where is_dq_valid = false
    and random() < 0.1  -- 10% sample
```

---

## Additional Resources

- **Macro Documentation**: `macros/data_quality/README.md`
- **ADR**: `docs/decisions/ADR-004-data-quality-quarantine.md`
- **Implementation Summary**: `temp/v0.8_PHASE5_IMPLEMENTATION_SUMMARY.md`
- **dbt Testing Standards**: `docs/reference/DBT_TESTING_STANDARDS.md`

---

**Last Updated**: 2026-02-01
**Version**: v0.8.0
