---
audience: [developer]
priority: high
size: small
last_updated: 2026-01-29
status: active
tags: [reference, python, uv, migration]
---

# UV Migration Guide

This document describes the project's migration to uv-managed Python environment for reproducible dependency management.

## What Changed

- Added `pyproject.toml` for project metadata and dependencies
- Added `uv.lock` for reproducible, locked dependency versions (committed to git)
- Added `.python-version` for automatic Python version selection (3.11)
- Added PEP 723 headers to standalone scripts for compatibility with `uv run`

## Why UV?

| Benefit | Details |
|---------|---------|
| **Speed** | 10-100x faster than pip |
| **Reproducibility** | `uv.lock` ensures identical installs across machines |
| **Simplicity** | Single tool for all Python package needs |
| **Compatibility** | Works with existing Python ecosystem, PEP standards |

## Migration Steps

### For Existing Contributors

1. **Update uv** (if needed):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Remove old venv and recreate**:

   ```bash
   rm -rf .venv
   uv sync
   ```

3. **Verify installation**:

   ```bash
   uv run dbt --version
   # Should show: dbt 1.11.2

   uv run dbt debug
   # Should connect to dev.duckdb
   ```

4. **Update your shell** (one-time):

   ```bash
   # Activate the project venv
   source .venv/bin/activate

   # Or use uv run for one-off commands
   uv run dbt build
   ```

### For New Contributors

1. **Install uv**:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone and setup**:

   ```bash
   git clone <repo>
   cd dbt-playground
   uv sync
   ```

3. **Run dbt**:

   ```bash
   uv run dbt debug
   uv run dbt compile
   uv run dbt build
   ```

## Command Reference

### Common Workflows

| Task | Command |
|------|---------|
| **Install project deps** | `uv sync` |
| **Install with dev tools** | `uv sync --all-extras` |
| **Add a package** | `uv add pandas` |
| **Add dev package** | `uv add --group dev pytest` |
| **Run dbt** | `uv run dbt build` |
| **Run script** | `uv run scripts/extract_content.py` |
| **Activate venv** | `source .venv/bin/activate` |
| **Run one-off tool** | `uvx ruff check .` |
| **Update packages** | `uv sync --upgrade` |

### Comparison: Old vs New

| Old (pip) | New (uv) |
|-----------|----------|
| `pip install pkg` | `uv add pkg` |
| `pip install -r requirements.txt` | `uv sync` |
| `pip freeze > requirements.txt` | *Automatic via uv.lock* |
| `python script.py` | `uv run script.py` |
| `source venv/bin/activate && python -m pytest` | `uv run pytest` |
| `.gitignore requirements.txt` | *Commit uv.lock instead* |

## Key Files

| File | Purpose | Commit to Git |
|------|---------|---------------|
| `pyproject.toml` | Project metadata, dependencies | ✅ Yes |
| `uv.lock` | Locked dependency versions | ✅ Yes |
| `.python-version` | Python version (3.11) | ⚠️ Optional |
| `.venv/` | Virtual environment | ❌ No (.gitignore) |

## Troubleshooting

### "uv: command not found"

Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### "No pyproject.toml found"

Ensure you're in the project root:

```bash
pwd
# Should be: /Users/cmbays/Documents/claude/dbt-playground
```

### "Python version mismatch"

uv will automatically download the correct Python version:

```bash
uv python install 3.11
uv sync
```

### "dbt debug fails after uv sync"

Verify dbt-duckdb installation:

```bash
uv run dbt --version
# Should show: dbt 1.11.2

uv run python -c "import duckdb; print(duckdb.__version__)"
```

### "Different package versions between machines"

This is exactly why `uv.lock` exists! Make sure both machines run:

```bash
uv sync  # Uses uv.lock for identical versions
```

## FAQ

### Can I still use `pip install`?

Not recommended, but technically possible. Use `uv add` instead:

```bash
# ❌ Don't do this
pip install pandas

# ✅ Do this instead
uv add pandas
```

### Should I activate the venv manually?

Optional. You can either:

1. **Activate once**: `source .venv/bin/activate`, then use `python` normally
2. **Use uv for each command**: `uv run python script.py`

Pick whichever workflow you prefer.

### What if I need a different Python version?

Update `.python-version` and re-sync:

```bash
echo "3.12" > .python-version
uv sync
```

### Is `uv.lock` safe to edit?

No, don't edit it manually. Use uv commands to manage dependencies, it regenerates automatically.

### Can I use this with Docker?

Yes, use `uv` in your Dockerfile:

```dockerfile
FROM ghcr.io/astral-sh/uv:latest

WORKDIR /app
COPY . .

# Install dependencies
RUN uv sync --frozen

# Run dbt
CMD ["uv", "run", "dbt", "build"]
```

## Related Documentation

- **Quick Start**: See `CLAUDE.md` Development Environment section
- **Coding Standards**: See `.claude/rules/coding-style.md` Python section
- **dbt Standards**: See `docs/reference/DBT_CODING_STANDARDS.md`

## Support

For uv questions, see [official docs](https://docs.astral.sh/uv/).

For project-specific help, check `.claude/rules/` or ask in the team channel.
