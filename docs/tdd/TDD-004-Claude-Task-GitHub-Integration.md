# TDD-004: Claude Task GitHub Integration MVP

**Status**: Draft
**Author**: Technical Architect (Claude)
**Created**: 2026-01-25
**Updated**: 2026-01-25

**Source PRD**: PRD-004-Claude-Task-GitHub-Integration
**Related Issue**: TBD (Epic issue to be created)
**Architecture Diagram**: Inline D2 diagrams included

---

## Overview

This Technical Design Document specifies the architecture for integrating Claude Code's task primitives with GitHub issues. The system enables cross-session task persistence, metadata-driven agent coordination, and optional bidirectional sync between Claude tasks and GitHub issues.

The design follows a 4-layer architecture:
1. **Core Primitives** (Claude Code built-in): TaskCreate, TaskUpdate, TaskList, TaskGet
2. **Metadata Validation** (Phase 1): Schema validation and utility functions
3. **GitHub Sync Scripts** (Phases 2-3): Issue-to-task conversion and status sync
4. **Workflow Orchestration** (Phases 4-5): Epic → TDD → Task automation

This TDD covers **MVP Phases 0-2**: Discovery, metadata foundation, and pull integration.

---

## Technical Approach

### Selected Option: Bash + jq Scripts with JSON Schema Validation

**Approach**: Build lightweight Bash scripts leveraging `gh` CLI and `jq` for all GitHub operations and JSON manipulation. Use JSON Schema with jq-based validation for metadata enforcement. Store all task data in Claude Code's built-in persistence mechanism (`~/.claude/tasks/`).

**Rationale**:
- **Minimal dependencies**: Bash, jq, and gh CLI are standard tools on developer machines
- **Cross-platform**: Works on macOS, Linux, Windows (WSL/Git Bash)
- **Transparency**: Scripts are readable and auditable
- **Extensibility**: Easy to enhance with additional validation rules or workflow patterns
- **Reliability**: No runtime dependencies beyond Claude Code itself

### Alternatives Considered

#### Option A: Node.js Scripts with TypeScript
**Approach**: Implement integration layer as Node.js/TypeScript scripts with npm dependencies for GitHub API interaction and JSON Schema validation.

**Pros**:
- Richer validation libraries (ajv, joi)
- Better error messages
- Type safety for maintenance
- More familiar to web developers

**Cons**:
- Additional runtime dependency (Node.js)
- Slower execution for simple operations
- Package.json dependency management overhead
- Overkill for shell-friendly operations like `gh` CLI calls

**Complexity**: Medium-High

#### Option B: Python Scripts with GitHub API Library
**Approach**: Use Python with PyGithub library for GitHub operations and jsonschema for validation.

**Pros**:
- Rich ecosystem for JSON/validation
- Good error handling
- Readable syntax

**Cons**:
- Python not guaranteed on all systems
- Additional dependency management (pip)
- Slower startup time than Bash
- Overhead for simple text processing

**Complexity**: Medium

### Decision Rationale

**Bash + jq wins for this use case** because:
1. `gh` CLI already provides authenticated GitHub operations—no need to reinvent
2. `jq` is purpose-built for JSON manipulation and widely adopted
3. Shell scripts integrate naturally with CLI-based workflows
4. Zero additional runtime dependencies beyond tools developers already have
5. Simpler to debug and maintain for infrastructure-focused scripts

---

## Architecture

### §1: 4-Layer System Architecture

```d2
direction: down

# Layer 1: Core Primitives
layer1: {
  label: "Layer 1: Core Primitives (Claude Code Built-in)"
  style.fill: "#e8f4f8"

  TaskCreate: "TaskCreate()" {
    shape: rectangle
  }
  TaskUpdate: "TaskUpdate()" {
    shape: rectangle
  }
  TaskList: "TaskList()" {
    shape: rectangle
  }
  TaskGet: "TaskGet()" {
    shape: rectangle
  }

  storage: "~/.claude/tasks/" {
    shape: cylinder
    style.fill: "#d0e8f0"
  }

  TaskCreate -> storage: persist
  TaskUpdate -> storage: persist
  TaskList -> storage: read
  TaskGet -> storage: read
}

# Layer 2: Metadata Validation
layer2: {
  label: "Layer 2: Metadata Validation (Phase 1)"
  style.fill: "#fff4e6"

  validate: "validate-metadata.sh" {
    shape: rectangle
  }
  helpers: "task-helpers.sh" {
    shape: rectangle
  }

  validate -> helpers: uses
}

# Layer 3: GitHub Sync
layer3: {
  label: "Layer 3: GitHub Sync Scripts (Phases 2-3)"
  style.fill: "#e8f5e9"

  issue_to_task: "issue-to-task.sh" {
    shape: rectangle
  }
  task_to_status: "task-to-status.sh" {
    shape: rectangle
  }

  gh_cli: "gh CLI" {
    shape: hexagon
    style.fill: "#c8e6c9"
  }
  jq: "jq" {
    shape: hexagon
    style.fill: "#c8e6c9"
  }

  issue_to_task -> gh_cli: fetch issue
  issue_to_task -> jq: parse JSON
  task_to_status -> gh_cli: update issue
}

# Layer 4: Workflow Orchestration
layer4: {
  label: "Layer 4: Workflow Orchestration (Phases 4-5)"
  style.fill: "#f3e5f5"

  epic_workflow: "epic-workflow.sh" {
    shape: rectangle
  }
  update_epic: "update-epic-tasks.sh" {
    shape: rectangle
  }
  cleanup: "task-cleanup.sh" {
    shape: rectangle
  }
}

# Connections between layers
layer4.epic_workflow -> layer3.issue_to_task: calls
layer4.update_epic -> layer3.task_to_status: calls

layer3.issue_to_task -> layer2.validate: validate metadata
layer3.task_to_status -> layer2.validate: validate metadata

layer2.validate -> layer1.TaskCreate: valid metadata
layer3.issue_to_task -> layer1.TaskCreate: creates task
layer3.task_to_status -> layer1.TaskGet: reads task
layer3.task_to_status -> layer1.TaskUpdate: updates task

# External systems
github: "GitHub Issues" {
  shape: cloud
  style.fill: "#24292e"
  style.stroke: "#0366d6"
}

github -> layer3.gh_cli: API
layer3.task_to_status -> github: update status
```

### §2: Data Flow Diagrams

#### Pull Flow: GitHub Issue → Claude Task

```d2
direction: right

user: "Christopher" {
  shape: person
}

github_issue: "GitHub Issue #14" {
  shape: document
  style.fill: "#f6f8fa"
}

script: "issue-to-task.sh 14" {
  shape: rectangle
  style.fill: "#e8f5e9"
}

gh_fetch: "gh issue view 14 --json" {
  shape: rectangle
  style.fill: "#c8e6c9"
}

parse: "Parse with jq" {
  shape: rectangle
  style.fill: "#fff9c4"
}

validate: "validate-metadata.sh" {
  shape: rectangle
  style.fill: "#fff4e6"
}

output: "TaskCreate call" {
  shape: document
  style.fill: "#e8f4f8"
}

claude_task: "Claude Task" {
  shape: cylinder
  style.fill: "#e0e0e0"
}

user -> script: run
script -> gh_fetch: fetch
gh_fetch -> github_issue: API call
github_issue -> parse: JSON response
parse -> validate: metadata JSON
validate -> output: if valid
output -> user: copy-paste
user -> claude_task: TaskCreate()
```

