---
audience: [multi-agent, human]
priority: high
size: medium
last_updated: 2026-01-31
status: active
tags: [github-actions, automation, ci-cd, enforcement]
---

# GitHub Enforcement Strategy

Overview of GitHub Actions automation for enforcing workflow standards in this project.

## Philosophy

GitHub Actions provides **server-side enforcement** - the final layer in our defense-in-depth strategy. Unlike local hooks that can be bypassed, these workflows run on GitHub's infrastructure and cannot be skipped.

This complements our existing enforcement layers:

```text
Layer 5: GitHub Actions (this doc) ──── Server-side, unbypasable
Layer 4: Pre-Push Hook ──────────────── Local, blocks push to main
Layer 3: Pre-Commit Hook ────────────── Local, blocks commit to main
Layer 2: Supervisor Phase Gate ──────── Agent orchestration
Layer 1: Persona Verification ───────── Agent self-checks
```

See [UNDERSTANDING_PR_WORKFLOW.md](../for_chris/UNDERSTANDING_PR_WORKFLOW.md) for the full defense-in-depth philosophy.

---

## Phase 1 Workflows

Phase 1 focuses on PR quality enforcement without blocking development velocity.

### Workflow Overview

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| PR Validation | `pr-validation.yml` | PR open/edit | Enforce conventional commits in PR titles |
| Issue Linker | `issue-linker.yml` | PR open/edit | Require issue references |
| PR Labeler | `pr-labeler.yml` | PR open/sync | Auto-apply labels |
| dbt Tests | `dbt-test.yml` | PR + push to main | Run dbt build and tests |
| Project Automation | `project-automation.yml` | Issue open/labeled | Auto-add to GitHub Project |

---

## Workflow Details

### 1. PR Validation (`pr-validation.yml`)

**Purpose**: Enforce conventional commit format in PR titles.

**Triggers**:

- `pull_request: opened`
- `pull_request: edited`
- `pull_request: synchronize`

**What it checks**:

```text
Pattern: ^(feat|fix|docs|style|refactor|test|chore|build|ci)(\(.+\))?!?:\s*.+
```

**Valid examples**:

- `feat(staging): add stg_stripe__payments model`
- `fix(marts): correct null handling in dim_customers`
- `docs: update README`
- `feat!: remove deprecated API` (breaking change)

**Failure behavior**: Check fails with detailed error message explaining format.

**Location**: [`.github/workflows/pr-validation.yml`](../../.github/workflows/pr-validation.yml)

---

### 2. Issue Linker (`issue-linker.yml`)

**Purpose**: Require PRs to reference at least one issue for traceability.

**Triggers**:

- `pull_request: opened`
- `pull_request: edited`
- `pull_request: synchronize`

**What it checks**:

1. PR body contains issue reference (case-insensitive):
   - **Closing keywords** (auto-close on merge): `Closes #N`, `Fixes #N`, `Resolves #N`
   - **Related keywords** (link only): `Related to #N`, `See also #N`

2. Referenced issues actually exist in the repository

3. Warns if a closing keyword references an already-closed issue

**Categorized Logging**:

The workflow logs issues by category:

```text
Closing issues: #94 (Closes), #95 (Fixes)
Related issues: #91 (Related to)
```

**Failure behavior**: Check fails if no issue reference found or issue doesn't exist.

**Location**: [`.github/workflows/issue-linker.yml`](../../.github/workflows/issue-linker.yml)

---

### 3. PR Labeler (`pr-labeler.yml`)

**Purpose**: Automatically apply labels based on PR characteristics.

**Triggers**:

- `pull_request: opened`
- `pull_request: synchronize`

**Labels applied**:

#### By Commit Type (from PR title)

| Title Prefix | Label Applied |
|--------------|---------------|
| `feat:` | `enhancement` |
| `fix:` | `bug` |
| `docs:` | `documentation` |
| `refactor:` | `refactor` |
| `test:` | `testing` |
| `chore:` | `chore` |
| `perf:` | `performance` |
| `ci:` | `ci/cd` |

#### By Size (lines changed)

| Lines Changed | Label |
|---------------|-------|
| < 10 | `size/XS` |
| 10-49 | `size/S` |
| 50-199 | `size/M` |
| 200-499 | `size/L` |
| 500+ | `size/XL` |

#### By dbt Layer (files modified)

| Path Contains | Label |
|---------------|-------|
| `models/staging` | `layer/staging` |
| `models/intermediate` | `layer/intermediate` |
| `models/marts` | `layer/marts` |
| `models/analytics` | `layer/analytics` |

**Permissions required**: `pull-requests: write`

