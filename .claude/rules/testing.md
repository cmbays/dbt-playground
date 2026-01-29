# Testing Rules

Standards for testing, verification, and quality assurance in dbt projects.

## Testing Philosophy

- Test data quality at every layer
- Prefer generic tests for common patterns; singular tests for complex logic
- Document test failures and their resolutions
- Run tests after every model change

## Test Categories

| Category | Purpose | When to Use |
|----------|---------|-------------|
| **Schema Tests** | Validate column properties | Every model |
| **Data Tests** | Validate business rules | Critical models |
| **Singular Tests** | Complex custom validation | Edge cases |
| **Source Freshness** | Monitor data timeliness | Production pipelines |
| **Unit Tests** | Test macros and logic | Reusable code |

## dbt Test Types

### Schema Tests (Generic)

```yaml
version: 2

models:
  - name: stg_synthea__patients
    columns:
      - name: patient_id
        data_tests:
          - unique
          - not_null
      - name: gender
        data_tests:
          - accepted_values:
              values: ['M', 'F', 'O']
      - name: birth_date
        data_tests:
          - not_null
```

### Data Tests (Custom)

```yaml
models:
  - name: fct_encounters
    data_tests:
      - dbt_utils.expression_is_true:
          expression: "total_claim_cost >= 0"
      - dbt_utils.recency:
          datepart: day
          field: encounter_date
          interval: 365
```

### Singular Tests

```sql
-- tests/assert_valid_encounter_dates.sql
-- Ensure encounter end dates are after start dates

select
    encounter_id,
    start_timestamp,
    stop_timestamp
from {{ ref('stg_synthea__encounters') }}
where stop_timestamp < start_timestamp
```

### Relationship Tests

```yaml
columns:
  - name: patient_id
    data_tests:
      - relationships:
          to: ref('dim_patients')
          field: patient_id
```

## Test Documentation

### Location

- Schema tests: `models/<layer>/<source>/_<source>__models.yml`
- Singular tests: `tests/`
- Test results: `temp/v[X.Y]_TESTING.md`

### Template

```markdown
# Test Results: v[X.Y] - [Feature]

## Date
YYYY-MM-DD

## Summary
[Pass/Fail] - [X/Y tests passing]

## dbt Test Results

| Model | Tests | Pass | Fail | Warn |
|-------|-------|------|------|------|
| stg_synthea__patients | 5 | 5 | 0 | 0 |
| fct_encounters | 8 | 7 | 1 | 0 |

## Failed Tests
| Test | Model | Error | Resolution |
|------|-------|-------|------------|
| not_null | fct_encounters.provider_id | 3 nulls found | Added where clause |

## Warnings
| Test | Model | Issue | Action |
|------|-------|-------|--------|
| freshness | source.patients | 2 days stale | Expected during dev |

## Data Quality Checks
- [ ] Primary keys unique
- [ ] Foreign keys valid
- [ ] No orphaned records
- [ ] Date ranges reasonable
- [ ] Numeric values within bounds

## Sign-Off
Ready for deployment: Yes/No
Tester: [name/date]
```

## TDD Workflow for dbt

### Red-Green-Refactor

1. **RED**: Write failing test in YAML or singular test file
2. **GREEN**: Implement model to pass test
3. **REFACTOR**: Optimize model, ensure tests still pass

### Test-First Example

```yaml
# 1. Define expected behavior first
models:
  - name: stg_synthea__patients
    columns:
      - name: patient_id
        data_tests:
          - unique
          - not_null
      - name: birth_date
        data_tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: "birth_date <= current_date"
```

```sql
-- 2. Implement model to pass tests
with source as (
    select * from {{ source('synthea_raw', 'patients') }}
),

renamed as (
    select
        id as patient_id,
        birthdate as birth_date
    from source
    where birthdate is not null
      and birthdate <= current_date
)

select * from renamed
```

## Data Quality Edge Cases

### Primary Keys

- Uniqueness across partitions
- No nulls
- Consistent format (UUID vs integer)

### Foreign Keys

- Referential integrity
- No orphaned records
- Graceful null handling

### Dates and Timestamps

- Valid date ranges
- No future dates where inappropriate
- Timezone consistency
- End date >= Start date

### Numeric Values

- Non-negative where required
- Within reasonable bounds
- Precision/scale appropriate

### Categorical Values

- Only expected values
- Consistent casing
- No leading/trailing whitespace

## Bug Documentation

### When Found

```markdown
## Bug: [Short Description]

### Environment
- dbt version: X.Y.Z
- DuckDB version: X.Y.Z
- Date: YYYY-MM-DD

### Test That Failed
```sql
-- The failing test
select * from {{ ref('model') }}
where condition_violated
```

### Root Cause

[What caused the data quality issue]

### Resolution

[How it was fixed in the model]

### Prevention

[Tests added to prevent recurrence]

```

## Performance Testing

### Metrics to Check

- Model build time
- Test execution time
- Row counts per model
- Data freshness

### dbt Commands

```bash
# Time a specific model
dbt run --select model_name --profile-start-time

# Run with timing info
dbt run --select staging --threads 4

# Check row counts
dbt run-operation log_row_counts --args '{models: ["stg_synthea__patients"]}'
```

## Verification Before Deployment

### Pre-Deploy Checklist

- [ ] All dbt tests pass (`dbt test`)
- [ ] Models compile (`dbt compile`)
- [ ] Documentation generated (`dbt docs generate`)
- [ ] No warnings on critical models
- [ ] Source freshness acceptable
- [ ] Row counts reasonable
- [ ] Version documented in CHANGELOG

## Continuous Testing

### After Every Model Change

```bash
# Run tests for changed model and downstream
dbt test --select model_name+
```

### Before Every Commit

```bash
# Full test suite
dbt test

# Build and test in one command
dbt build
```

### Before Every Release

```bash
# Full build with all tests
dbt build --full-refresh

# Generate documentation
dbt docs generate
dbt docs serve
```

## dbt_expectations Examples

```yaml
# Advanced data quality tests
columns:
  - name: encounter_date
    data_tests:
      - dbt_expectations.expect_column_values_to_be_of_type:
          column_type: date
      - dbt_expectations.expect_column_values_to_be_between:
          min_value: "'2000-01-01'"
          max_value: "current_date"

  - name: total_claim_cost
    data_tests:
      - dbt_expectations.expect_column_values_to_be_between:
          min_value: 0
          max_value: 1000000
          strictly: false
```
