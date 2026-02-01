# TDD-005: GitHub Integration Enhancements

**Technical Design Document**
**Version**: 1.0
**Date**: 2026-02-01
**Status**: Draft

---

## Document Metadata

| Field | Value |
|-------|-------|
| TDD ID | TDD-005 |
| Title | GitHub Integration Enhancements |
| Author | Technical Architect Agent |
| Related PRD | PRD-005-GitHub-Integration.md |
| Epic Issue | TBD (#140) |
| Milestone | v0.8 |

---

## 1. Architecture Overview

### 1.1 System Context

This design integrates with the existing GitHub automation infrastructure:

```
+------------------+     +------------------+     +------------------+
|   PRD Documents  |---->|  GitHub Issues   |---->|   Task Files     |
|   (docs/specs/)  |     |  (Epic/Task)     |     |  (backlog/tasks/)|
+------------------+     +------------------+     +------------------+
        |                        |                        |
        v                        v                        v
+------------------+     +------------------+     +------------------+
|  GitHub Actions  |<----|   Pull Requests  |---->|   Code Changes   |
|  (Workflows)     |     |   (feat/fix)     |     |   (models/)      |
+------------------+     +------------------+     +------------------+
        |                        |
        v                        v
+------------------+     +------------------+
|   CODEOWNERS     |     |  Branch          |
|   (review)       |     |  Protection      |
+------------------+     +------------------+
```

### 1.2 Component Overview

| Component | Purpose | New/Existing |
|-----------|---------|--------------|
| CODEOWNERS | Reviewer assignment | New |
| Task file naming | Issue-ID correlation | Modified |
| PRD metadata | Traceability links | Modified |
| Task sync workflow | Auto file management | New |
| Branch protection | Merge gates | New (config) |

### 1.3 Design Principles

1. **Additive changes only** - No breaking changes to existing files
2. **Opt-in automation** - Label-triggered, not blanket automation
3. **Clear conventions** - Documented patterns over implicit behavior
4. **Single source of truth** - GitHub issues are authoritative; task files are derived

---

## 2. Detailed Design

### 2.1 CODEOWNERS File Design

**Location**: `.github/CODEOWNERS`

**Design Rationale**:

- GitHub parses CODEOWNERS from root or `.github/` directory
- More specific patterns override less specific (last match wins)
- Use glob patterns for directory matching

**File Structure**:

```
# .github/CODEOWNERS
# Code Owners for dbt-playground
# Last match wins - order from general to specific

# =============================================================================
# DEFAULT OWNER
# =============================================================================
# Catch-all: any file not matched below
* @cmbays

# =============================================================================
# DBT MODELS (by layer)
# =============================================================================
# Staging layer - source transformations
dbt_project/models/staging/** @cmbays

# Intermediate layer - business logic
dbt_project/models/intermediate/** @cmbays

# Marts layer - dimensional models
dbt_project/models/marts/** @cmbays

# Analytics layer - reporting models
dbt_project/models/analytics/** @cmbays

# =============================================================================
# DBT CONFIGURATION
# =============================================================================
dbt_project/dbt_project.yml @cmbays
dbt_project/packages.yml @cmbays
dbt_project/profiles.yml @cmbays
dbt_project/macros/** @cmbays
dbt_project/tests/** @cmbays
dbt_project/seeds/** @cmbays

# =============================================================================
# INFRASTRUCTURE
# =============================================================================
# GitHub Actions and automation
.github/** @cmbays

# Claude agent configuration
.claude/** @cmbays

# Python scripts
scripts/** @cmbays

# =============================================================================
# DOCUMENTATION
# =============================================================================
docs/** @cmbays
*.md @cmbays
CHANGELOG.md @cmbays

# =============================================================================
# PROJECT CONFIGURATION
# =============================================================================
pyproject.toml @cmbays
uv.lock @cmbays
.python-version @cmbays
.gitignore @cmbays

# =============================================================================
# BACKLOG AND PLANNING
# =============================================================================
backlog/** @cmbays
temp/** @cmbays
playgrounds/** @cmbays
```

**Validation**:

- GitHub validates syntax on push
- Run `gh api repos/{owner}/{repo}/codeowners/errors` to check for errors

---

### 2.2 Task File Naming Migration Strategy

#### 2.2.1 Current State Analysis

**Existing Files** (11 task files):

```
backlog/tasks/
  task-2 - API-Test-Task.md
  task-3 - Phase-1.3-Test-session-heartbeat-workflow.md
  ...
  task-12 - E2E-Test-Multi-worktree-task-visibility.md
```

**Naming Pattern**: `task-{N} - {Title-With-Dashes}.md`

**Issues**:

- Sequential `{N}` does not match GitHub issue IDs
- Spaces in filenames complicate scripting
- No machine-readable link to GitHub

#### 2.2.2 New Naming Convention

**Pattern Options** (choose one):

| Option | Pattern | Example | Pros | Cons |
|--------|---------|---------|------|------|
| A | `issue-{N}.md` | `issue-137.md` | Simple, scriptable | No context in filename |
| B | `{N}-{slug}.md` | `137-add-codeowners.md` | Context + ID | Slug generation needed |
| C | `{N}.md` | `137.md` | Minimal | No context |

**Recommendation**: **Option A** (`issue-{N}.md`) for simplicity and automation.

- Filename is entirely machine-derived from issue number
- No slug generation or truncation logic
- Context lives in file frontmatter and issue body

#### 2.2.3 Migration Path

**Phase 1: Parallel Patterns (v0.8.1)**

1. Do NOT rename existing files
2. New files use `issue-{N}.md` pattern
3. Add `github_issue` to existing files opportunistically

**File Detection Logic**:

```bash
# Detect file format
if [[ "$filename" =~ ^issue-([0-9]+)\.md$ ]]; then
    # New format - extract issue number
    issue_num="${BASH_REMATCH[1]}"
elif [[ "$filename" =~ ^task-([0-9]+) ]]; then
    # Old format - check frontmatter for github_issue
    issue_num=$(grep '^github_issue:' "$file" | awk '{print $2}')
fi
```

**Phase 2: Optional Bulk Migration (v0.9+)**

If desired, create migration script:

```bash
#!/bin/bash
# migrate-task-files.sh
# Renames task-N files to issue-{github_issue}.md if frontmatter exists

for file in backlog/tasks/task-*.md; do
    issue=$(yq '.github_issue' "$file" 2>/dev/null)
    if [[ -n "$issue" && "$issue" != "null" ]]; then
        mv "$file" "backlog/tasks/issue-${issue}.md"
    fi
done
```

---

### 2.3 Task File YAML Schema

**Current Schema** (from `CLAUDE_TASK_INTEGRATION.md`):

```yaml
---
id: TASK-12
title: 'E2E Test: Multi-worktree task visibility'
status: UNDERSTAND
assignee: []
created_date: '2026-02-01 05:28'
labels:
  - testing
dependencies: []
priority: medium
---
```

**Enhanced Schema** (new fields):

```yaml
---
id: TASK-137                         # Keep for backwards compatibility
github_issue: 137                    # NEW: Link to GitHub issue
title: 'Add CODEOWNERS file'
status: UNDERSTAND
assignee: []
created_date: '2026-02-01 10:00'
labels:
  - enhancement
  - workflow
dependencies: []
priority: high
epic_issue: 140                      # NEW: Parent Epic (optional)
milestone: v0.8                      # NEW: Milestone (optional)
prd: docs/specs/PRD-005.md           # NEW: Related PRD (optional)
---
```

**Schema Definition** (for validation):

```yaml
# docs/schemas/task-file.schema.yaml
type: object
required:
  - id
  - title
  - status
properties:
  id:
    type: string
    pattern: "^TASK-\\d+$"
  github_issue:
    type: integer
    minimum: 1
  title:
    type: string
  status:
    type: string
    enum: [UNDERSTAND, PLAN, BUILD, VERIFY, DEPLOY, DONE, BLOCKED]
  assignee:
    type: array
    items:
      type: string
  created_date:
    type: string
  labels:
    type: array
    items:
      type: string
  dependencies:
    type: array
    items:
      type: string
  priority:
    type: string
    enum: [low, medium, high, critical]
  epic_issue:
    type: integer
  milestone:
    type: string
  prd:
    type: string
```

---

### 2.4 PRD Traceability Link Format

**Current PRD Frontmatter**:

```yaml
---
prd_id: PRD-004
title: Claude Task GitHub Integration
created: 2026-01-15
status: active
---
```

**Enhanced PRD Frontmatter**:

```yaml
---
prd_id: PRD-005
title: GitHub Integration Enhancements
created: 2026-02-01
status: active
epic_issue: 140                      # NEW: Primary Epic issue
related_issues:                      # NEW: All related issues
  - 140  # Epic
  - 141  # CODEOWNERS
  - 142  # Task naming
  - 143  # Traceability
milestone: v0.8
---
```

**GitHub Issue Body Format** (Epic template):

```markdown
## Description
[Feature description here]

## Metadata
- **PRD**: docs/specs/PRD-005-GitHub-Integration.md
- **TDD**: docs/specs/TDD-005-GitHub-Integration.md
- **Milestone**: v0.8

## Child Issues
- [ ] #141 - CODEOWNERS file
- [ ] #142 - Task file naming
- [ ] #143 - PRD traceability

## Acceptance Criteria
- [ ] AC-1: [Criterion]
- [ ] AC-2: [Criterion]
```

**Validation Workflow Enhancement**:

Add to `.github/workflows/issue-linker.yml`:

```yaml
- name: Validate PRD reference
  if: contains(github.event.pull_request.body, 'PRD:')
  run: |
    PRD_PATH=$(echo "${{ github.event.pull_request.body }}" | grep -oP 'PRD: \K[^\s]+')
    if [[ -n "$PRD_PATH" && ! -f "$PRD_PATH" ]]; then
      echo "::warning::PRD file not found: $PRD_PATH"
    fi
```

---

### 2.5 Task File Sync Workflow Design

**Workflow File**: `.github/workflows/task-file-sync.yml`

```yaml
name: Task File Sync

on:
  issues:
    types: [opened, closed, labeled, unlabeled]

permissions:
  contents: write
  issues: read

jobs:
  sync-task-file:
    runs-on: ubuntu-latest
    # Only run for issues with 'task' label
    if: contains(github.event.issue.labels.*.name, 'task')

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Create task file on issue open
        if: github.event.action == 'opened' || github.event.action == 'labeled'
        run: |
          ISSUE_NUM="${{ github.event.issue.number }}"
          TASK_FILE="backlog/tasks/issue-${ISSUE_NUM}.md"

          # Skip if file already exists
          if [[ -f "$TASK_FILE" ]]; then
            echo "Task file already exists: $TASK_FILE"
            exit 0
          fi

          # Extract issue metadata
          TITLE="${{ github.event.issue.title }}"
          CREATED="${{ github.event.issue.created_at }}"
          LABELS=$(echo '${{ toJSON(github.event.issue.labels.*.name) }}' | jq -r '.[]' | sed 's/^/  - /')
          MILESTONE="${{ github.event.issue.milestone.title }}"

          # Generate task file
          cat > "$TASK_FILE" << EOF
          ---
          id: TASK-${ISSUE_NUM}
          github_issue: ${ISSUE_NUM}
          title: '${TITLE//\'/\'\'}'
          status: UNDERSTAND
          assignee: []
          created_date: '${CREATED}'
          labels:
          ${LABELS}
          dependencies: []
          priority: medium
          milestone: ${MILESTONE:-""}
          ---

          ## Description

          <!-- Auto-generated from GitHub issue #${ISSUE_NUM} -->
          <!-- Edit in GitHub issue for single source of truth -->

          See: https://github.com/${{ github.repository }}/issues/${ISSUE_NUM}
          EOF

          echo "Created task file: $TASK_FILE"

      - name: Archive task file on issue close
        if: github.event.action == 'closed'
        run: |
          ISSUE_NUM="${{ github.event.issue.number }}"
          TASK_FILE="backlog/tasks/issue-${ISSUE_NUM}.md"
          ARCHIVE_DIR="backlog/archive/tasks"

          # Skip if file doesn't exist
          if [[ ! -f "$TASK_FILE" ]]; then
            echo "No task file to archive for issue #${ISSUE_NUM}"
            exit 0
          fi

          # Create archive directory if needed
          mkdir -p "$ARCHIVE_DIR"

          # Move to archive
          mv "$TASK_FILE" "${ARCHIVE_DIR}/issue-${ISSUE_NUM}.md"

          echo "Archived task file: ${ARCHIVE_DIR}/issue-${ISSUE_NUM}.md"

      - name: Commit changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

          git add backlog/

          if git diff --cached --quiet; then
            echo "No changes to commit"
            exit 0
          fi

          ACTION="${{ github.event.action }}"
          ISSUE_NUM="${{ github.event.issue.number }}"

          if [[ "$ACTION" == "opened" || "$ACTION" == "labeled" ]]; then
            git commit -m "chore(backlog): create task file for #${ISSUE_NUM}"
          elif [[ "$ACTION" == "closed" ]]; then
            git commit -m "chore(backlog): archive task file for #${ISSUE_NUM}"
          fi

          git push
```

**Design Decisions**:

1. **Label-triggered**: Only issues with `task` label get files
2. **Idempotent**: Checks for existing file before creating
3. **Archive on close**: Moves to `backlog/archive/` rather than deleting
4. **Minimal content**: Task file points to issue as source of truth
5. **Bot attribution**: Uses `github-actions[bot]` for commits

---

### 2.6 Branch Protection Configuration

**Configuration Method**: GitHub API via `gh` CLI

**Setup Script**:

```bash
#!/bin/bash
# configure-branch-protection.sh

OWNER="cmbays"
REPO="dbt-playground"
BRANCH="main"

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/${OWNER}/${REPO}/branches/${BRANCH}/protection" \
  -f required_status_checks='{"strict":true,"contexts":["dbt-test","pr-validation"]}' \
  -f enforce_admins=false \
  -f required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":true,"required_approving_review_count":1}' \
  -f restrictions=null \
  -f allow_force_pushes=false \
  -f allow_deletions=false
```

**Protection Rules**:

| Rule | Value | Rationale |
|------|-------|-----------|
| Required status checks | `dbt-test`, `pr-validation` | Ensure CI passes |
| Strict status checks | `true` | Branch must be up-to-date |
| Required reviews | 1 | At least one approval |
| CODEOWNERS review | `true` | Code owners must approve |
| Dismiss stale reviews | `true` | Re-approve after changes |
| Enforce admins | `false` | Allow emergency bypass |
| Force push | `false` | Protect history |

**Emergency Bypass**:

Since `enforce_admins=false`, repo admins (cmbays) can bypass protection in emergencies. Document this in `docs/reference/GITHUB_ENFORCEMENT.md`:

```markdown
## Emergency Bypass Procedure

Branch protection can be bypassed by admins in emergencies:

1. Navigate to PR
2. Click "Merge" dropdown
3. Select "Merge without waiting for requirements"
4. Document reason in PR comments

**Use sparingly** - bypasses should be rare and documented.
```

---

## 3. Implementation Sequence

### 3.1 Phase 1 Implementation Order

```
Step 1: CODEOWNERS (1-2 hrs)
   |
   v
Step 2: Task File Naming Docs (1-2 hrs)
   |
   v
Step 3: PRD Metadata Fields (2-3 hrs)
   |
   v
Step 4: Validate & Test Phase 1
```

**Step 1: CODEOWNERS**

1. Create `.github/CODEOWNERS` with content from Section 2.1
2. Open test PR to verify reviewer assignment
3. Fix any syntax errors reported by GitHub

**Step 2: Task File Naming**

1. Update `docs/guides/CLAUDE_TASK_INTEGRATION.md` with new convention
2. Create `docs/templates/task-file.md` template with new schema
3. Add `github_issue` to one existing task as proof of concept

**Step 3: PRD Metadata**

1. Update `docs/templates/prd-template.md` with new fields
2. Add metadata to PRD-005 (this feature)
3. Update `docs/reference/GITHUB_ENFORCEMENT.md` with traceability section

---

### 3.2 Phase 2 Implementation Order

```
Step 4: Task Sync Workflow (4-5 hrs)
   |
   v
Step 5: Branch Protection (2-3 hrs)
   |
   v
Step 6: Validate & Test Phase 2
```

**Step 4: Task Sync Workflow**

1. Create `.github/workflows/task-file-sync.yml`
2. Test with manual issue creation (add `task` label)
3. Verify file creation and archival
4. Monitor for edge cases (label removal, re-opening)

**Step 5: Branch Protection**

1. Run configuration script
2. Verify PRs require review
3. Verify status checks required
4. Test emergency bypass
5. Document in GITHUB_ENFORCEMENT.md

---

## 4. Testing Strategy

### 4.1 Unit Tests

| Component | Test | Method |
|-----------|------|--------|
| CODEOWNERS | Syntax valid | `gh api repos/{owner}/{repo}/codeowners/errors` |
| Task schema | YAML valid | `yq validate` against schema |
| PRD metadata | Fields present | Grep for required fields |

### 4.2 Integration Tests

| Scenario | Steps | Expected |
|----------|-------|----------|
| CODEOWNERS review | Open PR changing `dbt_project/models/staging/` | Review requested from @cmbays |
| Task file creation | Open issue with `task` label | File created at `backlog/tasks/issue-{N}.md` |
| Task file archive | Close task-labeled issue | File moved to `backlog/archive/tasks/` |
| Branch protection | Push directly to main | Push rejected |
| Branch protection bypass | Admin force merge | Merge succeeds with warning |

### 4.3 Manual Test Checklist

**Phase 1 Tests**:

- [ ] Create PR touching staging model, verify review requested
- [ ] Create PR touching `.github/`, verify review requested
- [ ] Open PRD file, verify `epic_issue` field present
- [ ] Create new task file, verify uses `issue-{N}.md` naming

**Phase 2 Tests**:

- [ ] Create issue with `task` label, verify file created in ~30s
- [ ] Close task issue, verify file archived
- [ ] Remove `task` label from open issue, verify no file deletion
- [ ] Open PR without review, verify cannot merge
- [ ] Open PR with failing checks, verify cannot merge

---

## 5. Rollback Plan

### 5.1 CODEOWNERS Rollback

```bash
# Remove CODEOWNERS file
git rm .github/CODEOWNERS
git commit -m "revert(github): remove CODEOWNERS file"
git push
```

### 5.2 Task Sync Workflow Rollback

```bash
# Disable workflow
git rm .github/workflows/task-file-sync.yml
git commit -m "revert(github): disable task file sync workflow"
git push

# Clean up any auto-created files manually if needed
```

### 5.3 Branch Protection Rollback

```bash
# Remove branch protection
gh api \
  --method DELETE \
  "/repos/cmbays/dbt-playground/branches/main/protection"
```

---

## 6. Security Considerations

### 6.1 Token Permissions

| Token | Scope | Used By |
|-------|-------|---------|
| `GITHUB_TOKEN` | `contents: write`, `issues: read` | task-file-sync workflow |
| No additional tokens required | - | - |

### 6.2 Branch Protection Security

- **No force push**: History cannot be rewritten
- **Admin bypass**: Only admins can bypass (documented, rare)
- **Status checks**: Malicious code blocked by failing tests

### 6.3 Workflow Security

- **Issue content sanitization**: Title sanitized in bash to prevent injection
- **Label-based trigger**: Only `task` label triggers file creation
- **Read-only issue data**: Workflow only reads issue metadata

---

## 7. Monitoring and Observability

### 7.1 Workflow Monitoring

```bash
# List recent workflow runs
gh run list --workflow=task-file-sync.yml

# View specific run
gh run view <run-id>

# Check for failures
gh run list --workflow=task-file-sync.yml --status=failure
```

### 7.2 API Rate Limit Monitoring

```bash
# Check current rate limit
gh api rate_limit --jq '.rate'
```

### 7.3 CODEOWNERS Errors

```bash
# Check for CODEOWNERS syntax errors
gh api repos/cmbays/dbt-playground/codeowners/errors
```

---

## 8. Documentation Updates Required

| Document | Update |
|----------|--------|
| `CLAUDE.md` | Add CODEOWNERS and branch protection to workflow docs |
| `docs/reference/GITHUB_ENFORCEMENT.md` | Add Sections for CODEOWNERS, branch protection, traceability |
| `docs/guides/CLAUDE_TASK_INTEGRATION.md` | Update task naming convention |
| `.claude/rules/git-workflow.md` | Add branch protection notes |
| `CHANGELOG.md` | Add v0.8.1 section |

---

## 9. Open Technical Questions

| ID | Question | Owner | Status |
|----|----------|-------|--------|
| TQ-1 | Should task sync workflow update existing files on issue edit? | Architect | Open (Recommend: No, GitHub is SoT) |
| TQ-2 | Should branch protection require linear history? | Architect | Open (Recommend: No, too restrictive) |
| TQ-3 | Should CODEOWNERS use team references if teams created later? | Architect | Open (Recommend: Defer to v1.0) |

---

## 10. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-01 | Architect Agent | Initial design |

---

*Document created: 2026-02-01*
*Author: Technical Architect Agent*
