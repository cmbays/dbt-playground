# Coding Style Rules

Standards for SQL, YAML, and Python in this dbt project.

## SQL Standards

### Structure

- Use CTEs (Common Table Expressions) for readability
- One CTE per logical step
- Final SELECT at the end of the model
- Consistent 4-space indentation

### Naming Conventions

- **Models**: `stg_`, `int_`, `fct_`, `dim_` prefixes
- **Columns**: snake_case (e.g., `patient_id`, `encounter_date`)
- **CTEs**: Descriptive names (e.g., `source`, `renamed`, `filtered`)
- **Aliases**: Full table aliases, not single letters

```sql
-- Good
select
    patients.patient_id,
    encounters.encounter_date
from patients
left join encounters
    on patients.patient_id = encounters.patient_id

-- Avoid
select
    p.patient_id,
    e.encounter_date
from patients p
left join encounters e
    on p.patient_id = e.patient_id
```

### CTE Pattern

```sql
with source as (
    select * from {{ source('synthea_raw', 'patients') }}
),

renamed as (
    select
        id as patient_id,
        first as first_name,
        last as last_name,
        birthdate as birth_date
    from source
),

final as (
    select
        patient_id,
        first_name,
        last_name,
        birth_date,
        current_timestamp as _loaded_at
    from renamed
)

select * from final
```

### Formatting

- Keywords in lowercase (`select`, `from`, `where`)
- One column per line in SELECT
- Commas at the beginning of lines (leading commas)
- Align column definitions

```sql
select
    patient_id
    , first_name
    , last_name
    , birth_date
    , current_timestamp as _loaded_at
from source
where birth_date is not null
```

### Comments

```sql
-- Model: stg_synthea__patients
-- Description: Staging model for patient demographics
-- Source: synthea_raw.patients

{#
    Multi-line Jinja comments for
    complex explanations
#}
```

## YAML Standards

### Model Documentation

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

### Source Definitions

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

### Formatting

- 2-space indentation
- Use quotes for strings with special characters
- List items aligned
- One blank line between major sections

## dbt Best Practices

### Model Layers

| Layer | Prefix | Purpose |
|-------|--------|---------|
| Staging | `stg_` | 1:1 with source, renamed/retyped |
| Intermediate | `int_` | Business logic, joins |
| Facts | `fct_` | Measures, events |
| Dimensions | `dim_` | Descriptive attributes |

### Ref and Source Usage

```sql
-- Always use ref() for model dependencies
select * from {{ ref('stg_synthea__patients') }}

-- Always use source() for raw data
select * from {{ source('synthea_raw', 'patients') }}
```

### Jinja Macros

- Use for repeated logic
- Document parameters
- Keep macros focused

```sql
{% macro calculate_age(birth_date, reference_date) %}
    date_diff('year', {{ birth_date }}, {{ reference_date }})
{% endmacro %}
```

## Python Standards

### Organization

- Scripts in `scripts/` directory
- Use virtual environment (`.venv/`)
- Follow PEP 8 style guide

### Naming

- snake_case for functions and variables
- PascalCase for classes
- UPPER_SNAKE_CASE for constants

```python
# Constants
DEFAULT_TARGET = 'dev'
MAX_THREADS = 4

# Functions
def load_synthea_data(file_path: str) -> None:
    """Load Synthea CSV data into DuckDB."""
    pass

# Classes
class DataLoader:
    """Handles data loading operations."""
    pass
```

### Type Hints

```python
def get_model_path(model_name: str, layer: str = 'staging') -> str:
    """
    Get the file path for a dbt model.

    Args:
        model_name: Name of the model
        layer: Model layer (staging, intermediate, marts)

    Returns:
        Full path to the model file
    """
    return f"models/{layer}/{model_name}.sql"
```

## File Organization

### Naming

- Lowercase with underscores for SQL: `stg_synthea__patients.sql`
- Lowercase with hyphens for Python: `load-data.py`
- Descriptive names that indicate purpose

### Directory Structure

```
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

## Code Quality

### Avoid

- SELECT * in final models (explicit columns only)
- Hardcoded values (use variables or seeds)
- Overly complex CTEs (break into intermediate models)
- Duplicated logic (extract to macros)

### Prefer

- Explicit column selection
- Descriptive aliases
- Documentation for every model
- Tests for critical columns
- Incremental models for large datasets

## Testing Standards

### Required Tests

- `unique` and `not_null` on primary keys
- `accepted_values` on categorical columns
- `relationships` for foreign keys

```yaml
columns:
  - name: patient_id
    data_tests:
      - unique
      - not_null
  - name: gender
    data_tests:
      - accepted_values:
          values: ['M', 'F', 'O']
  - name: organization_id
    data_tests:
      - relationships:
          to: ref('dim_organizations')
          field: organization_id
```
