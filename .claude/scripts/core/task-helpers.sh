#!/usr/bin/env bash
# task-helpers.sh - Utility functions for Claude task metadata
# Usage: source this file to use helper functions

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

# Extract epic_id from metadata
# Args: $1 = metadata JSON string
# Returns: Epic ID or empty string
get_epic_id() {
  local metadata="$1"
  echo "$metadata" | jq -r '.epic_id // empty'
}

# Extract tdd_section from metadata
# Args: $1 = metadata JSON string
# Returns: TDD section or empty string
get_tdd_section() {
  local metadata="$1"
  echo "$metadata" | jq -r '.tdd_section // empty'
}

# Extract effort from metadata
# Args: $1 = metadata JSON string
# Returns: Effort (S/M/L/XL) or empty string
get_effort() {
  local metadata="$1"
  echo "$metadata" | jq -r '.effort // empty'
}
