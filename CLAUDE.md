# CLAUDE.md — dbt-playground

## What this is

A synthetic **Synthea healthcare dbt project** on **DuckDB**. It is a
public, self-contained dbt project that serves as (a) the public fixture
source for the `breezy-bays-labs/cute-dbt` tool and (b) the target of a
cute-dbt GitHub-Pages PR-review dogfood.

All data is synthetic. There is no real patient data anywhere in this
repo, and there must never be.

## Layout

```text
dbt_project/   # the dbt project — models, macros, tests, seeds, snapshots
docs/          # dbt-domain reference, PRDs/TDDs, ADRs
scripts/       # lint wrappers: lint-sql.sh, lint-yaml.sh, fix-sql.sh
.claude/       # dbt-focused agents, commands, skills + settings
.github/       # dbt-test CI + Claude review workflows
```

The dbt layering is `staging/synthea → intermediate → marts/{core,analytics}`,
with a data-quality quarantine pattern (see
`docs/reference/DATA_QUALITY_QUARANTINE.md`).

Key reference docs: `docs/reference/ARCHITECTURE.md`,
`docs/reference/TECH_STACK.md`, `docs/reference/DBT_CODING_STANDARDS.md`,
`docs/reference/DBT_TESTING_STANDARDS.md`.

## Environment

Python is managed by **uv**. dbt runs on **DuckDB** via `dbt-duckdb`.

| Command | Purpose |
|---------|---------|
| `uv sync` | Install deps from `pyproject.toml` |
| `uv run dbt deps` | Install dbt packages (from `dbt_project/`) |
| `uv run dbt build` | Build models + run tests |
| `uv run dbt compile` | Compile SQL |
| `uv run dbt docs generate` | Generate docs |
| `npm run lint` | md + yaml + sql lint |
| `npm run lint:sql:fix` | sqlfluff auto-fix |

Pre-commit: markdown (markdownlint, auto-fix), YAML (yamllint),
SQL (sqlfluff, manual fix). A pre-push hook runs `dbt compile` and
rejects hardcoded `database.schema.table` references — use `ref()` /
`source()`.

## Conventions

- Branch + PR for everything; never push directly to `main`.
- Use `uv` for Python, never `pip`.
- Every dbt model gets a description and at least one test.
- Keep all fixture/seed data synthetic.

## Claude tooling

The `.claude/` directory ships dbt-focused agents
(`dbt-developer`, `dbt-tester`, `dbt-documenter`, `data-modeler`,
`healthcare-analyst`, `semantic-analyst`), `/dbt-*` commands, and dbt
skills (model development, testing, code review, deployment, semantic
layer, source onboarding). The dbt MCP server is configured in
root `.mcp.json` (`uvx dbt-mcp`).
