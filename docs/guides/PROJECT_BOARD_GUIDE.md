---
audience: [pm, developer, multi-agent]
priority: medium
size: medium
dependencies: [PROJECT_WORKFLOW]
last_updated: 2026-01-25
status: active
tags: [workflow, github, tracking]
---

# GitHub Project Board Guide

**Japanese Study Site Roadmap**
**Project URL**: https://github.com/users/cmbays/projects/2
**Linked to Repository**: cmbays/japanese-study-site (discoverable from repo Projects tab)

---

## Quick Reference

### Project Details
- **Project Number**: 2
- **Project ID**: PVT_kwHOAX7HsM4BNdiT
- **Owner**: cmbays
- **Type**: Repository-linked Board (Table + Kanban views)

### Key Commands
```bash
# List all items in project
gh project item-list 2 --owner cmbays

# Add issue to project
gh project item-add 2 --owner cmbays --url <ISSUE_URL>

# View project in browser
gh project view 2 --owner cmbays --web
```

---

## Project Board Views

### View 1: Kanban Board (Default)

**Purpose**: Track workflow state at a glance

**Group by**: Status column
**Columns**: Backlog → Blocked → Ready → In Progress → Review → Done

**How to use**:
- Drag items between columns to update status
- Focus on "In Progress" (limit: 3 items max)
- Unblock items in "Blocked" column ASAP

**Filtering**:
- Filter by `phase:1` to see only Phase 1 tasks
- Filter by `assignee:@me` to see your tasks
- Filter by `type:task` to hide epics

### View 2: Epic Roadmap (Recommended for Planning)

**Purpose**: See all tasks grouped by Epic

