# Phase 3: GitHub Project Management

**Status**: READY TO IMPLEMENT
**Date**: 2026-01-31
**Version**: 1.0
**Meta Issue**: #92

---

## Overview

Phase 3 expands GitHub-MCP usage to include project management (issue creation, milestone tracking, PR-issue linking) to eliminate manual GitHub UI navigation.

**Goal**: Automate GitHub project operations through CLI and PM persona, enabling fully programmatic roadmap and issue management.

---

## Why Phase 3 Matters

Currently, most GitHub project operations require manual UI:

- ❌ PM manually creates issues in GitHub UI
- ❌ Milestones created by hand
- ❌ Issues manually linked to PRs
- ❌ Roadmap tracked in docs, not GitHub

Phase 3 fixes this:

- ✅ PM creates issues via CLI command
- ✅ Milestones auto-managed
- ✅ PR-issue linking automated
- ✅ Roadmap visible in GitHub Projects

---

## Phase 3 Features

### Feature 1: GitHub Issue Creation (#93)

**Objective**: Enable PM to create issues programmatically.

**What it does**:

- Create issues with title, description, labels, milestone
- Validate issue format and references
- Auto-link related issues
- No GitHub UI required

**Command Pattern**:

```bash
pm: create-issue "feat(staging): add new source table" \
  --label enhancement,data \
  --milestone v0.8 \
  --assignee cmbays \
  --priority high
```

**YAML Template** (temp/issue-template.yaml):

```yaml
title: "feat(staging): add new model"
description: |
  ## Description
  Clear description of the issue

  ## Acceptance Criteria
  - [ ] Criteria 1
  - [ ] Criteria 2

  ## Related
  Closes #N (if this closes another issue)
  Related to #N (if this is related)

labels:
  - enhancement
  - data
  - staging

milestone: v0.8
assignee: cmbays
priority: high  # high, medium, low
```

**Testing**:

- Create test issue via CLI
- Verify labels applied
- Verify milestone assigned
- Verify related issues linked

---

### Feature 2: Milestone Tracking (#94)

**Objective**: Create and manage release milestones.

**What it does**:

- Create milestones for v0.8, v0.9, v1.0
- Track milestone progress
- Auto-close issues when PR merged
- Update CLAUDE.md with milestone status

**Milestones to Create**:

| Milestone | Target Date | Focus | Issues |
|-----------|-------------|-------|--------|
| **v0.8** | Feb 28, 2026 | GitHub Project Management | #92, #93, #94, #95 |
| **v0.9** | Mar 31, 2026 | Advanced Analytics | TBD |
| **v1.0** | June 30, 2026 | Production Ready | TBD |

**Command Pattern**:

```bash
gh milestone create \
  --title "v0.8" \
  --description "GitHub Project Management" \
  --due-date "2026-02-28"

# Link issues to milestone
gh issue edit 93 --milestone "v0.8"
gh issue edit 94 --milestone "v0.8"
```

**Roadmap Status in CLAUDE.md**:

```markdown
### v0.8: GitHub Project Management (Feb 2026)
- ✅ Phase 2: GitHub-MCP PR Reviews (Complete)
- 🚀 Phase 3: Project Management (In Progress)
  - [ ] Issue creation (#93)
  - [ ] Milestone tracking (#94)
  - [ ] PR-issue linking (#95)
  - [ ] Project integration (#96)
```

---

### Feature 3: Automated PR-Issue Linking (#95)

**Objective**: Auto-link PRs to issues via conventional syntax.

**What it does**:

- PR title/body with "Closes #N" links and closes issue
- "Related to #N" links without closing
- GitHub Actions validates syntax
- Issues closed automatically on PR merge

**Conventional Syntax**:

| Syntax | Behavior |
|--------|----------|
| `Closes #N` | Link PR, auto-close issue on merge |
| `Fixes #N` | Same as Closes |
| `Resolves #N` | Same as Closes |
| `Related to #N` | Link PR, keep issue open |
| `See also #N` | Link in description, reference only |

**PR Title Example**:

```
feat(staging): add customer source table

Closes #93
Related to #71
```

**Validation**:

- pr-validation workflow checks syntax
- Issue number must exist
- Links created bidirectionally

**Testing**:

- Create PR with "Closes #X"
- Merge PR
- Verify issue auto-closes
- Verify bidirectional link

---

### Feature 4: GitHub Projects Integration (#96)

**Objective**: Visual roadmap using GitHub Projects.

**What it does**:

