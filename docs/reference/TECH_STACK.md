# Technology Stack

**Last Updated**: 2026-02-04
**Version Policy**: Exact pins for reproducibility. Updates via Dependabot PRs.

---

## Quick Reference

| Category | Technology | Version |
|----------|-----------|---------|
| Language | Python | 3.11 |
| Package Manager | **uv** (not pip) | 0.5.13 |
| Data Transformation | dbt-core | 1.11.2 |
| Database | DuckDB | 1.4.4 |
| Testing | pytest | 9.0.2 |
| Linting | ruff | 0.14.14 |
| CI/CD | GitHub Actions | Self-hosted runner |

> **Important**: Always use `uv` for Python packages. Never use `pip` directly.

---

## Python Stack

### Runtime

| Package | Locked Version | Purpose |
|---------|----------------|---------|
| Python | 3.11 | Runtime (pinned in `.python-version`) |
| uv | 0.5.13 | Package manager (replaces pip/poetry) |

### Core Dependencies

From `uv.lock` (production):

| Package | Locked Version | Purpose |
|---------|----------------|---------|
| dbt-core | 1.11.2 | Data transformation framework |
| dbt-duckdb | 1.10.0 | DuckDB adapter for dbt |
| duckdb | 1.4.4 | Embedded analytics database |
| click | 8.3.1 | CLI framework |
| pyyaml | 6.0.3 | YAML parsing |
| rich | 14.3.2 | Terminal formatting |
| jsonschema | 4.26.0 | JSON/YAML validation |

### Development Dependencies

| Package | Locked Version | Purpose |
|---------|----------------|---------|
| pytest | 9.0.2 | Test framework |
| pytest-cov | 7.0.0+ | Coverage reporting |
| ruff | 0.14.14 | Linting and formatting |
| sqlfluff | 4.0.0 | SQL linting |
| sqlfluff-templater-dbt | 3.0.0+ | dbt integration for SQLFluff |
| pre-commit | 3.7.0+ | Git hooks |
| flask | 3.1.2 | Local dev server |
| flask-cors | 6.0.2 | CORS for dev server |

### Version Files

| File | Purpose |
|------|---------|
| `.python-version` | Python version for uv/pyenv |
| `pyproject.toml` | Project metadata, dependency specs |
| `uv.lock` | Locked versions (commit this!) |

---

## JavaScript/Frontend Stack

### Node.js Dependencies

From `package.json`:

| Package | Version | Purpose |
|---------|---------|---------|
| @playwright/test | ^1.58.1 | E2E testing |
| husky | ^9.0.0 | Git hooks |
| lint-staged | ^15.0.0 | Pre-commit linting |
| markdownlint-cli2 | ^0.17.0 | Markdown linting |
| serve | ^14.2.5 | Static file server |
| ajv | ^8.17.1 | JSON schema validation |
| commander | ^14.0.3 | CLI for Node scripts |

### CDN Dependencies (Playgrounds)

All playgrounds use CDN-hosted libraries. **Lock to exact versions** to prevent breaking changes.

| Library | Locked Version | CDN URL | Used In |
|---------|----------------|---------|---------|
| Mermaid | 10.9.0 | `https://cdn.jsdelivr.net/npm/mermaid@10.9.0/dist/mermaid.min.js` | workflow-hub, mermaid-designer, agent-visualizer, learning-playground |
| Reveal.js | 4.6.0 | `https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/dist/reveal.js` | learning-playground |
| Panzoom | 9.4.3 | `https://cdn.jsdelivr.net/npm/panzoom@9.4.3/+esm` | mermaid-designer |

**Note**: Some playgrounds currently use `@10` (major only). Standardize to exact minor versions (e.g., `@10.9.0`) when updating.

---

## Data Stack

### dbt Configuration

| Setting | Value |
|---------|-------|
| dbt version | 1.11.2 |
| Profile | `healthcare_analytics` |
| Database | DuckDB (embedded) |
| Database file | `dbt_project/dev.duckdb` |

### dbt Packages

From `dbt_project/packages.yml`:

| Package | Version | Purpose |
|---------|---------|---------|
| dbt-labs/dbt_utils | 1.3.3 | Essential macros and tests |
| metaplane/dbt_expectations | 0.10.10 | Data quality testing framework |
| godatadriven/dbt_date | 0.17.1 | Date/time utilities (dim_date) |
| dbt-labs/codegen | 0.14.0 | Code generation helpers |

### Data Source

| Source | Description |
|--------|-------------|
| Synthea | Synthetic healthcare data generator |
| Format | CSV seeds in `dbt_project/seeds/` |

---

## CI/CD Stack

