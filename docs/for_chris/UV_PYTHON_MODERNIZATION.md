---
audience: [human, sage]
priority: medium
size: medium
last_updated: 2026-01-29
status: active
tags: [learning, python, uv, dbt, modernization]
---

# UV Python Modernization: A dbt Project Journey

**Topic**: Modernizing a dbt project to use uv-managed Python dependencies

**Context**: dbt-playground v0.2 migration from implicit pip management to explicit uv workflow

**Why this matters**: Python dependency management is a common pain point. Understanding the "why" behind uv choices helps you make informed decisions for future projects.

---

## The Problem We Solved

Before this migration, the project had a subtle problem: **no explicit dependency management**. dbt was installed "somehow" (probably `pip install dbt-duckdb` at some point), and the Python scripts just assumed the right packages were there.

This works fine for solo development. It becomes a nightmare when:

- You need to set up a new machine
- Someone else wants to contribute
- CI/CD needs reproducible builds
- You forget which Python version you used

The solution: Explicit, reproducible dependency management with uv.

---

## Why uv Over pip/poetry/pipenv?

I chose uv for several reasons:

**Speed**: uv is written in Rust and is 10-100x faster than pip. Installing dbt-duckdb and all its dependencies takes ~2 seconds instead of ~30 seconds.

**Simplicity**: One tool does everything. No juggling between pip, pip-tools, virtualenv, pyenv, etc.

**Standards-based**: Uses `pyproject.toml` (PEP 621) and lock files (like npm/yarn). No proprietary formats.

**Lock files that work**: `uv.lock` actually ensures reproducibility. Unlike `pip freeze`, it captures the entire dependency tree with hashes.

The tradeoff: uv is newer (2024) and less widely adopted. But for a learning project, that's fine.

---

## Key Decisions and Why

### Decision 1: No Build System

Traditional Python projects include a `[build-system]` section:

```toml
# NOT USED - we skipped this
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Why we skipped it**: dbt projects aren't Python libraries. Nobody will `pip install dbt-playground`. The build system is only needed if you're publishing a package to PyPI.

Adding it would create unnecessary complexity and potential version conflicts. Keep it simple.

### Decision 2: Loose Version Constraints

We use `dbt-duckdb>=1.10.0` instead of `dbt-duckdb==1.11.2`.

**Why**: The exact version (1.11.2) didn't exist as a separate package. dbt-duckdb versioning doesn't always match dbt-core versioning.

More importantly: loose constraints + lock file is the modern best practice. The `pyproject.toml` says "I need at least version 1.10", and the `uv.lock` records exactly which version was installed (1.11.2 as a transitive dependency of dbt-core).

This gives you:

- **Flexibility**: Can upgrade without changing pyproject.toml
- **Reproducibility**: Lock file ensures everyone gets the same version
- **Clarity**: pyproject.toml shows intent, lock file shows reality

### Decision 3: Commit the Lock File

Some teams debate whether to commit lock files. For applications (vs libraries), the answer is clear: **yes, commit it**.

The `uv.lock` file is like a receipt. It says "here's exactly what was installed when this worked." Without it, `uv sync` might install newer versions that introduce bugs.

### Decision 4: PEP 723 for Scripts

We added headers like this to Python scripts:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
```

**Why**: This is PEP 723 (Inline Script Metadata). It makes scripts self-documenting and enables `uv run script.py` to automatically handle dependencies.

For stdlib-only scripts (like ours), `dependencies = []` is explicit about having no external requirements. For scripts that need pandas or requests, you'd list them here.

The nice thing: scripts become portable. You can copy a PEP 723 script to any machine with uv and it just works.

---

## What We Learned the Hard Way

### Version Numbers Lie

I initially tried `dbt-duckdb>=1.11.2` because that's what `dbt --version` showed. It failed. The actual package on PyPI was `dbt-duckdb 1.10.0`, and dbt-core 1.11.2 was a transitive dependency.

**Lesson**: Always check what actually exists before pinning versions.

```bash
# How to check available versions
uv pip index versions dbt-duckdb
```

### Dev Dependencies Syntax is Changing

We used:

```toml
[tool.uv]
dev-dependencies = [
    "sqlfluff>=3.0.0",
]
```

This works but shows a deprecation warning. The new standard will be `[dependency-groups]` but it's not fully stable yet.

**Lesson**: Accept that Python packaging is still evolving. Use what works today, plan to migrate later.

### Linters May Strip PEP 723 Headers

Some code formatters don't recognize PEP 723 syntax and may reformat or strip the header block. The scripts still work, but you lose the self-documentation benefit.

**Lesson**: Test scripts after running formatters/linters.

---

## The Final Architecture

```
dbt-playground/
├── pyproject.toml      # Project definition (human-written)
├── uv.lock             # Exact versions (machine-generated)
├── .python-version     # Python version (3.11)
├── .venv/              # Virtual environment (not in git)
└── scripts/
    ├── extract_content.py         # PEP 723 header
    └── insert_shopping_dialogues.py  # PEP 723 header
```

**Workflow**:

1. Clone repo
2. Run `uv sync`
3. Everything works

That's it. No README steps about "install Python 3.11, create virtualenv, pip install..."

---

## When to Use This Pattern

**Good fit**:

- dbt projects (any adapter)
- Data engineering projects
- Team projects needing reproducibility
- CI/CD pipelines

**Not needed**:

- Quick scripts you'll run once
- Jupyter notebook exploration
- Projects already using poetry/pipenv (migration cost)

---

## Connecting to Bigger Patterns

This migration connects to broader software engineering principles:

**Explicit over implicit**: Don't rely on "it's probably installed". Define exactly what you need.

**Reproducibility over convenience**: The lock file adds a step, but saves hours of debugging "works on my machine" issues.

**Standards over tools**: pyproject.toml is a Python standard. uv implements it, but so could another tool. You're not locked in.

---

## References

- **Executable workflow**: `.claude/skills/learned-pattern-uv-dbt-project-setup.md`
- **Technical patterns**: `docs/reference/LEARNINGS.md#dbt--uv-patterns`
- **Team guide**: `docs/reference/UV_MIGRATION.md`
- **uv documentation**: <https://docs.astral.sh/uv/>

---

*Last updated: 2026-01-29 after v0.2 environment modernization*
