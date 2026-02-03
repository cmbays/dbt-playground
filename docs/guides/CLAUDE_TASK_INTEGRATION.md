---
audience: [pm, architect, multi-agent]
priority: medium
size: large
dependencies: [PROJECT_WORKFLOW]
last_updated: 2026-02-02
status: active
tags: [workflow, claude-tasks, coordination]
---

# Claude Task GitHub Integration Guide

**Version**: v0.4 (Issue-ID Naming Convention)
**Last Updated**: 2026-02-02
**Status**: Active

---

## Table of Contents

1. [Overview](#overview)
2. [Task File Naming Convention](#task-file-naming-convention)
3. [Architecture](#architecture)
4. [Metadata Schema](#metadata-schema)
5. [Validation Rules](#validation-rules)
6. [Usage Examples](#usage-examples)
7. [Script Reference](#script-reference)
8. [Workflows](#workflows)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

---

## Overview

### Purpose

The Claude Task GitHub Integration system enables cross-session task persistence and seamless conversion between GitHub issues and Claude Code tasks. This allows multi-agent workflows to coordinate across sessions with validated metadata and formal dependency tracking.

### Key Features

- **Cross-Session Persistence**: Tasks survive Claude session restarts
- **Metadata Validation**: Schema-based validation prevents errors
- **GitHub Integration**: Convert GitHub issues to Claude tasks
- **Dependency Tracking**: Epic → TDD → Task relationships preserved
- **Opt-in Sync** (Phase 3+): Auto-sync task completion to GitHub

### When to Use

**Use Claude Tasks for**:

- Session-level work coordination between agents
- Breaking down GitHub issues into implementation sub-tasks
- Tracking progress within a single coding session
- Agent handoffs (PM → Architect → Developer → Reviewer)

**Use GitHub Issues for**:

- Long-term project planning and roadmap
- External visibility and collaboration
- Milestone tracking and release planning
- Source of truth for project management

---

## Task File Naming Convention

### Overview (v0.10+)

Task files in `backlog/tasks/` use the GitHub issue ID as the filename for direct traceability.

### New Convention

**Pattern**: `issue-{N}.md` where `{N}` is the GitHub issue number.

**Examples**:

| GitHub Issue | Task File |
|--------------|-----------|
| #161 | `backlog/tasks/issue-161.md` |
| #170 | `backlog/tasks/issue-170.md` |

### Legacy Convention

Existing files using `task-{N} - {Title}.md` pattern remain valid and are not renamed.

**Legacy Examples**:

```
backlog/tasks/task-2 - API-Test-Task.md
backlog/tasks/task-12 - E2E-Test-Multi-worktree-task-visibility.md
```

Both patterns coexist. The system detects file format automatically.

### Task File Schema

New task files include the `github_issue` field for direct linking:

```yaml
---
id: TASK-161
github_issue: 161           # Direct link to GitHub issue
title: 'Create CODEOWNERS file'
status: UNDERSTAND
assignee: []
created_date: '2026-02-02'
labels:
  - enhancement
  - ci/cd
dependencies: []
priority: high
epic_issue: 147             # Parent Epic (optional)
milestone: v0.10            # Milestone (optional)
prd: docs/specs/PRD-029-GITHUB-INTEGRATION.md  # PRD reference (optional)
---

## Description

<!-- Auto-generated from GitHub issue #161 -->
<!-- Edit in GitHub issue for single source of truth -->

See: https://github.com/cmbays/dbt-playground/issues/161
```

### Schema Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Task identifier (e.g., TASK-161) |
| `github_issue` | integer | Recommended | GitHub issue number |
| `title` | string | Yes | Task title |
| `status` | string | Yes | Workflow status |
| `assignee` | array | Yes | Assigned agents/sessions |
| `created_date` | string | Yes | Creation date |
| `labels` | array | Yes | GitHub labels |
| `dependencies` | array | Yes | Blocking tasks |
| `priority` | string | Yes | Priority level |
| `epic_issue` | integer | No | Parent Epic issue number |
| `milestone` | string | No | Target milestone |
| `prd` | string | No | Related PRD document path |

**Note**: The automatic `task-file-sync` workflow generates files with core fields only. Manually-created task files may include extended metadata (`epic_issue`, `milestone`, `prd`) which are fully supported by tooling.

### Automatic Task File Creation

When using the task-file-sync GitHub workflow (v0.10+), task files are automatically created when issues are opened with the `task` or `type:task` label.

**Trigger**: Issue opened with task label
**Result**: `backlog/tasks/issue-{N}.md` created automatically
**Archive**: File moved to `backlog/archive/tasks/` on issue close

---

## Architecture

### 4-Layer System

```
┌─────────────────────────────────────────────────┐
│ Layer 4: Workflow Orchestration (Phase 4+)     │
│ - epic-workflow.sh, update-epic-tasks.sh        │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ Layer 3: GitHub Sync Scripts (Phases 2-3)      │
│ - issue-to-task.sh, task-to-status.sh           │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ Layer 2: Metadata Validation (Phase 1)         │
│ - validate-metadata.sh, task-helpers.sh         │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ Layer 1: Core Primitives (Claude Code)         │
│ - TaskCreate, TaskUpdate, TaskList, TaskGet     │
└─────────────────────────────────────────────────┘
```

**MVP (Phases 0-2)** delivers Layers 1-3 (Layer 3 pull integration only).

### Data Flow

**Pull Integration (Phase 2)**:

```
GitHub Issue → issue-to-task.sh → validate-metadata.sh → TaskCreate → Claude Task
```

**Push Integration (Phase 3+)**:

```
Claude Task (completed) → task-to-status.sh → gh CLI → GitHub Issue (status update)
```

---

## Metadata Schema

All task metadata must include a `type` field and conform to type-specific validation rules.

### Task Types

| Type | Description | Required Fields | Optional Fields |
|------|-------------|-----------------|-----------------|
| `epic` | Parent feature issue | type, epic_id, prd | tdd, phase, tasks, github_issue, sync_on_complete |
| `task` | Implementation task | type | All others optional |
| `tdd` | TDD creation task | type, tdd_id, epic_id | deliverable, context_doc, github_issue, sync_on_complete |
| `pm-work` | PM workflow task | type | github_issues, action, depends_on_tdd |
| `documentation` | Documentation task | type | purpose, deliverable, related_epic |

### Common Fields

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `type` | string | Task type (required) | One of: epic, task, tdd, pm-work, documentation |
| `github_issue` | integer | GitHub issue number | Must be > 0 |
| `sync_on_complete` | boolean | Enable auto-sync on completion | Default: false |

---

## Validation Rules

### Pattern Validation

| Field | Pattern | Valid Examples | Invalid Examples |
|-------|---------|----------------|------------------|
| `epic_id` | `^PRD-\d{3}$` | PRD-001, PRD-042 | PRD-1, prd-001, PRD-1234 |
| `tdd_id` | `^\d{3}$` | 001, 042, 999 | 1, TDD-001, 42 |
| `tdd_section` | `^§\d+$` | §3, §12, §100 | section3, S3, para3 |
| `effort` | `^(S\|M\|L\|XL)$` | S, M, L, XL | SMALL, s, medium |

### Type-Specific Validation

#### Epic Metadata

```javascript
{
  "type": "epic",           // Required
  "epic_id": "PRD-001",    // Required, must match PRD-\d{3}
  "prd": "docs/specs/PRD-001-Feature.md",  // Required
  "tdd": "docs/specs/TDD-001-Feature.md",    // Optional
  "phase": 1,              // Optional
  "tasks": [13, 14, 15],   // Optional, array of issue numbers
  "github_issue": 7,       // Optional but recommended
  "sync_on_complete": false // Optional, default false
}
```

**Validation**: Must have `epic_id` matching pattern and `prd` field.

#### Task Metadata

```javascript
{
  "type": "task",          // Required
  "github_issue": 14,      // Optional but recommended
  "task_id": "T1.2",       // Optional
  "epic": 7,               // Optional, parent Epic issue number
  "tdd_section": "§3",     // Optional, must match §\d+
  "effort": "M",           // Optional, must be S/M/L/XL
  "wave": 1,               // Optional
  "persona": "dev",        // Optional
  "sync_on_complete": true // Optional, default false
}
```

**Validation**: No required fields beyond `type`. Optional fields validated if present.

#### TDD Metadata

```javascript
{
  "type": "tdd",                 // Required
  "tdd_id": "001",               // Required, must be 3 digits
  "epic_id": "PRD-001",          // Required, must match PRD-\d{3}
  "github_issue": 7,             // Optional
  "deliverable": "docs/specs/TDD-001.md",  // Optional
  "context_doc": "temp/TDD-001-CONTEXT.md",  // Optional
  "sync_on_complete": true       // Optional
}
```

**Validation**: Must have `tdd_id` (3 digits) and `epic_id` (PRD-XXX format).

#### PM Work Metadata

```javascript
{
  "type": "pm-work",       // Required
  "github_issues": "13-23", // Optional
  "action": "batch-update", // Optional
  "depends_on_tdd": "001"  // Optional
}
```

**Validation**: Only `type` required.

#### Documentation Metadata

```javascript
{
  "type": "documentation",  // Required
  "purpose": "teach-workflow",  // Optional
  "deliverable": "docs/PROJECT_WORKFLOW.md",  // Optional
  "related_epic": 7        // Optional
}
```

**Validation**: Only `type` required.

---

## Usage Examples

### Example 1: Epic Task Creation

```javascript
TaskCreate({
  subject: "Epic: JLPT Mastery Engine",
  description: "Implement spaced repetition system for JLPT kanji learning...",
  metadata: {
    github_issue: 7,
    type: "epic",
    epic_id: "PRD-001",
    prd: "docs/specs/PRD-001-JLPT-Mastery-Engine.md",
    tdd: "docs/specs/TDD-001-JLPT-Mastery-Engine.md",
    phase: 1,
    tasks: [13, 14, 15, 16],
    sync_on_complete: false
  }
})
```

### Example 2: Implementation Task Creation

```javascript
TaskCreate({
  subject: "Implement SM-2 algorithm per TDD-001 §3",
  description: "Core spaced repetition algorithm...",
  metadata: {
    github_issue: 14,
    type: "task",
    task_id: "T1.2",
    epic: 7,
    tdd_section: "§3",
    effort: "M",
    wave: 1,
    persona: "dev",
    sync_on_complete: true
  }
})
```

### Example 3: TDD Creation Task

```javascript
TaskCreate({
  subject: "Create TDD-001: JLPT Mastery Engine",
  description: "Technical design document for Epic #7...",
  metadata: {
    github_issue: 7,
    type: "tdd",
    tdd_id: "001",
    epic_id: "PRD-001",
    deliverable: "docs/specs/TDD-001-JLPT-Mastery-Engine.md",
    sync_on_complete: true
  }
})
```

### Example 4: Documentation Task

```javascript
TaskCreate({
  subject: "Document Claude Task Integration workflow",
  description: "Create user guide for task integration...",
  metadata: {
    type: "documentation",
    purpose: "teach-workflow",
    deliverable: "docs/CLAUDE_TASK_INTEGRATION.md"
  }
})
```

---

## Script Reference

### validate-metadata.sh

**Location**: `.claude/scripts/core/validate-metadata.sh`

**Purpose**: Validates Claude task metadata against JSON schema

**Usage**:

```bash
.claude/scripts/core/validate-metadata.sh '<metadata-json>'
```

**Examples**:

```bash
# Valid Epic metadata
.claude/scripts/core/validate-metadata.sh '{
  "type": "epic",
  "epic_id": "PRD-001",
  "prd": "docs/specs/PRD-001.md",
  "github_issue": 7
}'
# → Exit 0, stderr: "✓ Metadata valid: type=epic"

# Invalid metadata (missing required field)
.claude/scripts/core/validate-metadata.sh '{
  "type": "epic",
  "prd": "docs/specs/PRD-001.md"
}'
# → Exit 1, stderr: "ERROR: Epic requires 'epic_id' field"
```

**Exit Codes**:

- `0` - Metadata is valid
- `1` - Metadata is invalid (schema violation)
- `2` - System error (jq missing, invalid JSON syntax)

---

### task-helpers.sh

**Location**: `.claude/scripts/core/task-helpers.sh`

**Purpose**: Utility functions for metadata extraction and formatting

**Usage**:

```bash
source .claude/scripts/core/task-helpers.sh

# Extract fields
METADATA='{"type": "epic", "github_issue": 7}'
get_github_issue "$METADATA"    # → 7
get_task_type "$METADATA"       # → epic
is_sync_enabled "$METADATA"     # → false

# Build metadata
build_epic_metadata 7 "PRD-001" "docs/specs/PRD-001.md"
build_task_metadata 14 "T1.2" 7 "§3"
```

**Functions**:

- `get_github_issue` - Extract GitHub issue number
- `get_task_type` - Extract task type
- `is_sync_enabled` - Check if sync enabled
- `format_metadata` - Pretty-print metadata JSON
- `build_epic_metadata` - Build Epic metadata JSON
- `build_task_metadata` - Build Task metadata JSON
- `get_epic_id` - Extract epic_id
- `get_tdd_section` - Extract tdd_section
- `get_effort` - Extract effort

---

### issue-to-task.sh (Phase 2)

**Location**: `.claude/scripts/github-sync/issue-to-task.sh`

**Purpose**: Converts GitHub issue to Claude TaskCreate call

**Usage**:

```bash
.claude/scripts/github-sync/issue-to-task.sh <issue-number>
```

**Examples**:

```bash
# Convert Epic issue #7
.claude/scripts/github-sync/issue-to-task.sh 7

# Output (copy-paste into Claude):
TaskCreate({
  subject: "Epic: JLPT Mastery Engine",
  description: "...",
  metadata: {
    "github_issue": 7,
    "type": "epic",
    "epic_id": "PRD-001",
    "prd": "docs/specs/PRD-001-JLPT-Mastery-Engine.md"
  }
})

# Convert Task issue #14
.claude/scripts/github-sync/issue-to-task.sh 14
```

**Exit Codes**:

- `0` - Conversion successful
- `1` - Validation error
- `2` - GitHub error (issue not found, gh CLI failed)

---

## Workflows

### Workflow 1: Convert Epic to Claude Task

**Scenario**: You want to work on Epic #7 in Claude session

**Steps**:

```bash
# 1. Convert GitHub issue to TaskCreate call
.claude/scripts/github-sync/issue-to-task.sh 7

# 2. Copy the output TaskCreate call

# 3. Paste into Claude session
# Claude will create the task with validated metadata

# 4. Verify task created
TaskList()
```

**Result**: Epic task created with full metadata, ready for agent coordination

---

### Workflow 2: Break Down Epic into Sub-Tasks

**Scenario**: Epic task exists, you want to create implementation sub-tasks

**Steps**:

```javascript
// In Claude session with Epic task already created

// Create sub-task 1
TaskCreate({
  subject: "Implement SM-2 algorithm",
  description: "Core spaced repetition algorithm per TDD-001 §3",
  metadata: {
    github_issue: 14,
    type: "task",
    epic: 7,
    tdd_section: "§3",
    effort: "M"
  }
})

// Create sub-task 2
TaskCreate({
  subject: "Build review queue UI",
  description: "User interface for review sessions per TDD-001 §5",
  metadata: {
    github_issue: 15,
    type: "task",
    epic: 7,
    tdd_section: "§5",
    effort: "L"
  }
})

// Verify tasks
TaskList()
```

---

### Workflow 3: Multi-Agent Coordination

**Scenario**: PM → Architect → Developer handoff

**Phase 1: PM Creates Epic Task**:

```bash
# PM converts Epic issue to task
.claude/scripts/github-sync/issue-to-task.sh 7
# PM creates task in Claude session
```

**Phase 2: Architect Creates TDD Task**:

```javascript
// Architect sees Epic task via TaskList()
// Creates TDD task linked to Epic
TaskCreate({
  subject: "Create TDD-001 for JLPT Engine",
  metadata: {
    type: "tdd",
    tdd_id: "001",
    epic_id: "PRD-001",
    github_issue: 7
  }
})
```

**Phase 3: Developer Works on Implementation**:

```javascript
// Developer sees both Epic and TDD tasks
// Creates implementation task
TaskCreate({
  subject: "Implement SM-2 algorithm",
  metadata: {
    type: "task",
    epic: 7,
    tdd_section: "§3"
  }
})

// Developer completes work
TaskUpdate({
  taskId: "<task-id>",
  status: "completed"
})
```

**Result**: Full Epic → TDD → Task workflow tracked with metadata

---

## Troubleshooting

### Issue: Validation fails with "Invalid JSON syntax"

**Cause**: Malformed JSON in metadata string

**Solution**:

```bash
# Test JSON syntax first
echo '{"type": "epic"}' | jq .

# If jq errors, fix JSON syntax
# Common issues: missing quotes, trailing commas, unescaped characters
```

---

### Issue: "Epic requires 'epic_id' field"

**Cause**: Epic metadata missing required field

**Solution**:

```javascript
// ❌ Invalid
{
  "type": "epic",
  "prd": "docs/specs/PRD-001.md"
}

// ✅ Valid
{
  "type": "epic",
  "epic_id": "PRD-001",
  "prd": "docs/specs/PRD-001.md"
}
```

---

### Issue: "epic_id must match pattern PRD-XXX"

**Cause**: Epic ID doesn't follow required format

**Solution**:

```javascript
// ❌ Invalid patterns
"epic_id": "PRD-1"      // Need 3 digits
"epic_id": "prd-001"    // Must be uppercase
"epic_id": "PRD-1234"   // Too many digits

// ✅ Valid patterns
"epic_id": "PRD-001"
"epic_id": "PRD-042"
"epic_id": "PRD-999"
```

---

### Issue: "tdd_section must match pattern §N"

**Cause**: TDD section doesn't use correct format

**Solution**:

```javascript
// ❌ Invalid formats
"tdd_section": "section3"   // Must use §
"tdd_section": "S3"         // Must use §
"tdd_section": "para3"      // Must use §

// ✅ Valid formats
"tdd_section": "§3"
"tdd_section": "§12"
"tdd_section": "§100"
```

---

### Issue: "effort must be S/M/L/XL"

**Cause**: Effort value not in allowed set

**Solution**:

```javascript
// ❌ Invalid values
"effort": "SMALL"
"effort": "medium"
"effort": "s"

// ✅ Valid values
"effort": "S"
"effort": "M"
"effort": "L"
"effort": "XL"
```

---

### Issue: issue-to-task.sh fails with "gh: command not found"

**Cause**: GitHub CLI not installed

**Solution**:

```bash
# Install gh CLI
brew install gh

# Authenticate
gh auth login

# Test
gh --version
```

---

### Issue: issue-to-task.sh fails with "jq: command not found"

**Cause**: jq not installed

**Solution**:

```bash
# Install jq
brew install jq

# Test
jq --version
```

---

## FAQ

### Q: When should I use GitHub issues vs Claude tasks?

**A**:

- **GitHub issues**: Long-term planning, external visibility, milestone tracking, source of truth
- **Claude tasks**: Session-level work, agent coordination, breaking down implementation, temporary sub-tasks

### Q: Do Claude tasks persist across sessions?

**A**: Yes, Claude Code handles task persistence automatically. Tasks survive session restarts.

### Q: Can I create Claude tasks manually without scripts?

**A**: Yes, use `TaskCreate` directly with valid metadata. The scripts just automate conversion from GitHub.

### Q: What happens if I don't include `github_issue` in metadata?

**A**: Task works fine, but can't sync back to GitHub (Phase 3+). Recommended to include for traceability.

### Q: Can I update metadata after task creation?

**A**: Yes, use `TaskUpdate` with new metadata. Metadata can be updated at any time.

### Q: How do I find tasks with specific metadata?

**A**: Use `TaskList()` to see all tasks. Filter manually or use `TaskGet` to inspect individual task metadata.

### Q: What if my GitHub issue body doesn't match extraction patterns?

**A**: Script extracts what it can. Missing optional fields result in minimal metadata. You can manually edit the TaskCreate call before pasting.

### Q: Can I have multiple Epic tasks for the same GitHub issue?

**A**: Yes, but not recommended. One Epic task per Epic issue is the intended pattern.

### Q: Does metadata validation happen automatically?

**A**: No, validation is explicit via `validate-metadata.sh`. The `issue-to-task.sh` script calls validation automatically.

### Q: What's the difference between `type: "task"` and `type: "epic"`?

**A**:

- **Epic**: Parent feature, requires `epic_id` and `prd`, represents GitHub Epic issue
- **Task**: Implementation work, no required fields beyond `type`, represents implementation sub-task

---

## Related Documentation

- **PRD**: `docs/specs/PRD-004-Claude-Task-GitHub-Integration.md`
- **TDD**: `docs/specs/TDD-004-Claude-Task-GitHub-Integration.md`
- **Testing**: `temp/v0.3_TESTING-task-integration.md`
- **Discovery**: `temp/phase0-discovery-notes.md`
- **Script README**: `.claude/scripts/README.md`
- **Project Board Guide**: `docs/PROJECT_BOARD_GUIDE.md`

---

**Version History**:

- v0.4 (2026-02-02): Issue-ID naming convention, github_issue field, auto-sync workflow
- v0.3 (2026-01-25): Initial MVP (Phases 0-2)

**Maintained by**: Claude (Technical Architect / Developer)
