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

## Resources

- [dbt Documentation](https://docs.getdbt.com/)
- [Synthea Patient Generator](https://synthetichealth.github.io/synthea/)
- [Project CLAUDE.md](../CLAUDE.md) - Development guidelines
