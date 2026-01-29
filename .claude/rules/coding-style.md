# Coding Style Rules

Quick reference for SQL, YAML, and Python standards. For detailed examples, see `docs/reference/DBT_CODING_STANDARDS.md`.

## SQL Essentials

- Use CTEs (not subqueries), one per logical step
- Keywords lowercase (`select`, `from`, `where`)
- Leading commas, one column per line
- 4-space indentation
- Full table aliases (not single letters)

## Model Naming

| Layer | Prefix | Purpose |
|-------|--------|---------|
| Staging | `stg_` | 1:1 with source |
| Intermediate | `int_` | Business logic |
| Facts | `fct_` | Events, measures |
| Dimensions | `dim_` | Attributes |

## Required Patterns

- `ref()` for model dependencies
- `source()` for raw data
- Document every model and column
- No hardcoded values
- Explicit column selection (no `SELECT *` in final)

## File Naming

- SQL: `stg_synthea__patients.sql` (underscores)
- Python: `load-data.py` (hyphens)
- YAML: 2-space indentation

## YAML Formatting

- 2-space indentation
- Quotes for special characters
- One blank line between sections
