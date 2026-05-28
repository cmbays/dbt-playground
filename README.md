# dbt-playground

A synthetic **Synthea healthcare dbt project** running on **DuckDB**.

This repo is a public, self-contained dbt project built on
[Synthea](https://github.com/synthetichealth/synthea) synthetic
(non-real) healthcare data. It exists for two purposes:

1. **Public fixture source** for the
   [`breezy-bays-labs/cute-dbt`](https://github.com/breezy-bays-labs/cute-dbt)
   tool — its compiled `manifest.json` and unit-test shapes are used as
   demo/test fixtures.
2. **Dogfood target** for a cute-dbt GitHub-Pages PR-review workflow.

All data here is synthetic. No real patient data is present.

## Stack

- **dbt** with **DuckDB** (`dbt-duckdb`)
- **uv** for Python environment management
- **sqlfluff** (SQL) + **yamllint** (YAML) + **markdownlint** linting

## Quick start

```bash
# Install uv if needed: https://docs.astral.sh/uv/
uv sync

cd dbt_project
uv run dbt deps        # install dbt packages
uv run dbt build       # build models + run tests
uv run dbt docs generate && uv run dbt docs serve
```

The dbt project (`healthcare_analytics` profile) uses a `:memory:` /
local DuckDB target. See `dbt_project/README.md` for project-specific
detail.

## Project layout

```text
dbt-playground/
├── dbt_project/        # the dbt project (staging → intermediate → marts/analytics)
│   ├── models/         # staging/synthea, intermediate, marts/core, marts/analytics
│   ├── macros/         # incl. data-quality / quarantine helpers
│   ├── tests/          # singular data-quality tests
│   ├── seeds/  snapshots/  analyses/
│   └── dbt_project.yml  packages.yml
├── docs/               # dbt-domain reference, PRDs/TDDs, ADRs
├── scripts/            # lint wrappers (sqlfluff / yamllint)
├── .claude/            # dbt-focused Claude Code agents, commands, skills
└── .github/workflows/  # dbt-test CI + Claude review
```

## Documentation

| Doc | Purpose |
|-----|---------|
| [docs/reference/ARCHITECTURE.md](docs/reference/ARCHITECTURE.md) | System / layering architecture |
| [docs/reference/PROJECT_STRUCTURE.md](docs/reference/PROJECT_STRUCTURE.md) | File organization |
| [docs/reference/TECH_STACK.md](docs/reference/TECH_STACK.md) | Technology versions and rationale |
| [docs/reference/DBT_CODING_STANDARDS.md](docs/reference/DBT_CODING_STANDARDS.md) | dbt modeling conventions |
| [docs/reference/DBT_TESTING_STANDARDS.md](docs/reference/DBT_TESTING_STANDARDS.md) | Testing conventions |
| [docs/reference/DATA_QUALITY_QUARANTINE.md](docs/reference/DATA_QUALITY_QUARANTINE.md) | DQ / quarantine pattern |
| [docs/reference/UV_MIGRATION.md](docs/reference/UV_MIGRATION.md) | uv Python workflow |
| [docs/for_chris/KIMBALL_DIMENSIONAL_MODELING.md](docs/for_chris/KIMBALL_DIMENSIONAL_MODELING.md) | Dimensional modeling primer |

PRDs and TDDs for each layer live under `docs/specs/`.

## License

To be determined.
