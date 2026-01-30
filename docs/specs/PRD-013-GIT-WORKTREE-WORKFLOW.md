---
title: Git Worktree Workflow
prd_number: PRD-013
epic: E12-Developer-Experience
version: 1.0.0
status: draft
author: pm
created: 2026-01-29
last_updated: 2026-01-29
---

## Overview

### Problem Statement

When running multiple Claude Code sessions (3+ terminals) simultaneously, each working on different features, all sessions share the same working directory. This creates conflicts:

1. **Branch conflicts**: One session switches branches while another is mid-work
2. **Uncommitted changes**: Session A's changes block Session B's branch switch
3. **State confusion**: Claude cannot reliably know which branch/feature it is working on
4. **Lost context**: Switching branches loses in-progress work from other sessions

This makes parallel "team" development inefficient and error-prone.

### Goal

Enable parallel development workflows where each Claude Code session operates in an isolated git worktree with its own branch, directory, and tracked state. Sessions can work independently without interfering with each other.

### Success Metrics

- 3+ Claude sessions can work simultaneously without branch/file conflicts
- Each session maintains awareness of its assigned worktree and feature
- Draft PRs created at worktree creation for visibility
- Clear workflow for creating, using, and cleaning up worktrees
- Documentation enables Chris to understand and manage worktrees

---

## User Stories

### US-1: Independent Session Work

**As a** user running multiple Claude Code sessions
**I want** each session to work in its own isolated directory
**So that** I can have parallel teams working on different features without conflicts

**Acceptance Criteria**:

- [ ] Each worktree has its own directory (e.g., `../dbt-playground-tuva/`)
- [ ] Each worktree is tied to a specific feature branch
- [ ] Sessions can build/test without affecting other sessions
- [ ] Switching focus between sessions does not lose work

### US-2: Session State Awareness

**As** Claude working in a session
**I want** to know which worktree/branch I am in and what task I am working on
**So that** I can maintain context and make appropriate commits

**Acceptance Criteria**:

- [ ] Worktree state is discoverable (via git worktree list or state file)
- [ ] Current branch and feature scope are clear
- [ ] Progress tracking per worktree (WORKFLOW_STATE.md or similar)
- [ ] Claude can report which "team" it is operating as

### US-3: Visibility Through Draft PRs

**As a** user managing multiple parallel features
**I want** a draft PR created when a worktree/branch is created
**So that** I can see all in-progress work in GitHub and track progress

**Acceptance Criteria**:

- [ ] Draft PR created with feature description at worktree setup
- [ ] PR title includes feature/worktree identifier
- [ ] PR body includes scope and acceptance criteria
- [ ] Commits push to branch and appear in PR

### US-4: Learning and Management

**As** Chris (the user)
**I want** to understand how worktrees work and how to manage them
**So that** I can set up, monitor, and clean up parallel development

**Acceptance Criteria**:

- [ ] FOR_CHRIS learning doc explains worktree concepts
- [ ] Commands for creating/listing/removing worktrees documented
- [ ] Best practices for worktree naming and branch management
- [ ] Cleanup procedures for completed features

---

## Requirements

### Functional Requirements

#### FR-1: Worktree Naming Convention

**Priority**: P0 (Critical)

Worktrees must follow a consistent naming pattern for discoverability.

**Specification**:

| Component | Pattern | Example |
|-----------|---------|---------|
| Directory | `dbt-playground-{track}` | `dbt-playground-tuva` |
| Location | Sibling to main repo | `../dbt-playground-tuva/` |
| Branch | `feat/{track}-{feature}` or `feat/{track}` | `feat/tuva-connectors` |

**Track Names** (suggested):

- `tuva` - Tuva integration work
- `marts` - Dimensional models / marts
- `docs` - Documentation improvements
- `infra` - Infrastructure / tooling
- `fix` - Bug fixes

#### FR-2: Branch Naming Tied to Worktree

**Priority**: P0 (Critical)

Each worktree must have a dedicated branch that is not used elsewhere.

**Rules**:

- One branch per worktree (enforced by git)
- Branch created at worktree creation time
- Branch name includes track identifier
- Branch pushed to origin for PR creation

#### FR-3: Draft PR at Worktree Creation

**Priority**: P1 (High)

When creating a worktree, immediately create a draft PR for visibility.

**Workflow**:

```bash
# 1. Create worktree with new branch
git worktree add ../dbt-playground-tuva -b feat/tuva-connectors

# 2. Navigate to worktree
cd ../dbt-playground-tuva

# 3. Push branch and create draft PR
git push -u origin feat/tuva-connectors
gh pr create --draft --title "feat(tuva): Tuva connector models" \
  --body "## Scope\n- [ ] Patient connector\n- [ ] Encounter connector\n..."
```

#### FR-4: Commit Granularity

**Priority**: P1 (High)

Work in worktrees should follow commit-per-model or commit-per-feature granularity for clean history.

**Guidelines**:

- One commit per model file (for new models)
- One commit per logical change (for modifications)
- Meaningful commit messages following conventional commits
- Regular pushes to keep PR updated

#### FR-5: State Tracking

**Priority**: P2 (Medium)

Each worktree should have a way to track progress and current focus.

**Options**:

| Option | Location | Pros | Cons |
|--------|----------|------|------|
| Per-worktree file | `WORKFLOW_STATE.md` in each worktree | Isolated, travels with worktree | Not visible from main |
| Centralized file | `temp/WORKTREE_STATE.md` in main | Single view of all work | Merge conflicts possible |
| PR description | GitHub PR body | Visible to all, no file | Requires GitHub access |

**Recommendation**: Use PR description as source of truth with optional local `WORKFLOW_STATE.md` for Claude context.

#### FR-6: Supervisor/Orchestrate Worktree Awareness

**Priority**: P2 (Medium)

The supervisor agent should be aware of worktrees and able to assign work appropriately.

**Capabilities**:

- List active worktrees and their branches
- Identify which session is which worktree
- Route tasks to appropriate worktree/session
- Prevent conflicting assignments

---

### Non-Functional Requirements

#### NFR-1: Minimal Setup Overhead

Creating a worktree should be quick (under 2 minutes including PR creation).

#### NFR-2: No Interference with Main Repo

Worktrees should not affect the main repository state. Work in a worktree should not block work in main or other worktrees.

#### NFR-3: Clean Removal

Worktrees should be easy to clean up after merging:

```bash
# After PR merge
git worktree remove ../dbt-playground-tuva
git branch -d feat/tuva-connectors
```

---

## Scope

### In Scope

- Worktree workflow definition and naming conventions
- CLAUDE.md updates with worktree guidance
- FOR_CHRIS learning documentation
- Supervisor awareness of worktrees (documentation)
- Draft PR workflow integration

### Out of Scope

- Automated worktree management scripts (future enhancement)
- Worktree-aware IDE configuration
- CI/CD changes for worktree branches
- Cross-worktree dependency management

---

## Implementation Plan

### Phase 1: Documentation (This PRD)

1. Define worktree conventions (this document)
2. Create GitHub issues for implementation work
3. Get approval on workflow

### Phase 2: Documentation Updates

1. Update CLAUDE.md with worktree section
2. Create FOR_CHRIS learning document
3. Update git-master agent with worktree commands

### Phase 3: Supervisor Integration

1. Update supervisor persona with worktree awareness
2. Document orchestration with multiple worktrees
3. Test parallel session workflow

---

## Workflow Examples

### Example 1: Setting Up a New Feature Track

```bash
# In main repo directory
cd /Users/cmbays/Documents/claude/dbt-playground

# Create worktree for Tuva work
git worktree add ../dbt-playground-tuva -b feat/tuva-connectors main

# Navigate to new worktree
cd ../dbt-playground-tuva

# Verify setup
git status  # Shows on feat/tuva-connectors

# Push branch and create draft PR
git push -u origin feat/tuva-connectors
gh pr create --draft \
  --title "feat(tuva): Tuva connector models" \
  --body "## Overview
Implement Tuva connector models for clinical data.

## Scope
- [ ] int_tuva__patient
- [ ] int_tuva__encounter
- [ ] int_tuva__condition
- [ ] Tests and documentation

## Context
Track: tuva
Worktree: ../dbt-playground-tuva"
```

### Example 2: Working in a Worktree Session

```bash
# Claude starts in worktree
pwd
# /Users/cmbays/Documents/claude/dbt-playground-tuva

# Check current state
git worktree list
# /Users/cmbays/Documents/claude/dbt-playground       abc1234 [main]
# /Users/cmbays/Documents/claude/dbt-playground-tuva  def5678 [feat/tuva-connectors]

# Work on feature
uv run dbt run --select int_tuva__patient

# Commit and push
git add models/intermediate/tuva/
git commit -m "feat(tuva): add int_tuva__patient connector"
git push
```

### Example 3: Cleaning Up After Merge

```bash
# After PR is merged to main
cd /Users/cmbays/Documents/claude/dbt-playground

# Update main
git checkout main
git pull

# Remove worktree
git worktree remove ../dbt-playground-tuva

# Delete local branch (remote deleted via PR merge)
git branch -d feat/tuva-connectors

# Verify
git worktree list
# /Users/cmbays/Documents/claude/dbt-playground  abc1234 [main]
```

---

## Open Questions

1. **Q**: Should we have a maximum number of concurrent worktrees?
   **A**: Recommend 3-4 max to keep mental model manageable.

2. **Q**: How does dbt work across worktrees with shared database?
   **A**: DuckDB file is per-worktree (gitignored), so no conflicts. Each worktree has its own dev.duckdb.

3. **Q**: Should worktree state be committed?
   **A**: No - worktree state is ephemeral. PR description is the source of truth.

4. **Q**: How do we handle dependencies between worktrees?
   **A**: Avoid cross-dependencies. If worktree B needs changes from A, merge A first.

---

## Dependencies

### Upstream

- Git worktree support (built into git)
- GitHub CLI (gh) for PR creation

### Downstream

- All future parallel development work
- Supervisor orchestration

---

## Related

- **GitHub Issues**: See GITHUB-ISSUES.md Epic 12
- **Learning Doc**: docs/for_chris/GIT_WORKTREES.md (to be created)
- **CLAUDE.md**: To be updated with worktree section

---

*PRD Status: Draft - Awaiting Review*
