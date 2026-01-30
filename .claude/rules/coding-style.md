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

## Python / uv

### Package Management

- Use `uv` exclusively (never `pip`)
- Add packages: `uv add <package>` or `uv add --dev <package>`
- Install dependencies: `uv sync`
- Run commands: `uv run <command>`

### Running Scripts

```bash
# Run Python scripts
uv run python scripts/my_script.py

# Run dbt commands
uv run dbt build

# Run one-off tools without installing
uvx ruff check .
```

### Script Headers (PEP 723)

For standalone scripts, use inline metadata:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests", "rich"]
# ///
```

See `docs/reference/UV_MIGRATION.md` for complete guide.