### GitHub Actions

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| test.yml | PR, push to main | Python tests + linting |
| dbt-test.yml | PR (dbt files) | dbt build validation |
| pr-validation.yml | PR open/edit | Conventional commit titles |
| issue-linker.yml | PR open/edit | Require issue references |
| pr-labeler.yml | PR open/sync | Auto-apply labels |
| task-file-sync.yml | Issue events | Task file automation |

### Runner Configuration

| Setting | Value |
|---------|-------|
| Type | Self-hosted |
| Platform | macOS ARM64 |
| Location | Local machine |

### Action Versions

| Action | Version |
|--------|---------|
| actions/checkout | v4 |
| actions/cache | v4 |
| actions/upload-artifact | v4 |
| astral-sh/setup-uv | v4 |

---

## Tool Configuration

### Ruff (Linting/Formatting)

From `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "C4", "SIM"]

[tool.ruff.format]
quote-style = "single"
```

### SQLFluff

```
dialect = duckdb
templater = dbt
```

### Pre-commit Hooks

| Hook | Tool | Auto-fix |
|------|------|----------|
| Markdown | markdownlint-cli2 | Yes |
| YAML | yamllint | No |
| SQL | sqlfluff | Manual |
| Python | ruff | Yes |

---

## Rejected Alternatives

### Why dbt over Plain SQL

| Factor | Plain SQL | dbt |
|--------|-----------|-----|
| Dependency management | Manual ordering | Automatic via `ref()` |
| Testing | External tools | Built-in |
| Documentation | Separate system | Integrated |
| Incremental builds | DIY | Native support |

**Decision**: dbt provides a mature framework for data transformation with testing, documentation, and dependency management built in.

### Why DuckDB over SQLite/PostgreSQL

| Factor | SQLite | PostgreSQL | DuckDB |
|--------|--------|------------|--------|
| Setup | Zero config | Server required | Zero config |
| Analytics | Limited | Full | Optimized |
| Columnar | No | No | Yes |
| dbt support | Community | Official | Official |

**Decision**: DuckDB offers PostgreSQL-compatible analytics with SQLite's simplicity. Perfect for local development and learning.

### Why uv over pip/poetry

| Factor | pip | poetry | uv |
|--------|-----|--------|-----|
| Speed | Slow | Medium | 10-100x faster |
| Lock file | requirements.txt | poetry.lock | uv.lock |
| Python management | External | External | Built-in |
| PEP 723 scripts | No | No | Yes |

**Decision**: uv provides faster, more reproducible dependency management with integrated Python version management.

### Why Vanilla JS over React (Playgrounds)

| Factor | React | Vanilla JS |
|--------|-------|------------|
| Build step | Required | None |
| File count | Multiple | Single HTML |
| Dependencies | npm ecosystem | CDN only |
| Learning curve | Framework | Native browser |

**Decision**: Single-file HTML playgrounds are self-contained, portable, and require no build tools. Appropriate for developer tools, not production apps.

---

## Updating Dependencies

### Python Dependencies (uv)

This project uses **uv** exclusively for Python package management. Never use pip directly.

```bash
# Update a specific package to latest
uv add package --upgrade

# Update to specific version
uv add package==x.y.z

# Update all dependencies (regenerates uv.lock)
uv lock --upgrade

# Install after lock changes
uv sync

# Check what's installed
uv pip list
```

**Key files**:
- `pyproject.toml` - Dependency specifications (version ranges)
- `uv.lock` - Locked versions (exact, reproducible) - **always commit this**

### Node Dependencies

```bash
# Update package.json
npm update

# Check for outdated
npm outdated
```

### CDN Dependencies

1. Check for new versions at jsdelivr.com
2. Update URL in playground HTML files
3. Test playground functionality
4. Update this document

### Dependabot + uv Workflow

Dependabot doesn't have native uv support yet, but the `pip` ecosystem can parse `pyproject.toml` and propose updates. Configuration is in `.github/dependabot.yml`.

**When Dependabot opens a Python PR**:

```bash
# 1. Check out the Dependabot branch
git checkout dependabot/pip/package-name-x.y.z

# 2. Regenerate uv.lock with the updated version
uv lock

# 3. Install and test
uv sync
uv run pytest tests/

# 4. Commit the updated uv.lock
git add uv.lock
git commit --amend --no-edit

# 5. Push (force needed since we amended)
git push --force-with-lease
```

**Ecosystems monitored**:
- `pip` - Python dependencies (via pyproject.toml, applied with uv)
- `npm` - Node.js dependencies
- `github-actions` - Action versions in workflows

---

## Version History

| Date | Change |
|------|--------|
| 2026-02-04 | Initial document created |

---

## Related Documents

- [UV_MIGRATION.md](./UV_MIGRATION.md) - uv workflow guide
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [DBT_CODING_STANDARDS.md](./DBT_CODING_STANDARDS.md) - dbt patterns