#### Push Flow: Claude Task → GitHub Status (Opt-in)

```d2
direction: right

task_complete: "TaskUpdate(status: completed)" {
  shape: rectangle
  style.fill: "#e8f4f8"
}

check_metadata: "Check sync_on_complete flag" {
  shape: diamond
  style.fill: "#fff9c4"
}

sync_script: "task-to-status.sh" {
  shape: rectangle
  style.fill: "#e8f5e9"
}

gh_update: "gh issue edit" {
  shape: rectangle
  style.fill: "#c8e6c9"
}

gh_comment: "gh issue comment" {
  shape: rectangle
  style.fill: "#c8e6c9"
}

github_updated: "GitHub Issue Updated" {
  shape: document
  style.fill: "#f6f8fa"
}

skip: "Skip sync" {
  shape: rectangle
  style.fill: "#ffebee"
}

task_complete -> check_metadata: trigger
check_metadata -> sync_script: if true
check_metadata -> skip: if false
sync_script -> gh_update: update labels
sync_script -> gh_comment: add comment
gh_update -> github_updated: status:review
gh_comment -> github_updated: completion note
```

### Component Descriptions

| Component | Responsibility | Language | Phase |
|-----------|----------------|----------|-------|
| **validate-metadata.sh** | Enforces JSON schema validation on task metadata | Bash + jq | 1 |
| **task-helpers.sh** | Utility functions for metadata extraction and formatting | Bash + jq | 1 |
| **issue-to-task.sh** | Converts GitHub issue to TaskCreate call with metadata | Bash + jq | 2 |
| **task-to-status.sh** | Syncs completed Claude tasks to GitHub issue status (opt-in) | Bash + jq | 3 |
| **epic-workflow.sh** | Orchestrates Epic → TDD → Task workflow automation | Bash + jq | 4 |
| **update-epic-tasks.sh** | Batch updates GitHub tasks with TDD section references | Bash + jq | 4 |
| **task-cleanup.sh** | Removes old completed tasks based on retention policy | Bash | 5 |

---

## §3: Metadata Schema Specification

### JSON Schema Definition

All task metadata must conform to this schema:

```javascript
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Claude Task Metadata Schema",
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": {
      "type": "string",
      "enum": ["epic", "task", "tdd", "pm-work", "documentation"],
      "description": "Type of task (required)"
    },
    "github_issue": {
      "type": "integer",
      "minimum": 1,
      "description": "GitHub issue number (optional but recommended)"
    },
    "sync_on_complete": {
      "type": "boolean",
      "default": false,
      "description": "Enable auto-sync on task completion (optional)"
    }
  },
  "allOf": [
    {
      "if": { "properties": { "type": { "const": "epic" } } },
      "then": {
        "required": ["epic_id", "prd"],
        "properties": {
          "epic_id": { "type": "string", "pattern": "^PRD-\\d{3}$" },
          "prd": { "type": "string" },
          "tdd": { "type": "string" },
          "phase": { "type": "integer", "minimum": 0 },
          "tasks": {
            "type": "array",
            "items": { "type": "integer", "minimum": 1 }
          }
        }
      }
    },
    {
      "if": { "properties": { "type": { "const": "task" } } },
      "then": {
        "properties": {
          "task_id": { "type": "string" },
          "epic": { "type": "integer", "minimum": 1 },
          "tdd_section": { "type": "string", "pattern": "^§\\d+$" },
          "effort": { "type": "string", "enum": ["S", "M", "L", "XL"] },
          "wave": { "type": "integer", "minimum": 1 },
          "persona": { "type": "string" }
        }
      }
    },
    {
      "if": { "properties": { "type": { "const": "tdd" } } },
      "then": {
        "required": ["tdd_id", "epic_id"],
        "properties": {
          "tdd_id": { "type": "string", "pattern": "^\\d{3}$" },
          "epic_id": { "type": "string", "pattern": "^PRD-\\d{3}$" },
          "deliverable": { "type": "string" },
          "context_doc": { "type": "string" }
        }
      }
    },
    {
      "if": { "properties": { "type": { "const": "pm-work" } } },
      "then": {
        "properties": {
          "github_issues": { "type": "string" },
          "action": { "type": "string" },
          "depends_on_tdd": { "type": "string" }
        }
      }
    },
    {
      "if": { "properties": { "type": { "const": "documentation" } } },
      "then": {
        "properties": {
          "purpose": { "type": "string" },
          "deliverable": { "type": "string" },
          "related_epic": { "type": "integer", "minimum": 1 }
        }
      }
    }
  ],
  "additionalProperties": false
}
```

### Metadata Types and Examples

#### Epic Metadata
```javascript
{
  "github_issue": 7,              // Required for traceability
  "type": "epic",                 // Required
  "epic_id": "PRD-001",          // Required: matches PRD naming
  "prd": "docs/specs/PRD-001-JLPT-Mastery-Engine.md",  // Required
  "tdd": "docs/tdd/TDD-001-JLPT-Mastery-Engine.md",    // Added after TDD creation
  "phase": 1,                     // Optional: implementation phase
  "tasks": [13, 14, 15, 16],      // Optional: child GitHub issues
  "sync_on_complete": false       // Optional: default false for Epics
}
```

**Validation Rules**:
- `epic_id` must match pattern `PRD-\d{3}` (e.g., PRD-001, PRD-042)
- `prd` must be a valid file path
- `tasks` array items must be integers > 0
- `sync_on_complete` defaults to false if omitted

#### Implementation Task Metadata
```javascript
{
  "github_issue": 14,            // Optional but recommended
  "type": "task",                // Required
  "task_id": "T1.2",             // Optional: task identifier
  "epic": 7,                     // Optional: parent Epic issue number
  "tdd_section": "§3",           // Optional: TDD section reference
  "effort": "M",                 // Optional: S/M/L/XL
  "wave": 1,                     // Optional: implementation wave
  "persona": "dev",              // Optional: responsible agent
  "sync_on_complete": true       // Optional: enable auto-sync
}
```

**Validation Rules**:
- `tdd_section` must match pattern `§\d+` (e.g., §1, §3, §12)
- `effort` must be one of: S, M, L, XL
- `epic` must be integer > 0 if present
- `sync_on_complete` defaults to false if omitted

#### TDD Creation Task Metadata
```javascript
{
  "github_issue": 7,                                      // Parent Epic
  "type": "tdd",                                          // Required
  "tdd_id": "001",                                        // Required: matches TDD numbering
  "epic_id": "PRD-001",                                   // Required: links to PRD
  "deliverable": "docs/tdd/TDD-001-JLPT-Mastery-Engine.md",
  "context_doc": "temp/TDD-001-CREATION-CONTEXT.md",
  "sync_on_complete": true                                // Update Epic when complete
}
```

**Validation Rules**:
- `tdd_id` must match pattern `\d{3}` (e.g., 001, 042)
- `epic_id` must match pattern `PRD-\d{3}`
- `deliverable` should point to `docs/tdd/` directory

#### PM Workflow Task Metadata
```javascript
{
  "type": "pm-work",                    // Required
  "github_issues": "13-23",             // Range or array representation
  "action": "batch-update",             // Type of PM work
  "depends_on_tdd": "001",              // TDD dependency
  "sync_on_complete": false             // PM work doesn't sync to single issue
}
```

