# Claude Scripts Documentation

**Version**: v0.3 (MVP - Phases 0-2)
**Last Updated**: 2026-01-25

---

## Overview

This directory contains Bash scripts for integrating Claude Code task primitives with GitHub issues. The scripts enable metadata validation, GitHub-to-Claude task conversion, and automated workflow coordination.

### Directory Structure

```
.claude/scripts/
├── core/                    # Phase 1 - Validation layer
│   ├── validate-metadata.sh
│   └── task-helpers.sh
├── github-sync/             # Phase 2-3 - GitHub integration
│   ├── issue-to-task.sh    # Phase 2 - MVP
│   └── task-to-status.sh   # Phase 3 - Post-MVP
├── workflows/               # Phase 4-5 - Orchestration (future)
│   ├── epic-workflow.sh
│   ├── update-epic-tasks.sh
│   └── task-cleanup.sh
└── README.md               # This file
```

---

## Core Scripts (Phase 1)

### validate-metadata.sh

**Purpose**: Validates Claude task metadata against JSON schema

**Location**: `.claude/scripts/core/validate-metadata.sh`

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
# Output (stderr): ✓ Metadata valid: type=epic
# Exit code: 0

# Invalid Epic metadata (missing epic_id)
.claude/scripts/core/validate-metadata.sh '{
  "type": "epic",
  "prd": "docs/specs/PRD-001.md"
}'
# Output (stderr): ERROR: Epic requires 'epic_id' field
# Exit code: 1

# Invalid type
.claude/scripts/core/validate-metadata.sh '{
  "type": "feature"
}'
# Output (stderr): ERROR: Invalid type 'feature'. Must be one of: epic task tdd pm-work documentation
# Exit code: 1
```

**Exit Codes**:
- `0` - Metadata is valid
- `1` - Metadata is invalid (schema violation)
- `2` - System error (jq missing, invalid JSON syntax)

**Validation Rules**:
- **Required field**: `type` (must be one of: epic, task, tdd, pm-work, documentation)
- **Epic**: Requires `epic_id` (pattern: PRD-XXX) and `prd`
- **Task**: No required fields beyond `type`
- **TDD**: Requires `tdd_id` (pattern: XXX) and `epic_id` (pattern: PRD-XXX)
- **Optional fields**: Validated if present (patterns, enums, type checks)

---

### task-helpers.sh

**Purpose**: Utility functions for metadata extraction and formatting

**Location**: `.claude/scripts/core/task-helpers.sh`

**Usage**:
```bash
# Source the file to use functions
source .claude/scripts/core/task-helpers.sh

# Use helper functions
METADATA='{"type": "epic", "github_issue": 7, "epic_id": "PRD-001"}'
get_github_issue "$METADATA"    # → 7
get_task_type "$METADATA"       # → epic
get_epic_id "$METADATA"         # → PRD-001
is_sync_enabled "$METADATA"     # → false
```

**Available Functions**:

| Function | Args | Returns | Description |
|----------|------|---------|-------------|
| `get_github_issue` | metadata JSON | Issue number or empty | Extract GitHub issue number |
| `get_task_type` | metadata JSON | Task type or empty | Extract task type |
| `is_sync_enabled` | metadata JSON | "true" or "false" | Check if sync enabled |
| `format_metadata` | metadata JSON | Formatted JSON | Pretty-print metadata |
| `build_epic_metadata` | issue_num, epic_id, prd, tdd | JSON metadata | Build Epic metadata |
| `build_task_metadata` | issue_num, task_id, epic, tdd_section | JSON metadata | Build Task metadata |
| `get_epic_id` | metadata JSON | Epic ID or empty | Extract epic_id |
| `get_tdd_section` | metadata JSON | TDD section or empty | Extract tdd_section |
| `get_effort` | metadata JSON | Effort or empty | Extract effort (S/M/L/XL) |

**Examples**:

```bash
# Build Epic metadata
build_epic_metadata 7 "PRD-001" "docs/specs/PRD-001.md"
# Output: {"github_issue":7,"type":"epic","epic_id":"PRD-001",...}

# Build Task metadata
build_task_metadata 14 "T1.2" 7 "§3"
# Output: {"github_issue":14,"type":"task","task_id":"T1.2","epic":7,...}

