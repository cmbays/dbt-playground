# Healthcare Analytics dbt Project

A dbt project for healthcare data transformation using Synthea synthetic patient data.

## Quick Start

```bash
# Install dependencies
uv sync

# Load source data
uv run dbt run-operation load_synthea_sources

# Build all models and run tests
uv run dbt build

# Generate and serve documentation
uv run dbt docs generate
uv run dbt docs serve
```

## Documentation

The dbt documentation site provides:

- **Model lineage**: Visual DAG of all data transformations
- **Column descriptions**: Documentation for every column
- **Test coverage**: View tests defined on each model
- **Source freshness**: Track data loading status

### Serving Docs Locally

```bash
# Generate docs (creates target/catalog.json and target/index.html)
uv run dbt docs generate

# Serve docs on http://localhost:8080
uv run dbt docs serve

# Serve on a different port
uv run dbt docs serve --port 8000
```

### Docs Structure

| Layer | Models | Description |
|-------|--------|-------------|
| Staging | 9 | 1:1 source transformations (stg_synthea__*) |
| Intermediate | 2 | Business logic enrichment (int_*) |
| Marts - Dims | 5 | Dimension tables (dim_*) |
| Marts - Facts | 4 | Fact tables (fct_*) |
| Marts - Analytics | 4 | Specialized analytics (fct_**summary, fct**_metrics) |
| Views | 2 | Dashboard-ready views (v_*) |
| Snapshots | 1 | SCD Type 2 (snp_patients) |

## Project Structure

```text
dbt_project/
├── models/
│   ├── staging/synthea/     # Source transformations
│   ├── intermediate/        # Business logic
│   └── marts/               # Analytics-ready models
├── macros/                  # Reusable SQL functions
├── seeds/                   # Static reference data
├── snapshots/               # SCD Type 2 tracking
├── tests/                   # Singular tests
└── target/                  # Generated artifacts
```

## Commands

| Command | Purpose |
|---------|---------|
| `dbt run` | Build all models |
| `dbt test` | Run all tests |
| `dbt build` | Run + test in DAG order |
| `dbt docs generate` | Generate documentation |
| `dbt docs serve` | Serve docs at localhost:8080 |

## Unit tests (cute-dbt format coverage)

Three unit_tests on `dim_payers` + `mart_dq_summary` exercise dbt's
three fixture formats (`dict`, `csv`, `sql`) for the cute-dbt
unit-test explorer ([breezy-bays-labs/cute-dbt#39 + #66](https://github.com/breezy-bays-labs/cute-dbt/issues/66)).

**Format coverage:**

| Test | Given format | Expect format | Demonstrates |
|---|---|---|---|
| `test_dim_payers_injects_unknown_sentinel` | dict | dict | Compact key-value mock for many columns |
| `test_mart_dq_summary_combines_encounter_and_medication_metrics` | csv | csv | Tabular form for repeated boolean columns |
| `test_mart_dq_summary_zero_quarantined_when_all_valid` | sql | dict | Inline SELECT mock when fine-grained casts matter |

**Execution prerequisite — dict and csv given formats**: dbt's
unit-test framework introspects the upstream relation's schema to
NULL-fill columns not provided in the mock. The introspection requires
the upstream model to **exist** in the warehouse. With the default
`:memory:` DuckDB profile, the upstream relations vanish between
`run-operation` and `test` invocations, so `dbt test --select
test_type:unit` fails. Two paths:

1. **Persistent DuckDB target** (recommended for local dev). Add to
   `~/.dbt/profiles.yml`:

   ```yaml
   healthcare_analytics:
     outputs:
       unit_test:
         type: duckdb
         path: 'target/playground-unit-test.duckdb'
         threads: 4
   ```

   Then:

   ```bash
   uv run dbt run-operation load_synthea_sources --target unit_test
   uv run dbt build --empty --select "+mart_dq_summary +dim_payers" --target unit_test
   uv run dbt test --select "test_type:unit" --target unit_test
   ```

2. **Inline mock with `sql` format** for the `given` block (no
   introspection required, passes standalone against `:memory:`). The
   `test_mart_dq_summary_zero_quarantined_when_all_valid` test
   demonstrates this pattern.

The persistent-target approach is preferred when authoring new
unit_tests because dict and csv given are more readable for
multi-column mocks.

## Resources

- [dbt Documentation](https://docs.getdbt.com/)
- [Synthea Patient Generator](https://synthetichealth.github.io/synthea/)
- [Project CLAUDE.md](../CLAUDE.md) - Development guidelines