#### Documentation Task Metadata
```javascript
{
  "github_issue": null,                  // Null OK for internal docs
  "type": "documentation",               // Required
  "purpose": "teach-workflow",
  "deliverable": "docs/PROJECT_WORKFLOW.md",
  "related_epic": 7,
  "sync_on_complete": false              // Docs don't auto-sync
}
```

### Schema Versioning Strategy

**Version**: Embed in metadata as `"_schema_version": "1.0.0"`

**Compatibility Rules**:
- **Patch version** (1.0.x): Add optional fields only
- **Minor version** (1.x.0): Add new task types or optional validation
- **Major version** (x.0.0): Breaking changes to required fields

**Migration Path**:
When schema changes, `validate-metadata.sh` should:
1. Check `_schema_version` field (if present)
2. Attempt to migrate older schemas automatically (minor versions)
3. Fail with clear error message for incompatible major versions

---

## §4: Validation Layer Design

### validate-metadata.sh Algorithm

```bash
#!/usr/bin/env bash
# validate-metadata.sh - Validates Claude task metadata against JSON schema
# Usage: validate-metadata.sh <metadata-json-string>
# Exit codes: 0 = valid, 1 = invalid, 2 = schema error

set -euo pipefail

METADATA="$1"

# Step 1: Parse JSON (catch syntax errors)
if ! echo "$METADATA" | jq empty 2>/dev/null; then
  echo "ERROR: Invalid JSON syntax" >&2
  exit 1
fi

# Step 2: Extract type field (required)
TYPE=$(echo "$METADATA" | jq -r '.type // empty')
if [[ -z "$TYPE" ]]; then
  echo "ERROR: Missing required field 'type'" >&2
  exit 1
fi

# Step 3: Validate type is whitelisted
VALID_TYPES=("epic" "task" "tdd" "pm-work" "documentation")
if [[ ! " ${VALID_TYPES[@]} " =~ " ${TYPE} " ]]; then
  echo "ERROR: Invalid type '$TYPE'. Must be one of: ${VALID_TYPES[*]}" >&2
  exit 1
fi

# Step 4: Validate github_issue (if present)
GITHUB_ISSUE=$(echo "$METADATA" | jq -r '.github_issue // empty')
if [[ -n "$GITHUB_ISSUE" ]]; then
  if ! [[ "$GITHUB_ISSUE" =~ ^[0-9]+$ ]] || [[ "$GITHUB_ISSUE" -lt 1 ]]; then
    echo "ERROR: github_issue must be integer > 0, got: $GITHUB_ISSUE" >&2
    exit 1
  fi
fi

# Step 5: Validate sync_on_complete (if present)
SYNC_FLAG=$(echo "$METADATA" | jq -r '.sync_on_complete // empty')
if [[ -n "$SYNC_FLAG" ]] && [[ "$SYNC_FLAG" != "true" ]] && [[ "$SYNC_FLAG" != "false" ]]; then
  echo "ERROR: sync_on_complete must be boolean, got: $SYNC_FLAG" >&2
  exit 1
fi

# Step 6: Type-specific validation
case "$TYPE" in
  epic)
    # Epic requires: epic_id, prd
    EPIC_ID=$(echo "$METADATA" | jq -r '.epic_id // empty')
    PRD=$(echo "$METADATA" | jq -r '.prd // empty')

    if [[ -z "$EPIC_ID" ]]; then
      echo "ERROR: Epic requires 'epic_id' field" >&2
      exit 1
    fi

    if ! [[ "$EPIC_ID" =~ ^PRD-[0-9]{3}$ ]]; then
      echo "ERROR: epic_id must match pattern PRD-XXX, got: $EPIC_ID" >&2
      exit 1
    fi

    if [[ -z "$PRD" ]]; then
      echo "ERROR: Epic requires 'prd' field" >&2
      exit 1
    fi
    ;;

  task)
    # Task optional fields: validate if present
    TDD_SECTION=$(echo "$METADATA" | jq -r '.tdd_section // empty')
    EFFORT=$(echo "$METADATA" | jq -r '.effort // empty')

    if [[ -n "$TDD_SECTION" ]] && ! [[ "$TDD_SECTION" =~ ^§[0-9]+$ ]]; then
      echo "ERROR: tdd_section must match pattern §N, got: $TDD_SECTION" >&2
      exit 1
    fi

    if [[ -n "$EFFORT" ]] && ! [[ "$EFFORT" =~ ^(S|M|L|XL)$ ]]; then
      echo "ERROR: effort must be S/M/L/XL, got: $EFFORT" >&2
      exit 1
    fi
    ;;

  tdd)
    # TDD requires: tdd_id, epic_id
    TDD_ID=$(echo "$METADATA" | jq -r '.tdd_id // empty')
    EPIC_ID=$(echo "$METADATA" | jq -r '.epic_id // empty')

    if [[ -z "$TDD_ID" ]]; then
      echo "ERROR: TDD requires 'tdd_id' field" >&2
      exit 1
    fi

    if ! [[ "$TDD_ID" =~ ^[0-9]{3}$ ]]; then
      echo "ERROR: tdd_id must be 3 digits (001-999), got: $TDD_ID" >&2
      exit 1
    fi

    if [[ -z "$EPIC_ID" ]]; then
      echo "ERROR: TDD requires 'epic_id' field" >&2
      exit 1
    fi

    if ! [[ "$EPIC_ID" =~ ^PRD-[0-9]{3}$ ]]; then
      echo "ERROR: epic_id must match pattern PRD-XXX, got: $EPIC_ID" >&2
      exit 1
    fi
    ;;

  pm-work|documentation)
    # No required fields beyond 'type'
    ;;
esac

# Step 7: All validations passed
echo "✓ Metadata valid: type=$TYPE" >&2
exit 0
```

### Validation Error Codes

| Exit Code | Meaning | Example |
|-----------|---------|---------|
| 0 | Valid metadata | All checks passed |
| 1 | Schema violation | Missing required field, invalid pattern |
| 2 | System error | jq not installed, file not found |

### Error Messages

All error messages follow this pattern:
```
ERROR: <field-name> <constraint> [actual-value]
```

Examples:
```
ERROR: Missing required field 'type'
ERROR: Invalid type 'bug'. Must be one of: epic task tdd pm-work documentation
ERROR: github_issue must be integer > 0, got: abc
ERROR: tdd_section must match pattern §N, got: section3
ERROR: epic_id must match pattern PRD-XXX, got: PRD-1
```

### jq Validation Patterns

```bash
# Check field exists
FIELD=$(echo "$JSON" | jq -r '.fieldname // empty')
if [[ -z "$FIELD" ]]; then
  echo "ERROR: Missing required field 'fieldname'" >&2
  exit 1
fi

# Validate enum value
if ! [[ "$VALUE" =~ ^(option1|option2|option3)$ ]]; then
  echo "ERROR: field must be option1/option2/option3, got: $VALUE" >&2
  exit 1
fi

# Validate pattern (regex)
if ! [[ "$VALUE" =~ ^§[0-9]+$ ]]; then
  echo "ERROR: field must match pattern §N, got: $VALUE" >&2
  exit 1
fi

# Validate integer > 0
if ! [[ "$VALUE" =~ ^[0-9]+$ ]] || [[ "$VALUE" -lt 1 ]]; then
  echo "ERROR: field must be integer > 0, got: $VALUE" >&2
  exit 1
fi

# Validate boolean
if [[ "$VALUE" != "true" ]] && [[ "$VALUE" != "false" ]]; then
  echo "ERROR: field must be boolean, got: $VALUE" >&2
  exit 1
fi
```