- Create GitHub Project for v0.8
- Add issues to project
- Automate status columns:
  - **Backlog** - Not started
  - **In Progress** - Being worked
  - **In Review** - PR created
  - **Done** - PR merged, issue closed
- Auto-update on PR events

**Automation Rules**:

| Event | Action |
|-------|--------|
| Issue created | Add to Backlog |
| PR created for issue | Move to In Review |
| PR merged | Move to Done, close issue |
| Issue closed | Move to Done |

**Setup**:

```bash
# Create project (manual via GitHub UI for now)
# Then add automation via workflow

# Add issues to project
gh project item-add --id PROJECT_ID --issue 93
gh project item-add --id PROJECT_ID --issue 94
```

**Roadmap Page**:

- Embed GitHub Project in docs/roadmap/
- Links to open issues
- Progress tracking

---

## Implementation Order

### Week 1: Issue Creation

1. Implement Feature 1 (Issue creation)
2. Create milestones
3. Test issue workflow

### Week 2: Linking

4. Implement Feature 3 (PR-issue linking)
5. Update pr-validation workflow
6. Test PR-close workflow

### Week 3: Projects

7. Implement Feature 4 (Project integration)
8. Set up automation
9. Test end-to-end

---

## GitHub Issues Created

| # | Title | Feature | Status |
|---|-------|---------|--------|
| #92 | Phase 3 Meta Issue | Meta | Open |
| #93 | Issue Creation | Feature 1 | Open |
| #94 | Milestone Tracking | Feature 2 | Open |
| #95 | PR-Issue Linking | Feature 3 | Open |
| #96 | Project Integration | Feature 4 | Open |

**View all**: <https://github.com/cmbays/dbt-playground/issues?q=is%3Aopen+label%3Aworkflow>

---

## Tools & Commands

**gh CLI Commands**:

```bash
# Create issue
gh issue create --title "..." --body "..." --label "..." --milestone "..."

# Create milestone
gh milestone create --title "v0.8" --due-date "2026-02-28"

# Link issue to milestone
gh issue edit 93 --milestone "v0.8"

# Add to project
gh project item-add --id PROJECT_ID --issue 93

# Close issue
gh issue close 93 --comment "Closed via PR merge"

# View issue
gh issue view 93 --web  # Opens in browser
```

**Automation**:

- GitHub Actions workflow for PR-issue linking
- Workflow-on-PR-merge for auto-closing issues
- Project automation rules (built-in, no code needed)

---

## Success Criteria

Phase 3 is complete when:

✅ Feature 1 (Issue Creation)

- PM can create issues via CLI without UI
- Issues appear with correct labels and milestone
- Related issues auto-linked

✅ Feature 2 (Milestone Tracking)

- v0.8, v0.9, v1.0 milestones created
- Issues assigned to milestones
- Progress tracked in CLAUDE.md

✅ Feature 3 (PR-Issue Linking)

- PRs with "Closes #N" link bidirectionally
- Issues auto-close on PR merge
- Syntax validated in pr-validation

✅ Feature 4 (Project Integration)

- GitHub Project created for v0.8
- Issues auto-move through columns
- Roadmap visible and up-to-date

---

## Phase 3 Benefits

| Benefit | Impact |
|---------|--------|
| No UI Navigation | Faster workflow, less context switching |
| Automated Linking | No manual PR-issue matching |
| Roadmap Visibility | Teams see progress in one place |
| Audit Trail | All operations logged in GitHub |
| Scalability | Can manage hundreds of issues programmatically |

---

## Next Steps

1. **Product Manager**: Review this plan, create issues (DONE ✅)
2. **Architect**: Design implementation approach for Feature 1-4
3. **Developer**: Implement each feature following the architecture
4. **Tester**: Write test specifications for each feature
5. **Reviewer**: Code review and security review
6. **Documenter**: Update guides and CLAUDE.md

---

## Timeline

- **Now**: Issues created (#92-96)
- **This week**: Features 1-2 implemented
- **Next week**: Features 3-4 implemented
- **End of month**: Phase 3 complete, v0.8 milestone ready

---

## References

- GitHub Issues: <https://github.com/cmbays/dbt-playground/issues?q=is%3Aopen+label%3Aworkflow>
- gh CLI docs: <https://cli.github.com/manual>
- GitHub Projects: <https://docs.github.com/en/issues/planning-and-tracking-with-projects>
- Phase 2 Reference: `docs/for_chris/PHASE_2_GITHUB_MCP_SETUP.md`

---

**Phase 3 is now in the backlog and ready for implementation. Next: Architect designs Feature 1-4 approach.**