**Layout**: Table
**Group by**: Epic (#7, #8, #9)
**Sort by**: Task ID (T1.1, T1.2, etc.)
**Columns to show**: Epic, Task ID, Title, Status, Effort, Persona

**How to use**:
- Expand each Epic to see its tasks
- Check task dependencies in "Blocked By" column
- Track Epic completion percentage

### View 3: Wave Timeline

**Purpose**: Plan development in waves

**Layout**: Table
**Group by**: Wave (Wave 1-5)
**Sort by**: Priority → Status
**Columns to show**: Wave, Task ID, Title, Status, Effort, Blocked By

**How to use**:
- Focus on current wave (Wave 1 = T1.1-T1.10, T2.1)
- Identify bottlenecks (multiple tasks blocked by same task)
- Plan next wave when current is 80% complete

### View 4: My Tasks

**Purpose**: Personal task list

**Layout**: Table
**Filter**: `assignee:@me` AND `status != Done`
**Sort by**: Priority → Status
**Columns to show**: Title, Epic, Status, Effort, Due Date

**How to use**:
- Daily: Check what you're working on
- Claim new tasks by assigning to yourself
- Update status as you progress

---

## Custom Fields Explained

### Status
**Type**: Single Select
**Options**: Backlog, Blocked, Ready, In Progress, Review, Done

- **Backlog**: Not yet ready to start (may have dependencies)
- **Blocked**: Waiting on another task to complete
- **Ready**: All dependencies met, ready to claim
- **In Progress**: Currently being worked on
- **Review**: Code complete, awaiting review/merge
- **Done**: Merged and closed

**Workflow**: Ready → In Progress → Review → Done

### Effort
**Type**: Single Select
**Options**: XS, S, M, L, XL

- **XS**: <2 hours (quick fixes, small updates)
- **S**: <1 day (simple features, single file changes)
- **M**: 1-3 days (moderate features, multiple files)
- **L**: 3-5 days (complex features, cross-cutting changes)
- **XL**: 1+ weeks (major features, architectural changes)

**Use for**: Sprint planning, capacity estimation

### Wave
**Type**: Single Select
**Options**: Wave 1, Wave 2, Wave 3, Wave 4, Wave 5

Groups tasks by development phase:
- **Wave 1**: Foundation (T1.1-T1.10, T2.1)
- **Wave 2**: Queuing & Aggregation (T1.4-T1.7)
- **Wave 3**: Session Experience (T2.2-T2.8)
- **Wave 4**: Habit Formation (T3.1-T3.6)
- **Wave 5**: Testing & Polish

**Use for**: Milestone planning, dependency tracking

### Persona
**Type**: Single Select
**Options**: PM, Architect, Developer, Tester, Sensei, Design

Indicates which persona/role is primary owner:
- **PM**: Product Manager (requirements, planning)
- **Architect**: Technical Architect (design, TDD)
- **Developer**: Developer (implementation)
- **Tester**: Quality Tester (verification)
- **Sensei**: Japanese Sensei (content accuracy)
- **Design**: Design Reviewer (UI/UX review)

**Use for**: Filtering tasks by role, assigning work

### Priority
**Type**: Single Select
**Options**: P0, P1, P2, P3

- **P0**: Critical (blocks other work, must do first)
- **P1**: High (important for milestone)
- **P2**: Medium (nice to have for milestone)
- **P3**: Low (can defer to next phase)

**Default**: Most Phase 1 tasks are P1 (high priority for v0.3)

### Epic
**Type**: Text
**Format**: Issue reference (e.g., "#7", "#8", "#9")

Links task to parent Epic issue.

---

## Labels System

### Type Labels (Mutually Exclusive)
- `type:epic` - Parent feature issues (3 total)
- `type:task` - Implementation tasks (24 total)
- `type:bug` - Defect reports
- `type:question` - Clarification requests

### Status Labels (Sync with Custom Field)
- `status:ready` - Ready to start
- `status:blocked` - Waiting on dependencies
- `status:in-dev` - Currently implementing
- `status:review` - Code review phase
- `status:on-hold` - Paused
- `status:triage` - Bug needs assessment

### Effort Labels (Optional, use Custom Field instead)
- `effort:xs` through `effort:xl`

### Phase Labels
- `phase:1` - v0.3 Foundation
- `phase:2` - v0.4 Engagement
- `phase:3` - v0.5 Deep Learning
- `phase:4` - v0.6 Active Recall

### Persona Labels
- `persona:pm`, `persona:arch`, `persona:dev`, `persona:tester`, `persona:design`, `persona:sensei`

---

## Common Workflows

### Starting a New Task

1. **Find ready tasks**:
   ```bash
   gh issue list --label "status:ready" --milestone "v0.3 - Foundation"
   ```
   Or filter project board: `status:Ready`

2. **Claim the task**:
   ```bash
   gh issue edit <ISSUE_NUMBER> --add-assignee @me
   ```
   Or assign via GitHub UI

3. **Move to In Progress**:
   ```bash
   gh issue edit <ISSUE_NUMBER> --add-label "status:in-dev"
   ```
   Or drag on project board to "In Progress" column

4. **Break down into Claude tasks** (optional):
   Use `TaskCreate` to create session-level sub-tasks

5. **Start working**: Follow acceptance criteria and testing plan

### Completing a Task

1. **Verify Definition of Done**:
   - [ ] Code implemented and working
   - [ ] Manual testing complete (no console errors)
   - [ ] Works on mobile (375px width tested)
   - [ ] localStorage data validates correctly
   - [ ] Code reviewed (if applicable)
   - [ ] PR merged to main

2. **Create pull request**:
   ```bash
   gh pr create --title "feat(scope): description" --fill
   ```

3. **Move to Review**:
   ```bash
   gh issue edit <ISSUE_NUMBER> --add-label "status:review"
   ```

4. **After PR merge**:
   ```bash
   gh issue close <ISSUE_NUMBER>
   ```
   (Automatically moves to "Done" on project board)

### Unblocking Tasks

When a blocker task completes:

1. **Find dependent tasks**:
   - Check Epic issue body for task list
   - Or search issues for "Blocked By: #<TASK_NUMBER>"

2. **Update blocked tasks**:
   ```bash
   gh issue edit <BLOCKED_TASK> --remove-label "status:blocked" --add-label "status:ready"
   ```

3. **Update project board**:
   - Drag from "Blocked" to "Ready" column

### Daily Standup Workflow

1. **Check My Tasks view**:
   - What did I complete yesterday?
   - What am I working on today?
   - Any blockers?

2. **Update task status**:
   - Move completed tasks to "Review" or "Done"
   - Claim new tasks from "Ready"

3. **Communicate blockers**:
   - Comment on issue with blocker details
   - Add `status:blocked` label if waiting on something

---

## Filtering Tips

### Show Only Ready Tasks
```
Filter: status:Ready AND phase:1
```
Result: All Phase 1 tasks with no blockers

### Show Wave 1 Tasks
```
Filter: wave:"Wave 1"
```
Result: All foundation tasks (T1.1-T1.10, T2.1)

### Show My In-Progress Tasks
```
Filter: assignee:@me AND status:"In Progress"
```
Result: Everything you're currently working on

### Show Epic 1 Tasks
```
Filter: epic:#7
```
Result: All tasks belonging to PRD-001 (SRS Engine)

### Show High Priority Tasks
```
Filter: priority:P0 OR priority:P1
```
Result: All critical and high priority tasks

---

## Automation Rules

### Auto-add New Issues
**Trigger**: Issue created with `type:task` or `type:epic` label
**Action**: Add to project, set Status = Backlog

### Auto-move to In Progress
**Trigger**: Label `status:in-dev` added
**Action**: Set Status = In Progress

### Auto-move to Review
**Trigger**: Label `status:review` added
**Action**: Set Status = Review

### Auto-move to Done
**Trigger**: Issue closed
**Action**: Set Status = Done

### Blocked Alert
**Trigger**: Label `status:blocked` added
**Action**: Set Status = Blocked, add comment

---

## Metrics & Reporting

### Epic Progress
```bash
# Count completed tasks per epic
gh issue list --milestone "v0.3 - Foundation" --state closed --label "type:task" --json number,title

# Calculate percentage
# Epic 1: X/10 tasks complete = Y%
# Epic 2: X/8 tasks complete = Y%
# Epic 3: X/6 tasks complete = Y%
```

### Wave Progress
```bash
# List Wave 1 tasks
gh issue list --milestone "v0.3 - Foundation" --label "type:task" --json number,title,state

# Filter by custom field in web UI
```

### Effort Estimation
- Total effort: 8 S + 16 M = ~8 + ~32 = 40 person-days
- With parallelization: ~6-8 weeks

### Velocity Tracking
- Track: Tasks completed per week
- Target: 3-4 tasks/week (assuming 1 developer)
- Adjust wave planning based on velocity

---

## Best Practices

### For Product Managers
- Keep Epic issues updated with task progress
- Review project board weekly
- Adjust priorities based on blockers
- Create new tasks as discoveries happen

### For Developers
- Claim only what you can complete this week
- Update status daily (or after each session)
- Comment on blockers immediately
- Link PRs to task issues

### For Reviewers
- Check "Review" column daily
- Review PRs within 24 hours
- Leave clear, actionable feedback
- Approve or request changes (don't leave hanging)

### For Everyone
- **Don't skip "Ready" status**: Only claim tasks with no blockers
- **Respect WIP limits**: Max 3 tasks in "In Progress"
- **Keep it current**: Update status as you work, not at end of week
- **Communicate**: Comment on issues, don't work in silence

---

## Claude Task Integration

**New in v0.3**: Convert GitHub issues to Claude tasks for session-level work coordination.

### Overview

Claude Task GitHub Integration enables:
- **Cross-session task persistence** - Tasks survive Claude restarts
- **GitHub-to-Claude conversion** - Convert issues to tasks with metadata
- **Metadata validation** - Schema-based validation prevents errors
- **Multi-agent coordination** - PM → Architect → Developer workflows

**When to use**:
- Session-level work (breaking down GitHub issues)
- Agent handoffs and coordination
- Temporary sub-tasks within a coding session

**When NOT to use**:
- Long-term planning (use GitHub issues)
- External visibility (use GitHub issues)
- Milestone tracking (use GitHub issues)

### Quick Start

#### Convert GitHub Issue to Claude Task

```bash
# Convert Epic issue #7
.claude/scripts/github-sync/issue-to-task.sh 7

# Copy the TaskCreate call output
# Paste into Claude session
# Task is created with validated metadata
```

#### Validate Metadata

```bash
# Validate metadata before creating task
.claude/scripts/core/validate-metadata.sh '{
  "type": "epic",
  "epic_id": "PRD-001",
  "prd": "docs/specs/PRD-001.md",
  "github_issue": 7
}'
# Output: ✓ Metadata valid: type=epic
```

### Task Types

| Type | Purpose | Required Fields |
|------|---------|-----------------|
| `epic` | Parent feature issue | type, epic_id, prd |
| `task` | Implementation work | type |
| `tdd` | TDD creation task | type, tdd_id, epic_id |
| `pm-work` | PM workflow task | type |
| `documentation` | Documentation task | type |

### Common Workflows

#### Workflow: Epic → TDD → Task

```javascript
// 1. PM converts Epic issue to Claude task
// (using issue-to-task.sh script)

// 2. Architect creates TDD task
TaskCreate({
  subject: "Create TDD-001: JLPT Engine",
  metadata: {
    type: "tdd",
    tdd_id: "001",
    epic_id: "PRD-001",
    github_issue: 7
  }
})

// 3. Developer creates implementation task
TaskCreate({
  subject: "Implement SM-2 algorithm",
  metadata: {
    type: "task",
    epic: 7,
    tdd_section: "§3",
    effort: "M"
  }
})

// 4. Developer completes task
TaskUpdate({taskId: "<id>", status: "completed"})
```

#### Workflow: Break Down Epic into Sub-Tasks

```bash
# Convert main Epic
.claude/scripts/github-sync/issue-to-task.sh 7

# In Claude session, create sub-tasks:
TaskCreate({
  subject: "Sub-task 1",
  metadata: {type: "task", epic: 7, tdd_section: "§3"}
})

TaskCreate({
  subject: "Sub-task 2",
  metadata: {type: "task", epic: 7, tdd_section: "§5"}
})

# Track progress
TaskList()
```

### Scripts Reference

**Location**: `.claude/scripts/`

| Script | Purpose | Usage |
|--------|---------|-------|
| `core/validate-metadata.sh` | Validate metadata | `validate-metadata.sh '<json>'` |
| `core/task-helpers.sh` | Utility functions | `source task-helpers.sh` |
| `github-sync/issue-to-task.sh` | Convert issue to task | `issue-to-task.sh <issue-number>` |

**Full documentation**: See [.claude/scripts/README.md](../.claude/scripts/README.md) and [CLAUDE_TASK_INTEGRATION.md](CLAUDE_TASK_INTEGRATION.md)

### Dependencies

```bash
# Required tools (install if missing)
brew install gh jq

# Authenticate gh CLI
gh auth login
```

### Troubleshooting

#### Script fails: "gh: command not found"

```bash
brew install gh
gh auth login
```

#### Script fails: "jq: command not found"

```bash
brew install jq
```

#### Validation fails: "Epic requires 'epic_id' field"

**Cause**: Epic metadata missing required field

**Fix**: Ensure issue contains Epic ID in title or body (format: PRD-001)

#### Conversion produces empty metadata

**Cause**: Issue body doesn't match extraction patterns

**Fix**: Check issue format. Script looks for:
- Epic ID: PRD-XXX anywhere in title/body
- PRD path: docs/specs/PRD-XXX*.md
- Task ID: T*.* after "Task ID:" or "Task:"

**Debug**:
```bash
# View issue body
gh issue view 7 --json body | jq -r '.body'
```

---

## Troubleshooting

### Issue Not Appearing on Board

**Cause**: Issue wasn't added to project (or doesn't have `type:epic` or `type:task` label for automation)
**Fix**:
```bash
gh project item-add 2 --owner cmbays --url <ISSUE_URL>
```

### Custom Field Not Updating

**Cause**: Must update via project board UI or API (not labels)
**Fix**: Edit custom field directly on project board

### Can't Find Filtered Tasks

**Cause**: Filter syntax incorrect
**Fix**: Use exact custom field values (case-sensitive):
- Status: "Ready" (not "ready")
- Wave: "Wave 1" (not "wave 1")

### Automation Not Working

**Cause**: Automation rules require labels (e.g., `status:in-dev`)
**Fix**: Add the appropriate label to trigger automation

---

## Resources

### GitHub Documentation
- [Projects (beta) documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [GitHub CLI projects](https://cli.github.com/manual/gh_project)

### Project Files
- Issue templates: `.github/ISSUE_TEMPLATE/`
- Setup scripts: `.github/scripts/`
- This guide: `docs/PROJECT_BOARD_GUIDE.md`

### Quick Links
- [Project Board](https://github.com/users/cmbays/projects/2) (linked to repository, discoverable from repo's Projects tab)
- [v0.3 Milestone](https://github.com/cmbays/japanese-study-site/milestone/1)
- [All Issues](https://github.com/cmbays/japanese-study-site/issues)
- [Phase 1 Plan](../temp/PHASE1_SETUP_COMPLETE.md)

---

*Last Updated: 2026-01-25*
*For questions or improvements, open an issue with `type:question` label*