---

## §5: GitHub Sync Scripts

### issue-to-task.sh Detailed Algorithm

```bash
#!/usr/bin/env bash
# issue-to-task.sh - Converts GitHub issue to Claude TaskCreate call
# Usage: issue-to-task.sh <issue-number>
# Output: TaskCreate call with validated metadata (stdout)
# Exit codes: 0 = success, 1 = validation error, 2 = GitHub error

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALIDATE_SCRIPT="$SCRIPT_DIR/../core/validate-metadata.sh"

# Step 1: Validate arguments
if [[ $# -ne 1 ]]; then
  echo "Usage: issue-to-task.sh <issue-number>" >&2
  exit 2
fi

ISSUE_NUM="$1"

if ! [[ "$ISSUE_NUM" =~ ^[0-9]+$ ]]; then
  echo "ERROR: Issue number must be integer, got: $ISSUE_NUM" >&2
  exit 2
fi

# Step 2: Fetch issue from GitHub
echo "Fetching GitHub issue #$ISSUE_NUM..." >&2

ISSUE_JSON=$(gh issue view "$ISSUE_NUM" --json title,body,labels,number 2>&1)
if [[ $? -ne 0 ]]; then
  echo "ERROR: Failed to fetch issue #$ISSUE_NUM" >&2
  echo "$ISSUE_JSON" >&2
  exit 2
fi

# Step 3: Extract basic fields
TITLE=$(echo "$ISSUE_JSON" | jq -r '.title')
BODY=$(echo "$ISSUE_JSON" | jq -r '.body // ""')
LABELS=$(echo "$ISSUE_JSON" | jq -r '.labels[].name' | tr '\n' ',' | sed 's/,$//')

echo "Issue: $TITLE" >&2
echo "Labels: $LABELS" >&2

# Step 4: Parse type from labels
TYPE=$(echo "$LABELS" | grep -oE 'type:[^,]+' | cut -d':' -f2 || echo "")

if [[ -z "$TYPE" ]]; then
  echo "ERROR: No type: label found on issue #$ISSUE_NUM" >&2
  echo "Available labels: $LABELS" >&2
  exit 1
fi

# Step 5: Extract metadata based on type
case "$TYPE" in
  epic)
    # Extract epic_id from body (format: "Epic ID: PRD-001" or "**Epic**: PRD-001")
    EPIC_ID=$(echo "$BODY" | grep -oP '(?:Epic ID|Epic):\s*\K[A-Z]+-\d+' | head -1 || echo "")

    # Extract PRD link (format: "PRD: docs/specs/..." or "[PRD](docs/specs/...)")
    PRD=$(echo "$BODY" | grep -oP '(?:PRD:\s*|PRD\]\()\K[^\s)]+' | head -1 || echo "")

    # Extract TDD link (format: "TDD: docs/tdd/..." or "[TDD](docs/tdd/...)")
    TDD=$(echo "$BODY" | grep -oP '(?:TDD:\s*|TDD\]\()\K[^\s)]+' | head -1 || echo "")

    # Build metadata JSON
    METADATA=$(jq -n \
      --arg github_issue "$ISSUE_NUM" \
      --arg type "$TYPE" \
      --arg epic_id "$EPIC_ID" \
      --arg prd "$PRD" \
      --arg tdd "$TDD" \
      '{
        github_issue: ($github_issue | tonumber),
        type: $type,
        epic_id: $epic_id,
        prd: $prd
      } + (if $tdd != "" then {tdd: $tdd} else {} end)')
    ;;

  task)
    # Extract epic reference (format: "Epic: #7" or "Part of #7")
    EPIC=$(echo "$BODY" | grep -oP '(?:Epic|Part of):\s*#\K\d+' | head -1 || echo "")

    # Extract TDD section (format: "Implements: §3" or "TDD Section: §3")
    TDD_SECTION=$(echo "$BODY" | grep -oP '(?:Implements|TDD Section):\s*\K§\d+' | head -1 || echo "")

    # Extract task ID (format: "Task ID: T1.2" or "**Task**: T1.2")
    TASK_ID=$(echo "$BODY" | grep -oP '(?:Task ID|Task):\s*\K[A-Z0-9.]+' | head -1 || echo "")

    # Extract effort from labels
    EFFORT=$(echo "$LABELS" | grep -oE 'effort:[^,]+' | cut -d':' -f2 || echo "")

    # Build metadata JSON
    METADATA=$(jq -n \
      --arg github_issue "$ISSUE_NUM" \
      --arg type "$TYPE" \
      --arg task_id "$TASK_ID" \
      --arg epic "$EPIC" \
      --arg tdd_section "$TDD_SECTION" \
      --arg effort "$EFFORT" \
      '{
        github_issue: ($github_issue | tonumber),
        type: $type
      } + (if $task_id != "" then {task_id: $task_id} else {} end)
        + (if $epic != "" then {epic: ($epic | tonumber)} else {} end)
        + (if $tdd_section != "" then {tdd_section: $tdd_section} else {} end)
        + (if $effort != "" then {effort: $effort} else {} end)
        + {sync_on_complete: true}')
    ;;

  tdd)
    # Extract TDD ID from body
    TDD_ID=$(echo "$BODY" | grep -oP '(?:TDD ID|TDD):\s*\K\d+' | head -1 || echo "")

    # Extract Epic ID
    EPIC_ID=$(echo "$BODY" | grep -oP '(?:Epic ID|Epic):\s*\K[A-Z]+-\d+' | head -1 || echo "")

    # Build metadata JSON
    METADATA=$(jq -n \
      --arg github_issue "$ISSUE_NUM" \
      --arg type "$TYPE" \
      --arg tdd_id "$TDD_ID" \
      --arg epic_id "$EPIC_ID" \
      '{
        github_issue: ($github_issue | tonumber),
        type: $type,
        tdd_id: $tdd_id,
        epic_id: $epic_id,
        sync_on_complete: true
      }')
    ;;

  *)
    echo "ERROR: Unsupported task type: $TYPE" >&2
    exit 1
    ;;
esac

# Step 6: Validate metadata
echo "Validating metadata..." >&2

if ! "$VALIDATE_SCRIPT" "$METADATA" 2>&1; then
  echo "ERROR: Metadata validation failed" >&2
  echo "Metadata: $METADATA" >&2
  exit 1
fi

# Step 7: Generate TaskCreate call
echo "Generating TaskCreate call..." >&2

# Escape body for JSON string
BODY_ESCAPED=$(echo "$BODY" | jq -Rs .)

# Format metadata for display (pretty-printed)
METADATA_PRETTY=$(echo "$METADATA" | jq .)

# Output TaskCreate call
cat <<EOF

TaskCreate({
  subject: "$TITLE",
  description: $BODY_ESCAPED,
  metadata: $METADATA_PRETTY
})

EOF

echo "✓ Conversion successful. Copy the TaskCreate call above." >&2
exit 0
```

### Label Parsing Logic

Labels follow the pattern `prefix:value`. The script extracts:

| Label Pattern | Extraction | Usage |
|--------------|------------|-------|
| `type:epic` | `TYPE=epic` | Determines task type |
| `type:task` | `TYPE=task` | Determines task type |
| `type:tdd` | `TYPE=tdd` | Determines task type |
| `effort:S` | `EFFORT=S` | Task effort estimation |
| `effort:M` | `EFFORT=M` | Task effort estimation |
| `effort:L` | `EFFORT=L` | Task effort estimation |
| `effort:XL` | `EFFORT=XL` | Task effort estimation |
| `status:*` | Ignored | Not used in metadata |
| `persona:*` | Ignored | Can be added in future |