**Location**: [`.github/workflows/pr-labeler.yml`](../../.github/workflows/pr-labeler.yml)

---

### 4. dbt Tests (`dbt-test.yml`)

**Purpose**: Run dbt build and tests on code changes.

**Triggers**:

- `pull_request` when paths match:
  - `dbt_project/**`
  - `pyproject.toml`
- `push` to `main` when paths match:
  - `dbt_project/**`

**What it does**:

1. Checkout repository
2. Install `uv` package manager
3. Set up Python 3.11
4. Install project dependencies (`uv sync`)
5. Configure dbt profile for CI (in-memory DuckDB)
6. Load source data via `dbt run-operation load_synthea_sources`
7. Run `dbt build --full-refresh`
8. Parse results and comment on PR
9. Upload artifacts (manifest.json, run_results.json, logs)

**dbt Profile for CI**:

```yaml
healthcare_analytics:
  target: ci
  outputs:
    ci:
      type: duckdb
      path: ':memory:'
      threads: 4
```

**PR Comment**: Posts summary of test results including pass/fail counts.

**Artifacts retained**: 7 days

**Location**: [`.github/workflows/dbt-test.yml`](../../.github/workflows/dbt-test.yml)

---

## Required Labels

For the PR Labeler to work, these labels must exist in the repository:

### Type Labels

- `enhancement` - New feature
- `bug` - Bug fix
- `documentation` - Documentation changes
- `refactor` - Code refactoring
- `testing` - Test changes
- `chore` - Maintenance tasks
- `performance` - Performance improvements
- `ci/cd` - CI/CD changes

### Size Labels

- `size/XS` - Extra small (< 10 lines)
- `size/S` - Small (10-49 lines)
- `size/M` - Medium (50-199 lines)
- `size/L` - Large (200-499 lines)
- `size/XL` - Extra large (500+ lines)

### Layer Labels

- `layer/staging` - Staging models
- `layer/intermediate` - Intermediate models
- `layer/marts` - Marts models
- `layer/analytics` - Analytics models

---

## Workflow Architecture

```text
                    PR Created/Updated
                           |
           +---------------+---------------+
           |               |               |
           v               v               v
    +-----------+   +-----------+   +-----------+
    |    PR     |   |   Issue   |   |    PR     |
    | Validation|   |  Linker   |   |  Labeler  |
    +-----------+   +-----------+   +-----------+
           |               |               |
           v               v               v
    [Title Format]  [Issue Exists] [Apply Labels]
           |               |               |
           +---------------+---------------+
                           |
                           v
                    +-------------+
                    |  dbt Tests  |  (if dbt_project changed)
                    +-------------+
                           |
                           v
                    [Build + Test]
                           |
                           v
                    [Comment Results]
```

---

### 5. Project Automation (`project-automation.yml`)

**Purpose**: Automatically add labeled issues to GitHub Projects for roadmap tracking.

**Triggers**:

- `issues: opened`
- `issues: labeled`

**What it does**:

1. Checks if issue has qualifying labels: `workflow`, `phase-3`, `enhancement`, or `bug`
2. Adds issue to the v0.8 Roadmap project
3. Logs the addition with issue details

**Prerequisites**:

- GitHub Project created (see setup instructions below)
- `PROJECT_TOKEN` secret configured with `project` scope

**GitHub Project Setup**:

1. Navigate to: https://github.com/users/cmbays/projects
2. Create new "Board" project named "v0.8 Roadmap"
3. Add Status field with options: Backlog, In Progress, In Review, Done
4. Configure built-in automation:
   - Item added -> Set status to Backlog
   - Item closed -> Set status to Done
5. Note the project URL for workflow configuration
6. Add `PROJECT_TOKEN` secret to repository settings

**Location**: [`.github/workflows/project-automation.yml`](../../.github/workflows/project-automation.yml)

---

## Future Phases

### Phase 2 (Planned)

- Slack notifications for PR events
- Auto-assign reviewers based on CODEOWNERS
- Stale PR management

### Phase 3 (Complete)

- PR-Issue linking enhancements (closing vs related keywords)
- GitHub Projects integration with auto-add

---

## Related Documentation

- [GitHub Actions Quick Reference](./GITHUB_ACTIONS.md) - Quick reference and troubleshooting
- [GitHub Actions Guide](../for_chris/GITHUB_ACTIONS_GUIDE.md) - Manual testing and setup
- [PR Workflow Philosophy](../for_chris/UNDERSTANDING_PR_WORKFLOW.md) - Defense-in-depth strategy
- [Git Workflow Rules](../../.claude/rules/git-workflow.md) - Branch and commit conventions

---

*Last Updated: 2026-01-31*
