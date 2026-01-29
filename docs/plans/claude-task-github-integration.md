# Claude Task Primitives ↔ GitHub Issues Integration (Revised)

## Overview

Integrate Claude Code's task primitives with GitHub issues to enable:

- Cross-session task persistence for multi-agent workflows
- Lightweight pull-on-demand + opt-in push-on-complete sync workflow
- Enhanced Epic → TDD → Task orchestration with dependency tracking
- Agent coordination with formal metadata conventions and validation

**Philosophy**: GitHub issues remain the source of truth for long-term planning. Claude tasks serve as session-level coordination primitives for agent handoffs, sub-task breakdown, and context preservation.

## Current State

**What We Have**:

- 27 GitHub issues (3 epics, 24 tasks) in Project #1
- Recent Claude task usage (as of 2026-01-25) with ad-hoc metadata
- Heavy reliance on `gh` CLI for GitHub operations
- Epic → TDD → Task workflow established but not formalized for Claude tasks
- Task persistence to `~/.claude/tasks/` available

**What's Missing**:

- Formalized metadata schema for GitHub-Claude linking
- Metadata validation layer
- Scripts to convert GitHub issues → Claude tasks
- Opt-in sync mechanism for task completion → GitHub status updates
- Architecture documentation and diagrams
- Integration pattern documentation

## Objectives

### Primary (MVP)

1. **Establish metadata schema**: Define and validate task metadata conventions
2. **Pull integration**: Script to convert GitHub issues → Claude tasks with metadata
3. **Documentation**: Architecture diagrams and integration guides

### Secondary (Post-MVP)

4. **Push integration**: Opt-in sync for Claude task completion → GitHub status updates
5. **Epic workflow**: Orchestrate Epic → TDD → Task pattern with automation
6. **Maintenance tools**: Cleanup scripts and edge case handling

---

## Architecture Overview

### Layered Design

