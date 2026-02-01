# PRD-005: GitHub Integration Enhancements

**Product Requirements Document**
**Version**: 1.0
**Date**: 2026-02-01
**Status**: Draft

---

## Document Metadata

| Field | Value |
|-------|-------|
| PRD ID | PRD-005 |
| Title | GitHub Integration Enhancements |
| Author | Product Manager Agent |
| Owner | @cmbays |
| Related Issues | TBD (#140 Epic) |
| Milestone | v0.8 |
| Priority | P1 |

---

## 1. Problem Statement

### 1.1 Background

The dbt-playground project has established solid GitHub automation foundations:

- 5 active GitHub Actions workflows (PR validation, issue linking, labeling, dbt tests, project automation)
- `github-ops.py` CLI for issue and milestone management
- PR-Issue linking with closing and related keywords
- GitHub Projects integration for roadmap tracking

However, several gaps remain that limit traceability, increase manual overhead, and prevent automated workflows from reaching their full potential.

### 1.2 Problems to Solve

#### Problem 1: Incomplete Traceability Chain

**Current State**: PRs link to issues, but there is no structured way to trace from:

- PRD documents to GitHub Epic issues
- Epic issues to child Task issues
- Task files in the backlog to their corresponding GitHub issues

**Impact**:

- Cannot answer "which PRD drove this feature?" without manual digging
- No way to see all implementation tasks for a given Epic
- Audit trail gaps between planning docs and code changes

#### Problem 2: Task File Naming Mismatch

**Current State**: Task files use sequential numbers (`task-1`, `task-2`, etc.) that have no relationship to GitHub issue IDs.

**Impact**:

- Cannot easily find the task file for GitHub issue #137
- Manual mapping required when converting issues to tasks
- Automation blocked (cannot auto-create task files)

#### Problem 3: No Code Ownership

**Current State**: No CODEOWNERS file exists. PRs do not automatically request reviewers based on changed files.

**Impact**:

- PRs may sit unreviewed
- No clear responsibility for code areas
- No enforcement of domain expertise review

#### Problem 4: Manual Task Management

**Current State**: Task files must be manually created, named, and archived when issues change state.

**Impact**:

- Time spent on administrative work
- Risk of task files becoming stale or orphaned
- Inconsistent task file content and metadata

### 1.3 Out of Scope Problems (Deferred)

The following problems were identified in research but are explicitly out of scope for v0.8:

| Problem | Reason for Deferral |
|---------|---------------------|
| Separate bot accounts for agents | GitHub ToS complexity, minimal value for single-developer project |
| Native sub-issue hierarchy | GitHub has no API support; text-based solutions are fragile |
| Complex approval matrices | Single-owner project does not need multi-tier review |
| External DQ tools (Great Expectations, Soda) | Separate initiative, may be v1.0 |

---

## 2. User Stories and Use Cases

### 2.1 Primary Personas

| Persona | Role | Primary Need |
|---------|------|--------------|
| Chris (cmbays) | Project Owner | Clear traceability, minimal manual work |
| Claude Agents | Development Assistants | Structured metadata for coordination |
| Future Contributors | External Collaborators | Clear code ownership, easy onboarding |

### 2.2 User Stories

#### US-1: As a project owner, I want PRDs to link to GitHub issues so that I can trace features from planning to implementation

**Acceptance Criteria**:

- PRD YAML frontmatter includes `related_issues` field with issue numbers
- PRD frontmatter includes `epic_issue` field for the primary Epic
- GitHub Epic issues include `PRD:` reference in body

**Priority**: P1

---

#### US-2: As a project owner, I want task files named by GitHub issue ID so that I can find them easily

**Acceptance Criteria**:

- New task files use `issue-{N}.md` naming pattern
- Task YAML frontmatter includes `github_issue` field
- Documentation updated with new convention
- Existing task files remain unchanged (backwards compatibility)

**Priority**: P1

---

#### US-3: As a project owner, I want automatic reviewer assignment so that PRs don't sit unreviewed

**Acceptance Criteria**:

- CODEOWNERS file maps file paths to reviewers
- PRs automatically request review from code owners
- dbt model layers have explicit ownership

**Priority**: P1

---

#### US-4: As a Claude agent, I want task files auto-created when issues are opened so that I can start work immediately

**Acceptance Criteria**:

- GitHub Action creates task file when issue opened with `task` label
- Task file contains YAML frontmatter with issue metadata
- Task file archived when issue closed

**Priority**: P2 (Phase 2)

---

#### US-5: As a project owner, I want branch protection so that unreviewed code cannot merge to main

**Acceptance Criteria**:

- Main branch requires PR review before merge
- Status checks must pass (dbt-test, pr-validation)
- CODEOWNERS approval required for affected paths

**Priority**: P2 (Phase 2)

---

#### US-6: As a future contributor, I want clear code ownership so that I know who to ask about specific areas

**Acceptance Criteria**:

- CODEOWNERS file documents all code areas
- Documentation explains ownership model
- GitHub UI shows code owners on PRs

**Priority**: P1

---

### 2.3 Use Cases

#### UC-1: Creating a New Feature from PRD

**Actor**: Chris (with Claude agents)
**Precondition**: PRD document exists in `docs/specs/`
**Flow**:

1. Chris creates Epic issue referencing PRD in body
2. PRD frontmatter updated with `epic_issue` field
3. Child task issues created, each referencing Epic
4. Task files auto-created for each task issue (Phase 2)
5. Developers implement features, referencing issues in commits
6. PRs reference task/Epic issues, auto-close on merge

**Postcondition**: Full traceability from PRD to merged code

---

#### UC-2: Reviewing a PR

**Actor**: Chris (as reviewer)
**Precondition**: PR opened by Claude agent
**Flow**:

1. GitHub requests review from CODEOWNERS
2. PR Labeler applies type, size, and layer labels
3. Issue Linker validates issue references
4. dbt-test workflow runs build and tests
5. Reviewer approves PR
6. Branch protection allows merge
7. Related issues auto-closed

**Postcondition**: Quality-assured code merged with full audit trail

---

#### UC-3: Finding Implementation Details for a Feature

**Actor**: Chris (or future contributor)
**Precondition**: Feature was implemented via this workflow
**Flow**:

1. Start from PRD document
2. Follow `epic_issue` link to GitHub Epic
3. View child issues listed in Epic body
4. Navigate to specific task issue
5. Find task file via `issue-{N}.md` naming
6. View PR that closed the task
7. Browse commits in that PR

**Postcondition**: Full understanding of feature implementation

---

## 3. Functional Requirements

### FR-1: CODEOWNERS File

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Create `.github/CODEOWNERS` file | P1 |
| FR-1.2 | Map all dbt model directories to owner (@cmbays) | P1 |
| FR-1.3 | Map infrastructure files (.github/, .claude/, scripts/) to owner | P1 |
| FR-1.4 | Map documentation (docs/, *.md) to owner | P1 |
| FR-1.5 | Map configuration files (pyproject.toml, dbt_project.yml) to owner | P1 |
| FR-1.6 | Verify file syntax is valid for GitHub | P1 |

---

### FR-2: Task File Naming Convention

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | Define new naming pattern: `issue-{N}.md` or `{N}-short-title.md` | P1 |
| FR-2.2 | Update task template to use new pattern | P1 |
| FR-2.3 | Add `github_issue` field to task YAML frontmatter schema | P1 |
| FR-2.4 | Document new convention in CLAUDE_TASK_INTEGRATION.md | P1 |
| FR-2.5 | Create migration guide for existing tasks | P2 |
| FR-2.6 | Preserve existing sequential-named files (no breaking changes) | P1 |

---

### FR-3: PRD-to-Issue Traceability

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | Add `related_issues` array field to PRD YAML frontmatter | P1 |
| FR-3.2 | Add `epic_issue` field to PRD YAML frontmatter | P1 |
| FR-3.3 | Update PRD template with new fields | P1 |
| FR-3.4 | Add `PRD:` reference field to GitHub issue template (Epic type) | P1 |
| FR-3.5 | Add `Child Issues:` list field to GitHub issue template (Epic type) | P1 |
| FR-3.6 | Document traceability conventions in GITHUB_ENFORCEMENT.md | P1 |

---

### FR-4: Task File Sync Automation (Phase 2)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Create workflow triggered on `issues: opened` event | P2 |
| FR-4.2 | Create workflow triggered on `issues: closed` event | P2 |
| FR-4.3 | Filter to only process issues with `task` label | P2 |
| FR-4.4 | Auto-create task file at `backlog/tasks/issue-{N}.md` | P2 |
| FR-4.5 | Populate task file with frontmatter from issue metadata | P2 |
| FR-4.6 | Auto-archive task file on close (move to `backlog/archive/`) | P2 |
| FR-4.7 | Commit changes with descriptive message | P2 |

---

### FR-5: Branch Protection (Phase 2)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1 | Require pull request reviews (minimum 1) | P2 |
| FR-5.2 | Require CODEOWNERS approval | P2 |
| FR-5.3 | Require status checks to pass (dbt-test, pr-validation) | P2 |
| FR-5.4 | Require branches to be up to date before merging | P2 |
| FR-5.5 | Do NOT restrict who can push to main (Claude needs access) | P2 |
| FR-5.6 | Document emergency bypass procedure | P2 |

---

## 4. Non-Functional Requirements

### NFR-1: ToS Compliance

| ID | Requirement | Rationale |
|----|-------------|-----------|
| NFR-1.1 | Do not create multiple GitHub accounts for agents | GitHub ToS prohibits multiple accounts per person |
| NFR-1.2 | Use Co-authored-by for agent attribution | Compliant alternative to separate accounts |
| NFR-1.3 | Personal access tokens only for cmbays account | Single authenticated user |

### NFR-2: Maintainability

| ID | Requirement | Rationale |
|----|-------------|-----------|
| NFR-2.1 | CODEOWNERS file must be simple and obvious | Easy to update as project grows |
| NFR-2.2 | Task file automation must be opt-in (via label) | Prevent unwanted file creation |
| NFR-2.3 | All conventions documented in reference docs | Onboarding and consistency |
| NFR-2.4 | Workflows must log clearly for debugging | Troubleshooting failed runs |

### NFR-3: Backwards Compatibility

| ID | Requirement | Rationale |
|----|-------------|-----------|
| NFR-3.1 | Existing task files must continue to work | No breaking changes |
| NFR-3.2 | Existing PRDs valid without new fields | Gradual adoption |
| NFR-3.3 | Branch protection must allow emergency bypass | Cannot be locked out |

### NFR-4: Performance

| ID | Requirement | Rationale |
|----|-------------|-----------|
| NFR-4.1 | Task sync workflow completes in < 30 seconds | Fast feedback loop |
| NFR-4.2 | Traceability validation adds < 5 seconds to issue-linker | Minimal overhead |
| NFR-4.3 | Monitor GitHub API rate limits | 5000 requests/hour limit |

---

## 5. Acceptance Criteria

### Phase 1 Acceptance Criteria

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-1.1 | CODEOWNERS file exists at `.github/CODEOWNERS` | File inspection |
| AC-1.2 | PRs automatically request review from @cmbays | Open PR, verify review request |
| AC-1.3 | New task files use `issue-{N}.md` naming | Create task from issue |
| AC-1.4 | Task template includes `github_issue` frontmatter | Template inspection |
| AC-1.5 | CLAUDE_TASK_INTEGRATION.md documents new naming | Doc review |
| AC-1.6 | At least one PRD has `epic_issue` field populated | File inspection |
| AC-1.7 | GitHub Epic issue template includes PRD reference | Template inspection |
| AC-1.8 | Existing task files unchanged and functional | TaskList verification |

### Phase 2 Acceptance Criteria

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-2.1 | Task file auto-created when issue opened with `task` label | Open issue, check backlog/ |
| AC-2.2 | Task file moved to archive when issue closed | Close issue, check archive/ |
| AC-2.3 | Workflow logs issue details correctly | Workflow run output |
| AC-2.4 | Branch protection requires PR review | Try direct push (should fail) |
| AC-2.5 | Branch protection requires status checks | PR without passing checks (should block) |
| AC-2.6 | Emergency bypass documented | Doc review |

---

## 6. Out of Scope

The following items are explicitly out of scope for this PRD:

| Item | Reason | Future Consideration |
|------|--------|---------------------|
| Separate GitHub accounts per agent | ToS compliance, infrastructure complexity | v1.0+ if GitHub Apps needed |
| gh-sub-issue extension adoption | Current task list pattern sufficient | v0.9 evaluation |
| Label-based reviewer routing | Single-owner project | v1.0+ with team growth |
| External DQ tool integration | Separate initiative | v1.0 |
| GitHub Projects V2 custom fields | Current automation sufficient | v0.9 if needed |
| Real-time Slack notifications | No Slack integration currently | v1.0+ |
| Automated milestone creation | Manual milestone management sufficient | v0.9 |

---

## 7. Dependencies

### External Dependencies

| Dependency | Type | Risk |
|------------|------|------|
| GitHub CODEOWNERS feature | Platform | Low (stable feature) |
| GitHub Actions | Platform | Low (already in use) |
| GitHub API rate limits | Platform | Medium (monitor usage) |
| gh CLI | Tool | Low (already in use) |

### Internal Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| docs/guides/CLAUDE_TASK_INTEGRATION.md | Documentation | Exists, needs update |
| docs/reference/GITHUB_ENFORCEMENT.md | Documentation | Exists, needs update |
| backlog/tasks/ directory | Directory | Exists |
| Issue templates | Templates | May need creation |

---

## 8. Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| PRD-to-Issue traceability | 0% | 100% (new PRDs) | PRD frontmatter has epic_issue |
| Task files with github_issue | ~0% | 100% (new tasks) | Frontmatter field present |
| PRs with auto-assigned reviewer | 0% | 100% | CODEOWNERS active |
| Manual task file creation | All | Zero (new issues) | Workflow automation |
| Unreviewed PRs merged | Unknown | 0% | Branch protection |

---

## 9. Timeline and Milestones

| Phase | Target | Deliverables |
|-------|--------|--------------|
| Phase 1 | v0.8.1 (Week 1) | CODEOWNERS, task naming, PRD traceability |
| Phase 2 | v0.8.2 (Week 2-3) | Task sync workflow, branch protection |
| Phase 3 | v0.9+ | Advanced features (evaluation only) |

---

## 10. Open Questions

| ID | Question | Owner | Status |
|----|----------|-------|--------|
| Q1 | Should task files include full issue body or just metadata? | PM | Open |
| Q2 | What labels trigger task file creation? Just `task` or also `enhancement`? | PM | Open |
| Q3 | Should archived tasks retain issue metadata for searchability? | PM | Open |
| Q4 | How to handle issues without milestone (should they get task files)? | PM | Open |

---

## 11. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-01 | PM Agent | Initial draft |

---

*Document created: 2026-02-01*
*Author: Product Manager Agent*
