# dbt Coding Standards Reference

Detailed SQL, YAML, and Python patterns for this dbt project. dbt agents should read this file before implementing models.

## SQL CTE Pattern

```sql
with source as (
    select * from {{ source('synthea_raw', 'patients') }}
),

renamed as (
    select
        id as patient_id
        , first as first_name
        , last as last_name
        , birthdate as birth_date
    from source
),

final as (
    select
        patient_id
        , first_name
        , last_name
        , birth_date
        , current_timestamp as _loaded_at
    from renamed
)

select * from final
```

## SQL Formatting

- Keywords lowercase (`select`, `from`, `where`)
- One column per line in SELECT
- Leading commas (commas at beginning of lines)
- 4-space indentation
- Full table aliases, not single letters

```sql
-- Good: full aliases
select
    patients.patient_id,
    encounters.encounter_date
from patients
left join encounters
    on patients.patient_id = encounters.patient_id

-- Avoid: single-letter aliases
select p.patient_id from patients p
```

## YAML Model Documentation

```yaml
version: 2

models:
  - name: stg_synthea__patients
    description: Staging model for patient demographics
    columns:
      - name: patient_id
        description: Unique patient identifier (UUID)
        data_tests:
          - unique
          - not_null
      - name: birth_date
        description: Patient date of birth
```

## YAML Source Definitions

```yaml
sources:
  - name: synthea_raw
    description: Raw Synthea synthetic healthcare data
    schema: main
    tables:
      - name: patients
        description: Patient demographics
        columns:
          - name: Id
            description: Unique patient identifier
```

## Model Layers

| Layer | Prefix | Purpose |
|-------|--------|---------|
| Staging | `stg_` | 1:1 with source, renamed/retyped |
| Intermediate | `int_` | Business logic, joins |
| Facts | `fct_` | Measures, events |
| Dimensions | `dim_` | Descriptive attributes |

## Jinja Macros

```sql
{% macro calculate_age(birth_date, reference_date) %}
    date_diff('year', {{ birth_date }}, {{ reference_date }})
{% endmacro %}
```

## Directory Structure

```text
dbt_project/
├── models/
│   ├── staging/
│   │   └── synthea/
│   │       ├── _synthea__sources.yml
│   │       ├── _synthea__models.yml
│   │       └── stg_synthea__patients.sql
│   ├── intermediate/
│   │   └── healthcare/
│   │       └── int_encounters__enriched.sql
│   └── marts/
│       └── core/
│           ├── _core__models.yml
│           ├── dim_patients.sql
│           └── fct_encounters.sql
├── macros/
│   └── healthcare_utils.sql
├── tests/
│   └── assert_valid_dates.sql
└── seeds/
    └── ref_codes.csv
```

## Python Standards

- snake_case for functions and variables
- PascalCase for classes
- UPPER_SNAKE_CASE for constants
- Type hints on all functions
- Scripts in `scripts/` directory

## Code Quality

### Avoid

- SELECT * in final models
- Hardcoded values (use variables or seeds)
- Overly complex CTEs (break into intermediate models)
- Duplicated logic (extract to macros)

### Prefer

- Explicit column selection
- Descriptive aliases
- Documentation for every model
- Tests for critical columns
