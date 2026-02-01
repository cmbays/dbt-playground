# Data Quality Macros

Reusable macros for implementing data quality quarantine patterns in dbt.

## Overview

This macro library provides a systematic approach to handling data quality violations:

1. **Detect**: Flag invalid records at the staging layer
2. **Isolate**: Quarantine bad records in dedicated tables
3. **Filter**: Prevent quarantined records from flowing to downstream marts

## Macros

### `add_dq_flags(source_cte, validations)`

Adds data quality validation columns to a staging model.

**Parameters:**

- `source_cte` (string): Name of the CTE containing cleaned data
- `validations` (dict): Map of validation_name to SQL condition

**Returns:**

SELECT statement with original columns plus:

- Individual boolean flags for each validation (e.g., `valid_timestamps`)
- `is_dq_valid` (boolean): True if ALL validations pass
- `failed_dq_tests` (varchar[]): Array of failed validation names

**Example:**

```sql
with renamed as (
    select
        encounter_id,
        encounter_start_at,
        encounter_end_at
    from source
),

with_dq_flags as (
    {{ add_dq_flags(
        source_cte='renamed',
        validations={
            'valid_encounter_timestamps': 'encounter_end_at >= encounter_start_at',
            'no_future_encounter_dates': 'encounter_start_at <= current_timestamp',
            'start_after_1900': 'encounter_start_at >= timestamp \'1900-01-01\''
        }
    ) }}
)

select * from with_dq_flags
```

**Generated columns:**

- `valid_encounter_timestamps` (boolean)
- `no_future_encounter_dates` (boolean)
- `start_after_1900` (boolean)
- `is_dq_valid` (boolean)
- `failed_dq_tests` (varchar[])

---

### `quarantine_filter(enabled=true, field_name='is_dq_valid')`

Generates a WHERE clause to filter out quarantined records.

**Parameters:**

- `enabled` (bool): Whether to apply filter (default: true)
- `field_name` (string): Name of validity flag (default: 'is_dq_valid')

**Returns:**

SQL WHERE clause: `where is_dq_valid = true`

**Example:**

```sql
with encounters as (
    select * from {{ ref('stg_synthea__encounters') }}
    {{ quarantine_filter() }}
)
```

This ensures only valid records flow into fact tables.

---

### `generate_quarantine_model(source_model, description='')`

Generates a complete quarantine table that isolates invalid records.

**Parameters:**

- `source_model` (string): Name of the staging model (e.g., 'stg_synthea__encounters')
- `description` (string): Optional description comment

**Returns:**

Complete SQL SELECT for quarantine model

**Example:**

```sql
-- models/intermediate/quarantine/int_dq_quarantine__encounters.sql
{{ config(
    materialized='table',
    tags=['intermediate', 'quarantine', 'data_quality']
) }}

{{ generate_quarantine_model(
    source_model='stg_synthea__encounters',
    description='Encounters quarantined due to data quality violations'
) }}
```

This creates a table containing only records where `is_dq_valid = false`.

---

## Usage Pattern

### Step 1: Add DQ Flags to Staging Model

```sql
-- models/staging/synthea/stg_synthea__encounters.sql

with source as (
    select * from {{ source('synthea_raw', 'encounters') }}
),

renamed as (
    select
        Id as encounter_id,
        cast(START as timestamp) as encounter_start_at,
        cast(STOP as timestamp) as encounter_end_at
    from source
),

with_dq_flags as (
    {{ add_dq_flags(
        source_cte='renamed',
        validations={
            'valid_encounter_timestamps': 'encounter_end_at >= encounter_start_at',
            'no_future_encounter_dates': 'encounter_start_at <= current_timestamp'
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

### Step 2: Create Quarantine Table

```sql
-- models/intermediate/quarantine/int_dq_quarantine__encounters.sql

{{ config(
    materialized='table',
    tags=['intermediate', 'quarantine', 'data_quality']
) }}

{{ generate_quarantine_model(
    source_model='stg_synthea__encounters',
    description='Encounters quarantined due to data quality violations'
) }}
```

### Step 3: Filter in Downstream Models

```sql
-- models/marts/core/fct_encounters.sql

with encounters as (
    select * from {{ ref('stg_synthea__encounters') }}
    {{ quarantine_filter() }}
)

select * from encounters
```

### Step 4: Document in Schema YAML

```yaml
# models/staging/synthea/_synthea__models.yml

models:
  - name: stg_synthea__encounters
    columns:
      - name: valid_encounter_timestamps
        description: "Flag: encounter_end_at >= encounter_start_at"
      - name: no_future_encounter_dates
        description: "Flag: encounter_start_at <= current_timestamp"
      - name: is_dq_valid
        description: "True if all data quality validations pass"
        tests:
          - not_null
      - name: failed_dq_tests
        description: "Array of failed validation names (empty if valid)"
```

---

## Testing Quarantine Tables

Verify quarantine isolation:

```yaml
# models/intermediate/quarantine/_quarantine__models.yml

models:
  - name: int_dq_quarantine__encounters
    description: "Encounters failing data quality validations"
    tests:
      - dbt_utils.expression_is_true:
          expression: "count(*) >= 0"  # May be empty
    columns:
      - name: encounter_id
        tests:
          - unique
          - not_null
      - name: is_dq_valid
        tests:
          - accepted_values:
              values: [false]  # Only invalid records
      - name: failed_dq_tests
        tests:
          - not_null
```

---

## Monitoring Data Quality

Create a summary analytics table:

```sql
-- models/marts/analytics/mart_dq_summary.sql

with encounter_metrics as (
    select
        'encounters' as entity_type,
        count(*) filter (where is_dq_valid = false) as quarantined_count,
        count(*) as total_count,
        round(100.0 * count(*) filter (where is_dq_valid = false) / count(*), 2) as quarantine_rate_pct
    from {{ ref('stg_synthea__encounters') }}
)

select * from encounter_metrics
```

---

## DuckDB-Specific Features

These macros use DuckDB-specific syntax:

- `list_value()` for array construction
- `filter (where ...)` for conditional aggregation

For portability to other databases, these would need to be adapted.

---

## Best Practices

1. **Test at Boundaries**: Add DQ flags at staging (earliest detection)
2. **Single Source of Truth**: Document all validations in one place
3. **Preserve Evidence**: Keep quarantine tables for investigation
4. **Monitor Trends**: Track quarantine rates over time
5. **Alert on Thresholds**: Flag when quarantine rate exceeds 1%

---

## Troubleshooting

**Issue**: Macro not found

```bash
dbt parse  # Verify macro syntax
dbt clean && dbt deps  # Rebuild dependencies
```

**Issue**: Array syntax error

- Ensure using DuckDB adapter (not Postgres/Snowflake)
- Check `list_value()` function availability

**Issue**: Performance degradation

- Materialize staging as tables (not views) if validations are complex
- Index `is_dq_valid` column in warehouse if supported

---

## Version History

- **v0.8 (Phase 5)**: Initial implementation for encounters and medications quarantine