### Body Metadata Extraction Patterns

```bash
# Epic ID: PRD-001
grep -oP '(?:Epic ID|Epic):\s*\K[A-Z]+-\d+'

# PRD: docs/specs/PRD-001.md or [PRD](docs/specs/PRD-001.md)
grep -oP '(?:PRD:\s*|PRD\]\()\K[^\s)]+'

# Epic: #7 or Part of #7
grep -oP '(?:Epic|Part of):\s*#\K\d+'

# Implements: §3 or TDD Section: §3
grep -oP '(?:Implements|TDD Section):\s*\K§\d+'

# Task ID: T1.2 or **Task**: T1.2
grep -oP '(?:Task ID|Task):\s*\K[A-Z0-9.]+'
```

### task-to-status.sh Algorithm (Phase 3)

```bash
#!/usr/bin/env bash
# task-to-status.sh - Syncs Claude task completion to GitHub
# Usage: task-to-status.sh <task-id>
# Exit codes: 0 = success, 1 = error, 2 = skipped (opt-in disabled)

set -euo pipefail

TASK_ID="$1"

# Step 1: Get task details
# NOTE: This pseudocode assumes TaskGet can be called from shell
TASK_JSON=$(claude-code-cli task get "$TASK_ID" 2>/dev/null || echo "{}")

if [[ "$TASK_JSON" == "{}" ]]; then
  echo "ERROR: Task #$TASK_ID not found" >&2
  exit 1
fi

# Step 2: Extract metadata
GITHUB_ISSUE=$(echo "$TASK_JSON" | jq -r '.metadata.github_issue // empty')
STATUS=$(echo "$TASK_JSON" | jq -r '.status')
SYNC_ENABLED=$(echo "$TASK_JSON" | jq -r '.metadata.sync_on_complete // false')

# Step 3: Check if sync is enabled
if [[ "$SYNC_ENABLED" != "true" ]]; then
  echo "Task #$TASK_ID sync not enabled (sync_on_complete: false)" >&2
  exit 2
fi

# Step 4: Check if task has GitHub issue
if [[ -z "$GITHUB_ISSUE" ]]; then
  echo "Task #$TASK_ID has no github_issue metadata" >&2
  exit 2
fi

# Step 5: Only sync if completed
if [[ "$STATUS" != "completed" ]]; then
  echo "Task #$TASK_ID not completed (status: $STATUS)" >&2
  exit 2
fi

# Step 6: Update GitHub issue
echo "Syncing task #$TASK_ID → GitHub issue #$GITHUB_ISSUE..." >&2

gh issue edit "$GITHUB_ISSUE" \
  --remove-label "status:in-dev" \
  --add-label "status:review" 2>&1

if [[ $? -ne 0 ]]; then
  echo "ERROR: Failed to update labels on issue #$GITHUB_ISSUE" >&2
  exit 1
fi

# Step 7: Add completion comment
gh issue comment "$GITHUB_ISSUE" \
  --body "✅ Completed via Claude task #$TASK_ID" 2>&1

if [[ $? -ne 0 ]]; then
  echo "WARNING: Failed to add comment to issue #$GITHUB_ISSUE" >&2
  # Don't fail on comment error
fi

echo "✓ Synced task #$TASK_ID → issue #$GITHUB_ISSUE" >&2
exit 0
```

---

## §6: API Contracts

### Script Interfaces

#### validate-metadata.sh

```bash
# INTERFACE
validate-metadata.sh <metadata-json-string>

# INPUTS
# - $1: JSON string containing metadata to validate

# OUTPUTS
# - stdout: Success message if valid
# - stderr: Error messages if invalid

# EXIT CODES
# - 0: Metadata is valid
# - 1: Metadata is invalid (schema violation)
# - 2: System error (jq missing, syntax error)

# EXAMPLES
validate-metadata.sh '{"type": "epic", "epic_id": "PRD-001", "prd": "docs/specs/PRD-001.md"}'
# → exit 0

validate-metadata.sh '{"type": "task", "tdd_section": "invalid"}'
# → exit 1, stderr: "ERROR: tdd_section must match pattern §N, got: invalid"
```

#### issue-to-task.sh

```bash
# INTERFACE
issue-to-task.sh <issue-number>

# INPUTS
# - $1: GitHub issue number (integer)

# OUTPUTS
# - stdout: TaskCreate call formatted for copy-paste
# - stderr: Progress messages and errors

# EXIT CODES
# - 0: Conversion successful
# - 1: Validation error
# - 2: GitHub error (issue not found, gh CLI failed)

# EXAMPLES
issue-to-task.sh 7
# → stdout: TaskCreate({ subject: "...", metadata: {...} })
# → exit 0

issue-to-task.sh 999999
# → stderr: "ERROR: Failed to fetch issue #999999"
# → exit 2
```

#### task-to-status.sh

```bash
# INTERFACE
task-to-status.sh <task-id>

# INPUTS
# - $1: Claude task ID (string)

# OUTPUTS
# - stdout: None
# - stderr: Progress messages and errors

# EXIT CODES
# - 0: Sync successful
# - 1: Error (GitHub update failed)
# - 2: Skipped (opt-in disabled or no github_issue)

# EXAMPLES
task-to-status.sh "task-123"
# → stderr: "✓ Synced task #task-123 → issue #14"
# → exit 0

task-to-status.sh "task-456"
# → stderr: "Task #task-456 sync not enabled (sync_on_complete: false)"
# → exit 2
```

### Helper Function Signatures (task-helpers.sh)

```bash
#!/usr/bin/env bash
# task-helpers.sh - Utility functions for Claude task metadata

# Extract github_issue from metadata JSON
# Args: $1 = metadata JSON string
# Returns: GitHub issue number or empty string
get_github_issue() {
  local metadata="$1"
  echo "$metadata" | jq -r '.github_issue // empty'
}

# Extract task type from metadata JSON
# Args: $1 = metadata JSON string
# Returns: Task type (epic, task, tdd, etc.) or empty string
get_task_type() {
  local metadata="$1"
  echo "$metadata" | jq -r '.type // empty'
}

# Check if sync is enabled
# Args: $1 = metadata JSON string
# Returns: "true" or "false"
is_sync_enabled() {
  local metadata="$1"
  echo "$metadata" | jq -r '.sync_on_complete // false'
}

# Format metadata for display (pretty-printed)
# Args: $1 = metadata JSON string
# Returns: Formatted JSON
format_metadata() {
  local metadata="$1"
  echo "$metadata" | jq .
}

# Build Epic metadata JSON
# Args: $1=issue_num, $2=epic_id, $3=prd, $4=tdd (optional)
# Returns: JSON metadata string
build_epic_metadata() {
  local issue_num="$1"
  local epic_id="$2"
  local prd="$3"
  local tdd="${4:-}"

  jq -n \
    --arg github_issue "$issue_num" \
    --arg epic_id "$epic_id" \
    --arg prd "$prd" \
    --arg tdd "$tdd" \
    '{
      github_issue: ($github_issue | tonumber),
      type: "epic",
      epic_id: $epic_id,
      prd: $prd,
      sync_on_complete: false
    } + (if $tdd != "" then {tdd: $tdd} else {} end)'
}

# Build Task metadata JSON
# Args: $1=issue_num, $2=task_id, $3=epic (optional), $4=tdd_section (optional)
# Returns: JSON metadata string
build_task_metadata() {
  local issue_num="$1"
  local task_id="${2:-}"
  local epic="${3:-}"
  local tdd_section="${4:-}"

  jq -n \
    --arg github_issue "$issue_num" \
    --arg task_id "$task_id" \
    --arg epic "$epic" \
    --arg tdd_section "$tdd_section" \
    '{
      github_issue: ($github_issue | tonumber),
      type: "task",
      sync_on_complete: true
    } + (if $task_id != "" then {task_id: $task_id} else {} end)
      + (if $epic != "" then {epic: ($epic | tonumber)} else {} end)
      + (if $tdd_section != "" then {tdd_section: $tdd_section} else {} end)'
}
```

