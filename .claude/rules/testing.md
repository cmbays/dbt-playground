# Testing Rules

Quick reference for dbt testing. For detailed examples, see `docs/reference/DBT_TESTING_STANDARDS.md`.

## Testing Philosophy

- Test data quality at every layer
- Generic tests for common patterns
- Singular tests for complex business logic
- Run tests after every model change

## Required Tests

Every model must have:

- `unique` + `not_null` on primary key
- `accepted_values` on categorical columns
- `relationships` for foreign keys

## Test Categories

| Category | Purpose |
|----------|---------|
| Schema Tests | Column properties (unique, not_null) |
| Data Tests | Business rules |
| Singular Tests | Complex validation |
| Source Freshness | Data timeliness |

## TDD Workflow

1. **RED**: Write failing test first
2. **GREEN**: Implement model to pass
3. **REFACTOR**: Optimize, tests still pass

## Commands

```bash
dbt test --select model_name+  # Model and downstream
dbt test                        # Full suite
dbt build                       # Build and test
```

## Pre-Deploy Checklist

- [ ] All dbt tests pass
- [ ] Models compile
- [ ] Documentation generated
- [ ] Row counts reasonable
