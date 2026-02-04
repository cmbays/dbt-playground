# Deploy Checklist

**Last Updated**: 2026-02-04
**Enforcement**: CI automated (GitHub Actions)
**Scope**: Pre-merge requirements for all PRs

---

## Quick Reference

| PR Type | Tests | Review | Docs | CHANGELOG | Issue Link |
|---------|-------|--------|------|-----------|------------|
| `feat` | Required | Required | Required | Required | Required |
| `fix` | Required | Required | If affected | Required | Required |
| `docs` | N/A | Required | N/A | Optional | Required |
| `refactor` | Required | Required | If affected | Optional | Required |
| `chore` | If applicable | Required | N/A | Optional | Required |
| `test` | Required | Required | N/A | Optional | Required |

---

## CI-Enforced Gates (Blocking)

These checks run automatically and **must pass** before merge.

### 1. PR Validation (`pr-validation.yml`)

- **Conventional commit title**: `type(scope): description`
- Valid types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `build`, `ci`

```
feat(staging): add stg_stripe__payments model  ✓
fix(marts): correct null handling              ✓
Added new feature                              ✗
```

### 2. Issue Linker (`issue-linker.yml`)

- **Must reference at least one issue** in PR description
- Use: `Closes #N`, `Fixes #N`, `Resolves #N` (auto-closes)
- Or: `Related to #N`, `See also #N` (links only)

### 3. Test Suite (`test.yml`)

| Check | Requirement |
|-------|-------------|
| pytest | All tests pass |
| Coverage | ≥75% on `scripts/lib/` |
| ruff lint | No errors |
| ruff format | Code formatted |

### 4. dbt Tests (`dbt-test.yml`)

Triggers when dbt files change:

| Check | Requirement |
|-------|-------------|
| dbt build | All models compile |
| dbt test | All 425+ tests pass |

---

## Tiered Requirements by PR Type

### `feat` - New Features

**All gates required.**

| Category | Items |
|----------|-------|
| **Code** | CI passes, code review approved |
| **Tests** | New tests for new functionality |
| **Docs** | Update affected docs, add to CHANGELOG |
| **Git** | Issue linked, conventional title |

### `fix` - Bug Fixes

**Focus on regression prevention.**

| Category | Items |
|----------|-------|
| **Code** | CI passes, code review approved |
| **Tests** | Add regression test for the bug |
| **Docs** | Update CHANGELOG, fix affected docs if any |
| **Git** | Issue linked (preferably the bug report) |

### `docs` - Documentation

**Lighter requirements.**

| Category | Items |
|----------|-------|
| **Code** | N/A (no code changes) |
| **Tests** | N/A |
| **Docs** | Content accurate, links valid |
| **Git** | Issue linked, review approved |

### `refactor` - Code Restructuring

**No behavior change, ensure stability.**

| Category | Items |
|----------|-------|
| **Code** | CI passes, code review approved |
| **Tests** | Existing tests still pass |
| **Docs** | Update if architecture changed |
| **Git** | Issue linked |

### `chore` - Maintenance

**Dependencies, config, tooling.**

| Category | Items |
|----------|-------|
| **Code** | CI passes |
| **Tests** | If applicable |
| **Docs** | N/A |
| **Git** | Issue linked |

---

## Documentation Requirements

### When to Update CHANGELOG

| PR Type | CHANGELOG Required |
|---------|-------------------|
| `feat` | **Yes** - Under "Added" |
| `fix` | **Yes** - Under "Fixed" |
| `docs` | Optional |
| `refactor` | Optional - Under "Changed" if significant |
| `chore` | Optional - Under "Changed" for deps |

### Affected Docs Checklist

When your PR changes behavior, check if these need updates:

- [ ] `CLAUDE.md` - If workflow or commands changed
- [ ] `docs/reference/*.md` - If architecture or standards changed
- [ ] `.claude/agents/*.md` - If agent behavior changed
- [ ] `.claude/commands/*.md` - If command behavior changed
- [ ] `playgrounds/*.html` - If playground usage changed

---

## Review Requirements

### Code Review

All PRs require at least one approval:

| Reviewer | Focus Areas |
|----------|-------------|
| Human | Architecture, business logic, security |
| Agent (code-reviewer) | Patterns, bugs, style consistency |
| Agent (security-reviewer) | For auth, input handling, API endpoints |

### Self-Review Checklist

Before requesting review:

- [ ] Code follows project coding standards
- [ ] No commented-out code or debug logs
- [ ] No hardcoded secrets or credentials
- [ ] Complex logic has comments
- [ ] Error handling is appropriate

---

## Post-Merge Smoke Test

After merge to main, verify manually:

### For `feat` PRs

1. Pull latest main: `git checkout main && git pull`
2. Install deps: `uv sync`
3. Run quick validation:
   ```bash
   uv run pytest tests/ -q --tb=no  # Tests pass
   uv run dbt build --select state:modified+  # dbt works
   ```
4. If playground changed: Open in browser, verify functionality

### For `fix` PRs

1. Verify the original bug is fixed
2. Verify no regression in related functionality

### For Infrastructure PRs

1. Verify CI pipelines run correctly
2. Check GitHub Actions logs for the merge commit

---

## Relationship to QA Enforcement (FS3)

| Document | Purpose | When Used |
|----------|---------|-----------|
| **DEPLOY_CHECKLIST.md** | Merge readiness | Before every PR merge |
| **QA_REPORT.md** | Testing documentation | Major features, complex fixes |

- **QA_REPORT.md** documents *what was tested and how*
- **DEPLOY_CHECKLIST.md** ensures *all gates are met*
- For significant PRs, QA_REPORT completion is a recommended (not blocking) item

---

## PR Template Alignment

The existing `.github/PULL_REQUEST_TEMPLATE.md` includes:

- Summary section ✓
- Related Issues section ✓
- Type of Change checkboxes ✓
- Testing section ✓
- Checklist section ✓

**This document formalizes which items are blocking vs advisory.**

---

## Troubleshooting Failed Checks

### PR Title Invalid

```
Error: PR title must follow Conventional Commits format
```

**Fix**: Edit PR title to `type(scope): description`

### No Issue Linked

```
Error: PR must reference at least one issue
```

**Fix**: Add `Closes #N` or `Related to #N` to PR description

### Tests Failing

```
Error: pytest failed
```

**Fix**:
1. Run locally: `uv run pytest tests/ -v`
2. Fix failing tests
3. Push fix

### dbt Build Failing

```
Error: dbt build failed
```

**Fix**:
1. Run locally: `uv run dbt build`
2. Check model SQL for errors
3. Run tests: `uv run dbt test`

---

## Version History

| Date | Change |
|------|--------|
| 2026-02-04 | Initial document created |

---

## Related Documents

- [WORKFLOW_STAGES.md](../reference/WORKFLOW_STAGES.md) - 5-stage workflow (VERIFY stage)
- [QA_REPORT template](../../docs/templates/agent-reports/QA_REPORT.md) - Testing documentation
- [GITHUB_ENFORCEMENT.md](../reference/GITHUB_ENFORCEMENT.md) - CI workflow details
- [PR Template](../../.github/PULL_REQUEST_TEMPLATE.md) - PR description format