### Error Handling Protocols

All scripts follow these conventions:

1. **Exit codes**:
   - 0 = Success
   - 1 = Validation/logic error
   - 2 = System/external error

2. **Error output**:
   - All errors go to stderr
   - Format: `ERROR: <description>`
   - Include context (actual value, expected format)

3. **Progress output**:
   - Progress messages go to stderr
   - Format: `<message>...` or `✓ <success message>`
   - Allows stdout to contain only script output

4. **Graceful degradation**:
   - If optional operation fails, warn but don't fail (e.g., GitHub comment)
   - If required operation fails, fail immediately with clear error

5. **Validation order**:
   - Validate arguments first
   - Validate external dependencies (gh CLI, jq)
   - Fetch data
   - Validate data
   - Perform operation

---

## §7: Testing Strategy

### Unit Tests for Validation Logic

**Test Framework**: `bats` (Bash Automated Testing System)

```bash
# test/validate-metadata.bats

@test "validate-metadata accepts valid Epic metadata" {
  run .claude/scripts/core/validate-metadata.sh '{
    "type": "epic",
    "epic_id": "PRD-001",
    "prd": "docs/specs/PRD-001.md",
    "github_issue": 7
  }'

  [ "$status" -eq 0 ]
  [[ "$output" =~ "✓ Metadata valid: type=epic" ]]
}

@test "validate-metadata rejects Epic without epic_id" {
  run .claude/scripts/core/validate-metadata.sh '{
    "type": "epic",
    "prd": "docs/specs/PRD-001.md"
  }'

  [ "$status" -eq 1 ]
  [[ "$output" =~ "ERROR: Epic requires 'epic_id' field" ]]
}

@test "validate-metadata rejects invalid epic_id pattern" {
  run .claude/scripts/core/validate-metadata.sh '{
    "type": "epic",
    "epic_id": "PRD-1",
    "prd": "docs/specs/PRD-001.md"
  }'

  [ "$status" -eq 1 ]
  [[ "$output" =~ "ERROR: epic_id must match pattern PRD-XXX" ]]
}

@test "validate-metadata accepts valid Task metadata" {
  run .claude/scripts/core/validate-metadata.sh '{
    "type": "task",
    "github_issue": 14,
    "tdd_section": "§3",
    "effort": "M"
  }'

  [ "$status" -eq 0 ]
}

@test "validate-metadata rejects invalid tdd_section pattern" {
  run .claude/scripts/core/validate-metadata.sh '{
    "type": "task",
    "tdd_section": "section3"
  }'

  [ "$status" -eq 1 ]
  [[ "$output" =~ "ERROR: tdd_section must match pattern §N" ]]
}

@test "validate-metadata rejects invalid effort value" {
  run .claude/scripts/core/validate-metadata.sh '{
    "type": "task",
    "effort": "HUGE"
  }'

  [ "$status" -eq 1 ]
  [[ "$output" =~ "ERROR: effort must be S/M/L/XL" ]]
}

@test "validate-metadata rejects unknown task type" {
  run .claude/scripts/core/validate-metadata.sh '{
    "type": "bug"
  }'

  [ "$status" -eq 1 ]
  [[ "$output" =~ "ERROR: Invalid type 'bug'" ]]
}

@test "validate-metadata rejects github_issue < 1" {
  run .claude/scripts/core/validate-metadata.sh '{
    "type": "task",
    "github_issue": 0
  }'

  [ "$status" -eq 1 ]
  [[ "$output" =~ "ERROR: github_issue must be integer > 0" ]]
}
```

### Integration Tests for Script Workflows

```bash
# test/issue-to-task.bats

setup() {
  # Create mock gh CLI responses
  export GH_MOCK_DIR="$BATS_TMPDIR/gh-mock"
  mkdir -p "$GH_MOCK_DIR"
}

teardown() {
  rm -rf "$GH_MOCK_DIR"
}

@test "issue-to-task converts Epic issue successfully" {
  # Mock gh issue view response
  cat > "$GH_MOCK_DIR/issue-7.json" <<EOF
{
  "title": "Epic: JLPT Mastery Engine",
  "body": "Epic ID: PRD-001\nPRD: docs/specs/PRD-001.md",
  "labels": [{"name": "type:epic"}],
  "number": 7
}
EOF

  # Mock gh CLI to return fixture
  function gh() {
    cat "$GH_MOCK_DIR/issue-7.json"
  }
  export -f gh

  run .claude/scripts/github-sync/issue-to-task.sh 7

  [ "$status" -eq 0 ]
  [[ "$output" =~ "TaskCreate" ]]
  [[ "$output" =~ '"type": "epic"' ]]
  [[ "$output" =~ '"epic_id": "PRD-001"' ]]
}

@test "issue-to-task converts Task issue successfully" {
  cat > "$GH_MOCK_DIR/issue-14.json" <<EOF
{
  "title": "Implement SM-2 algorithm",
  "body": "Epic: #7\nImplements: §3\nTask ID: T1.2",
  "labels": [{"name": "type:task"}, {"name": "effort:M"}],
  "number": 14
}
EOF

  function gh() {
    cat "$GH_MOCK_DIR/issue-14.json"
  }
  export -f gh

  run .claude/scripts/github-sync/issue-to-task.sh 14

  [ "$status" -eq 0 ]
  [[ "$output" =~ '"type": "task"' ]]
  [[ "$output" =~ '"epic": 7' ]]
  [[ "$output" =~ '"tdd_section": "§3"' ]]
  [[ "$output" =~ '"effort": "M"' ]]
}

@test "issue-to-task fails for invalid issue number" {
  function gh() {
    echo "ERROR: issue not found" >&2
    return 1
  }
  export -f gh

  run .claude/scripts/github-sync/issue-to-task.sh 999999

  [ "$status" -eq 2 ]
  [[ "$output" =~ "ERROR: Failed to fetch issue" ]]
}
```

### Edge Cases to Test

| Category | Edge Case | Expected Behavior |
|----------|-----------|-------------------|
| **Metadata Validation** | Missing required field | Exit 1, clear error message |
| | Invalid pattern (PRD-1 vs PRD-001) | Exit 1, show expected pattern |
| | Extra unknown fields | Exit 1, reject (strict schema) |
| | github_issue as string "14" | Accept (coerce to number) |
| | github_issue = 0 | Exit 1, must be > 0 |
| | sync_on_complete omitted | Accept, default to false |
| **GitHub Sync** | Issue not found (404) | Exit 2, "issue not found" |
| | No type: label on issue | Exit 1, "No type: label found" |
| | Multiple type: labels | Use first match |
| | Body missing Epic ID | Epic metadata has empty epic_id, validation fails |
| | Malformed body (no patterns match) | Metadata has empty optional fields, validation succeeds |
| **Task Sync** | Task has no github_issue | Exit 2, skip sync |
| | Task has sync_on_complete=false | Exit 2, skip sync |
| | GitHub issue already closed | gh CLI handles, comment still added |
| | Label doesn't exist | gh CLI handles, creates label |
| | Network failure | Exit 1, propagate gh error |
| **Helpers** | Empty metadata | Functions return empty strings |
| | Malformed JSON | jq errors, scripts exit 1 |
| | Null values in metadata | Treated as absent (jq `.field // empty`) |

