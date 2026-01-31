---
audience: [human, sage]
priority: high
size: medium
last_updated: 2026-01-31
status: active
tags: [learning, github-actions, ci-cd, setup]
---

# GitHub Actions Guide

A practical guide for understanding, testing, and maintaining GitHub Actions in this project.

**Who this is for**: Developers who need to understand, debug, or extend the GitHub Actions automation.

---

## Quick Start

### View Current Status

```bash
# See all recent workflow runs
gh run list

# See runs for current PR
gh pr checks

# Watch a specific run in real-time
gh run watch
```

### Force Re-run

If a workflow failed due to transient issues:

```bash
# Re-run all failed jobs
gh run rerun <run-id> --failed

# Re-run entire workflow
gh run rerun <run-id>
```

---

## Understanding Our Workflows

We have four active workflows. Here's what each does and when:

### 1. PR Validation - Title Format Check

**When it runs**: Every time you open or edit a PR

**What it checks**: Your PR title must follow conventional commits:

```text
feat(staging): add new model       # Good
fix: correct null handling         # Good (scope optional)
feat!: breaking API change         # Good (breaking change)
Add new model                      # BAD - missing type
```

**If it fails**:

1. Edit your PR title on GitHub
2. Or use git to amend: `git commit --amend` then force push

### 2. Issue Linker - Traceability

**When it runs**: Every time you open or edit a PR

**What it checks**: PR description must reference an issue:

```markdown
## Summary
This PR adds patient demographics.

Closes #42
```

Valid keywords: `Closes`, `Fixes`, `Resolves`, `Related to`

**If it fails**:

1. Create an issue if one doesn't exist
2. Edit PR description to add `Closes #N`

### 3. PR Labeler - Auto-Labeling

**When it runs**: Every time you open a PR or push commits

**What it does**: Automatically applies labels based on:

- PR title type (feat -> enhancement, fix -> bug)
- Size of changes (XS, S, M, L, XL)
- dbt layers touched (staging, intermediate, marts, analytics)

**If it fails**: Usually means labels don't exist. See "Setup" below.

### 4. dbt Tests - Data Quality

**When it runs**:

- On PRs that change `dbt_project/` or `pyproject.toml`
- On push to main that changes `dbt_project/`

**What it does**:

1. Sets up Python and uv
2. Installs dependencies
3. Configures in-memory DuckDB
4. Loads test data
5. Runs `dbt build --full-refresh`
6. Comments test results on PR
7. Uploads artifacts

**If it fails**:

1. Read the failure log carefully
2. Run locally: `uv run dbt build`
3. Fix failing tests
4. Push again

---

## Manual Testing

### Testing Locally Before Push

Always run dbt tests locally before pushing:

```bash
# Quick test
uv run dbt test

# Full build (matches CI)
uv run dbt build --full-refresh

# Test specific model
uv run dbt test --select model_name
```

### Simulating CI Environment

The CI uses an in-memory DuckDB. To match:

```bash
# Create CI-like profile
cat > ~/.dbt/profiles.yml << 'EOF'
healthcare_analytics:
  target: ci
  outputs:
    ci:
      type: duckdb
      path: ':memory:'
      threads: 4
EOF

# Run with CI target
uv run dbt build --target ci
```

### Testing Workflow Changes

To test workflow changes without affecting main:

1. Create a test branch
2. Modify the workflow file
3. Open a draft PR
4. Watch the workflow run
5. Iterate until it works
6. Open real PR with your changes

```bash
# Create test branch
git checkout -b test/workflow-change

# Edit workflow
# ... make changes to .github/workflows/*.yml

# Push and create draft PR
git push -u origin test/workflow-change
gh pr create --draft --title "test: workflow changes"

# Watch the run
gh run watch
```

---

## Setup Instructions

### First-Time Setup

If you're setting up GitHub Actions for a new fork or repo:

#### 1. Enable Actions

```bash
# Check if enabled
gh repo view --json hasIssuesEnabled

# Enable via GitHub UI:
# Settings > Actions > General > Allow all actions
```

#### 2. Create Required Labels

The PR Labeler needs these labels to exist:

```bash
# Type labels
gh label create "enhancement" --color "a2eeef" --description "New feature"
gh label create "bug" --color "d73a4a" --description "Bug fix"
gh label create "documentation" --color "0075ca" --description "Documentation"
gh label create "refactor" --color "cfd3d7" --description "Code refactoring"
gh label create "testing" --color "f9d0c4" --description "Testing"
gh label create "chore" --color "fef2c0" --description "Maintenance"
gh label create "performance" --color "5319e7" --description "Performance"
gh label create "ci/cd" --color "fbca04" --description "CI/CD"

# Size labels
gh label create "size/XS" --color "ededed" --description "< 10 lines"
gh label create "size/S" --color "d4d4d4" --description "10-49 lines"
gh label create "size/M" --color "b3b3b3" --description "50-199 lines"
gh label create "size/L" --color "8c8c8c" --description "200-499 lines"
gh label create "size/XL" --color "666666" --description "500+ lines"

# Layer labels
gh label create "layer/staging" --color "1d76db" --description "Staging models"
gh label create "layer/intermediate" --color "0e8a16" --description "Intermediate models"
gh label create "layer/marts" --color "5319e7" --description "Marts models"
gh label create "layer/analytics" --color "e99695" --description "Analytics models"
```

#### 3. Verify Workflows

```bash
# List workflows
gh workflow list

# They should all show as "active"
```

---

## Common Issues and Solutions

### Issue: "Resource not accessible by integration"

**Cause**: Workflow lacks permissions

**Solution**: Add permissions to the job in the workflow file:

```yaml
jobs:
  my-job:
    permissions:
      pull-requests: write
```

### Issue: Workflow doesn't trigger

**Cause**: Event doesn't match trigger

**Check**:

1. Is the file in `.github/workflows/`?
2. Does the trigger match your event?
3. Is the workflow enabled?

```bash
gh workflow list
gh workflow enable <name>  # if disabled
```

### Issue: dbt tests fail with "source not found"

**Cause**: Source data not loaded

**Solution**: Ensure `load_synthea_sources` runs first:

```yaml
- name: Load source data
  run: uv run dbt run-operation load_synthea_sources
```

### Issue: Tests pass locally but fail in CI

**Possible causes**:

1. Different Python version (we use 3.11)
2. Different dependencies (run `uv sync`)
3. Different dbt profile (CI uses `:memory:`)
4. State from previous runs (CI starts fresh)

**Debug approach**:

```bash
# Match CI Python version
uv python install 3.11
uv sync

# Use in-memory database
uv run dbt build --target ci
```

### Issue: Workflow taking too long

**Typical times**:

- PR Validation: < 30 seconds
- Issue Linker: < 30 seconds
- PR Labeler: < 1 minute
- dbt Tests: 2-5 minutes

**If dbt tests are slow**:

- Consider caching dependencies
- Check for inefficient models
- Review test coverage (too many tests?)

---

## Extending Workflows

### Adding a New Check

1. Create new file in `.github/workflows/`
2. Define trigger events
3. Add steps
4. Test on draft PR

Example simple check:

```yaml
name: SQL Lint

on:
  pull_request:
    paths:
      - '**.sql'

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install sqlfluff
        run: pip install sqlfluff

      - name: Lint SQL
        run: sqlfluff lint dbt_project/models/
```

### Modifying Existing Workflow

1. Create feature branch
2. Edit workflow file
3. Push and watch the run
4. Iterate until working
5. Open PR

---

## Monitoring and Maintenance

### Weekly Checks

```bash
# Check for failed runs
gh run list --status failure --limit 20

# Check workflow run times
gh run list --limit 20 --json databaseId,conclusion,updatedAt
```

### Monthly Maintenance

1. Update action versions if new ones available
2. Review workflow run times
3. Check for deprecated features
4. Audit permissions

### Updating Action Versions

```yaml
# Before: old version
- uses: actions/checkout@v3

# After: updated version
- uses: actions/checkout@v4
```

Always test updates on a branch first.

---

## Useful Commands Reference

```bash
# View workflow runs
gh run list
gh run list --workflow=dbt-test.yml
gh run list --status failure

# View specific run
gh run view <run-id>
gh run view <run-id> --log
gh run view <run-id> --log-failed

# Watch running workflow
gh run watch

# Re-run workflow
gh run rerun <run-id>
gh run rerun <run-id> --failed

# Download artifacts
gh run download <run-id>
gh run download <run-id> -n dbt-artifacts

# PR checks
gh pr checks
gh pr checks <pr-number>

# Workflow management
gh workflow list
gh workflow view <name>
gh workflow enable <name>
gh workflow disable <name>
```

---

## Related Documentation

- [GitHub Enforcement Strategy](../reference/GITHUB_ENFORCEMENT.md) - Workflow descriptions
- [GitHub Actions Quick Reference](../reference/GITHUB_ACTIONS.md) - Quick lookup
- [PR Workflow Philosophy](./UNDERSTANDING_PR_WORKFLOW.md) - Why we enforce this

---

*Last Updated: 2026-01-31*
