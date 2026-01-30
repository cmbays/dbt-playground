# PRD-015: PR-Centric Development Workflow Enhancement

## Overview

**Author**: Claude Code Agent System
**Status**: Complete
**Created**: 2026-01-29
**Updated**: 2026-01-29

### Problem Statement

The current development workflow has several gaps that reduce visibility and context preservation:

1. Development context is not captured early in git history
2. Reviews produce local output only, not captured in PRs
3. Single reviewer is a quality bottleneck
4. Post-review updates (docs, learnings, PM) happen after merge or are forgotten
5. No formal approval gate before merge
6. Cross-session visibility is limited

### Goal

Establish a PR-centric development workflow where:

- Development context is captured from the start via draft PRs
- Multiple review agents comment directly on PRs
- Post-review updates (docs, sage, PM) happen before merge
- Supervisor provides final approval gate
- Cross-session visibility through git/PR history

## User Stories

As a **developer**, I want draft PRs created automatically so that my work is visible from the start.

As a **code reviewer**, I want to post comments directly to GitHub PRs so that feedback is captured in the audit trail.

As a **supervisor**, I want to orchestrate multi-agent reviews so that quality is ensured through multiple perspectives.

As a **documenter**, I want to commit updates to PR branches so that changelog entries are part of the PR history.

As a **sage**, I want to extract learnings from PRs so that patterns are captured while context is fresh.

As a **cross-session agent**, I want to see development context via `gh pr view` so that I can understand work in progress.

## Requirements

### Functional Requirements

1. **FR-1**: Git-master creates draft PR at branch/worktree creation (--with-pr default on)
2. **FR-2**: Code Reviewer posts inline comments and summary reviews to GitHub PRs
3. **FR-3**: Security Reviewer posts security findings to GitHub PRs
4. **FR-4**: Supervisor orchestrates multi-agent reviews and monitors approval count
5. **FR-5**: Supervisor requires 2+ approvals before proceeding to post-review queue
6. **FR-6**: Post-review queue runs docs→sage→pm agents, committing to PR branch
7. **FR-7**: Supervisor performs final approval checklist before authorizing merge
8. **FR-8**: Git-master enforces approval gate (no merge without super: APPROVED)
9. **FR-9**: Git-master auto-cleans up worktree and branch after merge

### Non-Functional Requirements

1. **NFR-1**: All review comments must be captured in GitHub PR history
2. **NFR-2**: Workflow must support parallel work via git worktrees
3. **NFR-3**: Cross-session agents can read context via `gh pr view`

## Acceptance Criteria

- [x] `/branch` creates draft PR by default
- [x] `/review --pr N` posts review to GitHub PR
- [x] Supervisor can orchestrate Code + Security + Design reviews
- [x] Supervisor monitors for 2+ approvals
- [x] Post-review queue documented with agent invocation templates
- [x] Supervisor final approval checklist defined
- [x] Git-master blocks merge without supervisor approval
- [x] Auto-cleanup workflow defined for post-merge

## Scope

### In Scope

- Agent persona updates (git-master, supervisor, code-reviewer, security-reviewer, documenter, sage)
- Command updates (branch, review)
- New workflow file (post-review-queue.md)
- GitHub CLI integration for PR comments and reviews

### Out of Scope

- Automated CI/CD integration
- GitHub Actions configuration
- Branch protection rule changes
- Automated testing before merge

## Dependencies

- GitHub CLI (`gh`) installed and authenticated
- Git worktree support (git >= 2.7)
- Existing agent system infrastructure

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| PR context captured | 100% of features | All branches have draft PR |
| Reviews in PR history | 100% | All reviews posted via gh CLI |
| Multi-reviewer coverage | 2+ approvals | Supervisor tracks approval count |
| CHANGELOG in PR | 100% of feat/fix | Post-review queue commits |

## Implementation Summary

### Files Modified

| File | Change |
|------|--------|
| `.claude/agents/git-master.md` | PR-first workflow, approval gate, auto-cleanup |
| `.claude/agents/supervisor.md` | Review orchestration, post-review queue, final approval |
| `.claude/agents/code-reviewer.md` | PR comment posting via gh CLI |
| `.claude/agents/security-reviewer.md` | PR security review posting |
| `.claude/agents/documenter.md` | PR-commit mode for changelog |
| `.claude/agents/sage.md` | PR learning extraction |
| `.claude/commands/branch.md` | --with-pr flag (default on) |
| `.claude/commands/review.md` | --pr flag for GitHub posting |

### Files Created

| File | Purpose |
|------|---------|
| `.claude/workflows/post-review-queue.md` | Post-review agent queue definition |

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| PR comment format | Inline + summary | Better code context with line-specific feedback |
| Approval tracking | GitHub native reviews | Uses `gh pr review --approve/--request-changes` |
| Sage frequency | On request or milestones | Avoids noise, focuses on meaningful learnings |
| Worktree cleanup | Auto after merge | Git-master removes worktree + branch when PR merges |

## Related

- **Workflow**: `.claude/workflows/post-review-queue.md`
- **Rules**: `.claude/rules/git-workflow.md`
- **Agents**: All modified agent personas
