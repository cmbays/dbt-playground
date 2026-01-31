# GitHub Actions Roadmap

**Author**: Product Manager
**Date**: 2026-01-31
**Status**: Planning
**Related**: [ENFORCEMENT_PLAN.md](/Users/cmbays/Documents/claude/dbt-playground/temp/ENFORCEMENT_PLAN.md), [GITHUB_ACTIONS_STRATEGY.md](/Users/cmbays/Documents/claude/dbt-playground/temp/GITHUB_ACTIONS_STRATEGY.md)

---

## Overview

This roadmap defines the phased rollout of 10 GitHub Actions workflows to automate enforcement, validation, and workflow intelligence for the dbt-playground project.

---

## Phases Summary

| Phase | Timeline | Workflows | Theme |
|-------|----------|-----------|-------|
| MVP | Week 1-2 | 4 workflows | Foundation validation |
| Phase 2 | Week 3-4 | 4 workflows | Process compliance |
| Phase 3 | Week 5-6 | 4 workflows | Security and automation |
| Phase 4 | Week 7+ | 3 workflows | Observability |

---

## MVP Phase (Week 1-2)

**Goal**: Establish foundational validation that catches issues before merge.

| # | Workflow | Impact | Priority | Effort | Dependencies |
|---|----------|--------|----------|--------|--------------|
| 1 | `pr-validation.yml` | Hard block | P0 | S | None (already designed) |
| 2 | `issue-linker.yml` | Hard block | P0 | M | None |
| 3 | `pr-labeler.yml` | Advisory | P0 | S | None |
| 4 | `dbt-test.yml` | Hard block | P0 | L | uv, DuckDB setup |

### Workflow Details

#### 1. pr-validation.yml (Already Designed)

- **Trigger**: `pull_request` (opened, synchronize, reopened, edited)
- **What**: Validates PR title format (conventional commits), CHANGELOG check (warning), PR template check (warning)
- **Effort**: Small - copy from ENFORCEMENT_PLAN.md
- **Acceptance**: Invalid PR title blocks merge

#### 2. issue-linker.yml

