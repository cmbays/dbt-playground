# Learned Pattern: UV + dbt Project Setup

**Purpose**: Systematic workflow for setting up and maintaining a dbt project with uv-managed Python dependencies.

**Owner**: Developer persona

**Extracted from**: dbt-playground v0.2 environment modernization

**Proven in**: dbt-playground uv migration (2026-01-29)

---

## When to Use

**Trigger conditions**:

- Setting up a new dbt project from scratch
- Migrating existing dbt project from pip/requirements.txt to uv
- Adding Python scripts to a dbt project
- Troubleshooting dependency issues in dbt projects

**Proactive use**:

- Part of project initialization workflow
- Before adding any Python dependencies
- When onboarding new team members

---

## Prerequisites

**Required**:

- uv installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- dbt adapter package name (e.g., `dbt-duckdb`, `dbt-snowflake`)
- Target Python version (recommend 3.11+ for dbt 1.8+)

**Recommended**:

- Existing `profiles.yml` or dbt configuration
- Understanding of dbt adapter compatibility

---

## Process

### Step 1: Create pyproject.toml

**Purpose**: Define project metadata and dependencies

**Key decisions**:

1. **No build-system section** - dbt projects are not Python libraries
2. **Loose version constraints** - Use `>=1.10.0` not exact versions
3. **Separate dev-dependencies** - Linters/tools in `[tool.uv]`

**Template**:

```toml
[project]
name = "your-dbt-project"
version = "0.1.0"
description = "Brief project description"
requires-python = ">=3.11"
dependencies = [
    "dbt-duckdb>=1.10.0",  # Or your adapter
]

[tool.uv]
dev-dependencies = [
    "sqlfluff>=3.0.0",
    "sqlfluff-templater-dbt>=3.0.0",
    "pre-commit>=3.7.0",
]
```

**Common gotchas**:

- Check actual package availability: `dbt-duckdb>=1.10.0` exists, but `dbt-duckdb>=1.11.2` may not
- The `tool.uv.dev-dependencies` syntax shows deprecation warning (acceptable for now)
- Don't add `[build-system]` section - causes unnecessary complexity for non-library projects

---

### Step 2: Create .python-version

**Purpose**: Pin Python version for automatic selection

**Action**:

```bash
echo "3.11" > .python-version
```

**Benefits**:

- uv automatically uses correct Python version
- Prevents "works on my machine" issues
- Enables uv to download Python if needed

---

### Step 3: Initialize Virtual Environment

**Purpose**: Create reproducible environment

**Commands**:

```bash
# Remove old venv if exists
rm -rf .venv

# Create new venv and install dependencies
uv sync

# Verify installation
uv run dbt --version
uv run dbt debug
```

**Expected output**:

```
Using CPython 3.11.x
Creating virtual environment at: .venv
Resolved X packages in Yms
Installed Z packages in Wms

dbt 1.11.2
dbt debug: All checks passed!
```

---

### Step 4: Configure Git Tracking

**Purpose**: Ensure reproducible builds across machines

**Actions**:

```bash
# Add to .gitignore (if not already):
echo ".venv/" >> .gitignore

# Commit lock file:
git add uv.lock pyproject.toml .python-version
git commit -m "chore: add uv dependency management"
```

**Key files**:

| File | Commit? | Reason |
|------|---------|--------|
| `pyproject.toml` | Yes | Project definition |
| `uv.lock` | Yes | Reproducible builds |
| `.python-version` | Yes | Version consistency |
| `.venv/` | No | Generated locally |

---

### Step 5: Add PEP 723 Headers to Scripts

**Purpose**: Enable standalone script execution with `uv run`

**When to use**:

- Scripts with external dependencies (pandas, requests, etc.)
- Scripts that should be self-documenting
- Cross-project utility scripts

**Template for scripts with dependencies**:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pandas>=2.0.0",
#     "requests>=2.31.0",
# ]
# ///
"""
Script description here.
"""

import pandas as pd
import requests
# ... rest of script
```

**Template for stdlib-only scripts**:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Script description here.
"""

import sys
from pathlib import Path
# ... rest of script
```

**Note**: PEP 723 headers may be stripped by some linters but functionality remains intact.

---

### Step 6: Verify Complete Setup

**Purpose**: Confirm everything works together

**Verification checklist**:

```bash
# 1. dbt works
uv run dbt --version
uv run dbt debug

# 2. dbt can compile/build
uv run dbt compile

# 3. Scripts run correctly
uv run scripts/your_script.py

# 4. Dev tools work
uv run sqlfluff lint dbt_project/models/
```

---

## Common Workflows After Setup

### Adding a New Dependency

```bash
# Production dependency
uv add pandas

# Development dependency
uv add --dev pytest

# Then commit lock file
git add uv.lock pyproject.toml
git commit -m "chore: add pandas dependency"
```

### Running dbt Commands

```bash
# All dbt commands go through uv run
uv run dbt build
uv run dbt test
uv run dbt docs generate
```

### Running Python Scripts

```bash
# Scripts in scripts/ directory
uv run scripts/extract_content.py

# Or with arguments
uv run scripts/load_data.py --source synthea
```

### Updating Dependencies

```bash
# Update all packages
uv sync --upgrade

# Update specific package
uv add dbt-duckdb@latest
```

---

## Troubleshooting

### "Package version not found"

**Symptom**: `uv add dbt-duckdb>=1.11.2` fails

**Cause**: Exact version doesn't exist in PyPI

**Fix**: Use available version (check PyPI): `dbt-duckdb>=1.10.0`

### "dbt debug fails"

**Symptom**: dbt installed but can't connect

**Fix**:

1. Check `profiles.yml` exists and is configured
2. Verify database path/credentials
3. Run `uv run dbt debug` for detailed error

### "Module not found in script"

**Symptom**: Script fails with import error

**Fix**:

1. If script uses project deps: just `uv run script.py`
2. If script has unique deps: add PEP 723 header

### "Deprecation warning for dev-dependencies"

**Symptom**: Warning about `tool.uv.dev-dependencies`

**Status**: Acceptable for now; syntax still works

**Future**: May migrate to `dependency-groups` when stable

---

## Decision Framework: When to Use Each Approach

| Scenario | Approach |
|----------|----------|
| Project dependencies (dbt, adapters) | `pyproject.toml` `[project.dependencies]` |
| Dev tools (linters, formatters) | `pyproject.toml` `[tool.uv.dev-dependencies]` |
| Script-specific deps | PEP 723 header in script |
| One-off tool execution | `uvx tool-name` (no install) |

---

## See Also

- `docs/reference/UV_MIGRATION.md` - Team migration guide
- `.claude/rules/coding-style.md` - Python/uv coding standards
- `CLAUDE.md` - Development environment section
- `docs/reference/LEARNINGS.md#dbt-uv-patterns` - Technical patterns
