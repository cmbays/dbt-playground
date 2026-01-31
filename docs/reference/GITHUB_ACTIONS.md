---
audience: [multi-agent, human]
priority: high
size: medium
last_updated: 2026-01-31
status: active
tags: [github-actions, ci-cd, quick-reference]
---

# GitHub Actions Quick Reference

Quick reference guide for understanding and working with GitHub Actions in this project.

## Workflow Files

All workflows live in `.github/workflows/`:

| File | Name | Status |
|------|------|--------|
| `pr-validation.yml` | PR Validation | Active |
| `issue-linker.yml` | Issue Linker | Active |
| `pr-labeler.yml` | PR Labeler | Active |
| `dbt-test.yml` | dbt Tests | Active |

---

## PR Lifecycle with GitHub Actions

```text
1. Create Feature Branch
   |
   v
2. Open Pull Request
   |
   +---> PR Validation (check title format)
   +---> Issue Linker (verify issue reference)
   +---> PR Labeler (apply type/size/layer labels)
   +---> dbt Tests (if dbt files changed)
   |
   v
3. All Checks Pass?
   |
   +-- No --> Fix issues, push again
   |
   +-- Yes --> Ready for review
   |
   v
4. Code Review
   |
   v
5. Merge to Main
   |
   +---> dbt Tests (run on main)
```

---

## Status Check Quick Reference

### Passing PR Checklist

- [ ] PR title follows conventional commits (`feat:`, `fix:`, etc.)
- [ ] PR body contains issue reference (`Closes #N`)
- [ ] Referenced issue exists
- [ ] dbt tests pass (if dbt files changed)

### Common Failures

| Check | Failure Reason | Fix |
|-------|----------------|-----|
| PR Validation | Bad title format | Use `type(scope): description` |
| Issue Linker | No issue reference | Add `Closes #N` to description |
| Issue Linker | Issue not found | Create issue or fix number |
| dbt Tests | Tests failing | Fix failing tests locally first |
| dbt Tests | Build error | Check dbt compilation errors |

---

## Viewing Workflow Results

### From GitHub UI

1. Go to the PR page
2. Scroll to "Checks" section at bottom
3. Click on failing check for details
4. View "Actions" tab for full run history

### From Command Line

```bash
# List workflow runs
gh run list

# View specific run
gh run view <run-id>

# Watch a running workflow
gh run watch <run-id>

# View workflow logs
gh run view <run-id> --log
```

---

## Manual Workflow Triggers

Some workflows can be triggered manually (not currently enabled):

```bash
# If workflow_dispatch is enabled
gh workflow run <workflow-name>
```

---

## Debugging Failed Workflows

### Step 1: Identify the failure

```bash
# Get recent failed runs
gh run list --status failure --limit 5

# View failure details
gh run view <run-id> --log-failed
```

### Step 2: Read the error message

Each workflow provides specific error messages:

- **PR Validation**: Shows expected format and examples
- **Issue Linker**: Shows which issue number wasn't found
- **dbt Tests**: Shows test output and failures

### Step 3: Fix locally

```bash
# For dbt failures - run locally first
uv run dbt build

# For title format - amend and force push
git commit --amend
git push --force
```

---

## Workflow Permissions

| Workflow | Permissions |
|----------|-------------|
| PR Validation | Read (default) |
| Issue Linker | Read (default) |
| PR Labeler | `pull-requests: write` |
| dbt Tests | Read (default) + artifact upload |

---

## Environment Variables

### dbt Test Workflow

| Variable | Value | Purpose |
|----------|-------|---------|
| `DBT_TARGET` | `ci` | Use CI profile |
| `DUCKDB_PATH` | `:memory:` | In-memory database |

---

## Artifacts

### dbt Tests Artifacts

Artifacts are retained for 7 days:

- `manifest.json` - dbt manifest
- `run_results.json` - Test results
- `dbt_output.log` - Full build output

Download via:

```bash
gh run download <run-id> -n dbt-artifacts
```

---

## Adding New Workflows

### Workflow Template

```yaml
name: Workflow Name

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  job-name:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Your step
        run: echo "Hello"
```

### Best Practices

1. Use `actions/checkout@v4` for checkout
2. Use `actions/github-script@v7` for GitHub API calls
3. Pin action versions with `@vX` (not `@main`)
4. Add descriptive step names
5. Use job-level `defaults.run.working-directory` when needed

---

## Troubleshooting

### Workflow not running

**Symptoms**: PR opened but no checks appear

**Causes**:

- Workflow file syntax error
- Trigger doesn't match event
- Workflow disabled

**Fix**:

```bash
# Check workflow status
gh workflow list

# Enable if disabled
gh workflow enable <workflow-name>
```

### Permission denied errors

**Symptoms**: "Resource not accessible by integration"

**Fix**: Add permissions block to job:

```yaml
jobs:
  my-job:
    permissions:
      pull-requests: write  # for labeling
      issues: write         # for commenting
```

### Checkout fails

**Symptoms**: "Could not find version matching..."

**Fix**: Use specific ref:

```yaml
- uses: actions/checkout@v4
  with:
    ref: ${{ github.head_ref }}
```

### dbt tests fail but pass locally

**Symptoms**: Tests pass on your machine but fail in CI

**Causes**:

- Missing source data
- Different dbt profile
- Environment differences

**Fix**:

1. Ensure `load_synthea_sources` runs first
2. Check profile uses `:memory:` database
3. Verify Python/dbt versions match

---

## Monitoring

### Check workflow health

```bash
# Recent runs summary
gh run list --limit 10

# Failure rate
gh run list --status failure --limit 50 | wc -l
```

### Workflow run time

Watch for workflows taking too long - consider caching if dbt tests exceed 5 minutes.

---

## Related Documentation

- [GitHub Enforcement Strategy](./GITHUB_ENFORCEMENT.md) - Detailed workflow descriptions
- [GitHub Actions Guide](../for_chris/GITHUB_ACTIONS_GUIDE.md) - Manual testing steps
- [Git Workflow Rules](../../.claude/rules/git-workflow.md) - Commit conventions

---

*Last Updated: 2026-01-31*