- **Trigger**: `pull_request` (opened, edited, synchronize)
- **What**: Validates at least one issue is linked (Closes #N, Fixes #N, Related to #N)
- **Effort**: Medium - JavaScript parsing in actions/github-script
- **Acceptance**: PR without linked issue cannot merge

#### 3. pr-labeler.yml

- **Trigger**: `pull_request` (opened, synchronize)
- **What**: Auto-labels by commit type, size (XS/S/M/L/XL), dbt layer
- **Effort**: Small - straightforward labeling logic
- **Acceptance**: Labels automatically applied

#### 4. dbt-test.yml

- **Trigger**: `pull_request` + `push` (main) on dbt_project/** changes
- **What**: Runs `dbt build`, parses results, comments on PR
- **Effort**: Large - requires uv setup, DuckDB in-memory, data seeding
- **Acceptance**: All dbt tests must pass for merge

### MVP Prerequisites

- [ ] Create required GitHub labels (size/*, layer/*, enhancement, bug, etc.)
- [ ] Configure branch protection to require `pr-validation` status check
- [ ] Create `.github/workflows/` directory

---

## Phase 2 (Week 3-4)

**Goal**: Enforce process compliance and improve visibility.

| # | Workflow | Impact | Priority | Effort | Dependencies |
|---|----------|--------|----------|--------|--------------|
| 5 | `changelog-enforcer.yml` | Hard block | P1 | S | pr-labeler for skip-changelog label |
| 6 | `agent-tracker.yml` | Advisory | P1 | M | Agent report templates |
| 7 | `stale-pr-notifier.yml` | Advisory | P2 | S | None |
| 8 | `pr-size-analyzer.yml` | Advisory | P2 | S | None |

### Workflow Details

#### 5. changelog-enforcer.yml

- **Trigger**: `pull_request` (opened, synchronize, labeled, unlabeled)
- **What**: Blocks feat/fix PRs without CHANGELOG.md update (skip with label)
- **Effort**: Small - file diff check
- **Acceptance**: feat/fix PRs require CHANGELOG or skip-changelog label

#### 6. agent-tracker.yml

- **Trigger**: `pull_request` on temp/AGENT_REPORTS/** changes
- **What**: Summarizes agent reports, posts consolidated comment on PR
- **Effort**: Medium - Markdown parsing, summary generation
- **Acceptance**: Agent findings visible in PR comments
- **Design Note**: See `temp/AGENT_TRACKER_DESIGN_QUESTIONS.md` for open questions

#### 7. stale-pr-notifier.yml

- **Trigger**: `schedule` (daily cron)
- **What**: Comments on PRs with no activity for 7+ days
- **Effort**: Small - GitHub API query
- **Acceptance**: Stale PRs get notification comment

#### 8. pr-size-analyzer.yml

- **Trigger**: `pull_request`
- **What**: Warns on PRs exceeding 500 lines, suggests splitting
- **Effort**: Small - lines changed check
- **Acceptance**: Large PRs get advisory warning

---

## Phase 3 (Week 5-6)

**Goal**: Harden security and automate formatting/documentation.

| # | Workflow | Impact | Priority | Effort | Dependencies |
|---|----------|--------|----------|--------|--------------|
| 9 | `secrets-scanner.yml` | Hard block | P0 | M | TruffleHog action |
| 10 | `wip-detector.yml` | Hard block | P1 | S | None |
| 11 | `lint-check.yml` | Advisory | P2 | M | sqlfluff, markdownlint |
| 12 | `dbt-docs-generator.yml` | Artifact | P2 | M | dbt-test success |

### Workflow Details

#### 9. secrets-scanner.yml

- **Trigger**: `pull_request`, `push` (main)
- **What**: Scans for hardcoded secrets, credentials, API keys
- **Effort**: Medium - TruffleHog integration, custom dbt credential check
- **Acceptance**: Detected secrets block merge

#### 10. wip-detector.yml

- **Trigger**: `pull_request` (opened, synchronize, edited, ready_for_review)
- **What**: Blocks merge if PR title/commits contain WIP markers
- **Effort**: Small - pattern matching
- **Acceptance**: WIP markers block non-draft PRs

#### 11. lint-check.yml

- **Trigger**: `pull_request` on SQL/MD/YAML changes
- **What**: Runs sqlfluff, markdownlint, yamllint; annotates violations
- **Effort**: Medium - multiple linter setup
- **Acceptance**: Lint violations shown as annotations (advisory)

#### 12. dbt-docs-generator.yml

- **Trigger**: `push` (main) on dbt_project/** changes, `workflow_dispatch`
- **What**: Generates dbt docs, uploads as artifact
- **Effort**: Medium - dbt docs generate, artifact upload
- **Acceptance**: Docs artifact available for download

---

## Phase 4 (Week 7+)

**Goal**: Full automation and observability.

| # | Workflow | Impact | Priority | Effort | Dependencies |
|---|----------|--------|----------|--------|--------------|
| 13 | `merge-notify.yml` | Audit | P1 | S | None (already designed) |
| 14 | `release-notes.yml` | Artifact | P2 | M | Tag push trigger |
| 15 | `admin-audit.yml` | Advisory | P3 | M | GitHub audit log access |

### Workflow Details

#### 13. merge-notify.yml (Already Designed)

- **Trigger**: `push` (main)
- **What**: Logs merge details to step summary for audit trail
- **Effort**: Small - copy from ENFORCEMENT_PLAN.md
- **Acceptance**: Every merge to main logged

#### 14. release-notes.yml

- **Trigger**: `push` (tags v*)
- **What**: Auto-generates release notes from commits, creates GitHub release
- **Effort**: Medium - commit parsing, release creation
- **Acceptance**: Tagged versions get auto-generated release

#### 15. admin-audit.yml

- **Trigger**: `schedule` (weekly cron)
- **What**: Reports on admin bypasses, protection changes, anomalies
- **Effort**: Medium - GitHub audit log API
- **Acceptance**: Weekly compliance report generated

---

## Effort Estimates

| Size | Hours | Examples |
|------|-------|----------|
| S (Small) | 1-2h | pr-validation, merge-notify, wip-detector |
| M (Medium) | 2-4h | issue-linker, agent-tracker, lint-check |
| L (Large) | 4-8h | dbt-test (requires CI environment setup) |

**Total Estimated Effort**: 30-40 hours across all phases

---

## Dependencies Graph

```
pr-validation.yml (MVP)
        |
        v
issue-linker.yml (MVP)
        |
        v
pr-labeler.yml (MVP) -----> changelog-enforcer.yml (Phase 2)
        |                           |
        v                           v
dbt-test.yml (MVP) ---------> dbt-docs-generator.yml (Phase 3)
        |
        v
merge-notify.yml (Phase 4) --> release-notes.yml (Phase 4)

secrets-scanner.yml (Phase 3) -- independent
wip-detector.yml (Phase 3) -- independent
lint-check.yml (Phase 3) -- independent (advisory)
agent-tracker.yml (Phase 2) -- independent (see design questions)
stale-pr-notifier.yml (Phase 2) -- independent
pr-size-analyzer.yml (Phase 2) -- independent
admin-audit.yml (Phase 4) -- independent
```

---

## Success Criteria

### MVP Complete

- [ ] Invalid PR titles block merge
- [ ] PRs without linked issues block merge
- [ ] PRs auto-labeled by type and size
- [ ] dbt test failures block merge

### Phase 2 Complete

- [ ] feat/fix PRs require CHANGELOG (with bypass option)
- [ ] Agent reports summarized in PR comments
- [ ] Stale PRs receive notifications
- [ ] Large PRs receive split suggestions

### Phase 3 Complete

- [ ] Secrets in code block merge
- [ ] WIP markers block non-draft PRs
- [ ] Lint violations annotated (advisory)
- [ ] dbt docs generated on main push

### Phase 4 Complete

- [ ] All merges to main logged
- [ ] Tagged releases auto-documented
- [ ] Weekly admin audit reports generated

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| dbt-test CI slowdown | Medium | High | Cache uv dependencies, use in-memory DuckDB |
| False positive secrets | Medium | Medium | Configure .trufflehogignore, tune patterns |
| Issue linker too strict | Medium | Medium | Allow "Related to" as soft link |
| Agent tracker complexity | Medium | Medium | Start with simple summary, iterate |

---

## Open Questions

1. **Agent Tracker Design**: How should agent reports persist after PR merge? See `temp/AGENT_TRACKER_DESIGN_QUESTIONS.md`

2. **GitHub-MCP Integration**: Could GitHub-MCP automate review posting without human approval for each API call?

3. **dbt Test Data Seeding**: Should CI seed full Synthea data or use a minimal subset?

---

## Related Documentation

- [ENFORCEMENT_PLAN.md](/Users/cmbays/Documents/claude/dbt-playground/temp/ENFORCEMENT_PLAN.md) - Branch protection and validation design
- [GITHUB_ACTIONS_STRATEGY.md](/Users/cmbays/Documents/claude/dbt-playground/temp/GITHUB_ACTIONS_STRATEGY.md) - Technical implementation details
- [git-workflow.md](/Users/cmbays/Documents/claude/dbt-playground/.claude/rules/git-workflow.md) - Git conventions

---

*Last Updated: 2026-01-31*
*Status: Planning - Ready for MVP Implementation*