# Extract fields
METADATA='{"github_issue": 14, "type": "task", "epic": 7}'
get_github_issue "$METADATA"   # → 14
get_task_type "$METADATA"      # → task
```

---

## GitHub Sync Scripts (Phase 2)

### issue-to-task.sh

**Purpose**: Converts GitHub issue to Claude TaskCreate call with validated metadata

**Location**: `.claude/scripts/github-sync/issue-to-task.sh`

**Usage**:
```bash
.claude/scripts/github-sync/issue-to-task.sh <issue-number>
```

**Examples**:

```bash
# Convert Epic issue #7
.claude/scripts/github-sync/issue-to-task.sh 7

# Output (stdout):
# TaskCreate({
#   subject: "PRD-001: JLPT Mastery Engine",
#   description: "...",
#   metadata: {
#     "github_issue": 7,
#     "type": "epic",
#     "epic_id": "PRD-001",
#     "prd": "docs/specs/PRD-001-JLPT-Mastery-Engine.md"
#   }
# })

# Output (stderr):
# Fetching GitHub issue #7...
# Issue: PRD-001: JLPT Mastery Engine
# Labels: type:epic, phase:1
# Validating metadata...
# ✓ Metadata valid: type=epic
# Generating TaskCreate call...
# ✓ Conversion successful. Copy the TaskCreate call above.

# Exit code: 0
```

**Exit Codes**:
- `0` - Conversion successful, TaskCreate call on stdout
- `1` - Validation error (metadata invalid, missing required fields)
- `2` - GitHub error (issue not found, gh CLI failed, invalid argument)

**Extraction Patterns**:

| Metadata Field | Extraction Pattern | Example Match |
|----------------|-------------------|---------------|
| **Epic ID** | PRD-XXX anywhere in title or body | "PRD-001: Feature" |
| **PRD Path** | docs/specs/PRD-XXX*.md | docs/specs/PRD-001-Feature.md |
| **TDD Path** | docs/tdd/TDD-XXX*.md | docs/tdd/TDD-001-Feature.md |
| **Epic Reference** | #N after "Epic:" or "Part of" | "Epic: #7" → 7 |
| **TDD Section** | §N after "Implements:" or "TDD Section:" | "Implements: §3" → §3 |
| **Task ID** | T*.* after "Task ID:" or "Task:" | "Task ID: T1.2" → T1.2 |
| **Effort** | effort:* label | effort:m → M (uppercased) |

**Workflow**:
1. Fetch issue from GitHub (via `gh issue view`)
2. Extract metadata based on issue type (epic, task, tdd)
3. Validate metadata (via `validate-metadata.sh`)
4. Generate TaskCreate call formatted for copy-paste
5. Output TaskCreate to stdout, progress to stderr

**Error Handling**:

```bash
# Issue not found
.claude/scripts/github-sync/issue-to-task.sh 999999
# ERROR: Failed to fetch issue #999999
# Exit code: 2

# Invalid issue number
.claude/scripts/github-sync/issue-to-task.sh abc
# ERROR: Issue number must be integer, got: abc
# Exit code: 2

# No type: label
.claude/scripts/github-sync/issue-to-task.sh 42
# ERROR: No type: label found on issue #42
# Available labels: status:ready, phase:1
# Exit code: 1

# Epic missing epic_id
.claude/scripts/github-sync/issue-to-task.sh 50
# ERROR: Epic requires 'epic_id' field
# Metadata: {"type":"epic","epic_id":"","prd":"..."}
# Exit code: 1
```

---

## Workflow Scripts (Phase 4-5 - Future)

*These scripts are planned for post-MVP implementation.*

### epic-workflow.sh (Phase 4)

**Purpose**: Automate Epic → TDD → Task workflow setup

**Status**: Not yet implemented

**Planned Usage**:
```bash
.claude/scripts/workflows/epic-workflow.sh <epic-issue-number>
```

### update-epic-tasks.sh (Phase 4)

**Purpose**: Batch update GitHub tasks with TDD section references

**Status**: Not yet implemented

### task-cleanup.sh (Phase 5)

**Purpose**: Remove old completed tasks based on retention policy

**Status**: Not yet implemented

---

## Dependencies

### Required

- **gh CLI**: GitHub command-line tool
  ```bash
  brew install gh
  gh auth login
  gh --version
  ```

- **jq**: JSON parsing and manipulation
  ```bash
  brew install jq
  jq --version
  ```

### Optional

- **bats**: Bash testing framework (for automated tests)
  ```bash
  brew install bats-core
  ```

---

## Common Workflows

### Workflow 1: Convert GitHub Epic to Claude Task

```bash
# 1. Convert issue
.claude/scripts/github-sync/issue-to-task.sh 7