### Manual Testing Checklist

```markdown
# Phase 0: Discovery Testing
- [ ] Create task in Claude session A
- [ ] Restart Claude (new session B)
- [ ] Verify task visible in session B with TaskList()
- [ ] Verify metadata preserved correctly

# Phase 1: Validation Testing
- [ ] validate-metadata.sh accepts all 5 valid task types
- [ ] validate-metadata.sh rejects missing required fields
- [ ] validate-metadata.sh rejects invalid patterns (epic_id, tdd_section)
- [ ] validate-metadata.sh rejects invalid enum values (type, effort)
- [ ] Error messages are clear and actionable

# Phase 2: Pull Integration Testing
- [ ] issue-to-task.sh 7 converts Epic successfully
- [ ] issue-to-task.sh 14 converts Task successfully
- [ ] Generated TaskCreate call is valid (copy-paste works)
- [ ] Metadata passes validation
- [ ] Script handles missing optional fields gracefully

# Phase 3: Push Integration Testing (If Implemented)
- [ ] task-to-status.sh syncs completed task with sync_on_complete=true
- [ ] task-to-status.sh skips task with sync_on_complete=false
- [ ] GitHub issue labels updated correctly
- [ ] GitHub issue comment added
- [ ] Script handles missing github_issue gracefully
```

---

## §8: Implementation Phases

### Phase 0: Discovery & Validation

**Duration**: 1-2 hours
**Deliverable**: `temp/phase0-discovery-notes.md`

**Tasks**:
1. **Test task persistence**
   ```bash
   # In Claude session
   TaskCreate({
     subject: "Test persistence",
     metadata: {type: "documentation", test: true}
   })

   # Record task ID
   # Exit Claude, restart
   # Verify with TaskList()
   ```

2. **Inspect task storage**
   ```bash
   ls -la ~/.claude/tasks/
   cat ~/.claude/tasks/<task-file>
   # Document file format
   ```

3. **Prototype metadata extraction**
   ```bash
   gh issue view 7 --json title,body,labels,number | jq
   # Extract epic_id, prd manually
   # Verify patterns work
   ```

4. **Document findings**
   - How persistence works
   - File format in ~/.claude/tasks/
   - Metadata preservation behavior
   - Any environment variables needed

**Acceptance Criteria**:
- [ ] Task survives session restart
- [ ] Metadata schema validated against issues #7, #14
- [ ] Prototype extraction works
- [ ] Persistence mechanism documented

**Decision Point**: If persistence doesn't work as expected, reevaluate approach.

---

### Phase 1: Foundation (MVP Part 1)

**Duration**: 3-4 hours
**Deliverable**: Validation layer + architecture docs

**Tasks**:

1. **Create validate-metadata.sh**
   - Implement full validation algorithm (see §4)
   - Test with all 5 task types
   - Test error cases

2. **Create task-helpers.sh**
   - Implement helper functions (see §6)
   - Source in other scripts

3. **Create architecture diagram**
   - D2 format (see §1)
   - All 4 layers clearly shown
   - Save to docs/tdd/TDD-004-Architecture.d2

4. **Create docs/CLAUDE_TASK_INTEGRATION.md**
   - Metadata schema documentation
   - Validation rules
   - Architecture overview
   - When to use GitHub vs Claude tasks
   - Troubleshooting section

5. **Configure task persistence** (if needed)
   - Document CLAUDE_CODE_TASK_LIST_ID
   - OR update .claude/settings.json
   - Verify works across sessions

**Acceptance Criteria**:
- [ ] validate-metadata.sh rejects invalid schemas
- [ ] validate-metadata.sh accepts all valid metadata types
- [ ] task-helpers.sh functions work correctly
- [ ] Architecture diagram shows all 4 layers
- [ ] Documentation explains metadata schema with 3+ examples
- [ ] Task persistence configured and verified

---

### Phase 2: Pull Integration (MVP Part 2)

**Duration**: 4-5 hours
**Deliverable**: issue-to-task.sh + documentation

**Tasks**:

1. **Create issue-to-task.sh**
   - Implement full algorithm (see §5)
   - Call validate-metadata.sh
   - Output TaskCreate call

2. **Test with real issues**
   ```bash
   ./claude/scripts/github-sync/issue-to-task.sh 7
   # Copy output
   # Paste in Claude session
   # Verify task created

   ./claude/scripts/github-sync/issue-to-task.sh 14
   # Verify Task metadata correct
   ```

3. **Create .claude/scripts/README.md**
   - Document all scripts in .claude/scripts/
   - Usage examples
   - Error codes
   - Troubleshooting

4. **Update docs/PROJECT_BOARD_GUIDE.md**
   - Add "Claude Task Integration" section
   - Document workflow
   - Link to detailed guide

**Acceptance Criteria**:
- [ ] Script successfully converts Epic issue to TaskCreate call
- [ ] Script successfully converts Task issue to TaskCreate call
- [ ] Metadata validation runs and catches errors
- [ ] Script output can be copy-pasted to create task
- [ ] README documents usage with examples
- [ ] PROJECT_BOARD_GUIDE updated

---

### MVP Checkpoint

**Evaluation**:
After Phase 2, assess:
1. Is manual workflow sufficient?
2. How often will we use this?
3. Is auto-sync worth the complexity?
4. Should we proceed with Phases 3-5?

**Deliverables to Review**:
- Working validation layer
- issue-to-task.sh converting issues successfully
- Complete documentation
- Architecture diagrams

**Decision**: Proceed to Phase 3 OR stop at MVP

---

## File Changes

| File | Change Type | Description | Phase |
|------|-------------|-------------|-------|
| `temp/phase0-discovery-notes.md` | Create | Discovery findings and validation results | 0 |
| `.claude/scripts/core/validate-metadata.sh` | Create | Metadata validation script | 1 |
| `.claude/scripts/core/task-helpers.sh` | Create | Utility helper functions | 1 |
| `docs/tdd/TDD-004-Architecture.d2` | Create | Architecture diagrams (D2 format) | 1 |
| `docs/CLAUDE_TASK_INTEGRATION.md` | Create | Integration guide and metadata schema docs | 1 |
| `.claude/scripts/github-sync/issue-to-task.sh` | Create | GitHub issue → Claude task conversion | 2 |
| `.claude/scripts/README.md` | Create | Script documentation and usage | 2 |
| `docs/PROJECT_BOARD_GUIDE.md` | Modify | Add Claude Task Integration section | 2 |
| `.claude/scripts/github-sync/task-to-status.sh` | Create | Claude task → GitHub status sync (opt-in) | 3 |
| `.claude/scripts/workflows/epic-workflow.sh` | Create | Epic → TDD → Task orchestration | 4 |
| `.claude/scripts/workflows/update-epic-tasks.sh` | Create | Batch task updates | 4 |
| `.claude/scripts/workflows/task-cleanup.sh` | Create | Cleanup old completed tasks | 5 |
| `.claude/agents/AGENTS.md` | Modify | Add Task Metadata Standards section | 4 |
| `.claude/agents/product-manager.md` | Modify | Add Epic workflow documentation | 4 |