```
┌─────────────────────────────────────────────────────┐
│ Layer 4: Workflow Orchestration                     │
│ (.claude/scripts/workflows/)                        │
│ - epic-workflow.sh, update-epic-tasks.sh            │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ Layer 3: GitHub Sync Scripts                        │
│ (.claude/scripts/github-sync/)                      │
│ - issue-to-task.sh, task-to-status.sh               │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ Layer 2: Metadata Validation                        │
│ (.claude/scripts/core/)                             │
│ - validate-metadata.sh, task-helpers.sh             │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ Layer 1: Core Primitives                            │
│ (Claude Code Built-in)                              │
│ - TaskCreate, TaskUpdate, TaskList, TaskGet         │
└─────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| GitHub operations | `gh` CLI | Native GitHub integration |
| JSON parsing | `jq` | Standard CLI JSON processor |
| Scripts | Bash | Cross-platform, minimal dependencies |
| Task storage | `~/.claude/tasks/` | Claude Code built-in |
| Metadata validation | JSON Schema + jq | Industry standard |

---

## Implementation Phases

### Phase 0: Discovery & Validation (NEW)

**Goal**: Validate assumptions and prototype core functionality before full implementation

**Tasks**:

1. **Test task persistence mechanism**

   ```bash
   # Create test task
   TaskCreate({subject: "Test Persistence", metadata: {test: true}})

   # Verify storage
   ls ~/.claude/tasks/

   # Start new session, verify survival
   TaskList()
   ```

2. **Prototype issue-to-task conversion**

   ```bash
   # Manually convert issue #7 to understand data structure
   gh issue view 7 --json title,body,labels,number

   # Draft TaskCreate call with metadata
   # Validate metadata structure makes sense
   ```

3. **Validate metadata schema**
   - Test with real GitHub issues (#7, #14)
   - Ensure labels parse correctly
   - Verify TDD section extraction works

4. **Document persistence mechanism**
   - How does `CLAUDE_CODE_TASK_LIST_ID` work?
   - File format in `~/.claude/tasks/`
   - Cross-session behavior

**Deliverables**:

- `temp/phase0-discovery-notes.md` (findings and validation results)
- Prototype scripts in `temp/` for review

**Acceptance Criteria**:

- [ ] Task created in one session is visible in next session
- [ ] Task metadata schema validated against real issues
- [ ] Prototype issue-to-task conversion works for Epic and Task
- [ ] Persistence mechanism documented and understood

**Decision Point**: Go/No-Go for Phases 1-5 based on validation results

---

### Phase 1: Foundation (REVISED - MVP Part 1)

**Goal**: Establish metadata conventions, validation layer, and architecture documentation

**Tasks**:

1. **Create `.claude/scripts/core/validate-metadata.sh`**

   ```bash
   #!/usr/bin/env bash
   # Validates Claude task metadata against schema
   # Usage: validate-metadata.sh '{"github_issue": 7, "type": "epic"}'

   # Uses jq to validate:
   # - Required fields present
   # - Type values whitelisted
   # - github_issue is number (if present)
   # - No unknown fields
   ```

2. **Create `.claude/scripts/core/task-helpers.sh`**

   ```bash
   # Utility functions:
   # - get_task_metadata(task_id)
   # - validate_task_type(type)
   # - extract_github_issue(metadata)
   ```

3. **Create architecture diagram**
   - File: `docs/tdd/TDD-XXX-Task-Integration-Architecture.d2`
   - Show data flow: GitHub → Scripts → Claude Tasks → GitHub
   - Include layer architecture diagram
   - Document sync patterns (pull, push, opt-in)

4. **Create `docs/CLAUDE_TASK_INTEGRATION.md`**
   - Document metadata schema with validation rules
   - Explain when to use GitHub issues vs Claude tasks
   - Include architecture diagram
   - Document Layer 1-4 architecture
   - Add troubleshooting section

5. **Configure task persistence** (if needed)
   - Document how to set `CLAUDE_CODE_TASK_LIST_ID` environment variable
   - OR update `.claude/settings.json` if that's the mechanism
   - Document based on Phase 0 findings

**Deliverables**:

- `.claude/scripts/core/validate-metadata.sh`
- `.claude/scripts/core/task-helpers.sh`
- `docs/tdd/TDD-XXX-Task-Integration-Architecture.d2`
- `docs/CLAUDE_TASK_INTEGRATION.md` (initial version)
- Configuration documentation

**Acceptance Criteria**:

- [ ] validate-metadata.sh rejects invalid schemas
- [ ] validate-metadata.sh accepts all valid metadata types (epic, task, tdd, pm-work, documentation)
- [ ] Architecture diagram shows all 4 layers clearly
- [ ] Documentation explains metadata schema with examples
- [ ] Task persistence configured and verified

---

### Phase 2: Pull Integration (REVISED - MVP Part 2)

**Goal**: Manual script to convert GitHub issues → Claude tasks with validated metadata

**Tasks**:

1. **Create `.claude/scripts/github-sync/issue-to-task.sh`**

   ```bash
   #!/usr/bin/env bash
   # Converts GitHub issue to Claude TaskCreate call
   # Usage: issue-to-task.sh <issue-number>

   issue_num=$1
   issue_json=$(gh issue view "$issue_num" --json title,body,labels,number)

   # Parse with jq
   title=$(echo "$issue_json" | jq -r '.title')
   body=$(echo "$issue_json" | jq -r '.body')
   labels=$(echo "$issue_json" | jq -r '.labels[].name')

   # Extract metadata
   type=$(echo "$labels" | grep '^type:' | cut -d':' -f2)
   epic=$(echo "$body" | grep -oP 'Epic: #\K\d+' || echo "null")

   # Build metadata JSON
   metadata=$(jq -n \
     --arg github_issue "$issue_num" \
     --arg type "$type" \
     --arg epic "$epic" \
     '{github_issue: ($github_issue | tonumber), type: $type, epic: ($epic | tonumber)}')

   # Validate metadata
   .claude/scripts/core/validate-metadata.sh "$metadata" || exit 1

   # Output TaskCreate call
   echo "TaskCreate({"
   echo "  subject: \"$title\","
   echo "  description: \"$body\","
   echo "  metadata: $metadata"
   echo "})"
   ```

2. **Create `.claude/scripts/README.md`**
   - Document `issue-to-task.sh` usage
   - Provide examples for Epic, Task, Bug conversion
   - Explain metadata extraction logic
   - Show validation error examples

3. **Test with sample issues**

   ```bash
   # Test Epic conversion
   .claude/scripts/github-sync/issue-to-task.sh 7

   # Test Task conversion
   .claude/scripts/github-sync/issue-to-task.sh 14

   # Verify metadata structure
   # Verify validation catches errors
   ```

4. **Update `docs/PROJECT_BOARD_GUIDE.md`**
   - Add "Claude Task Integration" section
   - Document when to use `issue-to-task.sh`
   - Show manual workflow examples
   - Link to detailed guide

**Deliverables**:

- `.claude/scripts/github-sync/issue-to-task.sh` (Bash script)
- `.claude/scripts/README.md`
- Updated `docs/PROJECT_BOARD_GUIDE.md`

**Acceptance Criteria**:

- [ ] Script successfully converts Epic issue to TaskCreate call
- [ ] Script successfully converts Task issue to TaskCreate call
- [ ] Metadata validation runs and catches errors
- [ ] Script output can be copy-pasted to create task
- [ ] Documentation explains usage with examples

---

## MVP CHECKPOINT

**Status**: After completing Phase 0, 1, and 2, we have:

✅ **Foundation Complete**

- Metadata schema defined and validated
- Architecture documented with diagrams
- Task persistence understood and configured

✅ **Pull Integration Working**

- Manual conversion of GitHub issues → Claude tasks
- Metadata validation layer functional
- Documentation complete for basic usage

**Value Delivered**:

- Can manually convert GitHub issues to Claude tasks with validated metadata
- Clear architecture and conventions established
- Ready for agent-based workflows

**Decision Point**: Evaluate if auto-sync (Phase 3) is needed before proceeding

### Evaluation Criteria

**Proceed with Phase 3-5 if**:

- Manual workflow is too tedious
- Multiple agents need automatic sync
- High volume of task completions

**Stop at MVP if**:

- Manual workflow suffices
- Small number of tasks
- Sync complexity outweighs benefit

---

---

### Phase 3: Push Integration (REVISED - Opt-In Sync)

**Goal**: Opt-in sync mechanism for Claude task completion → GitHub status updates

**Tasks**:

1. **Create `.claude/scripts/github-sync/task-to-status.sh`**

   ```bash
   #!/usr/bin/env bash
   # Manually sync Claude task completion to GitHub
   # Usage: task-to-status.sh <task-id>

   task_id=$1

   # Get task details
   task_json=$(TaskGet({taskId: "$task_id"}) | jq)

   # Extract metadata
   github_issue=$(echo "$task_json" | jq -r '.metadata.github_issue')
   status=$(echo "$task_json" | jq -r '.status')

   # Only sync if opted in
   sync_enabled=$(echo "$task_json" | jq -r '.metadata.sync_on_complete // false')

   if [[ "$sync_enabled" != "true" ]]; then
     echo "Task sync not enabled (sync_on_complete: false)"
     exit 0
   fi

   # Update GitHub issue
   if [[ "$status" == "completed" && "$github_issue" != "null" ]]; then
     gh issue edit "$github_issue" \
       --remove-label "status:in-dev" \
       --add-label "status:review"

     gh issue comment "$github_issue" \
       --body "✅ Completed via Claude task #$task_id"
   fi
   ```

2. **Create wrapper function for opt-in auto-sync**
   - Document pattern in `docs/CLAUDE_TASK_INTEGRATION.md`:

   ```javascript
   // Opt-in auto-sync pattern
   function completeTaskWithSync(taskId, summary) {
     // 1. Mark task complete
     TaskUpdate({taskId, status: "completed"});

     // 2. Optionally sync to GitHub
     const task = TaskGet({taskId});
     if (task.metadata.sync_on_complete) {
       Bash({
         command: `.claude/scripts/github-sync/task-to-status.sh ${taskId}`,
         description: "Sync task completion to GitHub"
       });
     }
   }
   ```

3. **Test sync mechanism**
   - Create task with `sync_on_complete: true`
   - Create task with `sync_on_complete: false`
   - Mark both completed
   - Verify only first syncs to GitHub

4. **Update `docs/CLAUDE_TASK_INTEGRATION.md`**
   - Document opt-in sync pattern
   - Explain `sync_on_complete` metadata flag
   - Show manual sync workflow
   - Add examples of sync output

**Deliverables**:

- `.claude/scripts/github-sync/task-to-status.sh`
- Updated documentation with opt-in pattern

**Acceptance Criteria**:

- [ ] Manual sync script works for completed tasks
- [ ] Opt-in flag (`sync_on_complete`) respected
- [ ] GitHub issue status updated correctly
- [ ] Comment added to GitHub issue
- [ ] Tasks without `github_issue` handled gracefully
- [ ] Documentation shows both manual and opt-in patterns

---

### Phase 4: Epic Workflow Orchestration (Optional)

**Goal**: Automate Epic → TDD → Task workflow setup with error handling

**Tasks**:

1. **Create `.claude/scripts/workflows/epic-workflow.sh`**

   ```bash
   #!/usr/bin/env bash
   # Orchestrates Epic → TDD → Task workflow
   # Usage: epic-workflow.sh <epic-issue-number>

   epic_num=$1

   # Fetch Epic with validation
   epic_json=$(gh issue view "$epic_num" --json title,body,labels 2>/dev/null)
   if [[ $? -ne 0 ]]; then
     echo "Error: Issue #$epic_num not found"
     exit 1
   fi

   # Validate it's an Epic
   type=$(echo "$epic_json" | jq -r '.labels[] | select(.name | startswith("type:")) | .name' | cut -d':' -f2)
   if [[ "$type" != "epic" ]]; then
     echo "Error: Issue #$epic_num is not an Epic (type: $type)"
     exit 1
   fi

   # Extract PRD link
   prd_link=$(echo "$epic_json" | jq -r '.body' | grep -oP 'PRD:\s*\K[^\s]+')
   if [[ -z "$prd_link" ]]; then
     echo "Warning: No PRD link found in Epic body"
   fi

   # Generate TDD creation task
   echo "Creating TDD creation task for Epic #$epic_num..."
   # [TaskCreate call with proper metadata]
   ```

2. **Create `.claude/scripts/workflows/update-epic-tasks.sh`**

   ```bash
   # Batch update GitHub tasks to reference TDD sections
   # Requires TDD to exist first
   ```

3. **Update `.claude/agents/product-manager.md`**
   - Add "Epic → TDD → Task Workflow" section
   - Document when to use `epic-workflow.sh`
   - Provide workflow diagram
   - Include error handling guidance

4. **Update `.claude/agents/AGENTS.md`**
   - Add "Task Metadata Standards" section
   - Include full metadata schema reference
   - Document handoff protocols using Claude tasks
   - Show dependency management patterns

5. **Test Epic workflow**
   - Test with well-formed Epic (#7)
   - Test with malformed Epic (missing PRD)
   - Test with non-Epic issue
   - Verify error handling

**Deliverables**:

- `.claude/scripts/workflows/epic-workflow.sh`
- `.claude/scripts/workflows/update-epic-tasks.sh`
- Updated agent documentation

**Acceptance Criteria**:

- [ ] Script validates issue is an Epic before proceeding
- [ ] Script handles missing PRD link gracefully
- [ ] Script generates TDD creation task with correct metadata
- [ ] Error messages are clear and actionable
- [ ] Documentation shows error handling patterns

---

### Phase 5: Refinement & Polish (Optional)

**Goal**: Add maintenance tools, comprehensive docs, and edge case handling

**Tasks**:

1. **Create `.claude/scripts/workflows/task-cleanup.sh`**

   ```bash
   #!/usr/bin/env bash
   # Clean up old completed tasks
   # Default: 30 days (configurable)

   retention_days=${1:-30}
   cutoff_date=$(date -d "$retention_days days ago" +%Y-%m-%d)

   echo "Finding tasks completed before $cutoff_date..."

   # List completed tasks (pseudo-code - depends on TaskList output format)
   completed_tasks=$(TaskList() | jq '.[] | select(.status == "completed")')

   # Filter by date and prompt for deletion
   # Generate cleanup report
   ```

2. **Add comprehensive error handling**
   - Handle `gh` CLI failures (network, auth, not found)
   - Validate metadata in all scripts
   - Add retry logic with backoff for network operations
   - Log errors to `.claude/logs/task-integration.log`

3. **Enhance workflow diagrams**
   - Epic → TDD → Task flow (D2 diagram)
   - Pull/Push sync diagram with opt-in flag
   - Layer architecture diagram (already in Phase 1)
   - Add all diagrams to `docs/CLAUDE_TASK_INTEGRATION.md`

4. **Document edge cases & FAQ**
   - What if TDD doesn't exist yet? (Block tasks until created)
   - What if GitHub issue is closed? (Sync should skip)
   - What if task has no GitHub issue? (No sync, that's OK)
   - What if metadata invalid? (Validation catches, fails gracefully)
   - Add FAQ section to integration guide

5. **Create real-world examples**
   - Example 1: PM creates Epic, Architect creates TDD
   - Example 2: Developer implements task with sync
   - Example 3: Multi-agent workflow with dependencies
   - Example 4: Error handling scenarios
   - Example 5: Manual sync workflow

**Deliverables**:

- `.claude/scripts/workflows/task-cleanup.sh`
- Enhanced error handling across all scripts
- Complete workflow diagrams
- Comprehensive documentation with 5+ examples
- FAQ section

**Acceptance Criteria**:

- [ ] Cleanup script identifies old tasks correctly
- [ ] All scripts handle `gh` CLI errors gracefully
- [ ] Diagrams clearly show all workflows
- [ ] FAQ answers common questions
- [ ] Examples cover Epic, Task, and multi-agent scenarios
- [ ] Cleanup retention configurable (default 30 days)

---

## Metadata Schema Reference

### Schema Validation Rules

All metadata must pass validation via `validate-metadata.sh`:

- **type** (required): One of `"epic"`, `"task"`, `"tdd"`, `"pm-work"`, `"documentation"`
- **github_issue** (optional): Number, if present must be > 0
- **sync_on_complete** (optional): Boolean, defaults to `false`
- Type-specific fields validated based on type value

### Epic Task Metadata

```javascript
{
  github_issue: 7,
  type: "epic",
  epic_id: "PRD-001",
  prd: "docs/specs/PRD-001-JLPT-Mastery-Engine.md",
  tdd: "docs/tdd/TDD-001-JLPT-Mastery-Engine.md",  // Added after TDD creation
  phase: 1,
  tasks: [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],  // Child GitHub issues
  sync_on_complete: false  // Epics typically don't auto-sync
}
```

### TDD Creation Task Metadata

```javascript
{
  github_issue: 7,  // Parent Epic
  type: "tdd",
  tdd_id: "001",
  epic_id: "PRD-001",
  deliverable: "docs/tdd/TDD-001-JLPT-Mastery-Engine.md",
  context_doc: "temp/TDD-001-CREATION-CONTEXT.md",
  sync_on_complete: true  // Update Epic when TDD complete
}
```

### Implementation Task Metadata

```javascript
{
  github_issue: 14,
  type: "task",
  task_id: "T1.2",
  epic: 7,
  tdd_section: "§3",  // TDD section implemented
  effort: "M",
  wave: 1,
  persona: "dev",
  sync_on_complete: true  // Auto-sync to GitHub on completion
}
```

### PM Workflow Task Metadata (No GitHub Issue)

```javascript
{
  type: "pm-work",
  github_issues: "13-23",  // Range or array
  action: "batch-update",
  depends_on_tdd: "001",
  sync_on_complete: false  // PM work doesn't sync to single issue
}
```

### Documentation Task Metadata

```javascript
{
  github_issue: null,
  type: "documentation",
  purpose: "teach-workflow",
  deliverable: "docs/PROJECT_WORKFLOW.md",
  related_epic: 7,
  sync_on_complete: false  // Docs don't auto-sync
}
```

---

## Critical Files

### Directory Structure

```
.claude/
├── scripts/
│   ├── core/                    # Phase 1
│   │   ├── validate-metadata.sh
│   │   └── task-helpers.sh
│   ├── github-sync/             # Phases 2-3
│   │   ├── issue-to-task.sh
│   │   └── task-to-status.sh
│   └── workflows/               # Phases 4-5
│       ├── epic-workflow.sh
│       ├── update-epic-tasks.sh
│       └── task-cleanup.sh
├── scripts/README.md
```

### New Files to Create

| Phase | File | Purpose |
|-------|------|---------|
| 0 | `temp/phase0-discovery-notes.md` | Discovery findings |
| 1 | `.claude/scripts/core/validate-metadata.sh` | Metadata validation |
| 1 | `.claude/scripts/core/task-helpers.sh` | Utility functions |
| 1 | `docs/tdd/TDD-XXX-Task-Integration-Architecture.d2` | Architecture diagram |
| 1 | `docs/CLAUDE_TASK_INTEGRATION.md` | Integration guide |
| 2 | `.claude/scripts/github-sync/issue-to-task.sh` | GitHub → Claude conversion |
| 2 | `.claude/scripts/README.md` | Script documentation |
| 3 | `.claude/scripts/github-sync/task-to-status.sh` | Claude → GitHub sync |
| 4 | `.claude/scripts/workflows/epic-workflow.sh` | Epic orchestration |
| 4 | `.claude/scripts/workflows/update-epic-tasks.sh` | Batch task updates |
| 5 | `.claude/scripts/workflows/task-cleanup.sh` | Cleanup old tasks |

### Files to Update

| Phase | File | Changes |
|-------|------|---------|
| 2 | `docs/PROJECT_BOARD_GUIDE.md` | Add "Claude Task Integration" section |
| 4 | `.claude/agents/AGENTS.md` | Add "Task Metadata Standards" section |
| 4 | `.claude/agents/product-manager.md` | Add "Epic → TDD → Task Workflow" section |

---

## Workflow Examples

### Example 1: Starting Epic Work

```bash
# User: "Start implementing Epic #7"

