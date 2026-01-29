# dbt Testing Standards Reference

Detailed testing patterns for this dbt project. dbt agents should read this file before writing tests.

## Schema Tests (Generic)

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
```

## Singular Tests

```sql
-- tests/assert_valid_encounter_dates.sql
select
    encounter_id,
    start_timestamp,
    stop_timestamp
from {{ ref('stg_synthea__encounters') }}
where stop_timestamp < start_timestamp
```

## Relationship Tests

```yaml
columns:
  - name: patient_id
    data_tests:
      - relationships:
          to: ref('dim_patients')
          field: patient_id
```

## Test Documentation Template

```markdown
# Test Results: v[X.Y] - [Feature]

## Summary
[Pass/Fail] - [X/Y tests passing]

## dbt Test Results
| Model | Tests | Pass | Fail |
|-------|-------|------|------|
| stg_synthea__patients | 5 | 5 | 0 |

## Failed Tests
| Test | Model | Error | Resolution |
|------|-------|-------|------------|
| not_null | fct_encounters.provider_id | 3 nulls | Added where clause |
```

## TDD Workflow

1. **RED**: Write failing test in YAML
2. **GREEN**: Implement model to pass test
3. **REFACTOR**: Optimize, ensure tests pass

## Data Quality Edge Cases

### Primary Keys

- Uniqueness across partitions
- No nulls
- Consistent format (UUID vs integer)

### Foreign Keys

- Referential integrity
- No orphaned records

### Dates

- Valid date ranges
- No future dates where inappropriate
- End date >= Start date

### Numeric Values

- Non-negative where required
- Within reasonable bounds

## dbt_expectations Examples

```yaml
columns:
  - name: encounter_date
    data_tests:
      - dbt_expectations.expect_column_values_to_be_between:
          min_value: "'2000-01-01'"
          max_value: "current_date"
```

## Commands

```bash
# Run tests for model and downstream
dbt test --select model_name+

# Full test suite
dbt test

# Build and test
dbt build
```

## Pre-Deploy Checklist

- [ ] All dbt tests pass
- [ ] Models compile
- [ ] No warnings on critical models
- [ ] Row counts reasonable