---

## Implementation Sequence

### Phase 0 Sequence (Discovery)
1. Test task persistence in Claude Code
2. Inspect ~/.claude/tasks/ directory structure
3. Prototype metadata extraction from GitHub issues #7 and #14
4. Document findings in temp/phase0-discovery-notes.md
5. Make Go/No-Go decision

### Phase 1 Sequence (Foundation)
1. Create .claude/scripts/core/ directory
2. Implement validate-metadata.sh
3. Write unit tests for validation (bats)
4. Implement task-helpers.sh
5. Create architecture diagrams (D2)
6. Write docs/CLAUDE_TASK_INTEGRATION.md
7. Configure task persistence (if needed)

### Phase 2 Sequence (Pull Integration)
1. Create .claude/scripts/github-sync/ directory
2. Implement issue-to-task.sh
3. Test with Epic issue #7
4. Test with Task issue #14
5. Write integration tests (bats)
6. Create .claude/scripts/README.md
7. Update docs/PROJECT_BOARD_GUIDE.md

### Phase 3 Sequence (Push Integration - Optional)
1. Implement task-to-status.sh
2. Test opt-in sync with sync_on_complete=true
3. Test skip behavior with sync_on_complete=false
4. Document opt-in pattern in CLAUDE_TASK_INTEGRATION.md
5. Create wrapper function examples

---

## Data Structures

### Task Persistence Format (Inferred from Discovery)

```javascript
// ~/.claude/tasks/<task-id>.json (hypothetical format)
{
  "id": "task-abc123",
  "subject": "Implement SM-2 algorithm per TDD-001 §3",
  "description": "Full task description...",
  "status": "in_progress",
  "metadata": {
    "github_issue": 14,
    "type": "task",
    "task_id": "T1.2",
    "epic": 7,
    "tdd_section": "§3",
    "effort": "M",
    "sync_on_complete": true
  },
  "created_at": "2026-01-25T10:30:00Z",
  "updated_at": "2026-01-25T14:45:00Z"
}
```

### GitHub Issue Response Format

```javascript
// gh issue view <number> --json title,body,labels,number
{
  "title": "Implement SM-2 algorithm per TDD-001 §3",
  "body": "Epic: #7\nImplements: §3\nTask ID: T1.2\n\n...",
  "labels": [
    {"name": "type:task"},
    {"name": "effort:M"},
    {"name": "status:in-dev"}
  ],
  "number": 14
}
```

---

## State Management

### Task Metadata State
- **Storage**: Claude Code's built-in persistence (~/.claude/tasks/)
- **Format**: JSON (preserved exactly as provided to TaskCreate)
- **Lifecycle**: Created → In Progress → Completed → (Optional cleanup)
- **Persistence**: Survives session restarts, browser refreshes

### GitHub Issue State
- **Source of Truth**: GitHub API
- **Sync Pattern**: Pull-on-demand (Phase 2), Opt-in push (Phase 3)
- **State Fields**: Labels (status:*, effort:*), Comments

---

## Edge Cases

| Case | Handling |
|------|----------|
| **GitHub issue closed before sync** | gh CLI handles gracefully, comment still added |
| **Task has no github_issue** | Skip sync, log message |
| **Multiple type: labels on issue** | Use first match, warn in stderr |
| **Body patterns don't match** | Optional fields remain empty, validation passes if required fields present |
| **jq not installed** | Script fails with "ERROR: jq not found" |
| **gh CLI not authenticated** | Script fails with gh error message |
| **Metadata exceeds localStorage limit** | Not handled in MVP (future consideration) |
| **Task created manually (no script)** | Works fine if metadata is valid |
| **Issue body uses Markdown links** | Regex handles both plain and markdown link formats |

---

## Error Handling

| Error Scenario | Handling | User Feedback |
|----------------|----------|---------------|
| **Invalid metadata schema** | Exit 1, clear error message | `ERROR: epic_id must match pattern PRD-XXX, got: PRD-1` |
| **GitHub issue not found** | Exit 2, propagate gh error | `ERROR: Failed to fetch issue #999999` |
| **gh CLI not installed** | Exit 2, dependency error | `ERROR: gh CLI not found. Install from https://cli.github.com/` |
| **jq not installed** | Exit 2, dependency error | `ERROR: jq not found. Install with: brew install jq` |
| **Network failure** | Exit 2, propagate gh error | `ERROR: Network error fetching issue` |
| **Task not found** | Exit 1, task error | `ERROR: Task #task-123 not found` |
| **Sync disabled** | Exit 2, skip message | `Task #task-123 sync not enabled (sync_on_complete: false)` |

---

## Performance Considerations

- **gh CLI calls**: ~500ms per call (network dependent)
- **jq parsing**: <10ms for typical metadata
- **Validation**: <50ms per metadata object
- **Script execution**: Total <1s for issue-to-task conversion

**Optimization opportunities**:
- Cache gh issue responses for repeated conversions
- Batch processing for multiple issues (Phase 4)

---

## Accessibility Considerations

Not applicable (CLI-only tooling).

---

## Testing Considerations

### Critical Test Areas
1. **Metadata validation**: All task types, all required/optional fields
2. **Pattern matching**: epic_id, tdd_section, task_id formats
3. **Label parsing**: type:*, effort:* extraction
4. **Body extraction**: All regex patterns for Epic/Task/TDD
5. **Error handling**: Missing dependencies, network failures
6. **Edge cases**: See Edge Cases table

### Test Data
- Use real GitHub issues #7 (Epic) and #14 (Task) for integration tests
- Create mock gh CLI responses for unit tests
- Test with malformed JSON, missing fields, invalid patterns

---

## Dependencies

### External Tools (Required)
- **gh CLI**: GitHub operations
  - Validation: `gh --version`
  - Installation: https://cli.github.com/
- **jq**: JSON parsing
  - Validation: `jq --version`
  - Installation: `brew install jq` (macOS)

### Claude Code Features (Required)
- **Task Primitives**: TaskCreate, TaskUpdate, TaskList, TaskGet
- **Task Persistence**: ~/.claude/tasks/ storage

### Optional Dependencies
- **bats**: For automated testing
  - Installation: `brew install bats-core`
- **D2**: For rendering architecture diagrams
  - Installation: `brew install d2`

---

## Open Questions

### Phase 0 (Discovery)
1. Does ~/.claude/tasks/ persist automatically, or does it require configuration?
2. What is the exact file format in ~/.claude/tasks/?
3. Does metadata preserve complex types (arrays, nested objects)?
4. Can TaskGet be called from shell, or only within Claude session?

### Phase 1 (Foundation)
5. Should validation reject extra unknown fields (strict) or allow them (permissive)?
6. Should we version the schema itself with "_schema_version" field?

### Phase 2 (Pull Integration)
7. Should script support multiple output formats (JSON, YAML, plain text)?
8. Should we cache gh issue responses for repeated conversions?

### Phase 3+ (Post-MVP)
9. Should sync_on_complete default to true or false?
10. How should we handle sync failures (retry, queue, ignore)?

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2026-01-25 | Technical Architect (Claude) | Initial draft for MVP (Phases 0-2) |