# 1. Run epic workflow script
./claude/scripts/epic-workflow.sh 7

# Creates Claude tasks:
# - Task #1: "Architect: Create TDD-001" (metadata: {github_issue: 7, type: "tdd"})
# - Task #2: "PM: Update tasks #13-23" (blocked by #1)
# - Task #3: "PM: Document workflow" (blocked by #2)

# 2. Architect creates TDD-001
# 3. Mark Task #1 complete → auto-syncs to Epic #7
# 4. Task #2 unblocks → PM updates GitHub tasks
```

### Example 2: Implementing a Task

```bash
# User: "Work on task T1.2 (GitHub #14)"

# 1. Convert GitHub issue to Claude task
node .claude/scripts/issue-to-task.js 14

# Creates Claude Task #5:
# - Subject: "Implement SM-2 algorithm per TDD-001 §3"
# - Metadata: {github_issue: 14, task_id: "T1.2", tdd_section: "§3"}

# 2. Developer implements per TDD
# 3. Mark Task #5 complete → auto-syncs to #14 (status → review)
```

### Example 3: Auto-Sync on Completion

```javascript
// When TaskUpdate({taskId: 5, status: "completed"}) called:

// 1. Hook reads task metadata: {github_issue: 14}
// 2. Updates GitHub issue #14:
//    - Remove label: status:in-dev
//    - Add label: status:review
//    - Add comment: "✅ Completed via Claude task #5"
// 3. Developer gets confirmation in terminal
```

---

## Verification Steps

### Phase 0 Verification

- [ ] Task created in session A is visible in session B
- [ ] Task metadata persists correctly
- [ ] Prototype issue-to-task conversion works for Epic #7
- [ ] Prototype conversion works for Task #14
- [ ] Discovery notes document findings

### Phase 1 Verification (MVP Part 1)

- [ ] `validate-metadata.sh` rejects invalid metadata
- [ ] `validate-metadata.sh` accepts all valid metadata types
- [ ] Architecture diagram shows all 4 layers
- [ ] Documentation explains metadata schema
- [ ] Task persistence configured and verified

### Phase 2 Verification (MVP Part 2)

- [ ] `issue-to-task.sh 7` generates correct Epic TaskCreate call
- [ ] `issue-to-task.sh 14` generates correct Task TaskCreate call
- [ ] Generated metadata passes validation
- [ ] Output can be copy-pasted to create task
- [ ] README documents usage with examples

### MVP Checkpoint Review

- [ ] Manual GitHub → Claude conversion works
- [ ] Metadata validation layer functional
- [ ] Architecture documented
- [ ] Basic usage documented
- **Decision**: Proceed with Phases 3-5 or stop at MVP?

### Phase 3 Verification (If Implemented)

- [ ] `task-to-status.sh` updates GitHub issue correctly
- [ ] Opt-in flag (`sync_on_complete: true`) respected
- [ ] Tasks without flag don't sync
- [ ] Comment added to GitHub issue
- [ ] Tasks without `github_issue` handled gracefully

### Phase 4 Verification (If Implemented)

- [ ] `epic-workflow.sh 7` succeeds for well-formed Epic
- [ ] Script validates Epic type before proceeding
- [ ] Script handles missing PRD link gracefully
- [ ] Error messages are clear
- [ ] Generated tasks have correct metadata

### Phase 5 Verification (If Implemented)

- [ ] `task-cleanup.sh` identifies old tasks correctly
- [ ] Retention period configurable
- [ ] All scripts handle `gh` CLI errors gracefully
- [ ] Workflow diagrams complete
- [ ] FAQ section answers common questions

---

## Success Criteria

### MVP Success Criteria (Phases 0-2)

- ✅ Task persistence works across sessions
- ✅ Metadata schema defined and validated
- ✅ GitHub issues convert to Claude tasks with correct metadata
- ✅ Architecture documented with diagrams
- ✅ Manual workflow documented with examples
- ✅ Integration enhances (not replaces) GitHub workflow

### Full Implementation Success Criteria (Phases 3-5, Optional)

- ✅ Opt-in task completion → GitHub sync works
- ✅ Epic workflow creates TDD → Task update chain with error handling
- ✅ Cleanup removes old completed tasks (configurable retention)
- ✅ Comprehensive documentation with 5+ examples
- ✅ FAQ covers common edge cases
- ✅ All scripts handle errors gracefully

---

## Notes

### Core Principles

- **GitHub remains source of truth**: Don't create GitHub issues from Claude tasks automatically
- **Metadata is critical**: All scripts rely on consistent, validated metadata schema
- **Opt-in by default**: Auto-sync must be explicitly enabled via metadata flag
- **Bash over Node.js**: Simpler, fewer dependencies, better for CLI operations
- **Validation layer**: All metadata validated before use
- **Error handling**: Scripts fail gracefully with helpful messages

### Development Guidelines

- **Test incrementally**: Verify each phase before moving to next
- **Documentation first**: Write docs as you build, not after
- **MVP checkpoint**: Evaluate value before proceeding to Phases 3-5
- **Prototype before committing**: Phase 0 validates assumptions
- **Use jq for JSON**: Standard, powerful, widely available

---

## Implementation Strategy

### Immediate Actions (Phase 0)

1. Test task persistence mechanism
2. Prototype issue-to-task conversion
3. Validate metadata schema design
4. Document findings in `temp/phase0-discovery-notes.md`

### MVP Path (Phases 1-2)

1. Build metadata validation layer
2. Create architecture documentation
3. Implement manual GitHub → Claude conversion
4. Document basic usage patterns

### Evaluation Checkpoint

After MVP complete, evaluate:

- Is manual workflow sufficient?
- Do we need auto-sync (Phase 3)?
- Is Epic orchestration valuable (Phase 4)?
- What polish is needed (Phase 5)?

### Full Implementation (If Approved)

1. Implement opt-in sync (Phase 3)
2. Add Epic workflow automation (Phase 4)
3. Polish with cleanup and comprehensive docs (Phase 5)

---

## Next Steps After Approval

1. **Create feature branch**: `feat/claude-task-github-integration`
2. **Start with Phase 0** (Discovery - 1-2 hours)
   - Validate task persistence
   - Prototype scripts
   - Document findings
3. **Proceed to Phase 1** (Foundation)
   - Create validation layer
   - Build architecture docs
4. **Complete Phase 2** (Pull Integration)
   - Implement issue-to-task.sh
   - Document usage
5. **MVP Checkpoint**: Evaluate before Phases 3-5
6. **Create PR** after MVP or full implementation (depending on decision)
