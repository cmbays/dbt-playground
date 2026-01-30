---
audience: [developer]
priority: low
size: small
last_updated: 2026-01-29
status: active
tags: [scripts, utilities, build, index]
---

# Scripts Folder

Utility scripts for building and maintaining the dbt-playground project.

## Running Scripts

All Python scripts should be run with `uv run`:

```bash
uv run python scripts/script_name.py
```

Shell scripts can be run directly:

```bash
./scripts/script_name.sh
```

## Available Scripts

### Shell Scripts

| Script | Purpose |
|--------|---------|
| `lint-sql.sh` | Run sqlfluff lint on SQL files |
| `fix-sql.sh` | Auto-fix SQL formatting issues |
| `lint-yaml.sh` | Run yamllint on YAML files |
| `validate-frontmatter.sh` | Validate YAML frontmatter in docs |
| `count-agent-tokens.sh` | Count tokens in agent definitions |

### Python Scripts

| Script | Purpose |
|--------|---------|
| `rss_digest.py` | RSS aggregator for AI/Claude content (26 feeds, interactive HTML output) |
| `extract_content.py` | Content extraction utility |
| `insert_shopping_dialogues.py` | Data insertion utility |

## Adding New Scripts

### Shell Scripts

```bash
#!/usr/bin/env bash
# Description of what the script does
set -euo pipefail

# Script logic here
```

### Python Scripts

For scripts with dependencies, use PEP 723 inline metadata:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pandas", "rich"]
# ///

"""Script description."""

# Script logic here
```

Then run with: `uv run scripts/my_script.py`

## Potential Future Scripts

- `seed_data.py` - Generate sample seed data
- `validate_models.py` - Validate dbt model conventions
- `generate_docs.py` - Generate documentation from models