# 2. Copy TaskCreate call from stdout

# 3. Paste into Claude session (Claude creates task)

# 4. Verify task created
TaskList()
```

### Workflow 2: Validate Metadata Before Creating Task

```bash
# 1. Build metadata JSON
METADATA=$(source .claude/scripts/core/task-helpers.sh && build_epic_metadata 7 "PRD-001" "docs/specs/PRD-001.md")

# 2. Validate
.claude/scripts/core/validate-metadata.sh "$METADATA"

# 3. If valid, use in TaskCreate
echo "$METADATA" | jq .
```

### Workflow 3: Convert Multiple Issues

```bash
# Convert all task issues for Epic #7
for issue in 13 14 15 16 17; do
  echo "Converting issue #$issue..."
  .claude/scripts/github-sync/issue-to-task.sh $issue > "task-$issue.txt"
done

# Review generated TaskCreate calls
cat task-*.txt
```

---

## Troubleshooting

### Script Not Executable

```bash
# If you see "Permission denied"
chmod +x .claude/scripts/core/validate-metadata.sh
chmod +x .claude/scripts/core/task-helpers.sh
chmod +x .claude/scripts/github-sync/issue-to-task.sh
```

### gh CLI Not Authenticated

```bash
# If you see "authentication required"
gh auth login

# Verify authentication
gh auth status
```

### jq Not Found

```bash
# If you see "jq: command not found"
brew install jq
```

### Extraction Patterns Not Matching

**Issue**: Script extracts empty fields from issue body

**Cause**: Issue body doesn't match expected patterns

**Solution**: Check issue body format and update patterns if needed. The script uses case-insensitive awk patterns for flexibility.

**Debug**:
```bash
# View issue body
gh issue view 7 --json body | jq -r '.body'

# Test extraction manually
BODY=$(gh issue view 7 --json body | jq -r '.body')
echo "$BODY" | awk '{match($0, /PRD-[0-9]{3}/); if (RSTART) print substr($0, RSTART, RLENGTH)}'
```

---

## Testing

### Manual Testing

```bash
# Test validation script
.claude/scripts/core/validate-metadata.sh '{"type": "epic", "epic_id": "PRD-001", "prd": "test.md"}'

# Test helper functions
source .claude/scripts/core/task-helpers.sh
get_task_type '{"type": "epic"}'

# Test conversion script
.claude/scripts/github-sync/issue-to-task.sh 7
```

### Automated Testing (Future)

```bash
# Run bats tests (when implemented)
bats test/validate-metadata.bats
bats test/issue-to-task.bats
```

---

## Development Guidelines

### Adding New Scripts

1. Place in appropriate directory (core, github-sync, workflows)
2. Make executable: `chmod +x script.sh`
3. Add shebang: `#!/usr/bin/env bash`
4. Use `set -euo pipefail` for safety
5. Document in this README
6. Write tests (if using bats)

### Script Standards

- **Exit codes**: 0=success, 1=validation error, 2=system error
- **Output**: stdout=data, stderr=progress/errors
- **Error format**: `ERROR: <description>`
- **Success format**: `✓ <message>`
- **Dependencies**: Check for gh and jq at start if needed

### Bash Best Practices

- Quote all variables: `"$VAR"` not `$VAR`
- Use `[[ ]]` for tests, not `[ ]`
- Prefer `$(command)` over `` `command` ``
- Use local variables in functions
- Handle empty values with `${VAR:-default}`

---

## Related Documentation

- **Integration Guide**: `docs/CLAUDE_TASK_INTEGRATION.md`
- **PRD**: `docs/specs/PRD-004-Claude-Task-GitHub-Integration.md`
- **TDD**: `docs/tdd/TDD-004-Claude-Task-GitHub-Integration.md`
- **Testing**: `temp/v0.3_TESTING-task-integration.md`
- **Project Board**: `docs/PROJECT_BOARD_GUIDE.md`

---

**Maintained by**: Claude (Developer)
**Version**: v0.3 MVP (Phases 0-2)
**Last Updated**: 2026-01-25
